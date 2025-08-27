# Aggregating the WRF-Hydro Modeling Application output to twelve-digit hydrologic unit codes (HUC12s)
**Workflow Authors:** Kevin Sampson and Aubrey Dugger at NSF National Center for Atmospheric Research (NCAR)

The aggregation workflow consists of 1 python script and 2 jupyter notebooks. The python script houses various functions that the jupyter notebooks call to conduct calculations. This workflow aggregates key variables from the 10-year WRF-Hydro Modeling Application forced with CONUS404-BA to the contiguous United States (CONUS) water boundary dataset (WBD) HUC12s for the years 2010-2021. Additional steps are included in this workflow that prepare the data for publication and make the outputs comparable to the [National Hydrologic Model/Precipitation-Runoff Modeling System (NHM/PRMS)](https://www.usgs.gov/mission-areas/water-resources/science/national-hydrologic-model-infrastructure) model outputs. Originally generated for the National Integrated Water Availability Assessment (NIWAA) reports, the 10-year WRF-Hydro modeling application outputs were aggregated to HUC12 catchments by Kevin Sampson and Aubrey Dugger using NCAR HPC systems and published to [Science Base](https://www.sciencebase.gov/catalog/item/6411fd40d34eb496d1cdc99d).

## Input Data
The input data for this workflow consist of the WRF-Hydro modeling application monthly summary outputs and static files. The monthly summaries are the outputs from the hourly to monthly section of this workflow. In addition to variables differing by dimension, they also differ by resolution. This requires different HUC12 grid sizes to be used in the aggregation. 

## Overview 
Tracking computation times for a 3-year subset of WRF-Hydro modeling application on USGS Hovenweep system.

| **Script** | **Description** | **Datasets processed** | **Dask** | **Completion Time** | **Output** | 
| ------ | ------ | ------ | ------ | ------ | ------ |
| 01_2D_spatial_aggregation | Aggregation to HUC12s of 2-Dimensional variables | monthly LDASOUT & LDASIN | Yes | 2 hours | CONUS_HUC12_2D_WY2011_2013.nc |
| 02_1D_spatial_aggregation | Aggregation to HUC12s of 1-Dimensional variables | monthly GWOUT & CHRTOUT | No | 2.5 hours | CONUS_HUC12_1D_WY2011_2013.nc |
| usgs_common | python script containg functions used in aggregation | --- | No | --- | --- |

## Compute Environment Needs
Users will need to create and activate a conda environment using the [wrfhydro_huc12_agg.yml](wrfhydro_huc12_agg.yml) file to run the python script and notebooks. For this environment to work, the latest version of Miniforge should be installed in the user area on Hovenweep. Miniconda may work, but has not been tested with this workflow. 

#### Ensure Miniforge is installed
```
# check to see if miniforge is installed
which conda

# if it returned something like what is listed below, then miniforge is installed. 
/home/youruser/miniforge3/bin/conda

# if there is not miniforge listed, it will need to be installed
```

#### Installing Miniforge
```
# go to this link and make sure this is the latest version before entering into powershell console
wget https://github.com/conda-forge/miniforge/releases/download/24.7.1-2/Miniforge3-24.7.1-2-Linux-x86_64.sh 

# install
bash Miniforge3-24.7.1-2-Linux-x86_64.sh 

# be sure to type yes when prompted, it should be twice
# close out of powershell and reopen to finish the installation process
```

#### Installing conda environment from wrfhydro_huc12_agg.yml file   
```
# cd to folder containing wrfhydro_huc12_agg.yml and create the environment.
conda env create -f wrfhydro_huc12_agg.yml

# activate conda environment
conda activate wrfhydro_huc12_agg
```
Since this portion of the workflow utilizes Dask, it is important that the correct resources are allocated. The method used by the HyTEST team leverages the OnDemand Jupyter Notebook launcher hosted on [ARC HPC Portal](https://hpcportal.cr.usgs.gov/). When launching a jupyter notebook session, boxes can be selected that allow the repository file path is and the environment to be entered prior to launching a session. Be sure to enter the following information before launching a session:
- **cpu** as the nodetype
- request a total of **2 cores**
- request at least **150GB** of memory. 

*Note:* Although the aggregation part of this workflow does not always use 150GB, dask will need that memory for the 2-Dimensional aggregation script. 

## Instructions
### 1. Set-up
Confirm that the [usgs_common.py](wrfhydro_huc12_agg.yml) python script has the correct paths to the WRF-Hydro modeling application output static files under the "Domain Files" section. The paths currently are set up to point to the HyTEST directory on hovenweep where the 3-year subset of the data is stored. This script has multiple functions that are called into the 1-D and 2-D aggregation jupyter notebooks. 

### 2. 2-D Aggregation
The [2-Dimensional Aggregation jupyter notebook](01_2D_spatial_aggregation.ipynb) aggregates the 2-Dimensional WRF-Hydro modeling application outputs LDASOUT (monthly outputs named water_YYYYMM.nc) and LDASIN (monthly outputs named clim_YYYYMM.nc) to HUC12 basins, using the 1000 m grid file. The file paths for the LDASOUT and LDASIN monthly data, the 1000 m HUC12 grid file, and the location for the 2D aggregated outputs to be stored will need to be specified. This script will spin up a dask cluster to parallelize the aggregation, a link to the dask dashboard is provided to monitor workers during calculations. Once this script has finished processing, the dask cluster will need to be spun down and closed. The product from this script will be 1 netCDF file containing the spatially aggregated outputs of the 2-Dimensional WRF-Hydro monthly modeling application outputs for the years 2011-2013.   

### 3. 1-D Aggregation
The [1-Dimensional Aggregation jupyter notebook](02_1D_spatial_aggregation.ipynb) aggregates the 1-Dimensional WRF-Hydro modeling application outputs GWOUT (monthly outputs named gw_YYYYMM.nc) and CHRTOUT (monthly outputs named chrtout_YYYYMM.nc) to HUC12 basins, using the crosswalk csv file. The file paths for the GWOUT and CHRTOUT monthly data, the HUC12 crosswalk file, and the location for the 1D aggregated outputs to be stored will need to be specified. The product from this script will be 1 netCDF file containing the spatially aggregated outputs of the 1-Dimensional WRF-Hydro monthly modeling application outputs for the years 2011-2013.

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
