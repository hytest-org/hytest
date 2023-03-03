#!/usr/bin/env python

import argparse
import dask
import fsspec
import pandas as pd
import os
import time
import xarray as xr
import warnings

import zarr.storage

from numcodecs import Zstd   # , Blosc

import conus404_helpers as ch
from dask.distributed import Client

warnings.filterwarnings('ignore')


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized zarr files from WRF CONUS404')
    parser.add_argument('-i', '--index', help='Index to process', type=int, required=True)
    parser.add_argument('-s', '--step', help='Number of indices to process from start index', type=int, required=True)
    parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-d', '--dst_dir', help='Path to destination zarr store', required=True)
    parser.add_argument('-z', '--zarr_dir', help='Location of source zarr files', required=True)

    args = parser.parse_args()

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    print(f'SLURMD_NODENAME: {os.environ.get("SLURMD_NODENAME")}')
    # print(f'RAM_SCRATCH: {temp_store}')

    first_idx = args.index
    idx_span = args.step
    last_idx = first_idx + idx_span

    base_dir = os.path.realpath(args.base_dir)
    outzarr_dir = os.path.realpath(args.dst_dir)

    src_zarr = os.path.realpath(f'{args.zarr_dir}/target_*')

    dst_zarr = outzarr_dir
    # dst_zarr = f'{outzarr_dir}/conus404_whole.zarr'

    # base_dir = '/caldera/projects/usgs/water/wbeep/conus404_work'
    # outzarr_dir = f'{base_dir}/zarr_out'

    print(f'{first_idx=}')
    print(f'{idx_span=}')
    print(f'{last_idx=}')
    print('-'*60)
    print(f'{base_dir=}')
    print(f'{outzarr_dir=}')
    print(f'{src_zarr=}')
    print(f'{dst_zarr=}')

    time_cnk = 144

    fs = fsspec.filesystem('file')
    # zlist = sorted(fs.glob(f'{base_dir}/test1/target_0*'))
    zlist = sorted(fs.glob(src_zarr))
    num_targets = len(zlist)

    if num_targets < last_idx - 1:
        idx_span = num_targets - first_idx
        last_idx = first_idx + idx_span
        print(f'NOTE: Adjusted processing indices')

    print(f'Index start: {first_idx}; Index end: {last_idx - 1}')

    t1_proc = time.time()
    # Start up the cluster
    # client = Client(n_workers=8, threads_per_worker=1, memory_limit='24GB')
    client = Client()

    # Change the default compressor to Zstd
    # NOTE: 2022-08: The LZ-related compressors seem to generate random errors
    #       when part of a job on denali or tallgrass.
    zarr.storage.default_compressor = Zstd(level=9)
    # zarr.storage.default_compressor = Blosc(cname='blosclz', clevel=4, shuffle=Blosc.SHUFFLE)

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}')

    # Max total memory in gigabytes for cluster
    total_mem = sum(vv['memory_limit'] for vv in client.scheduler_info()['workers'].values()) / 1024**3
    total_threads = sum(vv['nthreads'] for vv in client.scheduler_info()['workers'].values())
    print(f'Total memory: {total_mem:0.1f} GB')
    print(f'Number of threads: {total_threads}')

    print(f'Client startup time: {time.time() - t1_proc:0.3f} s', flush=True)

    for i in range(first_idx, last_idx):
        t1 = time.time()
        start = i * time_cnk
        stop = (i + 1) * time_cnk

        # print(zlist[i])
        dsi = xr.open_dataset(zlist[i], engine='zarr', mask_and_scale=True, chunks={})
        drop_vars = ch.get_accum_types(dsi).get('constant', [])

        # NOTE: 2022-09-29 PAN - with mask_and_scale set to False certain attributes must be
        #       removed before writing to a zarr region or xarray will puke with a ValueError
        #       just because.
        #       See https://github.com/pydata/xarray/issues/6329 for a similar problem
        # for cvar in dsi.variables:
        #     if '_FillValue' in dsi[cvar].attrs.keys():
        #         del dsi[cvar].attrs['_FillValue']
        #     elif 'scale_factor' in dsi[cvar].attrs.keys():
        #         del dsi[cvar].attrs['scale_factor']

        dsi.drop_vars(drop_vars, errors='ignore').to_zarr(dst_zarr, region={'time': slice(start, stop)})
        print(f'  Index {i}: {time.time() - t1:0.3f} s', flush=True)

    client.close()
    if dask.config.get("temporary-directory") == '/dev/shm':
        try:
            fs.rm(f'/dev/shm/dask-worker-space', recursive=True)
        except FileNotFoundError:
            pass

    print(f'Total time: {(time.time() - t1_proc) / 60.0:0.3f} m')


if __name__ == '__main__':
    main()
