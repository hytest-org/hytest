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


