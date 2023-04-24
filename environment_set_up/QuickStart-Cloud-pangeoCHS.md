# Quick-Start for pangeo.chs.usgs.gov Cloud Environment

Once you are added, the url will take you to your own personal JupyterHub space. The files in this space are only visible/accessible to the user who created them, so you will need to push them to a shared repository to work collaboratively. You will also have access to a shared set of kernels that are managed by USGS's Cloud Technologies (CTek) team in the Enterprise Technology Office (ETO). To use this JupyterHub instance:

1) Obtain access to `pangeo.chs.usgs.gov` by following 
[these instructions](https://support.chs.usgs.gov/display/CHSKB/Pangeo+Framework)

2) Open [https://pangeo.chs.usgs.gov/](https://pangeo.chs.usgs.gov/) in your browser

3) Spawn a server with the appropriate specifications from the menu of options that appears (the smallest one is probably fine if you are just testing things out)

4) Launch a terminal, configure your Github credentials, and clone this repository (or another that you are working on) into your working space

5) Use the navigation panel on the left to open a notebook, and select the pangeo conda env kernel in the dropdown menu in the upper right

6) Now you are ready to run/develop your notebooks

If you want to update the packages in the pangeo kernel, you will need to create a merge request with 
changes to this 
[environment.yml](https://code.chs.usgs.gov/usgs-chs/CHS-IaC/baseline/managed-services/pangeo/pangeo-image/-/blob/master/pangeo-notebook/environment.yml).
[Here is an example of a successfully merged request](https://code.chs.usgs.gov/usgs-chs/CHS-IaC/baseline/managed-services/pangeo/pangeo-image/-/merge_requests/45).
Please note that the update to the environment may take several weeks to go through.
