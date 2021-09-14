def flatten(a):
    return [item for sublist in a for item in sublist]

def idx_self_reference(indices):
    """
    Check Array for Existing: Array[IDX] == [IDX]
    """
    for c, idx in enumerate(indices):
        if c == idx:
            return True
    return False
