# Clusters and AWS Credentials

Parallel processing using clusters of nodes will pose special challenges when
dealing with managing the AWS credentials needed to access object storage on S3.
The main issue is that separate workers in the cluster must have their own
copy of the credentials, and may not be able to retrieve them for themselves.
An example of this behaviour is the cluster configuration on a cloud platform
such as the ESIP/QHUB deployment.

## Cloud Cluster Workers

A 'cloud' deployment will often deploy a cluster of worker nodes using
kubernetes. Each of the workers operates on a separate node (think of this as
if it is a separate virtual host), within a memory image which is created/copied
at run time.  A typical code block to do this on esip/qhub might look like
this:

```python
from dask_gateway import Gateway
gateway = Gateway()
options = gateway.cluster_options()
options.conda_environment='users/pangeo'
options.profile = 'Medium Worker'
cluster = gateway.new_cluster(options)
cluster.adapt(minimum=10, maximum=30)

# get the client for the cluster
client = cluster.get_client()
print(client.dashboard_link)
```
Esip/qhub uses a dask "Gateway" as the mechanism to interact with the cluster
of kubernetes workers. Each of the workers in this node gets a copy of the
running program, executed within the conda environment as specified in the
cluster options.

It is critical to understand that those workers get a copy of the program
*only* and run it in a lightweight Docker container holding the conda
environment.  Cluster workers under this scheme do **NOT** get a copy of the
operating system, and they do not have access to a file system. Individual
cluster workers cannot read or write to (for example) `/home/username/file.txt`
because `/home` is not availabie; no filesystems are available to node
workers on a cloud cluster.

What does this mean for AWS credentials?  Typicall, those credentials are
read from a special configuration file in your home folder (`/home/username/.aws/credentials`).
Your interactive session in the jupyter notebook will be able to read that, but
**NONE** of the workers in the cluster will be able to.  We have to pass
AWS credentials to workers another way.

### Watch out for "Automatic" Profile Parsing

Some of the python libraries you may use will hide/automate much of the detail
for setting AWS credentials.  Take, for example this common way to get access
to an S3 object store:

```python
fs_read = fsspec.filesystem('s3', profile='my-profile-name', requestor-pays=True)
```

The `fsspec` library will automatically consult the AWS configuration (most often
by reading `/home/username/.aws/credentials` to set credentials based on the
profile name.) If that statement is executed in a cloud worker with no other
preparation, `fsspec` won't be able to resolve the profile name to credentials
using your `.aws/credentials` file (because workers don't have access to the
filesystem).

### AWS Credentials as Environment Variables

The common way to do give workers AWS credentials is to configure manually
and store them in special "environment" variables.  Environment variables are
a part of the part of the execution environment which holds the running
program -- so they are included in the memory footprint of the program/script.
This will be duplicated to all workers when they begin execution. The trick,
then, is to correctly set up those environment variables in advance.

We can do this if we manually parse the credentials file and set environment
variables based on what we find.

```python
import os
import configparser
awsconfig = configparser.ConfigParser()
awsconfig.read(
    os.path.expanduser('~/.aws/credentials') # default location...
    # if yours is elsewhere, change this path.
)
_profile_nm  = 'osn-renci'
_endpoint = 'https://renc.osn.xsede.org'
# Set environment vars based on parsed awsconfig
# NOTE that the _profile_nm key must exist as a section in the config file.
os.environ['AWS_ACCESS_KEY_ID']     = awsconfig[_profile_nm]['aws_access_key_id']
os.environ['AWS_SECRET_ACCESS_KEY'] = awsconfig[_profile_nm]['aws_secret_access_key']
os.environ['AWS_S3_ENDPOINT']       = _endpoint
try:
    # Obliterate any reference to a profile.
    del os.environ['AWS_PROFILE']
except KeyError:
    pass
```

It is very important to note that you should **NEVER** manually hard-code `AWS_SECRET_ACCESS_KEY`.
Always parse it from a secrets file or the AWS config file. If you hard-code that value, it will
persist in your code--which, if ever shared, will give away your access password.

Note the warning in the above code block: the profile name must exist in the
credentials file as a 'section'.  If you look at the config file, that would
look like this:

```text
[osn-renci]
aws_access_key_id = ABC123ABC12ABC123
aws_secret_access_key = qwertyuiop2asdfghjkl1zxcvbnm
```

Your key ID and access key will be different, of course. If you don't have a
'section' for the named profile, the `configparser` will not be able to
retrieve the values it needs.

### Environment Established

Now that the environment holds values for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and
other important values, the environment will propagate those values for any in-memory copies
of the program, including spawned cluster workers.

```python
fs_write = fsspec.filesystem('s3',
                         anon=False, # force a consult to environment vars set above.
                         skip_instance_cache=True,
                         client_kwargs={'endpoint_url': os.environ['AWS_S3_ENDPOINT']}
                         # NOTE: no profile mentioned.
                        )
fname='s3://bucketname/path/to/your/dataset.zarr'
fs_write.ls(os.path.dirname(fname))
```

### Complete Cluster Setup for Cloud

To set up your cluster to take advantage of these environment variables, do this:

```python
from dask_gateway import Gateway
gateway = Gateway()
options = gateway.cluster_options()
options.conda_environment='users/pangeo'
options.profile = 'Medium Worker'
### SET os.environ as above AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, and AWS_S3_ENDPOINT
options.environment_vars = dict(os.environ)
#  ^^^^^^^^^^^^^^^^^^^^^^     This tells the cluster what OS Environment variables
# you want to propagate.  This example propagates *ALL* os.environ variables.
cluster = gateway.new_cluster(options)
cluster.adapt(minimum=10, maximum=30)

# get the client for the cluster
client = cluster.get_client()
print(client.dashboard_link)
```

### Trust, but Verify
The following simple code block with verify what a cluster worker thinks of
as the AWS credential:

```python
def myAWS_Credentials():
    return os.environ.get('AWS_ACCESS_KEY_ID', '<not set>')

print(myAWS_Credentials())
# This will print the credentials used in the notebook environment

print(client.submit(myAWS_Credentials).result())
# This will print the credentials used on an anonymous worker node in the cluster.
```

If those two values are different, then the workers are operating with
different credentials than the notebook environment. Verify that the OS
environment variables are set correctly **before** starting the cluster
and attaching a gateway client.
