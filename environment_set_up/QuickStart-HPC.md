# Quick-Start for HPC

This document will help you set up the correct computing environment on a compute
server, and access the notebooks on your local desktop.

## 1) Configure the software environment

This should only need to be done once. After you have the necessary
configuration established in this step, you should be able to do
future work by only doing steps
**2** ([starting a server](#2-start-the-jupyter-server)), and
**3** ([running your notebooks](#3-run-notebooks)) for your routine workflow.

This software environment refers to steps taken on the HPC host.

### 1.a) Download materials to HPC account

* Log in to the HPC machine
* Run this command:

```text
curl -s -L 'https://github.com/USGS-python/hytest_notebook_tutorials/releases/latest/download/HyTEST-Tutorials.zip' | tar xvf -
```

> **NOTE**: The above URL is a placeholder until we get set up with our release schedule and standards.  It is not likely to work yet.

You should now have a directory, `hytest` into which this archive has
been placed.

```text
> cd hytest
> ls -l
...
```

### 1.b) Set up a `hytest` Conda environment

> **NOTE**: We are using 'hytest' as the environment name.  If you need to use
another name, you'll need to make some adjustments to the
[environment file](./HPC/HyTest.yml).

Conda is a package manager -- it will automate much of the software downloading
and configuring that we will need to run these notebooks. Use the `HyTEST.yml` environment definition file as the input specification to create a
new environment which includes the necessary software:

```text
> conda env create -f ./HPC/HyTest.yml
...
...
```

> **NOTE**: We're using the `conda` given to us from the sysadmin. You may
see other conda-like replacements used on other environments (`mamba` is a popular
one).  They are functionally equivalent for what we need to do here.

### 1.c) Configure Jupyter Server

The Jupyter Server is the element which will actually run the notebooks
which display in a remote (i.e. your desktop) web browser.  We have an auto-configuration script which will help with this configuration. Run:

```text
> ./environment_set_up/auto-conf.sh
Set the access password for connecting to this Jupyter Server...
Enter password:
Verify password:
...
```

The password you supply will be used when you attempt to connect to the
Jupyter server from your local web browser.

Note that this <kbd>auto-conf.py</kbd> script handles a lot of
configuration that you need only do once. It writes a configuration
file to `$HOME/.jupyter/jupyter_server_config.json`, which will simplify
the process of starting the server in future steps.

If you need (or want) to deviate from the vanilla set-up created by
`auto-conf.py` you can find more detailed information for setting up
manually [here](./HPC/ManualConfig.md)

With that, your jupter server and its necessary environment should be set.

## 2) Start the jupyter server

Start Jupyter Server on an Interactive Compute Node

```text
> salloc -A account_name -t 02:00:00 -N 1 srun --pty bash
> conda activate hytest
> jupyter lab
```

<kbd>account_name</kbd> is your account credential/name

**NOTE** If you chose to configure more [manually](./HPC/ManualConfig.md),
you may need to supply extra options to that `jupyter lab` command.

## 3) Run Notebooks

You are now ready to connect a web browser to your jupyter server.  Launch
a web browser on your dekstop and connect to the URL provided in the
startup messaging when you launched `jupyter lab`.

> NOTE:  Don't use the `localhost` option.  Use the URL which includes
your HPC host's full network name. That should look something like
<kbd>https://denali:8402/</kbd>.

The Jupyter Server will ask for a password.  This is the one supplied
in [Step 1c](#1c-configure-jupyter-server) above.

You can now run existing notebooks found in `hytest` , or create
your own.

## 4) Shut Down Server

After a daily session, you will want to shut down the server. In the
terminal session where you started `jupyter lab`, merely press Cntl-C
to signal the server to shut down.
