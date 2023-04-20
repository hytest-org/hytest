# Dask Cluster on Denali HPC

```python
import os
import logging

from dask.distributed import LocalCluster, Client

## Denali is treated like a very, very, very big PC.  
cluster = LocalCluster(threads_per_worker=1)
client = Client(cluster)
    
print("The 'cluster' object can be used to adjust cluster behavior.  i.e. 'cluster.adapt(minimum=10)'")
print("The 'client' object can be used to directly interact with the cluster.  i.e. 'client.submit(func)' ")
print(f"The link to view the client dashboard is:\n>  {client.dashboard_link}")
```