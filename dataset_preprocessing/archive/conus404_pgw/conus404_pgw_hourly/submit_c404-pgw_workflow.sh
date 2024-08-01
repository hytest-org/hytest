#!/bin/bash -e

MAX_JOBS=10
STEP=1   # STEP should match num_chunks_per_job in conus404_pgw.yml
FIRST_STEP=1
LAST_STEP=2556

sbatch --array=${FIRST_STEP}-${LAST_STEP}:${STEP}%${MAX_JOBS} to_zarr.sbatch
