import random


def select_random_address_query(cached: bool = True) -> str:
    """
    Generate a SQL query to select a random address.

    Args:
        cached (bool, optional): Whether to use cached addresses. Defaults to True.

    Returns:
        str: The SQL query string to select a random address.
    """
    cached_addresses = [
        'ID_1',
        'ID_2'
    ]
    if cached:
        address_id = random.choice(cached_addresses)
        sub_query_1 = f"""@
            WITH random_address AS (
                    SELECT *
                    FROM db.address 
                    WHERE status = 1 AND level = 5 AND address_id = '{address_id}'
                    LIMIT 1
                )
            """
    else:
        sub_query_1 = """@
            WITH random_address AS (
                    SELECT *
                    FROM registry.address 
                    WHERE status = 1 AND level = 5
                      AND l5atuid IN (SELECT atuid FROM db.address WHERE status = 1)
                      AND l4atuid IN (SELECT atuid FROM db.address WHERE status = 1)
                      AND l3atuid IN (SELECT atuid FROM db.address WHERE status = 1)
                      AND l2atuid IN (SELECT atuid FROM db.address WHERE status = 1)
                      AND l1atuid IN (SELECT atuid FROM db.address WHERE status = 1)
                    ORDER BY RANDOM() 
                    LIMIT 1
                )
            """
    sub_query_2 = """@
        SELECT * 
            FROM db.address
            WHERE atuid IN (
                SELECT atuid FROM random_address
                UNION ALL
                SELECT l4atuid FROM random_address
                UNION ALL
                SELECT l3atuid FROM random_address
                UNION ALL
                SELECT l2atuid FROM random_address
                UNION ALL
                SELECT l1atuid FROM random_address
            )
            ORDER BY codificatorlevel;
        """
    return f'{sub_query_1}\n{sub_query_2}'
