#!/bin/bash
#SBATCH -J cat_zarr
#SBATCH -t 00:30:00
#SBATCH -o %j-to_zarr.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
# #SBATCH --hint=nomultithread
#SBATCH --cpus-per-task=40
#  #SBATCH --array=10-100:10

# STEP should match the stride in the --array argument
export STEP=10
export PATH="$PATH:$HOME/anaconda3/bin"

source activate pangeo

base_dir=/caldera/projects/usgs/water/wbeep/conus404_work
src_zarr_dir=/caldera/hytest_scratch/scratch/hourly_test.zarr

echo $SLURM_ARRAY_TASK_ID
python /caldera/projects/usgs/water/wbeep/conus404_work/conus404_hourly_derived_solar_radiation.py -b $base_dir -s $src_zarr_dir -i $SLURM_ARRAY_TASK_ID --step $STEP
