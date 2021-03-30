#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node
source /cvmfs/cms.cern.ch/cmsset_default.sh

EOSDIR=/store/user/pedrok/SVJ2017/Limits/datacards_Mar29
xrdcp -s root://cmseos.fnal.gov/${EOSDIR}/CMSSW_10_2_13.tgz .
tar -xf CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz
export SCRAM_ARCH=slc6_amd64_gcc700
cd CMSSW_10_2_13/src/
scramv1 b ProjectRename
eval `scramv1 runtime -sh`

echo "CMSSW: "$CMSSW_BASE

ls -la Stat/Limits/python
cd Stat/Limits/test
echo "Arguments passed to this script are:"
echo "Mode: ${1}"
echo "Doing Systematics. ${6}"
if [ ${6} == "N" ]
then
  s="-s"
else
  s=""
fi

echo "Signal Parameters: ${2} ${3} ${4} ${5}"
SVJ_NAME="SVJ_mZprime${2}_mDark${3}_rinv${4}_alpha${5}"
cmd="python createDatacardsOnly.py -m ${1} -t -Z ${2} -D ${3} -R ${4} -A ${5} ${s}"


echo "combine commands:"
echo ${cmd}
echo ${cmd} >/dev/stderr

$cmd


# export items to EOS
echo "List all root files = "
ls *.root
echo "List all files"
ls 
echo "*******************************************"
EOSDIR=${EOSDIR}/${SVJ_NAME}
OUTDIR=root://cmseos.fnal.gov/${EOSDIR}/
echo "xrdcp output for condor"
for FILE in ws*.root SVJ*.txt
do
  echo "xrdcp -f ${FILE} ${OUTDIR}${FILE}"
  xrdcp -f ${FILE} ${OUTDIR}${FILE} 2>&1
  rm ${FILE}
done



cd ${_CONDOR_SCRATCH_DIR}
rm -rf CMSSW_10_2_13
