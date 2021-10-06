import contextlib
from multiprocessing import Pool
from tqdm.auto import tqdm


def flatten(a):
    return [item for sublist in a for item in sublist]


def distinct(a):
    return list(dict.fromkeys(sorted(a)))


def distinct_list_of_dicts(dic_list, key):
    return list({x[key]: x for x in dic_list}.values())
    # return list({key(x) for x in dic_list}.values())


def includes_excludes_filter(string, includes, excludes):
    for exclude in excludes:
        if exclude in string:
            return False

    for include in includes:
        if include in string:
            return True

    return False


def idx_self_reference(indices):
    """
    Check Array for Existing: Array[IDX] == [IDX]
    """
    for c, idx in enumerate(indices):
        if c == idx:
            return True
    return False

def filter_not_none(lst):
    return filter(lambda x: x is not None, lst)

def filter_is_dir(lst):
    return filter(lambda x: x.is_dir(), lst)
