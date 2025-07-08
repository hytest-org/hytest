# Compute Environments

This section contains instructional materials and helper scripts to set up your computational environment for running HyTEST workflows and scripts in this repository.

The HyTEST workflows are built largely on the [Pangeo](https://pangeo.io/) software stack, and are designed to be portable between the cloud, HPC clusters, and your local computer (though some workflows may take an unreasonable amount of time to complete if you are working only on a local computer). Most of our workflows are contained in Jupyter notebooks, and we recommend running them in [JupyterLab](https://jupyterlab.readthedocs.io/en/latest/) or another development environment of your choice that supports Jupyter notebooks. If you are working on a team, you may want to consider using a shared [JupyterHub](https://jupyter.org/hub) instance, which allows multiple users to work in the same environment and share files easily. Below, we describe a few options for setting up or connecting to JupyterHub resources.


## Setting Up Your Own Computing Environment

If you do not have access to a JupyterLab/JupyterHub environment that has already been deployed, we recommend you follow [these instructions](QuickStart-General.md) to set up a computational environment that can run our workflows.

## USGS Cloud Environment (only available to USGS staff)

If you are a USGS employee, and you would like to run HyTEST workflows in a cloud environment, we recommend that you work with the CHS's deployment of [Nebari](https://www.nebari.dev/), which can be accessed [here](https://nebari.chs.usgs.gov/). This JupyterHub instance is deployed on USGS's AWS account, and any USGS employee can request access to this space.

### Account Setup
You will need to request an account before you can log in. If you previously used the `pangeo.chs.usgs.gov` endpoint, you will have an account and you can proceed to log in with the `USGS Login` button. If you do not have an account yet, you can submit a request for one [here](https://taskmgr.chs.usgs.gov/plugins/servlet/desk/portal/10/create/485).

### File Space
This resource offers both a private (per user) and a shared file space in the JupyterHub environment. The private space is only visible to the user who created it, while the shared space allows for file sharing and collaboration among team members.

### Kernels
USGS's Cloud Hosting Solutions (CHS) team provides a global "pangeo" environment that is available to all users in the Nebari space by default. This environment includes many of the packages needed to run pangeo-style workflows.

However, most users will need to add custom packages for their workflows at some point. Thankfully, Nebari also allows any user to set up and modify a set of python kernels in their personal namespace.

We also have a HyTEST team set up in this space, where we manage a set of environments needed to run our HyTEST workflows. Please reach out to asnyder@usgs.gov if you have your Nebari account set up and would like to be added to the HyTEST team.


## USGS HPC Environment (only available to USGS staff)

While we prioritize the development of workflows to run on "_cloud_" infrastructure, we also provide some guidance for running them on USGS's supercomputers. First, make sure you have an account on Denali, Tallgrass, and/or Hovenweep. We recommend requesting accounts on all of these systems, as at times compute nodes may be unavailable on one system or the other. To get an account, fill out the [request form](https://hpcportal.cr.usgs.gov/index.html) and wait for approval (this may take a day or so).

Note that to access any of the HPCs, you must be on the DOI Network. If you are not in the office, please make sure you access these resources on the VPN.

You will need to access an enviroment which emulates the Jupyter server -- where the notebooks will reside and execute -- using the HPC hardware. There are many ways to do this. Here are three options, in increasing order of complexity and flexibility:

1) [Open OnDemand](OpenOnDemand.md)<br>
   This option provides the most effortless access to HPC hardware using a web interface. However, this only runs on the [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html) and [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html) supercomputers.
2) [Jupyter Forward](JupyterForward.md)<br>
   This option gives you more control over how to launch the server, and on which host (can be run on [`Denali`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/denali.html), [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html), [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html), or other hosts to which you have a login). This setup requires that you install the jupyter-forward software on your PC.
3) [Custom Server Script](StartScript.md)<br>
   This option lets you completely customize your HPC compute environment and invoke the Jupyter server from a command shell on the HPC. This requires familiarity with the HPC command line, file editing, etc. This (can be run on [`Denali`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/denali.html), [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html), [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html), or other hosts to which you have a login).