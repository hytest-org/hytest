#!/usr/bin/env python

import argparse
import dask
import fsspec
import os
import pandas as pd
import time
import xarray as xr
import zarr
import zarr.storage

from numcodecs import Zstd   # , Blosc
from dask.distributed import Client, LocalCluster

import conus404_helpers as ch


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized hourly zarr files from CONUS404 hourly netcdf')
    parser.add_argument('-d', '--dst_zarr', help='Location of destination hourly zarr store', required=True)
    parser.add_argument('-s', '--src_zarr', help='Location of source hourly zarr store', required=True)

    args = parser.parse_args()

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    print(f'SLURMD_NODENAME: {os.environ.get("SLURMD_NODENAME")}')

    src_zarr = args.src_zarr

    # Output zarr store
    dst_zarr = args.dst_zarr

    time_chunk = 6 * 24
    x_chunk = 175
    y_chunk = 175

    dst_chunks = dict(y=y_chunk, x=x_chunk)

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}', flush=True)

    start_time = time.time()

    print('=== Open client ===', flush=True)
    cluster = LocalCluster(n_workers=15, threads_per_worker=2, processes=True)

    fs = fsspec.filesystem('file')
    zlist = sorted(fs.glob(f'{args.src_zarr}/target_*'))

    with Client(cluster) as client:
        total_mem = sum(vv['memory_limit'] for vv in client.scheduler_info()['workers'].values()) / 1024**3
        total_threads = sum(vv['nthreads'] for vv in client.scheduler_info()['workers'].values())
        print(f'    --- Total memory: {total_mem:0.1f} GB; Threads: {total_threads}')

        print('--- Set compression ---', flush=True)
        # Change the default compressor to Zstd
        # NOTE: 2022-08: The LZ-related compressors seem to generate random errors
        #       when part of a job on denali or tallgrass.
        zarr.storage.default_compressor = Zstd(level=9)

        print('--- Create zarr store ---', flush=True)
        ds0 = xr.open_dataset(zlist[0], engine='zarr', mask_and_scale=True, chunks={})
        ds1 = xr.open_dataset(zlist[-1], engine='zarr', mask_and_scale=True, chunks={})

        # ds = xr.open_dataset(src_zarr, engine='zarr',
        #                      backend_kwargs=dict(consolidated=True), chunks={})

        # Get integration information
        accum_types = ch.get_accum_types(ds0)
        drop_vars = accum_types['constant']

        # Get the full date range from the hourly zarr store
        dates = pd.date_range(start=ds0.time[0].values, end=ds1.time[-1].values, freq='1h')
        print(f'    date range: {ds0.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values} to '
              f'{ds1.time.dt.strftime("%Y-%m-%d %H:%M:%S")[-1].values}')
        print(f'    number of timesteps: {len(dates)}')

        # dates = pd.date_range(start=ds.time[0].values, end=ds.time[-1].values, freq='1d')

        # Get all variables but the constant variables
        source_dataset = ds0.drop_vars(drop_vars, errors='ignore')

        print('    --- Create template', end=' ')
        template = (source_dataset.chunk(dst_chunks).pipe(xr.zeros_like).isel(time=0, drop=True).expand_dims(time=len(dates)))
        template['time'] = dates
        template = template.chunk({'time': time_chunk})
        print(f'       {time.time() - start_time:0.3f} s', flush=True)

        print('    --- Write template', flush=True, end=' ')
        # Writes no data (yet)
        template.to_zarr(dst_zarr, compute=False, consolidated=True, mode='w')
        print(f'       {time.time() - start_time:0.3f} s', flush=True)

        # Remove the existing chunk encoding for constant variables
        for vv in drop_vars:
            try:
                del ds0[vv].encoding['chunks']
            except KeyError:
                pass

        # Add the wrf constants
        print('    --- Write constant variables', end=' ')
        ds0[drop_vars].chunk(dst_chunks).to_zarr(dst_zarr, mode='a')
        print(f'       {time.time() - start_time:0.3f} s', flush=True)

    print(f'Runtime: {(time.time() - start_time) / 60.:0.3f} m')
    print('--- done', flush=True)


if __name__ == '__main__':
    main()
