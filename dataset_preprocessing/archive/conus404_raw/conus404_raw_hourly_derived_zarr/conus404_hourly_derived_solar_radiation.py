#!/usr/bin/env python

import argparse
import dask
import datetime
import fsspec
import os
import pandas as pd
import time
import xarray as xr
import zarr.storage

from numcodecs import Zstd   # , Blosc
from dask.distributed import Client

import conus404_helpers as ch
import conus404_maths as cmath


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized zarr files for CONUS404 derived variables')
    parser.add_argument('-i', '--index', help='Index to process', type=int, required=True)
    parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-s', '--src_zarr', help='Path to source zarr dataset', required=True)
    parser.add_argument('--step', help='Number of indices to process from start index', type=int, default=1)

    args = parser.parse_args()

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    print(f'SLURMD_NODENAME: {os.environ.get("SLURMD_NODENAME")}')

    base_dir = os.path.realpath(args.base_dir)
    dst_zarr = f'{ch.set_target_path(args.src_zarr, base_dir)}'

    print(f'{base_dir=}')
    print(f'{dst_zarr=}')
    print('-'*60)

    base_date = datetime.datetime(1979, 10, 1)
    num_days = 6
    delta = datetime.timedelta(days=num_days)

    # We specify a chunk index and the start date is selected based on that
    index_start = args.index
    index_span = args.step
    index_end = index_start + index_span

    st_date = base_date + datetime.timedelta(days=num_days * index_start)

    if (st_date - base_date).days % num_days != 0:
        print(f'Start date must begin at the start of a {num_days}-day chunk')

    print(f'{base_date=}')
    print(f'{st_date=}')
    print(f'{num_days=}')
    print(f'{delta=}')
    print(f'{index_start=}')
    print('-'*60)

    time_chunk = num_days * 24

    # Start up the cluster
    # client = Client(n_workers=8, threads_per_worker=1, memory_limit='24GB')
    client = Client()

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}')

    # Read variables to process
    # df = pd.read_csv(proc_vars_file)

    fs = fsspec.filesystem('file')

    start = time.time()

    # Change the default compressor to Zstd
    # NOTE: 2022-08: The LZ-related compressors seem to generate random errors
    #       when part of a job on denali or tallgrass.
    zarr.storage.default_compressor = Zstd(level=9)
    # zarr.storage.default_compressor = Blosc(cname='blosclz', clevel=4, shuffle=Blosc.SHUFFLE)

    # Open the source/destination zarr file
    ds = xr.open_dataset(dst_zarr, engine='zarr',
                         backend_kwargs=dict(consolidated=True), chunks={})

    en_date = pd.to_datetime(str(ds.time[-1].values))
    print(f'{en_date=}')

    src_vars = ['ACLWDNB', 'ACLWUPB', 'ACSWDNB', 'ACSWDNT', 'ACSWUPB',
                'I_ACLWDNB', 'I_ACLWUPB', 'I_ACSWDNB', 'I_ACSWDNT', 'I_ACSWUPB']
    bucket_vars = ['I_ACLWDNB', 'I_ACLWUPB', 'I_ACSWDNB', 'I_ACSWDNT', 'I_ACSWUPB']
    remove_vars = ['lat', 'lon', 'x', 'y', 'time']
    remove_vars.extend(bucket_vars)

    for ii in range(index_start, index_end):
        print('-'*40)
        t1 = time.time()

        if base_date + datetime.timedelta(days=num_days * ii) >= en_date:
            # No more dates left to process
            break

        c_start = ii * time_chunk
        c_end = (ii + 1) * time_chunk
        print(f'{c_start} to {c_end}')

        ds2 = ds[src_vars].isel(time=slice(c_start, c_end))

        for vv in ['ACLWDNB', 'ACLWUPB', 'ACSWDNB', 'ACSWDNT', 'ACSWUPB']:
            ds2[vv] = cmath.solar_radiation_acc(ds2[vv], ds2[f'I_{vv}'])

        ds2.compute()

        for vv in ['ACLWDNB', 'ACLWUPB', 'ACSWDNB', 'ACSWDNT', 'ACSWUPB']:
            if 'notes' in ds2[vv].attrs:
                del ds2[vv].attrs['notes']
            ds2[vv].attrs['integration_length'] = 'accumulated since 1979-10-01 00:00:00'

        end = time.time()
        print(f'Chunk: {ii}, compute() elapsed time: {end - t1:0.3f} s')

        # Remove all variables except the ones we want to add
        ds2_src = ds2.drop_vars(remove_vars, errors='ignore')
        # print(ds2_src)

        # Now write the data
        ds2_src.to_zarr(dst_zarr, region={'time': slice(c_start, c_end)})

        print(f'Chunk: {ii}, elapsed time: {(end - start) / 60.:0.3f} m')

    client.close()
    print('-- done', flush=True)

    if dask.config.get("temporary-directory") == '/dev/shm':
        ch.delete_dir(fs, '/dev/shm/dask-worker-space')


if __name__ == '__main__':
    main()
