# NWM Variables of Interest

Of the variables listed in <https://ral.ucar.edu/sites/default/files/public/WRFHydroV5_OutputVariableMatrix_V5.pdf>,
the following are selected for evaluation:

| Variable | Domain  | Description |
| -----    | --------| ----- |
| ACCET    | LDASOUT | Accumulated total evapotranspiration |
| SNEQV    | LDASOUT | Snow water equivalent |
| FSNO     | LDASOUT | Fraction of surface covered by snow |
| ACCPRCP  | LDASOUT | Accumulated precipitation
| SOIL_M   | LDASOUT | Volumetric soil moisture
| CANWAT   | LDASOUT | Total canopy water (liquid + ice)
| CANICE   | LDASOUT | Canopy ice water content
| depth    | GWOUT   | Groundwater bucket water level
| sfcheadrt| RTOUT   | Surface head (from HYDRO)
| SFCRNOFF | LDASOUT | Surface runoff: accumulated
| UGDRNOFF | LDASOUT | Underground runoff: accumulated

The source data is accessed via the AWS Open Data registry.
See <https://registry.opendata.aws/nwm-archive/>

Datasets are available as netcdf or zarr file format via S3 buckets.
We prefer the zarr, so will prioritize reading data from
<https://noaa-nwm-retrospective-2-1-zarr-pds.s3.amazonaws.com/index.html>.
This data also has the advantage of already being aggregated/assembled into
complete time series.

:::{sidebar}
To read the underlying netcdf files, go here instead:
<https://noaa-nwm-retrospective-2-1-pds.s3.amazonaws.com/index.html#model_output/>
:::