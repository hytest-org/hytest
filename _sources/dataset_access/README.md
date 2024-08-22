# CONUS404 Access

This section contains notebooks that demonstrate how to access and perform basic data manipulation for the [CONUS404 dataset](https://doi.org/10.5066/P9PHPK4F). 

In the CONUS404 intake sub-catalog (see [here](../dataset_catalog/README.md) for an explainer of our intake data catalog), you will see entries for four CONUS404 datasets: conus404-hourly, conus404-daily, conus404-monthly, and conus404-daily-diagnostic data. Each of these datasets is duplicated in three different storage locations (as the [intake catalog section](../dataset_catalog/README.md) also describes). The conus404-hourly data is a subset of the wrfout model output and conus404-daily-diagnostic is a subset from the wrfxtrm model output, both of which are described in the official [CONUS404 data release](https://doi.org/10.5066/P9PHPK4F). We also have conus404-daily and conus404-monthly files, which are just resampled from the conus404-hourly data.

**Please note that the values in the ACLWDNB, ACLWUPB, ACSWDNB, ACSWDNT, and ACSWUPB variables available in the zarr store differ from the original model output.** These variables have been re-calculated to reflect the accumulated value since the model start, as directed in the WRF manual. An attribute has been added to each of these variables in the zarr store to denote the accumulation period for the variable. 

We currently have five notebooks to help demonstrate how to work with these datasets in a python workflow:
- [Explore CONUS404 Dataset](./conus404_explore.ipynb): opens the CONUS404 dataset, loads and plots the entire spatial 
   domain of a specified variable at a specfic time step, and loads and plots a time series of a variable at a specified coordinate pair.
- [CONUS404 Temporal Aggregation](./conus404_temporal_aggregation.ipynb): calculates a daily average of the CONUS404 hourly data.
- [CONUS404 Spatial Aggregation](./conus404_spatial_aggregation.ipynb): calculates the area-weighted mean of the CONUS404 data for all HUC12s in the Delaware River Basin.
- [CONUS404 Point Selection](./conus404_point_selection.ipynb): samples the CONUS404 data at a selection of gage locations using their lat/lon point coordinates.
- [CONUS404 Regridding (Curvilinear => Rectilinear)](./conus404_regrid.ipynb): regrids a subset of the CONUS404 dataset from a curvilinear grid to a rectilinear grid and saves the output to a netcdf file. The package used in this demo is not compatible with Windows. We hope to improve upon this methodology, and will likely update the package/technique used in the future.

These methods are likely applicable to many of the other key HyTEST datasets that can be opened with xarray.

*Note: If you need help setting up a computing environment where you can run these notebooks, you should review the [Computing Environments](../environment_set_up/README.md) section of the documentation.*