#!/bin/bash

## Set options for the SLURM scheduler -- edit as appropriate
#SBATCH -J jupyternb
#SBATCH -t 2-00:00:00
#SBATCH -o %j-jupyternb.out
#SBATCH -p workq
#SBATCH -A wbeep
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=40

# We will launch the server on a randomly assigned port number between 8400 and 9400.  This
# minimizes the chances that we will impact other jupyter servers running at the same time.
JPORT=`shuf -i 8400-9400 -n 1`

### this will load the centralized HyTEST conda environment.
module use --append /caldera/projects/usgs/water/impd/hytest/modules
module load hytest

### If you want to use your own conda environment, remove the above module load statement
### and include statements here to activate your own environment:
# export PATH=/path/to/your/conda/bin:$PATH
# source activate envname

echo
echo "##########################################################################"
echo "Run the following ssh command from a new terminal on your desktop"
echo "ssh -N -L $JPORT:`hostname`:$JPORT -L 8787:`hostname`:8787 $USER@denali.cr.usgs.gov"
echo "##########################################################################"
echo

echo
echo "##########################################################################"
echo "COPY and paste the 127.0.0.1 URL below into a browser on your desktop"
echo "##########################################################################"
echo

srun jupyter lab --ip '*' --no-browser --port $JPORT --notebook-dir $PWD