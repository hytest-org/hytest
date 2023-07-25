import asyncio
import io
import time
import zipfile
import httpx
import pandas as pd
from tqdm import tqdm

year = input("Enter year: ")
year = str(year)
var = input("Enter variable (ppt, tmax, tmin): ")
concurrent_requests = input("Enter concurrent requests (if none entered, default is 10):")

# set number of concurrent requests to not time out HTTP server
if concurrent_requests != "":
    MAX_CONCURRENT_REQUESTS = int(concurrent_requests)
else:
    MAX_CONCURRENT_REQUESTS = 10

# create client to handle downloading files and extracting
async def download_and_extract_file(url: str, semaphore: asyncio.Semaphore, progress_bar: tqdm):
    async with semaphore:
        async with httpx.AsyncClient(timeout=None) as client:
            response = await client.get(url, follow_redirects=True)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                    z.extractall("./download/")
                    progress_bar.update(1)

async def main():
    time_start = time.time()
    print(f"Downloading PRISM data for {year} and the {var} variable...")
    
    # function to programmatically set up URLs
    def create_urls(var: str, dates_list: list):
        base_url = "http://services.nacse.org/prism/data/public/4km/"
        full_url_list = []
        for date in dates_list:
            full_url = f"{base_url}{var}/{date}"
            full_url_list.append(full_url)
        return full_url_list

    # create list of dates for full year
    dates_list = (pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31")
                  .strftime("%Y%m%d")
                  .tolist())
    
    # create URL list
    url_list = create_urls(var, dates_list)

    # Create a semaphore to limit concurrent requests
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

    # Download and extract files asynchronously
    tasks = []
    # set up tqdm bar
    with tqdm(total=len(url_list)) as pbar:
        for url in url_list:
            tasks.append(download_and_extract_file(url, semaphore, pbar))
        await asyncio.gather(*tasks)

    time_end = time.time()
    print("Download complete! Please continue to the next step.")
    print(f"Time to download and extract files: {time_end - time_start} seconds")

if __name__ == "__main__":
    # Check if an event loop is already running
    if asyncio.get_event_loop().is_running():
        asyncio.run_coroutine_threadsafe(main(), asyncio.get_event_loop())
    else:
        asyncio.run(main())



# import httpx
# import zipfile
# import io
# import pandas as pd
# import asyncio
# import time

# year = input("Enter year: ")
# year = str(year)
# var = input("Enter variable (ppt, tmax, tmin): ")


# MAX_CONCURRENT_REQUESTS = 10

# async def download_and_extract_file(url: str, semaphore: asyncio.Semaphore): #file: str, 
#     async with semaphore:
#         async with httpx.AsyncClient(timeout=None) as client:
#             response = await client.get(url, follow_redirects=True)
#             if response.status_code == 200:
#                 with zipfile.ZipFile(io.BytesIO(response.content)) as z:
#                     z.extractall("./download/")

# async def main():
    
#     time_start = time.time()
#     print(f"Downloading PRISM data for {year} and the {var} variable...")
#     # Set up URLs
#     def create_urls(var: str, dates_list: list):
#         base_url = "http://services.nacse.org/prism/data/public/4km/"
#         full_url_list = []
#         for date in dates_list:
#             full_url = f"{base_url}{var}/{date}"
#             full_url_list.append(full_url)

#         return full_url_list

#     # Create list of dates for January 1992 using pandas
#     dates_list = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31").strftime("%Y%m%d").tolist()
#     url_list = create_urls(var, dates_list)

#     # Create a semaphore to limit concurrent requests
#     semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)

#     # Download and extract files asynchronously
#     tasks = []
#     for url in url_list:
#         tasks.append(download_and_extract_file(url, semaphore))
#     await asyncio.gather(*tasks)

#     time_end = time.time()
#     print("Download complete! Please continue to the next step.")
#     print(f"Time to download and extract files: {time_end - time_start} seconds")

# if __name__ == "__main__":
#     # Check if an event loop is already running
#     if asyncio.get_event_loop().is_running():
#         asyncio.run_coroutine_threadsafe(main(), asyncio.get_event_loop())
#     else:
#         asyncio.run(main())