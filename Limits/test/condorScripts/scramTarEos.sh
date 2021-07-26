#!/bin/bash
orgDir=`pwd`
# move to CMSSW dir
echo ${orgDir}
echo ${CMSSW_BASE}
cd ${CMSSW_BASE}
echo `pwd`
#to recompile
scramv1 b clean ; scramv1 b

#move to biasStudies2 dir
cd ..
echo `pwd`

# to create the tarball of CMSSW without unnecessary files
tar --exclude-caches-all --exclude-vcs -zcf CMSSW_10_2_13.tgz CMSSW_10_2_13 --exclude="*.root" --exclude=tmp
ls -la

#move said tarball to eos space so that condor can access it
xrdcp -f CMSSW_10_2_13.tgz root://cmseos.fnal.gov//store/user/pedrok/SVJ2017/Limits/datacards_Jul26

#move back to original directory
cd ${orgDir}
echo `pwd`
