import hashlib
from datetime import datetime


def get_md5_hash(input_str: str):
    hash_hex = None
    if not input_str:
        raise RuntimeError("Invalid input string for hashing.")

    hash_obj = hashlib.md5()
    hash_obj.update(input_str.encode("utf-8"))

    return hash_obj.hexdigest()


def json_serialiser(obj):
    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%d %h:%M:%S")

    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
