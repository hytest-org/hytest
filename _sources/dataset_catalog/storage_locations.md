# Data Storage Locations
Before getting into the details of how to use our [STAC or intake catalogs](./README.md), it will be helpful to have some background on the various data storage systems HyTEST uses to host data assets. Many of the datasets in our intake catalog have been duplicated in multiple storage locations, so you will need to have a basic understanding of these systems to navigate the data catalog. For datasets that are duplicated in multiple locations, the data on all storage systems will be identical; however, the details and costs associated with accessing them may differ. 

The four locations we store data currently are: **AWS S3 buckets**, **Open Storage Network (OSN) pods**, and [USGS on-premises supercomputer](https://hpcportal.cr.usgs.gov/) storage systems (one storage system for the **Tallgrass/Denali** supercomputers and another for the **Hovenweep** supercomputer).

## Identifying Storage Location from a Data Catalog Entry
### intake
In the intake catalog, datasets that are duplicated in multiple locations will have an intake catalog entry for each storage location. These entries will have identical names, up until the last hypenated part of the name, which will indicate the storage location; for example, `conus404-hourly-s3`, `conus404-hourly-osn`, and `conus404-hourly-onprem-hw` are all identical datasets stored in different places (`s3`, `osn`, and `onprem-hw`).

### STAC
In the STAC Catalog, datasets that are duplicated in multiple locations will have multiple **Assets** attached to the singular STAC entry for that dataset. Information about the storage location for each data asset is included in the the asset's title, description, and roles.

## Description of Storage Locations
Each of the storage locations used by the HyTEST community to host data assets is described in more detail below.

### Open Storage Network (OSN) Pod
This location provides object storage through Woods Hole Oceanographic Institute’s [Open Storage Network (OSN)](https://www.openstoragenetwork.org/) storage pod. This OSN pod that HyTEST uses is housed at the Massachusetts Green High Performance Computing Center on a **high-speed (100+ GbE) network**. This copy of the data is **free** to access from any computing environment and **does not require any credentials** to access.

The OSN pod storage can be accessed through an API that is compatible with the basic data access model of the S3 API. The only major difference is that the user needs to specify the appropriate endpoint url for the OSN pod when making the request. However, *a user accessing data on the OSN pod through HyTEST's intake catalog or the WMA STAC Catalog will not have to worry about these details* because the python packages used to open the data from these catalogs will ingest that information directly from our catalog. If you would like to access the data on the OSN pod through a mechanism other than intake or STAC, you may want to review the [Data/Cloud Storage](../essential_reading/DataSources/Data_S3.md) section of this book.

**Datasets in the intake catalog that are stored on the OSN pod have a name ending in "-osn".**

### AWS S3
This location provides object storage through an Amazon Web Services (AWS) Simple Storage Service (S3) bucket. This data is free to access for workflows that are running in the AWS us-west-2 region. However, if you would like to pull the data out of the AWS cloud (to your local computer, a supercomputer, or another cloud provider) or into another [AWS cloud region](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.RegionsAndAvailabilityZones.html), you will incur fees. This is because the bucket that we use to store the data is a **“requester pays”** bucket. The costs associated with reading the data to other computing environments or AWS regions is documented [here](https://aws.amazon.com/s3/pricing/) (on the “Requests and Data Retrievals” tab). If you do need to read this data into a computing environment outside the AWS us-west-2 region, you will need to make sure you have an [AWS account](https://aws.amazon.com/account/) set up. You will need credentials from this account to read in the data, and your account will be billed. Please refer to the [AWS Credentials](../environment_set_up/Help_AWS_Credentials.ipynb) section of this book for more details on handling AWS credentials.

**Datasets in the intake catalog that are stored in an S3 bucket have a name ending in "-s3".**

### USGS On-premises Supercomputer Storage (Caldera for Tallgrass/Denali and Hovenweep)
The last storage location is the USGS on-premises disk storage that is attached to the USGS supercomputers (often referred to as Caldera). This location is **only accessible to USGS employees or collaborators who have been granted access to [USGS supercomputers](https://hpcportal.cr.usgs.gov/)**. This is the preferred data storage to use if you are working on the USGS supercomputers as it will give you the fastest data reads.

The Tallgrass and Denali supercomputers share on filesystem, and the Hovenweep supercomputer has a different filesystem. These supercomputers can only read data from their own filesystems (you *cannot* read data from the filesystem attached to Denali/Tallgrass into Hovenweep and vice versa). You also *cannot* read data from an on-premises storage system into any computing environment outside of the USGS supercomputers (like your local computer or the cloud). More information about this storage system can be found in the [HPC User Docs](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/caldera.html) (which are also only accessible through the internal USGS network).

**Datasets in the intake catalog that are stored on the filesystem attached to Denali/Tallgrass have a name ending in "-onprem", while datasets stored on the filesystem attached to Hovenweep have a name ending in "-onprem-hw".**

### Storage Location Summary
The following table is a quick summarization of the storage locations described above in a more quickly referenceable format.

| Storage Location | Who Can Access? | What computing environments can you read the data into? | Cost to Access | Intake Catalog Naming |
|---|---|---|---|---|
| Open Storage Network (OSN) Pod | Public, no credentials required | any computing location | Free | -osn |
| AWS S3 Storage | Public, AWS credentials required | any computing location | Free for workflows running in AWS us-west-2 region, otherwise see [AWS pricing](https://aws.amazon.com/s3/pricing/) | -s3 |
| Hovenweep (USGS Supercomputer) | USGS employees, collaborators with access to USGS supercomputers | USGS Hovenweep supercomputer | Free | -onprem-hw |
| Tallgrass/Denali (USGS Supercomputers) | USGS employees,s collaborators with access to USGS supercomputers | USGS Tallgrass and Denali supercomputers | Free | -onprem |