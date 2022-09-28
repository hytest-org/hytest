# DASK jobqueue

Details for connecting the dask job queue to the SLURM scheduler on `tallgrass`.  We use `dask-jobqueue` on `tallgrass` because there are only a few CPUs per node and we are often sharing them.  The job queue service within dask helps with equitable distribution of work.

```python
import os
from dask_jobqueue import SLURMCluster

project = os.environ.get('SLURM_JOB_ACCOUNT', "Unknown")
cluster = SLURMCluster(
    processes=1,
    cores=1,
    memory='10GB',
    interface='ib0',
    project=project,
    walltime='01:00:00',
    job_extra={'hint': 'multithread', 'exclusive': 'user'}
)
cluster.scale(10)

from dask.distributed import Client
client = Client(cluster)
```

The `scale()` method submits a batch of jobs to the SLURM job queue system.
Depending on how busy the job queue is, it can take a few minutes for workers
to join your cluster. You can usually check the status of your queued jobs
using a command line utility like `squeue -u $USER`. You can also check the
status of your cluster from inside your Jupyter session:

For more examples of how to use `dask-jobqueue`, refer to the
[package documentation](http://dask-jobqueue.readthedocs.io).

## Further Reading

* [Deploying Dask on HPC](http://dask.pydata.org/en/latest/setup/hpc.html)
* [Configuring and Deploying Jupyter Servers](http://jupyter-notebook.readthedocs.io/en/stable/index.html)
