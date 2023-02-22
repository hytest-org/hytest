#!/usr/bin/env python

import os
import argparse
import dask
import numpy as np
import time
import xarray as xr
import zarr
import zarr.storage

from numcodecs import Zstd   # , Blosc
from dask.distributed import Client, LocalCluster

import conus404_helpers as ch


def compute_daily(ds, var_list, st_idx, en_idx, chunks=None, var_type='instant'):
    if chunks is None:
        chunks = {}

    if var_type == 'instant':
        ds_day_cnk = ds[var_list].isel(time=slice(st_idx, en_idx))
        print(f'    instant: hourly range: {st_idx} ({ds_day_cnk.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values}) to '
              f'{en_idx} ({ds_day_cnk.time.dt.strftime("%Y-%m-%d %H:%M:%S")[-1].values})')

        # Hourly to daily coarsening for instantaneous variables
        ds_daily = ds_day_cnk[var_list].coarsen(time=24, boundary='pad').mean(skipna=False).chunk(chunks)
    elif var_type == 'cum60':
        ds_day_cnk = ds[var_list].isel(time=slice(st_idx+1, en_idx+1))
        print(f'    cum60: hourly range: {st_idx+1} ({ds_day_cnk.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values}) to '
              f'{en_idx+1} ({ds_day_cnk.time.dt.strftime("%Y-%m-%d %H:%M:%S")[-1].values})')

        # Variables accumulated in the prior 60 minutes
        ds_daily = ds_day_cnk[var_list].coarsen(time=24, boundary='pad').sum(skipna=False).chunk(chunks)
    elif var_type == 'cum_sim':
        ds_day_cnk = ds[var_list].isel(time=slice(st_idx+1, en_idx+1))
        print(f'    cum_sim: hourly range: {st_idx+1} ({ds_day_cnk.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values}) to '
              f'{en_idx+1} ({ds_day_cnk.time.dt.strftime("%Y-%m-%d %H:%M:%S")[-1].values})')

        ds_max = ds_day_cnk[var_list].coarsen(time=24, boundary='pad').max(skipna=False)
        ds_min = ds_day_cnk[var_list].coarsen(time=24, boundary='pad').min(skipna=False)
        ds_daily = (ds_max - ds_min).chunk(chunks)
        # ds_daily = (ds_day_cnk[var_list].coarsen(time=24, boundary='trim').max() - ds_day_cnk[var_list].coarsen(time=24, boundary='trim').min())
    else:
        raise NotImplementedError(f'Daily computation for {var_type} is not implemented')

    return ds_daily


def adjust_time(ds, time_adj):
    # Adjust the time values, pass the original encoding to the new time index
    save_enc = ds.time.encoding
    del save_enc['chunks']

    ds['time'] = ds['time'] - np.timedelta64(time_adj, 'm')
    ds.time.encoding = save_enc

    return ds


def remove_chunk_encoding(ds):
    # Remove the existing encoding for chunks
    for vv in ds.variables:
        try:
            del ds[vv].encoding['chunks']
        except KeyError:
            pass

    return ds


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized daily zarr files from CONUS404 hourly')
    parser.add_argument('-i', '--index', help='Index to process', type=int, required=True)
    parser.add_argument('-l', '--loop', help='Number of index steps to process', type=int, default=1)
    # parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-d', '--dst_zarr', help='Location of destination daily zarr store', required=True)
    parser.add_argument('-s', '--src_zarr', help='Location of source hourly zarr store', required=True)
    parser.add_argument('-t', '--type', help='Integration type to compute',
                        choices=['cum60', 'cum_sim', 'instant'], default='instant')

    args = parser.parse_args()

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    print(f'SLURMD_NODENAME: {os.environ.get("SLURMD_NODENAME")}')

    c_idx = args.index

    src_zarr = args.src_zarr

    # Output zarr store
    dst_zarr = args.dst_zarr

    # Chunk information for the daily zarr store
    time_chunk = 36   # daily: number of days per chunk
    x_chunk = 350
    y_chunk = 350

    # daily_chunks = dict(y=y_chunk, x=x_chunk, y_stag=y_chunk, x_stag=x_chunk)

    accum_type_map = {'cum60': 'accumulated over prior 60 minutes',
                      'cum_sim': 'accumulated since 1979-10-01 00:00:00',
                      # 'cum_sim_bucket': 'accumulated since 1979-10-01 00:00:00 bucket',
                      'instant': 'instantaneous'}

    # Amount in minutes to adjust the daily time
    adj_val = {'instant': 690,
               'cum60': 750,
               'cum_sim': 750}

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

        # Hourly source information needed for processing
        hrly_days_per_cnk = 6
        hrly_time_cnk = 24 * hrly_days_per_cnk
        hrly_step_idx = 24 * time_chunk
        hrly_last_idx = ds.time.size

        if c_idx * hrly_step_idx >= hrly_last_idx:
            print('Starting index beyond end of available hourly data')
            exit()

        # Get integration information for computing daily
        accum_types = ch.get_accum_types(ds)
        var_list = accum_types[accum_type_map[args.type]]
        var_list.sort()
        print(f'    --- Number of variables of type, {args.type}: {len(var_list)}')

        drop_vars = accum_types['constant']

        for c_loop in range(args.loop):
            loop_start = time.time()
            print(f'--- Index {c_idx:04d} ---', flush=True)

            c_st = c_idx * hrly_step_idx
            c_en = c_st + hrly_step_idx

            if c_st >= hrly_last_idx:
                print(f'Starting index, {c_st}, is past the end of available hourly timesteps..exiting')
                break

            if c_en > hrly_last_idx:
                c_en = hrly_last_idx

            # print('    --- compute_daily_avg()', flush=True)
            ds_daily = compute_daily(ds, var_list, st_idx=c_st, en_idx=c_en,
                                     chunks={'time': time_chunk, 'x': x_chunk, 'y': y_chunk},
                                     var_type=args.type)

            # print('    --- call compute()', flush=True)
            ds_daily.compute()

            # print('    --- adjust_time()', flush=True)
            ds_daily = adjust_time(ds_daily, time_adj=adj_val[args.type])

            # print('    --- remove_chunk_encoding()', flush=True)
            ds_daily = remove_chunk_encoding(ds_daily)

            # Cumulative variables may be missing the time for the last day at the end of the POR
            # This shows as NaT in the last time index. This needs to be filled before writing
            # to the zarr store. The data values for this last day will be NaN.
            if np.isnat(ds_daily.time.values[-1]):
                ds_daily.time.values[-1] = ds_daily.time.values[-2] + np.timedelta64(1, 'D')

            # Get the daily output index positions
            daily_st = int(c_st / 24)
            daily_en = int(c_en / 24)
            print(f'    daily range: {daily_st} ({ds_daily.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values}) to '
                  f'{daily_en} ({ds_daily.time.dt.strftime("%Y-%m-%d %H:%M:%S")[-1].values})')

            # print('    --- write to zarr store', flush=True)
            ds_daily.drop_vars(drop_vars, errors='ignore').to_zarr(dst_zarr, region={'time': slice(daily_st, daily_en)})

            print(f'    time: {(time.time() - loop_start) / 60.:0.3f} m', flush=True)
            c_idx += 1

    print(f'Runtime: {(time.time() - start_time) / 60.:0.3f} m')
    print('--- done', flush=True)


if __name__ == '__main__':
    main()
