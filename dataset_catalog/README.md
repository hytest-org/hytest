# HyTEST Data Catalog (Intake)
This section describes how to use HyTEST's [intake catalog](https://intake.readthedocs.io/en/latest/catalog.html). Intake catalogs help reduce or remove the burden of handling different file formats and storage locations, making it easier to read data into your workflow. They also allow data providers to update the filepath/storage location of a dataset without breaking the workflows that were built on top of the intake catalog.

Our catalog facilitates this access for HyTEST's key data offerings and is used to read the data into the notebooks contained in this repository. While intake catalogs are Python-centric, they are stored as a yaml file, which should also be easy to parse using other programming languages, even if there is no equivalent package in that programming language.

Please note that this catalog is a temporary solution for reading data into our workflows. By the end of 2025, we hope to replace this catalog by a [STAC](https://stacspec.org/en) catalog. We plan to update all notebooks to read from our STAC at that time, as well. You can learn more about the USGS Water Mission Area's STAC catalog [here](./STAC.md).

## Storage Locations
Before getting into the details of how to use the intake catalog, it will be helpful to have some background on the various data storage systems HyTEST uses. Many of the datasets in our intake catalog have been duplicated in multiple storage locations, so you will need to have a basic understanding of these systems to navigate the data catalog. For datasets that are duplicated in multiple locations, the data on all storage systems will be identical; however, the details and costs associated with accessing them may differ. Datasets that are duplicated in multiple locations will have identical names, up until the last hypenated part of the name, which will indicate the storage location; for example, `conus404-hourly-cloud`, `conus404-hourly-osn`, and `conus404-hourly-onprem` are all identical datasets stored in different places. The four locations we store data currently are: **AWS S3 buckets**, **Open Storage Network (OSN) pods**, and [USGS on-premises supercomputer](https://hpcportal.cr.usgs.gov/) storage systems (one storage system for the **Tallgrass/Denali** supercomputers and another for the **Hovenweep** supercomputer). Each of these locations is described in more detail below.

### AWS S3
This location provides object storage through an Amazon Web Services (AWS) Simple Storage Service (S3) bucket. This data is free to access for workflows that are running in the AWS us-west-2 region. However, if you would like to pull the data out of the AWS cloud (to your local computer, a supercomputer, or another cloud provider) or into another [AWS cloud region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html), you will incur fees. This is because the bucket storing the data is a **“requester pays”** bucket. The costs associated with reading the data to other computing environments or AWS regions is documented [here](https://aws.amazon.com/s3/pricing/) (on the “Requests and Data Retrievals” tab). If you do need to read this data into a computing environment outside the AWS us-west-2 region, you will need to make sure you have an [AWS account](https://aws.amazon.com/account/) set up. You will need credentials from this account to read in the data, and your account will be billed. Please refer to the [AWS Credentials](../environment_set_up/Help_AWS_Credentials.ipynb) section of this book for more details on handling AWS credentials.

**Datasets in the intake catalog that are stored in an S3 bucket have a name ending in "-cloud".**

### Open Storage Network (OSN) Pod
This location provides object storage through Woods Hole Oceanographic Institute’s [Open Storage Network (OSN)](https://www.openstoragenetwork.org/) storage pod. This OSN pod that HyTEST uses is housed at the Massachusetts Green High Performance Computing Center on a **high-speed (100+ GbE) network**. This copy of the data is **free** to access from any computing environment and **does not require any credentials** to access.

The OSN pod storage can be accessed through an API that is compatible with the basic data access model of the S3 API. The only major difference is that the user needs to specify the appropriate endpoint url for the OSN pod when making the request. However, *a user accessing data on the OSN pod through HyTEST's intake catalog will not have to worry about these details*, as the intake package will handle them for you. If you would like to access the data on the OSN pod through a mechanism other than intake, you may want to review the [Data/Cloud Storage](../essential_reading/DataSources/Data_S3.md) section of this book.

**Datasets in the intake catalog that are stored on the OSN pod have a name ending in "-osn".**
 
### USGS On-premises Supercomputer Storage (Caldera for Tallgrass/Denali and Hovenweep)
The last storage location is the USGS on-premises disk storage that is attached to the USGS supercomputers (often referred to as Caldera). This location is **only accessible to USGS employees or collaborators who have been granted access to [USGS supercomputers](https://hpcportal.cr.usgs.gov/)**. This is the preferred data storage to use if you are working on the USGS supercomputers as it will give you the fastest data reads.

The Tallgrass and Denali supercomputers share on filesystem, and the Hovenweep supercomputer has a different filesystem. These supercomputers can only read data from their own filesystems (you *cannot* read data from the filesystem attached to Denali/Tallgrass into Hovenweep and vice versa). You also *cannot* read data from an on-premises storage system into any computing environment outside of the USGS supercomputers (like your local computer or the cloud). More information about this storage system can be found in the [HPC User Docs](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/caldera.html) (which are also only accessible through the internal USGS network).

**Datasets in the intake catalog that are stored on the filesystem attached to Denali/Tallgrass have a name ending in "-onprem", while datasets stored on the filesystem attached to Hovenweep have a name ending in "-onprem-hw".**

## Example Intake Catalog Usage
Now that you have an understanding of the different storage systems HyTEST uses, you will be able to navigate the HyTEST intake catalog and make a selection that is appropriate for your computing environment. Below is a demonstration of how to use HyTEST's intake catalog to select and open a dataset in your python workflow.

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

## Demos
Demos for working with the data catalogs can be found in the [demos](https://github.com/hytest-org/hytest/tree/main/dataset_catalog/demos) folder of our repository.

## Subcatalogs
The main HyTEST intake catalog includes the use of sub-catalogs. A sub-catalog may contain a set of datasets for a particular use case (like a specific tutorial) or groupings of related datasets. For example, the CONUS404 datasets (at different time steps and storage locations) are stored in their own sub-catalog. An example of calling these catalogs in can be found [here](./subcatalogs/README.md). 

