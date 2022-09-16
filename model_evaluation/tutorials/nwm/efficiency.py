# coding: utf-8
# pylint: disable=fixme,line-too-long,invalid-name
#   invalid-name -> We are using 'invalid' variable names like e, and logNSE in order to be compatible
#                   with established usage patterns and matching an existing library elsewhere.
"""

+=====================================+=====================================================================+
| Metric                              | Reference                                                           |
+=====================================+=====================================================================+
| Nash-Sutcliffe efficiency (NSE)     | Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting      |
|                                     | through conceptual models part I—A discussion of principles.        |
|                                     | Journal of hydrology, 10(3), 282-290.                               |
|                                     | https://www.sciencedirect.com/science/article/pii/0022169470902556?via%3Dihub
|                                     |                                                                     |
| Kling-Gupta efficiency (KGE)        | Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).   |
|                                     | Decomposition of the mean squared error and NSE performance         |
|                                     | criteria: Implications for improving hydrological modelling.        |
|                                     | Journal of hydrology, 377(1-2), 80-91.                              |
|                                     | https://www.sciencedirect.com/science/article/pii/S0022169409004843 |
|                                     |                                                                     |
| logNSE                              | Oudin, L., Andréassian, V., Mathevet, T., Perrin, C., & Michel, C.  |
|                                     | (2006). Dynamic averaging of rainfall‐runoff model simulations      |
|                                     | from complementary model parameterizations. Water Resources         |
|                                     | Research, 42(7).                                                    |
|                                     |                                                                     |
+=====================================+=====================================================================+

"""

import numpy as np
from scipy.stats import pearsonr
from .err import rSD, MSE
from .utils import logXform


def KGE(obs, sim) -> float:
    """
    Kling-Gupta efficiency (KGE)

    See: Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009).
            Decomposition of the mean squared error and NSE performance criteria:
            Implications for improving hydrological modelling. Journal of
            hydrology, 377(1-2), 80-91.
|           https://www.sciencedirect.com/science/article/pii/S0022169409004843

    Returns:
        float: Calculated KGE
    """

    r = pearsonr(obs, sim)[0]
    alpha = rSD(obs, sim)
    beta = np.sum(sim) / np.sum(obs)
    return 1 - np.sqrt((r-1)**2 + (alpha-1)**2 + (beta-1)**2)

def NSE(obs, sim) -> float:
    """
    Nash-Sutcliffe efficiency (NSE)

    See: Nash, J. E., & Sutcliffe, J. V. (1970). River flow forecasting through
            conceptual models part I—A discussion of principles. Journal of
            hydrology, 10(3), 282-290.
            https://www.sciencedirect.com/science/article/pii/0022169470902556?via%3Dihub

    Returns:
        float: calculated NSE
    """
    return 1 - (MSE(obs, sim) / np.var(obs, ddof=0))
    # NOTE:  regarding the use of np.var() vs pd.Series.var()
    #  --> Numpy  uses a default ddof=0
    #  --> Pandas uses a default ddof=1
    # so for a pd.Series in my_data, np.var(my_data) will produce a
    # slightly different result than will my_data.var() ...
    # To make the pandas result agree with numpy, we need to
    # explicity use the ddof=0 parameter.  The original codespec for
    # this benchmark series used numpy, so we conform to that as canon.

def logNSE(obs, sim) -> float:
    """
    logNSE - computes NSE using the log of data (rather than data)

    See: Oudin, L., Andréassian, V., Mathevet, T., Perrin, C., & Michel, C. (2006).
            Dynamic averaging of rainfall‐runoff model simulations from complementary
            model parameterizations. Water Resources Research, 42(7).                                                    |

    Returns:
        float: Calculated NSE of log(data)
    """
    return NSE(logXform(obs, clip=0.01), logXform(sim, clip=0.1))
