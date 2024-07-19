import datetime as dt

import geopandas as gpd
import geoviews as gv
import holoviews as hv
import numpy as np
import pandas as pd
import panel as pn

from app import *
from config import *
from map_logic import *

# this file contains all the widgets and their default values

start_date = pn.widgets.DatePicker(
    # description = "select start date",
    name="select start date",
    value=dt.date(2001, 1, 1),
    start=dt.date(2001, 1, 1),
    end=dt.date.today(),
)
entered_points = pn.widgets.TextInput(
    name="Streamgage Site ID",
    placeholder="Streamgage Site ID #",
)
end_date = pn.widgets.DatePicker(
    # description = "select start date",
    name="select end date",
    value=dt.date.today(),
    start=dt.date(2001, 1, 1),
    end=dt.date.today(),
)
state_selector = pn.widgets.MultiSelect(
    description="Hold ctrl to toggle multiple states",
    name="Select a state",
    options=state_list,
)
streamgage_input = pn.widgets.TextInput(
    name="Streamgage Site ID",
    placeholder="Streamgage Site ID #",
    description="Enter a column delimited list e.g. 01022500, 01022502",
)
base_map_options = {
    "OpenStreetMap": gv.tile_sources.OSM,
    "ESRI Imagery": gv.tile_sources.EsriImagery,
    "ESRI World Street Map": gv.tile_sources.EsriWorldStreetMap,
}

map_selector = pn.widgets.Select(
    description="Use to select Base Map",
    name="Select a Base Map",
    options=list(base_map_options.keys()),
    value="OpenStreetMap",
)

subset_selector = pn.widgets.MultiSelect(
    description="Use to select subset",
    name="Select a subset",
    options=STREAMGAGE_SUBSET,
)
