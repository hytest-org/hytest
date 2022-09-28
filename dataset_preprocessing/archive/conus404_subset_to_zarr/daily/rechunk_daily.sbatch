#!/bin/bash
#SBATCH -J rechunk
#SBATCH -t 00:20:00
#SBATCH -o %j-rechunk.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10

export PATH="$PATH:$HOME/miniconda3/bin"

source activate pangeo

base_dir=/caldera/projects/usgs/water/wbeep/conus404_work
wrf_dir=wrfout_post
const_file=wrf_constants_conus404_final.nc
metadata_file=wrfout_metadata_w_std.csv
proc_vars_file=2022-03-16_DRB_addl_vars.csv
target_store=/calscratch/global/pnorton_daily_tmp

python /caldera/projects/usgs/water/wbeep/conus404_work/conus404_daily_rechunk_ja.py -i $SLURM_ARRAY_TASK_ID -b $base_dir -w $wrf_dir -c $const_file -v $proc_vars_file -m $metadata_file -d $target_store

