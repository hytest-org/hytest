#!/bin/bash -e

STEP=10
MAX_JOBS=30

LAST_STEP=2556

# Create final ZARR of CONUS404 data
sbatch --array=0-${LAST_STEP}:${STEP}%${MAX_JOBS} to_zarr.sbatch

#sbatch --array=10-${LAST_STEP}:${STEP}%${MAX_JOBS} to_zarr.sbatch
