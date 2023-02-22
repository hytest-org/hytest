#!/usr/bin/env python

import os
import argparse
import dask
# import numpy as np
import time
import xarray as xr
import zarr
import zarr.storage

from numcodecs import Zstd   # , Blosc
from dask.distributed import Client, LocalCluster

import conus404_helpers as ch


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized monthly zarr files from CONUS404 daily')
    # parser.add_argument('-i', '--index', help='Index to process', type=int, required=True)
    # parser.add_argument('-l', '--loop', help='Number of index steps to process', type=int, default=1)
    # parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-d', '--dst_zarr', help='Location of destination monthly zarr store', required=True)
    parser.add_argument('-s', '--src_zarr', help='Location of source daily zarr store', required=True)
    parser.add_argument('-t', '--type', help='Integration type to compute',
                        choices=['cum24', 'instant'], default='instant')

    args = parser.parse_args()

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    print(f'SLURMD_NODENAME: {os.environ.get("SLURMD_NODENAME")}')

    src_zarr = args.src_zarr

    # Output zarr store
    dst_zarr = args.dst_zarr

    # Chunk information for the daily zarr store
    time_chunk = 36   # daily: number of days per chunk
    x_chunk = 350
    y_chunk = 350

    # daily_chunks = dict(y=y_chunk, x=x_chunk, y_stag=y_chunk, x_stag=x_chunk)

    accum_type_map = {'cum24': '24-hour accumulation',
                      'instant': 'instantaneous'}

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}', flush=True)

    start_time = time.time()
    print('=== Open client ===', flush=True)
    cluster = LocalCluster(n_workers=15, threads_per_worker=2, processes=True)

    # client = Client(n_workers=15, threads_per_worker=2)   # , diagnostics_port=None)
    # client.amm.start()

    with Client(cluster) as client:
        total_mem = sum(vv['memory_limit'] for vv in client.scheduler_info()['workers'].values()) / 1024**3
        total_threads = sum(vv['nthreads'] for vv in client.scheduler_info()['workers'].values())
        print(f'    --- Total memory: {total_mem:0.1f} GB; Threads: {total_threads}')

        print('--- Set compression ---', flush=True)
        # Change the default compressor to Zstd
        # NOTE: 2022-08: The LZ-related compressors seem to generate random errors
        #       when part of a job on denali or tallgrass.
        zarr.storage.default_compressor = Zstd(level=9)

        print('--- Open source datastore ---', flush=True)
        # Open hourly source datastore
        ds = xr.open_dataset(src_zarr, engine='zarr',
                             backend_kwargs=dict(consolidated=True), chunks={})

        # Get integration information for computing daily
        accum_types = ch.get_accum_types(ds)
        var_list = accum_types[accum_type_map[args.type]]
        var_list.remove('time')
        var_list.sort()
        print(f'    --- Number of variables of type, {args.type}: {len(var_list)}')

        drop_vars = accum_types['constant']

        mon_chunks = {'time': time_chunk, 'x': x_chunk, 'y': y_chunk}

        for cvar in var_list:
            loop_start = time.time()
            print(f'--- Variable {cvar} ---', flush=True)

            if cvar == 'U':
                mon_chunks = dict(time=time_chunk, y=y_chunk, x_stag=x_chunk)
            elif cvar == 'V':
                mon_chunks = dict(time=time_chunk, x=x_chunk, y_stag=y_chunk)
            else:
                mon_chunks = dict(time=time_chunk, y=y_chunk, x=x_chunk)

            ds_tmp = ds[[cvar]]

            if args.type == 'instant':
                ds_monthly = ds_tmp[[cvar]].resample(time='M').mean(skipna=False).chunk(mon_chunks)
            elif args.type == 'cum24':
                ds_monthly = ds_tmp[[cvar]].resample(time='M').sum(skipna=False).chunk(mon_chunks)

            ds_monthly.compute()

            mon_st = 0
            mon_en = ds_monthly.time.size
            ds_monthly.drop_vars(drop_vars, errors='ignore').to_zarr(dst_zarr, region={'time': slice(mon_st, mon_en)})

            # Cumulative variables may be missing the time for the last day at the end of the POR
            # This shows as NaT in the last time index. This needs to be filled before writing
            # to the zarr store. The data values for this last day will be NaN.
            # if np.isnat(ds_daily.time.values[-1]):
            #     ds_daily.time.values[-1] = ds_daily.time.values[-2] + np.timedelta64(1, 'D')

            print(f'    time: {(time.time() - loop_start) / 60.:0.3f} m', flush=True)

    print(f'Runtime: {(time.time() - start_time) / 60.:0.3f} m')
    print('--- done', flush=True)


if __name__ == '__main__':
    main()
