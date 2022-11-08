# HPC Server :: Jupyter Forward

This option will configure your HPC account to access the correct Jupyter server software.  That server
will be invoked by a command installed on your PC.  This option minimizes the configuration changes
needed on the HPC host, but still permits relatively easy access to that hardware via a personal Jupyter
Server.

## 1) Configure your HPC account to access the HyTEST [conda](www.anaconda.org) environment :

    * log in to either HPC host ( `denali` or `tallgrass` )
    * Execute this command:  ` echo "module load hytest" >> ~/.bashrc"
    * NOTE.  It is **critical** that the above command uses the double-greater-than.  If you accidentally just use a single,
      bad things will happen.

## 2) Install `jupyter-forward` on your PC.

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
      Launch an `Anaconda Shell` from your Start menu, then execute:
      ```text
      > conda install -c conda-forge jupyter-forward
      ```

## 3) Launch Server

   With all of that set up, you are now ready to launch a session on the HPC using
   `jupyter-forward` on your PC. Do this every time you would like to run notebooks
   housed on the HPC host.
    * Launch an `Anaconda Shell` from your start menu
    * Run `jupyter-forward denali`
    * NOTE: This command will run the jupter server on the **login node** of Denali.
      This is OK if your workload is light (i.e. for tutorials).  If you will be doing
      heavier processing:
```text
jupyter-forward --launch-command "srun -A acctname -N 1 -t 02:00:00"  denali
```

## 4) Shut Down Server<br>

After a daily session, you will need to shut down the jupyter server.
In the terminal session where you started `jupyter-forward`, merely press Ctl-C
to signal the server to shut down.