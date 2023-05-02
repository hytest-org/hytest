# Compute Environments

This section contains instructional materials and helper scripts to set up your computational environment for running HyTEST workflows and scripts in this repository.

The HyTEST workflows are built largely on the [Pangeo](https://pangeo.io/) software stack, and are designed to be portable between the cloud, HPC clusters, and your local computer (though some workflows may take an unreasonable amount of time to complete if you are working only on a local computer).

The instructions in this README help guide you to set up your own computational environment or to 
utilize USGS HPC and cloud resources (only available to USGS staff). If you do  not have access 
to USGS computational resources, we recommend you follow [these instructions](QuickStart-General.md) 
to set up a computational environment that can run our workflows.

## USGS Cloud Environment

If you are working in the cloud, we expect you to work in a JupyterHub instance that has
already been set up. If you are a USGS Water Mission Area (WMA) employee, you have a few
options for accessing a JupyterHub instance:
1) [pangeo.chs.usgs.gov](QuickStart-Cloud-pangeoCHS.md)<br>
   This JupyterHub instance is currently deployed on USGS's AWS account, and any USGS employee
   can request access to this space. Once you are added, the url will take you to your own
   personal JupyterHub space. The files in this space are only visible/accessible to the user
   who created them, so you will need to push them to a shared repository to work collaboratively.
   You will also have access to a shared set of kernels that are managed by USGS's Cloud Technologies
   (CTek) team in the Enterprise Technology Office (ETO). Anyone can put in a request to update these 
   shared kernels, but sometimes the update process can take several weeks.
2) [Nebari](QuickStart-Cloud-Nebari.md)<br>
   The HyTEST project is currently working on deploying an instance of [Nebari](https://www.nebari.dev/) JupyterHub. HyTEST will
   allow some of our priority users to test out this space once it is created. We will also provide instructions for how your project can deploy its own instance of Nebari JupyterHub. Nebari includes a shared space in the JupyterHub deployement, where all users can access and run aeach other's files/scripts. Any
   user can also quickly modify and update a set of shared kernels so that all users are working in the same development environment. This work is currently in development, and these instructions will be updated once this is available.
3) Your own JupyterHub Instance<br>
   Your can also work with your own deployment of a JupyterHub environment. You will need to
   make sure you have a kernel with all of the required packages set up to run these notebooks.


## USGS HPC Environment

While we prioritize the development of workflows to run on "_cloud_" infrastructure, we also provide some guidance for running them on USGS's supercomputers. You will need to access an enviroment which emulates the Jupyter server -- where the notebooks will reside and execute -- using the HPC hardware. There are many ways to do this. Here are three options, in increasing order of complexity and flexibility:

1) [Open OnDemand](OpenOnDemand.md)<br>
   This option provides the most effortless access to HPC hardware using a web interface. However, this only runs on the [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html) supercomputer.
2) [Jupyter Forward](JupyterForward.md)<br>
   This option gives you more control over how to launch the server, and on which host (can be
   run on [`Denali`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/denali.html), [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html), or other hosts to which you have a login). This setup requires that you
   install the jupyter-forward software on your PC.
3) [Custom Server Script](StartScript.md)<br>
   This option lets you completely customize your HPC compute environment and invoke the Jupyter
   server from a command shell on the HPC. This requires familiarity with the HPC command line, file
   editing, etc.

## Spinning Up Dask Clusters

Some of the notebooks in this repository make use of parallelism using Dask clusters.
The details of spinning up a cluster will differ, depending upon the environment.
We have a few sample 'helper' notebooks to illustrate the recommended way to
start clusters in these environments:

* [Local Desktop](Start_Dask_Cluster_Desktop.ipynb)
* [Denali HPC](Start_Dask_Cluster_Denali.ipynb)
* [Tallgrass HPC](Start_Dask_Cluster_Tallgrass.ipynb)
* [Nebari](Start_Dask_Cluster_Nebari.ipynb)
* [Pangeo.CHS.usgs.gov](Start_Dask_Cluster_PangeoCHS.ipynb)
