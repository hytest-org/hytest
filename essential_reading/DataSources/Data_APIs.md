# Data/APIs

Application Programming Interfaces (API) are a common way of accessing and processing data over the internet between a distant application and the application (or script) you are working on. Another method is File Transfer Protocol calls (FTP), which are used to transfer large amounts of data over the internet. As FTPs are not communications between applications but just simple data tranfers with no processing capabilities, they are being used less and less over time, though some data is still only available over the internet in this fashion. 

## **API**

In Python, there are different ways of getting data with APIs and we will examine two of the more common: using a library such as `requests` to query the API or use a library a developer has created to make interacting with an API easier, such as `pygeohydro`, through different helper functions or improved documentation.

#### `requests` 
The `requests` library is a [well documented library](https://requests.readthedocs.io/en/latest/) for issuing *get* requests. 

A common example in geospatial work is getting data from ArcGIS Feature Service layers and creating a `geopandas GeoDataFrame` from it. The typical process for accomplishing this is using a combination of the REST API page, the REST API query page to help build a query (if available), and an ArcGIS Online view of the data for help understanding the contents of fields. An example is the [HUC10 Watershed](https://hub.arcgis.com/datasets/CC-NY::wbdhu10-watershed/explore?location=42.219929%2C-73.252807%2C9.00) by Columbia County Planning.The dataset can be explored using the included map and an comes with an [API Explorer](https://hub.arcgis.com/datasets/CC-NY::wbdhu10-watershed/api) to help build the API. 

Putting this all together would look like this:
<br>

```python
import requests
import geopandas as gpd

# create base url and paylaod
base_url = "https://services3.arcgis.com/F5762GA30C3SyZFy/arcgis/rest/services/Watershed_Boundary_Dataset/FeatureServer/4/query?"
payload = {"where":"1=1", #all records that match
    "returnGeometry":"true",
    "outFields": "*",
    "outSR":"4326", #WGS84
    "f": "pjson" #f=format
}

# send request, which will create URL
r = requests.get(base_url, params=payload)

# check that get was successful before creating GeoDataFrame
if r.status_code == 200: #200 = success
    gdf = gpd.read_file(r.text)
else:
    print(f"Request failed. Status code = {r.status_code}")

# plot to see the geometries
gdf.plot()
```

Some FeatureServers have preformatted data calls that return the data as a GeoJSON, which can be read directly into a GeoDataFrame. The same code above would look like this with a GeoJSON API call:

```python
import geopandas as gpd

url = "https://services3.arcgis.com/F5762GA30C3SyZFy/arcgis/rest/services/Watershed_Boundary_Dataset/FeatureServer/4/query?outFields=*&where=1%3D1&f=geojson"

# create GeoDataFrame
gdf = gpd.read_file(url)

# plot to see the geometries
gdf.plot()
```

#### `pygeohydro`

Libraries like [pygeohydro](https://docs.hyriver.io/autoapi/pygeohydro/index.html) provide easy ways to format data calls to APIs by formatting the URL behind the scenes using their helper functions. This call is being made to the [WBD HUC6 Feature Layer](https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/3) and is being done using the already known HUC6 ids 020401 and 020402. 

```python
from pygeohydro import pygeohydro

# bring in HUC6 boundaries based on known IDs
gdf = pygeohydro.WBD("huc6").byids("huc6", ["020401", "020402"])

gdf.plot()
```

You can also use the `bysql` method to send a condition to the *where* field in the [query](https://hydro.nationalmap.gov/arcgis/rest/services/wbd/MapServer/3/query). If we wanted the HUC6 boundaries found only in the state of Michigan (MI), we would create a SQL call (column='value') as states='MI'. Note the single quotes, which SQL uses in this instance and will not work with double quotes (" ").

```python
from pygeohydro import pygeohydro

# bring in HUC boundaries found only in Michigan
gdf = pygeohydro.WBD("huc6").bysql("states='MI'")

gdf.plot()
```

## **FTP**

FTP is often the access method for many legacy datasets. An example is bringing in data from NOAA's [Global Climate Reference Network FTP Server](https://www.ncei.noaa.gov/access/crn/qcdatasets.html). Here, the `fsspec` library is used to create an FTPFileSystem instance locally that speaks to the FTP server, read in a text file that contains station data using `pandas`, and the data is used to create a GeoDataFrame.

```python
import geopandas as gpd
from fsspec.implementations.ftp import FTPFileSystem
import pandas as pd

fs = FTPFileSystem("ftp.ncei.noaa.gov")

data = pd.read_table(fs.open("/pub/data/uscrn/products/stations.tsv")) 

gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data["LONGITUDE"], data["LATITUDE"]), crs="EPSG:4326")

gdf.plot()
```

Say you just wanted the daily tabular data from a single station, you could use a combination of `fsspec` functions, including `glob` to search for files.

```python
from fsspec.implementations.ftp import FTPFileSystem
import pandas as pd

stat_name = "Avondale"

# instantiate FTP system
fs = FTPFileSystem("ftp.ncei.noaa.gov")

# get list of all files with Avondale in name
file_list_glob = fs.glob(
    f"/pub/data/uscrn/products/daily01/**/*{stat_name}*")

# create dataframe of data
df = pd.DataFrame()

for file in file_list_glob:
    stat_data = pd.read_csv(fs.open(file), header=None, sep="\t")
    df = pd.concat([df, stat_data])

# the data is all crammed into a single column so spread it out
df = df[0].str.split(" +",expand = True)

df.head()
```

These are a couple of ways of accessing data using APIs and FTPs.