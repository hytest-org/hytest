 # USGS Water Mission Area STAC Catalog

By the end of 2025, we hope to replace the HyTEST intake catalog by a [STAC](https://stacspec.org/en) catalog.

The USGS Water Mission Area (WMA) has built out its own STAC Catalog, surfaced through a [pygeoapi](https://pygeoapi.io/) endpoint [here](https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection). The WMA STAC catalog contains a selection of key hydro-terrestrial modeling datasets that were converted to analysis-ready cloud-optimized formats to improve their usability. These datasets are freely and publicly accessible through an Open Storage Network (OSN) Pod, described in the [previous section](./README.md). After identifying the dataset you want to use from the STAC catalog, you can read it into your workflow using the S3 API endpoint listed on the dataset landing page with a code snippet like the following:

```python
import fsspec
import xarray as xr

zarr_url = 's3://mdmf/gdp/LOCA_historical.zarr/'

fs = fsspec.filesystem('s3', anon=True, endpoint_url='https://usgs.osn.mghpcc.org/')

ds = xr.open_dataset(fs.get_mapper(zarr_url), engine='zarr', 
                             backend_kwargs={'consolidated':True}, chunks={})
ds
```