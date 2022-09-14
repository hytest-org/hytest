# Getting Started with On-Prem HPC

This tutorial covers how to set up and use the Pangeo environment/stack
on  USGS High Performance Computing (HPC) systems:

1) Creating a custom hytest conda environment
2) Configuring [Jupyter](https://jupyter.org/) server
3) Launching a Jupyter server
4) Connecting to your Jupyter server and the[Dask](https://dask.pydata.org/) 
   dashboard from your personal computer

This document assumes that you already have an access to
Denali and Tallgrass and are comfortable using the command line.

## Installing a Conda Software Environment

This is the same manual process as describe in the 
[Quick-Start for HPC](./QuickStart-HPC.md)

## Configure Jupyter

Jupyter notebook servers include a password for security. First we generate the Jupyter config file then set a password:

```text
jupyter server --generate-config
jupyter server password
```

This creates the file `~/.jupyter/jupyter_server_config.py`.

Finally, we configure dask\'s dashboard to forward through
Jupyter.  Add the following line to your `~/.bashrc` file:

```sh
export DASK_DISTRIBUTED__DASHBOARD__LINK="/proxy/8787/status"
```

## Start a Jupyter Notebook Server

Now that we have Jupyter configured, we can start a notebook server on our interactive compute node. Use the [script provided](./start_jupyter.sh) to do this.

```text
> salloc -A account_name -t 02:00:00 -N 1 srun --pty bash
> cd $HOME/HyTEST-Tutorials/
> ./HPC/start_jupyter.sh
```

Follow the steps printed out by the script to get connected. Note that after you login using the `ssh` command in Step 2, the cursor will hang.  This is expected and you can minimize the window.

## Running Notebooks

### Special Notes for dask jobqueue

Most HPC systems use a job-scheduling system to manage job submissions
and executions among many users.
The [dask-jobqueue](http://dask-jobqueue.readthedocs.io) package is designed to help
dask interface with these job queuing systems. Usage is quite simple and can be done
from within your Jupyter notebook. See
[this doc](../Syllabus/L2/xx_dask-jobqueue.ipynb) for dask-specific details and how
to interact with `dask-jobqueue` from within your notebook.
