#!/usr/bin/env python

import argparse
import dask
import fsspec
import pandas as pd
import os
import time
import xarray as xr

from dask.distributed import Client


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized zarr files from WRF CONUS404')
    parser.add_argument('-i', '--index', help='Index to process', type=int, required=True)
    parser.add_argument('-s', '--step', help='Number of indices to process from start index', type=int, required=True)
    parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-d', '--dst_dir', help='Location to store file zarr file', required=True)
    parser.add_argument('-z', '--zarr_dir', help='Location of source zarr files', required=True)

    args = parser.parse_args()

    first_idx = args.index
    idx_span = args.step
    last_idx = first_idx + idx_span

    base_dir = os.path.realpath(args.base_dir)
    outzarr_dir = os.path.realpath(args.dst_dir)

    src_zarr = os.path.realpath(f'{args.zarr_dir}/target_*')

    zarr_whole = f'{outzarr_dir}/conus404_whole.zarr'

    # base_dir = '/caldera/projects/usgs/water/wbeep/conus404_work'
    # outzarr_dir = f'{base_dir}/zarr_out'

    print(f'{first_idx=}')
    print(f'{idx_span=}')
    print(f'{last_idx=}')
    print('-'*60)
    print(f'{base_dir=}')
    print(f'{outzarr_dir=}')
    print(f'{src_zarr=}')
    print(f'{zarr_whole=}')

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

    # Start up the cluster
    # client = Client(n_workers=8, threads_per_worker=1, memory_limit='24GB')
    client = Client()

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}')

    # Max total memory in gigabytes for cluster
    total_mem = sum(vv['memory_limit'] for vv in client.scheduler_info()['workers'].values()) / 1024**3
    total_threads = sum(vv['nthreads'] for vv in client.scheduler_info()['workers'].values())
    print(f'Total memory: {total_mem:0.1f} GB')
    print(f'Number of threads: {total_threads}')

    t1_proc = time.time()
    if first_idx == 0:
        # Open first and last zarr file to get date range
        ds0 = xr.open_dataset(zlist[0], engine='zarr', chunks={})
        ds1 = xr.open_dataset(zlist[-1], engine='zarr', chunks={})

        # TODO: the freq argument must reflect the time interval (e.g hourly, daily)
        dates = pd.date_range(start=ds0.time[0].values, end=ds1.time[-1].values, freq='1h')

        # Have to drop the constant variables (e.g. variables having no time dimension)
        drop_vars = ['BF', 'BH', 'C1F', 'C1H', 'C2F', 'C2H', 'C3F', 'C3H', 'C4F', 'C4H',
                     'CF1', 'CF2', 'CF3', 'CFN', 'CFN1', 'CLAT', 'COSALPHA', 'DN', 'DNW',
                     'DZS', 'E', 'F', 'FNM', 'FNP', 'HGT', 'ISLTYP', 'IVGTYP', 'LAKEMASK',
                     'LANDMASK', 'LU_INDEX', 'MAPFAC_M', 'MAPFAC_MX', 'MAPFAC_MY',
                     'MAPFAC_U', 'MAPFAC_UX', 'MAPFAC_UY', 'MAPFAC_V', 'MAPFAC_VX', 'MAPFAC_VY',
                     'MAX_MSTFX', 'MAX_MSTFY', 'MF_VX_INV', 'MUB', 'P00', 'PB', 'PHB',
                     'P_STRAT', 'P_TOP', 'RDN', 'RDNW', 'RDX', 'RDY', 'SHDMAX', 'SHDMIN',
                     'SINALPHA', 'SNOALB', 'T00', 'TISO', 'TLP', 'TLP_STRAT', 'VAR',
                     'VAR_SSO', 'XLAND', 'lat', 'lat_u', 'lat_v', 'lon', 'lon_u', 'lon_v',
                     'ZETATOP', 'ZNU', 'ZNW', 'ZS']

        source_dataset = ds0.drop_vars(drop_vars, errors='ignore')

        template = (source_dataset.chunk().pipe(xr.zeros_like).isel(time=0, drop=True).expand_dims(time=len(dates)))
        template['time'] = dates
        template = template.chunk({'time': time_cnk})

        # Writes no data (yet)
        template.to_zarr(zarr_whole, compute=False, consolidated=True, mode='w')

        # Writes the data
        ds0.drop_vars(drop_vars).to_zarr(zarr_whole, region={'time': slice(0, time_cnk)})

        # Add the wrf constants
        ds0[drop_vars].to_zarr(zarr_whole, mode='a')
        print(f'  Index {first_idx} (pre-create output): {time.time() - t1_proc:0.3f} s')

    for i in range(first_idx, last_idx):
        if i == 0:
            continue
        t1 = time.time()
        start = i * time_cnk
        stop = (i + 1) * time_cnk

        # print(zlist[i])
        dsi = xr.open_dataset(zlist[i], engine='zarr', chunks={})
        dsi.to_zarr(zarr_whole, region={'time': slice(start, stop)})
        print(f'  Index {i}: {time.time() - t1:0.3f} s')

    client.close()
    if dask.config.get("temporary-directory") == '/dev/shm':
        try:
            fs.rm(f'/dev/shm/dask-worker-space', recursive=True)
        except FileNotFoundError:
            pass

    print(f'Total time: {time.time() - t1_proc:0.3f} s')


if __name__ == '__main__':
    main()
