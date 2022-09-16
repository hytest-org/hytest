# coding: utf-8
# pylint: disable=fixme,line-too-long,invalid-name
#   invalid-name -> We are using 'invalid' variable names like e, and logNSE in order to be compatible
#                   with established usage patterns and matching an existing library elsewhere.
"""

+=====================================+=====================================================================+
| Metric                              | Reference                                                           |
+=====================================+=====================================================================+
| percent bias in midsegment slope of | Yilmaz, K. K., Gupta, H. V., & Wagener, T. (2008). A process‐based  |
| the flow-duration curve (FDC)       | diagnostic approach to model evaluation: Application to the NWS     |
| between Q20-Q70                     | distributed hydrologic model. Water Resources Research, 44(9).      |
|                                     |                                                                     |
| percent bias in FDC low-segment     | Yilmaz, K. K., Gupta, H. V., & Wagener, T. (2008). A process‐based  |
| volume (Q0-Q30)                     | diagnostic approach to model evaluation: Application to the NWS     |
|                                     | distributed hydrologic model. Water Resources Research, 44(9).      |
|                                     |                                                                     |
| percent bias in FDC high-segment    | Yilmaz, K. K., Gupta, H. V., & Wagener, T. (2008). A process‐based  |
| volume (Q98-Q100)                   | diagnostic approach to model evaluation: Application to the NWS     |
|                                     | distributed hydrologic model. Water Resources Research, 44(9).      |
+=====================================+=====================================================================+

"""

import logging
import numpy as np

def pBiasRR(obs, sim) -> float:
    """
    percent bias -- a measure of the mean tendency of simulated values to be
    greater than or less than associated observed values.

    Returns:
        float: calculated percent bias / units = percent (i.e. 90 rather than 0.90)

    Math:
    See equation A1 from Yilmaz et al.
    .. math::
        100 × \frac{\displaystyle\sum_{i=1}^{n}(\hat{x}_{i} - x_{i})}{\sum_{i=1}^{n}x_{i}}

    """
    return 100 * np.sum(sim - obs) / np.sum(obs)

def pBiasFMS(obs, sim) -> float:
    """
    calculates percent bias of the slope the mid-segment of FDC.

    Returns:
        float: percent bias for values in exceedence probability range 0.2-0.7

    The Math:
    See eqn A2 from Yilmaz
    .. math::
        100 × \cfrac{ [log(QS_{m1}) - log(QS_{m2})] - [log(QO_{m1}) - log(QO_{m2})] }
                        { [log(QO_{m1}) - log(QO_{m2})] }
    """
    # Exceedence = 1 - percentile  //  percentile = 1 - exceedence
    # mid-segment slope is defined as those observations with flow exceedence probabilities between 20% and 70%.
    # This leads to percentiles/quantiles of 30% and 80% to establish the cut-offs
    #
    QO_m1, QO_m2 = np.quantile(obs, [0.30, 0.80])
    QS_m1, QS_m2 = np.quantile(sim, [0.30, 0.80])
    m = np.log(QS_m1) - np.log(QS_m2)
    o = np.log(QO_m1) - np.log(QO_m2)
    return 100 * (m - o ) / o

def pBiasFHV(obs, sim) -> float:
    """
    calculates percent bias over the high-flow segment volume.

    Returns:
        float:

    The Math:
    See eqn A3 from Yilmaz
    .. math::
        100 × \cfrac{\displaystyle\sum_{h=1}^H(QS_h - QO_h)}{\displaystyle\sum_{h=1}^H QO_h}

    The range 'h' from 1-H is those indices for exceedence probababilities between 0 and 2%
    """
    # Exceedence = 1 - percentile  //  percentile = 1 - exceedence
    # 'High-Volume' is defined as those observations with flow exceedence probabilities between 0 and 2%.
    # This leads to percentiles/quantiles of 98% and 100% to establish the cut-offs
    #
    minval, maxval = np.quantile(obs, [0.98, 1.0])
    idx = (obs >= minval) & (obs <= maxval)
    QS_h = sim[idx]
    QO_h = obs[idx]
    # standard pbias over these observations
    return 100 * ( (QS_h - QO_h).sum() / QO_h.sum() )

def pBiasFLV(obs, sim) -> float:
    """
    calculates percent bias over the low-flow segment volume.
    Note that for low-flow observations a log transform is done before the
    pbias calculation.

    Returns:
        float: percent bias for values in exceedence probability range 0.7-1.0

    The Math
    See eqn A4 from Yilmaz
    .. math::
        \%BiasFHV = -100 × \cfrac{
                    \displaystyle\sum_{l=1}^L[log(QS_l) - log(QS_L)] -
                    \displaystyle\sum_{l=1}^L[log(QO_l) - log(QO_l)]
                }{
                    \displaystyle\sum_{l=1}^L[log(QO_l) - log(QO_L)]
        }
    """
    # Exceedence = 1 - percentile  //  percentile = 1 - exceedence
    # Low-Volume is defined as those observations with flow exceedence probabilities between 70% and 100%.
    # This leads to percentiles/quantiles of 0% and 30% to establish the cut-offs
    #

    _, QO_L = np.quantile(obs, [0.0, 0.30])
    _, QS_L = np.quantile(sim, [0.0, 0.30])
    idx = (obs <= QO_L)

    QS_l = sim[idx]
    QO_l = obs[idx]
    m = np.sum(np.log(QS_l) - np.log(QS_L))
    o = np.sum(np.log(QO_l) - np.log(QO_L))
    return -100 * (( m - o ) / o)
