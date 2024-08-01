Scripts used to rechunk and convert CONUS404-PGW model output to cloud-optimized zarr format

The conversion script can be executed individually (e.g. while in an interactive HPC job) or submitted as a batch SLURM job.

The file `pangeo_310.yml` is the YAML file can be used to create the conda environment used by this workflow.


## Batch SLURM job

The batch job is designed to run on hovenweep. Running the following,

```bash
./submit_c404-pgw_workflow.sh
```

will submit a job array for rechunking the CONUS404-PGW model output variables and merging the chunks 
into a single zarr dataset. Job output is saved into 
the current working directory.

Please note: for the batch jobs to work a conda environment named `pangeo_310` must
exist (with all required libraries) and the scripts must be in the current 
working directory from where the shell script is run.


## Manual execution in an interactive job
To manually run the conversion process
```bash
python model_output_to_zarr.py --config-file conus404_pgw.yml --chunk-index <index>
```
where `<index>` is the one-based chunk number to process.





srun --pty -p cpu -A mappnat --ntasks=1 --cpus-per-task=2 -t 04:00:00 -u bash -i
./model_output_to_zarr.py --config-file conus404_pgw.yml --chunk-index 1183