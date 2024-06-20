import ssl

import cartopy
import cartopy.feature as cf
import dask
import geopandas as gpd
import geoviews as gv
import geoviews.feature as gf
import holoviews as hv
import httpx
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
import truststore
from cartopy import crs as ccrs
from config import *
from geoviews import opts

#================================SETUP=====================================
# create SSL context for internal intranet and read file
# this is a method used when calling a library like httpx, urllib3, or requests directly rather than `truststore.inject_into_ssl()`
# ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# states_request = httpx.get("https://www.geoboundaries.org/api/current/gbOpen/USA/ADM1/", verify=ctx)
# truststore.inject_into_ssl()
# states_request = httpx.get("https://www.geoboundaries.org/api/current/gbOpen/USA/ADM1/")
# get GeoJSON link
# states_json = (states_request.json()
#                .get('simplifiedGeometryGeoJSON'))
states_path = "./data/geoBoundaries-USA-ADM1_simplified.geojson"
# read GeoJSON file
states = gpd.read_file(states_path)
# states = gpd.read_file(states_json)
states = states[~states['shapeName'].isin(EX_STATES)]
# set crs
mapproj = ccrs.PlateCarree()
# Initialize setup for below functions
hv.extension('bokeh')
path = "./data/streamflow_gages_v1_n5390.csv"
pn.extension("plotly", "vega")

#============ Abandon this for now ===================================#
# Create a map template including rough borders for a start 
# gv_us = cf.NaturalEarthFeature(category='cultural', 
#     name='admin_1_states_provinces_lines', scale='50m', facecolor='none')
# gv_us = gv.Feature(gv_us).geoms().opts(
#     line_color="black", line_width=1, line_dash='dashed')
#============ Abandon this for now ===================================#

#=========================================================================


# Read in the dataframe 
def _get_data(_filepath:str)->gpd.GeoDataFrame:
    '''
    Reads streamflow data from a .csv and filters it based on the 'gagesII_class==ref'.
    Args:
        _filepath (str): Path to the .csv file 
    Returns:
        gpd.GeoDataFrame: the filtered geopandas data file
    '''
    read_data = gpd.read_file(_filepath)
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    # clean up long, and lat data
    filtered_data['dec_lat_va'] = filtered_data['dec_lat_va'].str.replace('lat', '').astype(float)
    filtered_data['dec_long_va'] = filtered_data['dec_long_va'].str.replace('long', '').astype(float)
    return filtered_data

# Define data frames 
# gv_us_map = gv.Polygons(gv_us)


state_list = list(states['shapeName'].unique())
# sorted list
state_list.sort()
state_selector = pn.widgets.MultiSelect(
    description="Hold ctrl to toggle multiple states",
    name="Select a state",
    options=state_list,
)

# Plotting configurations
plot_opts = dict(
    #Dimensions, and UI setup
    responsive=True, projection = ccrs.PlateCarree(), width=800, height=600, xlim=(-125, -50), ylim=(5, 50),
    #title
    title='United States Streamgage Map'
)

# Instantiate template
model_eval = pn.template.FastGridTemplate(
    title="HyTEST Model Evaluation",  
)

# Plotting and Servable execution 
stream_gage = _get_data(path)
# Features = gv.Overlay([gf.ocean, gf.land, gf.rivers, gf.lakes, gf.borders, gf.coastline])
# features = gv.Polygons(states, crs=mapproj)

# Widget setup to select multiple states

# @pn.depends(state=' '.join(state_selector.param.options))


# def state_filter(state:str):
#     filtered_states = state.split(' ')
#     return filtered_states

# features: gv.Polygons = gv.Polygons()

@pn.depends(state_selector)
####################### set a default value, wich is the value of state selector
def display_states(state_list:list=state_selector.value)->gv.Polygons:
    """
    Create a GeoViews Polygons object from a GeoDataFrame of US states.
    
    Parameters:
    state_list (list): A list of US states to display on the map.
    
    Returns:
    A GeoViews Polygons object containing the selected US states.
    """

    
    print(state_list)
    
    if len(state_list) > 0:
        ############## if any states have been selected, narrow what is displayed
        filt_states = states[states['shapeName'].isin(state_list)]
        print(filt_states)
        features = gv.Polygons(filt_states, crs=mapproj)
        
    else:
        ############## else return all states
        features = gv.Polygons(states, crs=mapproj)

    return features
    
@pn.depends(state_selector)
def display_points(state_list:list)->gv.Points:
    """
    Create a GeoViews Points object from a GeoDataFrame of streamflow gages.
    
    Parameters:
    state_list (list): A list of US states to display on the map.
    
    Returns:
    A GeoViews Points object containing the streamflow gages.
    """
    #Right now just use all of the points we will change this later
    displayed_points = gv.Points((stream_gage['dec_long_va'],stream_gage['dec_lat_va'])).opts(**plot_opts,color='lightgreen', size=5)
    return displayed_points

@pn.depends(state_selector)
def print_states(state_list:list):
    """
    Print the selected values from the state_selector widget.
    Parameters:
    state_list (list): A list of US states selected in the state_selector widget.
    """
    display_states(state_list)
    print(state_list)

# features = gv.Polygons(states, crs=mapproj)
# points = gv.Points((stream_gage['dec_long_va'],stream_gage['dec_lat_va'])).opts(**plot_opts,color='lightgreen', size=5)

# us_map = (gv_us_map*features).opts(**plot_opts)
# footer = pn.pane.Markdown("""For questions about this application, please visit the [Hytest Repo](https://github.com/hytest-org/hytest/issues)""" ,width=500, height =200)
# us_map_panel = pn.panel(us_map)

model_eval = pn.Column(
    pn.Row(state_selector),

    pn.Row(display_states),
    pn.Row(print_states)
)
model_eval.servable()
