import holoviews as hv
hv.extension("bokeh")

import pandas as pd

from pygeohydro import NWIS
import panel as pn
import param
import datetime as dt
from datetime import timedelta

import nest_asyncio
nest_asyncio.apply()

#Plotting ops 1/4 the size of the map
flow_plot_opts = dict(
    width=300,
    height=150,
    title='Flow Plot',
    xaxis=None,
    yaxis=None
)

class FlowPlot(param.Parameterized):
    """Instantiate flow map """
    flow_data = param.DataFrame(precedence=-1)
    site_ids = param.ListSelector(default=[], label = "select site ids")
    start_date = param.Date(default =  dt.datetime(2020,1,1) ,label = "Start Date")
    end_date = param.Date(default =  dt.datetime(2020,1,10),label = "End Date")

    #same logic
    def __init__(self, **params):
        super().__init__(**params)

    #Destroy for loop just do a single ID
    def getflow(self, site_ids, dates):
        nwis = NWIS()
        data = nwis.get_streamflow(site_ids, dates)
        return data
    
    @param.depends("site_ids", "start_date", "end_date", watch = True)
    def update_flow_data(self):
        start_date = self.start_date
        end_date = self.end_date
        dates = (start_date, end_date)
        id = self.site_ids[0]
        dates = (start_date, end_date)
        self.flow_data = self.getflow(id, dates)

    
    @param.depends("flow_data", watch = True)
    def plot_streamflow(self):
        if self.flow_data is None or self.flow_data.empty:
            return hv.Curve([]).opts(**flow_plot_opts)

        curves = []
        for column in self.flow_data.columns:
            curve = hv.Curve(self.flow_data[column]).opts(title=f"Streamflow for {column}", xlabel='Date', ylabel='Flow Value')
            curves.append(curve)

        return hv.Overlay(curves).opts(legend_position='right')

    @param.depends("plot_streamflow")
    def view(self):
        return pn.pane.HoloViews(self.plot_streamflow(), sizing_mode = 'stretch_width')
    
