# Finalizing the Spatially Aggregated WRF-Hydro Modeling Application outputs 

**Workflow Authors:** Kevin Sampson and Aubrey Dugger at NSF National Center for Atmospheric Research (NCAR)

The aggregation workflow consists of 2 jupyter notebooks. The python script houses various functions that the jupyter notebooks call to conduct calculations. This workflow aggregates key variables from the 10-year WRF-Hydro Modeling Application forced with CONUS404-BA to the contiguous United States (CONUS) water boundary dataset (WBD) HUC12s for the years 2010-2021. Additional steps are included in this workflow that prepare the data for publication and make the outputs comparable to the [National Hydrologic Model/Precipitation-Runoff Modeling System (NHM/PRMS)](https://www.usgs.gov/mission-areas/water-resources/science/national-hydrologic-model-infrastructure) model outputs. Originally generated for the National Integrated Water Availability Assessment (NIWAA) reports, the 10-year WRF-Hydro modeling application outputs were aggregated to HUC12 catchments by Kevin Sampson and Aubrey Dugger using NCAR HPC systems and published to [Science Base](https://www.sciencebase.gov/catalog/item/6411fd40d34eb496d1cdc99d).

## Input Data
The input data for this workflow consist of the WRF-Hydro modeling application monthly summary outputs and static files. The monthly summaries are the outputs from the hourly to monthly section of this workflow. In addition to variables differing by dimension, they also differ by resolution. This requires different HUC12 grid sizes to be used in the aggregation. 

## Overview 
Tracking computation times for a 3-year subset of WRF-Hydro modeling application on USGS Hovenweep system.

| **Script** | **Description** | **Datasets processed** | **Dask** | **Completion Time** | **Output** | 
| ------ | ------ | ------ | ------ | ------ | ------ |
| 01_Merge_1D_and_2D_files | Combine 1-Dimensional and 2-Dimensional aggregations into one netcdf file | CONUS_HUC12_2D_20111001_20120930.nc & CONUS_HUC12_1D_2011001_20120930.nc | No | 10 min | CONUS_HUC12_WB_combined_19791001_20220930.nc |
| 02_Format | Formatting | CONUS_HUC12_WB_combined_19791001_20220930.nc | No | 10 min | huc12_monthly_wb_iwaa_wrfhydro_WY2011_2013.nc |

## Compute Environment Needs
Users will need to create and activate a conda environment using the [wrfhydro_huc12_agg.yml](02_Spatial_Aggregation/wrfhydro_huc12_agg.yml) file to run the python script and notebooks. For this environment to work, the latest version of Miniforge should be installed in the user area on Hovenweep. Miniconda may work, but has not been tested with this workflow. See the README documentation in the [Spatial Aggregation](02_Spatial_Aggregation/) folder for first time environment set up instructions.  

## Instructions

### 1. Merge 
The [Merge 1-D and 2-D jupyter notebook](03_Finalize/01_Merge_1D_and_2D_files.ipynb) combines the spatially aggregated outputs of the monthly 1-Dimensional & 2-Dimensional WRF-Hydro modeling application outputs into 1 netCDF file. This script also contains plots that allow the user to explore the range in values for each variable.  

### 2. Finalize
The [Format jupyter notebook](03_Finalize/02_Format.ipynb) takes the merged output from step 1 and clarifies variable names, adds character HUCID's, and modifies data types. A 'yrmo' variable is added as a place for year/month information to be stored and to provide an efficient way for R users to access the final datasets. The output from this script is 1 netCDF file containing the monthly WRF-Hydro modeling application outputs aggregated to HUC12s for the years 2011-2013 that is comparable to the netCDF stored on this [Science Base](https://www.sciencebase.gov/catalog/item/6411fd40d34eb496d1cdc99d) page where the original outputs of this workflow are stored. 
  

## Variable Table
<table>
  <tr>
    <th>Source</th>
    <th>File</th>
    <th>Variable</th>
    <th>Name</th>
    <th>Description</th>
    <th>Units</th>
    <th>Type</th>
    <th>Spatial</th>
    <th>In Publication</th>
  </tr>
  <tr>
    <td rowspan="19"><a href="#WRF-Hydro"><b>WRF-Hydro</b></a></td>
    <td rowspan="12">LDASOUT</td>
    <td>deltaACCET</td>
    <td>ET change</td>
    <td>Total monthly evapotranspiration (land only)</td>
    <td>mm</td>
    <td>2D</td>
    <td>1000 m grid</td>
    <td>---</td>
  </tr>
  <tr>
    <td>deltaACSNOW</td>
    <td>Snowfall change</td>
    <td>Total monthly snowfall (land only)</td>
    <td>mm</td>
    <td>2D</td>
    <td>1000 m grid</td>
    <td>---</td>
  </tr>
  <tr>
    <td>deltaSNEQV</td>
    <td>SWE change</td>
    <td>Average monthly snow water equivalent (land only)</td>
    <td>mm</td>    
    <td>2D</td>
    <td>1000 m grid</td>
    <td>---</td>      
  </tr>
  <tr>
    <td>deltaSOILM</td>
    <td>Soil Water change</td>
    <td>Average monthly soil moisture in 2m soil column (land only)</td>
    <td>mm</td>
    <td>2D</td>
    <td>1000 m grid</td>
    <td>---</td>      
  </tr>
  <tr>
    <td>deltaUGDRNOFF</td>
    <td>Recharge change</td>
    <td>Total monthly recharge (land only)</td>
    <td>mm</td> 
    <td>2D</td>
    <td>1000 m grid</td>
    <td>---</td>      
  </tr>
  <tr>
    <td>deltaSOILM_depthmean</td>
    <td>---</td>
    <td>Change in depth-mean volumetric soil moisture, ratio of water volume to soil volume (month end minus month start) </td>
    <td>---</td>  
    <td>2D</td>
    <td>1000 m grid</td>
    <td>---</td>      
  </tr>
  <tr>
    <td>avgSNEQV</td>
    <td>SWE average</td>
    <td>Mean snow water equivalent </td>
    <td>mm</td>
    <td>2D</td>
    <td>1000 m grid</td>
    <td>Yes</td>      
  </tr>
  <tr>
    <td>avgSOILM</td>
    <td>Soil Water average</td>
    <td>Mean volumetric soil moisture by layer </td>
    <td>m3/m3</td>
    <td>2D</td>
    <td>1000 m grid</td>     
    <td>Yes</td>   
  </tr>
  <tr>
    <td>avgSOILM_depthmean</td>
    <td>---</td>
    <td>Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) over month </td>
    <td>---</td>
    <td>2D</td>
    <td>1000 m grid</td>     
    <td>---</td> 
  </tr>
  <tr>
    <td>avgSOILM_wltadj_depthmean</td>
    <td>---</td>
    <td>Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) minus wilting point over month </td>
    <td>---</td>
    <td>2D</td>
    <td>1000 m grid</td>
    <td>Yes</td>      
  </tr>
  <tr>
    <td>avgSOILSAT</td>
    <td>Soil Saturation average</td>
    <td>Average monthly fractional soil saturation in 2m soil column (land only) </td>
    <td>---</td>
    <td>2D</td>
    <td>1000 m grid</td>      
    <td>Yes</td>
  </tr>
  <tr>
    <td>avgSOILSAT_wltadj_top1</td>
    <td>---</td> 
    <td>Average fractional soil saturation above wilting point (soil moisture minus wilting point divided by maximum water content minus wilting point) over top layer (top 10cm) over month</td>
    <td>---</td>
    <td>2D</td>
    <td>1000 m grid</td>  
    <td>Yes</td>      
  </tr>
  <tr>
    <td rowspan="4">GWOUT</td>
    <td>totOutflow</td>
    <td>Total outflow volume over month</td>
    <td>---</td>
    <td>m3</td>
    <td>1D</td>
    <td>crosswalk</td>
    <td>---</td> 
  </tr>
  <tr>
    <td>totInflow</td>
    <td>Total inflow volume over month</td>
    <td>---</td>
    <td>m3</td>
    <td>1D</td>
    <td>crosswalk</td>
    <td>---</td> 
  </tr>
  <tr>
    <td>deltaDepth</td>
    <td>Change in baseflow bucket storage (month end minus month start)</td>
    <td>---</td>
    <td>mm</td>
    <td>1D</td>
    <td>crosswalk</td>
    <td>---</td> 
  </tr>
  <tr>
    <td>bucket_depth</td>
    <td>Ground Water Store</td>
    <td>Average monthly groundwater storage</td>
    <td>mm</td>
    <td>1D</td>
    <td>crosswalk</td> 
    <td>Yes</td>
  </tr>
  <tr>
    <td rowspan="3">CHRTOUT</td>
    <td>totqBucket</td>
    <td>Baseflow</td>
    <td>Total monthly baseflow</td>
    <td>mm</td>
    <td>1D</td>
    <td>crosswalk</td> 
    <td>Yes</td>
  </tr>
  <tr>
    <td>totqSfcLatRunoff</td>
    <td>Surfaceflow</td>
    <td>Total monthly surface flow</td>
    <td>mm</td>
    <td>1D</td>
    <td>crosswalk</td> 
    <td>Yes</td>
  </tr>
  <tr>
    <td>totStreamflow</td>
    <td>---</td>
    <td>Total streamflow volume over month</td>
    <td>---</td>
    <td>1D</td>
    <td>crosswalk</td> 
    <td>---</td>
  </tr>
  <tr>
    <td rowspan="2"><a href="#CONUS404-BA"><b>CONUS404-BA</b></a></td>
    <td rowspan="2">LDASIN</td>
    <td>totPRECIP</td>
    <td>Precipitation</td>
    <td>Total monthly precipitation</td>
    <td>mm</td>
    <td>2D</td>
    <td>1000 m grid</td>  
    <td>Yes</td>
  </tr>
    <td>avgT2D</td>
    <td>Temperature</td>
    <td>Average 2-m air temperature</td>  
    <td>K</td>  
    <td>2D</td>
    <td>1000 m grid</td> 
    <td>---</td>     
  </tr>
</table>
