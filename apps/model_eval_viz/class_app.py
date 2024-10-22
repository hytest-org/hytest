import geopandas as gpd
import geoviews as gv
import holoviews as hv
import pandas as pd
import panel as pn

from config import EX_STATES
from map import Map
from flow import FlowPlot
pn.extension(notifications=True)
hv.extension("bokeh")

# notifications
pn.state.notifications.position = 'top-center'

### PATHS  # noqa: E266
states_path = "./data/geoBoundaries-USA-ADM1_simplified.geojson"
streamgages_path = "./data/streamflow_gages_v1_n5390.csv"

### DATA  # noqa: E266
# read GeoJSON file
def _get_state_data(_filepath: str) -> tuple[gpd.GeoDataFrame, list]:
    """Read in state geographies."""
    # create 
    _states = gpd.read_file(_filepath)
    _states = _states[~_states['shapeName'].isin(EX_STATES)]

    _states_list = list(_states['shapeName'].unique())
    _states_list.sort()

    return _states, _states_list

states_data, states_list = _get_state_data(states_path)

def _get_streamgage_data(_filepath: str) -> gpd.GeoDataFrame:
    """Reads streamflow data from a .csv and filters it based on the 'gagesII_class==ref'."""  # noqa: D401
    # read lat-long or xy data using pandas read_csv
    read_data = pd.read_csv(_filepath, dtype=dict(site_no=str, nldi=int, swim=int, gfv1d1=int))

    # filter
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    # now turn into a geodataframe
    filtered_gdf = gpd.GeoDataFrame(filtered_data,  # noqa: W291
                                    geometry=gpd.points_from_xy(filtered_data.dec_long_va, filtered_data.dec_lat_va),
                                    crs="EPSG:4326"  # most data is exported in EPSG:4326
    )
    return filtered_gdf
streamgage_data = _get_streamgage_data(streamgages_path)
map = Map(states = states_data, streamgages = streamgage_data)
flow = FlowPlot()
# def show_flow_plot(event):
#     x, y = map.stream.x, map.stream.y
#     print(x,y)
#     if not(pd.isna(x) or pd.isna(y)):
#         nearest_point = streamgage_data.geometry.distance(gpd.points_from_xy([x],[y])).idxmin()
#         site_id = streamgage_data.loc(nearest_point,['site_no'])
#         flow.site_id = site_id
#         print(x,y)
# def show_flow_plot(x,y):
#     print(x,y)
#     return pn.pane.Str('Click at %0.3f, %0.3f' % (x, y), width=200)

### WIDGET OPTIONS  # noqa: E266

# tap_map = hv.DynamicMap(show_flow_plot, streams=[map.stream])
# flow = FlowPlot()
# flow.plot_streamflow()
map.param.state_select.objects = states_list
model_eval = pn.template.MaterialTemplate(
    title="HyTEST Model Evaluation",
    sidebar=[
        map.param, flow.param
    ],
    main=[map.view, flow.view],
)

# flow.param.site_ids.objects = ['01021480','01021470']

# model_eval = pn.template.FastGridTemplate(
#     title="HyTEST Model Evaluation",
#     sidebar=[
#         map.param,
#     ],
#     # main=[pn.pane.HoloViews(map.view)],
# )

# model_eval.main.append(map.view)
model_eval.servable()
