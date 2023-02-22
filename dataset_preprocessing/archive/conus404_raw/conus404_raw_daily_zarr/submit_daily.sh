#!/bin/bash -e

STEP=4
MAX_JOBS=30

LAST_STEP=426

# Compute daily interval from hourly
sbatch --array=0-${LAST_STEP}:${STEP}%${MAX_JOBS} compute_daily.sbatch
