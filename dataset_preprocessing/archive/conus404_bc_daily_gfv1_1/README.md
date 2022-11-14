This archive contains the scripts used to process conus404 bias-corrected daily zarr data to the NHGF geospatial-fabric v1.1

This data was processed using jupyter notebooks on tallgrass

The c404bc data are located here: /caldera/hytest_scratch/scratch/conus404/conus404_daily_bc.zarr

The processed data are located here /caldera/projects/usgs/water/wbeep/onhm_dev/climate/c404bc
NOTE paths in the notebooks would need to be adjusted to the locations noted below.

Including:
environment-dev.yml - conda/mamba file for creating working python environment
The fabric data - gfv1.1_simple.shp
c404bc by calendar year, for example 1980_gfv11_c404_daily_bc.nc

notebooks:
c404_calc_wghts.ipynb: used to generate weights for area-weighted statists
run_weghts_c404bc.ipynb: given weights calculated above, process area-weighted average values of gridded c404 bias corrected daily data to hru polygons


