import cartopy
import cartopy.feature as cf
from cartopy import crs as ccrs
from config import *
import dask
import datetime as dt
import geopandas as gpd
import geoviews as gv
import geoviews.feature as gf
from geoviews import opts
import holoviews as hv
import httpx
import hvplot.pandas
import nest_asyncio 
import numpy as np
import pandas as pd
import panel as pn
from pygeohydro import NWIS
import re
import truststore
import ssl

nest_asyncio.apply()
# create SSL context for internal intranet and read file
# this is a method used when calling a library like httpx, urllib3, or requests directly rather than `truststore.inject_into_ssl()`
# ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# states_request = httpx.get("https://www.geoboundaries.org/api/current/gbOpen/USA/ADM1/", verify=ctx)
# truststore.inject_into_ssl()
# states_request = httpx.get("https://www.geoboundaries.org/api/current/gbOpen/USA/ADM1/")

# get GeoJSON link
# states_json = (states_request.json()
#                .get('simplifiedGeometryGeoJSON'))


# nwis class
nwis = NWIS()

states_path = "./data/geoBoundaries-USA-ADM1_simplified.geojson"
path = "./data/streamflow_gages_v1_n5390.csv"

# read GeoJSON file
states = gpd.read_file(states_path)

# states = gpd.read_file(states_json)
states = states[~states['shapeName'].isin(EX_STATES)]
_states_bbox = states.geometry.total_bounds

# set ccrs
mapproj = ccrs.Mercator(central_longitude=0.0, min_latitude=-80.0, max_latitude=84.0, globe=None, latitude_true_scale=0.0)

# Initialize setup for below functions
hv.extension('bokeh')
pn.extension("plotly", "vega")


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
    read_data = pd.read_csv(_filepath, dtype=dict(site_no=str))
    # filter
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    # now turn into a geodataframe
    filtered_gdf = gpd.GeoDataFrame(filtered_data, 
                                    geometry=gpd.points_from_xy(filtered_data.dec_long_va, filtered_data.dec_lat_va), 
                                    crs="EPSG:4326") # most data is exported in EPSG:4326
    return filtered_gdf


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

# Plotting and Servable execution 
stream_gage = _get_data(path)

# Widget setup to select multiple states
state_list = list(states['shapeName'].unique())
#sort alphabetically
state_list.sort()

start_date = pn.widgets.DatePicker(
    # description = "select start date",
    name = "select start date",
    value = dt.date(2001,1,1),
    start = dt.date(2001,1,1),
    end = dt.date.today(),


)
end_date = pn.widgets.DatePicker(
    # description = "select start date",
    name = "select end date",
    value = dt.date.today(),
    start = dt.date(2001,1,1),
    end = dt.date.today(),

)
state_selector = pn.widgets.MultiSelect(
    description="Hold ctrl to toggle multiple states",
    name="Select a state",
    options=state_list,
)
streamgage_input = pn.widgets.TextInput(
    name='Streamgage Site ID', 
    placeholder='Streamgage Site ID #',
    description='Enter a column delimited list e.g. 01022500, 01022502',
    
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
    value = 'OpenStreetMap',
)

subset_selector = pn.widgets.MultiSelect(
    description="Use to select subset",
    name="Select a subset",
    options=STREAMGAGE_SUBSET,
)

def display_streamflow(ids:str) -> pd.DataFrame:
    '''
    display the means stream flow given a set of dates 
    
    Parameters: string of Id's, start and end dates
    Returns: return a pandas dataframe
    '''
    id_list = [pid.strip() for pid in ids.split(",")]
    site_no = id_list[0]
    dates = (start_date.value,end_date.value)
    qobs = nwis.get_streamflow(site_no, dates)
    return qobs 
# create a pn.rx() to allow Panel to link display_streamflow, and streamgage_input
if streamgage_input.value != '':
    displayed_streamflow = pn.rx(display_streamflow)(streamgage_input)


def display_map(map: str) -> gv.WMTS:
    '''
    Display a map, based on the string input to select a base input to overlay beneath the state boundaries polygons object. 

    Parameters:
        map(str): A string for a base map Defaults to `map_selector.value`.

    Returns:
        gv.WMTS: A Tile source type from the GeoViews library.
    '''

    basemap = base_map_options[map]
    return basemap
    
# create a pn.rx() to allow Panel to link map_selector with a Geoviews(Holoviews under the hood) object
displayed_map = pn.rx(display_map)(map_selector)

def display_states(state_list:list)->gv.Polygons:
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
    
# create a pn.rx() to allow Panel to link state_selector with a Geoviews(Holoviews under the hood) object
# replaces @pn.depends
displayed_states = pn.rx(display_states)(state_selector)



def enter_event(event)->None:
    '''
    Event handler function for the 'Enter' button widget.

    Checks if the value entered in the 'streamgage_input' widget contains any non-numeric or non-comma characters. If so, clears the input value of 'streamgage_input',
    clears the value of 'entered_points' widget and sets the placeholder text for 'streamgage_input'. If the input value is valid, updates the value of 'entered_points'
    widget to match the value of 'streamgage_input'.
    
    Parameters:
    event : The input in the textbox for the data set 

    Returns: None
    '''
    sg_value = streamgage_input.value 
    if re.search('[^0-9, ]',sg_value):
        streamgage_input.value = '' 
        entered_points.value = ''
        streamgage_input.placeholder ="Expected Format:[id_no], [id_no2]..."
    else:
        entered_points.value = sg_value
    
enter_id = pn.panel(pn.widgets.Button(name='Enter', button_type='primary'))

enter_id.on_click(enter_event)




def display_points(state_list:list,ids:str, data_set:str)->gv.Points:
    '''
    Create a GeoViews Points object from a GeoDataFrame of streamflow gages.
    
    Parameters:
    state_list (list): A list of US states to display on the map.
    
    Returns:
    A GeoViews Points object containing the streamflow gages.
    '''
    data_set = subset_selector.value
    if len(state_list) > 0:
        ############## if any states have been selected, narrow what is displayed
        filt_states = states[states['shapeName'].isin(state_list)]
        # clip stream_gage to the filtered states
        filt_points = stream_gage.clip(filt_states)
    else:
        filt_points = stream_gage
    if ids:
        # filter stream_gage to only include the specified IDs
        id_list = [pid.strip() for pid in ids.split(",")]
        if (id_list != []):
            filt_points = filt_points[filt_points['site_no'].isin(id_list)]
    if data_set != "":
        filt_points = filt_points[(filt_points[data_set]==1).all(axis=1)] 
    
    selected_points = gv.Points(filt_points).opts(**plot_opts,color='lightgreen', size=5)


    return selected_points

# create a pn.rx() to allow Panel to link state_selector with a Geoviews(Holoviews under the hood) object
# replaces @pn.depends
if streamgage_input.value == '':
    displayed_points =pn.rx(display_points)(state_selector,streamgage_input,subset_selector)
else:
    displayed_points =pn.rx(display_points)(state_selector,entered_points,subset_selector)


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
    streamgage_input.value = ''
    entered_points.value = ''
    
# Template Setup 
clear_map = pn.panel(pn.widgets.Button(name='Reset Map', button_type='primary'))
pn.bind(reset_map, clear_map, watch=True)
footer = pn.pane.Markdown("""For questions about this application, please visit the [Hytest Repo](https://github.com/hytest-org/hytest/issues)""" ,width=500, height =20)


map_modifier = pn.Column(state_selector, map_selector, subset_selector, streamgage_input, enter_id, clear_map, start_date, end_date,sizing_mode='stretch_width')

model_eval = pn.template.FastGridTemplate(
    title="HyTEST Model Evaluation",  
     sidebar=[
        map_modifier,
    ],
)


subset_selector.param.watch(display_points, 'value')
model_eval.main[0:5, 0:12] = pn.pane.HoloViews(displayed_map * displayed_states * displayed_points) # unpack us map onto model_eval
model_eval.main[5:6, 0:12] = footer # unpack footer onto model_eval
model_eval.servable() 
