# CONUS404 Access


The contents of this folder contain notebooks that demonstrate how to access and perform 
basic data manipulation (subset, aggreation) for key HyTEST datasets. Currently, all 
notebooks are focused on the CONUS404 dataset, but notebooks focused on other datasets may 
be added in the future. Descriptions of the what each of the current notebooks demonstrate 
are provided below:


- `conus404_explore.ipynb`: opens the CONUS404 dataset, loads and plots the entire spatial 
   domain of a specified variable at a specfic time step, and loads and plots a time series 
   of a variable at a specified coordinate pair
- `conus404_regrid.ipynb`: regrids a subset of the CONUS404 dataset from a curvilinear 
   grid to a rectilinear grid and saves the output to a netcdf file
- `conus404_spatial_aggregation.ipynb`: calculates the area-weighted mean of a specified 
   CONUS404 variable for all HUC12s in the Delaware River Basin
- `conus404_temporal_aggregation.ipynb`: calculates a daily average of the CONUS404 hourly data

