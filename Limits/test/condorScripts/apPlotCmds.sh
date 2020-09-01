#!/bin/bash

REG=${1}


if [ ! -e "SVJ_mZprime3100_mDark20_rinv03_alphapeak_${REG}_2018_hist.txt" ]
then
  echo "file doesnt exist"
  #combine -M FitDiagnostics -d SVJ_mZprime3100_mDark20_rinv03_alphapeak_hist.txt  --minos all --robustFit=1 --saveWithUncertainties --cminDefaultMinimizerStrategy 0
fi

text2workspace.py  SVJ_mZprime3100_mDark20_rinv03_alphapeak_${REG}_2018_hist.txt
$CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d SVJ_mZprime3100_mDark20_rinv03_alphapeak_${REG}_2018_hist.root --doInitialFit --robustFit 1 -m 125
$CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d SVJ_mZprime3100_mDark20_rinv03_alphapeak_${REG}_2018_hist.root --robustFit 1 -m 125 --doFits
$CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/combineTool.py -M Impacts -d SVJ_mZprime3100_mDark20_rinv03_alphapeak_${REG}_2018_hist.root -o impacts_${REG}.json -m 125
$CMSSW_BASE/src/CombineHarvester/CombineTools/scripts/plotImpacts.py -i impacts_${REG}.json  -o impacts_${REG}
