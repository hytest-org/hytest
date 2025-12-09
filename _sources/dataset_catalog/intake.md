# HyTEST Data Catalog (Intake)
This section describes how to use HyTEST's [intake catalog](https://intake.readthedocs.io/en/latest/catalog.html). Intake catalogs help reduce or remove the burden of handling different file formats and storage locations, making it easier to read data into your workflow. They also allow data providers to update the filepath/storage location of a dataset without breaking the workflows that were built on top of the intake catalog.

Our catalog facilitates this access for HyTEST's key data offerings and is used to read the data into the notebooks contained in this repository. While intake catalogs are Python-centric, they are stored as a yaml file, which should also be easy to parse using other programming languages, even if there is no equivalent package in that programming language.

Please note that we are trying to move towards using the [USGS Water Mission Area STAC Catalog](STAC.ipynb) to catalog our data holdings. This transition may take time, and we may end up using a combination of the STAC Catalog and our HyTEST intake catalog, but we encourage users to prioritize reading data from STAC when possible, as we plan to move in that direction.

## Example Intake Catalog Usage
Now that you have an understanding of the [different storage systems HyTEST uses](./storage_locations.md), you will be able to navigate the HyTEST intake catalog and make a selection that is appropriate for your computing environment. Below is a demonstration of how to use HyTEST's intake catalog to select and open a dataset in your python workflow.

```python
import intake
url = 'https://raw.githubusercontent.com/hytest-org/hytest/main/dataset_catalog/hytest_intake_catalog.yml'
cat = intake.open_catalog(url)
list(cat)
```
produces a list of datasets, for example:
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

## Subcatalogs
The main HyTEST intake catalog includes the use of sub-catalogs. A sub-catalog may contain a set of datasets for a particular use case (like a specific tutorial) or groupings of related datasets. For example, the CONUS404 datasets (at different time steps and storage locations) are stored in their own sub-catalog. An example of calling these catalogs in can be found [here](./subcatalogs/README.md).

## Demos
You will see use of the intake catalog in many of the example workflows in the JupyterBook. Additional demos for working with the data catalogs can be found in the [demos](https://github.com/hytest-org/hytest/tree/main/dataset_catalog/demos) folder of our repository. These are not as fully documented as the tutorials found in this JupyterBook.