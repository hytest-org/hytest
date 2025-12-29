# WRF-Hydro Products Data Access

This section of our JupyterBook contains notebooks that demonstrate how to access the [WRF-Hydro dataset](https://doi.org/10.5066/P13ADWKZ). This dataset contains inputs for and outputs from a hydrologic simulation for the conterminous United States (CONUS) using the WRF-Hydro modeling system. This simulation was developed to provide water budget estimates for the period 10/1/1979 to 9/30/2022 using the bias adjusted version of the CONUS404 (CONUS404BA) atmospheric forcings dataset. Users should start by reviewing the official [WRF-Hydro data release](https://doi.org/10.5066/P13ADWKZ) to understand the file structure and appropriate usage before trying to access the data.

We have provided [one short notebook](./wrfhydro_explore.ipynb) to aid in accessing the data. This notebook opens up a subset of the model output from this release and plots a time series of streamflow data. This is just a start to working with the data, and users will need to adapt the notebook to their own data processing needs.

As you build upon this base access notebook, you may want to reference some of the data processing notebooks we built for the [CONUS404 dataset](https://hytest-org.github.io/hytest/dataset_access/CONUS404_ACCESS.html) which demonstrate a variety of data processing methods:

- [Explore CONUS404 Dataset](https://hytest-org.github.io/hytest/dataset_access/conus404_explore.html): opens the CONUS404 dataset, loads and plots the entire spatial domain of a specified variable at a specfic time step, and loads and plots a time series of a variable at a specified coordinate pair.
- [CONUS404 Temporal Aggregation](https://hytest-org.github.io/hytest/dataset_processing/tutorials/conus404_temporal_aggregation.html): calculates a daily average of the CONUS404 hourly data.
- [CONUS404 Spatial Aggregation](https://hytest-org.github.io/hytest/dataset_processing/spatial_aggregation.html): calculates the area-weighted mean of the CONUS404 data for a particular basin (several methods are demoed in this section)
- [CONUS404 Point Selection](https://hytest-org.github.io/hytest/dataset_processing/tutorials/conus404_point_selection.html): samples the CONUS404 data at a selection of gage locations using their lat/lon point coordinates.
- [CONUS404 Regridding (Curvilinear => Rectilinear)](https://hytest-org.github.io/hytest/dataset_processing/tutorials/conus404_regrid.html): regrids a subset of the CONUS404 dataset from a curvilinear grid to a rectilinear grid and saves the output to a netcdf file. The package used in this demo is not compatible with Windows. We hope to improve upon this methodology, and will likely update the package/technique used in the future.

*Note: If you need help setting up a computing environment where you can run these notebooks, you should review the [Computing Environments](https://hytest-org.github.io/hytest/environment_set_up/README.html) section of the documentation.*
