# Dask cluster on pangeo.chs.usgs.gov

```python
import os
from dask.distributed import Client
from dask_kubernetes.classic import KubeCluster

_env_to_add={}
aws_env_vars=['AWS_ACCESS_KEY_ID',
              'AWS_SECRET_ACCESS_KEY',
              'AWS_SESSION_TOKEN',
              'AWS_DEFAULT_REGION']
for _e in aws_env_vars:
    if _e in os.environ:
        _env_to_add[_e] = os.environ[_e]


cluster = KubeCluster(env=_env_to_add, n_workers=2)

client = Client(cluster)
```