# CONUS404 Access

This section contains notebooks that demonstrate how to access and perform basic data manipulation for the CONUS404 dataset. These methods are likely applicable to many of the other key HyTEST datasets that can be opened with xarray. If you need help setting up a computing environment where you can run these notebooks, you should review the [Computing Environments](../environment_set_up/README.md) section of the documentation.

We currently have four demonstrations:

- [Explore CONUS404 Dataset](./conus404_explore.ipynb): opens the CONUS404 dataset, loads and plots the entire spatial 
   domain of a specified variable at a specfic time step, and loads and plots a time series of a variable at a specified coordinate pair.
- [CONUS404 Temporal Aggregation](./conus404_temporal_aggregation.ipynb): calculates a daily average of the CONUS404 hourly data.
- [CONUS404 Spatial Aggregation](./conus404_spatial_aggregation.ipynb): calculates the area-weighted mean of a specified 
   CONUS404 variable for all HUC12s in the Delaware River Basin.
- [CONUS404 Regridding (Curvilinear => Rectilinear)](./conus404_regrid.ipynb): regrids a subset of the CONUS404 dataset from a curvilinear grid to a rectilinear grid and saves the output to a netcdf file. The package used in this demo is not compatible with Windows. We hope to improve upon this methodology, and will likely update the package/technique used in the future.
