import os
from functools import lru_cache


def files_dir_path() -> str:
    return os.path.dirname(__file__)


@lru_cache(maxsize=128)
def get_filepath(file_name: str) -> str:
    return os.path.join(files_dir_path(), file_name)
