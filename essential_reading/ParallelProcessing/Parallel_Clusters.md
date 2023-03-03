# Parallel / Clusters


dask parallelism makes use of 'clusters' of workers, each of which
is given some task to do.  Cluster configurations vary widely, depending
on the task and the hardware available.  Here are a few of the configurations
that you will see in use.

In each case, we need a handle for the cluster configuration, and a client
by which we can monitor or adjust the cluster.

## Local / Desktop

```python
import os
from dask.distributed import Client, LocalCluster

cluster = LocalCluster(threads_per_worker=os.cpu_count())
client = Client(cluster)
```

## Denali
Denali is treated as a very, very bit desktop.

```python
from dask.distributed import Client, LocalCluster

cluster = LocalCluster(threads_per_worker=1)
client=Client(cluster)
```


## Tallgrass
The SLURM scheduler controls how jobs are dispatched and serviced on the
tallgrass cluster.

```python
try:
    from dask.distributed import Client
    from dask_jobqueue import SLURMCluster
except ImportError as exc:
    raise ImportError("SLURM library not found!!") from exc

cluster = SLURMCluster(
    processes=1,
    cores=1,            #per job
    memory='10GB',      #per job
    interface='ib0',    #network interface for scheduler-worker communication.
    account=os.environ.get('SLURM_JOB_ACCOUNT', "Unknown"),
    walltime='04:00:00',
    job_extra_directives={'hint': 'multithread', 'exclusive':'user'}
    )
client = Client(cluster)
```

## JupyterHub / ESIP-QHUB
For 'cloud' computing platforms, such as the ESIP/QHUB jupyerhub server use
AWS-specific cluster configurations. The physical location of those compute
resurces is left to the cloud provider.
```python
import ebdpy as ebd

ebd.set_credentials(profile='esip-qhub')
aws_profile = 'esip-qhub'
aws_region = 'us-west-2'
endpoint = f's3.{aws_region}.amazonaws.com'
ebd.set_credentials(profile=aws_profile, region=aws_region, endpoint=endpoint)
worker_max = 30
client, cluster = ebd.start_dask_cluster(
    profile=aws_profile,
    worker_max=worker_max,
    region=aws_region,
    use_existing_cluster=True,
    adaptive_scaling=False,
    wait_for_cluster=False,
    worker_profile='Medium Worker',
    propagate_env=True
)
```

