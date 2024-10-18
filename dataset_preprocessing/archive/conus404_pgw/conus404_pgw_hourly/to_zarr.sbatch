#!/bin/bash
#SBATCH -J c404-pgw_zarr
##SBATCH -t 06:00:00
#SBATCH -t 00:50:00
#SBATCH -o %j-c404-pgw_zarr.out
#SBATCH -p cpu
#SBATCH -A mappnat
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

export PATH="$PATH:$HOME/miniforge3/bin"

source activate pangeo_310

echo $SLURM_ARRAY_TASK_ID
python /<path_to>/model_output_to_zarr.py --config-file conus404_pgw.yml --chunk-index ${SLURM_ARRAY_TASK_ID}
