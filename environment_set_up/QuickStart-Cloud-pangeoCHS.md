# Quick-Start for pangeo.chs.usgs.gov Cloud Environment

This document will help you set up the correct computing environment on the USGS JupyterHub instance deployed at pangeo.chs.usgs.gov. This JupyterHub instance is currently deployed on a USGS AWS account, and any USGS employee can request access to this space. Once you are added, the url will take you to your own personal JupyterHub space, and files in this space are only visible/accessible to the user who created them. You will also have access to a shared set of kernels.

1) Obtain access to `pangeo.chs.usgs.gov` by following 
[these instructions](https://support.chs.usgs.gov/display/CHSKB/Pangeo+Framework)

2) Clone this repository containing example notebooks into your working space

3) Open a notebook and select the pangeo conda env kernel

4) Run the notebook

If you want to update the packages in the pangeo kernel, you will need to create a merge request with 
changes to this 
[environment.yml](https://code.chs.usgs.gov/usgs-chs/CHS-IaC/baseline/managed-services/pangeo/pangeo-image/-/blob/master/pangeo-notebook/environment.yml).
[Here is an example of a successfully merged request](https://code.chs.usgs.gov/usgs-chs/CHS-IaC/baseline/managed-services/pangeo/pangeo-image/-/merge_requests/45).
Please note that the update to the environment may take several weeks to go through.
