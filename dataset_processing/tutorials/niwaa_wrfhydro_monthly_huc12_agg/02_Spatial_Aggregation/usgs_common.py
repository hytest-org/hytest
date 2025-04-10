'''
03/03/2022
    This script is inialized to store common datasets, variables, and functions 
    for use in the USGS_Water water budget processing workflow.
    Author: Aubrey Dugger
    Updated: Leah Staub 4/7/2025
'''

# --- Import Modules --- #

import os
import sys
import pathlib
import time
from pathlib import Path

import xarray as xr
import flox
import flox.xarray
import numpy as np
import pandas as pd
from osgeo import gdal
from osgeo import gdal_array
from osgeo import gdalconst

# --- End Import core modules --- #

# --- Region cutout indices from the CONUS domain --- #

# Using i/j indices - borrow the NCKS command dimension subset indices from script_forcing_subset.txt
# This should be the i and j index for the westmost (i0) and easternmost (i1) and southernmost (j0) and northernmost (j1)
# extent of the domain (inclusive)
region_bboxes = {
    'drb': {
        'LDASOUT': {
            'j1': 2434, 'j0': 2021,
            'i1': 4153, 'i0': 3967, },
        'RTOUT': {
            'j1': 9739, 'j0': 8084,
            'i1': 16615, 'i0': 15868, }, }}

# --- End Region cutout indices from the CONUS domain --- #

# --- Domain files --- #

# NWM geogrid (LSM) file
geogrid = r'/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_geo_em.d01.CONUS_1km_NIWAAv1.0.nc'

# NWM LDASOUT Spatial Metadata file - contains spatial metadata for the LSM grid
geogrid_SM = r'/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_GEOGRID_LDASOUT_Spatial_Metadata_CONUS_1km_NIWAAv1.0.nc'

# NWM Fulldom_hires netCDF file - contains routing variables on the routing grid
fulldom = r'/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_Fulldom_CONUS_250m_NIWAAv1.0.nc'

# NWM channel routing parameters (RouteLink)
chrt_parms = r'/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_RouteLink_CONUS_NIWAAv1.0.nc'

# NWM groundwater bucket parameters (GWBUCKPARM)
gw_parms = r'/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_GWBUCKPARM_CONUS_NIWAAv1.0.nc'

# Soil properties file
soil_props = r'/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_soil_properties_CONUS_1km_NIWAAv1.0.nc'

# --- End Domain files --- #

# --- Variables to be used for water budget calculation for each type of file --- #

LDASOUT_vars = ['ACCET', 'UGDRNOFF', 'SOIL_M', 'SNEQV', ]

RTOUT_vars = ['sfcheadsubrt', ]

GWOUT_vars = ['bucket_depth', 'outflow']

CHRTOUT_vars = ['qBucket', 'qSfcLatRunoff', ]

PRECIP_vars = ['RAINRATE', ]

LAKEOUT_vars = ['inflow', 'outflow', 'water_sfc_elev', ]

# --- Coordinate variable and dimension name information --- #

# 1D Coordinates
time_coord = 'time'
feature_id = 'link'

# --- End Coordinate variable and dimension name information --- #

# --- Variables that should be masked to the LANDMASK for correct computation --- #

landmask_vars = ['RAINRATE', ]

# --- End variables that should be masked to the LANDMASk for correct computation --- #

# --- Other settings --- #

# NWM grid sizes
LSM_grid_size_y = 3840
LSM_grid_size_x = 4608
RT_grid_size_y = 15360
RT_grid_size_x = 18432

# Soil layer thickness (mm) for calculating bulk volume in soil column
soil_depths_mm = [100, 300, 600, 1000]

# --- End Other settings --- #

# --- Functions --- #

def get_size_gb(input_da, silent=False):
    '''
    Get the size of an Xarray DataSet or DataArray and print total size
    '''
    # Print out information about the input dataset
    dataset_size_GB = input_da.nbytes/(1024.**3)
    if not silent:
        print('Size of input dataset:\t{0:3.2f} Gb'.format(dataset_size_GB))
    return dataset_size_GB

def add_SM_to_ds(ds, Variable, ds_geo=None, grid_type='LDASOUT', latVar='lat', lonVar='lon'):
    '''
    This function will add 1D spatial metadata for geocentric coordinates (lat lon).
    '''
    
    # Variable attributes
    if grid_type in ['GWOUT', 'CHRTOUT', 'LAKEOUT']:
        ds[Variable].attrs['coordinates'] = "time lat lon"
        ds[latVar].attrs['long_name'] = "latitude of the polygon centroid"
        ds[latVar].attrs['units'] = "degrees_north"
        ds[latVar].attrs['standard_name'] = "latitude"
        ds[latVar].attrs['coordinates'] = "lat lon"
        ds[lonVar].attrs['long_name'] = "longitude of the polygon centroid"
        ds[lonVar].attrs['units'] = "degrees_east"
        ds[lonVar].attrs['standard_name'] = "longitude"
        ds[lonVar].attrs['coordinates'] = "lat lon"  
        ds.attrs['featureType'] = "timeSeries"
        
    if grid_type == 'LDASOUT':
        for attr in ds_geo.attrs:
            ds.attrs[attr] = ds_geo.attrs[attr]
    
    if grid_type == 'RTOUT':
        ds['crs'] = ds_geo['crs']
        ds[Variable].attrs['grid_mapping'] = "crs"
        ds[Variable].attrs['coordinates'] = "time y x"
        ds[Variable].attrs['esri_pe_string'] = ds_geo['crs'].attrs['esri_pe_string']
        ds.attrs['proj4'] = ds_geo.attrs['proj4']
    
    # Global attributes
    ds.attrs['Convention'] = "CF-1.6"
    return ds

def return_raster_array(in_file):
    '''
    Read a GDAL-compatible raster file from disk and return the array of raster
    values as well as the nodata value.
    '''
    ds = gdal.Open(in_file, gdalconst.GA_ReadOnly)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    ndv = band.GetNoDataValue()                                                 # Obtain nodata value
    ds = band = None
    return arr, ndv

def flip_dim(array_dimensions, DimToFlip='south_north'):
    '''
    Function to flip a dimension based on provided dimension names.

        array_dimensions - A list of dimension names for the input dataset
        DimToFlip - The dimension to reverse.
    '''

    # Determine how to slice the array in order to fit into the netCDF
    ind = [slice(None)] * len(array_dimensions)                                 # Build array slice as default (:)

    # Flip a dimension if necessary
    if DimToFlip in array_dimensions:
        flipIdx = array_dimensions.index(DimToFlip)
        ind[flipIdx] = slice(None,None,-1)
        print("    Reversing order of dimension '{0}'".format(array_dimensions[flipIdx]))
        del flipIdx
    else:
        print("    Requested dimension for reversal not found '{0}'.".format(DimToFlip))
    return tuple(ind)
    
# https://stackoverflow.com/questions/64100160/numpy-split-array-into-chunks-of-equal-size-with-remainder
def split_given_size(a, size):
    return np.split(a, np.arange(size,len(a),size))

def run_flox_old(data, flox_by, flox_method='cohorts', flox_function="mean", n=1):
    '''
    This function appears to return, but takes a very long time after computation to return the output.
    '''
    tic1 = time.time()
    output = flox.groupby_reduce(
        data, 
        by=flox_by, 
        func=flox_function, 
        method=flox_method)
    print('\t[{0}] Flox groupby method ({1}): {2} records in {3:3.2f} seconds.'.format(n, flox_function, output[0].shape[0], time.time()-tic1))
    return output

def run_flox(data, flox_by, flox_function="mean", n=1):
    tic1 = time.time()
    #output = flox.xarray.xarray_reduce(data, flox_by, func=flox_function)
    output = flox.xarray.xarray_reduce(data, flox_by, func=flox_function).compute()
    print('\t[{0}]    Calculated zonal {1} in {2:3.2f} seconds.'.format(n, flox_function, time.time()-tic1))
    #print('\t[{0}] Flox groupby method ({1}): {2} records in {3:3.2f} seconds.'.format(n, flox_function, output[0].shape[0], time.time()-tic1))
    #return output.compute()
    return output

def write_csv(data_out, out_file, columns=[], index=None, drops=None):
    # Write output file
    tic1 = time.time()
    df_out = data_out.to_dataframe()
    if drops is not None:
        df_out = df_out.drop(columns=drops)
    df_out.to_csv(out_file)
    print('\t      Output file written in {0:3.2f} seconds.'.format(time.time()-tic1))

# Function to list files in a directory
def get_files_wildcard(inDir, file_pattern='*', recursive=False, silent=False):
    # Examine files in input directory
    if recursive==True:
        file_in = sorted([path for path in Path(inDir).rglob(file_pattern)])
    else:
        file_in = sorted([path for path in Path(inDir).glob(file_pattern)])
    if not silent:
        print('Found {0} files using wildcard "{1}" (recursive={2}) in the input directory:\n\t {3}'.format(len(file_in), file_pattern, recursive, inDir))
    return file_in

# Function to describe the structure of the input file
def report_structure(ds, variable, time_coord=time_coord, silent=False, xy_chunks=True):
    '''
    Inputs:
        ds - an xarray DataSet object.
        variable - String - a variable in the input DataSet object to examine.
        time_coord - string - the name of the time coordinate in the input DataSet object.
    Outputs:
        ds - The xarray DataSet object, possibly altered to unify chunk sizes
        timesteps - The time values in the input ifle
        x_chunk_sizes - The size of the DataSet chunk size in the x dimension
        y_chunk_sizes - The size of the DataSet chunk size in the y dimension
    '''

    # Pull the timesteps from the input file
    timesteps = ds[time_coord].values
    if not silent:
        print('Found {0} timestep(s) in input file'.format(timesteps.shape[0]))

    # Print out information about the input dataset
    dataset_size_GB = get_size_gb(ds, silent=True)
    if not silent:
        print('Size of input dataset:  {0:3.2f} Gb'.format(dataset_size_GB))

    # Find out the size of one timestep (the unit of processing)
    timestep_size_GB = get_size_gb(ds[variable].isel({time_coord:0}), silent=True)
    if not silent:
        print('Size of 1 timesteps in dataset:  {0:3.3f} Gb'.format(timestep_size_GB))

    # Unify chunks just in case they are not uniform
    ds = ds.unify_chunks()

    # Interpret time as a string
    time_chunk_sizes = ds.chunks[time_coord]
    full_time_chunk_ds_size_GB = ds[variable].isel({time_coord:slice(0, time_chunk_sizes[0])}).nbytes/(1024**3)
    if not silent:
        print('Size of 1 time chunk ({0} timesteps) for full extent of dataset:  {1:3.3f} Gb'.format(time_chunk_sizes[0], full_time_chunk_ds_size_GB)) 
        print('Time chunk sizes [first, last]: {0}, {1}'.format(time_chunk_sizes[0], time_chunk_sizes[-1]))

    # Determine chunk sizes in X and Y
    if xy_chunks:
        x_coord = 'x'
        y_coord = 'y'
        x_chunk_sizes = ds.chunks['x']
        y_chunk_sizes = ds.chunks['y']
    else:
        x_coord = 'west_east'
        y_coord = 'south_north'
        x_chunk_sizes = ds.chunks[x_coord]
        y_chunk_sizes = ds.chunks[y_coord]
    full_chunk_ds_size_GB = ds[variable].isel({time_coord:slice(0, time_chunk_sizes[0]), x_coord:slice(0, x_chunk_sizes[0]), y_coord:slice(0, y_chunk_sizes[0])}).nbytes/(1024**3)
    if not silent:
        print('Size of 1 chunk, ({0},{1}) cells, of the dataset:  {2:3.3f} Gb'.format(x_chunk_sizes[0], y_chunk_sizes[0], full_chunk_ds_size_GB)) 
        print('X chunk sizes [first, last]: {0}, {1}'.format(x_chunk_sizes[0], x_chunk_sizes[-1]))
        print('Y chunk sizes [first, last]: {0}, {1}'.format(y_chunk_sizes[0], y_chunk_sizes[-1]))       
    return ds, timesteps, x_chunk_sizes, y_chunk_sizes, time_chunk_sizes
    
# This function is used if the input files end in a YYYMM datestring.
def extract_dates(in_paths=[], format_str='%Y%m'):
    '''
    This function will take an input path and extract a date object from the filename. 
    Assumes that the filename ends with "_{datestring}.nc" (default = YYYYMM)
    '''
    dt_strings = [os.path.basename(in_path).split('.nc')[0].split('_')[1] for in_path in in_paths]
    dt_obj = pd.to_datetime(dt_strings, format=format_str)
    return dt_obj

def remove_atts(ds):
    '''
    Remove unecessary spatial attributes from input files. 
    '''
    
    # Eliminate any unecessary variable attributes (such as spatial metadata)
    for variable in ds.data_vars:
        if 'grid_mapping' in ds[variable].attrs:
            del ds[variable].attrs['grid_mapping']
        if 'esri_pe_string' in ds[variable].attrs:
            del ds[variable].attrs['esri_pe_string']
        if 'proj4' in ds[variable].attrs:
            del ds[variable].attrs['proj4']
        if variable == 'landmask':
            ds[variable].attrs = {'description':'Fraction of gridded land area in each HUC12'}
        if variable == 'total_gridded_area':
            ds[variable].attrs = {'description':'Number of 1km grid cells for HUC12. Equivalend to square kilometers. Based on grid association of each HUC12'}

    # Now eliminate unnecessary global attributes
    if 'grid_mapping' in ds.attrs:
        del ds.attrs['grid_mapping']
    if 'units' in ds.attrs:
        del ds.attrs['units']  
    if 'esri_pe_string' in ds.attrs:
        del ds.attrs['esri_pe_string'] 
    if 'long_name' in ds.attrs:
        del ds.attrs['long_name'] 
    if '_FillValue' in ds.attrs:
        del ds.attrs['_FillValue'] 
    if 'missing_value' in ds.attrs:
        del ds.attrs['missing_value'] 
    return ds

# Use a 2D grid of zone IDs to perform spatial aggregation.
# This is a representation of the zones on the same grid as the analysis data.
def add_raster_zone(ds, NWM_type, zone_raster, zone_name='zone', zone_nodata=0, landmask_results=False):
    '''
    Given an xarray DataSet object, add a 2D array of gridded zones for spatial 
    aggreagation.
    '''
    
    # Sort out resolution and input files
    if NWM_type == 'RTOUT':
        LSM_grid = False
    elif NWM_type == 'LDASOUT':
        LSM_grid = True
    print('Using raster grid of zones for spatial aggregation: {0}'.format(zone_raster))
    
    # Read in the raster that defines the zones
    zone_arr, zone_ndv = return_raster_array(zone_raster)
    zone_type = zone_arr.dtype

    # Flip the raster if necessary - easier than flipping each input array from the model data
    if LSM_grid:
        zone_arr = zone_arr[flip_dim(['y', 'x'], DimToFlip='y')]

    # Replace nodata values with np.nan, which requires converting to floating point.    
    zone_arr = zone_arr.astype('float')    
    zone_arr[zone_arr==zone_nodata] = np.nan

    # Obtain unique values
    zone_uniques = np.unique(zone_arr)
    zones_unique = zone_uniques[zone_uniques!=np.nan]
    print('{0} zones found in the input dataset'.format(zones_unique.shape[0]-1))
    del zone_uniques, zones_unique
    
    # Add zones to the Xarray DataSet object
    zones = xr.DataArray(zone_arr, dims=("y", "x"), name=zone_name)
    ds[zone_name] = zones.fillna(-1).astype(int)   # workaround flox bug
    del zones
    
    # Obtain landmask grid
    if landmask_results and NWM_type == 'LDASOUT':
        print('  Masking zone grid to LSM LANDMASK variable')
        landmask = xr.open_dataset(geogrid)['LANDMASK'].squeeze()
        zone_masked = zone_arr.copy()
        zone_masked[landmask==0] = np.nan
        masked_zone_name = '{0}_masked'.format(zone_name)
        zones_ma = xr.DataArray(zone_masked, dims=("y", "x"), name=masked_zone_name)
        
        # Filling NaN areas (water or ocean) with -1 removes it from that HUC.
        ds[masked_zone_name] = zones_ma.fillna(-1).astype(int)   # workaround flox bug
        
        # Save the landmask (1s and 0s)
        landmask_da = xr.DataArray(landmask, dims=("y", "x"), name='landmask')
        ds['landmask'] = landmask_da.fillna(0).astype(int)   # workaround flox bug
        del landmask, zones_ma
    
        # Obtain unique values
        zone_uniques = np.unique(zone_masked)
        zones_unique = zone_uniques[zone_uniques!=np.nan]
        print('{0} zones found in the input dataset after land-masking'.format(zones_unique.shape[0]-1))
        del zone_uniques, zones_unique, zone_masked
    else:
        masked_zone_name = ''
        
    del zone_arr
    return ds, zone_type, masked_zone_name
    
def soil_depth_info(soil_layer_index=[0, 1, 2, 3], soil_depths=[100, 300, 600, 1000]):
    '''
    Given soil properties info and depths, this function will reutrn 
    xarray DataArray objects that can be used to manipulate soil 
    DataArrays.
    
    soil_layer_index - List of soil layer coordinates
    soil_depths      - List of soil depths in mm.
    '''

    # Create DataArray with soil layer depths
    da_soil_depth = xr.DataArray(
        data=np.array(soil_depths),
        dims=["soil_layers_stag"],
        coords=dict(soil_layers_stag=soil_layer_index),
        attrs=dict(description="soil depth", units="mm"))

    #  Soil depth fraction:        layer depth / total depth
    da_soil_depth_frac = xr.DataArray(
        data=da_soil_depth.values / da_soil_depth.sum().values,
        dims=["soil_layers_stag"],
        coords=dict(soil_layers_stag=soil_layer_index),
        attrs=dict(description="soil depth fraction", units="-"))   
    
    return da_soil_depth, da_soil_depth_frac
    
def soil_depth_avg_val(da_ldasout, weights):
    '''
    Calculate a depth averaged soil value based on soil layer depths.
    
    ds_ldasout  -   DataSet object containing a soil_layers_stag dimension and 
                    soil moisture volume (m^3 per m^3) to be converted to depth-weighted average.
    weights     -   DataArray of soil depth fractions. Must sum to 1.0 and contain a mathcing 
                    dimension to the input DataSet (such as soil_layers_stag).
    '''
    
    # Multiply by depth fraction and sum the values over depth dimension to get depth averaged value
    return (da_ldasout * weights).sum(dim='soil_layers_stag')
    
def soil_water_pct_sat(da_ldasout, file_soil_param, soil_depths=[100, 300, 600, 1000]):
    '''
    Calculate soil water percent saturation, weighted by soil layer depths. 
    
    ds_ldasout  -   DataSet object containing a soil_layers_stag dimension and 
                    soil moisture volume (m^3 per m^3) to be converted to saturation frac.
    file_soil_param - The netCDF SoilProperties file that gives the maximum soil water volume (smcmax)
    soil_depths -   list of soil depths. Units irrelevant as it will be used to 
                    weight the soil_layers_stag dimension.
    '''

    # Open the soil properties file to obtain smcmax
    ds_soil_param = xr.open_dataset(soil_prop_file, engine='netcdf4').squeeze('Time')
    ds_soil_param = ds_soil_param.rename_dims({'west_east': 'x', 'south_north': 'y'})
    
    # Obtain soil layer depth and fraction information as xarray DataArrays
    da_soil_depth, da_soil_depth_frac = soil_depth_info(soil_layer_index=ds_soil_param.soil_layers_stag, 
                                                        soil_depths=soil_depths)
            
    result = (
        ((da_ldasout / ds_soil_param['smcmax']) * da_soil_depth_frac)
        .sum(dim='soil_layers_stag')
        .rename('soil_water_pct_sat')) # .persist()

    ds_soil_param.close()
    return result

# --- End Functions --- #

if __name__ == '__main__':
    pass