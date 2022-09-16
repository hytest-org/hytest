

import numpy as np


def logXform(a, **kwargs):
    if 'clip' in kwargs:
        A = a.clip(kwargs['clip'])
    return np.log(A)

