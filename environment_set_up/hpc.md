# Getting started with Pangeo with on-prem HPC 

This tutorial covers how to set up and use the Pangeo  Environment on USGS High Performance Computing (HPC) systems:

1.  Installing [conda](https://conda.io/docs/) and creating a custom Hytest conda environment 
2.  Configuring [Jupyter](https://jupyter.org/)
3.  Launching [Dask](https://dask.pydata.org/) with a job scheduler
4.  Launching a [Jupyter](https://jupyter.org/) server 
5.  Connecting to [Jupyter](https://jupyter.org/) and the
    [Dask](https://dask.pydata.org/) dashboard from your personal
    computer

This document assumes that you already have an
access to Denali and Tallgrass and are comfortable using the command
line. 

## Installing a software environment

First log into Denali or Tallgrass.  You will need to be on doi.net to assess these systems, so if you are remote you will need to use the VPN (Pulse Secure) or login to an AWS Workspace machine (if you have one).  

After logging in, request interactive access to a compute node so that you are not working on the main node. You can do this either by entering a "salloc" command similar to the following, or by creating a script containing the command in your `~/bin` directory:
```bash
#!/bin/bash
salloc -A woodshole -t 02:00:00 -N 1 srun --pty bash
```
which when executed, requests a node for 2 hours using the "woodshole" account.  You need to use your account name and adjust the time accordingly. (Note that at times a node with the requested resources will not be available and you will receive a "request pending" message; if this happens and you don't want to wait for the node, you can quit the command, logout, and try a different HPC machine.)

Next install the Conda package managment system to allow generation of self-contained Python environments without involving system admins. We will install "Mamba", which is a drop drop-in replacement for "conda" providing a fast, efficient and license-free way to run conda commands.  Copy and paste these lines to the terminal:

```bash
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-$(uname)-$(uname -m).sh"

bash Mambaforge-$(uname)-$(uname -m).sh

export PATH=$HOME/mambaforge/bin:$PATH
```
For the bash command, answer "yes" to accept the license agreement. For the next prompt either hit Enter to confirm, or specify a different location. And then answer "yes" when it asks if you want the script to run `conda init`. 

Now update your conda package manager with packages from the conda-forge channel:

```bash
conda config --add channels conda-forge --force 
mamba update --all
```
This will create a ``.condarc`` configuration file in your home
directory with the `conda-forge` channel setting. 

Now let's create a new conda environment for our HyTest work:
```bash
mamba create -n pangeo -c conda-forge \
      python dask jupyterlab dask-jobqueue ipykernel ipywidgets \
      xarray zarr numcodecs hvplot geoviews datashader xesmf \
      jupyter-server-proxy widgetsnbextension dask-labextension intake-xarray
```
*Note: you can add additional conda packages you need to this list.  Packages available through conda-forge can be explored at https://anaconda.org. 

Activate this environment:
```bash
conda activate pangeo
```
Your prompt should now look something like this (note the "pangeo" environment name):
```
(pangeo) $
```

And if you ask where your Python command lives, it should direct you to somewhere in your home directory:
```
(pangeo) $ which python
$HOME/mambaforge/envs/pangeo/bin/python
```
## Configure Jupyter

Jupyter notebook servers include a password for security. First we generate the Jupyter config file then set a password:
```
jupyter server --generate-config
jupyter server password
```
This creates the file `~/.jupyter/jupyter_server_config.py`. 

Finally, we configure dask\'s dashboard to forward through
Jupyter.  Add the following line to your `~/.bashrc` file (text editors include vi and nano):
```
export DASK_DISTRIBUTED__DASHBOARD__LINK="/proxy/8787/status"
```
------------------------------------------------------------------------



### Start a Jupyter Notebook Server

Now that we have Jupyter configured, we can start a notebook server on our interactive compute node.  First we can create a script like the one below.  Using a text editor such as vi or nano, open a file named "start_jupyter" in your ~/bin directory; then copy and paste the text below into the file. Be sure to change "$HOME/HyTest/Projects" to your own directory path, as appropriate, and then save the file.

```bash
(pangeo) rsignell@nid00243:~> more ~/bin/start_jupyter

#!/bin/bash
source activate pangeo
cd $HOME/HyTest/Projects
HOST=`hostname`
JPORT=$(shuf -i 8400-9400 -n 1)
echo ""
echo ""
echo "Step 1: Wait until this script says the Jupyter server"
echo "        has started. "
echo ""
echo "Step 2: Copy this ssh command into a terminal on your"
echo "        local computer:"
echo ""
echo "        ssh -N -L 8889:$HOST:$JPORT  $USER@$SLURM_CLUSTER_NAME.cr.usgs.gov"
echo ""
echo "Step 3: Browse to http://localhost:8889 on your local computer"
echo ""
echo ""
jupyter lab --no-browser --ip=$HOST --port=$JPORT
```
Now make your script executable and run it:
```
(pangeo) $ chmod u+x ~/bin/start_jupyter
(pangeo) $ start_jupyter
```
Follow the Steps 1,2,3 printed out by the script to get connected. Note that after you login using the ssh command in Step 2, the cursor will hang.  This is expected and you can minimize the window.

### Launch Dask with dask-jobqueue

Most HPC systems use a job-scheduling system to manage job submissions
and executions among many users. The
[dask-jobqueue](http://dask-jobqueue.readthedocs.io) package is designed to help dask interface with these job queuing systems. Usage is quite simple and can be done from within your Jupyter Notebook:

```python
from dask_jobqueue import SLURMCluster

if os.environ['SLURM_CLUSTER_NAME']=='tallgrass':
    cluster = SLURMCluster(processes=1,cores=1, 
        memory='10GB', interface='ib0',
        project='woodshole', walltime='04:00:00',
        job_extra={'hint': 'multithread', 
        'exclusive':'user'})

cluster.scale(18)

from dask.distributed import Client
client = Client(cluster)
```

The `scale()` method submits a batch of jobs to the SLURM job
queue system.  Depending on how busy the job queue is,
it can take a few minutes for workers to join your cluster. You can usually check the status of your queued jobs using a command line
utility like [squeue -u $USER. You can also check the status of your cluster from inside your Jupyter session:

``` python
print(client)
```

For more examples of how to use
[dask-jobqueue](http://dask-jobqueue.readthedocs.io), refer to the
[package documentation](http://dask-jobqueue.readthedocs.io).


## Further Reading

 -   [Deploying Dask on HPC](http://dask.pydata.org/en/latest/setup/hpc.html)
 -   [Configuring and Deploying Jupyter Servers](http://jupyter-notebook.readthedocs.io/en/stable/index.html)

