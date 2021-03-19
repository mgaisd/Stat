#!/bin/bash

for SIG in Sig0 Sig1 SigM
do
  for FUNCS in GenAltFitAlt
  do
    python ../plotTGraphErrors_aran.py -l -n plots/varyZ_mean_${SIG}${FUNCS} -f plots/varyZ_mean_cut${SIG}${FUNCS}.txt plots/varyZ_mean_bdt${SIG}${FUNCS}.txt
    python ../plotTGraphErrors_aran.py -l -n plots/varyZ_stdev_${SIG}${FUNCS} -f plots/varyZ_stdev_cut${SIG}${FUNCS}.txt plots/varyZ_stdev_bdt${SIG}${FUNCS}.txt
  done
done
