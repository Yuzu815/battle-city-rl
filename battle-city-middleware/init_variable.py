import builtins
import copy
from copy import deepcopy
from numbers import Number

from pandas import api, DataFrame

mutable = (dict, list, set, DataFrame)
immutable = (str, tuple, frozenset, Number)


def is_built_in_type(var):
    return type(var).__name__ in dir(builtins)


def is_mutable(var):
    return var is not None and (api.types.is_list_like(var) or isinstance(var, mutable) or not is_built_in_type(var))


def is_immutable(var):
    return var is None or isinstance(var, immutable)


def default(number, value=None):
    if is_mutable(value):
        return [deepcopy(value) for _ in range(number)]
    elif is_immutable(value):
        return [value] * number
    else:
        raise ValueError("Unexpected value type")


def duplicate(value, n):
    return [copy.deepcopy(value) for _ in range(n)]
