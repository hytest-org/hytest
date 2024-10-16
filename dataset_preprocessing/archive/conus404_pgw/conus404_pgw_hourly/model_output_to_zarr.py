#!/usr/bin/env python3

# import warnings
# warnings.simplefilter(action='ignore', category=FutureWarning)

from cyclopts import App, Parameter, validators
from pathlib import Path

import datetime
import fsspec
import numpy as np
import pandas as pd
import time

import xarray as xr
import zarr
import zarr.storage

from rich.console import Console
from rich import pretty

from numcodecs import Zstd
from dask_jobqueue import SLURMCluster  # , PBSCluster
from dask.distributed import Client   # , as_completed

from typing import Annotated, Dict, List, Union

import ctypes

import conus404_helpers as ch
import conus404_maths as cmath
from conus404_config import Cfg

pretty.install()
con = Console()

app = App(default_parameter=Parameter(negative=()))


def trim_memory() -> int:
    libc = ctypes.CDLL('libc.so.6')
    return libc.malloc_trim(0)


def set_blosc():
    import numcodecs
    numcodecs.blosc.use_threads = False

    return numcodecs.blosc.use_threads


def load_wrf_files(num_days: int,
                   st_date: Union[datetime.datetime, datetime.date],
                   file_pat: str,
                   wrf_dir: Annotated[Path, Parameter(validator=validators.Path(exists=True))]) -> xr.Dataset:
    """Load multiple WRF model output files into a single xarray dataset

    :param num_days: number of days of hourly files to load
    :param st_date: start date for building the file list
    :param file_pat: file pattern of the WRF model output files
    :param wrf_dir: directory containing the WRF model output files
    :return: xarray dataset of the selected WRF model output files
    """

    concat_dim = 'Time'

    try:
        job_files = ch.build_hourly_filelist(num_days, st_date, wrf_dir, file_pat, verify=False)
        ds = xr.open_mfdataset(job_files, concat_dim=concat_dim, combine='nested',
                               parallel=True, coords="minimal", data_vars="minimal",
                               engine='netcdf4', compat='override', chunks={})
    except FileNotFoundError:
        # Re-run the filelist build with the expensive verify
        job_files = ch.build_hourly_filelist(num_days, st_date, wrf_dir, file_pat, verify=True)
        con.print(job_files[0])
        con.print(job_files[-1])
        con.print(f'Number of valid files: {len(job_files)}')

        ds = xr.open_mfdataset(job_files, concat_dim=concat_dim, combine='nested',
                               parallel=True, coords="minimal", data_vars="minimal",
                               engine='netcdf4', compat='override', chunks={})

    return ds


def rechunk_job(chunk_index: int,
                max_mem: float,
                ds_wrf: xr.Dataset,
                target_dir: Annotated[Path, Parameter(validator=validators.Path(exists=True))],
                temp_dir: Annotated[Path, Parameter(validator=validators.Path(exists=True))],
                constants_file: Annotated[Path, Parameter(validator=validators.Path(exists=True))],
                var_metadata: pd.DataFrame,
                var_list: List[str],
                chunk_plan: Dict[str, int]):
    """Use rechunker to rechunk WRF netcdf model output files into zarr format

    :param chunk_index: index of chunk to process
    :param max_mem: maximum memory per thread
    :param ds_wrf:
    :param target_dir: directory for target zarr files
    :param temp_dir: directory used for temporary zarr files during rechunking
    :param constants_file: netcdf file containing WRF constants
    :param var_metadata: dataframe containing variable metadata
    :param var_list: list of variables to process
    :param chunk_plan: dictionary containing chunk sizes for rechunking
    """

    # Attributes that should be removed from all variables
    remove_attrs = ['FieldType', 'MemoryOrder', 'stagger', 'cell_methods']

    rename_dims = {'south_north': 'y', 'west_east': 'x',
                   'south_north_stag': 'y_stag', 'west_east_stag': 'x_stag',
                   'Time': 'time'}

    rename_vars = {'XLAT': 'lat', 'XLAT_U': 'lat_u', 'XLAT_V': 'lat_v',
                   'XLONG': 'lon', 'XLONG_U': 'lon_u', 'XLONG_V': 'lon_v'}

    fs = fsspec.filesystem('file')

    start_time = time.time()

    # =============================================
    # Do some work here
    # var_list = df_vars['variable'].to_list()
    # var_list.append('time')

    # Rechunker requires empty temp and target dirs
    ch.delete_dir(fs, temp_dir)
    ch.delete_dir(fs, target_dir)
    time.sleep(3)  # Wait for files to be removed (necessary? hack!)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~
    # Open netcdf source files
    # t1 = time.time()

    if chunk_index == 0:
        # Add the wrf constants during the first time chunk
        ds_constants = xr.open_dataset(constants_file, decode_coords=True, chunks={})
        ds_wrf = ds_wrf.merge(ds_constants)

        for vv in ds_constants.variables:
            if vv in rename_vars:
                var_list.append(rename_vars[vv])
            elif vv in rename_dims:
                var_list.append(rename_dims[vv])
            else:
                var_list.append(vv)
        ds_constants.close()

        ds_wrf = ch.apply_metadata(ds_wrf, rename_dims, rename_vars, remove_attrs, var_metadata)
    else:
        # The rename_vars variable is only needed for the first rechunk index
        # when the constants file is added.
        ds_wrf = ch.apply_metadata(ds_wrf, rename_dims, {}, remove_attrs, var_metadata)

    # con.print(f'    Open mfdataset: {time.time() - t1:0.3f} s')

    # with performance_report(filename=f'dask_perf_{args.index}.html'):
    ch.rechunker_wrapper(ds_wrf[var_list], target_store=target_dir, temp_store=temp_dir,
                         mem=max_mem, consolidated=True, verbose=False,
                         chunks=chunk_plan)

    end_time = time.time()
    con.print(f'  rechunker: {chunk_index}, elapsed time: {(end_time - start_time) / 60.:0.3f} minutes')


def to_zarr(chunk_index: int,
            chunk_plan: Dict[str, int],
            src_zarr: Annotated[Path, Parameter(validator=validators.Path(exists=True))],
            dst_zarr: Annotated[Path, Parameter(validator=validators.Path(exists=True))]):
    """Insert chunk into existing zarr store

    :param chunk_index: index of chunk to insert
    :param chunk_plan: dictionary containing chunk sizes
    :param src_zarr: source zarr chunk
    :param dst_zarr: destination zarr store
    """

    # Accumulated solar radiation variables which have matching bucket variables
    solrad_vars = {'ACLWDNB': 'I_ACLWDNB',
                   'ACLWUPB': 'I_ACLWUPB',
                   'ACSWDNB': 'I_ACSWDNB',
                   'ACSWDNT': 'I_ACSWDNT',
                   'ACSWUPB': 'I_ACSWUPB'}

    # t1_proc = time.time()

    # Get the time values from the destination zarr store
    ds_dst = xr.open_dataset(dst_zarr, engine='zarr', mask_and_scale=True, chunks={})
    dst_time = ds_dst.time.values

    start_time = time.time()

    start = chunk_index * chunk_plan['time']
    stop = (chunk_index + 1) * chunk_plan['time']

    try:
        ds_src = xr.open_dataset(src_zarr, engine='zarr', mask_and_scale=True, chunks={})
    except FileNotFoundError:
        con.print(f'[red]ERROR[/]: {src_zarr} does not exist; skipping.')
        return

    drop_vars = ch.get_accum_types(ds_src).get('constant', [])

    st_date_src = ds_src.time.values[0]
    en_date_src = ds_src.time.values[-1]
    st_time_idx = np.where(dst_time == st_date_src)[0].item()
    en_time_idx = np.where(dst_time == en_date_src)[-1].item() + 1

    # con.print(f'  time slice: {start}, {stop} = {stop-start}')
    # con.print(f'  dst time slice: {st_time_idx}, {en_time_idx} = {en_time_idx - st_time_idx}')

    # First process everything but the accumulated solar radiation variables
    drop_sol_vars = list(set(ds_src.variables.keys()) & (set(solrad_vars.keys()) | set(solrad_vars.values())))
    # con.print(f'Dropping solar radiation variables: {drop_sol_vars}')
    ds_src = ds_src.drop_vars(drop_sol_vars)

    # Also drop the constants
    ds_src = ds_src.drop_vars(drop_vars, errors='ignore')
    ds_src.to_zarr(dst_zarr, region={'time': slice(st_time_idx, en_time_idx)})

    # con.print('Process solar radiation variables')
    # Second: reopen the zarr and only process the accumulated solar radiation variables
    ds_src = xr.open_dataset(src_zarr, engine='zarr', mask_and_scale=True, chunks={})
    drop_nonsol_vars = list(set(ds_src.variables.keys()) - (set(solrad_vars.keys()) | set(solrad_vars.values())))
    ds_src = ds_src.drop_vars(drop_nonsol_vars)

    # con.print('Computing accumulated solar radiation values')
    for sol_var, bucket_var in solrad_vars.items():
        ds_src[sol_var] = cmath.solar_radiation_acc(ds_src[sol_var], ds_src[bucket_var])

    ds_src.compute()

    for sol_var, bucket_var in solrad_vars.items():
        if 'notes' in ds_src[sol_var].attrs:
            del ds_src[sol_var].attrs['notes']

        # TODO: 2024-05-08 PAN - add base_date to arguments and use it below
        ds_src[sol_var].attrs['integration_length'] = 'accumulated since 1979-10-01 00:00:00'

    # Drop the bucket variables
    ds_src = ds_src.drop_vars(solrad_vars.values(), errors='ignore')
    ds_src.to_zarr(dst_zarr, region={'time': slice(st_time_idx, en_time_idx)})

    end_time = time.time()
    con.print(f'  to_zarr: {chunk_index}, elapsed time: {(end_time - start_time) / 60.:0.3f} minutes')


def resolve_path(msg: str, path: str):
    try:
        path = Path(path).resolve(strict=True)
    except FileNotFoundError:
        con.print(f'[red]{msg}[/]: {path} does not exist')
        exit()

    return path


@app.default()
def run_job(config_file: str,
            chunk_index: int):
    """Run the rechunking job

    :param config_file: configuration file
    :param chunk_index: index of chunk to process
    """

    job_name = f'wrf_rechunk_{chunk_index}'

    config = Cfg(config_file)

    wrf_dir = resolve_path('wrf_dir', config.wrf_dir)
    constants_file = resolve_path('constants_file', config.constants_file)
    metadata_file = resolve_path('metadata_file', config.metadata_file)
    vars_file = resolve_path('vars_file', config.vars_file)
    dst_zarr = resolve_path('dst_zarr', config.dst_zarr)

    con.print(f'{wrf_dir=}')
    con.print(f'{constants_file=}')
    con.print(f'{metadata_file=}')
    con.print(f'{vars_file=}')
    con.print('-'*60)

    chunk_plan = config.chunk_plan
    num_days = config.num_days
    base_date = config.base_date
    base_date = datetime.datetime.strptime(base_date, '%Y-%m-%d %H:%M:%S')
    delta = datetime.timedelta(days=num_days)

    con.print(base_date)

    con.print(f'{chunk_index=}')
    con.print(f'base_date={base_date.strftime("%Y-%m-%d %H:%M:%S")}')
    con.print(f'{num_days=}')
    con.print('-'*60)
    con.print(f'{chunk_plan=}')
    con.print('-'*60)


    # cluster = PBSCluster(job_name=job_name,
    #                      queue=config.queue,
    #                      account=config.account,
    #                      interface=config.interface,
    #                      cores=config.cores_per_job,
    #                      processes=config.processes,
    #                      local_directory = '/local_scratch/pbs.$PBS_JOBID/dask/spill',
    #                      resource_spec = 'select=1:ncpus=1:mem=4GB',
    #                      memory=config.memory_per_job,
    #                      walltime=config.walltime
    #                      death_timeout=75)

    cluster = SLURMCluster(job_name=job_name,
                           queue=config.queue,
                           account=config.account,
                           interface=config.interface,
                           cores=config.cores_per_job,    # this is --cpus-per-task
                           processes=config.processes,    # this is numbers of workers for dask
                           memory=f'{config.memory_per_job} GiB',   # total amount of memory for job
                           walltime=config.walltime)
                           # job_cpu=8,   # this appears to override cores, but cores is still a required argument
                           # job_extra_directives=['--nodes=6'],
                           # local_directory='/home/pnorton/hytest/hourly_processing')

    con.print(cluster.job_script())
    cluster.scale(jobs=config.max_jobs)

    client = Client(cluster)
    client.wait_for_workers(24)

    # max_mem = ch.get_maxmem_per_thread(client, max_percent=0.6, verbose=True)
    max_mem = f'{(config.memory_per_job / config.cores_per_job) * 0.8:0.1f}GB'
    # con.print(f'Maximum memory per thread for rechunking: {max_mem}')

    # Change the default compressor to Zstd
    zarr.storage.default_compressor = Zstd(level=9)

    # Max total memory in gigabytes for cluster
    # total_mem = sum(vv['memory_limit'] for vv in client.scheduler_info()['workers'].values()) / 1024**3
    # total_threads = sum(vv['nthreads'] for vv in client.scheduler_info()['workers'].values())
    # con.print(f'Total memory: {total_mem:0.1f} GB')
    # con.print(f'Number of threads: {total_threads}')

    fs = fsspec.filesystem('file')

    # Read variables to process
    df_vars = pd.read_csv(vars_file)
    var_list = df_vars['variable'].to_list()
    var_list.append('time')
    con.print(f'Number of variables to process: {len(var_list)}')

    # Read the metadata file for modifications to variable attributes
    var_metadata = ch.read_metadata(metadata_file)

    # ==================================
    # Looping starts here
    # ==================================

    # chunk_index = 15
    # num_chunks_per_job = 2

    for cidx in range(chunk_index, chunk_index+config.num_chunks_per_job):
        # Set the target directory
        target_dir = Path(config.target_dir) / f'{config.target_pat}{cidx:05d}'
        temp_dir = Path(config.temp_dir) / f'tmp_{cidx:05d}'
        con.print(f'{target_dir=}')
        con.print(f'{temp_dir=}')

        # Start date is selected based on chunk index
        st_date = base_date + datetime.timedelta(days=num_days * cidx)
        en_date = st_date + delta - datetime.timedelta(days=1)

        con.print(f'{cidx}: {st_date.strftime("%Y-%m-%d %H:%M:%S")} to ' +
                  f'{en_date.strftime("%Y-%m-%d %H:%M:%S")}')

        if (st_date - base_date).days % num_days != 0:
            con.print(f'[red]ERROR[/]: Start date must begin at the start of a {num_days}-day chunk')

        start_time = time.time()
        ds_wrf = load_wrf_files(num_days=num_days,
                                st_date=st_date,
                                file_pat=config.wrf_file_pat,
                                wrf_dir=wrf_dir)

        rechunk_job(chunk_index=cidx,
                    max_mem=max_mem,
                    ds_wrf=ds_wrf,
                    target_dir=target_dir,
                    temp_dir=temp_dir,
                    constants_file=constants_file,
                    var_metadata=var_metadata,
                    var_list=var_list,
                    chunk_plan=chunk_plan)

        to_zarr(chunk_index=cidx,
                chunk_plan=chunk_plan,
                src_zarr=target_dir,
                dst_zarr=dst_zarr)

        # print('Removing target directory')
        ch.delete_dir(fs, target_dir)
        ch.delete_dir(fs, temp_dir)

        end_time = time.time()
        con.print(f'{cidx}, elapsed time: {(end_time - start_time) / 60.:0.3f} minutes')

    cluster.scale(0)


def main():
    app()


if __name__ == '__main__':
    main()
