#!/bin/bash -e

STEP=10
MAX_JOBS=30

LAST_STEP=2556

# Add derived variables to existing zarr store
sbatch --array=${STEP}-${LAST_STEP}:${STEP}%${MAX_JOBS} derived_solrad.sbatch
