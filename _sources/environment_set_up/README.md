# Compute Environments

This section contains instructional materials and helper scripts to set up your computational environment for running HyTEST workflows and scripts in this repository.

The HyTEST workflows are built largely on the [Pangeo](https://pangeo.io/) software stack, and are designed to be portable between the cloud, HPC clusters, and your local computer (though some workflows may take an unreasonable amount of time to complete if you are working only on a local computer).

## Setting Up Your Own Computing Environment

If you do not have access to USGS computational resources, we recommend you follow [these instructions](QuickStart-General.md) to set up a computational environment that can run our workflows.

## USGS Cloud Environment (only available to USGS staff)

If you are working in the cloud, we expect you to work in a JupyterHub instance that has already been set up. If you are a USGS Water Mission Area (WMA) employee, you have a few
options for accessing a JupyterHub instance. These are described below, and more detailed instructions to set each option up are included in the hyperlinked name of the environment:
1) [pangeo.chs.usgs.gov](QuickStart-Cloud-pangeoCHS.md)<br>
   This JupyterHub instance is currently deployed on USGS's AWS account, and any USGS employee
   can request access to this space. Once you are added, the url will take you to your own
   personal JupyterHub space. The files in this space are only visible/accessible to the user
   who created them, so you will need to push them to a shared repository to work collaboratively.
   You will also have access to a shared set of kernels that are managed by USGS's Cloud Technologies
   (CTek) team in the Enterprise Technology Office (ETO). Anyone can put in a request to update these 
   shared kernels, but sometimes the update process can take several weeks.
2) [Nebari](QuickStart-Cloud-Nebari.md)<br>
   The HyTEST project has successfully deployed an instance of [Nebari](https://www.nebari.dev/) JupyterHub in the USGS cloud account. Nebari includes both a private (per user) and shared file space in the JupyterHub environment. Any user can also quickly modify and update a set of shared kernels so that all members of a team can use the same development environment. HyTEST will allow some of our priority users to test their workflows in this space; please contact Amelia Snyder (asnyder@usgs.gov) if you would like to request access to this space. The HyTEST team is currently working on developing instructions for how your project can deploy its own instance of Nebari JupyterHub in the USGS cloud. 
3) Your own JupyterHub Instance<br>
   Your can also work with your own deployment of a JupyterHub environment. You will need to make sure you have a kernel with all of the required packages set up to run these notebooks.


## USGS HPC Environment (only avaialble to USGS staff)

While we prioritize the development of workflows to run on "_cloud_" infrastructure, we also provide some guidance for running them on USGS's supercomputers. First, make sure you have an account on Denali or Tallgrass. We recommend accounts on both systems, as at times compute nodes may be unavailable on one system or the other. To get an account, fill out the [request form](https://hpcportal.cr.usgs.gov/hpc-user-docs/index.html#getting-started) and wait for approval (this may take a day or so).

Note that to access any of the HPCs, you must be on the DOI Network. If you are not in the office, use Ivanti Secure to access the VPN.

You will need to access an enviroment which emulates the Jupyter server -- where the notebooks will reside and execute -- using the HPC hardware. There are many ways to do this. Here are three options, in increasing order of complexity and flexibility:

1) [Open OnDemand](OpenOnDemand.md)<br>
   This option provides the most effortless access to HPC hardware using a web interface. However, this only runs on the [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html) and [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html) supercomputers.
2) [Jupyter Forward](JupyterForward.md)<br>
   This option gives you more control over how to launch the server, and on which host (can be run on [`Denali`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/denali.html), [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html), [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html), or other hosts to which you have a login). This setup requires that you install the jupyter-forward software on your PC.
3) [Custom Server Script](StartScript.md)<br>
   This option lets you completely customize your HPC compute environment and invoke the Jupyter server from a command shell on the HPC. This requires familiarity with the HPC command line, file editing, etc. This (can be run on [`Denali`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/denali.html), [`Tallgrass`](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html), [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html), or other hosts to which you have a login).