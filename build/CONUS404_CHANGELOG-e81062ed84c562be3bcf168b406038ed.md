# CONUS404 Zarr Changelog

This changelog documents major changes to the [CONUS404 zarr datasets](./CONUS404_ACCESS.md). We do not anticipate regular changes to the dataset, but we may need to fix an occasional bug or update the dataset with additional years of data. Therefore, we recommend that users of the CONUS404 zarr data check this changelog regularly.

## 2025-04
We have move the CONUS404 zarr dataset in S3 storage to Glacier storage, so it is no longer accessible to be read into workflows. We recommend you use the copy of the zarr on the OSN pod, which can be accessed from any computing location.

## 2024-02
* Water year 2022 data (October 1, 2021 - September 30, 2022) was added to all zarr stores (`conus404-hourly-*`, `conus404-daily-*`, `conus404-monthly-*`).
* Coordinate x and y values were updated to fix an issue with how they were generated that resulted in small location errors (lat and lon were not changed).

## 2023-11
* Removed derived variables (E2, ES2, RH2, SH2) that were not part of original CONUS404 model output from CONUS404 zarr stores `conus404-hourly-*`, `conus404-daily-*`, `conus404-monthly-*`.
