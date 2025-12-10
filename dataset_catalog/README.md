# Data Catalogs
The HyTEST community currently makes use of several public data catalogs to read data into our modeling workflows. Two of these public data catalogs are maintained paritally or fully by the HyTEST community and contain a majority of the datasets you see used in our example workflows:
- [USGS Water Mission Area (WMA) STAC catalog](https://api.water.usgs.gov/gdp/pygeoapi/stac/stac-collection)
- [HyTEST intake catalog](https://github.com/hytest-org/hytest/blob/main/dataset_catalog/hytest_intake_catalog.yml)

We are also likely to reference other public data catalogs which point to analysis-ready data assets of relevance to our community. Some of the key data catalogs that we are not involved in the maintenance of, but reference regularly when looking for data assets include the following:
- [Registry of Open Data on AWS](https://registry.opendata.aws)
- [Microsoft Planetary Computer Data Catalog](https://planetarycomputer.microsoft.com/catalog)
- [ClimateR Catalog](https://mikejohnson51.github.io/climateR/)

## HyTEST Intake vs WMA STAC Catalogs
The HyTEST community started by catalogging the key data assets we needed for our workflows in an [intake catalog](https://intake.readthedocs.io/en/latest/catalog.html). We are now moving towards combining our data catalog with the USGS WMA [STAC Catalog](https://stacspec.org/en). At the present moment, the WMA STAC Catalog contains gridded datasets related to:
- common hydrologic model inputs such as climate or other forcing datasets
- hydrologic model outputs
- observational datasets related to hydrology and/or water budgets

The gridded datasets used by the HyTEST community are also still contained in our intake catalog, but we will move towards using the STAC Catalog exclusively for these assets in time.

The tabular and vector datasets used by the HyTEST community are currently cataloged only in our intake catalog; however, this may change with time, and we encourage our users to visit this page to get the latest information about recommended data catalogs and their maintenance status.

Currently you are likely to need to use a combination of these data catalogs to open all the data you need for our tutorials. We recommend prioritizing the use of the WMA STAC Catalog when possible, and supplementing with the HyTEST intake catalog for data assets that are not yet incorporated into the STAC Catalog. To learn more about each of theses catalogs, please review our tutorials of each:
- [WMA STAC Catalog](STAC.ipynb)
- [HyTEST intake catalog](intake.md)

In order to effectively understand which data assets are best for your usage, you may also need to read more about the different [storage locations](./storage_locations.md) that we use to store our data assets.
