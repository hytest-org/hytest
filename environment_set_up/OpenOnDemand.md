# HPC Server: Open OnDemand Quick-Start

This is a custom service provided by the USGS ARC team that is available to **anyone who has an account on the USGS high performance computers (HPCs)**. If you are a **USGS staff member** who does not yet have an account on the HPCs, you can request one [here](https://hpcportal.cr.usgs.gov/index.html). Once your USGS HPC account has been created, you will be able to follow the instructions below to use this service.

This is the easiest option for running Jupyter notebooks on the HPCs, as there is no configuration needed on your part. This option provides reasonable compute resources via the `tallgrass` and `hovenweep` HPC hosts:

* To log in to OnDemand, select the appropriate login link from the `OnDemand` section of the [HPC User Docs](https://hpcportal.cr.usgs.gov/). Note that you must be on the USGS VPN to access this host. Denali/Tallgrass share one disk for data storage and Hovenweep has a different disk. If you have data stored on the HPCs, you will want to choose whichever resource is attached to where your data is stored. If you are accessing data from a different, publicly accessible storage location, you can choose either option.
* From the OnDemand landing page, choose `Interactive Apps`. If you are using `Hovenweep`, select the `Jupyter` option from this dropdown. If you are using `Tallgrass`, you can either select `Jupyter` or you can launch the `HyTEST Jupyter` server app, which will include a conda environment pre-configured with the packages you need to run the workflows in this JupyterBook. If you do not use our pre-configured environment (if you selected `Jupyter`), you will need to build your own once your connect to the HPC. This process is described below in [Conda Environment Set Up](#Conda Environment Set Up).
* Fill in the form to customize the allocation in which the Jupyter Server will execute.
  * For light duty work (i.e. tutorials), a `Viz` node is likely adequate in your allocation request.  If you
will be doing heavier processing, you may want to request a compute node.  None of the HyTEST tutorials
utilize GPU code; a GPU-enabled node is not necessary.
  * You may want to consider adding the git and/or aws modules if you plan to use them during your session. You will just need to type `module load git` and/or `module load aws` in the `Module loads` section.
  * If you expect to run code in parallel on multiple compute nodes, you have two options. (1) You can use the form to request the number of cores you need and then run a [Dask Local Cluster](./Start_Dask_Cluster_Denali.ipynb) on those cores, or (2) you can request the standard 2 cores, and then use a [Dask SLURMCluster](./Start_Dask_Cluster_Tallgrass.ipynb) to submit new jobs to the SLURM scheduler, giving you access to additional compute nodes. Please see the HPC docs to learn more about the available compute and memory resources for [Tallgrass](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/tallgrass.html) and [Hovenweep](https://hpcportal.cr.usgs.gov/hpc-user-docs/supercomputers/hovenweep.html).
* Click Submit
* Once your server is ready, a `Connect to Jupyter` button will appear that you can click to start your session.

The Jupyter Server will run in an allocation on `tallgrass` or `hovenweep`. This server will have access to your home
directory/folder on that host, which is where your notebooks will reside.
 
## Conda Environment Set Up
If you need to set up your own conda environment to run the notebooks, proceed with the following steps:
* make sure you have the [HyTEST environment file](../hytest.yml) uploaded to the HPCs. You can manually upload just this file, or you can clone the [HyTEST repository](https://github.com/hytest-org/hytest), which contains this file.
* load the conda module with `module load conda`
* navigate in to the directory containing the environment yaml file from step 1, and create the hytest environment with `conda env create -f hytest.yml`
* activate your environment with `conda activate hytest`
* create kernel of hytest environment by running `python -m ipykernel install --user --name hytest --display-name "hytest"`

Now, you will be able to see the environment you just built as an available kernel from your Jupyter notebook.

For additional help setting up and using conda environments on the HPCs, please see the [HPC User Docs](https://hpcportal.cr.usgs.gov/hpc-user-docs/guides/software/environments/python/conda.html).

*Note: The code to build the HyTEST Jupyter app is in [this repository](https://code.chs.usgs.gov/sas/arc/arc-software/ood/bc_jupyter_hytest); however, this repo is only visible on the internal USGS network.*

## Dask Dashboard
If you plan to use the dask dashboard with OnDemand, you will need to launch your interactive session in a conda environment that includes the `dask_labextension` package. If you are using the HyTEST environment provided in the [hytest.yml] file in our repository, we have included this package. You will just need to choose the hytest environment when you are launching your interactive session (after you have built it).