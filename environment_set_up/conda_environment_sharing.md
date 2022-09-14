# Capturing and sharing Conda environments
A common use case:  You've created a custom Conda environment, maybe using `conda create -n myenv` or maybe an `environment.yml` file, but then you've added a few packages here and there to allow you to run various notebooks, and now you would like to share that environment with someone.

If you do `conda env export -n my_custom_env > environment.yml` you get an environment file with all packages in your current environment pinned to specific versions.  In the case I just ran, this was 450 lines long!   Instead, you can run `conda env export -n my_custom_env --from-history > environment.yml` and it will just add the packages as you added them yourself!  So in my case, instead of hundreds of packages, I just had:
```
name: rpy
channels:
  - conda-forge
dependencies:
  - rpy2
  - r-exactextractr
  - ipykernel
  - datashader
  - geoviews
  - hvplot
  - fiona
  - r-codetools
  - rioxarray
  - r-ncdf4
  - xagg
  - pygeos
  - spatialpandas
```
Much more manageable!   

If you want to share this exact environment, the best way is use `conda-lock`: 
1. Install conda-lock if you don't have it: `mamba install conda-lock`
1. Create the conda-lock file: `conda-lock --conda=mamba -f environment.yml -p linux-64`
1. Share the resulting `conda-lock.yml` with your colleague
1. Tell them to install `conda-lock` and re-create your environent with: `conda-lock install --name rpy conda-lock.yml`

