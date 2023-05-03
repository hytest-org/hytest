# HPC Server: Start Script Quick-Start

Use this option if you would like more control over the allocation request and the environment in
which the jupyter server runs. This option requires that you log into the HPC host to run a custom
script.  Copy [this example](./jupter-start.sh) and edit to your liking.

Launching in this way will start your custom jupyter server and plumb the port forwarding necessary
to make it available to your desktop web browser.

1) Log in to your HPC host
2) Execute the [jupyter-start.sh](./jupter-start.sh) script
3) Follow its instructions

The `jupyter-start.sh` script will direct you on how to start port forwarding (that's the `ssh` command to run
from your PC's command prompt) and will provide the URL where your PC's browser will find the jupter server.

This option can be useful if you want to build your own conda environment, rather than using the provided
HyTEST environment. The [Pangeo docs](https://pangeo.io/setup_guides/hpc.html) are a good place to start
if you would like to set up your own environment using this start script.  The central HyTEST environment
is built using [this](./HyTEST.yml) environment definition. We recommend that you
use it as the baseline if you will be building your own environment.

If you choose to do that, you will want to edit the `jupyter-start.sh` script to reflect
the particulars of your custom conda environment.  See [here](./QuickStart-HPC.md) for
an example walk-through of that process.
