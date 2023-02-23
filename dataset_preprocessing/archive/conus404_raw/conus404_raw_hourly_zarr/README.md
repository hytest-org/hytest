Scripts used to rechunk and convert CONUS404 module output to cloud-optimized zarr format

The rechunking and zarr merging scripts can be executed individually 
(e.g. while in an interactive HPC job) or submitted as a batch SLURM job.

## Batch SLURM job

The batch job is designed to run on denali. Currently paths are hardcoded in the
conus404_rechunk_ja.py and conus404_to_zarr.py scripts. Running the following,

```bash
./submit_conus404_processing.sh
```

will submit jobs for rechunking the CONUS404 variables and merging the chunks 
into a single zarr dataset. Each job is a job array and subsequents jobs won't 
run until the prior job completes successfully (e.g. rechunking must complete 
successfully before the zarr merging job will run). Job output is saved into 
the current working directory.

Please note: for the batch jobs to work a conda environment named `pangeo` must
exist (with all required libraries) and the scripts must be in the current 
working directory from where the shell script it run.

## Manual execution in an interactive job
To manually run the rechunker
```bash
python conus404_rechunk_ja.py -i <index>
```
where `<index>` is the zero-based chunk number to process. The rechunker processes 
6-day chunks of data with chunk indices starting at zero for the first 6-day chunk
indexed from the first model time (1979-10-01 00:00:00).

Each processed chunk is written to individual directories.

Once all chunks have been processed they need to be merged into a single zarr 
dataset. The script `conus404_to_zarr.py` is used to do this. The first index (zero) 
has special meaning; when this index is processed the initial empty zarr dataset is 
created, WRF constant variables are added, and a time variable for the entire
period is created. Subsequent indices only copy in the data for the non-constant 
variables.

To do this manually you would type something like the folllowing:

```bash
python conus404_to_zarr.py -i <index> -s <step>
```

where `<index>` is the zero-based chunk to add to the final zarr dataset and 
`<step>` is the number of chunks to process. For example,

```bash
python conus404_to_zarr.py -i 0 -s 10
```
would process chunks 0 to 9. Chunk zero would trigger the initial zarr dataset
creation and add the data from chunk 0. Then chunks 1-9 would be added to the zarr 
dataset. 

