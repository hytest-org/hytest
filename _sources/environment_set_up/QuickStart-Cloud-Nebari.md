# Cloud: Nebari Quick-Start

If you are a USGS employee, and you would like to run HyTEST workflows in a cloud environment, we recommend that you work with the CHS's deployment of [Nebari](https://www.nebari.dev/), which can be accessed [here](https://nebari.chs.usgs.gov/). This JupyterHub instance is deployed on USGS's AWS account, and any USGS employee can request access to this space.

## File Space
This resource offers both a private (per user) and a shared file space in the JupyterHub environment. The private space is only visible to the user who created it, while the shared space allows for file sharing and collaboration among team members.

## Kernels
USGS's Cloud Hosting Solutions (CHS) team provides a global "pangeo" environment that is available to all users in the Nebari space by default. This environment includes many of the packages needed to run pangeo-style workflows.

However, most users will need to add custom packages for their workflows at some point. Thankfully, Nebari also allows any user to set up and modify a set of python kernels in their personal namespace.

We also have a HyTEST team set up in this space, where we manage a set of environments needed to run our HyTEST workflows. Please reach out to asnyder@usgs.gov if you have your Nebari account set up and would like to be added to the HyTEST team.

## Accessing the Nebari JupyterHub Instance
To use this JupyterHub instance:

1) You will need to request an account before you can log in. If you previously used the `pangeo.chs.usgs.gov` endpoint, you will have an account and you can proceed to log in with the `USGS Login` button. If you do not have an account yet, you can submit a request for one [here](https://taskmgr.chs.usgs.gov/plugins/servlet/desk/portal/10/create/485).

2) Open [https://nebari.chs.usgs.gov/](https://nebari.chs.usgs.gov/) in your browser (you will need to be on the USGS network or VPN to access this resource)

3) Login using Keycloak  and the `USGS Login` button

4) Launch JupyterLab from the landing page, and spawn a server with the appropriate specifications from the menu of options that appears (the smallest one is probably fine if you are just testing things out)

5) Launch a terminal, configure your Github credentials, and clone this repository (or another that you are working on) into your working space

6) Use the navigation panel on the left to open a notebook, and select the hytest-pangeo conda env kernel in the dropdown menu in the upper right

Now you are ready to run/develop your notebooks.