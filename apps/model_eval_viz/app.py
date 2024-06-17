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
# states = gpd.read_file(states_json)
states = gpd.read_file(states_path)

states = states[~states['shapeName'].isin(EX_STATES)]


# set crs
mapproj = ccrs.PlateCarree()



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
    read_data = gpd.read_file(_filepath)
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    # clean up long, and lat data
    filtered_data['dec_lat_va'] = filtered_data['dec_lat_va'].str.replace('lat', '').astype(float)
    filtered_data['dec_long_va'] = filtered_data['dec_long_va'].str.replace('long', '').astype(float)
    return filtered_data

# Define data frames 
gv_us_map = gv.Polygons(gv_us)

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
features = gv.Polygons(states, crs=mapproj)

# Widget setup to select multiple states
state_selector = pn.widgets.MultiSelect(
    description="Hold ctrl to toggle multiple states",
    name="Select a state",

    options=list(states['shapeName'].unique()), 

    value=list(states['shapeName'].unique())

)
@pn.depends(state=state_selector.param.value)

def update_map(state):

    return map_overlay


us_map = (gv_us_map*features).opts(**plot_opts)
points = gv.Points((stream_gage['dec_long_va'],stream_gage['dec_lat_va'])).opts(**plot_opts,color='lightgreen', size=5)
footer = pn.pane.Markdown("""For questions about this application, please visit the [Hytest Repo](https://github.com/hytest-org/hytest/issues)""" ,width=500, height =200)
us_map_panel = pn.panel(us_map)
model_eval.main[0:1,0:7] = state_selector # unpack state selector onto model_eval
model_eval.main[1:4, 0:7] = us_map*points # unpack us map onto model_eval
model_eval.main[4:, 0:7] = footer # unpack footer onto model_eval
model_eval.servable() 

