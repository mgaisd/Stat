#!/bin/bash


rI=03
#for SIG in Sig0 Sig1 SigM
for SIG in Sig3M
do
  for FUNCS in GenAltFitAlt
  do
    python ../plotTGraphErrors_aran.py -l -n plots/varyZ/mean_${rI}_${SIG}${FUNCS} -f plots/varyZ/mean_${rI}_cut${SIG}${FUNCS}.txt plots/varyZ/mean_${rI}_bdt${SIG}${FUNCS}.txt -x "r_{inv} = ${rI/0/0.}"
    python ../plotTGraphErrors_aran.py -l -n plots/varyZ/stdev_${rI}_${SIG}${FUNCS} -f plots/varyZ/stdev_${rI}_cut${SIG}${FUNCS}.txt plots/varyZ/stdev_${rI}_bdt${SIG}${FUNCS}.txt -x "r_{inv} = ${rI/0/0.}"
  done
done
