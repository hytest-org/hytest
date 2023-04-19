# Dask Cluster on Tallgrass HPC

```python
import os
import logging

from dask.distributed import Client
from dask_jobqueue import SLURMCluster   

try:
    project = os.environ['SLURM_JOB_ACCOUNT']
except KeyError:
    logging.error("SLURM_JOB_ACCOUNT is not set in the active environment. Are you on the login node? You should not be running this there.")
    raise

cluster = SLURMCluster(
    processes=1, 
    cores=1, 
    memory='8GB', 
    interface='ib0',
    project=project, 
    walltime='01:00:00',      
    job_extra={'hint': 'multithread'},
    shared_temp_directory='/caldera/hytest_scratch/tmp'
)
cluster.adapt(minimum=2, maximum=30)

client = Client(cluster)

    
print("The 'cluster' object can be used to adjust cluster behavior.  i.e. 'cluster.adapt(minimum=10)'")
print("The 'client' object can be used to directly interact with the cluster.  i.e. 'client.submit(func)' ")
print(f"The link to view the client dashboard is:\n>  {client.dashboard_link}")
```