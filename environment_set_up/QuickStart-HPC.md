# Quick-Start for HPC

This document will help you set up the correct computing environment on a compute
server (an HPC node), and access the notebooks on the HPC via your local desktop.

This document assumes that you already have an access to either the `Denali` or `Tallgrass` [supercomputers at USGS](https://hpcportal.cr.usgs.gov/hpc-user-docs/index.html) and are comfortable using the command line.

The Process:

* Configure Software Environment on Denali/Tallgrass
    * Install Conda
    * Install software packages
    * Modify account configuration
* Install `jupyter-forward` on your PC
    * Install conda (if you don't already have it)
    * Add jupyter-forward


## 1) Configure the Software Environment on Denali/Tallgrass

This should only need to be done once. After you have the necessary
configuration established in this step, you should be able to do
future work by invoking a command on your PC.

### 1.a) Download HyTEST Materials to HPC Account

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

### 1.b) Install `conda` to your HPC user space.

Conda is a software package and dependency manager, similar in spirit to the `modules`
which allow custom configurations on the HPC.  Conda is best set up in your home
folder/directory on the HPC login node per the
[instructions](https://hpcportal.cr.usgs.gov/training/courses/Parallel_Python/Installing_parallel_packages.html#miniconda)
from ARC / HPC center.

* Download the latest miniconda installer:<br>
  Note: the ARC instructions take an explicit approach to finding the latest
    version.  The following link attempts to shortcut that:

```text
> wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
...
```

* You should now have a copy of `Miniconda3-latest-Linux-x86_64.sh`.  Run it:

```text
> bash Miniconda3-latest-Linux-x86_64.sh
...
```

Accept defaults for location.  But it is **very important** that you not allow
the installer to run an `init` to modify  your  login shell configuration. We
need to do that in a very specific way ourselves (see below). Answer _no_ when asked
if the installer should `init` for you.

### 1.c) Create a HyTEST-specific conda environment

[Conda] will automate much of the software downloading
and configuring to satisfy software prerequisites to run HyTEST notebooks.
The `HyTEST.yml` environment definition file will allow conda to do that all
at once:

```text
> source ~/miniconda3/bin/activate
> conda env create -f ./environment_set_up/HyTEST.yml
...
...
```

* The `source` command activates the conda environment manager
* The next command creates a new environment using the specified `.yml`.

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
for information about editing files.

Note that your `.bashrc` is an extremely important file which is consulted
every time you log in to the system.  If it gets broken in some way, you may need
admin help to fix it.  Be careful.

### 1.e) Test
Log out, then back in to Denali.  You should now be able to activate the
hytest environment with a command such as:

```text
> source activate hytest
```

## 2) Install `jupyter-forward` on your PC
This is a one-time operation to get the right software on your desktop.

The [jupyter-forward](https://pypi.org/project/jupyter-forward/) software will
wrap up a series of commands
necessary to to execute a jupyter server on the HPC host we just configured. It
is a convenience package intended to make HPC-based jupyter servers easy.

### 2.a) You need python

You will need to have python installed on your PC, along with either `pip` or
`conda` to help manage the python environments. We recommend anaconda.
You can request anaconda from IT,
or you can download the installer from [anaconda.com](https://www.anaconda.com/)
to install it in user spaced (admin is not required).

### 2.b) Install

python -m pip install jupyter-forward
```
conda install -c conda-forge jupyter-forward
```

## 3) Launch Server
With all of that set up, you are now ready to launch a session on the HPC using
`jupyter-forward` on your PC. Do this every time you would like to run notebooks
housed on the HPC host.

* Launch an `Anaconda Shell` from your start menu
* Run `jupyter-forward --conda-env=hytest denali`

## 4) Shut Down Server

After a daily session, you will want to shut down the jupyter server.
In the terminal session where you started `jupyter-forward`, merely press Ctl-C
to signal the server to shut down.
