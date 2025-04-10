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

