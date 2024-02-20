#!/usr/bin/env python

import argparse
import dask
import fsspec
import numpy as np
import os
import time
import xarray as xr
import warnings

import zarr.storage

from numcodecs import Zstd   # , Blosc

import conus404_helpers as ch
import conus404_maths as cmath
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

    target_pat = 'target_'

    first_idx = args.index
    idx_span = args.step
    last_idx = first_idx + idx_span

    base_dir = os.path.realpath(args.base_dir)
    outzarr_dir = os.path.realpath(args.dst_dir)

    src_zarr = os.path.realpath(f'{args.zarr_dir}/{target_pat}')

    dst_zarr = outzarr_dir

    print(f'{first_idx=}')
    print(f'{idx_span=}')
    print(f'{last_idx=}')
    print('-'*60)
    print(f'{base_dir=}')
    print(f'{outzarr_dir=}')
    print(f'{src_zarr=}')
    print(f'{dst_zarr=}')

    time_cnk = 144

    # Accumulated solar radiation variables which have matching bucket variables
    solrad_vars = {'ACLWDNB': 'I_ACLWDNB',
                   'ACLWUPB': 'I_ACLWUPB',
                   'ACSWDNB': 'I_ACSWDNB',
                   'ACSWDNT': 'I_ACSWDNT',
                   'ACSWUPB': 'I_ACSWUPB'}

    fs = fsspec.filesystem('file')
    # # zlist = sorted(fs.glob(f'{base_dir}/test1/target_0*'))
    # zlist = sorted(fs.glob(src_zarr))
    # num_targets = len(zlist)
    #
    # if num_targets < last_idx - 1:
    #     idx_span = num_targets - first_idx
    #     last_idx = first_idx + idx_span
    #     print(f'NOTE: Adjusted processing indices')

    # Build dictionary of candidate target paths to process
    target_dict = {idx: f'{args.zarr_dir}/{target_pat}{idx:05d}' for idx in range(first_idx, last_idx)}

    print(f'Index start: {first_idx}; Index end: {last_idx - 1}')

    t1_proc = time.time()
    # Start up the cluster
    # client = Client(n_workers=8, threads_per_worker=1, memory_limit='24GB')
    with dask.config.set({"distributed.scheduler.worker-saturation": 1.0}):
        client = Client(n_workers=10, threads_per_worker=2, diagnostics_port=None)   # , memory_limit='24GB')
    # client = Client()

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

    # if first_idx == 0:
    #     print('='*20, ' first index ', '='*20)
    #     # Open first and last zarr file to get date range
    #     # NOTE: 2022-09-29 PAN - must set mask_and_scale to False or xarray/zarr will
    #     #       convert integer variables with scale_factor set to >f8 dtype and somehow manage
    #     #       to corrupt the values in the process.
    #     ds0 = xr.open_dataset(zlist[0], engine='zarr', mask_and_scale=True, chunks={})
    #     ds1 = xr.open_dataset(zlist[-1], engine='zarr', mask_and_scale=True, chunks={})
    #
    #     # TODO: the freq argument must reflect the time interval (e.g hourly, daily)
    #     dates = pd.date_range(start=ds0.time[0].values, end=ds1.time[-1].values, freq='1h')
    #     print(f'    date range: {ds0.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values} to '
    #           f'{ds1.time.dt.strftime("%Y-%m-%d %H:%M:%S")[-1].values}')
    #     print(f'    number of timesteps: {len(dates)}')
    #
    #     # Have to drop the constant variables (e.g. variables having no time dimension)
    #     drop_vars = ch.get_accum_types(ds0).get('constant', [])
    #
    #     source_dataset = ds0.drop_vars(drop_vars, errors='ignore')
    #
    #     print(f'{len(dates)=}')
    #     print(f'{time_cnk=}')
    #
    #     template = (source_dataset.chunk().pipe(xr.zeros_like).isel(time=0, drop=True).expand_dims(time=len(dates)))
    #     template['time'] = dates
    #     template = template.chunk({'time': time_cnk})
    #
    #     # Writes no data (yet)
    #     template.to_zarr(dst_zarr, compute=False, encoding=bucket_enc, consolidated=True, mode='w')
    #
    #     # Add the wrf constants
    #     ds0[drop_vars].to_zarr(dst_zarr, mode='a')
    #
    #     print(f'    Index {first_idx} (pre-create zarr store): {time.time() - t1_proc:0.3f} s')
    #     print('-'*20, 'end first index', '-'*20, flush=True)

    # Get the time values from the destination zarr store
    ds_dst = xr.open_dataset(dst_zarr, engine='zarr', mask_and_scale=True, chunks={})
    dst_time = ds_dst.time.values

    for idx, cfile in target_dict.items():
        t1 = time.time()

        start = idx * time_cnk
        stop = (idx + 1) * time_cnk

        try:
            dsi = xr.open_dataset(cfile, engine='zarr', mask_and_scale=True, chunks={})
        except FileNotFoundError:
            print(f'{cfile} does not exist; skipping.')
            continue

        drop_vars = ch.get_accum_types(dsi).get('constant', [])

        st_date_src = dsi.time.values[0]
        en_date_src = dsi.time.values[-1]
        st_time_idx = np.where(dst_time == st_date_src)[0].item()
        en_time_idx = np.where(dst_time == en_date_src)[-1].item() + 1

        print(f'  time slice: {start}, {stop} = {stop-start}')
        print(f'  dst time slice: {st_time_idx}, {en_time_idx} = {en_time_idx - st_time_idx}')

        # NOTE: 2022-09-29 PAN - with mask_and_scale set to False certain attributes must be
        #       removed before writing to a zarr region or xarray will puke with a ValueError
        #       just because.
        #       See https://github.com/pydata/xarray/issues/6329 for a similar problem
        # for cvar in dsi.variables:
        #     if '_FillValue' in dsi[cvar].attrs.keys():
        #         del dsi[cvar].attrs['_FillValue']
        #     elif 'scale_factor' in dsi[cvar].attrs.keys():
        #         del dsi[cvar].attrs['scale_factor']

        # ==================== solar radiation ============================
        if len(set(dsi.variables.keys()) - set(solrad_vars.keys()) - set(solrad_vars.values()) - {'time'}) == 0:
            # When the target only contains the solar radiation variables which have matching bucket
            # variables then we compute the final accumulated values and drop the bucket variables.
            # This will fail if any of the sol_var or bucket_var variables is missing from the incoming target.
            print('Computing accumulated solar radiation values')
            for sol_var, bucket_var in solrad_vars.items():
                dsi[sol_var] = cmath.solar_radiation_acc(dsi[sol_var], dsi[bucket_var])

            dsi.compute()

            for sol_var, bucket_var in solrad_vars.items():
                if 'notes' in dsi[sol_var].attrs:
                    del dsi[sol_var].attrs['notes']
                dsi[sol_var].attrs['integration_length'] = 'accumulated since 1979-10-01 00:00:00'

            # Drop the bucket variables
            dsi = dsi.drop_vars(solrad_vars.values(), errors='ignore')
        elif len(set(dsi.variables.keys()) & (set(solrad_vars.keys()) | set(solrad_vars.values()))) > 0:
            # Accumulated solar radiation variables that have a matching bucket variable should not be
            # processed if we are processing other variables too.
            drop_sol_vars = list(set(dsi.variables.keys()) & (set(solrad_vars.keys()) | set(solrad_vars.values())))
            print(f'Dropping solar radiation variables: {drop_sol_vars}')
            dsi = dsi.drop_vars(drop_sol_vars)
        # =================================================================

        dsi = dsi.drop_vars(drop_vars, errors='ignore')
        dsi.to_zarr(dst_zarr, region={'time': slice(st_time_idx, en_time_idx)})
        print(f'  Index {idx}: {time.time() - t1:0.3f} s', flush=True)

    client.close()
    if dask.config.get("temporary-directory") == '/dev/shm':
        try:
            fs.rm(f'/dev/shm/dask-worker-space', recursive=True)
        except FileNotFoundError:
            pass

    print(f'Total time: {(time.time() - t1_proc) / 60.0:0.3f} m')


if __name__ == '__main__':
    main()
