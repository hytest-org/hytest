#!/bin/bash -e

STEP=4
MAX_JOBS=30

LAST_STEP=426

# First create the daily zarr store
jobid0=$(sbatch --parsable create_daily_zarr_store.sbatch)

# Compute daily interval from hourly
sbatch --dependency=afterok:${jobid0} --array=0-${LAST_STEP}:${STEP}%${MAX_JOBS} compute_daily.sbatch
