import hashlib


def hash_id(string) -> str:
    """
    Hashes a string using the MD5 algorithm and returns the first 8 characters of the resulting hash.

    Args:
        string (str): The string to be hashed.

    Returns:
        str: The first 8 characters of the MD5 hash of the input string.
    """
    hash = hashlib.md5(string.encode()).hexdigest()
    hash_id = hash[:8]
    return hash_id
