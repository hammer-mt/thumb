import hashlib

def hash_id(string):
    # hash to get a unique id that will be the same if passed the same string
    hash = hashlib.md5(string.encode()).hexdigest()
    hash_id = hash[:8]
    return hash_id