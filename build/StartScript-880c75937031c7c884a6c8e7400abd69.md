# HPC Server: Start Script Quick-Start

Use this option if you would like more control over the allocation request and the environment in
which the jupyter server runs. This option requires that you log into the HPC host to run a custom
script.  Copy [this example](./jupyter-start.sh) and edit to your liking.

Launching in this way will start your custom jupyter server and plumb the port forwarding necessary
to make it available to your desktop web browser.

1) Open a terminal window and log in to your HPC host. If you do not know how to do this, you can consult the [HPC User Docs](https://hpcportal.cr.usgs.gov/hpc-user-docs/guides/connecting/ssh.html).
2) [Clone](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository) the [hytest repository](https://github.com/hytest-org/hytest) into the directory you want to work in.
3) Request a compute node with a command like `salloc -A impd -t 1:00:00 -N 1 srun --pty bash`. If you are not in the `impd` group, you will need to replace `impd` with a group you are a part of. You may also need to update the number of hours you want to have access to the compute node (in this example, we are requesting 1 hour).
4) Navigate into the environment_set_up directory (`cd environment_set_up/`) and execute the [jupyter-start.sh](./jupyter-start.sh) script (`bash jupyter-start.sh`).
5) The `jupyter-start.sh` script will direct you on how to start port forwarding (that's the `ssh` command that you are directed to run from a new terminal on your desktop). You will want to open a new terminal window on your local computer an run this command. If prompted, log in with your AD username and password. The cursor will hang after entering your password. This is expected - you can minimize this window and move on to the next step.
6) The output of the script will also provide the URL where your PC's browser will find the jupter server. You can open one of these urls in your browser. 

Now you are set up with a Jupyter server connected to the HPC you logged in to.

This option can be useful if you want to build your own conda environment, rather than using the provided
HyTEST environment. The central HyTEST environment is built using [this](https://raw.githubusercontent.com/hytest-org/hytest/main/hytest.yml) environment definition. We recommend that you
use it as the baseline if you will be building your own environment.

If you choose to do that, you will want to edit the `jupyter-start.sh` script to reflect
the particulars of your custom conda environment.
