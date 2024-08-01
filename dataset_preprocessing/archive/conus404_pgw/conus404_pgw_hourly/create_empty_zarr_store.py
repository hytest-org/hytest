#!/usr/bin/env python3

import datetime
import fsspec
import pandas as pd
import time
import xarray as xr
import zarr

from cyclopts import App, Parameter, validators
from pathlib import Path

from numcodecs import Zstd
from dask_jobqueue import SLURMCluster, PBSCluster
from dask.distributed import Client

from rich.console import Console
from rich import pretty

from typing import Annotated, Dict, List, Union

import conus404_helpers as ch
from conus404_config import Cfg

from model_output_to_zarr import load_wrf_files, rechunk_job, resolve_path
pretty.install()
con = Console()

app = App(default_parameter=Parameter(negative=()))


def create_empty_zarr(src_zarr: Annotated[Path, Parameter(validator=validators.Path(exists=True))],
                      dst_zarr: Annotated[Path, Parameter(validator=validators.Path())],
                      end_date: Union[datetime.datetime, datetime.date],
                      chunk_plan: Dict[str, int]):
    """Create an empty zarr store with the same structure as the source zarr store

    :param src_zarr: Path to the source zarr store
    :param dst_zarr: Path to the destination zarr store
    :param end_date: End date for the new zarr store
    :param chunk_plan: Chunking plan for the new zarr store
    """

    # Accumulated solar radiation variables which have matching bucket variables
    solrad_vars = {'ACLWDNB': 'I_ACLWDNB',
                   'ACLWUPB': 'I_ACLWUPB',
                   'ACSWDNB': 'I_ACSWDNB',
                   'ACSWDNT': 'I_ACSWDNT',
                   'ACSWUPB': 'I_ACSWUPB'}

    start_time = time.time()

    con.print('--- Create zarr store ---')
    ds = xr.open_dataset(src_zarr, engine='zarr', backend_kwargs=dict(consolidated=True), chunks={})

    dst_chunks = dict(y=chunk_plan['y'], x=chunk_plan['x'],
                      y_stag=chunk_plan['y_stag'], x_stag=chunk_plan['x_stag'])
    time_chunk = chunk_plan['time']

    # Get integration information
    accum_types = ch.get_accum_types(ds)
    drop_vars = accum_types.get('constant', [])

    # Get the full date range from the hourly zarr store
    # dates = pd.date_range(start=ds.time[0].values, end=ds.time[-1].values, freq='1h')
    dates = pd.date_range(start=ds.time[0].values, end=end_date, freq='1h')
    con.print(f'    date range: {ds.time.dt.strftime("%Y-%m-%d %H:%M:%S")[0].values} to '
              f'{dates[-1].strftime("%Y-%m-%d %H:%M:%S")}')
    con.print(f'    number of timesteps: {len(dates)}')

    # Get all variables but the constant variables
    source_dataset = ds.drop_vars(drop_vars, errors='ignore')

    # Also drop the solar radiation bucket variables
    source_dataset = source_dataset.drop_vars(solrad_vars.values(), errors='ignore')

    # print('    --- Create template', end=' ')
    template = (source_dataset.chunk(dst_chunks).pipe(xr.zeros_like).isel(time=0, drop=True).expand_dims(time=len(dates)))
    template['time'] = dates
    template = template.chunk({'time': time_chunk})
    con.print(f'Create template:  {time.time() - start_time:0.3f} s')

    # print('    --- Write template', flush=True, end=' ')
    # Writes no data (yet)
    template.to_zarr(dst_zarr, compute=False, consolidated=True, mode='w')
    con.print(f'Write template: {time.time() - start_time:0.3f} s')

    # Remove the existing chunk encoding for constant variables
    for vv in drop_vars:
        try:
            del ds[vv].encoding['chunks']
        except KeyError:
            pass

    # Add the wrf constants
    # print('    --- Write constant variables', end=' ')
    if len(drop_vars) > 0:
        ds[drop_vars].chunk(dst_chunks).to_zarr(dst_zarr, mode='a')
    con.print(f'Write constant variabls: {time.time() - start_time:0.3f} s')


@app.default()
def run_job(config_file: str,
            chunk_index: int):
    """Create a zarr store

    :param config_file: Path to the configuration file
    :param chunk_index: Index of the chunk to process
    """

    job_name = f'wrf_rechunk_{chunk_index}'

    config = Cfg(config_file)

    wrf_dir = resolve_path('wrf_dir', config.wrf_dir)
    constants_file = resolve_path('constants_file', config.constants_file)
    metadata_file = resolve_path('metadata_file', config.metadata_file)
    vars_file = resolve_path('vars_file', config.vars_file)
    # dst_zarr = resolve_path('dst_zarr', config.dst_zarr)
    dst_zarr = Path(config.dst_zarr).resolve()

    temp_dir = Path(config.temp_dir) / f'tmp_{chunk_index:05d}'

    con.print(f'{wrf_dir=}')
    con.print(f'{temp_dir=}')
    con.print(f'{dst_zarr=}')
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
    #                      account="",
    #                      interface='ib0',
    #                      cores=config.cores_per_job,
    #                      memory=config.memory_per_job,
    #                      walltime="05:00:00",
    #                      death_timeout=75)

    cluster = SLURMCluster(job_name=job_name,
                           queue=config.queue,
                           account=config.account,
                           interface=config.interface,
                           cores=config.cores_per_job,    # this is --cpus-per-task
                           processes=config.processes,    # this is numbers of workers for dask
                           memory=f'{config.memory_per_job} GiB',   # total amount of memory for job
                           walltime=config.walltime)

    con.print(cluster.job_script())
    cluster.scale(jobs=config.max_jobs)

    client = Client(cluster)
    client.wait_for_workers(config.processes * config.max_jobs)

    max_mem = f'{(config.memory_per_job / config.cores_per_job) * 0.8:0.1f}GB'
    # con.print(f'Maximum memory per thread for rechunking: {max_mem}')

    # Change the default compressor to Zstd
    zarr.storage.default_compressor = Zstd(level=9)

    fs = fsspec.filesystem('file')

    # Read variables to process
    df_vars = pd.read_csv(vars_file)
    var_list = df_vars['variable'].to_list()
    var_list.append('time')
    con.print(f'Number of variables to process: {len(var_list)}')

    # Read the metadata file for modifications to variable attributes
    var_metadata = ch.read_metadata(metadata_file)

    # Set the target directory
    target_dir = Path(config.target_dir) / f'{config.target_pat}{chunk_index:05d}'
    con.print(f'{target_dir=}')

    # Start date is selected based on chunk index
    st_date = base_date + datetime.timedelta(days=num_days * chunk_index)
    en_date = st_date + delta - datetime.timedelta(days=1)

    con.print(f'{chunk_index}: {st_date.strftime("%Y-%m-%d %H:%M:%S")} to ' +
              f'{en_date.strftime("%Y-%m-%d %H:%M:%S")}')

    if (st_date - base_date).days % num_days != 0:
        con.print(f'[red]ERROR[/]: Start date must begin at the start of a {num_days}-day chunk')

    start_time = time.time()
    ds_wrf = load_wrf_files(num_days=num_days,
                            st_date=st_date,
                            file_pat=config.wrf_file_pat,
                            wrf_dir=wrf_dir)

    rechunk_job(chunk_index=chunk_index,
                max_mem=max_mem,
                ds_wrf=ds_wrf,
                target_dir=target_dir,
                temp_dir=temp_dir,
                constants_file=constants_file,
                var_metadata=var_metadata,
                var_list=var_list,
                chunk_plan=chunk_plan)

    end_time = time.time()
    con.print(f'{chunk_index}, elapsed time: {(end_time - start_time) / 60.:0.3f} minutes')

    # Create the empty final zarr destination
    create_empty_zarr(src_zarr=target_dir,
                      dst_zarr=dst_zarr,
                      end_date=config.end_date,
                      chunk_plan=chunk_plan)

    cluster.scale(0)


def main():
    app()


if __name__ == '__main__':
    main()
