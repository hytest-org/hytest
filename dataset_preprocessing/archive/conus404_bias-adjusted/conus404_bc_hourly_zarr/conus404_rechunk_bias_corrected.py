#!/usr/bin/env python

import os
import argparse
import dask
import datetime
import fsspec
import pandas as pd
import time
import xarray as xr
import zarr
import zarr.storage

from numcodecs import Zstd   # , Blosc
from dask.distributed import Client

import conus404_helpers as ch

import ctypes


def trim_memory() -> int:
    libc = ctypes.CDLL('libc.so.6')
    return libc.malloc_trim(0)


def set_blosc():
    import numcodecs
    numcodecs.blosc.use_threads = False

    return numcodecs.blosc.use_threads


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized zarr files from CONUS404 model output files')
    parser.add_argument('-i', '--index', help='Index to process', required=True)
    parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-w', '--wrf_dir', help='Base directory for WRF model output files', required=True)
    # parser.add_argument('-c', '--constants_file', help='Path to WRF constants', required=False, default=None)
    parser.add_argument('-v', '--vars_file', help='File containing list of variables to include in output',
                        required=True)
    parser.add_argument('-d', '--dst_dir', help='Location to store rechunked zarr files', required=True)
    # parser.add_argument('-m', '--metadata_file', help='File containing metadata to include in zarr files',
    #                     required=True)

    args = parser.parse_args()

    # Filename pattern for bias-adjusted hourly files
    file_pat = '{wrf_dir}/{wy_dir}/{fdate.strftime("%Y%m%d%H%M")}.LDASIN_DOMAIN1'

    temp_store = os.environ.get("RAM_SCRATCH")

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    print(f'SLURMD_NODENAME: {os.environ.get("SLURMD_NODENAME")}')
    print(f'RAM_SCRATCH: {temp_store}')

    if temp_store is None:
        # Try to use share memory even if the job doesn't set a directory
        temp_store = '/dev/shm/tmp'

    base_dir = os.path.realpath(args.base_dir)
    wrf_dir = os.path.realpath(args.wrf_dir)
    proc_vars_file = ch.set_file_path(args.vars_file, base_dir)

    # The scratch filesystem seems to randomly return false for pre-existing
    # directories when a lot of processes are using the same path. Try random
    # sleep to minimize this.
    try:
        target_store = f'{ch.set_target_path(args.dst_dir, base_dir)}/target'
    except FileNotFoundError:
        print(f'{args.dst_dir} not found; trying again')
        time.sleep(10)
        target_store = f'{ch.set_target_path(args.dst_dir, base_dir)}/target'

    print(f'{base_dir=}')
    print(f'{wrf_dir=}')
    print(f'{proc_vars_file=}')
    print(f'{target_store=}')
    print('-'*60)

    base_date = datetime.datetime(1979, 10, 1)
    num_days = 6
    delta = datetime.timedelta(days=num_days)

    # Start date is selected based on chunk index
    index_start = int(args.index)
    st_date = base_date + datetime.timedelta(days=num_days * index_start)
    en_date = st_date + delta - datetime.timedelta(days=1)

    print(f'{base_date=}')
    print(f'{st_date=}')
    print(f'{en_date=}')
    print(f'{num_days=}')
    print(f'{delta=}')
    print(f'{index_start=}')
    print('-'*60)

    if (st_date - base_date).days % num_days != 0:
        print(f'Start date must begin at the start of a {num_days}-day chunk')

    time_chunk = num_days * 24
    x_chunk = 175
    y_chunk = 175

    # Variables
    # RAINRATE
    # T2D (min, max)
    # crs
    # time
    # x
    # y

    # Start up the cluster
    # dask.config.set({'distributed.logging.distributed': 'warning'})
    # dask.config.set({'distributed.logging.distributed__client': 'warning'})
    # dask.config.set({'distributed.logging.bokeh': 'critical'})
    # dask.config.set({'distributed.logging.tornado': 'critical'})
    # dask.config.set({'distributed.logging.tornado__application': 'error'})

    client = Client(n_workers=6, threads_per_worker=2, diagnostics_port=None)
    client.amm.start()

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}')

    # Get the maximum memory per thread to use for chunking
    max_mem = ch.get_maxmem_per_thread(client, max_percent=0.7, verbose=False)

    # Read variables to process
    df = pd.read_csv(proc_vars_file)

    fs = fsspec.filesystem('file')

    start = time.time()

    cnk_idx = index_start
    c_start = st_date

    # Change the default compressor to Zstd
    # NOTE: 2022-08: The LZ-related compressors seem to generate random errors
    #       when part of a job on denali or tallgrass.
    zarr.storage.default_compressor = Zstd(level=9)
    # zarr.storage.default_compressor = Blosc(cname='blosclz', clevel=4, shuffle=Blosc.SHUFFLE)

    while c_start < en_date:
        tstore_dir = f'{target_store}_{cnk_idx:05d}'

        # =============================================
        # Do some work here
        var_list = df['variable'].to_list()
        var_list.append('time')

        # Rechunker requires empty temp and target dirs
        ch.delete_dir(fs, temp_store)
        ch.delete_dir(fs, tstore_dir)
        time.sleep(3)  # Wait for files to be removed (necessary? hack!)

        # ~~~~~~~~~~~~~~~~~~~~~~~~~
        # Open netcdf source files
        t1 = time.time()

        try:
            job_files = ch.build_hourly_filelist(num_days, c_start, wrf_dir, file_pat, verify=False)
            ds2d = xr.open_mfdataset(job_files, concat_dim='time', combine='nested',
                                     parallel=True, coords="minimal", data_vars="minimal",
                                     engine='netcdf4', compat='override', chunks={})
        except FileNotFoundError:
            # Re-run the filelist build with the expensive verify
            job_files = ch.build_hourly_filelist(num_days, c_start, wrf_dir, file_pat, verify=True)
            print(job_files[0])
            print(job_files[-1])
            print(f'Number of valid files: {len(job_files)}')

            ds2d = xr.open_mfdataset(job_files, concat_dim='time', combine='nested',
                                     parallel=True, coords="minimal", data_vars="minimal",
                                     engine='netcdf4', compat='override', chunks={})

        print(f'    Open mfdataset: {time.time() - t1:0.3f} s', flush=True)

        ch.rechunker_wrapper(ds2d[var_list], target_store=tstore_dir, temp_store=temp_store,
                             mem=max_mem, consolidated=True, verbose=False,
                             chunks={'time': time_chunk,
                                     'y': y_chunk, 'x': x_chunk})

        end = time.time()
        print(f'Chunk: {cnk_idx}, elapsed time: {(end - start) / 60.:0.3f}, {job_files[0]}')

        cnk_idx += 1
        c_start += delta

        client.run(trim_memory)

    client.close()
    print('-- rechunk done', flush=True)

    # Clear out the temporary storage
    ch.delete_dir(fs, temp_store)

    if dask.config.get("temporary-directory") == '/dev/shm':
        ch.delete_dir(fs, '/dev/shm/dask-worker-space')
        # try:
        #     fs.rm(f'/dev/shm/dask-worker-space', recursive=True)
        # except FileNotFoundError:
        #     pass


if __name__ == '__main__':
    main()
