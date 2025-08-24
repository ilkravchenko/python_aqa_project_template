import re


def escape_single_quotes(text: str) -> str:
    """
    Escapes single quotes between two letters in a string by replacing ' with ''.

    Args:
        text (str): The input string.

    Returns:
        str: The escaped string.
    """
    if not isinstance(text, str):
        return text  # Return unchanged if it's not a string

    return re.sub(r"(?<=\w)'(?=\w)", "''", text)
