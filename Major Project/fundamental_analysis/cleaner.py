import numpy as np

def to_float(value):
    try:
        if value in [None, "", "None"]:
            return np.nan
        return float(value)
    except:
        return np.nan


def safe_divide(a, b):
    if b in [0, None] or np.isnan(b):
        return np.nan
    return a / b
