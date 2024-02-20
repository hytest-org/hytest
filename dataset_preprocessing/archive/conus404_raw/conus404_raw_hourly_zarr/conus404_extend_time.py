#!/usr/bin/env python

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import argparse
import json
import pandas as pd
import xarray as xr

# from dask.distributed import Client
from zarr.convenience import consolidate_metadata
from zarr.util import NumberEncoder

from rich.console import Console
from rich import pretty

pretty.install()
con = Console(record=True)


def main():
    parser = argparse.ArgumentParser(description='Extend time range in zarr dataset by editing the metadata')
    parser.add_argument('--zarr', help='Zarr dataset to extend time range')
    parser.add_argument('--enddate', help='New ending date for zarr dataset (YYYY-MM-DD)')
    parser.add_argument('--freq', help='Frequency to use for timesteps (e.g. "1h")', default='1h')

    args = parser.parse_args()

    src_zarr_dir = args.zarr
    src_filename = f'{src_zarr_dir}/.zmetadata'

    con.print(f'Zarr store: {src_zarr_dir}')
    con.print(f'New end date: {args.enddate}')
    con.print('-'*40)

    # Read the consolidated metadata
    with open(src_filename, 'r') as in_hdl:
        data = json.load(in_hdl)

    # Open the target zarr dataset
    con.print('  reading zarr store')
    ds = xr.open_dataset(src_zarr_dir, engine='zarr',
                         backend_kwargs=dict(consolidated=True), chunks={})

    # Define the new time range
    # Date range should always start from the original starting date in the zarr dataset
    dates = pd.date_range(start=ds.time[0].values, end=args.enddate, freq=args.freq)

    con.print('  reading metadata')
    # Get the index for time dimension of each variable from the consolidated metadata
    time_index = {}

    for kk, vv in data['metadata'].items():
        if kk in ['.zattrs', '.zgroup']:
            continue

        varname, metatype = kk.split('/')

        if metatype == '.zattrs':
            try:
                time_index[varname] = vv['_ARRAY_DIMENSIONS'].index('time')
            except ValueError:
                # Time dimension not used for this variable
                pass

            # con.print(f'{kk} {vv["_ARRAY_DIMENSIONS"]}')

    # Index for the time dimension for each variable
    # con.print(time_index)

    # Change the size of the time dimension in the unconsolidated metadata for each variable
    # This will overwrite the original .zarray file for each variable
    con.print('  updating metadata')
    for kk, vv in time_index.items():
        cfilename = f'{src_zarr_dir}/{kk}/.zarray'

        with open(cfilename, 'r') as in_hdl:
            uncol_meta = json.load(in_hdl)

        # Update the shape of the variable
        uncol_meta['shape'][vv] = len(dates)

        # con.print('-'*10, kk, '-'*10)
        # con.print(uncol_meta)

        # Write the updated metadata file
        with open(cfilename, 'w') as out_hdl:
            json.dump(uncol_meta, out_hdl, indent=4, sort_keys=True, ensure_ascii=True, separators=(',', ': '), cls=NumberEncoder)

    ds.close()

    con.print('  consolidating metadata')
    # Re-open the zarr datastore using the unconsolidated metadata
    ds = xr.open_dataset(src_zarr_dir, engine='zarr',
                         backend_kwargs=dict(consolidated=False), chunks={})

    # Write a new consolidated metadata file
    consolidate_metadata(store=src_zarr_dir, metadata_key='.zmetadata')

    # Write the new time values
    con.print('  updating time variable in zarr store')
    save_enc = ds['time'].encoding

    ds.coords['time'] = dates
    ds['time'].encoding.update(save_enc)

    ds[['time']].to_zarr(src_zarr_dir, mode='a')


if __name__ == '__main__':
    main()
