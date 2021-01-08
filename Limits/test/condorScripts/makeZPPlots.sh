#!/bin/bash

for SIG in Sig0 Sig1
do
  #for FUNCS in GenMainFitMain GenAltFitMain 
  for FUNCS in GenMainFitAlt GenAltFitAlt
  do
    python ../plotTGraphErrors_aran.py plots/varyZ_mean_${SIG}${FUNCS} plots/varyZ_mean_lowCut${SIG}${FUNCS}.txt plots/varyZ_mean_lowSVJ2${SIG}${FUNCS}.txt plots/varyZ_mean_highCut${SIG}${FUNCS}.txt plots/varyZ_mean_highSVJ2${SIG}${FUNCS}.txt
    python ../plotTGraphErrors_aran.py plots/varyZ_stdev_${SIG}${FUNCS}  plots/varyZ_stdev_lowCut${SIG}${FUNCS}.txt plots/varyZ_stdev_lowSVJ2${SIG}${FUNCS}.txt plots/varyZ_stdev_highCut${SIG}${FUNCS}.txt plots/varyZ_stdev_highSVJ2${SIG}${FUNCS}.txt
    python ../plotTGraphErrors_aran.py plots/varyZ_chi2_${SIG}${FUNCS}  plots/varyZ_chi2_lowCut${SIG}${FUNCS}.txt plots/varyZ_chi2_lowSVJ2${SIG}${FUNCS}.txt plots/varyZ_chi2_highCut${SIG}${FUNCS}.txt plots/varyZ_chi2_highSVJ2${SIG}${FUNCS}.txt
  done
done
