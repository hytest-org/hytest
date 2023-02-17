import numpy as np
import xarray as xr

from typing import Union   # , Dict, Optional


# ===================================
# Vapor pressure formulas
# ===================================
def vp(qv: Union[float, xr.Dataset, xr.DataArray],
       pressure: Union[float, xr.Dataset, xr.DataArray]):
    """Water vapor pressure from mixing ratio and pressure

    :param qv: Water vapor mixing ratio [kg kg-1]
    :param pressure: Pressure [Pa]
    """
    # ACTION: OK
    # NOTE: Suggested in Milly DRB spreadsheet
    # NOTE: Slightly different from suggestion in WRF forum: https://forum.mmm.ucar.edu/phpBB3/viewtopic.php?t=9134#:~:text=Re%3A%20relative%20humidity&text=The%20Relative%20Humidity%20(RH)%20is,you%20can%20easily%20obtain%20RH.
    # NOTE: Used by Teten relative humidity formula
    epsilon = 0.622  # Rd / Rv; []

    # Sometimes qv (from WRF) is negative; we don't want this
    max_qv = np.maximum(qv, 0.0)

    # Avoid problems where e is near zero
    e = np.maximum(max_qv * pressure / (epsilon + max_qv), 0.001)
    return e


# ===================================
# Saturation vapor pressure formulas
# ===================================
def saturation_vp_bolton(temperature: Union[float, xr.Dataset, xr.DataArray]):
    """Saturation vapor pressure from Bolton formula (1980)

    :param temperature: Temperature [K]
    """
    # Note: This is the formulation used for sat vp in the relative humidity
    #       computation suggested in the WRF forum.
    #       https://forum.mmm.ucar.edu/phpBB3/viewtopic.php?t=9134#:~:text=Re%3A%20relative%20humidity&text=The%20Relative%20Humidity%20(RH)%20is,you%20can%20easily%20obtain%20RH.

    es0 = 611.2   # Saturation vapor pressure reference value; [Pa]
    svp2 = 17.67
    svp3 = 29.65
    svpt0 = 273.15   # [K]

    es = es0 * np.exp(svp2 * (temperature - svpt0) / (temperature - svp3))
    return es


def saturation_vp_magnus(temperature: Union[float, xr.Dataset, xr.DataArray]):
    """Magnus saturation vapor pressure formula

    :param temperature: Temperature [K]
    """

    # Lawrence (2005), eqn 6
    # Relative error less than 0.4% over -40C <= t <= 50C

    c1 = 610.94   # [Pa]
    a1 = 17.625
    b1 = 243.04   # [C]

    temp_c = temperature - 273.15
    es = c1 * np.exp(a1 * temp_c / (b1 + temp_c))

    print(f'{es=}')
    return es


def saturation_vp_teten(temperature: Union[float, xr.Dataset, xr.DataArray]):
    """Teten's formula for saturation vapor pressure from temperature

    :param temperature: Temperature [K]
    """
    # ACTION: OK
    es0 = 6.113  # Saturation vapor pressure reference value; [hPa]
    es0 *= 100   # [Pa]

    temp_c = temperature - 273.15   # [C]

    # Saturation vapor pressure
    es = es0 * np.exp(17.269 * temp_c / (temp_c + 237.3))   # [Pa]
    return es


# def compute_saturation_vp(temperature: Union[float, xr.Dataset, xr.DataArray]):
#     """Saturation vapor pressure from temperature
#
#     :param temperature: Temperature [K]
#     """
#     # Compute saturation vapor pressure from T2
#
#     # equation from Milly's DRB spreadsheet
#     return 611 * np.exp(17.269 * (temperature - 273.15) / (temperature - 35.85))


# ===================================
# Relative humidity formulas
# ===================================
def rh(qv: Union[float, xr.Dataset, xr.DataArray],
       pressure: Union[float, xr.Dataset, xr.DataArray],
       temperature: Union[float, xr.Dataset, xr.DataArray]):
    """Relative humidity

    :param qv: Water vapor mixing ratio [kg kg-1]
    :param pressure: Surface pressure [Pa]
    :param temperature: Temperature [K]
    """

    # NOTE: from wrf_user.f (NCL)
    # Saturation vapor pressure
    temp_c = temperature - 273.15   # [C]
    den1 = temperature - 29.65
    es = 6.112 * np.exp(17.67 * temp_c / den1)   # [Pa]

    # Saturation water vapor mixing ratio
    num2 = 0.622 * es
    den2 = 0.01 * pressure - 0.378 * es
    qvs = num2 / den2

    # Specific humidity
    sh = qv / qvs

    # Relative humidity
    return 100 * np.maximum(np.minimum(sh, 1.0), 0.0)


def rh_teten(qv: Union[float, xr.Dataset, xr.DataArray],
             pressure: Union[float, xr.Dataset, xr.DataArray],
             temperature: Union[float, xr.Dataset, xr.DataArray]):
    """Relative humidity using Teten's formula

    :param qv: Water vapor mixing ratio [kg kg-1]
    :param pressure: Surface pressure [Pa]
    :param temperature: Temperature [K]
    """
    # ACTION: OK
    # Vapor pressure
    e = vp(qv, pressure)   # [Pa]
    # e = (qv * pres) / (epsilon + qv)   # [Pa]

    # Saturation vapor pressure
    es = saturation_vp_teten(temperature)   # [Pa]

    # Relative humidity
    return 100.0 * (e / es)   # 0-100%


# ===================================
# Specific humidity formulas
# ===================================
def specific_humidity(qv: Union[float, xr.Dataset, xr.DataArray]):
    """Specific humdity from water vapor mixing ratio

    :param qv: Water vapor mixing ratio [kg kg-1]"""
    # ACTION: OK
    return qv / (1 + qv)


# ===================================
# Dewpoint temperature formulas
# ===================================

# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!!!
# !~ from WRF phys/module_diag_functions.F
# !~ Name:
# !~    calc_Dewpoint
# !~
# !~ Description:
# !~    This function approximates dewpoint given temperature and rh.
# !~
# !!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~!!!
# FUNCTION calc_Dewpoint ( tC, rh) result( Dewpoint )
#   !~ Variable Declaration
#   !  --------------------
#   real, intent ( in ) :: tC
#   real, intent ( in ) :: rh
#   real                :: Dewpoint
#
#   real :: term, es, e1, e, logs, expon
#
#   expon    = ( 7.5*tC ) / ( 237.7+tC )
#   es       = 6.112 * ( 10**expon )     ! Saturated vapor pressure
#   e        = es * ( rh/100.0 )         ! Vapor pressure
#   logs     = LOG10 ( e/6.112 )
#   Dewpoint = ( 237.7*logs ) / ( 7.5-logs )
#
# END FUNCTION calc_Dewpoint


def dewpoint_temperature(temperature: Union[float, xr.Dataset, xr.DataArray],
                         vapor_pressure: Union[float, xr.Dataset, xr.DataArray],
                         sat_vp: Union[float, xr.Dataset, xr.DataArray]):
    """Dewpoint temperature

    :param temperature: Temperature [K]
    :param vapor_pressure: Vapor pressure [Pa]
    :param sat_vp: Saturation vapor pressure [Pa]
    """

    #  237.3 * X / ( 17.269 - X ) ;  where X = { ln ( E2 / ESAT2 ) + 17.269 * ( T2 - 273.15 ) / ( T2 - 35.85 ) }
    # equation from Milly's DRB spreadsheet
    x = np.log(vapor_pressure / sat_vp) + 17.269 * (temperature - 273.15) / (temperature - 35.85)
    return 237.3 * x / (17.269 - x)


def dewpoint_temperature_magnus(qv: Union[float, xr.Dataset, xr.DataArray],
                                pressure: Union[float, xr.Dataset, xr.DataArray]):
    """Dewpoint temperature based on Magnus formula

    :param qv: Water vapor mixing ratio [kg kg-1]
    :param pressure: Pressure [Pa]
    """

    # Lawrence (2005), eqn 7
    c1 = 610.94   # [Pa]
    a1 = 17.625
    b1 = 243.04   # [C]

    # Vapor pressure
    e = vp(qv, pressure)

    # Dewpoint temperature
    return (b1 * np.log(e / c1)) / (a1 - np.log(e / c1)) + 273.15   # [K]


def solar_radiation_acc(ac_var, bucket_var):
    return ac_var + bucket_var
