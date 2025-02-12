# CONUS404 Products Data Access

*Before working with the CONUS404 data, you may want to consider reviewing [NCAR's Climate Primer for Water Availability Assessments](https://ncar.github.io/climate-primer-water/index.html) to learn more about how to apply this dataset in studies focused on water availability.*

This section of our JupyterBook contains notebooks that demonstrate how to access and perform basic data manipulation for the [CONUS404 dataset](https://doi.org/10.5066/P9PHPK4F). The examples can also be applied to the [CONUS404 bias-adjusted dataset](https://doi.org/10.5066/P9JE61P7) and the [CONUS404 psuedo global warming (PGW) dataset](https://doi.org/10.5066/P9HH85UU). 

In the CONUS404 intake sub-catalog (see [here](../dataset_catalog/README.md) for an explainer of our intake data catalog), you will see entries for:
- four CONUS404 datasets: `conus404-hourly`, `conus404-daily`, `conus404-monthly`, and `conus404-daily-diagnostic` data
- two CONUS404 bias-adjusted datasets: `conus404-hourly-ba`, `conus404-daily-ba`
- two CONUS404 PGW datasets: `conus404-pgw-hourly` and `conus404-pgw-daily-diagnostic`

Each of these datasets is duplicated in up to three different storage locations (as the [intake catalog section](../dataset_catalog/README.md) also describes).

**We recommend that you regularly check our [CONUS404 changelog](./CONUS404_CHANGELOG) to see any updates that have been made to the zarr stores.** We do not anticipate regular changes to the dataset, but we may need to fix an occasional bug or update the dataset with additional years of data.

## CONUS404 Data
CONUS404 is a unique, high-resolution hydro-climate dataset appropriate for forcing hydrological models and conducting meteorological analysis over the contiguous United States. Users should review the official [CONUS404 data release](https://doi.org/10.5066/P9PHPK4F) to understand the dataset before working with the zarr stores provided in our intake catalog.

The `conus404-hourly` data is a subset of the wrfout model output and `conus404-daily-diagnostic` is a subset from the wrfxtrm model output, both of which are described in the official data release. We also provide `conus404-daily` and `conus404-monthly` files, which are just resampled from the `conus404-hourly` data.

**Please note that the values in the ACLWDNB, ACLWUPB, ACSWDNB, ACSWDNT, and ACSWUPB variables available in the zarr store differ from the original model output.** These variables have been re-calculated to reflect the accumulated value since the model start, as directed in the WRF manual. An attribute has been added to each of these variables in the zarr store to denote the accumulation period for the variable. 

**We recommend that you regularly check our [CONUS404 changelog](./CONUS404_CHANGELOG) to see any updates that have been made to the zarr stores.** We do not anticipate regular changes to the dataset, but we may need to fix an occasional bug or update the dataset with additional years of data.

## CONUS404 Bias-Adjusted Data
The `conus404-hourly-ba` data contains bias-adjusted temperature and precipiation data from the CONUS404 dataset, which is described in the official [CONUS404 bias adjusted data release](https://doi.org/10.5066/P9JE61P7). Users should review the official data release to understand the dataset before working with the zarr stores provided in our intake catalog.

The `conus404-daily-ba` files are resampled from the `conus404-hourly-ba` data.

## CONUS404 PGW Data
The CONUS404 pseudo-global warming (PGW) dataset is a future-perturbed hydro-climate dataset, created as a follow on to the CONUS404 dataset. The CONUS404 PGW dataset represents the weather from 1980 to 2021 under a warmer and wetter climate environment and provides an opportunity to explore the event-based climate change impacts when used with the CONUS404 historical data. Users should review the official [CONUS404 PGW data release](https://doi.org/10.5066/10.5066/P9HH85UU) to understand the dataset before working with the zarr stores provided in our intake catalog.

The `conus404-pgw-hourly` data is a subset of the wrfout model output and `conus404-pgw-daily-diagnostic` is a subset from the wrfxtrm model output, both of which are described in the official data release.

**Please note that the values in the ACLWDNB, ACLWUPB, ACSWDNB, ACSWDNT, and ACSWUPB variables available in the zarr store differ from the original model output.** These variables have been re-calculated to reflect the accumulated value since the model start, as directed in the WRF manual. An attribute has been added to each of these variables in the zarr store to denote the accumulation period for the variable. 

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
