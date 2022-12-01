# Quick-Start for HPC

This document will help you set up the correct computing environment on a compute
server (an HPC node), and access the notebooks on the HPC via your local desktop.

These instructions are **DEPRECATED**.  The simplest options are to use one of these
methods:
* [OnDemand](./OpenOnDemand.md)
* [jupyter-forward](./JupyterForward.md)
* A [Start Script](./StartScript.md) from the HPC command prompt


If none of those methods works for you, it is possible to install your own
conda and virtual environments within the home directory on the HPC.

## The Configuration Process

An overview of the steps you will be taking:
  * Install Conda
  * Install software packages
  * Modify account configuration to recognize the above

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

## Launching the Server

You can now use your custom environment to launch a jupyter server within an
allocation.  While it is possible to run this from one of the login nodes, that
should only be done for the lightest of workloads.

To shart your custom jupyter server and environment, you'll want to modify
your own copy of the [jupyter-start.sh](./jupter-start.sh) script to utilize
your conda, and not the one we've configured:

Comment out these lines:

```text
module use --append /caldera/projects/usgs/water/impd/hytest/modules
module load hytest
```

And un-comment these lines (making necessary changes to the path):

```text
# export PATH=/path/to/your/conda/bin:$PATH
# source activate envname
```
