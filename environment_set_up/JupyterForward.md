# HPC Server: Jupyter Forward Quick-Start

This option will configure your HPC account to access the correct Jupyter server software.  That server
will be invoked by a command installed on your PC.  This option minimizes the configuration changes
needed on the HPC host, but still permits relatively easy access to that hardware via a personal Jupyter
Server.

## 1) Configure your HPC account to access the HyTEST [conda](https://www.anaconda.org) environment :

    * Open a terminal window and log in to your HPC host. If you do not know how to do this, you can consult the [HPC User Docs](https://hpcportal.cr.usgs.gov/hpc-user-docs/guides/connecting/ssh.html).
    * Edit your `.bashrc` file to include these two lines at the bottom:
      ```bash
      module use --append /caldera/projects/usgs/water/impd/hytest/modules
      module load hytest
      ```
    * NOTE: Edit your `.bashrc` with care. It controls what happens when you log in.  If it gets mangled,
      your account may not work correctly .

## 2) Install `jupyter-forward` on your PC

This is a one-time operation to get the right software on your desktop.
The [jupyter-forward](https://pypi.org/project/jupyter-forward/) software will
wrap up a series of commands necessary to to execute a jupyter server on the
HPC host we just configured. It is a convenience package intended to make
HPC-based jupyter servers easy.

    * Install Python on your PC. <br>
      You will need to have python installed on your PC, along with either `pip` or
      `conda` to help manage the python environments. We recommend anaconda.
      You can request anaconda from IT, or you can download the installer from [anaconda.com](https://www.anaconda.com/)
      to install it in user space (i.e. admin is not required).
    * Add `jupyter-forward` to your PC:<br>
      Launch an `Anaconda Prompt` from your Start menu, then execute:
      ```text
      > conda install -c conda-forge jupyter-forward
      ```
Anaconda provides the option for multiple virtual environments and configurations.  It does not
matter which one is active when you install `jupyter-forward` ( the "base" or some other).  You
just need to have that enviroment active when you attempt to launch the command later.

## 3) Launch Server

   With all of that set up, you are now ready to launch a session on the HPC using
   `jupyter-forward` on your PC. Do this every time you would like to run notebooks
   housed on the HPC host.

    * Launch an `Anaconda Prompt` from your start menu on your local computer
    * Run the following command to connect compute node. If you are not in the `impd` group, you will need to replace `impd` with a group you are a part of. You may also need to update the number of hours you want to have access to the compute node (in this example, we are requesting 1 hour).:

  ```text
    jupyter-forward --launch-command "srun -A impd -N 1 -t 01:00:00"  denali
  ```
    * Log in with your AD username and password.
    * The output of the script will also provide the URL where your PC's browser will find the jupter server. You can open one of these urls in your browser.

## 4) Shut Down Server<br>

After a daily session, you will need to shut down the jupyter server.
In the terminal session where you started `jupyter-forward`, merely press Ctl-C
to signal the server to shut down.