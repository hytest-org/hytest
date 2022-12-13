#!/bin/bash
#SBATCH -J create_zarr
#SBATCH -t 00:10:00
#SBATCH -o %j-create_daily_zarr.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
# #SBATCH --hint=nomultithread
#SBATCH --cpus-per-task=40
#  #SBATCH --array=10-100:10

export PATH="$PATH:$HOME/anaconda3/bin"

source activate pangeo

base_dir=/caldera/projects/usgs/water/wbeep/conus404_work
src_zarr_dir=/caldera/hytest_scratch/scratch/conus404/conus404_hourly.zarr
dst_zarr_dir=/caldera/hytest_scratch/scratch/conus404/conus404_daily.zarr

python ${base_dir}/create_empty_daily_zarr.py -s $src_zarr_dir -d $dst_zarr_dir
