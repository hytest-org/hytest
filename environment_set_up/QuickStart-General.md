# General QuickStart

## Jupyter Server
If you are working in an environment that already has a pathway to run Jupyter notebooks, you will not need to worry about this section. You will simply launch the Jupyter notebook in whatever way you know how.

If you do need to set up your own Jupyter server, this is a harder problem to solve -- primarily because 
there are so many variables and options to consider when setting it up. The [Jupyter](https://jupyter.org/)
docs give some help for setting up; however, these deployments, generally, are meant for a single user to run notebooks on a semi-private host. 

If multiple users will be using the same server, consider deploying a [Jupyter Hub](https://jupyter.org/hub) on a centralized computing host. There are many resources online for deploying a JupyterHub, including:
1. [Building multi-tenant JupyterHub Platforms on Amazon EKS](https://aws.amazon.com/blogs/containers/building-multi-tenant-jupyterhub-platforms-on-amazon-eks/)
2. [Microsoft Planetrary Computer's Guide: Deploy your own JupyterHub](https://planetarycomputer.microsoft.com/docs/concepts/hub-deployment/)

## Virtual Environment

We recommend `conda` (or its functional equivalent, `mamba`) as the environment configuration tool. If you are a USGS Staff Member, you will want to install [miniforge](https://conda-forge.org/download/), which includes conda and mamba.

The HyTEST workflows are built largely on the [Pangeo](https://pangeo.io/) software stack. The software stack we use is defined in [this environment file](https://raw.githubusercontent.com/hytest-org/hytest/main/hytest.yml). 

Use `conda` to create an environment called `hytest` with this command: 

```text
conda env create -f ./hytest.yml
```

You will then need to select the `hytest` environment as your kernel when you try to run the notebook.

While is is possible to run most of these workflows on a desktop system, they have been developed to run on a Linux variant.  This will affect which versions and which architectures of the various software packages are installed.