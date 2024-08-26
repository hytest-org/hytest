import re

import geoviews as gv
import panel as pn
import param

from config import STREAMGAGE_SUBSET

### Plot opts  # noqa: E266
map_plot_opts = dict(
    width=1200,
    height=600,
    title='United States Streamgage Map',
    xaxis=None,
    yaxis=None
)


class Map(param.Parameterized):
    """Instantiate map of CONUS."""

    states = param.DataFrame(precedence=-1)
    streamgages = param.DataFrame(precedence=-1)
    state_select = param.ListSelector(default=[], label="Select a State(s)", doc="Press the Ctrl button and left-click to select/deselect multiple states")
    basemap_select = param.Selector(default="OSM", objects=gv.tile_sources.tile_sources.keys(), label="Select a Basemap")
    streamgage_type_filter = param.Selector(objects=STREAMGAGE_SUBSET, default="all", label="Filter Streamgages by Type")
    streamgage_id_input = param.String(doc='Enter a column delimited list e.g. 01022500, 01022502', label='Streamgage Site ID')
    streamgage_id_string = param.String(precedence=-1, default="")
    search_streamgage_id_input = param.Event(label="Search IDs")
    clear_streamgage_id_input = param.Event(label="Clear IDs")
    reset_map = param.Event(label="Reset Map")

    def __init__(self, **params):
        super().__init__(**params)

    @param.depends("state_select")
    def display_states(self):
        """Display map of states."""
        if self.state_select:
            _states = gv.Polygons(self.states[self.states['shapeName'].isin(self.state_select)])
        else:
            _states = gv.Polygons(self.states)
        return _states

    @param.depends("basemap_select")
    def display_basemap(self):
        """Display basemap."""
        return gv.tile_sources.tile_sources[self.basemap_select]

    @param.depends("state_select", "streamgage_type_filter", "streamgage_id_string", watch=True)
    def display_streamgages(self):
        """Display points."""
        # give precedence to streamgage_id_input search
        if len(self.streamgage_id_string) > 0:
            id_list = [pid.strip() for pid in self.streamgage_id_string.split(",")]
            streamgages_to_display = self.streamgages[self.streamgages['site_no'].isin(id_list)]
        else:
            column = self.streamgage_type_filter
            if column != "all":
                streamgages_to_display = self.streamgages[self.streamgages[column] == 1]
            else:
                streamgages_to_display = self.streamgages

            if len(self.state_select) > 0:
                streamgages_to_display = (streamgages_to_display.clip(self.states[self.states['shapeName'].isin(self.state_select)]))

        return gv.Points(streamgages_to_display).options(
            cmap="Plasma",  # stand in and will be changed later
            color="complete_yrs",  # stand in and will be changed later
            size=5)  # stand in and will be changed later

    @param.depends("display_states", "display_basemap", "display_streamgages")
    def view(self):
        """Merge map components into display."""
        return pn.pane.HoloViews(self.display_basemap() * self.display_states() * self.display_streamgages().options(**map_plot_opts))

    # buttons
    @param.depends("search_streamgage_id_input", watch=True)
    def _update_streamgage_input(self):
        if re.search('[^0-9, ]', self.streamgage_id_input):
            pn.state.notifications.warning("Search included invalid characters. Please see the tooltip (?) for correct formatting.", duration=5000)
        else:
            self.streamgage_id_string = self.streamgage_id_input

    @param.depends("clear_streamgage_id_input", watch=True)
    def _clear_streamgage_input(self):
        self.streamgage_id_string = ""
        self.streamgage_id_input = ""

    @param.depends("reset_map", watch=True)
    def _reset_map(self):
        # loop through all params
        for par in self.param:
            # reset params with inputs
            if par not in ["name", "streamgages", "states", "search_streamgage_id_input", "clear_streamgage_id_input", "reset_map"]:
                setattr(self, par, self.param[par].default)
