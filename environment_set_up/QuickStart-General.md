# QuickStart 

The HyTEST workflows are built largely on the [Pangeo](https://pangeo.io/) 
software stack. For general advice, you should start with Pangeo's 
[Deployment Setup Guides](https://pangeo.io/setup_guides/index.html)
and select an option which resembles your compute environment.

The usual sticking points are to do with
* Getting the virtual environment correct
* Launching a Jupyter server

## Virtual Environment

We definitely recommend `conda` (or its functional equivalent, `mamba`)
as the environment configuration tool.  The software stack we use is 
defined in 
[this environment file](https://raw.githubusercontent.com/hytest-org/hytest/main/environment_set_up/HyTEST.yml). 

Use `conda` to create an environment called `hytest` with this command: 

```text
conda env create -f ./HyTEST.yml
```

While is is possible to run most of these workflows on a desktop system, 
they have been developed to run on a Linux variant.  This will affect which
versions and which architectures of the various software packages are 
installed. 

## Jupyter Server
The Jupyter server is the harder problem to solve -- primarily because 
there are so many variables and options to consider when setting it up. 
The Pangeo docs cover a few of the options, and the [Jupyter](https://jupyter.org/)
docs also give some help for setting up. These deploytments, generally, 
are meant for a single user to run notebooks on a semi-private host. 

If multiple users will be using the same server, consider deploying a
[Jupyter Hub](https://jupyter.org/hub) on a centralized computing host.


