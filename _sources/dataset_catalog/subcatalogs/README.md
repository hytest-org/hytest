# HyTEST Intake Sub-Catalogs
This section describes how to use the subcatalogs contained in HyTEST's main data catalog (`hytest_intake_catalog.yml`). Example usage of the CONUS404 sub-catalog is shown below.

```python
import intake
hytest_cat = intake.open_catalog("https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/hytest_intake_catalog.yml")
list(hytest_cat)
```

produces a list of datasets and sub-catalogs in the main HyTEST data catalog, for example:
```
['conus404-catalog',
 'conus404-drb-eval-tutorial-catalog',
 'nhm-v1.0-daymet-catalog',
 'nhm-v1.1-c404-bc-catalog',
 'nhm-v1.1-gridmet-catalog',
 'trends-and-drivers-catalog',
 'nhm-prms-v1.1-gridmet-format-testing-catalog',
 'nwis-streamflow-usgs-gages-onprem',
 'nwis-streamflow-usgs-gages-osn',
 'nwm21-streamflow-usgs-gages-onprem',
 'nwm21-streamflow-usgs-gages-osn',
 'nwm21-streamflow-cloud',
 'geofabric_v1_1-zip-osn',
 'geofabric_v1_1_POIs_v1_1-osn',
 'geofabric_v1_1_TBtoGFv1_POIs-osn',
 'geofabric_v1_1_nhru_v1_1-osn',
 'geofabric_v1_1_nhru_v1_1_simp-osn',
 'geofabric_v1_1_nsegment_v1_1-osn',
 'gages2_nndar-osn',
 'wbd-zip-osn',
 'huc12-geoparquet-osn',
 'huc12-gpkg-osn',
 'nwm21-scores',
 'lcmap-cloud',
 'rechunking-tutorial-osn',
 'pointsample-tutorial-sites-osn',
 'pointsample-tutorial-output-osn']

```
We can then open the CONUS404 sub-catalog with:
```python
cat = hytest_cat['conus404-catalog']
list(cat)
```
producing a list of all the CONUS404 dataset versions:
```
['conus404-hourly-onprem-hw',
 'conus404-hourly-cloud',
 'conus404-hourly-osn',
 'conus404-daily-diagnostic-onprem-hw',
 'conus404-daily-diagnostic-cloud',
 'conus404-daily-diagnostic-osn',
 'conus404-daily-onprem-hw',
 'conus404-daily-cloud',
 'conus404-daily-osn',
 'conus404-monthly-onprem-hw',
 'conus404-monthly-cloud',
 'conus404-monthly-osn',
 'conus404-hourly-ba-onprem-hw',
 'conus404-hourly-ba-osn',
 'conus404-daily-ba-onprem',
 'conus404-daily-ba-osn',
 'conus404-pgw-hourly-onprem-hw',
 'conus404-pgw-hourly-osn',
 'conus404-pgw-daily-diagnostic-onprem-hw',
 'conus404-pgw-daily-diagnostic-osn']
```

The characteristics of indivdual datasets can be explored:
```python
cat['conus404-hourly-osn']
```
producing
```yaml
conus404-hourly-osn:
  args:
    consolidated: true
    storage_options:
      anon: true
      client_kwargs:
        endpoint_url: https://usgs.osn.mghpcc.org/
      requester_pays: false
    urlpath: s3://hytest/conus404/conus404_hourly.zarr
  description: "CONUS404 Hydro Variable subset, 43 years of hourly values. These files\
    \ were created wrfout model output files (see ScienceBase data release for more\
    \ details: https://doi.org/10.5066/P9PHPK4F). This data is stored on HyTEST\u2019\
    s Open Storage Network (OSN) pod. This data can be read with the S3 API and is\
    \ free to work with in any computing environment (there are no egress fees)."
  driver: intake_xarray.xzarr.ZarrSource
  metadata:
    catalog_dir: https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/subcatalogs
```
