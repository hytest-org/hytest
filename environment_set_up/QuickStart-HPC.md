# Quick-Start for HPC

This document will help you set up the correct computing environment on a compute
server (an HPC node), and access the notebooks on the HPC via your local desktop.

This document assumes that you already have an access to either the `Denali` or `Tallgrass` [supercomputers at USGS](https://hpcportal.cr.usgs.gov/hpc-user-docs/index.html) and are comfortable using the command line.

## 1) Configure the Software Environment

This should only need to be done once. After you have the necessary
configuration established in this step, you should be able to do
future work by only doing steps
**2** ([starting a server](#2-start-the-jupyter-server)), and
**3** ([running your notebooks](#3-run-notebooks)) for your routine workflow.

This software environment refers to steps taken to configure the HPC host.

### 1.a) Download Materials to HPC Account

* Log in to the HPC machine
* Run this command:

```text
curl -s -L https://github.com/hytest-org/hytest/releases/latest/download/hytest.tar.gz | tar zxf -
```

You should now have a new directory, `hytest` into which this archive has
been placed.

```text
> cd hytest
> ls -l
...
```

### 1.b) Set Up a `hytest` Conda Environment

Most of the software we will use can be managed in a virual environment, managed
by `conda` (<https://docs.conda.io/en/latest/>).  This environement management tool
is not provided on `denali` or `tallgrass`, so you'll need to set it up yourself.

* `wget https://repo.anaconda.com/miniconda/Miniconda3-py39_4.12.0-Linux-x86_64.sh`
* `bash Miniconda3-py39_4.12.0-Linux-x86_64.sh`<br>
   follow the prompts, accepting default answers **EXCEPT** you must not let it 
   `init` your login shell.  When asked about this task, answer 'no'.
*  `rm Miniconda3-py39_4.12.0-Linux-x86_64.sh`
*  `source ${HOME}/miniconda3/bin/activate`

A baseline `conda` is now installed in your home folder (this home folder is
shared between `tallgrass` and `denali`...  you need do this only on one host
for it to be available to both).  With `conda` now available, we can ask it to
find and install all of the software HyTEST needs for running notebooks out
of a Jupyter server.  

Use the provided `HyTEST.yml` environment definition file
as the input specification to create a new environment which includes the necessary software:

```text
> conda env create -f ./environment_set_up/HyTEST.yml
...
...
```
This command will take some time to run.  In the end, you will have two 
virtual environments in your HPC accounts:  '_base_' and '_hytest_'.  We won't 
need the base installation, and will focus on the hytest environment for 
everything else we need to do. 

### 1.c) Configure Jupyter Server

The Jupyter Server is the element which will actually run the notebooks on the HPC, but
which display in a remote (i.e. your desktop) web browser.  We have an auto-configuration
script which will help with this configuration. Run:

```text
> ./environment_set_up/auto-conf.py
Set the access password for connecting to this Jupyter Server...
Enter password:
Verify password:
...
```

The password you supply will be used when you attempt to connect to the
Jupyter server from your local web browser.

Note that this `auto-conf.py` script handles a lot of
configuration that you need only do once. It writes a configuration
file to `$HOME/.jupyter/jupyter_server_config.json`, which will simplify
the process of starting the server in future steps.

If you need (or want) to deviate from the vanilla set-up created by
`auto-conf.py` you can find more detailed information for setting up
manually [here](ManualConfig-HPC.md)

With that, your jupter server and its necessary environment should be set.

## 2) Start the Jupyter Server

The computation and data access will run on the compute node, and render
results via web connection to the browser on your desktop. This model
uses a 'server' process on the HPC in order to coordinate that connection.

Start Jupyter Server on an interactive compute node

```text
> salloc -A account_name -t 02:00:00 -N 1 srun --pty bash
> conda activate hytest
> jupyter lab
```

`account_name` is one of your accounts codes on the supercomputer. You will see a list of your account codes when you first log in to the supercomputer. They are listed in a table after some text saying `Your account codes are:`.

**NOTE** If you chose to configure more [manually](./ManualConfig-HPC.md),
you may need to supply extra options to that `jupyter lab` command, or use the
`start_jupyter.sh` example script we've provided for that purpose.

## 3) Run Notebooks

You are now ready to connect a web browser to your jupyter server.  Launch
a web browser on your dekstop and connect to the URL provided in the
startup messaging when you launched `jupyter lab`.

> NOTE:  Don't use the `localhost` option.  Use the URL which includes
your HPC host's full network name. That should look something like
<kbd>https://denali:8402/</kbd>.

The Jupyter Server will ask for a password.  This is the one supplied
in [Step 1c](#1c-configure-jupyter-server) above.

You can now run existing notebooks found in `hytest`, or create
your own.

## 4) Shut Down Server

After a daily session, you will want to shut down the jupyter server.
In the terminal session where you started `jupyter lab`, merely press Ctl-C
to signal the server to shut down.
