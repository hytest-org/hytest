# HyTEST Data Catalog (Intake)
This section describes how to use HyTEST's [intake catalog](https://intake.readthedocs.io/en/latest/catalog.html). Intake catalogs help reduce or remove the burden of handling different file formats and storage locations, making it easier to read data into your workflow. They also allow data providers to update the filepath/storage location of a dataset without breaking the workflows that were built on top of the intake catalog.

Our catalog facilitates this access for HyTEST's key data offerings and is used to read the data into the notebooks contained in this repository. While intake catalogs are Python-centric, they stored as a yaml file, which should also be easy to parse using other programming languages, even if there is no equivalent package in that programming language. Example usage of this catalog is shown below.

Please note that this catalog is a temporary solution for reading data into our workflows. By the end of 2023, we hope to replace this catalog by a [STAC](https://stacspec.org/en). We plan to update all notebooks to read from our STAC at that time, as well.

```python
import intake
url = 'https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/hytest_intake_catalog.yml'
cat = intake.open_catalog(url)
list(cat)
```
produces a list of datasets, for example:
```
['conus404-drb-eval-tutorial-catalog',
 'nhm-v1.0-daymet-catalog',
 'nhm-v1.1-c404-bc-catalog',
 'nhm-v1.1-gridmet-catalog',
 'conus404-catalog',
 'nwis-streamflow-usgs-gages-onprem',
 'nwis-streamflow-usgs-gages-cloud',
 'nwm21-streamflow-usgs-gages-onprem',
 'nwm21-streamflow-usgs-gages-cloud',
 'nwm21-streamflow-cloud',
 'nwm21-scores',
 'lcmap-cloud',
 'rechunking-tutorial-cloud']
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
 
Once you have identified the dataset you would like to work with, xarray-type datasets can be loaded with `to_dask()`, while panda-type datasets can be loaded with `.read()`:
```python
ds = cat['lcmap-cloud'].to_dask()
df = cat['nwm21-scores'].read()
```

## Demos
Demos for working with the data catalogs can be found in the [demos](https://github.com/hytest-org/hytest/tree/main/dataset_catalog/demos) folder of our repository.

## Subcatalogs
The main HyTEST intake catalog includes the use of sub-catalogs. A sub-catalog may contain a set of datasets for a particular use case (like a specific tutorial) or groupings of related datasets. For example, the CONUS404 datasets (at different time steps and storage locations) are stored in their own sub-catalog. An example of calling these catalogs in can be found [here](./subcatalogs/README.md). 

