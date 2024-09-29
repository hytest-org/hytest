###
2020-01-01 05:00:00+00:00       1.548932  01021480
2020-01-02 05:00:00+00:00       1.455486  01021480
2020-01-03 05:00:00+00:00       1.396021  01021480
2020-01-04 05:00:00+00:00       1.353545  01021480
2020-01-05 05:00:00+00:00       1.345050  01021480
2020-01-06 05:00:00+00:00       1.254436  01021480
2020-01-07 05:00:00+00:00       1.206298  01021480
2020-01-08 05:00:00+00:00       1.169486  01021480
2020-01-09 05:00:00+00:00       1.093030  01021480
2020-01-10 05:00:00+00:00       1.070377  01021480
###
import pandas as pd
import datetime as dt
from pygeohydro import NWIS
import nest_asyncio
nest_asyncio.apply()


site_ids = ['01021480']
start_date = dt.datetime(2020,1,1)
end_date = dt.datetime(2020,1,10)
dates = (start_date, end_date)
def getflow(site_ids, dates):
        nwis = NWIS()
        dfs = []
        for site_id in site_ids:
            try:
                data = nwis.get_streamflow(site_id, dates)
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
print(flow_data)
