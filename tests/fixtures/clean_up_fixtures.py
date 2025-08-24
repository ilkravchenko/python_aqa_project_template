from typing import Callable

import pytest

CLEAN_UP = None


@pytest.fixture(scope="function")
def delete_owner(db_conn) -> Callable:
    """
    Fixture to delete an owner from the db after a test.

    This fixture provides a `factory` function that accepts an `owner_id`.
    After the test, the fixture ensures that the owner is deleted from the database to avoid any lingering data.

    Args:
        db_conn: The database connection for querying and deleting from the db.

    Yields:
        Callable: A function that takes an owner ID and ensures the owner is deleted after the test.
    """
    _owner_id = None

    def factory(owner_id: str) -> None:
        """
        Store the owner ID to be deleted after the test.

        Args:
            owner_id (str): The ID of the owner to be deleted.
        """
        nonlocal _owner_id
        _owner_id = owner_id

    yield factory

    # Teardown: Ensure the owner is deleted from the registry after the test
    if _owner_id:
        db_conn.run_query(
            f"""@
            DELETE FROM db.relation_type WHERE owner_object_id = '{_owner_id}';
            DELETE FROM db.owner_object WHERE owner_object_id = '{_owner_id}';
            """)


@pytest.fixture(scope="function")
def delete_property(db_conn) -> Callable:
    """
    Fixture to delete a property from the db and analytical system after a test.

    This fixture provides a `factory` function that accepts a `property_id`.
    After the test, the fixture ensures that all related entries for the property are deleted
    from the db and analytical system to maintain database cleanliness.

    Args:
        db_conn: The database connection for querying and deleting from the registry.

    Yields:
        Callable: A function that takes a property ID and ensures it is deleted after the test.
    """
    _property_id = None

    def factory(property_id: str) -> None:
        """
        Store the property ID to be deleted after the test.

        Args:
            property_id (str): The ID of the property to be deleted.
        """
        nonlocal _property_id
        _property_id = property_id

    yield factory

    # Teardown: Ensure the property and its related entries are deleted after the test
    if _property_id:
        db_conn.run_query(
            f"""@
            DELETE FROM db.sources_restoration_proof_document WHERE sources_restoration_works_id IN 
            (SELECT sources_restoration_works_id FROM db.sources_restoration_works WHERE real_estate_object_id='{_property_id}');
            DELETE FROM db.sources_restoration_works WHERE real_estate_object_id='{_property_id}';
            """
        )

