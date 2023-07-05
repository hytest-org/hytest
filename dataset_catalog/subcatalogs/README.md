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
 'nwis-streamflow-usgs-gages-onprem',
 'nwis-streamflow-usgs-gages-cloud',
 'nwm21-streamflow-usgs-gages-onprem',
 'nwm21-streamflow-usgs-gages-cloud',
 'nwm21-streamflow-cloud',
 'nwm21-scores',
 'lcmap-cloud',
 'rechunking-tutorial-cloud']

```
We can then open the CONUS404 sub-catalog with:
```python
cat = hytest_cat['conus404-catalog']
list(cat)
```
producing a list of all the CONUS404 dataset versions:
```
['conus404-hourly-onprem',
 'conus404-hourly-cloud',
 'conus404-hourly-osn',
 'conus404-daily-diagnostic-onprem',
 'conus404-daily-diagnostic-cloud',
 'conus404-daily-diagnostic-osn',
 'conus404-daily-onprem',
 'conus404-daily-cloud',
 'conus404-daily-osn',
 'conus404-monthly-onprem',
 'conus404-monthly-cloud',
 'conus404-monthly-osn']
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
        endpoint_url: https://renc.osn.xsede.org
      requester_pays: false
    urlpath: s3://rsignellbucket2/hytest/conus404/conus404_hourly_202302.zarr
  description: 'CONUS404 Hydro Variable subset, 40 years of hourly values. These files
    were created wrfout model output files (see ScienceBase data release for more
    details: https://www.sciencebase.gov/catalog/item/6372cd09d34ed907bf6c6ab1). This
    dataset is stored on AWS S3 cloud storage in a requester-pays bucket. You can
    work with this data for free in any environment (there are no egress fees).'
  driver: intake_xarray.xzarr.ZarrSource
  metadata:
    catalog_dir: https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/subcatalogs
```
