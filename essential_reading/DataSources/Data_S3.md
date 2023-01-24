# Data / Cloud Storage

One of the main storage locations for HyTest data is in '_The Cloud_'. This is sometimes referred to as **'Object Storage'**.
The data is kept in datacenters operated by Amazon, Microsoft, or similar, which makes it easily available to network-connected devices.
The main advantage of doing this is that if your compute engine is also in that same datacenter (or nearby, as is the case with many JupyterHub services),
the data doesn't have to go very far to get to the compute power.
This brings the computation to the data, rather than shipping large datasets across the internet to get to the compute engine.

[S3](https://aws.amazon.com/s3/) is Amazon's implementation of object storage, which pairs with the Amazon (AWS) nodes on which the Jupter Hub runs.
What follows is a brief demo of how S3 data is accessed (both read and write), and some pitfalls to watch out for.

The permissions scheme for S3 allows for anonymous/global read access, as well as secured access via specific credentials.
We'll look at generic workflows using an anonymous-access store, then finish off with some private/credentialed operations.

The easiest way to access S3 data from within a Python program is via the
[fsspec](https://filesystem-spec.readthedocs.io/en/latest/) module.
This is a layer of abstraction that lets us interact with arbitrary storage mechanisms as if
they are conventional file systems. It makes S3 'look' like a conventional file system.

## Anonymous Reads

A lot of data is available for global read, which does not require credentials or a profile.
In this case, we set `anon=True` when plumbing the `fsspec` object:

```python
fs = fsspec.filesystem(
    's3',
    anon=True   # Does not require credentials
    )
# 'fs' is an object which provides methods access to the virtual filesystem
# 'ls' method == list ; list files in a virtual folder to test if we really have access
fs.ls('s3://noaa-nwm-retrospective-2-1-zarr-pds/')
```

Output:

```text
['noaa-nwm-retrospective-2-1-zarr-pds/chrtout.zarr',
 'noaa-nwm-retrospective-2-1-zarr-pds/gwout.zarr',
 'noaa-nwm-retrospective-2-1-zarr-pds/lakeout.zarr',
 'noaa-nwm-retrospective-2-1-zarr-pds/ldasout.zarr',
 'noaa-nwm-retrospective-2-1-zarr-pds/precip.zarr',
 'noaa-nwm-retrospective-2-1-zarr-pds/rtout.zarr']
```

We can call other methods on the `fsspec` object "`fs`" to interact with filesystem objects.

```python
fs.info('s3://noaa-nwm-retrospective-2-1-zarr-pds/index.html')
```

Output:

```text
{'Key': 'noaa-nwm-retrospective-2-1-zarr-pds/index.html',
'LastModified': datetime.datetime(2021, 10, 1, 20, 48, 48, tzinfo=tzutc()),
'ETag': '"3b4b4277037c1127ed4ba68e26461b2e"',
'Size': 32357,
'StorageClass': 'STANDARD',
'type': 'file',
'size': 32357,
'name': 'noaa-nwm-retrospective-2-1-zarr-pds/index.html'}
```

Low-level operations with `fsspec` are designed to behave similarly to the 'native' file operations in Python.

```python
# Use open() to get something that behaves like a file handle for
# low-level Python read/write operations:
with fs.open('s3://noaa-nwm-retrospective-2-1-zarr-pds/index.html') as f:
    # print first 5 lines...
    for i in range(0, 5):
        line = f.readline()
        print(line)
```

Output:

```text
b'<!DOCTYPE html>\r\n'
b'\r\n'
b'<!--\r\n'
b'Copyright 2014-2018 Amazon.com, Inc. or its affiliates. All Rights Reserved.\r\n'
b'\r\n'
```

However -- most of the time, we don't need such low level access.
A more general, and useful, mechanism is to '_map_' an S3 object to a _virtual file_ using `get_mapper()`.
That _map_ object can then be treated as if it is a local file -- the `fsspec` mapping mechanism handles
all of the translation to interact with S3.

```python
m = fs.get_mapper('s3://noaa-nwm-retrospective-2-1-zarr-pds/chrtout.zarr')
# 'm' looks like a file as far as Python is concerned.
# It is now a stand-in for those functions that require a file as argument.
g = zarr.convenience.open_consolidated(m) # read zarr metadata for named file.
print(g.tree())
```

Output:

```text
/
 ├── crs () |S1
 ├── elevation (2776738,) float32
 ├── feature_id (2776738,) int32
 ├── gage_id (2776738,) |S15
 ├── latitude (2776738,) float32
 ├── longitude (2776738,) float32
 ├── order (2776738,) int32
 ├── streamflow (367439, 2776738) int32
 ├── time (367439,) int64
 └── velocity (367439, 2776738) int32
```

:::{warning}

We are deliberately demonstrating using commands that read **only** the zarr metadata from the
object storage -- **not the full data set**.

The above example is a very, _very_, **very** large dataset, which you don't want to load over the network to your desktop.
Execute full data read operations only if this notebook is being hosted and run out of the same AWS center where the data lives.

:::

:::{sidebar}

The good news about some of the larger science-oriented libraries (xarray, dask, pandas, zarr, etc), is that
they can automatically handle the `fsspec` operations for you **IF YOUR ACCESS IS ANONYMOUS**.
This is a convenience, but is a special case for read-only data where `anon=True` and `requestor_pays=False`.

Note that this is a feature of
[specific libraries](https://filesystem-spec.readthedocs.io/en/latest/#who-uses-fsspec),
and doesn't work everywhere.

Because it isn't universally available, and only applies to anonymous reads, examples in HyTEST will
always explicitly plumb `fsspec` 'longhand' using `get_mapper()`. You may see example code elsewhere
that takes the shortcut if it is available.

:::


## Credentialed Access

For most data storage within the HyTEST workflows, access will not be anonymous.
Permissions are set by the owners of that data, using credentials assigned to an AWS 'profile'.

Profile credentials are usually stored outside of the Python program (typically in a master file in
your ``HOME` folder on the compute/jupyter server).
You need to have this set up beforehand, and is usually achieved by copying specific credential files into the right spot.
A common mechanism to handle the profile configuration is with the `aws`
[command line interface](https://awscli.amazonaws.com/v2/documentation/api/latest/reference/configure/index.html).

To create a new AWS profile:

```sh
> aws configure --profile osn-renci
AWS Access Key ID :
AWS Secret Access Key :
Default region name : us-east-1
Default output format: json
```

The first two prompts will ask for key/security information you were assigned for access to object storage.
Answer last questions with "us-east-1" (region) and "json" (format).

Note that this configuration is specific to the OSN 'pod' storage.
Your profile name and region may be different.

## Endpoints

For storage operations, the AWS system needs the web address of the access point, or _endpoint_
where it should address filesystem operations. If your storage is completely within the Amazon
ecosystem, you will likely not need to specify an endpoint.
However, for 3rd-party storage (such as the OSN pod), you will need to explicitly declare the
endpoint when the filesystem is first referenced using `fsspec`.

```python
fs_write = fsspec.filesystem(
    's3',
    profile='osn-renci',  ## This is the profile name you configured above.
    client_kwargs={'endpoint_url': 'https://renc.osn.xsede.org'}
)
```

The enpoint URL will be given to you when your key ID and access key are assigned.

## Writing Data to S3

With greater permissions, you may be able to do more destructive activities (overwriting, removing, etc).
Examples:

* `mkdir` -- makes a new directory / folder
* `mv` -- moves/renames a file or folder
* `rm` -- removes a file or folder

See the [API documentation](https://filesystem-spec.readthedocs.io/en/latest/api.html)
for the full details of available operations.

## Read-only access with "requestor pays"

Some datasets, such as the first example above (anonymous reading), are offered with 'egress fees' paid by the data owner.
This means that all access is free to anybody.
The cost of the network bandwidth used to serve the data is covered by the data's host.
Not all "public" data is offered this way: it is still available to anybody who wants to read it, but
the access fees must be paid by the reador (i.e. the 'requestor').

When you access a requestor-pays dataset, your profile identifies the account which will be
billed for access.  Open such datasets with an extra option to `fsspec`:

```python
fs = fsspec.filesystem(
    's3',
    profile='osn-renci',
    anon=False,
    requestor_pays=True
)
fs.ls('s3://esip-qhub/noaa/nwm/')
```

The `fsspec` call identifies how you will be interacting with object storage (your identity and what
you are willing to pay for).  File-system operations using that `fs` handle will be made using that
configuration.
