#!/bin/bash -e

# NOTE: The python script options in rechunk.sbatch and to_zarr.sbatch must be
#       set correctly prior to running this job script.

STEP=10
MAX_JOBS=30

LAST_STEP=2556

# First rechunk the CONUS404 model output
jobid0=$(sbatch --parsable --array=0-${LAST_STEP}%${MAX_JOBS} rechunk.sbatch)

# Next create the final CONUS404 zarr dataset
jobid1=$(sbatch --parsable --dependency=afterok:${jobid0} --array=0-9:${STEP} to_zarr.sbatch)
sbatch --dependency=afterok:${jobid1} --array=10-${LAST_STEP}:${STEP}%${MAX_JOBS} to_zarr.sbatch
