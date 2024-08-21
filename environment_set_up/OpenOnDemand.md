# HPC Server: Open OnDemand Quick-Start

This is a custom service provided by the USGS ARC team. It is the easiest to use (no configuration needed on your part), and provides reasonable compute resources via the `tallgrass` and `hovenweep` hosts:

* To log in to OnDemand, select the appropriate login link from the `OnDemand` section of `https://hpcportal.cr.usgs.gov/`. Note that you must be on the VPN to access this host. Denali/Tallgrass share one disk for data storage and Hovenweep has a different disk. If you have data stored on the HPCs, you will want to choose whichever resource is attached to where your data is stored. If you are accessing data from a different, publicly accessible storage location, you can choose either option.
* From the OnDemand landing page, choose `Interactive Apps`. If you are using `Hovenweep`, select the `Jupyter` option from this dropdown. If you are using `Tallgrass`, you can either select `Jupyter` or you can launch the HyTEST Jupyter Server app, which will include a conda environment pre-configured with the packages you need to run the workflows in this JupyterBook. If you do not use our pre-configured environment, you will need to build your own. You can learn more about how to set up your own conda environment [here](https://hpcportal.cr.usgs.gov/hpc-user-docs/guides/software/environments/python/Python_Environment_Setup_with_Conda.html) in the HPC user docs.
* Fill in the form to customize the allocation in which the Jupyter Server will execute. You may want to consider adding the git and/or aws modules if you plan to use them during your session. You will just need to type `module load git` and/or `module load aws` in the `Module loads` section.
* Submit
* Once your server is ready, a `Connect to Jupyter` button will appear that you can click to start your session.

The Jupyter Server will run in an allocation on `tallgrass` or `hovenweep`. This server will have access to your home
directory/folder on that host, which is where your notebooks will reside.

For light duty work (i.e. tutorials), a `Viz` node is likely adequate in your allocation request.  If you
will be doing heavier processing, you may want to request a compute node.  None of the HyTEST tutorials
utilize GPU code; a GPU-enabled node is not necessary.

##### Note: The code to build this app is in [this repository](https://code.chs.usgs.gov/sas/arc/arc-software/ood/bc_jupyter_hytest); however, this repo is only visible on the internal USGS network.