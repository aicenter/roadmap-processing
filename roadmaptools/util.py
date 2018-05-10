

def filter_dict(input_dict: dict, keys: set):
    """
    Return a copy of input dictionary that contains only the specified keys.

    """
    out_dict = dict()
    for key in keys:
        if key in input_dict.keys():
            out_dict[key] = input_dict[key]

    return out_dict