# Parallel / Clusters

`dask` parallelism makes use of 'clusters' of individual workers.
Each worker is given some task to do, and typically operates in a lightweight environment (i.e. it does
not always have full access to the full system, notably the local filesystem).

Cluster configurations vary widely, depending on the task and the hardware available.
Here are a few of the configurations that you might see with HyTEST workflows.
In each case, we need a handle for the cluster configuration, and a client by which we can monitor or adjust the cluster.

## JupyterHub / ESIP-QHUB / Nebari

These names refer to different implementations of a 'JupyterHub' model.
This model hosts compute resources in the cloud, and offeres a Jupyter Lab interface by which that compute
environment is accessed.
The physical location of those compute resources is left to the cloud provider.

The vast majority of workflows you will find in the HyTEST repo will be written to run in this sort of environment.
The main trick to clusters in this enironment is to correctly configure workers such that they have a place
to write data (assuming that they need to), with adequate permissions. This means that AWS S3 credentials must
be configured for the cluster before the workers are created.

```python
import configparser
awsconfig = configparser.ConfigParser()
awsconfig.read(
    os.path.expanduser('~/.aws/credentials') # default location... if yours is elsewhere, change this.
)
_profile_nm  = 'osn-renci'
_endpoint = 'https://renc.osn.xsede.org'
# Set environment vars based on parsed awsconfig
os.environ['AWS_ACCESS_KEY_ID']     = awsconfig[_profile_nm]['aws_access_key_id']
os.environ['AWS_SECRET_ACCESS_KEY'] = awsconfig[_profile_nm]['aws_secret_access_key']
os.environ['AWS_S3_ENDPOINT']       = _endpoint
try:
    del os.environ['AWS_PROFILE']
except KeyError:
    pass

## to open a filesystem (IF NEEDED):
fs_write = fsspec.filesystem(  ## Note that no profile is specified... fsspec honors env variables.
    's3',
    skip_instance_cache=True,
    client_kwargs={'endpoint_url': _endpoint}
)
```

The above code merely sets up your credentials (identified by the profile name) in _environment
variables_. Unlike the file system, your python execution environment (and env variables) propagates
to cluster workers.

Note that if your cluster workers do not need to write any data to S3 or ready any `requester_pays` data,
then credentials likely won't need to be set at all.

Now you can spin up a cluster of workers:

```python
from dask_gateway import Gateway
gateway = Gateway()
options = gateway.cluster_options()
options.conda_environment='users/users-pangeo'  ##<< this is the conda environment we use on nebari.
options.profile = 'Medium Worker'
options.environment_vars = dict(os.environ)     ##<< copies env vars including AWS_* to worker env
cluster = gateway.new_cluster(options)          ##<< create cluster
cluster.adapt(minimum=2, maximum=30)

# get the client for the cluster
client = cluster.get_client()
client.dashboard_link                           ##<< prints the URL to monitor cluster activity
```

## Hosted Clusters

Each of the cluster options below will run on systems which do have access to a file system.
This means (among other things) that they won't necessarily need to have AWS credentials
configured in order to read and write data.

### Local / Desktop

Cluster workers can be made to operate on any host, even your desktop. The pool of resources will
be much more limited, so this is an unlikely configuration -- but it is possible

```python
import os
from dask.distributed import Client, LocalCluster

cluster = LocalCluster(threads_per_worker=os.cpu_count())
client = Client(cluster)
```

### Denali

Denali is treated as a very, very big desktop.

```python
from dask.distributed import Client, LocalCluster

cluster = LocalCluster(threads_per_worker=1)
client=Client(cluster)
```

### Tallgrass

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
