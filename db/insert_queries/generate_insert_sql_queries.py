import os
import uuid
from datetime import datetime, timezone
from typing import Literal

from utils.randomizer import generate_random_number_string, generate_legal_name, generate_ukrainian_name, \
    generate_random_email, generate_random_phone_number


def generate_query(table_name: str, body: dict) -> str:
    """
    Generate an SQL INSERT query.

    This function generates an SQL INSERT query string for a given table name and a dictionary of column-value pairs.

    Args:
        table_name (str): The name of the table to insert data into.
        body (dict): A dictionary containing column-value pairs to be inserted.

    Returns:
        str: The generated SQL INSERT query string.
    """
    if not body:
        return ''
    columns = ', '.join(body.keys())
    values = ', '.join([f"'{v}'" if isinstance(v, str) else ('NULL' if v is None else str(v)) for v in body.values()])
    return f"@INSERT INTO {table_name} ({columns}) VALUES ({values});"


def generate_owner_insert_query(subject_type: Literal['individual', 'legal'], **kwargs) -> tuple[str, dict]:
    """
    Generate an SQL INSERT query for the db.owner_object table based on subject type,
    along with a JSON body representing the data. All values can be passed through kwargs,
    otherwise default generated values will be used.

    Args:
        subject_type (Literal['individual', 'legal']): The subject type, either 'individual' or 'legal'.
        kwargs: Optional keyword arguments to override default generated values.

    Returns:
        tuple: The generated SQL INSERT query and the JSON body containing the data.
    """
    # Common fields between individual and legal entity
    owner_object_id = str(uuid.uuid4())
    subject_type_id = "1fe55701-716b-42cc-95b8-dada114ff642" if subject_type == 'individual' \
        else "25e706a2-f3db-4136-9f69-42f4f719cd1d"
    phone_number = kwargs.get('phone_number', generate_random_phone_number())
    email = kwargs.get('email', generate_random_email())
    ddm_created_at = kwargs.get('ddm_created_at', datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S'))
    ddm_created_by = kwargs.get('ddm_created_by', os.getenv('RNOKPP', '00000000'))
    ddm_updated_at = kwargs.get('ddm_updated_at', ddm_created_at)
    ddm_updated_by = kwargs.get('ddm_updated_by', ddm_created_by)

    # Initialize the JSON body
    json_body = {
        'owner_object_id': owner_object_id,
        'subject_type_id': subject_type_id,
        'phone_number': phone_number,
        'email': email,
        'ddm_created_at': ddm_created_at,
        'ddm_created_by': ddm_created_by,
        'ddm_updated_at': ddm_updated_at,
        'ddm_updated_by': ddm_updated_by
    }

    # For individual subject type
    if subject_type == "individual":
        first_name = kwargs.get('first_name', generate_ukrainian_name('first'))
        last_name = kwargs.get('last_name', generate_ukrainian_name('last'))
        second_name = kwargs.get('second_name', generate_ukrainian_name('second'))
        doc_type_id = kwargs.get('doc_type_id', '9e45a20b-1a05-477f-86b0-9a68e98d14f5')

        json_body.update({
            'first_name': first_name,
            'last_name': last_name,
            'second_name': second_name,
            "doc_type_id": doc_type_id,
        })
    # For legal entity subject type
    elif subject_type == "legal":
        name_legal_entity = kwargs.get('name_legal_entity', generate_legal_name())

        json_body.update({
            "name_legal_entity": name_legal_entity,
        })
    else:
        raise ValueError("Invalid subject_type. Must be either 'individual' or 'legal'.")

    # Generate the query using the helper function
    query = generate_query("db.owner_object", json_body)

    return query, json_body


def generate_full_building_query(owner_id, address_id, **kwargs):
    pass
