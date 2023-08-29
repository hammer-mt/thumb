import hashlib

def hash_id(string):
    # hash to get a unique id that will be the same if passed the same string
    hash = hashlib.md5(string.encode()).hexdigest()
    hash_id = hash[:8]
    return hash_id

def count_calls(prompts, cases, runs, models):
    # count the number of calls that will be made to the API
    calls = len(prompts) * len(cases) * len(models) * runs
    return calls