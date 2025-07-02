# Summarizing the WRF-Hydro Modeling Application outputs from hourly to monthly. 
**Workflow Authors:** Kevin Sampson and Aubrey Dugger at NSF National Center for Atmospheric Research (NCAR)

WRF-Hydro Modeling Application outputs are provided at the hourly time scale while CONUS404-BA temperature and precipitation outputs are provided at the 3-hour timescale. Many water-budget components are summarized at the monthly scale because daily or hourly scales may introduce unpredictable variation in model output. Monthly temporal resolution can also make it easier to identify patterns in the data. Additionally, NHM-PRMS data is at the monthly time scale, so summarizing WRF-Hydro outputs to a monthly time scale will make comparisons between the two models possible.   

## Overview
NCO is required for this workflow: [netCDF Operator](https://nco.sourceforge.net/). USGS HPC Hovenweep has an NCO module set up that needs to be loaded before the workflow is run. 

To keep processing times low, this workflow has been parallelized. There are 4 variables that need to be converted from hourly to monthly: LDASOUT, LDASIN, CHRTOUT, and GWOUT. Each variable has a shell script that does the hourly to monthly calculations. These can be run for a single year or called into a slurm file to run multiple years at once. 

| **Source** | **File** | **File Structure** | **Time Step** | **Shell Script** | **Slurm file** | **Processing Time** |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
| WRF-Hydro | LDASOUT | Calendar Year | 3-hourly | nco_process_ldasout.sh | ldasout_nco.slurm | XXX |
| CONUS404-BA | LDASIN | Water Year | hourly | nco_process_clim.sh | clim_nco.slurm | XXX |
| WRF-Hydro | GWOUT | Calendar Year | hourly | nco_process_gwout.sh | gwout_nco.slurm | XXX |
| WRF-Hydro | CHRTOUT | Calendar Year | hourly | nco_process_chrtout.sh | chrtout_nco.slurm | XXX |

## Set-Up
### One Year at a Time: 

Load netcdf operator
```
module load nco
```
Ensure paths in shell script are correct. 

Allow edit permission for the shell script, the shell files should be green after running this:
```
chmod +x /path/to/yourscript.sh
```
Run the shell script. 
```
./nco_process_ldasout.sh 2009
```
Repeat for other variables. 

### Multiple Years at Once: 

Ensure paths in shell scripts and slurm files are correct.  

Allow edit permission for the shell script:
```
chmod +x /path/to/yourscript.sh
```
Launch slurm script with an array of years of interest, 2011-2013 is used here. Adjust name of slurm file based on which WRF-Hydro output is being processed. 
```
sbatch --array=2011-2013 ldasout_nco.slurm
```
To check on the status of slurm request and find job id:
```
squeue -u <username>
```
If you need to cancel the request: 
```
scancel <jobid>
```
Repeat for other variables.

## Shell Scripts
<details>
<summary>LDASOUT:</summary>

### nco_process_ldasout.sh
#### Script Preparations:
You will need to specify three paths: 
  - The location of the 3-hour WRF-Hydro output LDASOUT files.
  - The location of the static soil properties file.
  - The location of where to save the monthly outputs.
#### Overview:
  - Process porosity & wilting point parameters
  - Process accumulated flux & state differences
  - Process mean states
  - Cleanup names

```
#!/bin/bash
# ###########################################################################
# Bash shell script to create monthly aggregates of WRF-Hydro LDASOUT files.
# Requirements: NCO (tested with version 5.2.9)
#               https://nco.sourceforge.net/
# Usage: Call shell script with a single argument specifying the 4-digit
#        year to process
#        e.g., ./nco_process_ldasout.sh 2009
# Developed: 06/11/2024, A. Dugger
# Updated: 4/7/2025, L. Staub
# ###########################################################################

# ###########################################################################
# USER-SPECIFIED INPUTS:

# Specify WRF-Hydro output directories:
# indir_base="/path/to/input/files/" #LDASOUT files
# soilparm="/path/to/soil_properties_file.nc" #soil properties static files

indir_base="/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/LDASOUT"
soilparm="/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/static_niwaa_wrf_hydro_files/WRFHydro_soil_properties_CONUS_1km_NIWAAv1.0.nc"


# Specify output directory where monthly files should be written to monthly folder:
# (output files will be named water_YYYYMM.nc)

outdir="/path/to/monthly/output/files/monthly"


# Check if the folder exists/create one
if [ ! -d "$outdir" ]; then
    # Create the folder
    mkdir -p "$outdir"
    echo "Folder created: $outdir"
else
    echo "Folder already exists: $outdir"
fi

# ###########################################################################

# ###########################################################################
# MAIN CODE. Probably no need to update anything below here.
# ###########################################################################

# Initial setup.
shopt -s nullglob
uniqid=`uuidgen`
tmpfile=tmp${uniqid}.nc
paramfile=params${uniqid}.nc


# Process porosity and wilting point parameters for use in soilsat calculations.
# These parameters are currently uniform over depth layers.
#the two lines below could not run because the tmpfile and paramfile do not exist??
rm ${tmpfile} 
rm ${paramfile}
ncks -A -v smcmax,smcwlt $soilparm ${paramfile}
ncrename -O -d south_north,y ${paramfile} ${paramfile}
ncrename -O -d west_east,x ${paramfile} ${paramfile}
ncrename -O -d Time,time ${paramfile} ${paramfile}
ncpdq -O -a time,y,soil_layers_stag,x ${paramfile} ${paramfile}

# Get the year to process from the command line argument.
# This setup is useful for scripting loops by year.
yr=${1}
echo "Processing year ${yr}"
YYYY=`printf %04d ${yr}`

# Loop through months
for mo in $(seq 1 1 12); do
  echo "  Processing month ${mo}"
  MM=`printf %02d ${mo}`

  # Setup input directory and output filename.
  indir="${indir_base}/${yr}" 
  outfile="${outdir}/water_${YYYY}${MM}.nc"
  rm $outfile

  # Grab the processing start time so we can track how long this takes.
  start_time=`date -u +%s`

  # Processing accumulated flux and state diffs
  # Adding one file so we can do a proper diff over accumulated terms
  # Resets happen at 00Z on the first day of month every 3 months
  # e.g., 197904010300.LDASOUT_DOMAIN1 to 197904302100.LDASOUT_DOMAIN1
  last_file_datetime=`date -d "${YYYY}${MM}01 + 1 month - 3 hour" +%Y%m%d%H`
  firstfile=`echo ${indir}/${YYYY}${MM}010000.LDASOUT_DOMAIN1`
  lastfile=`echo ${indir}/${last_file_datetime}00.LDASOUT_DOMAIN1`

  echo "      $firstfile $lastfile"

  if [ -f "${firstfile}" -a -f "${lastfile}" ]; then
    echo "      Processing diffs"
    echo "        first $firstfile"
    echo "        last $lastfile"
    echo "        output $outfile"
    ncdiff $lastfile $firstfile $tmpfile
    # Calculate depth-mean soil moisture by averaging over column by layer depths: (0.1, 0.3, 0.6, 1.0) = 2.0
    ncap2 -O -F -s "deltaSOILM_depthmean=float((SOIL_M(:,:,1,:)*0.1+SOIL_M(:,:,2,:)*0.3+SOIL_M(:,:,3,:)*0.6+SOIL_M(:,:,4,:)*1.0)/2.0)" ${tmpfile} ${tmpfile}
    if [ "${mo}" -eq 10 ]; then
      ncks -h -A -v SOIL_M,SNEQV,deltaSOILM_depthmean ${tmpfile} ${outfile}
      ncks -h -A -v ACCET,UGDRNOFF,ACSNOW ${lastfile} ${outfile}
    else
      ncks -h -A -v ACCET,UGDRNOFF,SOIL_M,SNEQV,ACSNOW,deltaSOILM_depthmean ${tmpfile} ${outfile}
    fi
    rm ${tmpfile}
    ncrename -h -v ACCET,deltaACCET ${outfile}
    ncrename -h -v ACSNOW,deltaACSNOW ${outfile}
    ncrename -h -v UGDRNOFF,deltaUGDRNOFF ${outfile}
    ncrename -h -v SOIL_M,deltaSOILM ${outfile}
    ncrename -h -v SNEQV,deltaSNEQV ${outfile}

    # Processing mean states
    # Averaging from 00Z of first day or month to 21Z of last day of month
    # Compiling list of files
    # e.g., 200506150500.LDASOUT_DOMAIN1
    infiles=(${indir}/${YYYY}${MM}*.LDASOUT_DOMAIN1)
    infiles_list=`echo "${infiles[*]}"`
    count=${#infiles[@]}
    echo "      Processing means"
    echo "        found $count files"
    echo "        first ${infiles[0]}"
    echo "        last ${infiles[-1]}"
    ncra -O -y avg -v SOIL_M,SNEQV ${infiles_list} ${tmpfile}
    # Calculate depth-mean soil moisture by averaging over column by layer depths: (0.1, 0.3, 0.6, 1.0) = 2.0
    ncap2 -O -F -s "avgSOILM_depthmean=float((SOIL_M(:,:,1,:)*0.1+SOIL_M(:,:,2,:)*0.3+SOIL_M(:,:,3,:)*0.6+SOIL_M(:,:,4,:)*1.0)/2.0)" ${tmpfile} ${tmpfile}
    # Bring in porosity and calculate soilsat
    # Note that porosity is uniform with depth, so it doesn't matter what layer we use
    ncks -A -v smcmax ${paramfile} ${tmpfile}
    ncap2 -O -F -s "avgSOILSAT=float(avgSOILM_depthmean/smcmax(:,:,1,:))" ${tmpfile} ${tmpfile}
    ncrename -h -v SOIL_M,avgSOILM ${tmpfile}
    ncrename -h -v SNEQV,avgSNEQV ${tmpfile}
    # Calculate new wilting point adjusted variables requested by USGS
    # Note that wilting point is uniform with depth, so it doesn't matter what layer we use
    ncks -A -v smcwlt ${paramfile} ${tmpfile}
    ncap2 -O -F -s "avgSOILM_wltadj_depthmean=float(avgSOILM_depthmean-smcwlt(:,:,1,:))" ${tmpfile} ${tmpfile}
    ncap2 -O -F -s "avgSOILSAT_wltadj_top1=float((avgSOILM(:,:,1,:)-smcwlt(:,:,1,:))/(smcmax(:,:,1,:)-smcwlt(:,:,1,:)))" ${tmpfile} ${tmpfile}
    # Combine average file with delta file
    ncks -h -A -v avgSOILM,avgSNEQV,avgSOILM_depthmean,avgSOILSAT,avgSOILM_wltadj_depthmean,avgSOILSAT_wltadj_top1 ${tmpfile} ${outfile}
    rm ${tmpfile}

    # Cleanup names and attributes.
    echo "Cleaning up attributes"
    ncatted -O -h -a valid_range,,d,, ${outfile} ${outfile}
    ncatted -O -h -a cell_methods,,d,, ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaACCET,o,c,"Change in accumulated evapotranspiration (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaACSNOW,o,c,"Change in accumulated snowfall (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaSNEQV,o,c,"Change in snow water equivalent (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaSOILM,o,c,"Change in layer volumetric soil moisture, ratio of water volume to soil volume (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaUGDRNOFF,o,c,"Change in accumulated underground runoff (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaSOILM_depthmean,o,c,"Change in depth-mean volumetric soil moisture, ratio of water volume to soil volume (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgSNEQV,o,c,"Average snow water equivalent over month" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgSOILM,o,c,"Average layer volumetric soil moisture (ratio of water volume to soil volume) over month" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgSOILM_depthmean,o,c,"Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) over month" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgSOILM_wltadj_depthmean,o,c,"Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) minus wilting point over month" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgSOILSAT,o,c,"Average fractional soil saturation (soil moisture divided by maximum water content) over month" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgSOILSAT_wltadj_top1,o,c,"Average fractional soil saturation above wilting point (soil moisture minus wilting point divided by maximum water content minus wilting point) over top layer (top 10cm) over month" ${outfile} ${outfile}
    ncatted -O -h -a units,avgSOILSAT,o,c,"fraction (0-1)" ${outfile} ${outfile}
    ncatted -O -h -a units,avgSOILSAT_wltadj_top1,o,c,"fraction (0-1)" ${outfile} ${outfile}

    # Wrap up the month.
    end_time=`date -u +%s`
    elapsed=`echo "$end_time - $start_time" | bc`
    echo "      Done aggregating hourly values : "${YYYY}"-"${MM}"  "$elapsed" seconds since start time."

  else
    # We didn't find any files for this year+month.
    echo "      Missing files. Skipping month."

  fi

done

rm ${paramfile}
```
</details>

<details>

<summary>GWOUT:</summary>

### nco_process_gwout.sh
#### Script Preparations:
You will need to specify two paths: 
  - The location of the hourly WRF-Hydro output GWOUT files.
  - The location of where to save the monthly outputs.

*Note: this script has some additional lines of code to deal with filetypes in the depth variable. Renaming the variable seems to fix this bug. Another option is to use older version of the NCO module- this has not been explored yet.
#### Overview:
  - Process accumulated flux & state differences
  - Rename "depth" column to "bucket_depth"
  - Process sums and means
  - Process flow totals
  - Process depth average
  - Cleanup names

```
#!/bin/bash
# ###########################################################################
# Bash shell script to create monthly aggregates of WRF-Hydro GWOUT files.
# Requirements: NCO (tested with version 5.2.9)
#               https://nco.sourceforge.net/
# Usage: Call shell script with a single argument specifying the 4-digit
#        year to process
#        e.g., ./nco_process_gwout.sh 2009
# Developed: 06/11/2024, A. Dugger
# Updated: 4/7/2025 L.Staub 
# ###########################################################################

# ###########################################################################
# USER-SPECIFIED INPUTS:

# Specify WRF-Hydro output directory:
#indir_base="/path/to/input/files"
indir_base="/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/GWOUT"

# Specify output directory where monthly files should be written to monthly folder:
# (output files will be named gw_YYYYMM.nc)

outdir="/path/to/monthly/output/files/monthly"


# Check if the folder exists/create one
if [ ! -d "$outdir" ]; then
    # Create the folder
    mkdir -p "$outdir"
    echo "Folder created: $outdir"
else
    echo "Folder already exists: $outdir"
fi

# ###########################################################################

# ###########################################################################
# MAIN CODE. Probably no need to update anything below here.
# ###########################################################################

# Initial setup.
shopt -s nullglob
uniqid=`uuidgen`
tmpfile=tmp${uniqid}.nc

mkdir $outdir

# Get the year to process from the command line argument.
# This setup is useful for scripting loops by year.
yr=${1}
echo "Processing year ${yr}"
YYYY=`printf %04d ${yr}`

# Loop through months
for mo in $(seq 1 1 12); do
  echo "  Processing month ${mo}"
  MM=`printf %02d ${mo}`

  # Calculate next year and month for diff calculations
  next_yr=${yr}
  next_mo=`echo "${mo} + 1" | bc`
  if [ "${next_mo}" -eq 13 ]; then
     next_mo=1
     next_yr=`echo "${yr} + 1" | bc`
  fi

  # Setup some print variables
  MM2=`printf %02d ${next_mo}`
  YYYY2=`printf %04d ${next_yr}`

  # Setup input directory and output filename.
  indir="${indir_base}/${yr}/"
  indir_next="${indir_base}/${next_yr}/"
  outfile="${outdir}/gw_${YYYY}${MM}.nc"
  rm $outfile

  # Grab the processing start time so we can track how long this takes.
  start_time=`date -u +%s`

  # Processing accumulated flux and state diffs
  firstfile=`echo ${indir}/${YYYY}${MM}010100.GWOUT_DOMAIN1`
  lastfile=`echo ${indir_next}/${YYYY2}${MM2}010000.GWOUT_DOMAIN1`

  echo "      $firstfile $lastfile"

  if [ -f "${firstfile}" -a -f "${lastfile}" ]; then
    echo "      Processing diffs"
    echo "        first $firstfile"
    echo "        last $lastfile"
    echo "        output $outfile"
    ncdiff $lastfile $firstfile $tmpfile
    ncks -h -A -v depth ${tmpfile} ${outfile}
    rm ${tmpfile}
    ncrename -h -v depth,deltaDepth ${outfile}

    # Compiling list of files
    # e.g., 200506150500.GWOUT_DOMAIN1
    infiles=(${indir}/${YYYY}${MM}*.GWOUT_DOMAIN1)
    infiles_list=`echo "${infiles[*]}"`
    count=${#infiles[@]}
    # Check and rename the variable "depth" to "bucket_depth" if not already renamed
    echo "      Checking and renaming 'depth' to 'bucket_depth' if necessary"    
    for infile in "${infiles[@]}"; do
    # Check if "depth" variable exists using ncdump
    if ncdump -h "${infile}" | grep -q 'depth'; then
        # Rename the variable only if "depth" exists
        echo "        Renaming 'depth' to 'bucket_depth' in ${infile}"
        ncrename -h -v .depth,bucket_depth "${infile}"
    else
        echo "        'depth' already renamed in ${infile}, skipping"
    fi
done 
   
    echo "      Processing sums and means"
    echo "        found $count files"
    echo "        first ${infiles[0]}"
    echo "        last ${infiles[-1]}"
    # Create totals and averages.
    echo "      Processing flow totals"
    ncea -h -y ttl -v inflow,outflow ${infiles_list} ${tmpfile}
    ncks -h -A -v inflow,outflow ${tmpfile} ${outfile}
    rm ${tmpfile}
    echo "      Processing depth average"
    #ncra -O -y avg -v depth ${infiles_list} tmpavg_gw.nc # does not work since no record dim
    ncea -h -y avg -v bucket_depth ${infiles_list} ${tmpfile}
    ncks -h -A -v bucket_depth ${tmpfile} ${outfile}
    rm ${tmpfile}
    ncap2 -O -s "inflow=float(inflow*3600)" ${outfile} ${outfile}
    ncap2 -O -s "outflow=float(outflow*3600)" ${outfile} ${outfile}
    ncrename -h -v inflow,totInflow ${outfile}
    ncrename -h -v outflow,totOutflow ${outfile}
    ncrename -h -v depth,bucket_depth ${outfile}

    # Cleanup names and attributes.
    ncatted -O -h -a valid_range,,d,, ${outfile} ${outfile}
    ncatted -O -h -a cell_methods,,d,, ${outfile} ${outfile}
    ncatted -O -h -a long_name,totInflow,o,c,"Total inflow volume over momth" ${outfile} ${outfile}
    ncatted -O -h -a long_name,totOutflow,o,c,"Total outflow volume over momth" ${outfile} ${outfile}
    ncatted -O -h -a long_name,deltaDepth,o,c,"Change in baseflow bucket storage (month end minus month start)" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgDepth,o,c,"Average baseflow bucket storage over month" ${outfile} ${outfile}
    ncatted -O -h -a units,totInflow,m,c,"m^3" ${outfile}
    ncatted -O -h -a units,totOutflow,m,c,"m^3" ${outfile}
    ncatted -O -h -a units,deltaDepth,m,c,"mm" ${outfile}
    ncatted -O -h -a units,bucket_depth,m,c,"mm" ${outfile}

    # Wrap up the month.
    end_time=`date -u +%s`
    elapsed=`echo "$end_time - $start_time" | bc`
    echo "      Done aggregating hourly values : "${YYYY}"-"${MM}"  "$elapsed" seconds since start time."

  else
    # We didn't find any files for this year+month.
    echo "      Missing files. Skipping month."

  fi

done
```

</details>

<details>
<summary>LDASIN:</summary>

### nco_process_clim.sh
#### Script Preparations:
You will need to specify two paths: 
  - The location of the hourly CONUS404-BA output LDASIN files.
  - The location of where to save the monthly outputs.

*Note: this script has some additional lines of code to deal with this data being organized by Water Year.
#### Overview:
  - Create totals and averages
  - Cleanup names

```
#!/bin/bash
############################################################################
# Bash shell script to create monthly aggregates of WRF-Hydro forcing files.
# Requirements: NCO (tested with version 5.2.9)
#               https://nco.sourceforge.net/
# Usage: Call shell script with a single argument specifying the 4-digit
#        year to process
#        e.g., ./nco_process_clim.sh 2009
# Developed: 06/11/2024, A. Dugger
# Updated: 4/7/2025 L. Staub
############################################################################

############################################################################
# USER-SPECIFIED INPUTS:

# Specify input forcing directory:
# (assumes forcings are organized by water year)
#indir_base="/path/to/met/forcings/"

indir_base="/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/LDASIN"

# Specify output directory where monthly files should be written to monthly folder:
# (output files will be named clim_YYYYMM.nc)

outdir="/path/to/monthly/output/files/monthly"

############################################################################

############################################################################
# MAIN CODE. Probably no need to update anything below here.
############################################################################

# Initial setup.
shopt -s nullglob
uniqid=`uuidgen`
tmpfile=tmp${uniqid}.nc

mkdir $outdir

# Get the year to process from the command line argument.
# This setup is useful for scripting loops by year.
yr=${1}
echo "Processing year ${yr}"
YYYY=`printf %04d ${yr}`

# Loop through months
for mo in $(seq 1 1 12); do
  echo "  Processing month ${mo}"
  MM=`printf %02d ${mo}`

  # Calculate water year for finding folder name.
  wy_yr=${yr}
  if [ "${mo}" -ge 10 ]; then
     wy_yr=`echo "${wy_yr} + 1" | bc`
  fi

  # Setup input directory and output filename.
  indir="${indir_base}/WY${wy_yr}/"
  outfile="${outdir}/clim_${YYYY}${MM}.nc"

  # Grab the processing start time so we can track how long this takes.
  start_time=`date -u +%s`

  # Compiling list of files
  # e.g., 200506150500.LDASIN_DOMAIN1
  infiles=(${indir}/${YYYY}${MM}*.LDASIN_DOMAIN1)
  count=${#infiles[@]}
  echo "      Found $count files"

  # Check if we found files. Otherwise skip.
  if [ ${count} -gt 0 ]; then
    echo "      Processing sums and means"
    echo "      first ${infiles[0]}"
    echo "      last ${infiles[-1]}"
    echo "      output $outfile"

    infiles_list=`echo "${infiles[*]}"`

    # Create totals and averages.
    # Start with precip (sum) and temperature (average).
    ncra -O -h -y ttl -v RAINRATE ${infiles_list} ${outfile}
    ncap2 -O -s "RAINRATE=float(RAINRATE*3600)" ${outfile} ${outfile}
    ncra -O -h -y avg -v T2D ${infiles_list} ${tmpfile}
    ncks -h -A -v T2D ${tmpfile} ${outfile}
    rm ${tmpfile}
    # Some additional met variables. Remove comments if you want to include.
    #ncra -O -h -y avg -v Q2D ${infiles_list} ${tmpfile}
    #ncks -h -A -v Q2D ${tmpfile} ${outfile}
    #rm ${tmpfile}
    #ncra -O -h -y avg -v SWDOWN ${infiles_list} ${tmpfile}
    #ncks -h -A -v SWDOWN ${tmpfile} ${outfile}
    #rm ${tmpfile}
    #ncra -O -h -y avg -v LWDOWN ${infiles_list} ${tmpfile}
    #ncks -h -A -v LWDOWN ${tmpfile} ${outfile}
    #rm ${tmpfile}
    #ncra -O -h -y avg -v U2D ${infiles_list} ${tmpfile}
    #ncks -h -A -v U2D ${tmpfile} ${outfile}
    #rm ${tmpfile}
    #ncra -O -h -y avg -v V2D ${infiles_list} ${tmpfile}
    #ncks -h -A -v V2D ${tmpfile} ${outfile}
    #rm ${tmpfile}
    #ncap2 -O -s "WND2D=float(sqrt(U2D^2 + V2D^2))" ${outfile} ${outfile} 
    #ncks -O -h -x -v V2D ${outfile} ${outfile}
    #ncks -O -h -x -v U2D ${outfile} ${outfile}

    # Cleanup names and attributes.
    # Remove the comments if you are including additional met variables.
    ncrename -h -v RAINRATE,totPRECIP ${outfile}
    ncrename -h -v T2D,avgT2D ${outfile}
    #ncrename -h -v Q2D,avgQ2D ${outfile}
    #ncrename -h -v SWDOWN,avgSWDOWN ${outfile}
    #ncrename -h -v LWDOWN,avgLWDOWN ${outfile}
    #ncrename -h -v WND2D,avgWND2D ${outfile}
    ncatted -O -h -a units,totPRECIP,o,c,"mm" ${outfile} ${outfile}
    ncatted -O -h -a long_name,totPRECIP,o,c,"Total precipitation over the month" ${outfile} ${outfile}
    ncatted -O -h -a long_name,avgT2D,o,c,"Average 2-m air temperature over the month" ${outfile} ${outfile}
    #ncatted -O -h -a long_name,avgQ2D,o,c,"Average 2-m specific humidity over the month" ${outfile} ${outfile}
    #ncatted -O -h -a long_name,avgSWDOWN,o,c,"Average downward shortwave radiation over the month" ${outfile} ${outfile}
    #ncatted -O -h -a long_name,avgLWDOWN,o,c,"Average downward longwave radiation over the month" ${outfile} ${outfile}
    #ncatted -O -h -a long_name,avgWND2D,o,c,"Average 2-m net windspeed over the month" ${outfile} ${outfile}

    # Wrap up the month.
    end_time=`date -u +%s`
    elapsed=`echo "$end_time - $start_time" | bc`
    echo "      Done aggregating hourly values : "${YYYY}"-"${MM}"  "$elapsed" seconds since start time."

  else
    # We didn't find any files for this year+month.
    echo "      Missing files. Skipping month."

  fi

done
```
</details>

<details>
<summary>CHRTOUT:</summary>

### nco_process_chrtout.sh
#### Script Preparations:
You will need to specify two paths: 
  - The location of the hourly WRF-Hydro output CHRTOUT files.
  - The location of where to save the monthly outputs.
#### Overview:
  - Create totals and averages
  - Clean names

```
#!/bin/bash
# ###########################################################################
# Bash shell script to create monthly aggregates of WRF-Hydro CHRTOUT files.
# Requirements: NCO (tested with version 5.2.9)
#               https://nco.sourceforge.net/
# Usage: Call shell script with a single argument specifying the 4-digit
#        year to process
#        e.g., ./nco_process_chrtout.sh 2009
# Developed: 06/11/2024, A. Dugger
# Updated: 4/7/2025, L. Staub 
# ###########################################################################

# ###########################################################################
# USER-SPECIFIED INPUTS:

# Specify WRF-Hydro output directory:
# (assumes files are organized by water year)
#indir_base="/path/to/input/files/" 
indir_base="/caldera/hovenweep/projects/usgs/water/impd/hytest/niwaa_wrfhydro_monthly_huc12_aggregations_sample_data/CHRTOUT"

# Specify output directory where monthly files should be written to monthly folder:
# (output files will be named chrt_YYYYMM.nc)
# Have all outputs saved to the same folder

outdir="/path/to/monthly/output/files/monthly"


# Check if the folder exists/create one
if [ ! -d "$outdir" ]; then
    # Create the folder
    mkdir -p "$outdir"
    echo "Folder created: $outdir"
else
    echo "Folder already exists: $outdir"
fi


# ###########################################################################

# ###########################################################################
# MAIN CODE. Probably no need to update anything below here.
# ###########################################################################

# Initial setup.
shopt -s nullglob


# Get the year to process from the command line argument.
# This setup is useful for scripting loops by year.
yr=${1}
echo "Processing year ${yr}"
YYYY=`printf %04d ${yr}`

# Loop through months
for mo in $(seq 1 1 12); do
  echo "  Processing month ${mo}"
  MM=`printf %02d ${mo}`

  # Setup input directory and output filename.
  indir="${indir_base}/${yr}/"
  outfile="${outdir}/chrt_${YYYY}${MM}.nc"

  # Grab the processing start time so we can track how long this takes.
  start_time=`date -u +%s`

  # Compiling list of files
  # e.g., 200506150500.CHRTOUT_DOMAIN1
  infiles=(${indir}/${YYYY}${MM}*.CHRTOUT_DOMAIN1)
  count=${#infiles[@]}
  echo "      Found $count files"

  # Check if we found files. Otherwise skip.
  if [ ${count} -gt 0 ]; then
    echo "      Processing sums and means"
    echo "      first ${infiles[0]}"
    echo "      last ${infiles[-1]}"
    echo "      output $outfile"

    infiles_list=`echo "${infiles[*]}"`

    # Create totals and averages.
    ncea -h -y ttl -v streamflow,qSfcLatRunoff,qBucket ${infiles_list} ${outfile}
    ncap2 -O -s "streamflow=float(streamflow*3600)" ${outfile} ${outfile}
    ncap2 -O -s "qSfcLatRunoff=float(qSfcLatRunoff*3600)" ${outfile} ${outfile}
    ncap2 -O -s "qBucket=float(qBucket*3600)" ${outfile} ${outfile}
    ncrename -h -v streamflow,totStreamflow ${outfile}
    ncrename -h -v qSfcLatRunoff,totqSfcLatRunoff ${outfile}
    ncrename -h -v qBucket,totqBucket ${outfile}

    # Cleanup names and attributes.
    ncatted -O -h -a valid_range,,d,, ${outfile} ${outfile}
    ncatted -O -h -a cell_methods,,d,, ${outfile} ${outfile}
    ncatted -O -h -a long_name,totStreamflow,m,c,"Total streamflow volume over momth" ${outfile} ${outfile}
    ncatted -O -h -a long_name,totqSfcLatRunoff,m,c,"Total surface flow volume over momth" ${outfile} ${outfile}
    ncatted -O -h -a long_name,totqBucket,m,c,"Total baseflow volume over month" ${outfile} ${outfile}
    ncatted -O -h -a units,totStreamflow,m,c,"m^3" ${outfile}
    ncatted -O -h -a units,totqSfcLatRunoff,m,c,"m^3" ${outfile}
    ncatted -O -h -a units,totqBucket,m,c,"m^3" ${outfile}

    # Wrap up the month.
    end_time=`date -u +%s`
    elapsed=`echo "$end_time - $start_time" | bc`
    echo "      Done aggregating hourly values : "${YYYY}"-"${MM}"  "$elapsed" seconds since start time."

  else
    # We didn't find any files for this year+month.
    echo "      Missing files. Skipping month."

  fi

done

```

</details>

## Results
The following metrics will be generated with these scripts: 
<table>
  <tr>
    <th>Source</th>
    <th>File</th>
    <th>Variable</th>
    <th>Name</th>
    <th>Description</th>
    <th>Units</th>
  </tr>
  <tr>
    <td rowspan="19"><a href="#WRF-Hydro"><b>WRF-Hydro</b></a></td>
    <td rowspan="12">LDASOUT</td>
    <td>deltaACCET</td>
    <td>ET change</td>
    <td>Total monthly evapotranspiration (land only)</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>deltaACSNOW</td>
    <td>Snowfall change</td>
    <td>Total monthly snowfall (land only)</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>deltaSNEQV</td>
    <td>SWE change</td>
    <td>Average monthly snow water equivalent (land only)</td>
    <td>mm</td>    
  </tr>
  <tr>
    <td>deltaSOILM</td>
    <td>Soil Water change</td>
    <td>Average monthly soil moisture in 2m soil column (land only)</td>
    <td>mm</td>      
  </tr>
  <tr>
    <td>deltaUGDRNOFF</td>
    <td>Recharge change</td>
    <td>Total monthly recharge (land only)</td>
    <td>mm</td>   
  </tr>
  <tr>
    <td>deltaSOILM_depthmean</td>
    <td>---</td>
    <td>Change in depth-mean volumetric soil moisture, ratio of water volume to soil volume (month end minus month start) </td>
    <td>---</td>    
  </tr>
  <tr>
    <td>avgSNEQV</td>
    <td>SWE average</td>
    <td>Mean snow water equivalent </td>
    <td>mm</td>  
  </tr>
  <tr>
    <td>avgSOILM</td>
    <td>Soil Water average</td>
    <td>Mean volumetric soil moisture by layer </td>
    <td>m3/m3</td>   
  </tr>
  <tr>
    <td>avgSOILM_depthmean</td>
    <td>---</td>
    <td>Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) over month </td>
    <td>---</td>
  </tr>
  <tr>
    <td>avgSOILM_wltadj_depthmean</td>
    <td>---</td>  
    <td>Average depth-mean volumetric soil moisture (ratio of water volume to soil volume) minus wilting point over month </td>
    <td>---</td>  
  </tr>
  <tr>
    <td>avgSOILSAT</td>
    <td>Soil Saturation average</td>
    <td>Average monthly fractional soil saturation in 2m soil column (land only) </td>
    <td>---</td> 
  </tr>
  <tr>
    <td>avgSOILSAT_wltadj_top1</td>
    <td>---</td> 
    <td>Average fractional soil saturation above wilting point (soil moisture minus wilting point divided by maximum water content minus wilting point) over top layer (top 10cm) over month</td>
    <td>---</td>     
  </tr>
  <tr>
    <td rowspan="4">GWOUT</td>
    <td>totOutflow</td>
    <td>Total outflow volume over month</td>
    <td>---</td>
    <td>m3</td>
  </tr>
  <tr>
    <td>totInflow</td>
    <td>Total inflow volume over month</td>
    <td>---</td>
    <td>m3</td>
  </tr>
  <tr>
    <td>deltaDepth</td>
    <td>Change in baseflow bucket storage (month end minus month start)</td>
    <td>---</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>bucket_depth</td>
    <td>Ground Water Store</td>
    <td>Average monthly groundwater storage</td>
    <td>mm</td>
  </tr>
  <tr>
    <td rowspan="3">CHRTOUT</td>
    <td>totqBucket</td>
    <td>Baseflow</td>
    <td>Total monthly baseflow</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>totqSfcLatRunoff</td>
    <td>Surfaceflow</td>
    <td>Total monthly surface flow</td>
    <td>mm</td>
  </tr>
  <tr>
    <td>totStreamflow</td>
    <td>---</td>
    <td>Total streamflow volume over month</td>
    <td>m3</td>
  </tr>
  <tr>
    <td rowspan="2"><a href="#CONUS404-BA"><b>CONUS404-BA</b></a></td>
    <td rowspan="2">LDASIN</td>
    <td>totPRECIP</td>
    <td>Precipitation</td>
    <td>Total monthly precipitation</td>
    <td>mm</td>
  </tr>
    <td>avgT2D</td>
    <td>Temperature</td>
    <td>Average 2-m air temperature</td>  
    <td>K</td>  
  </tr>
</table>



