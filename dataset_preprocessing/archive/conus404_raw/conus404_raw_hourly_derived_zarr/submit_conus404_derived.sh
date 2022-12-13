#!/bin/bash -e

STEP=10
MAX_JOBS=30

LAST_STEP=2556

# Add derived variables to existing zarr store
jobid1=$(sbatch --parsable --array=0-9:${STEP} derived.sbatch)
sbatch --dependency=afterok:${jobid1} --array=${STEP}-${LAST_STEP}:${STEP}%${MAX_JOBS} derived.sbatch
