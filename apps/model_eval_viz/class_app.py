import geopandas as gpd
import geoviews as gv
import holoviews as hv
import pandas as pd
import panel as pn
import param

from config import EX_STATES, STREAMGAGE_SUBSET

pn.extension()
hv.extension("bokeh")

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

# states = gpd.read_file(states_path)
# states = states[~states['shapeName'].isin(EX_STATES)]

def _get_streamgage_data(_filepath: str) -> gpd.GeoDataFrame:
    """Reads streamflow data from a .csv and filters it based on the 'gagesII_class==ref'."""  # noqa: D401
    # read lat-long or xy data using pandas read_csv
    read_data = pd.read_csv(_filepath, dtype=dict(site_no=str))
    # filter
    filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    # now turn into a geodataframe
    filtered_gdf = gpd.GeoDataFrame(filtered_data,  # noqa: W291
                                    geometry=gpd.points_from_xy(filtered_data.dec_long_va, filtered_data.dec_lat_va),
                                    crs="EPSG:4326"  # most data is exported in EPSG:4326
    )
    return filtered_gdf

streamgage_data = _get_streamgage_data(streamgages_path)

### WIDGET OPTIONS  # noqa: E266
# list of states for selector
# states_list = list(states['shapeName'].unique())
# states_list.sort()

### Plot opts  # noqa: E266
plot_opts = dict(
    # Dimensions, and UI setup
    # responsive=True,
    width=1200,
    height=600,
    title='United States Streamgage Map'
)


class Map(param.Parameterized):
    """Instantiate map of CONUS."""

    states = param.DataFrame(precedence=-1)
    streamgages = param.DataFrame(precedence=-1)
    state_select = param.ListSelector(objects=states_list, default=[], label="Select a State(s)", doc="Press the Ctrl button and left-click to select/deselect multiple states")
    basemap_select = param.Selector(default="OSM", objects=gv.tile_sources.tile_sources.keys(), label="Select a Basemap")
    streamgage_type_filter = param.Selector(objects=STREAMGAGE_SUBSET, default="all", label="Filter Streamgages by Type")

    def __init__(self, **params):
        super().__init__(**params)
        # self.streamgages = self._get_streamgage_data(streamgages_path)
        # self._filtered_states = gpd.GeoDataFrame()
        # # self._filtered_streamgages = gpd.GeoDataFrame()
        # self.states = self._get_state_data(states_path)

    # @param.depends("state_select", watch=True)
    # def _filter_state_selection(self):
    #     """Filter state geometries."""
    #     if self.state_select:
    #         self._filtered_states = self.states[self.states['shapeName'].isin(self.state_select)]
    #         self.streamgages = self.streamgages.clip(self.states)
    #     else:
    #         self.streamgages = self._get_streamgage_data(streamgages_path)
    #         self.states = self._get_state_data(states_path)

    @param.depends("state_select", watch=True)
    def display_states(self):
        """Display map of states."""
        # if not self._filtered_states.empty:
        if self.state_select:
            _states = gv.Polygons(self.states[self.states['shapeName'].isin(self.state_select)])
        else:
            _states = gv.Polygons(self.states)
        return _states

    @param.depends("basemap_select")
    def display_basemap(self):
        """Display basemap."""
        return gv.tile_sources.tile_sources[self.basemap_select]

    @param.depends("state_select", "streamgage_type_filter", watch=True)
    def display_streamgages(self):
        """Display points."""
        if self.state_select:
            if not self.streamgage_type_filter == "all":
                column = self.streamgage_type_filter
                print("column: ", column)
                streamgages_to_display = self.streamgages.clip(self.states[self.states['shapeName'].isin(self.state_select)])
                print("Is change from all firing?")
                print("Before")
                print(streamgages_to_display.shape)
                streamgages_to_display = streamgages_to_display[streamgages_to_display[column] == 1]
                print("After")
                print(streamgages_to_display.shape)
                return gv.Points(streamgages_to_display).options(
            cmap="Plasma",
            color="camels",
            size=5)
            else:
                print("is all firing")
                streamgages_to_display = self.streamgages.clip(self.states[self.states['shapeName'].isin(self.state_select)])
                return gv.Points(streamgages_to_display).options(
            cmap="Plasma",
            color="camels",
            size=5)
        else:
            streamgages_to_display = self.streamgages
            return gv.Points(streamgages_to_display).options(
            cmap="Plasma",
            color="camels",
            size=5)

        # return gv.Points(streamgages_to_display).options(
        #     cmap="Plasma",
        #     color="camels",
        #     size=5)

    # @param.depends("streamgage_type_filter", watch=True)
    # def _filter_streamgages_by_type(self):
    #     """Filter streamgages by type selected."""
    #     if not self.streamgage_type_filter == "all":
    #         column = self.streamgage_type_filter
    #         if self._filtered_streamgages.empty:
    #             self._filtered_streamgages = self.streamgages[self.streamgages[column] == 1]
    #         else:
                # print(f"COLUMN = {column}")
                # print("filtered streamgages columsn", self._filtered_streamgages.columns)
                # print(f"Filterd Streamgages", self._filtered_streamgages)
                # self._filtered_streamgages = self._filtered_streamgages[self._filtered_streamgages[column] == 1]
        # else:
        #     if 
        #     return

    @param.depends("display_states", "display_basemap")
    def view(self):
        """Merge map components into display."""
        return pn.pane.HoloViews(self.display_basemap() * self.display_states() * self.display_streamgages().options(**plot_opts))

    # def _get_streamgage_data(self, _filepath: str) -> gpd.GeoDataFrame:
    #     """Reads streamflow data from a .csv and filters it based on the 'gagesII_class==ref'."""  # noqa: D401
    #     # read lat-long or xy data using pandas read_csv
    #     read_data = pd.read_csv(_filepath, dtype=dict(site_no=str))
    #     # filter
    #     filtered_data = read_data[read_data['gagesII_class'] == 'Ref']
    #     # now turn into a geodataframe
    #     filtered_gdf = gpd.GeoDataFrame(filtered_data,  # noqa: W291
    #                                     geometry=gpd.points_from_xy(filtered_data.dec_long_va, filtered_data.dec_lat_va),
    #                                     crs="EPSG:4326"  # most data is exported in EPSG:4326
    #     )
    #     return filtered_gdf

    # def _get_state_data(self, _filepath: str) -> gpd.GeoDataFrame:
    #     """Read in state geographies."""
    #     _states = gpd.read_file(_filepath)
    #     _states = _states[~_states['shapeName'].isin(EX_STATES)]

    #     return _states


map = Map(states = states_data, streamgages = streamgage_data)
# pn.Column(pn.Row(map.param, map.view), map.streamgage_type_filter).servable()

model_eval = pn.template.MaterialTemplate(
    title="HyTEST Model Evaluation",
    sidebar=[
        map.param,
    ],
    # main=[pn.pane.HoloViews(map.view)],
)
# model_eval = pn.template.FastGridTemplate(
#     title="HyTEST Model Evaluation",
#     sidebar=[
#         map.param,
#     ],
#     # main=[pn.pane.HoloViews(map.view)],
# )

model_eval.main.append(map.view)
model_eval.servable()
# print(help(pn.template.FastGridTemplate))
