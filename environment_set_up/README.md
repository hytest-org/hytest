# Compute Environments

This section contains instructional materials and helper scripts to set up your computational environment for running HyTEST workflows and scripts in this repository.

The HyTEST workflows are built largely on the [Pangeo](https://pangeo.io/) software stack, and are designed to be portable between the cloud, HPC clusters, and your local computer (though some workflows may take an unreasonable amount of time to complete if you are working only on a local computer). Most of our workflows are contained in Jupyter notebooks, and we recommend running them in [JupyterLab](https://jupyterlab.readthedocs.io/en/latest/) or another development environment of your choice that supports Jupyter notebooks. If you are working on a team, you may want to consider using a shared [JupyterHub](https://jupyter.org/hub) instance, which allows multiple users to work in the same environment and share files easily. Below, we describe a few options for setting up or connecting to JupyterHub resources.


## Setting Up Your Own Computing Environment

If you do not have access to a JupyterLab/JupyterHub environment that has already been deployed, we recommend you follow [these instructions](QuickStart-General.md) to set up a computational environment that can run our workflows.

## USGS Cloud Environment (only available to USGS staff)

If you are a USGS employee, and you would like to run HyTEST workflows in a cloud environment, we recommend that you work with the CHS's deployment of [Nebari](https://www.nebari.dev/), which can be accessed [here](https://nebari.chs.usgs.gov/). This JupyterHub instance is deployed on USGS's AWS account, backed by a Kubernetes cluster for scaled compute, and any USGS employee can request access to this space. This resource offers both a private (per user) and a shared file space in the JupyterHub environment. The private space is only visible to the user who created it, while the shared space allows for file sharing and collaboration among team members. Learn how to use the Nebari JupyterHub instance in the [Quick-Start Guide](QuickStart-Cloud-Nebari.md).

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