def delete_all_test_data_query() -> str:
    """
    Generate a SQL query to delete all test data from the database.
    """
    query = """
    -- # Step 1: DELELE all test data from the database
    @DELETE FROM balance WHERE payer_id IN (SELECT payer_id FROM payer WHERE sponsor_name LIKE 'AQA%');
    @DELETE FROM payer WHERE sponsor_name LIKE 'AQA%';
    """
    return query
