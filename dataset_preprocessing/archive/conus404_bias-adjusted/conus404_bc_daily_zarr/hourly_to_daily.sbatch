#!/bin/bash
#SBATCH -J cat_zarr
#SBATCH -t 00:40:00
#SBATCH -o %j-hourly_to_daily.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
# #SBATCH --hint=nomultithread
#SBATCH --cpus-per-task=40
#  #SBATCH --array=10-100:10

# STEP should match the stride in the --array argument
export STEP=2
export PATH="$PATH:$HOME/anaconda3/bin"

source activate pangeo

src_zarr_dir=/caldera/hytest_scratch/scratch/conus404/conus404_hourly_biascorrected.zarr
dst_zarr_dir=/caldera/hytest_scratch/scratch/conus404/conus404_daily_biascorrected.zarr

echo $SLURM_ARRAY_TASK_ID
python /caldera/projects/usgs/water/wbeep/conus404_work/conus404_biascorrected_hourly_to_daily.py -i $SLURM_ARRAY_TASK_ID -l $STEP -s $src_zarr_dir -d $dst_zarr_dir

