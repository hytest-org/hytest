import geopandas as gpd
import geoviews as gv
import holoviews as hv
import pandas as pd
import panel as pn
import param

from config import EX_STATES, STREAMGAGE_SUBSET

# pn.extension("bokeh")
pn.extension()
hv.extension("bokeh")
# hv.extension('bokeh')

### PATHS  # noqa: E266
states_path = "./data/geoBoundaries-USA-ADM1_simplified.geojson"
streamgages_path = "./data/streamflow_gages_v1_n5390.csv"

### DATA  # noqa: E266
# read GeoJSON file
states = gpd.read_file(states_path)
states = states[~states['shapeName'].isin(EX_STATES)]

### WIDGET OPTIONS  # noqa: E266
# list of states for selector
states_list = list(states['shapeName'].unique())
states_list.sort()

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

    state_select = param.ListSelector(objects=states_list, default=[], label="Select a State(s)", doc="Press the Ctrl button and left-click to select/deselect multiple states")
    basemap_select = param.Selector(default="OSM", objects=gv.tile_sources.tile_sources.keys(), label="Select a Basemap")
    streamgage_type_filter = param.ListSelector(objects=STREAMGAGE_SUBSET, default=[], label="Filter Streamgages by Type", doc="Press the Ctrl button and left-click to select/deselect multiple types")

    def __init__(self, **params):
        super().__init__(**params)
        self.streamgages = self._get_data(streamgages_path)
        self._filtered_states = gpd.GeoDataFrame()

    @param.depends("state_select", watch=True)
    def _filter_states(self):
        """Filter state geometries."""
        self._filtered_states = states[states['shapeName'].isin(self.state_select)]

    # @param.depends("_filter_states")
    def display_states(self):
        """Display map of states."""
        if not self._filtered_states.empty:
            _states = gv.Polygons(self._filtered_states)
        else:
            _states = gv.Polygons(states)
        return _states

    @param.depends("basemap_select")
    def display_basemap(self):
        """Display basemap."""
        return gv.tile_sources.tile_sources[self.basemap_select]

    # @param.depends("state_select")
    def display_streamgages(self):
        """Display points."""
        if not self._filtered_states.empty:
            streamgages_to_display = self.streamgages.clip(self._filtered_states)
        else:
            streamgages_to_display = self.streamgages

        return gv.Points(streamgages_to_display).options(color="green", size=5)

    @param.depends("display_states", "display_basemap")
    def view(self):
        """Merge map components into display."""
        return pn.pane.HoloViews((self.display_basemap() * self.display_states() * self.display_streamgages()).options(**plot_opts))

    def _get_data(self, _filepath: str) -> gpd.GeoDataFrame:
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


map = Map()
pn.Row(map.param, map.view).servable()
