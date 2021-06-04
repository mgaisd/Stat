#!/bin/bash

for SIG in Sig0 Sig1
do
  #for FUNCS in GenMainFitMain GenAltFitMain 
  for FUNCS in GenAltFitAlt GenMainFitAlt 
  do
#  for rI in 01 03 05 07 09
#	  do
#		python ../plotTGraphErrors_aran.py -n plots/varyZ/mean_${rI}_${SIG}${FUNCS} -f plots/varyZ/mean_${rI}_lowCut${SIG}${FUNCS}.txt plots/varyZ/mean_${rI}_lowSVJ2${SIG}${FUNCS}.txt plots/varyZ/mean_${rI}_highCut${SIG}${FUNCS}.txt plots/varyZ/mean_${rI}_highSVJ2${SIG}${FUNCS}.txt -x "r_{inv} = ${rI/0/0.}"
#		python ../plotTGraphErrors_aran.py -n plots/varyZ/stdev_${rI}_${SIG}${FUNCS} -f plots/varyZ/stdev_${rI}_lowCut${SIG}${FUNCS}.txt plots/varyZ/stdev_${rI}_lowSVJ2${SIG}${FUNCS}.txt plots/varyZ/stdev_${rI}_highCut${SIG}${FUNCS}.txt plots/varyZ/stdev_${rI}_highSVJ2${SIG}${FUNCS}.txt -x "r_{inv} = ${rI/0/0.}"
#		#python ../plotTGraphErrors_aran.py -n plots/varyZ/chi2_${rI}_${SIG}${FUNCS} -f plots/varyZ/chi2_${rI}_lowCut${SIG}${FUNCS}.txt plots/varyZ/chi2_${rI}_lowSVJ2${SIG}${FUNCS}.txt plots/varyZ/chi2_${rI}_highCut${SIG}${FUNCS}.txt plots/varyZ/chi2_${rI}_highSVJ2${SIG}${FUNCS}.txt -x "r_{inv} = ${rI/0/0.}"
#	  done
  for mZ in 1500 1700 1900 2100 2300 2500 2700 2900 3100 3300 3500 3700 3900 4100 4300 4500 4700 4900 5100
	  do
		python ../plotTGraphErrors_aran.py -n plots/varyR/mean_${mZ}_${SIG}${FUNCS} -f plots/varyR/mean_${mZ}_lowCut${SIG}${FUNCS}.txt plots/varyR/mean_${mZ}_lowSVJ2${SIG}${FUNCS}.txt plots/varyR/mean_${mZ}_highCut${SIG}${FUNCS}.txt plots/varyR/mean_${mZ}_highSVJ2${SIG}${FUNCS}.txt -x "m_{Z'} = ${mZ} GeV"
		python ../plotTGraphErrors_aran.py -n plots/varyR/stdev_${mZ}_${SIG}${FUNCS} -f plots/varyR/stdev_${mZ}_lowCut${SIG}${FUNCS}.txt plots/varyR/stdev_${mZ}_lowSVJ2${SIG}${FUNCS}.txt plots/varyR/stdev_${mZ}_highCut${SIG}${FUNCS}.txt plots/varyR/stdev_${mZ}_highSVJ2${SIG}${FUNCS}.txt -x "m_{Z'} = ${mZ} GeV"
		#python ../plotTGraphErrors_aran.py -n plots/varyR/chi2_${mZ}_${SIG}${FUNCS} -f plots/varyR/chi2_${mZ}_lowCut${SIG}${FUNCS}.txt plots/varyR/chi2_${mZ}_lowSVJ2${SIG}${FUNCS}.txt plots/varyR/chi2_${mZ}_highCut${SIG}${FUNCS}.txt plots/varyR/chi2_${mZ}_highSVJ2${SIG}${FUNCS}.txt -x "m_{Z'} = ${mZ} GeV"
	  done
  done
done
