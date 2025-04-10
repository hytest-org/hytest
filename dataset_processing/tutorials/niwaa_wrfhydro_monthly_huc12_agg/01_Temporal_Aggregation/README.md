# Summarizing the WRF-Hydro Modeling Application outputs from hourly to monthly. 
**Workflow Authors:** Kevin Sampson and Aubrey Dugger at NSF National Center for Atmospheric Research (NCAR)

WRF-Hydro Modeling Application outputs are provided at the hourly time scale while CONUS404-BA temperature and precipitation outputs are provided at the 3-hour timescale. Many water-budget components are summarized at the monthly scale because daily or hourly scales may introduce unpredictable variation in model output. Monthly temporal resolution can also make it easier to identify patterns in the data. Additionally, NHM-PRMS data is at the monthly time scale, so summarizing WRF-Hydro outputs to a monthly time scale will make comparisons between the two models possible.   

## Overview
NCO is required for this workflow: [netCDF Operator](https://nco.sourceforge.net/). USGS HPC Hovenweep has an NCO module set up that needs to be loaded before the workflow is run. 

To keep processing times low, this workflow has been parallelized. There are 4 variables that need to be converted from hourly to monthly: LDASOUT, LDASIN, CHRTOUT, and GWOUT. Each variable has a shell script that does the hourly to monthly calculations. These can be run for a single year or called into a slurm file to run multiple years at once. 

| **Source** | **File** | **File Structure** | **Time Step** | **Shell Script** | **Slurm file** | **Processing Time** |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| WRF-Hydro | LDASOUT | Calendar Year | 3-hourly | nco_process_ldasout.sh | ldasout_nco.slurm | XXX |
| CONUS404-BA | LDASIN | Water Year | hourly | nco_process_clim.sh | clim_nco.slurm | XXX |
| WRF-Hydro | GWOUT | Calendar Year | hourly | nco_process_gwout.sh | gwout_nco.slurm | XXX |
| WRF-Hydro | CHRTOUT | Calendar Year | hourly | nco_process_chrtout.sh | chrtout_nco.slurm | XXX |

## LDASOUT:
#### nco_process_ldasout.sh
##### Script Preparations:
You will need to specify three paths: 
  - The location of the 3-hour WRF-Hydro output LDASOUT files.
  - The location of the static soil properties file.
  - The location of where to save the monthly outputs.
##### Overview:
-Process porosity & wilting point parameters
-Process accumulated flux & state differences
-Process mean states
-Cleanup names

## GWOUT:
#### nco_process_gwout.sh
##### Script Preparations:
You will need to specify two paths: 
  - The location of the hourly WRF-Hydro output GWOUT files.
  - The location of where to save the monthly outputs.
*Note: this script has some additional lines of code to deal with filetypes in the depth variable. Renaming the variable seems to fix this bug. Another option is to use older version of the NCO module- this has not been explored yet.
##### Overview:
-Process accumulated flux & state differences
-Rename "depth" column to "bucket_depth"
-Process sums and means
-Process flow totals
-Process depth average
-Cleanup names

## LDASIN:
#### nco_process_clim.sh
##### Script Preparations:
You will need to specify two paths: 
  - The location of the hourly CONUS404-BA output LDASIN files.
  - The location of where to save the monthly outputs.
*Note: this script has some additional lines of code to deal with this data being organized by Water Year.
##### Overview:
-Create totals and averages
-Cleanup names

## CHRTOUT:
#### nco_process_chrtout.sh
##### Script Preparations:
You will need to specify two paths: 
  - The location of the hourly WRF-Hydro output CHRTOUT files.
  - The location of where to save the monthly outputs.
##### Overview:
-Create totals and averages
-Clean names

## One Year at a Time: 

Load netcdf operator
```
module load nco
```
Ensure paths in shell script are correct. 

Allow edit permission for the shell script, the shell files should be green after running this:
```
chmod +x /path/to/yourscript.sh
```
Run the shell script. 
```
./nco_process_ldasout.sh 2009
```
Repeat for other variables. 

## Multiple Years at Once: 

Ensure paths in shell scripts and slurm files are correct.  

Allow edit permission for the shell script:
```
chmod +x /path/to/yourscript.sh
```
Launch slurm script with an array of years of interest, 2011-2013 is used here. Adjust name of slurm file based on which WRF-Hydro output is being processed. 
```
sbatch --array=2011-2013 ldasout_nco.slurm
```
To check on the status of slurm request and find job id:
```
squeue -u <username>
```
If you need to cancel the request: 
```
scancel <jobid>
```
Repeat for other variables.

## Results
The following metrics will be generated with these scripts: 
<table>
  <tr>
    <th>Source</th>
    <th>File</th>
    <th>Variable</th>
    <th>Name</th>
    <th>Description</th>
    <th>Units</th>
  </tr>
  <tr>
    <td rowspan="19"><a href="#WRF-Hydro"><b>WRF-Hydro</b></a></td>
    <td rowspan="12">LDASOUT</td>
    <td>deltaACCET</td>
    <td>ET change</td>
    <td>Total monthly evapotranspiration (land only)</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>deltaACSNOW</td>
    <td>Snowfall change</td>
    <td>Total monthly snowfall (land only)</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>deltaSNEQV</td>
    <td>SWE change</td>
    <td>Average monthly snow water equivalent (land only)</td>
    <td>mm</td>    
  </tr>
  <tr>
    <td>deltaSOILM</td>
    <td>Soil Water change</td>
    <td>Average monthly soil moisture in 2m soil column (land only)</td>
    <td>mm</td>      
  </tr>
  <tr>
    <td>deltaUGDRNOFF</td>
    <td>Recharge change</td>
    <td>Total monthly recharge (land only)</td>
    <td>mm</td>   
  </tr>
  <tr>
    <td>deltaSOILM_depthmean</td>
    <td>---</td>
    <td>Change in depth-mean volumetric soil moisture, ratio of water volume to soil volume (month end minus month start) </td>
    <td>---</td>    
  </tr>
  <tr>
    <td>avgSNEQV</td>
    <td>SWE average</td>
    <td>Mean snow water equivalent </td>
    <td>mm</td>  
  </tr>
  <tr>
    <td>avgSOILM</td>
    <td>Soil Water average</td>
    <td>Mean volumetric soil moisture by layer </td>
    <td>m3/m3</td>   
  </tr>
  <tr>
    <td>avgSOILM_depthmean</td>
    <td>---</td>
    <td>Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) over month </td>
    <td>---</td>
  </tr>
  <tr>
    <td>avgSOILM_wltadj_depthmean</td>
    <td>---</td>  
    <td>Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) minus wilting point over month </td>
    <td>---</td>  
  </tr>
  <tr>
    <td>avgSOILSAT</td>
    <td>Soil Saturation average</td>
    <td>Average monthly fractional soil saturation in 2m soil column (land only) </td>
    <td>---</td> 
  </tr>
  <tr>
    <td>avgSOILSAT_wltadj_top1</td>
    <td>---</td> 
    <td>Average fractional soil saturation above wilting point (soil moisture minus wilting point divided by maximum water content minus wilting point) over top layer (top 10cm) over month</td>
    <td>---</td>     
  </tr>
  <tr>
    <td rowspan="4">GWOUT</td>
    <td>totOutflow</td>
    <td>Total outflow volume over month</td>
    <td>---</td>
    <td>m3</td>
  </tr>
  <tr>
    <td>totInflow</td>
    <td>Total inflow volume over month</td>
    <td>---</td>
    <td>m3</td>
  </tr>
  <tr>
    <td>deltaDepth</td>
    <td>Change in baseflow bucket storage (month end minus month start)</td>
    <td>---</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>bucket_depth</td>
    <td>Ground Water Store</td>
    <td>Average monthly groundwater storage</td>
    <td>mm</td>
  </tr>
  <tr>
    <td rowspan="3">CHRTOUT</td>
    <td>totqBucket</td>
    <td>Baseflow</td>
    <td>Total monthly baseflow</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>totqSfcLatRunoff</td>
    <td>Surfaceflow</td>
    <td>Total monthly surface flow</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>totStreamflow</td>
    <td>---</td>
    <td>Total streamflow volume over month</td>
    <td>m3</td>
  </tr>
  <tr>
    <td rowspan="2"><a href="#CONUS404-BA"><b>CONUS404-BA</b></a></td>
    <td rowspan="2">LDASIN</td>
    <td>totPRECIP</td>
    <td>Precipitation</td>
    <td>Total monthly precipitation</td>
    <td>mm</td>
  </tr>
    <td>avgT2D</td>
    <td>Temperature</td>
    <td>Average 2-m air temperature</td>  
    <td>K</td>  
  </tr>
</table>



