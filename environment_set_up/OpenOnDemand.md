# HPC Server: Open OnDemand

This is a custom service provided by the ARC team and customized for use in HyTEST workflows. It is the easiest
to use (no configuration needed on your part), and provides reasonable compute resources via the `tallgrass`
host:

* Go to `https://tallgrass-denali-ondemand.cr.usgs.gov/pun/sys/dashboard/` in your web browser.
  Note that you must be on the VPN to access this host.
* Launch the HyTEST Jupyter Server app.
* Fill in the form to customize the allocation in which the Jupyter Server will execute.
* Submit

The Jupyter Server will run in an allocation on `tallgrass`. This server will have access to your home
directory/folder on that host, which is where your notebooks will reside.

For light duty work (i.e. tutorials), a `Viz` node is likely adequate in your allocation request.  If you
will be doing heavier processing, you may want to request a compute node.  None of the HyTEST tutorials
utilize GPU code; a GPU-enabled node is not necessary.
