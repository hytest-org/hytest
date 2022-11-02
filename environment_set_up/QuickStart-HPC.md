# Quick-Start for HPC

This document will help you set up the correct computing environment on a compute
server (an HPC node), and access the notebooks on the HPC via your local desktop.

:::{NOTE}
The instructions here will configure your user account on the HPC hosts (Denali and Tallgrass)
to support a custom and personalized jupyter server. We are working to add another option more
similar to the JupyteHub web-only experience in the near future.  Until that happens, this is
our recommended path to start using Jupyter notebooks on the HPC.
:::

This document assumes that you already have an access to either the `Denali` or `Tallgrass`
[supercomputers at USGS](https://hpcportal.cr.usgs.gov/hpc-user-docs/index.html) and are
comfortable using the command line.

## The Configuration Process

An overview of the steps you will be taking:

* Configure Software Environment on Denali/Tallgrass
  * Install Conda
  * Install software packages
  * Modify account configuration to recognize the above
* Install `jupyter-forward` on your PC
  * Install conda (if you don't already have it)
  * Add jupyter-forward

-----

## 1) Configure the Software Environment on Denali/Tallgrass

This should only need to be done once. After you have the necessary
configuration established in this step, you should be able to do
future work by invoking a command on your PC.

### 1.a) Download HyTEST Materials to HPC Account

* Log in to the HPC machine
* Run this command:

```text
curl -s -L https://github.com/hytest-org/hytest/releases/latest/download/HyTEST_EnvSetUp.tar.gz | tar zxf -
```

You should now have a new folder/directory, `hytest`, into which this archive has
been unpacked.

```text
> cd hytest
> ls -l
...
```

### 1.b) Install `conda` to your HPC user space

Conda is a software package and dependency manager, similar in spirit to the
`modules` which allow custom configurations on the HPC.  Conda is best set
up in your home folder/directory on the HPC login node per the
[instructions](https://hpcportal.cr.usgs.gov/training/courses/Parallel_Python/Installing_parallel_packages.html#miniconda)
from ARC / HPC center.

* Download the latest miniconda installer:<br>
  Note: the ARC instructions take an explicit approach to finding the latest
    version.  The following link attempts to shortcut that:

```text
> wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
```

* You should now have a copy of the miniconda installer: `Miniconda3-latest-Linux-x86_64.sh`.<br>Run it:

```text
> bash Miniconda3-latest-Linux-x86_64.sh

```

Accept defaults for location.  But it is **very important** that you
<font style="color: red">**NOT**</font> allow
the installer to run an `init` to modify  your  login shell configuration.
We need to do that in a very specific way ourselves (see below). Answer _no_ when asked
if the installer should `init` for you.

### 1.c) Create a HyTEST-specific conda environment

[Conda] will automate much of the software downloading
and configuring to satisfy software prerequisites to run HyTEST notebooks.
The `HyTEST.yml` environment definition file will allow conda to do that all
at once:


```text
> source ~/miniconda3/bin/activate
> conda env create -f ./environment_set_up/HyTEST.yml
```


* The `source` command activates the conda environment manager
* The next command creates a new environment using the specified `.yml` definition file.

### 1d) Edit the `.bashrc`

We can now direct the login shell to always be able to find the conda
commands and environments. This requires an edit of the control file for
your shell.

Edit your `${HOME}/.bashrc` file to add the following as the last line:

```text
export PATH=${HOME}/miniconda3/bin:${PATH}
```

You can use any editor you like to do this (`nano`) or (`vi`). See
<https://hpcportal.cr.usgs.gov/training/courses/Intro_to_HPC/include_edit.html>
for information about editing files.  `vi` should be available for all users.
`nano` may not be enabled by default.  If you would prefer to use `nano`, it
may be necessary to `module load nano` in order to get access to it.

Note that your `.bashrc` is an extremely important config file which is consulted
every time you log in to either system (Denali or Tallgrass).  If it gets broken
in some way, you may need admin help to fix it.  Be careful.

### 1.e) Test

Log out, then back in to Denali.  You should now be able to activate the
hytest environment with a command such as:

```text
> source activate hytest
```

You are now fully configured on the server side. The next step is to set up on
your PC to auto-start that server when you want to do work.

### 1.f) Clean Up

As a last step on the HPC, it is useful to remove the installers and other intermediate
data used to configure your conda and jupyter environment.  You may remove the
`Miniconda3-latest-Linux-x86_64.sh` installer.  Also, execute `conda clean -t -y`
to instruct conda to clean up its temporary download files.

-----

## 2) Install `jupyter-forward` on your PC

This is a one-time operation to get the right software on your desktop.

The [jupyter-forward](https://pypi.org/project/jupyter-forward/) software will
wrap up a series of commands necessary to to execute a jupyter server on the
HPC host we just configured. It is a convenience package intended to make
HPC-based jupyter servers easy.

### 2.a) You need Python and Anaconda

You will need to have python installed on your PC, along with either `pip` or
`conda` to help manage the python environments. We recommend anaconda.
You can request anaconda from IT,
or you can download the installer from [anaconda.com](https://www.anaconda.com/)
to install it in user space (i.e. admin is not required).

### 2.b) Install

Launch an `Anaconda Shell` from your Start menu, then execute:

```text
> conda install -c conda-forge jupyter-forward
```

Let it do all of the installing it needs. Upon completion, your configuration should
be set for easy launching of Jupyter on the HPC.

-----

## 3) Launch Server

With all of that set up, you are now ready to launch a session on the HPC using
`jupyter-forward` on your PC. Do this every time you would like to run notebooks
housed on the HPC host.

* Launch an `Anaconda Shell` from your start menu
* Run `jupyter-forward --conda-env=hytest denali`

Note that this command will run the jupter server on the **login node** of Denali.
This is OK if your workload is light (i.e. for tutorials).  If you will be doing
heavier processing:

```text
jupyter-forward --launch-command "srun -A acctname -N 1 -t 02:00:00" --conda-env=hytest denali

```

Where `acctname` is the account code to use for the Slurm
job in which this server will run.

## 4) Shut Down Server

After a daily session, you will want to shut down the jupyter server.
In the terminal session where you started `jupyter-forward`, merely press Ctl-C
to signal the server to shut down.
