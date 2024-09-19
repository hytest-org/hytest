import holoviews as hv
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
    start_date = param.Date(default =  dt.date.fromisoformat("2000-05-01"), label = "start date")
    end_date = param.Date(default =  dt.date.fromisoformat("2000-05-02"),label = "End Date")

    #same logic
    def __init__(self, **params):
        super().__init__(**params)
        # self.update_flow_data()

    def getflow(self,site_ids, dates):
        nwis = NWIS()
        dfs = []
        for site_id in site_ids:
            try:
                data = nwis.getflow(site_id, dates)
                if data.empty:
                    continue
                data['site_no'] = site_id
                dfs.append(data)
            except Exception as e:
                print(f"bug")
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs)
    
    @param.depends("site_ids", "start_date", "end_date", watch = True)
    def update_flow_data(self):
        if not self.site_ids or self.start_date or self.end_date:
            return
        dates = (start_date, end_date)
        self.flow_data = self.getflow(site_ids, dates)
    

    
    @param.depends("flow_data", watch = True)
    def plot_streamflow(self):
        curves = []
        ########### FIGURE OUT how to integrate the flow ##########################
        data = pd.DataFrame({"x": [0, 1, 5], "y": [0, 2, 10]})
        bars = hv.Bars(data, ["x"], ["y"])
        return bars
    
    @param.depends("plot_streamflow")
    def view(self):
        return pn.pane.HoloViews(self.plot_streamflow(), sizing_mode = 'stretch_width')
    
flow = FlowPlot()
flow.param.site_ids.objects = ['01021480','01021470']
pn.Row(flow.param,
flow.view


).servable()
