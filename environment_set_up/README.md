# HPC Environment

While these tutorial notebooks are intended for use on "_cloud_" infrastructure, it is possible to run them
on HPC hardware also.  Some notebooks will need modifications specific to the compute cluster hardware.
More importantly, you will also need to access an enviroment which emulates the Jupyter server -- where the
notebooks will reside and execute -- using the HPC hardware. There are many ways to do this. Here are three
options, in increasing order of complexity and flexibility:

1) [Open OnDemand](./OpenOnDemand.md)<br>
   Provides the most effortless access to HPC hardware using a web interface (not unlike the
   ESIP/QHUB interface). Only runs on `tallgrass`.
2) [Jupyter Forward](./JupyterForward.md)<br>
   This option gives you more control over how to launch the server, and on which host (can be
   run on `denali`, `tallgrass`, or other hosts to which you have a login).  Requires that you
   install an extra bit of software on your PC.
3) [Custom Server Script](./StartScript.md)<br>
   This option lets you completely customize your HPC compute environment and invoke the Jupyter
   server from a command shell on the HPC. Requires familiarity with the HPC command line, file
   editing, etc.

If your workflow makes use of parallelism using Dask on HPC hosts, read [this](./tallgrass_dask-jobqueue.md)
for information about how to configure the Slurm job scheduler within your notebook.