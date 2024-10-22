# Starting a Dask Cluster

Many of the workflows in this repository are designed to take advantage of parallelism via dask clusters. The details of spinning up a cluster will differ, depending on the [compute platform](./README.md). We have boilerplate code to help in starting a suitable cluster for many of the computing environments where HyTEST workflows are likely to run.

* [Nebari](Start_Dask_Cluster_Nebari.ipynb)
* [Pangeo.CHS.usgs.gov](Start_Dask_Cluster_PangeoCHS.ipynb)
* [Denali HPC](Start_Dask_Cluster_Denali.ipynb)
* [Tallgrass HPC](Start_Dask_Cluster_Tallgrass.ipynb)
* [Local Desktop](Start_Dask_Cluster_Desktop.ipynb)

If you are using dask in the USGS OnDemand computing environments, you may need to configure a few things first:
1. install dask dashboard package
2. start up ondemand using custom environment
3. run the correct code snippet above to start up a dask cluster - you should get back a url to connect to the dask dashboard that looks something like this: `http://172.25.1.29:8787/status`
4. before you can connect to the output url for the dask dashboard, you will need to tunnel in to the login node from you computer by running a command like `ssh -K -q -L 8787:172.25.1.29:8787 {username}@{supercomputer}-login1.gs.doi.net`. You will need to make sure the port and IP addresses match those output in your dashboard url. You will also need to fill in your username and the appropriate supercomputer name (`tg` for Tallgrass or `hw` for Hovenweep) in place of the `{placeholders}` above.
5. Now you can connect to your dashboard by pasting the url `https://localhost:8787/status` in your browser (make sure the port number matches the one on your dashboard link).