#!/bin/bash -e

STEP=2
MAX_JOBS=30

LAST_STEP=426

# Create daily 
sbatch --array=0-${LAST_STEP}:${STEP}%${MAX_JOBS} hourly_to_daily.sbatch
