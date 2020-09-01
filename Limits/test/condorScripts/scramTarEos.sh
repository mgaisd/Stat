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

#delete old tar
# cant use `eosrm` because that is an alias command
# `eos root... rm ...` comes from typing `alias` into command line
# and seeing what `eosrm` is an alias for
eos root://cmseos.fnal.gov rm store/user/cfallon/CMSSW_10_2_13.tgz
rm CMSSW_10_2_13.tgz

# to create the tarball of CMSSW without unnessecary files
tar --exclude-caches-all --exclude-vcs -zcf CMSSW_10_2_13.tgz CMSSW_10_2_13 --exclude="*.root" --exclude=tmp
ls -la

#move said tarball to eos space so that condor can access it
xrdcp CMSSW_10_2_13.tgz root://cmseos.fnal.gov//store/user/cfallon

#move back to original directory
cd ${orgDir}
echo `pwd`
