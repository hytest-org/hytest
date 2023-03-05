# Compute Environments

The `environment_set_up` directory contains instructional materials and helper scripts to set
up your computational environment for running HyTEST workflows and scripts in this repository.

The scripts in this repository are designed to be portable between a cloud environment and
on-prem HPC resources. We prioritize work in the cloud because anyone can create an account
there to run these workflows, but given that a large number of our users work on the USGS HPC
systems, we have also build out some instructional materials to help set up these workflows
in those environments as well.

## Cloud Environment

If you are working in the cloud, we expect you to work in a JupyterHub instance that has
already been set up. If you are a USGS Water Mission Area (WMA) employee, you have a few
options for accessing a JupyterHub instance:
1) [pangeo.chs.usgs.gov](QuickStart-Cloud-pangeoCHS.md)<br>
   This JupyterHub instance is currently deployed on a USGS AWS account, and any USGS employee
   can request access to this space. Once you are added, the url will take you to your own
   personal JupyterHub space, and files in this space are only visible/accessible to the user
   who created them. You will also have access to a shared set of kernels. The main disadvantage
   to using this JupyterHub instance is that if you want to update the packages in the kernel
   you are working in or create a new kernel, you will need to submit a ticket to CTek, and
   the update may not happen for several weeks.
2) [Nebari](QuickStart-Cloud-Nebari.md)<br>
   The HyTEST project is currently working on deploying an instance of Nebari JupyterHub, and
   we will allow some of our priority users to access this space. This will be a shared
   JupyterHub space, where all users can access and run any files in this deployment. Any
   user can also quickly modify and update the kernels available in this deployment. We will
   provide instructions for projects outside of HyTEST to deploy their own instance of a
   shared Nebari space. This work is currently in development, and these instructions will
   be updated once this is available.
3) Your own JupyterHub Instance<br>
   Your can also work with your own deployment of a JupyterHub environment. You will need to
   make sure you have a kernel with all of the required packages set up to run these notebooks.


## HPC Environment

While we prefer that these notebooks be run on "_cloud_" infrastructure, we also provide some guidance for running them on USGS's supercomputers. You will need to access an enviroment which emulates the Jupyter server -- where the notebooks will reside and execute -- using the HPC hardware. There are many ways to do this. Here are three options, in increasing order of complexity and flexibility:
While we prefer that these notebooks be run on "_cloud_" infrastructure, we also provide some guidance for running them on USGS's supercomputers. You will need to access an enviroment which emulates the Jupyter server -- where the notebooks will reside and execute -- using the HPC hardware. There are many ways to do this. Here are three options, in increasing order of complexity and flexibility:

1) [Open OnDemand](OpenOnDemand.md)<br>
   This option provides the most effortless access to HPC hardware using a web interface. Only runs on the [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html) supercomputer.
2) [Jupyter Forward](JupyterForward.md)<br>
   This option gives you more control over how to launch the server, and on which host (can be
   run on [`Denali`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/denali.html), [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html), or other hosts to which you have a login).  Requires that you
   install the jupyter-forward software on your PC.
3) [Custom Server Script](StartScript.md)<br>
   This option lets you completely customize your HPC compute environment and invoke the Jupyter
   server from a command shell on the HPC. Requires familiarity with the HPC command line, file
   editing, etc.

--------

Some of the notebooks in this repo make use of parallelism using Dask clusters.
The details of spinning up a cluster will differ, depending upon the environment.
We have a few sample 'helper' notebooks to illustrate the recommended way to
start clusters in these environments:

* [Denali HPC](Start_Dask_Cluster_Denali.ipynb)
* [Tallgrass HPC](Start_Dask_Cluster_Tallgrass.ipynb)
* [Nebari](Start_Dask_Cluster_Nebari.ipynb)
* [Pangeo.CHS.usgs.gov](Start_Dask_Cluster_PangeoCHS.ipynb)
