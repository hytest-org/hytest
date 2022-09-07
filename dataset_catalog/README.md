# hytest-catalogs
This directory holds the `hytest_intake_catalog.yml`. This catalog is structured to be compatible with the Python intake package and facilitates reading the data into the other notebooks contained in this repository. Example usage of this catalog is shown below.

Please note that this catalog is a temporary solution for reading data into our workflows. By the end of 2022, we hope to replace this catalog by a [STAC](https://stacspec.org/en). We plan to update all notebooks to read from our STAC at that time, as well.

```python
import intake
url = 'https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/hytest_intake_catalog.yml'
cat = intake.open_catalog(url)
list(cat)
```
produces a list of datasets, for example:
```
['conus404-40year-onprem',
 'conus404-2017-onprem',
 'conus404-2017-cloud',
 'nwis-streamflow-usgs-gages-onprem',
 'nwis-streamflow-usgs-gages-cloud',
 'nwm21-streamflow-usgs-gages-onprem',
 'nwm21-streamflow-usgs-gages-cloud',
 'nwm21-streamflow-cloud',
 'nwm21-scores',
 'lcmap-cloud']
 ```
 The characteristics of indivdual datasets can be explored:
```python
cat['lcmap-cloud']
```
producing
```yaml
lcmap-cloud:
  args:
    consolidated: false
    storage_options:
      fo: s3://nhgf-development/lcmap/lcmap.json
      remote_options:
        requester_pays: true
      remote_protocol: s3
      target_options:
        requester_pays: true
    urlpath: reference://
  description: LCMAP, all 36 years
  driver: intake_xarray.xzarr.ZarrSource
  metadata:
    catalog_dir: https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog
 ```
 and xarray-type datasets can be loaded with `to_dask()`, while panda-type datasets can be loaded with `.read()`:
```python
ds = cat['lcmap-cloud'].to_dask()
df = cat['nwm21-scores'].read()
```