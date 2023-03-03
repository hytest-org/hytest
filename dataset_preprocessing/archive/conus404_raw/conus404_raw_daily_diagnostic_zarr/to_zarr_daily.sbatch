#!/bin/bash
#SBATCH -J cat_zarr
#SBATCH -t 00:20:00
#SBATCH -o %j-to_zarr.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40

# STEP should match the stride in the --array argument
export STEP=10
export PATH="$PATH:$HOME/miniconda3/bin"

source activate pangeo

base_dir=/caldera/projects/usgs/water/wbeep/conus404_work
src_zarr_dir=/calscratch/global/pnorton_daily_tmp
dst_zarr_dir=/caldera/projects/usgs/water/wbeep/conus404_work/zarr_daily_out

echo $SLURM_ARRAY_TASK_ID
python /caldera/projects/usgs/water/wbeep/conus404_work/conus404_to_zarr_daily.py -i $SLURM_ARRAY_TASK_ID -s $STEP -b $base_dir -z $src_zarr_dir -d $dst_zarr_dir

