#!/bin/bash
echo "Starting job on " `date` #Date/time of start of job
echo "Running on: `uname -a`" #Condor job is running on this node
echo "System software: `cat /etc/redhat-release`" #Operating System on that node
source /cvmfs/cms.cern.ch/cmsset_default.sh

xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/CMSSW_10_2_13.tgz .
tar -xf CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz
export SCRAM_ARCH=slc6_amd64_gcc700
cd CMSSW_10_2_13/src/
scramv1 b ProjectRename
eval `scramv1 runtime -sh`

echo "CMSSW: "$CMSSW_BASE

cd Stat/Limits/test
#give names to parameters
mZ=${1}
mD=${2}
rI=${3}
aD=${4}
REGION=${5}
nTOYS=${6}
expSig=${7}
genFunc=${8} # 0 for bkgFunc, 1 for altFunc
fitFunc=${9} # 0 for bkgFunc, 1 for altFunc

SVJ_NAME="SVJ_mZprime${mZ}_mDark${mD}_rinv${rI}_alpha${aD}"

xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/biasStudies_FourStepBias_jul21/${SVJ_NAME}/${SVJ_NAME}_${REGION}_2018_template_bias.txt ${SVJ_NAME}_${REGION}_2018_template_bias.txt
xrdcp -s root://cmseos.fnal.gov//store/user/cfallon/biasStudies_FourStepBias_jul21/${SVJ_NAME}/ws_${SVJ_NAME}_${REGION}_2018_template.root ws_${SVJ_NAME}_${REGION}_2018_template.root

rMin=-10
rMax=10


#parOptsMain is for using the Main function, we want to ignore the Alt parameters
#parOptsAlt is the opposite
#parOptsTrack<X> is used in the FitDiag Command to track the parameters we use
#  i.e., if we use parOptsMain, we should also use parOptsTrackMain, but only in FitDiag
if [ ${REGION} == "highCut" ]
then
  parOptsMain="--setParameters pdf_index_${REGION}_2018=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_4_alt,${REGION}_p2_4_alt,${REGION}_p3_4_alt,${REGION}_p4_4_alt"
  parOptsAlt="--setParameters pdf_index_${REGION}_2018=1 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_3,${REGION}_p2_3,${REGION}_p3_3"
  parOptsTrackMain=" --trackParameters ${REGION}_p1_3,${REGION}_p2_3,${REGION}_p3_3"
  parOptsTrackAlt="--trackParameters ${REGION}_p1_4_alt,${REGION}_p2_4_alt,${REGION}_p3_4_alt,${REGION}_p4_4_alt"
elif [ ${REGION} == "lowCut" ]
then
  parOptsMain="--setParameters pdf_index_${REGION}_2018=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_3_alt,${REGION}_p2_3_alt,${REGION}_p3_3_alt"
  parOptsTrackMain="--trackParameters ${REGION}_p1_2,${REGION}_p2_2"
  parOptsAlt="--setParameters pdf_index_${REGION}_2018=1 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2,${REGION}_p2_2"
  parOptsTrackAlt="--trackParameters ${REGION}_p1_3_alt,${REGION}_p2_3_alt,${REGION}_p3_3_alt"
elif [ ${REGION} == "highSVJ2" ]
then
  if [ ${expSig} -eq 0 ]
  then
    rMin=-1
    rMax=1
  fi
  parOptsMain="--setParameters pdf_index_${REGION}_2018=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_1_alt"
  parOptsTrackMain="--trackParameters ${REGION}_p1_1"
  parOptsAlt="--setParameters pdf_index_${REGION}_2018=1 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_1"
  parOptsTrackAlt="--trackParameters ${REGION}_p1_1_alt"
elif [ ${REGION} == "lowSVJ2" ]
then
  if [ ${expSig} -eq 0 ]
  then
    rMin=-1
    rMax=1
  fi
  parOptsMain="--setParameters pdf_index_${REGION}_2018=0 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2_alt,${REGION}_p2_2_alt"
  parOptsTrackMain="--trackParameters ${REGION}_p1_2,${REGION}_p2_2"
  parOptsAlt="--setParameters pdf_index_${REGION}_2018=1 --freezeParameters pdf_index_${REGION}_2018,${REGION}_p1_2,${REGION}_p2_2"
  parOptsTrackAlt="--trackParameters ${REGION}_p1_2_alt,${REGION}_p2_2_alt"
else
  exit 1
fi


if [ ${genFunc} -eq 0 ]
then
  genName="${REGION}${optName}Sig${expSig}GenMain"
  parOptsMDFa=${parOptsMain}
  parOptsGen=${parOptsMain}
elif [ ${genFunc} -eq 1 ]
then
  genName="${REGION}${optName}Sig${expSig}GenAlt"
  parOptsMDFa=${parOptsAlt}
  parOptsGen=${parOptsAlt}
fi

if [ ${fitFunc} -eq 0 ]
then
  fitName="${genName}FitMain"
  parOptsMDFb=${parOptsMain}
  parOptsFit="${parOptsMain} ${parOptsTrackMain}"
elif [ ${fitFunc} -eq 1 ]
then
  fitName="${genName}FitAlt"
  parOptsMDFb=${parOptsAlt}
  parOptsFit="${parOptsAlt} ${parOptsTrackAlt}"
fi


cmdMDFa="combine ${SVJ_NAME}_${REGION}_2018_template_bias.txt -M MultiDimFit -n ${genName} --saveWorkspace --rMin -80 --rMax 80 ${parOptsMDFa}" 
cmdGen="combine higgsCombine${genName}.MultiDimFit.mH120.root --snapshotName MultiDimFit -M GenerateOnly ${parOptsGen} -n ${genName} -t ${nTOYS} --toysFrequentist --saveToys --expectSignal ${expSig} --bypassFrequentistFit --saveWorkspace -s 123456"
cmdMDFb="combine ${SVJ_NAME}_${REGION}_2018_template_bias.txt -M MultiDimFit -n ${fitName} --saveWorkspace --rMin -80 --rMax 80 ${parOptsMDFb}" 
cmdFit="combine higgsCombine${fitName}.MultiDimFit.mH120.root --snapshotName MultiDimFit -M FitDiagnostics ${parOptsFit} -n ${fitName} --toysFile higgsCombine${genName}.GenerateOnly.mH120.123456.root -t ${nTOYS} --toysFrequentist --saveToys --expectSignal ${expSig} --rMin ${rMin} --rMax ${rMax} --bypassFrequentistFit"


echo "combine commands:"
echo ${cmdMDFa}
echo ${cmdGen}
echo ${cmdMDFb}
echo ${cmdFit}
echo ${cmdMDFa} >/dev/stderr
echo ${cmdGen} >/dev/stderr
echo ${cmdMDFb} >/dev/stderr
echo ${cmdFit} >/dev/stderr

doStuff=1
if [ ${doStuff} -eq 1 ]
then
  echo "Doing Snapshot for Gen" >/dev/stderr
  $cmdMDFa
  echo "Done with Snapshot for Gen" >/dev/stderr
  echo "Doing Gen" >/dev/stderr
  $cmdGen
  echo "Done with Gen" >/dev/stderr
  echo "Doing Snapshot for Fit" >/dev/stderr
  $cmdMDFb
  echo "Done with Snapshot for Fit" >/dev/stderr
  echo "Doing Fit" >/dev/stderr
  $cmdFit
  echo "Done with Fit" >/dev/stderr
fi
# export items to EOS
echo "List all root files = "
ls *.root
echo "List all files"
ls 
echo "*******************************************"
OUTDIR=root://cmseos.fnal.gov//store/user/cfallon/biasStudies_FourStepBias_jul21/${SVJ_NAME}
echo "xrdcp output for condor"
for FILE in *.root
do
  if [ ! "ws_${SVJ_NAME}_${REGION}_2018_template.root" = ${FILE} ]
  then
    echo "xrdcp -f ${FILE} ${OUTDIR}/${FILE}"
    xrdcp -f ${FILE} ${OUTDIR}/${FILE} 2>&1
  fi
  rm ${FILE}
done
cd ${_CONDOR_SCRATCH_DIR}
rm -rf CMSSW_10_2_13

