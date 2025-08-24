import logging
import os
import platform
import socket
import subprocess
import time
from contextlib import contextmanager
from random import randint
from typing import Optional, Any, Literal, Union

import psycopg2
import yaml
from psycopg2 import OperationalError, pool
from psycopg2 import errorcodes, errors
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED

from data.constants import CI_NODE_PORT_IP
from utils.data_helper import escape_single_quotes


class DBConnector:
    """
    A class to manage PostgreSQL database connections using psycopg2 and OpenShift port forwarding.
    This class is context-managed, ensuring connections are properly established and closed.
    It also includes checks for port-forwarding stability and retry mechanisms for the connection.
    """

    def __init__(self, pod_name: str, namespace: str, pod_port: int, dbname: str, user: str,
                 password: str, max_retries: int = 5, retry_delay: float = 2.0, local_port: int = None):
        """
        Initialize the DBConnector with pod and database connection details.

        Args:
            pod_name (str): The name of the PostgreSQL pod.
            namespace (str): The OpenShift namespace.
            local_port (int): The local port to forward to.
            pod_port (int): The PostgreSQL port in the pod.
            dbname (str): The name of the PostgreSQL database.
            user (str): The PostgreSQL username.
            password (str): The PostgreSQL password.
            max_retries (int): Maximum number of retry attempts for the connection.
            retry_delay (float): Delay (in seconds) between retry attempts.
        """
        self.pod_name = pod_name
        self.namespace = namespace
        self.local_port = local_port or self.get_random_available_port()  # Dynamically assign a port if not specified
        self.pod_port = pod_port
        self.dbname = dbname
        self.user = user
        self.password = password
        self.connection = None
        self.connection_pool = None
        self.port_forward_process = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.is_ci = os.getenv('GITLAB_CI') == 'true' and pod_name.startswith('operational')
        self.prepared_statements = set()

        # Configure logging
        logging.basicConfig()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    @staticmethod
    def get_random_available_port() -> int:
        """
        Find a random available port within a specific range and check if it is free.

        Returns:
            int: A random available port number.
        """
        for _ in range(100):
            port = randint(30000, 40000)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:  # Port is free
                    return port
        raise Exception("Failed to find an available port for port-forwarding.")

    def __enter__(self):
        """
        Context manager entry point. Starts the port-forwarding and connects to the database.

        Returns:
            DBConnector: The DBConnector object with an active database connection.
        """
        # Start port-forwarding
        if not self.is_ci:
            self.logger.info("Attempting to start port-forwarding...")
            self.port_forward_process = self.port_forward_postgres()

        # Retry mechanism for database connection
        for attempt in range(1, self.max_retries + 1):
            try:
                # Ensure port-forwarding is still running before connecting
                if not self.is_port_forwarding_running() and not self.is_ci:
                    raise Exception("Port-forwarding process is not running.")

                # Attempt to connect to the database
                self.logger.info(f"Attempt {attempt}: Trying to connect to the database...")
                self.connection = self.connect_to_postgres()
                self.logger.info(f"Successfully connected to the database on attempt {attempt}")
                self.connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

                # Create connection pool for better performance
                self.create_connection_pool(min_connections=1, max_connections=10)

                break
            except Exception as e:
                self.logger.warning(f"Attempt {attempt} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    raise Exception("Failed to connect to the database after multiple retries.")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Context manager exit point. Cleans up the port-forwarding and closes the database connection.

        Args:
            exc_type, exc_value, traceback: Standard context manager exit parameters.
        """
        # Close the PostgreSQL connection pool
        if self.connection_pool:
            self.connection_pool.closeall()
            self.logger.info("PostgreSQL connection pool closed.")

        # Close the PostgreSQL connection
        if self.connection:
            self.connection.close()
            self.logger.info("PostgreSQL connection closed.")

        # Terminate the port-forward process
        if self.port_forward_process and not self.is_ci:
            self.port_forward_process.terminate()
            self.logger.info("Port-forwarding process terminated.")

    def port_forward_postgres(self) -> Optional[subprocess.Popen]:
        """
        Log in to OpenShift using `oc` and port-forward the PostgreSQL pod to a random available port.
        Retries login if it fails and port-forwarding with a different port up to `max_retries` times.

        Returns:
            Optional[subprocess.Popen]: The subprocess running the port-forwarding, or None if all attempts fail.
        """
        oc_path = '/opt/homebrew/bin/oc' if platform.system() == 'Darwin' else '/usr/local/bin/oc'
        oc_server = 'https://api.okd-3dc1.diia.digital:6443'
        kube_config_path = os.path.expanduser("~/.kube/config")
        backup_config_path = os.path.expanduser("~/.kube/config.bak")

        def validate_kube_config():
            """Validate YAML formatting of the Kubernetes config file."""
            if os.path.exists(kube_config_path):
                try:
                    with open(kube_config_path, "r") as f:
                        yaml.safe_load(f)  # Validate YAML
                    self.logger.info(f"Kubernetes config file is valid: {kube_config_path}")
                    return True
                except yaml.YAMLError as e:
                    self.logger.error(f"Invalid Kubernetes config file: {e}")
                    return False
            return False

        # Step 1: Check and backup existing config file
        if not validate_kube_config():
            self.logger.warning("Invalid kube config detected. Backing up and regenerating.")
            if os.path.exists(kube_config_path):
                os.rename(kube_config_path, backup_config_path)
                self.logger.info(f"Backed up corrupted kube config to {backup_config_path}")

        # Step 2: Attempt OpenShift Login with retries
        login_successful = False
        login_process = None
        for login_attempt in range(1, self.max_retries + 1):
            self.logger.info(f"Attempt {login_attempt}: Logging in to OpenShift server: {oc_server}")

            # Run `oc login` to generate a fresh config
            login_process = subprocess.run(
                [oc_path, "login", f"--server={oc_server}", f"--token={os.getenv('OC_SECRET')}",
                 "--insecure-skip-tls-verify"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if login_process.returncode == 0 and validate_kube_config():
                login_successful = True
                self.logger.info("Successfully logged into OpenShift with a valid kube config.")
                break
            else:
                self.logger.warning(
                    f"Login attempt {login_attempt} failed: {login_process.stderr.decode().strip()}"
                )
                time.sleep(self.retry_delay)

        if not login_successful:
            self.logger.error("Failed to log in to OpenShift after multiple attempts.")
            raise Exception(f"Login to OpenShift failed after multiple attempts - {login_process.stderr}")

        # Step 3: Attempt Port-Forwarding
        for attempt in range(1, self.max_retries + 1):
            self.local_port = self.get_random_available_port()
            self.logger.info(
                f"Attempt {attempt}: Starting port-forward from pod {self.pod_name}:{self.pod_port} "
                f"to localhost:{self.local_port}..."
            )

            process = subprocess.Popen(
                [oc_path, "port-forward", f"pod/{self.pod_name}", f"{self.local_port}:{self.pod_port}", "-n",
                 self.namespace],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for port-forwarding to establish
            time.sleep(3)

            if process.poll() is None:
                self.logger.info(f"Port forwarding successful. PostgreSQL is accessible at localhost:{self.local_port}")
                return process
            else:
                stderr_output = process.stderr.read().decode().strip()
                self.logger.warning(f"Port-forwarding failed. Error: {stderr_output}. Retrying with a different port.")
                process.terminate()
                time.sleep(self.retry_delay)

        self.logger.error("Failed to establish port-forwarding after multiple attempts.")
        raise Exception("Port-forwarding failed after multiple attempts.")

    def is_port_forwarding_running(self) -> bool:
        """
        Check if the port-forwarding process is still running.

        Returns:
            bool: True if the port-forwarding process is active, False otherwise.
        """
        if self.port_forward_process and self.port_forward_process.poll() is None:
            return True
        return False

    def connect_to_postgres(self) -> psycopg2.connect:
        """
        Establish a connection to PostgreSQL database using psycopg2 and validate it.

        Connection details vary based on environment:
        - In CI mode: Uses a hardcoded host IP (10.129.71.49) and port (31021)
        - In local mode: Uses localhost with dynamically assigned port

        For updating the CI environment host IP:
        1. Log in to OpenShift using the token from:
           https://oauth-openshift.apps.okd-3dc1.diia.digital/oauth/token/display
        2. Run this command to find the most recent available node:
           `oc get nodes -o wide | grep pzm-stage | sort -k5 -r | head -n 1`
        3. Use the IP address from the INTERNAL-IP column in the results and update the CI_NODE_PORT_IP constant.

        Returns:
            psycopg2.connection: Active connection to the PostgreSQL database
        """
        try:
            if self.is_ci:
                host = CI_NODE_PORT_IP
                port = '31021'
            else:
                host = 'localhost'
                port = self.local_port
            connection = psycopg2.connect(
                dbname=self.dbname,
                user=self.user,
                password=self.password,
                host=host,
                port=port,
                options="-c tcp_keepalives_idle=30 -c tcp_keepalives_interval=10 -c tcp_keepalives_count=5"
            )
            cursor = connection.cursor()
            cursor.execute("SELECT version();")
            db_version = cursor.fetchone()
            self.logger.info(f"Connected to PostgreSQL {self.pod_name} DB version: {db_version[0]}")
            cursor.close()
            return connection
        except Exception as e:
            self.logger.error(f"Error while connecting to PostgreSQL: {e}")
            raise

    def create_connection_pool(self, min_connections: int = 1,
                               max_connections: int = 10) -> pool.ThreadedConnectionPool:
        """
        Create a connection pool for better performance with multiple queries.

        Args:
            min_connections: Minimum number of connections to keep in the pool
            max_connections: Maximum number of connections allowed in the pool

        Returns:
            pool.ThreadedConnectionPool: The connection pool object
        """
        if self.is_ci:
            host = CI_NODE_PORT_IP
            port = '31021'
        else:
            host = 'localhost'
            port = self.local_port

        self.connection_pool = pool.ThreadedConnectionPool(
            min_connections,
            max_connections,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            host=host,
            port=port,
            options="-c tcp_keepalives_idle=30 -c tcp_keepalives_interval=10 -c tcp_keepalives_count=5"
        )
        self.logger.info(f"Created connection pool with {min_connections} to {max_connections} connections")
        return self.connection_pool

    @contextmanager
    def get_connection(self):
        """
        Get a connection from the pool with automatic return.

        Usage:
            with db_connector.get_connection() as conn:
                # Use the connection
        """
        if not self.connection_pool:
            self.create_connection_pool()

        conn = self.connection_pool.getconn()
        try:
            yield conn
        finally:
            self.connection_pool.putconn(conn)

    def reconnect(self) -> None:
        """
        Reconnect to port-forwarding and the PostgreSQL database.
        """
        self.logger.info("Reconnecting to port-forwarding and database...")
        # Terminate existing port-forwarding process if it exists
        if self.port_forward_process and not self.is_ci:
            self.port_forward_process.terminate()
            self.logger.info("Terminated the previous port-forwarding process.")

        # Restart port-forwarding
        if not self.is_ci:
            self.port_forward_process = self.port_forward_postgres()

        # Reconnect to the database
        self.connection = self.connect_to_postgres()

        # Recreate connection pool
        if self.connection_pool:
            self.connection_pool.closeall()
            self.create_connection_pool()

        self.logger.info("Reconnected successfully to the database.")

    @contextmanager
    def transaction(self):
        """
        Context manager for optimized transactions.

        Usage:
            with db_connector.transaction():
                db_connector.run_query("INSERT INTO...")
                db_connector.run_query("UPDATE...")
        """
        conn = self.connection
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)

        try:
            yield self
            conn.commit()
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction failed: {e}")
            raise
        finally:
            conn.set_isolation_level(old_isolation_level)

    def run_query(self, query: str, fetch: Literal['one', 'all'] = 'one', max_retries: int = 3,
                  params: Optional[list] = None, use_prepared: bool = False) -> Union[
        list[dict[str, Any]], dict[str, Any], None]:
        """
        Execute a SQL query and return the result as a dictionary with column names as keys.
        Automatically uses optimized methods based on query type.

        Args:
            query: SQL query to execute
            fetch: Whether to fetch 'one' row or 'all' rows
            max_retries: Maximum number of retry attempts
            params: Optional parameters for parameterized queries
            use_prepared: Whether to use prepared statements for this query

        Returns:
            dict[str, Any] or list[dict[str, Any]]: A dictionary representing the result for a single row,
                                                    or a list of dictionaries for multiple rows.
        """
        # Ensure cursor and connection are available
        if self.connection is None or self.connection.closed:
            self.logger.warning("Database connection is closed. Reconnecting...")
            self.reconnect()

        # Get the query type for specialized handling
        query = escape_single_quotes(query)
        query_type = query.strip().lower().split()[0] if query.strip() else ""

        # Use optimized methods based on query type
        if query_type == 'insert' and 'values' in query.lower():
            # For bulk inserts, we want to extract table name and columns
            # This is a simplified parsing that works for basic INSERT statements
            if params and isinstance(params, list) and len(params) > 10:
                # Attempt to parse the table name and columns for batch insert
                try:
                    # Extract table name - simplified parser
                    table_match = query.lower().split('insert into')[1].split('(')[0].strip()

                    # Extract columns - simplified parser
                    columns_match = query.split('(')[1].split(')')[0]
                    columns = [col.strip() for col in columns_match.split(',')]

                    self.logger.info(f"Converting to batch insert: {table_match} with {len(params)} rows")
                    return self.batch_insert(table_match, columns, params)
                except Exception as e:
                    self.logger.warning(f"Could not convert to batch insert: {e}. Using standard execution.")

        # For repeated parameterized queries, use prepared statements
        if use_prepared and params is not None:
            statement_name = f"stmt_{hash(query)}"
            return self.execute_prepared_statement(statement_name, query, params, fetch)

        # For standard execution
        cursor = self.connection.cursor()
        start_time = time.time()

        try:
            # Execute the SQL query with optimized retry mechanism
            for attempt in range(max_retries):
                try:
                    # Execute with parameters if provided
                    if params is not None:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)

                    execution_time = time.time() - start_time
                    if execution_time > 5:
                        self.logger.error(f"Slow query detected ({execution_time:.2f}s): {query[:500]}...")
                        print(f"WARNING: Slow query detected ({execution_time:.2f}s)")

                        # For slow INSERT queries, recommend batch operations
                        if query_type == 'insert':
                            self.logger.warning(
                                "Consider using batch_insert() for better performance with multiple INSERTs")
                    break
                except (errors.lookup(errorcodes.DEADLOCK_DETECTED),
                        errors.lookup(errorcodes.IN_FAILED_SQL_TRANSACTION),
                        errors.lookup(errorcodes.CONNECTION_FAILURE),
                        OperationalError) as e:

                    self.connection.rollback()
                    self.logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")

                    # Exponential backoff with shorter initial delay
                    time.sleep(0.2 * (2 ** attempt))

                    # Reconnect if it's a connection issue and not the last retry
                    if isinstance(e, (
                            OperationalError,
                            errors.lookup(errorcodes.CONNECTION_FAILURE))) and attempt < max_retries - 1:
                        self.reconnect()
                        cursor = self.connection.cursor()
            else:
                # If the function hasn't returned, all retries have failed
                self.logger.error(f"Failed to execute query after {max_retries} attempts.")
                raise Exception(f"Failed to execute query after {max_retries} attempts.")

            # Commit the transaction if modifying the database
            if query_type in ('delete', 'insert', 'update') or not cursor.description:
                self.connection.commit()
                return None

            # Fetch column names from the cursor description
            column_names = [desc[0] for desc in cursor.description]

            # Fetch results based on fetch mode
            if fetch == 'one':
                row = cursor.fetchone()
                if row:
                    # Map the result to a dictionary using column names
                    result = dict(zip(column_names, row))
                else:
                    result = None
            else:
                rows = cursor.fetchall()
                result = [dict(zip(column_names, row)) for row in rows]

            return result
        finally:
            cursor.close()

    def batch_insert(self, table_name: str, columns: list[str], values_list: list[tuple],
                     batch_size: int = 1000) -> bool:
        """
        Execute batch INSERT operations for better performance.

        Args:
            table_name: The name of the table
            columns: List of column names
            values_list: List of tuples containing values to insert
            batch_size: Number of rows to insert in each batch

        Returns:
            bool: True if successful
        """
        if not values_list:
            return True

        cursor = self.connection.cursor()
        try:
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            for i in range(0, len(values_list), batch_size):
                batch = values_list[i:i + batch_size]
                query = f"@INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                cursor.executemany(query, batch)
                self.connection.commit()

            self.logger.info(f"Batch inserted {len(values_list)} records into {table_name}")
            return True
        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Batch insert failed: {e}")
            raise
        finally:
            cursor.close()

    def execute_prepared_statement(self, statement_name: str, query: str, params: Optional[list] = None,
                                   fetch: Literal['one', 'all'] = 'one') -> Union[
        list[dict[str, Any]], dict[str, Any], None]:
        """
        Create and execute a prepared statement for better performance with repeated queries.

        Args:
            statement_name: Name to identify the prepared statement
            query: SQL query with placeholders
            params: Parameters to use with the query
            fetch: Whether to fetch 'one' row or 'all' rows

        Returns:
            The query results in the same format as run_query
        """
        cursor = self.connection.cursor()
        try:
            # Create prepared statement if it doesn't exist
            if statement_name not in self.prepared_statements:
                cursor.execute(f"PREPARE {statement_name} AS {query}")
                self.prepared_statements.add(statement_name)

            start_time = time.time()

            # Execute the prepared statement with parameters
            if params:
                params_placeholders = ', '.join([f"${i + 1}" for i in range(len(params))])
                cursor.execute(f"EXECUTE {statement_name}({params_placeholders})", params)
            else:
                cursor.execute(f"EXECUTE {statement_name}")

            execution_time = time.time() - start_time
            if execution_time > 5:
                self.logger.error(f"Slow prepared statement detected ({execution_time:.2f}s): {statement_name}")

            # Check if we need to return results
            if not cursor.description:
                self.connection.commit()
                return None

            # Fetch column names
            column_names = [desc[0] for desc in cursor.description]

            # Return results based on fetch mode
            if fetch == 'one':
                row = cursor.fetchone()
                return dict(zip(column_names, row)) if row else None
            else:
                rows = cursor.fetchall()
                return [dict(zip(column_names, row)) for row in rows]

        except Exception as e:
            self.connection.rollback()
            self.logger.error(f"Prepared statement execution failed: {e}")
            # Remove the statement from prepared set if it failed
            self.prepared_statements.discard(statement_name)
            raise
        finally:
            cursor.close()
