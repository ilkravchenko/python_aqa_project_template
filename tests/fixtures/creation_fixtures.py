from typing import Literal, Callable

import pytest

from db.insert_queries.generate_insert_sql_queries import generate_owner_insert_query, generate_full_building_query

CREATION = None


@pytest.fixture()
def create_owner(delete_owner, db_conn) -> Callable:
    """
    Fixture to create a legal owner and ensure it is cleaned up after the test.

    This fixture generates a legal owner, inserts the owner data into the database,
    and deletes the owner after the test.

    Args:
        delete_owner: Fixture for deleting the owner after the test.
        db_conn: Database connection for executing queries.

    Yields:
        dict: The owner details (JSON body) of the created legal owner.
    """
    _created_owner_id = None

    def factory(subject_type: Literal['individual', 'legal', 'dp'] = 'individual', **kwargs) -> dict:
        if subject_type == 'dp':
            return db_conn.run_query(
                "@SELECT * FROM owner_object WHERE name_legal_entity = 'DP'")
        else:
            # Generate the query and the body for inserting a new owner
            query, body = generate_owner_insert_query(subject_type=subject_type, **kwargs)

            nonlocal _created_owner_id
            _created_owner_id = body['owner_object_id']
            # Insert the owner into the registry database
            db_conn.run_query(query)

            # Yield the created owner body for use in the test
            return body

    yield factory
    # Cleanup: Ensure the created owner is deleted after the test
    delete_owner(_created_owner_id)


@pytest.fixture()
def create_property(create_owner, delete_property, db_conn, generate_random_address,
                    generate_random_address_by_community_katottg) -> Callable:
    """
    Fixture to create a property for the test and ensure it is cleaned up afterward.

    This fixture allows creating a real estate property (building or premises) using
    the provided factory function. The created property is enriched with metadata
    from related tables, making it more human-readable for test validation. After
    the test, it ensures the created property is cleaned up by invoking the
    `delete_property` function.

    Args:
        create_owner: Fixture to create an owner for the property.
        delete_property: Fixture to delete the property after the test.
        db_conn: Database connection for executing queries.
        generate_random_address: Fixture to generate a random address for the property.
        generate_random_address_by_community_katottg: Fixture to generate a random address by community katottg.

    Yields:
        Callable: A factory function to create properties with specified attributes.
    """
    _property_ids = []  # List to track created property IDs for cleanup

    def factory(real_estate_type: Literal['building', 'premises'] = 'building', **kwargs) -> dict:
        """
        Factory function to create a property with specified attributes.

        This function supports creating both buildings and premises. It generates
        SQL queries, executes them, and enriches the resulting property data with
        metadata from related tables.

        Args:
            real_estate_type (Literal['building', 'premises']): The type of property to create.
            kwargs: Additional attributes to customize the property creation.

        Returns:
            dict: A dictionary containing the created property's details, including
            enriched metadata from related tables.
        """
        # Step 1: Create an owner for the property
        created_owner = create_owner(**kwargs)

        # Step 2: Generate a random address for the property
        address = generate_random_address()

        # Step 3: Generate the SQL query and data for the property
        query, body = generate_full_building_query(
            created_owner['owner_object_id'],
            address_id=address['street']['address_id'],
            **kwargs
        )
        body['address'] = address  # Add address to the property data

        # Step 4: Execute the query to insert the property into the database
        db_conn.run_query(query)

        # Track the property ID for cleanup
        nonlocal _property_ids
        _property_ids.append(body['real_estate_object']['real_estate_object_id'])

        return body
