
#import numpy as np
from scipy.stats import spearmanr, pearsonr

def pearson_r(obs, sim) -> float:
    """
    Pearson Correlation -- Pearson's R, calculated using the scipi library method


    Returns
    -------
    float
        Pearson's R

    Reference
    ---------
    Pearson (1896, 1900, 1920)
    """
    return pearsonr(obs, sim)[0]


def spearman_r(obs, sim) -> float:
    """
    Spearman Correlation == Spearman's R, calcuated using the scipy method

    Returns
    -------
    float
        Calculated R

    Reference
    --------
    Charles Spearman (1904, 1910)                                       |
    """
    return spearmanr(obs, sim)[0]
