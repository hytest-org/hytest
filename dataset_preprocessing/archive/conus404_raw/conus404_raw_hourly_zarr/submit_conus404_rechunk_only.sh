#!/bin/bash -e

MAX_JOBS=30

FIRST_STEP=0
LAST_STEP=2556

# Rechunk CONUS404 model output
sbatch --array=${FIRST_STEP}-${LAST_STEP}%${MAX_JOBS} rechunk.sbatch
