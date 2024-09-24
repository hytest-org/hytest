
import pandas as pd
import datetime as dt
from pygeohydro import NWIS
import nest_asyncio
nest_asyncio.apply()


site_ids = ['01021480']
start_date = dt.datetime(2020,1,1)
end_date = dt.datetime(2020,1,10)
dates = (start_date, end_date)
def getflow(self,site_ids, dates):
        nwis = NWIS()
        dfs = []
        for site_id in site_ids:
            try:
                data = nwis.getflow(site_id, dates)
                if data.empty:
                    continue
                if data is None:
                    continue 
                data['site_no'] = site_id
                dfs.append(data)
            except Exception as e:
                print(f"bug")
        if not dfs:
            return pd.DataFrame()
        return pd.concat(dfs)
print(f"Dates {dates}")
flow_data = getflow(site_ids, dates)
print(flow_date.head())
