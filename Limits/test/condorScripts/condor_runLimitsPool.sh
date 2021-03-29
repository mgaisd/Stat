#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node
source /cvmfs/cms.cern.ch/cmsset_default.sh

#give names to paramters:
mZ=${1}
mD=${2}
rI=${3}
aD=${4}

xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/CMSSW_10_2_13.tgz .
tar -xf CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz
export SCRAM_ARCH=slc6_amd64_gcc700
cd CMSSW_10_2_13/src/
scramv1 b ProjectRename
eval `scramv1 runtime -sh`

echo "CMSSW: "$CMSSW_BASE
echo "python subdir"
ls -la Stat/Limits/python
cd Stat/Limits/test

SVJ_NAME="SVJ_mZprime${mZ}_mDark${mD}_rinv${rI}_alpha${aD}"
mkdir ${SVJ_NAME}
EOSDIR=/store/user/cfallon/datacards_07tsb_sys/${SVJ_NAME}

for REGION in highCut highSVJ2 lowCut lowSVJ2; do
	DC_NAME="${SVJ_NAME}_${REGION}_2018_template_bias.txt"
	WS_NAME="ws_${SVJ_NAME}_${REGION}_2018_template.root"
    echo "Trying to copy files to local"
    echo ${EOSDIR}
    echo ${REGION}
    echo ${DC_NAME}
    echo ${WS_NAME}
    xrdcp root://cmseos.fnal.gov/${EOSDIR}/${DC_NAME} ${SVJ_NAME}/.
    xrdcp root://cmseos.fnal.gov/${EOSDIR}/${WS_NAME} ${SVJ_NAME}/.
done
pwd
ls -la


echo "Signal Parameters: ${mZ} ${mD} ${rI} ${aD}"
#example of current good args to use - Kevin, 3/9/21
#-n 0 -m Alt -M --extra="-p -f -s" -I --signal 3100 20 03 peak
#cmd="python runLimitsPool.py -n 0 -m Alt -M --extra=\"-p -f -s\" -I --signal ${mZ} ${mD} ${rI} ${aD}"
#lesson learned: try NOT to use escape characters in bash commands.
#cmd='python runLimitsPool.py -n 0 -m Alt -M --extra="-p -f -s" -I --signal '"${mZ} ${mD} ${rI} ${aD}"

#echo "combine commands:"
#echo ${cmd}
#echo ${cmd} >/dev/stderr

#$cmd

#even better lesson learned, just don't try to use quotes in quotes in bash.

(set -x
python runLimitsPool.py -n 0 -m Alt -M --extra "-p -f -s" -I --signal ${mZ} ${mD} ${rI} ${aD}
)

SVJ_NAME="SVJ_mZprime${mZ}_mDark${mD}_rinv${rI}_alpha${aD}"

# export items to EOS
echo "List all root files = "
echo "*******************************************"
ls *.root
echo "List all files"
ls 
echo "*******************************************"
echo "List files in SVJ subdir:"
ls ${SVJ_NAME}
echo "*******************************************"
OUTDIR=root://cmseos.fnal.gov/${EOSDIR}/
echo "xrdcp output for condor"
for FILE in *.root *.pdf *.txt ${SVJ_NAME}/*.txt #Residuals/*.pdf plots/*.pdf Fisher/*.txt ${SVJ_NAME}/*.txt
do
  echo "xrdcp -f ${FILE} ${OUTDIR}${FILE}"
  xrdcp -f ${FILE} ${OUTDIR}${FILE} 2>&1
  rm ${FILE}
done



cd ${_CONDOR_SCRATCH_DIR}
rm -rf CMSSW_10_2_13
