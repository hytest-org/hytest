#!/bin/bash
#SBATCH -J compute_daily
#SBATCH -t 00:30:00
#SBATCH -o %j-compute_daily.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
# #SBATCH --hint=nomultithread
#SBATCH --cpus-per-task=40
#  #SBATCH --array=10-100:10

# STEP should match the stride in the --array argument
export STEP=4
export PATH="$PATH:$HOME/anaconda3/bin"

source activate pangeo

base_dir=/caldera/projects/usgs/water/wbeep/conus404_work
src_zarr_dir=/caldera/hytest_scratch/scratch/conus404/conus404_hourly.zarr
dst_zarr_dir=/caldera/hytest_scratch/scratch/conus404/conus404_daily.zarr
var_type='cum60'    # One of: instant, cum60, cum_sim

echo $SLURM_ARRAY_TASK_ID
python ${base_dir}/conus404_hourly_to_daily.py -i $SLURM_ARRAY_TASK_ID -l $STEP -s $src_zarr_dir -d $dst_zarr_dir --type $var_type
