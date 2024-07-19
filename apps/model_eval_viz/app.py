import datetime as dt
import re
import ssl

import cartopy
import cartopy.feature as cf
import geopandas as gpd
import geoviews as gv
import geoviews.feature as gf
import holoviews as hv
import httpx
import hvplot.pandas
import nest_asyncio
import numpy as np
import pandas as pd
import panel as pn
import truststore
from cartopy import crs as ccrs
from geoviews import opts
from pygeohydro import NWIS

from config import *
from data_logic import _get_data, display_points, display_streamflow, enter_event
from map_logic import display_map, display_states, reset_map
from widgets import *

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


states_path = "./data/geoBoundaries-USA-ADM1_simplified.geojson"
path = "./data/streamflow_gages_v1_n5390.csv"

# read GeoJSON file
states = gpd.read_file(states_path)

# states = gpd.read_file(states_json)
states = states[~states["shapeName"].isin(EX_STATES)]
_states_bbox = states.geometry.total_bounds

# set ccrs
mapproj = ccrs.Mercator(
    central_longitude=0.0, min_latitude=-80.0, max_latitude=84.0, globe=None, latitude_true_scale=0.0
)

# Initialize setup for below functions
hv.extension("bokeh")
pn.extension("plotly", "vega")

# Plotting configurations
plot_opts = dict(
    # Dimensions, and UI setup
    responsive=True,
    projection=mapproj,
    width=1200,
    height=600,
    # title
    title="United States Streamgage Map",
)

# Plotting and Servable execution
stream_gage = _get_data(path)

# Widget setup to select multiple states
state_list = list(states["shapeName"].unique())
# sort alphabetically
state_list.sort()


# create a pn.rx() to allow Panel to link display_streamflow, and streamgage_input
if streamgage_input.value != "":
    displayed_streamflow = pn.rx(display_streamflow)(streamgage_input)

# create a pn.rx() to allow Panel to link map_selector with a Geoviews(Holoviews under the hood) object
displayed_map = pn.rx(display_map)(map_selector)

# create a pn.rx() to allow Panel to link state_selector with a Geoviews(Holoviews under the hood) object
# replaces @pn.depends
displayed_states = pn.rx(display_states)(state_selector)

enter_id = pn.panel(pn.widgets.Button(name="Enter", button_type="primary"))

enter_id.on_click(enter_event)


# create a pn.rx() to allow Panel to link state_selector with a Geoviews(Holoviews under the hood) object
# replaces @pn.depends
if streamgage_input.value == "":
    displayed_points = pn.rx(display_points)(state_selector, streamgage_input, subset_selector)
else:
    displayed_points = pn.rx(display_points)(state_selector, entered_points, subset_selector)

# Template Setup
clear_map = pn.panel(pn.widgets.Button(name="Reset Map", button_type="primary"))
pn.bind(reset_map, clear_map, watch=True)
footer = pn.pane.Markdown(
    """For questions about this application, please visit the [Hytest Repo](https://github.com/hytest-org/hytest/issues)""",
    width=500,
    height=20,
)
map_modifier = pn.Column(
    state_selector,
    map_selector,
    subset_selector,
    streamgage_input,
    enter_id,
    clear_map,
    start_date,
    end_date,
    sizing_mode="stretch_width",
)

model_eval = pn.template.FastGridTemplate(
    title="HyTEST Model Evaluation",
    sidebar=[
        map_modifier,
    ],
)

subset_selector.param.watch(display_points, "value")
model_eval.main[0:5, 0:12] = pn.pane.HoloViews(
    displayed_map * displayed_states * displayed_points
)  # unpack us map onto model_eval
model_eval.main[5:6, 0:12] = footer  # unpack footer onto model_eval
model_eval.servable()
