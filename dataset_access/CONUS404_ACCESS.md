# CONUS404 and CONUS404 Bias-Adjusted Data Access

This section contains notebooks that demonstrate how to access and perform basic data manipulation for the [CONUS404 dataset](https://doi.org/10.5066/P9PHPK4F). The examples can also be applied to the [CONUS404 bias-adjusted dataset](https://doi.org/10.5066/P9JE61P7).

In the CONUS404 intake sub-catalog (see [here](../dataset_catalog/README.md) for an explainer of our intake data catalog), you will see entries for four CONUS404 datasets: `conus404-hourly`, `conus404-daily`, `conus404-monthly`, and `conus404-daily-diagnostic` data, as well as two CONUS404 bias-adjusted datasets: `conus404-hourly-ba`, `conus404-daily-ba`. Each of these datasets is duplicated in up to three different storage locations (as the [intake catalog section](../dataset_catalog/README.md) also describes).

## CONUS404 Data
The `conus404-hourly` data is a subset of the `wrfout` model output. For instantaneous variables, the data value at each time step represents the instantaneous value at the timestep. For accumulated variables, the data value represents the accumulated value up to the timestep (see the `integration_length` attribute attached to each accumulated variable for more details on the accumulation period).

The `conus404-daily-diagnostic` data is a subset from the `wrfxtrm` model output. These data represent the results of the past 24 hours, with the timestamp corresponding to the end time of the 24 hour period. Because the CONUS404 started at 1979-10-01_00:00:00, the first timestep (1979-10-01_00:00:00) for each variable is all zeros. 
 
Both of these datasets are described in the official [CONUS404 data release](https://doi.org/10.5066/P9PHPK4F).

We also have `conus404-daily` and `conus404-monthly` files, which are just resampled from the `conus404-hourly` data. To create the `conus404-daily` zarr, instantaneous variables are aggregated from 00:00:00 UTC to 11:00:00 UTC, while accumulated variables are aggregated from 01:00:00 UTC to 12:00:00 UTC of the next day.

**Please note that the values in the ACLWDNB, ACLWUPB, ACSWDNB, ACSWDNT, and ACSWUPB variables available in the zarr store differ from the original model output.** These variables have been re-calculated to reflect the accumulated value since the model start, as directed in the WRF manual. An attribute has been added to each of these variables in the zarr store to denote the accumulation period for the variable. 

**We recommend that you regularly check our [CONUS404 changelog](./CONUS404_CHANGELOG) to see any updates that have been made to the zarr stores.** We do not anticipate regular changes to the dataset, but we may need to fix an occasional bug or update the dataset with additional years of data.

## CONUS404 Bias-Adjusted Data
The `conus404-hourly-ba` data contains bias-adjusted temperature and precipiation data from the CONUS404 dataset, which is described in the official [CONUS404 bias adjusted data release](https://doi.org/10.5066/P9JE61P7). The `conus404-daily-ba` files are resampled from the `conus404-hourly-ba` data.

## Example Notebooks
We currently have five notebooks to help demonstrate how to work with these datasets in a python workflow:
- [Explore CONUS404 Dataset](./conus404_explore.ipynb): opens the CONUS404 dataset, loads and plots the entire spatial 
   domain of a specified variable at a specfic time step, and loads and plots a time series of a variable at a specified coordinate pair.
- [CONUS404 Temporal Aggregation](./conus404_temporal_aggregation.ipynb): calculates a daily average of the CONUS404 hourly data.
- [CONUS404 Spatial Aggregation](./conus404_spatial_aggregation.ipynb): calculates the area-weighted mean of the CONUS404 data for all HUC12s in the Delaware River Basin.
- [CONUS404 Point Selection](./conus404_point_selection.ipynb): samples the CONUS404 data at a selection of gage locations using their lat/lon point coordinates.
- [CONUS404 Regridding (Curvilinear => Rectilinear)](./conus404_regrid.ipynb): regrids a subset of the CONUS404 dataset from a curvilinear grid to a rectilinear grid and saves the output to a netcdf file. The package used in this demo is not compatible with Windows. We hope to improve upon this methodology, and will likely update the package/technique used in the future.

These methods are likely applicable to many of the other key HyTEST datasets that can be opened with xarray.

*Note: If you need help setting up a computing environment where you can run these notebooks, you should review the [Computing Environments](../environment_set_up/README.md) section of the documentation.*