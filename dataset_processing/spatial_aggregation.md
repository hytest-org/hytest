# Spatial Aggregation

Spatial aggregation of a gridded dataset to a polygon area is a common processing method in the geospatial world, and there are a variety of packages and methods that can be used to perform this task. Our team has tested two methods: one using the python package [gdptools](https://gdptools.readthedocs.io/en/develop/index.html#), and the other using conservative regional methods with xarray and geopandas natively, as described in [this Pangeo Discourse](https://discourse.pangeo.io/t/conservative-region-aggregation-with-xarray-geopandas-and-sparse/2715).

We developed both of these methods over the Delaware River Basin to test how their speed and accuracy would compare. You can see notebooks demonstrating each method over this spatially subsetted area in the following notebooks:
- [gdptools method](./tutorials/spatial_aggregation/conus404_spatial_aggregation_DRB.ipynb)
- [Pangeo method](./tutorials/spatial_aggregation/conus404_spatial_aggregation.ipynb)

As well as a notebook directly comparing the two methods' speed and accuracy:
- [gdptools-Pangeo comparison](./tutorials/spatial_aggregation/conus404_spatial_aggregation_comparison.ipynb)

While both methods will produce the same result in similar amounts of time, we recommend using the `gdptools` method as it set up with a more user-friendly interface.

If you plan to use `gdptools` at spatial scales larger than the Delaware River Basin, we have made a few adaptations to the workflows above to mitigate the likelihood of crashing the compute instance you are working on. We have two workflows demonstrating this larger-scale spatial processing of the CONUS404 data over a set of polygons covering the full CONUS extent. Each workflow processes the data to a different set of polygons ([NHDPlusV2 snapshot of the Watershed Boundary Dataset HUC12 boundaries](https://www.sciencebase.gov/catalog/item/60cb5edfd34e86b938a373f4) or [GeoSpatialFabric v1.1](https://www.sciencebase.gov/catalog/item/5e29d1a0e4b0a79317cf7f63)), both of which are commonly used in hydrologic modeling:
- [Geospatial Fabric v1.1](./tutorials/spatial_aggregation/conus404_spatial_aggregation_GFv1_1.ipynb)
- [NHDPlusV2 snapshot of the Watershed Boundary Dataset HUC12 boundaries](./tutorials/spatial_aggregation/conus404_spatial_aggregation_WBD12.ipynb)

Please note that these last two notebooks have not been executed in our JupyterBook because they are configured to run a large computation on a specific computing environment (USGS on-prem Hovenweep supercomputer), so they cannot be executed within the context that builds this book.