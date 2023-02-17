#!/bin/bash -e

STEP=10
MAX_JOBS=30

LAST_STEP=2556

# Create final ZARR of CONUS404 data
jobid1=$(sbatch --parsable --array=0-9:${STEP} to_zarr.sbatch)
sbatch --dependency=afterok:${jobid1} --array=${STEP}-${LAST_STEP}:${STEP}%${MAX_JOBS} to_zarr.sbatch
