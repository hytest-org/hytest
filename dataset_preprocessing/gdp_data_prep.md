
# Geo Data Portal : Dataset Preparation for the Geo Data Portal 
Created by [ Blodgett, David L.]{.author}, last modified by [ Hines,
Megan K.]{.editor} on May 13, 2015

## Introduction 

This page is a reference for NCCWSC projects that are gridded time
series data, generally climate projections, that will be archived using
techniques developed for the Geo Data Portal project. The process is
described at a high level to establish expectations in the first
section. An overview of the NetCDF-data model is given, largely to
disambiguate the language used in the subsequent section, but also as a
primer for those unfamiliar with NetCDF. The final section gives general
specifications and narrative notes regarding implementation of the
specifications. This document is subject to change, and will grow as
more NCCWSC projects do through this process. Please do not hesitate to
email [dblodgett@usgs.gov](mailto:dblodgett@usgs.gov) with questions comments and suggestions.

## Data Publication and Metadata Curation Process 

1.  **Collect sources and do science / modeling / downscaling.**
    1.  Attention to data delivery considerations during this process
        will greatly reduce the time required at the end of the project.

2.  **Create final dataset to be delivered to NCCWSC archive.**
    1.  The dataset should be collected into a single folder structure
        with basic readme-type documentation describing the file layout.

3.  **Transfer example files to archive manager for review.**
    1.  This should be via email, ftp, or other web-method.

4.  **Implement modifications needed to satisfy data archiving
    requirements.**

    1.  Some iteration may take place and some modifications may be
        implemented by the archive manager.

5.  **Complete metadata templates for publication.**
    1.  This should be completed after discussion of elements with CSC
        Data Managers.

6.  **Transfer all files to archive.**

    1.  For archives up to a terabyte, this can take place over the
        internet, otherwise, hard drives should be prepared and shipped.

7.  **Archive manager creates aggregations and makes final dataset
    modifications.**

    1.  Modifications that affect the dataset content, such as data
        packing, will be cleared with PIs.

8.  **Review metadata in final form prior to public release.**

    1.  This will be on publicly accessible, un-advertised testing
        servers.

9.  **Release dataset services and add to public dataset catalog.**

    1.  ISO Metadata will be released through various catalogs at final
        dataset release and permanent uris for data access will be
        established.

## Introduction to the NetCDF Data Model 

### NetCDF Data
This guide will not go into specifics of any library or package for
writing NetCDF data. Rather, below is an overview of important details
of NetCDF files required for easy access with various NetCDF tools
including those used for the Geo Data Portal.

NetCDF data are made up of dimensions, variables, and attributes.
Attributes are describe variables, and \'global\' attributes describe an
entire NetCDF file. Variables hold numerical values that are either data
or coordinates, where coordinate values have significance in time or
space.

#### Dimensions: 

Gridded NetCDF files will always have an X and Y dimension. They may
also have a T and / or Z dimension. Less common but possible, is a
\'string length\' dimension. Generally, dimensions are of a fixed size;
however, one dimension, commonly time, can be \'unlimited\' meaning it
can be added to with any special considerations.

#### Variables:

NetCDF variables are containers for data. The special \'coordinate
variables\' contain data that describes the dimension\'s coordinates in
space and time. A variable is defined by giving a name a data type, and
a dimensionality. eg. the \'lat\' variable is of type 64bit float and
has dimensionality \'y\' or the \'prcp\' variable is of type 16bit
integer and has dimensionality \'x,y,t\'. Once defined, data can be
written into the indices of a variable according to its data type and
dimensions.

#### Attributes: 

NetCDF attributes describe variables and datasets. To be useful across
multiple types of software, common conventions have been specified for
what particular attributes should be called. Dataset details such as
\'title\', \'summary\', and \'source\' should be used strictly by their
standard name for interoperability purposes. It is important to note
that there are many important variable attributes, like \'coordinates\'
\'grid_mapping\', and \'missing_value\' that should not be overlooked
because of their structural importance to a dataset.

When creating NetCDF data, if an attribute being used is not listed in
the conventions stated in the \'conventions\' global attribute, its
content should be unique from any described in the conventions. That is
not to say that the conventions are a limit, just a guide and
interoperability target.

For an in depth look at all things NetCDF please visit the Unidata
[NetCDF Users
guide](https://www.unidata.ucar.edu/software/netcdf/docs/netcdf/index.html#Top)

## Requirements and notes for gridded time series datasets. 

Gridded time series datasets can be broken high and low spatial
resolution. With 1-12km being low resolution and 10-30m bring high
resolution. Most datasets fall into one or the other category. Those in
the middle can be handled using either approach described here.

### General Specifications for Low Resolution Gridded Time Series Datasets: 

1.  Stored using NetCDF-3 or NetCDF-4 using the Classic data model.
2.  Should use Lat/Lon or Projected X/Y gridded coordinates with a
    [NetCDF-CF grid mapping
    variable.](http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#grid-mappings-and-projections)
3.  Time must be included in the file with the time stamps corresponding
    to the leading edge of the time step.
4.  All [NetCDF-CF
    Attributes](http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#idp4812688) should be included in files.
5.  As many [NetCDF Attribute Convention for Dataset Discovery
    attributes](http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_%28ACDD%29) as apply should be included in files.
6.  If possible, data should be packed into fixed precision integers
    using offset and scale factor attributes on applicable variables.
7.  Time must be the outer dimension (listed first in variable\'s
    dimensionality).
8.  For archiving (read performance), it is preferred that the time
    dimension be fixed rather than unlimited.

#### Notes regarding flexibility and purpose of these requirements: 
-   The Geo Data Portal archive includes a single, logical dataset, for
    each contiguous spatio-temporal domain. eg. Region-1 2000-2030,
    Region-2 2000-2030, Region-1 2070-2100, etc. These domains can be
    made up of collections of files and assembled using
    [NetCDF-Aggregation](http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/ncml/v2.2/Aggregation.html). 
    Metadata from the files in the collection bubbles
    up to the whole collection. That metadata can be defined,
    overwritten, or removed when the collection is defined.
-   The Geo Data Portal archive exposes all individual files from the
    collection for download. This means that any metadata that applies
    to each file should be included within the files and not just in the
    collection. While there is flexibility on this point, it should be
    considered best practice to include NetCDF-CF Attributes and NetCDF
    Attribute Convention for Dataset Discovery attributes in every file.
    Adding attributes to files is best done when initially creating
    them, but can be accomplished easily using the [NetCDF Operators
    Command
    *ncatted.*](http://nco.sourceforge.net/nco.html#ncatted-netCDF-Attribute-Editor)
-   Item 6 above is required for datasets larger than a few hundred
    gigabytes. In addition, chunking and deflation of data should be
    performed. It has been found that chunks should be no less than 400
    pixels and no more than 1000 pixels. This ensures that significant
    deflation is possible and the overhead when reading small subsets
    isn\'t too high.
-   In order to allow aggregation of collections and fast access to
    underlying data of large datsets, items 7 and 8 above are required.
    While item 8 stops tools like the [NetCDF
    Operators](http://nco.sourceforge.net/) from easily concatenating files together without a
    rewrite, it results in a huge improvement in performance when
    scanning files to determine their size. This is a result of a an
    \'unlimited\' dimensions coordinate variable (usually time) being
    stored interleaved in the file for each time step worth of data.
    When scanning for the available time range, a computer is forced to
    scan the entire file rather than reading the time coordinate
    variable as a contiguous block on disk as is the case with a
    \'fixed\' time dimension. Note that this change can be made using
    the NetCDF Operators flag \--fix_rec_dmn

### General Specifications for high resolution gridded time series datasets: 

1.  Stored as NetCDF-4 using the Classic data model or as GeoTIFF files.
2.  Should use Lat/Lon or Projected X/Y gridded coordinates with a
    [NetCDF-CF grid mapping
    variable](http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#grid-mappings-and-projections) or appropriate [GDAL
    compatible](http://www.gdal.org/)
    projection.
3.  Time/date must be included in the file for NetCDF or the file names
    for GeoTIFF with time stamps corresponding to the leading edge of
    the time step.
4.  All [NetCDF-CF
    Attributes](http://cf-pcmdi.llnl.gov/documents/cf-conventions/1.6/cf-conventions.html#idp4812688)should be included in NetCDF files or provided in
    .ncml format for GeoTIFF files.
5.  As many [NetCDF Attribute Convention for Dataset Discovery
    attributes](http://wiki.esipfed.org/index.php/Attribute_Convention_for_Data_Discovery_%28ACDD%29) as apply should be included.
6.  Data must be stored using appropriate data types and compressed
    using a NetCDF-4 or GeoTIFF deflation algorithm.
7.  For NetCDF data, time must be the outer dimension (listed first in
    variable\'s dimensionality).
8.  For NetCDF, it is preferred that the time dimension be fixed rather
    than unlimited.

#### Notes regarding flexibility and purpose of these requirements:
-   Generally, the notes for lower-resolution gridded time series data
    apply to high resolution and are not repeated here.
-   Collections of GeoTIFF files will be created using the [NetCDF
    Markup Language\'s
    \'joinNew\'](http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/ncml/v2.2/Aggregation.html#joinNew) aggregation type. This method relies on a time stamp
    being available in each file\'s name. The format is flexible but
    must be describable using the
    [java.text.SimpleDateFormat](http://www.unidata.ucar.edu/software/thredds/current/netcdf-java/ncml/v2.2/AnnotatedSchema.html#SimpleDateFormat) documented here.
-   Large data sets that could be stored as a smaller data type will be
    rejected. NetCDF-4 provides standard attributes to scale and offset
    integers into fixed precision decimals and GeoTIFFs can be written
    using signed and unsigned datatypes for a wide range of precisions.
    Depending on a dataset\'s contents, deflation is more or less
    effective. We suggest deflate level 1 for datasets that deflate well
    and deflate level 6 as a maximum. This ensures good read performance
    of the archived data.

 
