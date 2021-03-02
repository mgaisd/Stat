#!/bin/bash

MASS=$1
if [ -z "$MASS" ]; then
	exit 1
fi
eosArea=$2
TOYFILE=$3
TOYNAME=$4

toyArg=""
if [ -n "$TOYFILE" ]; then
	if [[ "$TOYFILE" == *"ASIMOV"* ]]; then
		toyArg="-t -1"
		TOYFILE=$(echo $TOYFILE | sed 's~ASIMOV~~')
	else
		toyArg="-t 1"
	fi
fi

SVJ_NAME=SVJ_mZprime${MASS}_mDark20_rinv03_alphapeak
if [ -n "$eosArea" ]; then
	export EOSDIR=${eosArea}/${SVJ_NAME}
fi

declare -A regions
regions[cut]="highCut lowCut"
regions[bdt]="highSVJ2 lowSVJ2"

for COMBO in cut bdt; do
	DC_NAMES=""
	WS_NAMES=""
	SetArgAll=""
	FrzArgAll=""
	TrkArgAll=""
	for REGION in ${regions[$COMBO]}; do
		DC_NAME=${SVJ_NAME}_${REGION}_2018_template_bias.txt
		DC_NAMES="${DC_NAMES}${DC_NAMES:+ }${DC_NAME}"
		WS_NAME=ws_${SVJ_NAME}_${REGION}_2018_template.root
		WS_NAMES="${WS_NAMES}${WS_NAMES:+ }${WS_NAME}"
		if [ -n "$eosArea" ]; then
			xrdcp -f -s root://cmseos.fnal.gov/${EOSDIR}/${DC_NAME} .
			xrdcp -f -s root://cmseos.fnal.gov/${EOSDIR}/${WS_NAME} .
		fi
		eval $(./getBiasArgs.py -r ${REGION} -n 1 -s "" -f ${WS_NAME})
		SetArgAll="${SetArgAll}${SetArgAll:+,}${SetArg}"
		FrzArgAll="${FrzArgAll}${FrzArgAll:+,}${FrzArg}"
		TrkArgAll="${TrkArgAll}${TrkArgAll:+,}${TrkArg}"
	done
	DC_NAME_ALL=datacard_${MASS}_${COMBO}
	combineCards.py $DC_NAMES > ${DC_NAME_ALL}.txt
	ARGS="--setParameters $SetArgAll --freezeParameters $FrzArgAll --trackParameters $TrkArgAll"
	if [ -n "$TOYFILE" ]; then
		ARGS="$ARGS --toysFile $(echo $TOYFILE | sed 's~COMBO~'${COMBO}'~') $toyArg --toysFrequentist"
	fi

	OUTNAME=impacts_${COMBO}${TOYNAME:+_}${TOYNAME}
	text2workspace.py ${DC_NAME_ALL}.txt
	combineTool.py -M Impacts -d ${DC_NAME_ALL}.root --doInitialFit --robustFit 1 -m 125 $ARGS
	combineTool.py -M Impacts -d ${DC_NAME_ALL}.root --robustFit 1 -m 125 --doFits --parallel 8 $ARGS
	combineTool.py -M Impacts -d ${DC_NAME_ALL}.root -o ${OUTNAME}.json -m 125
	plotImpacts.py -i ${OUTNAME}.json  -o ${OUTNAME}
	# subset
	python excludeImpacts.py -i ${OUTNAME}.json -m mcstat -x $(echo $FrzArgAll | tr ',' ' ')
	plotImpacts.py -i ${OUTNAME}_include.json  -o ${OUTNAME}_include
    plotImpacts.py -i ${OUTNAME}_include.json -o ${OUTNAME}_include_multi --per-page 4 --height 300 --label-size -1 --width 400
done
