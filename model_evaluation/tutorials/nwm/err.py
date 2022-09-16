# coding: utf-8
# pylint: disable=fixme

from decimal import DivisionByZero
import numpy as np
import logging


def MSE(obs, sim) -> float:
    """
    Mean Square Error --   Compute MSE over all paired values obs (x) and mod (x_hat)
        .. math::
            \displaystyle\sum_{i=1}^{n}(x_i - \hat{x}_i)^2

    Returns
    -------
    float
        Mean square error
    """
    err = obs - sim
    return np.mean(err**2)


def rMSE(obs, sim) -> float:
    """
    root mean square error

    Returns
    -------
    float
        square root of MSE()
    """
    return np.sqrt(MSE(obs, sim))


def rSD(obs, sim) -> float:
    """
    ratio of standard deviation  -- standard deviation of simulated/modeled
    values divided by the standard deviation of observed values

    Returns:
        float: calculated ratio
    """
    try:
        return np.std(sim) / np.std(obs)
    except DivisionByZero:
        logging.warning("std dev of observed is zero; ratio undefined")
        return None

def mae(obs, sim) -> float:
    return np.mean(np.abs(sim-obs))

def me(obs, sim) -> float:
    return np.mean(sim - obs)

def nrMSE(obs, sim, norm='sd'):
    if norm not in ['sd', 'maxmin']:
        logging.warning("Unknown normalization method '%s'.  Using default 'sd'", norm)
        norm = 'sd'
    cte = {
        'sd': np.std(obs),
        'maxmin': np.max(obs) - np.min(obs),
    }
    r = rMSE(obs, sim)
    try:
        return np.round((r / cte[norm]) * 100, 1)
    except DivisionByZero:
        logging.warning("'obs' is constant: not able to normalize rMSE.")
        return None

def RSR(obs, sim) -> float:
    """
    _summary_

    Returns
    -------
    _type_
        _description_

    Reference
    ---------
        Moriasi, D.N., Arnold, J.G., Van Liew, M.W., Bingner, R.L., Harmel,
        R.D., Veith, T.L. 2007. Model evaluation guidelines for systematic
        quantification of accuracy in watershed simulations.
        Transactions of the ASABE. 50(3):885-900.
    """
    try:
        return rMSE(obs, sim) / np.std(obs)
    except DivisionByZero:
        logging.warning("std dev of observed is zero; ratio undefined")
        return None

def ssq(obs, sim) -> float:
    """
    Parameters
    ----------
    obs : _type_
        _description_
    sim : _type_
        _description_

    Returns
    -------
    float
        _description_
    """
    return np.sum((sim - obs)**2)