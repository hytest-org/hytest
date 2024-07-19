import datetime as dt

import geopandas as gpd
import geoviews as gv
import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn

from app import *
from config import *

# this file deals with the logic involving the data, and displaying said data


def display_points(state_list: list, ids: str, data_set: str) -> gv.Points:
    """
    Create a GeoViews Points object from a GeoDataFrame of streamflow gages.

    Parameters:
    state_list (list): A list of US states to display on the map.

    Returns:
    A GeoViews Points object containing the streamflow gages.
    """
    data_set = subset_selector.value
    if len(state_list) > 0:
        # if any states have been selected, narrow what is displayed
        filt_states = states[states["shapeName"].isin(state_list)]
        # clip stream_gage to the filtered states
        filt_points = stream_gage.clip(filt_states)
    else:
        filt_points = stream_gage
    if ids:
        # filter stream_gage to only include the specified IDs
        id_list = [pid.strip() for pid in ids.split(",")]
        if id_list != []:
            filt_points = filt_points[filt_points["site_no"].isin(id_list)]
    if data_set != "":
        filt_points = filt_points[(filt_points[data_set] == 1).all(axis=1)]

    selected_points = gv.Points(filt_points).opts(**plot_opts, color="lightgreen", size=5)

    return selected_points


def display_streamflow(ids: str) -> pd.DataFrame:
    """

    display the means stream flow given a set of dates

    Parameters: string of Id's, start and end dates
    #TODO: changing return value later
    Returns: return a string of info of streamgage
    """
    id_list = [pid.strip() for pid in ids.split(",")]
    site_no = id_list[0]
    dates = (start_date.value, end_date.value)
    qobs = nwis.get_streamflow(site_no, dates)
    return qobs


def enter_event(event) -> None:
    """

    Event handler function for the 'Enter' button widget.

    Checks if the value entered in the 'streamgage_input' widget contains any non-numeric or non-comma characters. If so, clears the input value of 'streamgage_input',
    clears the value of 'entered_points' widget and sets the placeholder text for 'streamgage_input'. If the input value is valid, updates the value of 'entered_points'
    widget to match the value of 'streamgage_input'.

    Parameters:
    event : The input in the textbox for the data set

    Returns: None
    """
    sg_value = streamgage_input.value
    if re.search("[^0-9, ]", sg_value):
        streamgage_input.value = ""
        entered_points.value = ""
        streamgage_input.placeholder = "Expected Format:[id_no], [id_no2]..."
    else:
        entered_points.value = sg_value


# Read in the dataframe
def _get_data(_filepath: str) -> gpd.GeoDataFrame:
    """

    Read streamflow data from a .csv and filter it based on the 'gagesII_class==ref'.

    Parameters:
        _filepath (str): Path to the .csv file

    Returns:
        gpd.GeoDataFrame: the filtered geopandas data file
    """
    # read lat-long or xy data using pandas read_csv
    read_data = pd.read_csv(_filepath, dtype=dict(site_no=str))
    # filter
    filtered_data = read_data[read_data["gagesII_class"] == "Ref"]
    # now turn into a geodataframe
    filtered_gdf = gpd.GeoDataFrame(
        filtered_data, geometry=gpd.points_from_xy(filtered_data.dec_long_va, filtered_data.dec_lat_va), crs="EPSG:4326"
    )  # most data is exported in EPSG:4326
    return filtered_gdf
