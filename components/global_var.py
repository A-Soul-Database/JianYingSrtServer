def __init__():
    global __global_dict
    __global_dict = {}

def set(name, value):
    __global_dict[name] = value

def get(name, defValue=None):
    try:
        return __global_dict[name]
    except KeyError:
        return defValue