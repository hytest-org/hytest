#!/bin/bash -e

STEP=10
MAX_JOBS=30

LAST_STEP=639

#sbatch --array=0-10:10 to_zarr.sbatch
#sbatch --dependency=afterok:2749205 --array=0-100:10 to_zarr.sbatch

# First rechunk CONUS404 model output
jobid0=$(sbatch --parsable --array=0-${LAST_STEP}%${MAX_JOBS} rechunk_daily.sbatch)

# Create final ZARR of CONUS404 data
jobid1=$(sbatch --parsable --dependency=afterok:${jobid0} --array=0-9:${STEP} to_zarr_daily.sbatch)
sbatch --dependency=afterok:${jobid1} --array=10-${LAST_STEP}:${STEP}%${MAX_JOBS} to_zarr_daily.sbatch
