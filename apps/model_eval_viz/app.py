import cartopy
import cartopy.feature as cf
from cartopy import crs as ccrs
from config import *
import dask
import geopandas as gpd
import geoviews as gv
import geoviews.feature as gf
from geoviews import opts
import holoviews as hv
import httpx
import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
import ssl
import truststore

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
_states_bbox = states.geometry.total_bounds
print(_states_bbox)
# set ccrs
mapproj = ccrs.Mercator(central_longitude=0.0, min_latitude=-80.0, max_latitude=84.0, globe=None, latitude_true_scale=0.0)



# Initialize setup for below functions
hv.extension('bokeh')
path = "./data/streamflow_gages_v1_n5390.csv"
pn.extension("plotly", "vega")

# Create a map template including rough borders for a start 
gv_us = cf.NaturalEarthFeature(category='cultural', 
    name='admin_1_states_provinces_lines', scale='50m', facecolor='none')
gv_us = gv.Feature(gv_us).geoms().opts(
    line_color="black", line_width=1, line_dash='dashed')

# Read in the dataframe 
def _get_data(_filepath:str)->gpd.GeoDataFrame:
    '''
    Reads streamflow data from a .csv and filters it based on the 'gagesII_class==ref'.
    Args:
        _filepath (str): Path to the .csv file 
    Returns:
        gpd.GeoDataFrame: the filtered geopandas data file
    '''
    # read lat-long or xy data using pandas read_csv
    read_data = pd.read_csv(_filepath)
    # filter
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    # now turn into a geodataframe
    filtered_gdf = gpd.GeoDataFrame(filtered_data, 
                                    geometry=gpd.points_from_xy(filtered_data.dec_long_va, filtered_data.dec_lat_va), 
                                    crs="EPSG:4326") # most data is exported in EPSG:4326
    return filtered_gdf

# Define data frames 
gv_us_map = gv.Polygons(gv_us)

# Plotting configurations
plot_opts = dict(
    #Dimensions, and UI setup
    responsive=True, 
    projection = mapproj,
    width=1200, 
    height=600,
    #title
    title='United States Streamgage Map'
)

# Instantiate template

# Plotting and Servable execution 
stream_gage = _get_data(path)

# Widget setup to select multiple states
state_list = list(states['shapeName'].unique())
#sort alphabetically
state_list.sort()
state_selector = pn.widgets.MultiSelect(
    description="Hold ctrl to toggle multiple states",
    name="Select a state",
    options=state_list,
)


base_map_options = {
    'OpenStreetMap': gv.tile_sources.OSM,
    'ESRI Imagery': gv.tile_sources.EsriImagery,
    'ESRI World Street Map': gv.tile_sources.EsriWorldStreetMap,
}

map_selector = pn.widgets.Select(
    description="Use to select Base Map",
    name="Select a Base Map",
    options=list(base_map_options.keys()),

)


def display_map(map:list=map_selector.value)->gv.tile_sources:
    '''
    Display a map from a selected tile source or an initial extent.

    Parameters:
        map (list, optional): List of tile sources to select from. Defaults to `map_selector.value`.

    Returns:
        gv.tile_sources: A Tile source from the GeoViews library.
    '''

    if len(map) > 0:
        map = base_map_options[map_selector.value]
    else:
        #TODO find initial extent states.geometry.total_bounds
        map = gv.tile_sources.OSM
    return map

# create a DynamicMap to allow Panel to link map_selector with a Geoviews(Holoviews under the hood) object
displayed_map = hv.DynamicMap(pn.bind(display_map, map=map_selector))



def display_states(state_list:list=state_selector.value)->gv.Polygons:
    '''
    Create a GeoViews Polygons object from a GeoDataFrame of US states.
    
    Parameters:
    state_list (list): A list of US states to display on the map.
    
    Returns:
    A GeoViews Polygons object containing the selected US states.
    '''  
    if len(state_list) > 0:
        ############## if any states have been selected, narrow what is displayed
        filt_states = states[states['shapeName'].isin(state_list)]
        # filt_states = filt_states.to_crs(mapproj)
        features = gv.Polygons(filt_states).opts(responsive=True, projection = mapproj, framewise = True )
        
    else:
        ############## else return all states
        features = gv.Polygons(states).opts(responsive=True, projection = mapproj, framewise = True )
    return features
    
# create a DynamicMap to allow Panel to link state_selector with a Geoviews(Holoviews under the hood) object
# replaces @pn.depends
displayed_states = hv.DynamicMap(pn.bind(display_states, state_list=state_selector))

def display_points(state_list:list=state_selector.value)->gv.Points:
    '''
    Create a GeoViews Points object from a GeoDataFrame of streamflow gages.
    
    Parameters:
    state_list (list): A list of US states to display on the map.
    
    Returns:
    A GeoViews Points object containing the streamflow gages.
    '''
    if len(state_list) > 0:
        ############## if any states have been selected, narrow what is displayed
        filt_states = states[states['shapeName'].isin(state_list)]
        # clip stream_gage to the filtered states
        filt_points = stream_gage.clip(filt_states)
        # create a gv.Points
        displayed_points = gv.Points(filt_points).opts(**plot_opts,color='lightgreen', size=5)
                                     
    else:
        displayed_points = gv.Points(stream_gage).opts(**plot_opts,color='lightgreen', size=5)

    return displayed_points

# create a DynamicMap to allow Panel to link state_selector with a Geoviews(Holoviews under the hood) object
# replaces @pn.depends
displayed_points = hv.DynamicMap(pn.bind(display_points, state_list=state_selector))


def reset_map(event:bool)-> None:
    '''
    Reset the state selector when an event is triggered.
    Args:
        event (bool): A boolean flag to trigger the function.

    Returns:
        None.
    '''
    if not event:
        return
    state_selector.value = []

reset_button = pn.panel(pn.widgets.Button(name='Reset Map', button_type='primary'))
pn.bind(reset_map, reset_button, watch=True)
footer = pn.pane.Markdown("""For questions about this application, please visit the [Hytest Repo](https://github.com/hytest-org/hytest/issues)""" ,width=500, height =20)
map_modifier = pn.Row(state_selector, map_selector, reset_button, sizing_mode='stretch_width')

model_eval = pn.template.FastGridTemplate(
    title="HyTEST Model Evaluation",  
     main=[
        map_modifier,
    ]
)
model_eval.main[1:5, 0:9] = pn.pane.HoloViews(displayed_map * displayed_states * displayed_points) # unpack us map onto model_eval
model_eval.main[5:6, 0:9] = footer # unpack footer onto model_eval
model_eval.servable() 
