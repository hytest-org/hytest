# hytest-catalogs
This directory holds subcatalogs called in by the `hytest_intake_catalog.yml`. These catalogs are structured to be compatible with the Python intake package and facilitate reading the data into the other notebooks contained in this repository. The intake catalog is stored as a yaml file, which should also be easy to parse using other programming languages, even if there is no equivalent to the intake package in that programming language. Example usage of this catalog is shown below.

```python
import intake
url = 'https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/subcatalogs/conus404_catalog.yml'
cat = intake.open_catalog(url)
list(cat)
```
produces a list of datasets, for example:
```
['conus404-hourly-onprem',
 'conus404-hourly-cloud',
 'conus404-daily-diagnostic-onprem',
 'conus404-daily-diagnostic-cloud',
 'conus404-daily-onprem',
 'conus404-daily-cloud',
 'conus404-monthly-onprem',
 'conus404-monthly-cloud']
 ```
 The characteristics of indivdual datasets can be explored:
```python
cat['conus404-hourly-cloud']
```
producing
```yaml
conus404-hourly-cloud:
  args:
    consolidated: true
    storage_options:
      requester_pays: true
    urlpath: s3://nhgf-development/conus404/conus404_hourly_202209.zarr
  description: 'CONUS404 Hydro Variable subset, 40 years of hourly values. These files
    were created wrfout model output files (see ScienceBase data release for more
    details: https://www.sciencebase.gov/catalog/item/6372cd09d34ed907bf6c6ab1). This
    dataset is stored on AWS S3 cloud storage in a requester-pays bucket. You can
    work with this data for free if your workflow is running in the us-west-2 region,
    but you will be charged according to AWS S3 pricing (https://aws.amazon.com/s3/pricing/)
    to read the data into a workflow running outside of the cloud or in a different
    AWS cloud region.'
  driver: intake_xarray.xzarr.ZarrSource
  metadata:
    catalog_dir: https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/subcatalogs
```
 and xarray-type datasets can be loaded with `to_dask()`:
```python
ds = cat['conus404-hourly-cloud'].to_dask()
```

### Demos
Demos for working with the data catalogs can be found in the [demos](https://github.com/hytest-org/hytest/tree/main/dataset_catalog/demos) folder.