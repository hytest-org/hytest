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
    zarr_store = f'{ch.set_target_path(args.src_zarr, base_dir)}'

    print(f'{base_dir=}')
    print(f'{zarr_store=}')
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
    ds = xr.open_dataset(zarr_store, engine='zarr',
                         backend_kwargs=dict(consolidated=True), chunks={})

    en_date = pd.to_datetime(str(ds.time[-1].values))
    print(f'{en_date=}')

    hourly_meta = dict(RH2=dict(coordinates='lon lat',
                                grid_mapping='crs',
                                long_name='Relative humidity at 2 meters',
                                notes='Tetens equation',
                                units=''),
                       E2=dict(coordinates='lon lat',
                               grid_mapping='crs',
                               long_name='Vapor pressure at 2 meters',
                               notes='',
                               units='Pa'),
                       ES2=dict(coordinates='lon lat',
                                grid_mapping='crs',
                                long_name='Saturation vapor pressure at 2 meters',
                                notes='Tetens equation',
                                units='Pa'),
                       SH2=dict(coordinates='lon lat',
                                grid_mapping='crs',
                                long_name='Specific humidity at 2 meters',
                                notes='',
                                units='kg kg-1'),
                       TD2=dict(coordinates='lon lat',
                                grid_mapping='crs',
                                long_name='Temperature dewpoint at 2 meters',
                                notes='',
                                units='K'),
                       )

    src_vars = ['T2', 'Q2', 'PSFC']
    remove_vars = ['lat', 'lon', 'x', 'y', 'time']
    remove_vars.extend(src_vars)

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

        ds2['RH2'] = cmath.rh_teten(ds2.Q2, ds2.PSFC, ds2.T2)
        ds2['SH2'] = cmath.specific_humidity(ds2.Q2)
        ds2['E2'] = cmath.vp(ds2.Q2, ds2.PSFC)
        ds2['ES2'] = cmath.saturation_vp_teten(ds2.T2)
        # ds2['TD2'] = cmath.dewpoint_temperature_magnus(ds2.Q2, ds2.PSFC)

        ds2.compute()

        end = time.time()
        print(f'Chunk: {ii}, Compute elapsed time: {end - t1:0.3f} s')

        # Remove all variables except the ones we want to add
        ds2_src = ds2.drop_vars(remove_vars, errors='ignore')

        if ii == 0:
            print(f'Chunk: {ii}, first index')
            # Add the attributes for the new variables
            for cvar in ds2.variables:
                if cvar in hourly_meta:
                    for attr_key, attr_val in hourly_meta[cvar].items():
                        if attr_val != '':
                            ds2[cvar].attrs[attr_key] = attr_val

            # For the first time chunk create the entire array for each variable and add to zarr
            # NOTE: Add logic to check if variable already exists in the zarr_store
            template = (ds2_src.chunk().pipe(xr.zeros_like).isel(time=0, drop=True).expand_dims(time=ds.time.size))
            template = template.chunk({'time': time_chunk})

            # This writes no data
            # NOTE: Do not set the mode='w' this will erase ALL existing variables
            #       in the zarr store.
            template.to_zarr(zarr_store, mode='a', compute=False, consolidated=True)

        # Now write the data
        ds2_src.to_zarr(zarr_store, mode='a', region={'time': slice(c_start, c_end)})

        print(f'Chunk: {ii}, elapsed time: {(end - start) / 60.:0.3f} m')

    client.close()
    print('-- done', flush=True)

    if dask.config.get("temporary-directory") == '/dev/shm':
        ch.delete_dir(fs, '/dev/shm/dask-worker-space')


if __name__ == '__main__':
    main()
