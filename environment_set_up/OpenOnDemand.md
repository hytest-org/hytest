# HPC Server: Open OnDemand Quick-Start

This is a custom service provided by the ARC team and customized for use in HyTEST workflows. It is the easiest
to use (no configuration needed on your part), and provides reasonable compute resources via the `tallgrass`
host:

* Go to `https://tg-ood.cr.usgs.gov/pun/sys/dashboard` in your web browser.
  Note that you must be on the VPN to access this host. You will be prompted to log in to the server, and you should use your AD username and password here.
* Launch the HyTEST Jupyter Server app under the Interactive Apps dropdown menu.
* Fill in the form to customize the allocation in which the Jupyter Server will execute. You may want to consider adding the git and/or aws modules if you plan to use them during your session. You will just need to type `module load git` and/or `module load aws` in the `Module loads` section.
* Submit
* Once your server is ready, a `Connect to Jupyter` button will appear that you can click to start your session.

The Jupyter Server will run in an allocation on `tallgrass`. This server will have access to your home
directory/folder on that host, which is where your notebooks will reside.

For light duty work (i.e. tutorials), a `Viz` node is likely adequate in your allocation request.  If you
will be doing heavier processing, you may want to request a compute node.  None of the HyTEST tutorials
utilize GPU code; a GPU-enabled node is not necessary.

##### Note: The code to build this app is in [this repository](https://code.chs.usgs.gov/sas/arc/arc-software/ood/bc_jupyter_hytest); however, this repo is only visible on the internal USGS network.