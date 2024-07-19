import datetime as dt

import cartopy
import cartopy.feature as cf
import geopandas as gpd
import geoviews as gv
import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn
from cartopy import crs as ccrs

from app import *
from config import *

# this file deals with the logic involving the geometry, and fit of the base map.


def display_map(map: str) -> gv.WMTS:
    """

    Display a map, based on the string input to select a base input to overlay beneath the state boundaries polygons object.

    Parameters:
        map(str): A string for a base map Defaults to `map_selector.value`.

    Returns:
        gv.WMTS: A Tile source type from the GeoViews library.
    """
    basemap = base_map_options[map]
    return basemap


def display_states(state_list: list) -> gv.Polygons:
    """
    Create a GeoViews Polygons object from a GeoDataFrame of US states.

    Parameters:
    state_list (list): A list of US states to display on the map.

    Returns:
    A GeoViews Polygons object containing the selected US states.
    """
    if len(state_list) > 0:
        # if any states have been selected, narrow what is displayed
        filt_states = states[states["shapeName"].isin(state_list)]
        # filt_states = filt_states.to_crs(mapproj)
        features = gv.Polygons(filt_states).opts(responsive=True, projection=mapproj, framewise=True)

    else:
        # else return all states
        features = gv.Polygons(states).opts(responsive=True, projection=mapproj, framewise=True)
    return features


def reset_map(event: bool) -> None:
    """
    Reset the state selector when an event is triggered.

    Args:
        event (bool): A boolean flag to trigger the function.

    Returns:
        None.
    """
    if not event:
        return
    state_selector.value = []
    streamgage_input.value = ""
    entered_points.value = ""
