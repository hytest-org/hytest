#!/usr/bin/env python

# import numpy as np
import os
import argparse
import dask
import datetime
import fsspec
# import numpy as np
import pandas as pd
# import rechunker
import time
import xarray as xr
# import zarr

import conus404_helpers as ch

from dask.distributed import Client


def main():
    parser = argparse.ArgumentParser(description='Create cloud-optimized zarr files from WRF CONUS404 daily model output files')
    parser.add_argument('-i', '--index', help='Index to process', required=True)
    parser.add_argument('-b', '--base_dir', help='Directory to work in', required=False, default=None)
    parser.add_argument('-w', '--wrf_dir', help='Base directory for WRF model output files', required=True)
    parser.add_argument('-c', '--constants_file', help='Path to WRF constants', required=False, default=None)
    parser.add_argument('-v', '--vars_file', help='File containing list of variables to include in output', required=True)
    parser.add_argument('-d', '--dst_dir', help='Location to store rechunked zarr files', required=True)
    parser.add_argument('-m', '--metadata_file', help='File containing metadata to include in zarr files', required=True)

    args = parser.parse_args()

    print(f'HOST: {os.environ.get("HOSTNAME")}')
    if os.environ.get('HOSTNAME') == 'denali-login2':
        exit(-1)

    index_start = int(args.index)
    print(f'{index_start=}')

    base_dir = os.path.realpath(args.base_dir)
    wrf_dir = os.path.realpath(args.wrf_dir)

    const_file = ch.set_file_path(args.constants_file, base_dir)
    metadata_file = ch.set_file_path(args.metadata_file, base_dir)
    proc_vars_file = ch.set_file_path(args.vars_file, base_dir)
    target_store = f'{ch.set_target_path(args.dst_dir, base_dir)}/target'

    print(f'{base_dir=}')
    print(f'{wrf_dir=}')
    print(f'{const_file=}')
    print(f'{metadata_file=}')
    print(f'{proc_vars_file=}')
    print(f'{target_store=}')
    print('-'*60)

    temp_store = '/dev/shm/tmp'
    base_date = datetime.datetime(1979, 10, 1)
    num_days = 24
    delta = datetime.timedelta(days=num_days)

    # We specify a chunk index and the start date is selected based on that
    index_start = int(args.index)
    st_date = base_date + datetime.timedelta(days=num_days * index_start)
    en_date = st_date + delta - datetime.timedelta(days=1)
    print(f'{index_start=}')

    print(f'{base_date=}')
    print(f'{st_date=}')
    print(f'{en_date=}')
    print(f'{num_days=}')
    print(f'{delta=}')

    if (st_date - base_date).days % num_days != 0:
        print(f'Start date must begin at the start of a {num_days}-day chunk')

    # index_start = int((st_date - base_date).days / num_days)
    print(f'{index_start=}')
    print('-'*60)

    time_chunk = num_days
    x_chunk = 350
    y_chunk = 350

    # Variables to drop from the constants file
    drop_vars = ['BF', 'BH', 'C1F', 'C1H', 'C2F', 'C2H', 'C3F', 'C3H', 'C4F', 'C4H',
                 'CF1', 'CF2', 'CF3', 'CFN', 'CFN1', 'CLAT', 'COSALPHA', 'DN', 'DNW',
                 'DZS', 'E', 'F', 'FNM', 'FNP', 'HGT', 'ISLTYP', 'IVGTYP', 'LAKEMASK',
                 'LU_INDEX', 'MAPFAC_M', 'MAPFAC_MX', 'MAPFAC_MY',
                 'MAPFAC_U', 'MAPFAC_UX', 'MAPFAC_UY', 'MAPFAC_V', 'MAPFAC_VX', 'MAPFAC_VY',
                 'MAX_MSTFX', 'MAX_MSTFY', 'MF_VX_INV', 'MUB', 'P00', 'PB', 'PHB',
                 'P_STRAT', 'P_TOP', 'RDN', 'RDNW', 'RDX', 'RDY', 'SHDMAX', 'SHDMIN',
                 'SINALPHA', 'SNOALB', 'T00', 'TISO', 'TLP', 'TLP_STRAT', 'VAR',
                 'VAR_SSO', 'XLAND', 'XLAT_U', 'XLAT_V', 'XLONG_U', 'XLONG_V',
                 'ZETATOP', 'ZNU', 'ZNW', 'ZS']

    # Attributes that should be removed from all variables
    remove_attrs = ['FieldType', 'MemoryOrder', 'stagger', 'cell_methods']

    rename_dims = {'south_north': 'y', 'west_east': 'x', 'Time': 'time'}

    rename_vars = {'XLAT': 'lat', 'XLONG': 'lon',
                   'south_north': 'y', 'west_east': 'x'}

    # Read the metadata file for modifications to variable attributes
    var_metadata = ch.read_metadata(metadata_file)

    # Add additional time attributes
    var_metadata['time'] = dict(axis='T', standard_name='time')

    # Start up the cluster
    client = Client(n_workers=8, threads_per_worker=1, memory_limit='24GB')

    print(f'dask tmp directory: {dask.config.get("temporary-directory")}')

    # Get the maximum memory per thread to use for chunking
    max_mem = ch.get_maxmem_per_thread(client, max_percent=0.7, verbose=False)

    # Read variables to process
    df = pd.read_csv(proc_vars_file)

    fs = fsspec.filesystem('file')

    start = time.time()

    cnk_idx = index_start
    c_start = st_date

    while c_start < en_date:
        job_files = ch.build_filelist_wrf2d(num_days, c_start, wrf_dir)

        if len(job_files) < num_days:
            print(f'Number of files not equal to time chunk; adjusting to {len(job_files)}')
            num_days = len(job_files)
            time_chunk = num_days

        tstore_dir = f'{target_store}_{cnk_idx:05d}'
        # num_time = len(job_files)

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
        ds2d = xr.open_mfdataset(job_files, concat_dim='Time', combine='nested',
                                 parallel=True, coords="minimal", data_vars="minimal",
                                 compat='override', chunks={})

        if cnk_idx == 0:
            # Add the wrf constants during the first time chunk
            df_const = xr.open_dataset(const_file, decode_coords=False, chunks={})
            ds2d = ds2d.merge(df_const)

            for vv in df_const.variables:
                if vv in rename_vars:
                    var_list.append(rename_vars[vv])
                elif vv in rename_dims:
                    var_list.append(rename_dims[vv])
                else:
                    var_list.append(vv)
            df_const.close()

            ds2d = ch.apply_metadata(ds2d, rename_dims, rename_vars, remove_attrs, var_metadata)
        else:
            # The rename_vars variable is only needed for the first rechunk index
            # when the constants file is added.
            ds2d = ch.apply_metadata(ds2d, rename_dims, {}, remove_attrs, var_metadata)

        print(f'    Open mfdataset: {time.time() - t1:0.3f} s')

        ch.rechunker_wrapper(ds2d[var_list], target_store=tstore_dir, temp_store=temp_store,
                             mem=max_mem, consolidated=True, verbose=False,
                             chunks={'time': time_chunk,
                                     'y': y_chunk, 'x': x_chunk,
                                     'y_stag': y_chunk, 'x_stag': x_chunk})

        end = time.time()
        print(f'Chunk: {cnk_idx}, elapsed time: {(end - start) / 60.:0.3f}, {job_files[0]}')

        cnk_idx += 1
        c_start += delta

    client.close()
    
    print('-- rechunk done', flush=True)

    # Clear out the temporary storage
    ch.delete_dir(fs, temp_store)

    if dask.config.get("temporary-directory") == '/dev/shm':
        ch.delete_dir(fs, '/dev/shm/dask-worker-space')


if __name__ == '__main__':
    main()
