#!/bin/bash
# this should be run as ./bash_runCombine.py x y from the test dir.
# where x == 1 will force GEN to run
# and y == 1 will force FIT to run
runGen=$1
runFit=$2

if [ $runGen == 1 ]
then
	echo "Doing GEN"
fi
if [ $runFit == 1 ]
then
	echo "Doing FIT"
fi

testDIR="/uscms_data/d3/cfallon/SVJ/biasStudies/CMSSW_10_2_13/src/Stat/Limits/test/"
wsDIR="cards_Feb21_Thry/SVJ_mZprime3000_mDark20_rinv03_alphapeak/"
wsPATH="${testDIR}${wsDIR}"
#echo $wsPATH
for region in lowCut lowSVJ2 highCut highSVJ2
#for region in highCut
do
	regionPATH="${testDIR}${wsDIR}${region}"
	#echo $regionPATH
	for year in 2018
	do
		echo "Performing bias test for region $region"
		echo $wsPATH
		echo $regionPATH
		if [ ! -d $regionPATH ]
		then
			echo "Destination directory for $region doesn't exits. Making..."
			mkdir $regionPATH
		fi
		cd $regionPATH
		if [ $runGen == 1 ]
		then
			echo "Running GEN for MainSig0"
			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=0 --toysFrequentist -t 1000 --expectSignal 0 -n MainSig0 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_p2_2_alt,${region}_p1_2_alt,${region}_p2_2,${region}_p1_2 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --bypassFrequentistFit > /dev/null
		fi
		#if [ ! -e $regionPATH/higgsCombineMainSig1.GenerateOnly.mH125.123456.root ] || [ $runGen ]
		#then
		#	echo "Running GEN for MainSig1"
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=0 --toysFrequentist -t 500 --expectSignal 1 -n MainSig1 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_${year}_p2_2_alt,${region}_${year}_p1_2_alt #> $regionPATH/combineLog_MainSig0.out #2>&1
		#fi
		if [ $runGen == 1 ]
		then
			echo "Running GEN for AltSig0"
			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=1 --toysFrequentist -t 1000 --expectSignal 0 -n AltSig0 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_p2_2,${region}_p1_2 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --bypassFrequentistFit > /dev/null
		fi
		#if [ ! -e $regionPATH/higgsCombineAltSig1.GenerateOnly.mH125.123456.root ] || [ $runGen ]
		#then
		#	echo "Running GEN for AltSig1"
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=1 --toysFrequentist -t 500 --expectSignal 1 -n AltSig1 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_p2_2,${region}_p1_2 > /dev/null
		#fi
		#if [ ! -e $regionPATH/higgsCombineMainSig1Main.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig1Main.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
		#then
		#	echo "M1M"
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0,${region}_${year}_p2_2_alt=0,${region}_${year}_p1_2_alt=0 --toysFile $regionPATH/higgsCombineMainSig1.GenerateOnly.mH125.123456.root -n MainSig1Main --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_${year}_p2_2_alt,${region}_${year}_p1_2_alt --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p2_2,${region}_p1_2 --saveNormalizations > /dev/null
		#fi
		if [ $runFit == 1 ]
		then
			echo "M0M"		
			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0,${region}_${year}_p2_2_alt=0,${region}_${year}_p1_2_alt=0 --toysFile $regionPATH/higgsCombineMainSig0.GenerateOnly.mH125.123456.root -n MainSig0Main -t 1000  --rMin -20 --rMax 20 --minos none --freezeParameters pdf_index_${region}_${year},${region}_p2_2_alt,${region}_p1_2_alt,${region}_p2_2,${region}_p1_2 --cminDefaultMinimizerStrategy 0 --robustFit 1 --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p2_2,${region}_p1_2 --saveNormalizations --bypassFrequentistFit > /dev/null
		fi
		#if [ ! -e $regionPATH/higgsCombineMainSig1Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig1Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
		#then	
		#	echo "M1A"	
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineMainSig1.GenerateOnly.mH125.123456.root -n MainSig1Alt --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy > /dev/null
		#fi
		#if [ ! -e $regionPATH/higgsCombineMainSig0Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig0Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
		#then
		#	echo "M0A"		
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineMainSig0.GenerateOnly.mH125.123456.root -n MainSig0Alt --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy > /dev/null
		#fi
		#if [ ! -e $regionPATH/higgsCombineAltSig1Main.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig1Main.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
		#then
		#	echo "A1M"
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineAltSig1.GenerateOnly.mH125.123456.root -n AltSig1Main --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p2_2,${region}_p1_2 --saveNormalizations > /dev/null
		#fi
		if [ $runFit == 1 ]
		then
			echo "A0M"
			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineAltSig0.GenerateOnly.mH125.123456.root -n AltSig0Main -t 1000 --rMin -20 --rMax 20 --minos none --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p2_2,${region}_p1_2 --saveNormalizations --bypassFrequentistFit > /dev/null #2>&1
		fi
		#if [ ! -e $regionPATH/higgsCombineAltSig0Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig1Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
		#then
		#	echo "A1A"
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=1,${region}_p2_2=0,${region}_p1_2=0 --toysFile $regionPATH/higgsCombineAltSig1.GenerateOnly.mH125.123456.root -n AltSig1Alt -t 500 --rMin -5 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_p2_2,${region}_p1_2 --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy > /dev/null
		#fi
		#if [ ! -e $regionPATH/higgsCombineAltSig0Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig0Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
		#then
		#	echo "A0A"
		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=1,${region}_p2_2=0,${region}_p1_2=0 --toysFile $regionPATH/higgsCombineAltSig0.GenerateOnly.mH125.123456.root -n AltSig0Alt -t 500 --rMin -5 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_p2_2,${region}_p1_2 --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy > /dev/null
		#fi
		cd ..
	done
done

#for region in highSVJ2
#do
#	regionPATH="${testDIR}${wsDIR}${region}"
#	#echo $regionPATH
#	for year in 2018
#	do
#		echo "Performing bias test for region $region"
#		echo $wsPATH
#		echo $regionPATH
#		if [ ! -d $regionPATH ]
#		then
#			echo "Destination directory for $region doesn't exits. Making..."
#			mkdir $regionPATH
#		fi
#		cd $regionPATH
#		if [ ! -e $regionPATH/higgsCombineMainSig1.GenerateOnly.mH125.123456.root ] || [ $runGen ]
#		then
#			echo "Running GEN for MainSig0"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=0 --toysFrequentist -t 500 --expectSignal 1 -n MainSig1 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_${year}_p2_2_alt,${region}_${year}_p1_2_alt  #> $regionPATH/combineLog_MainSig1.out #2>&1
#		fi
#		if [ ! -e $regionPATH/higgsCombineMainSig0.GenerateOnly.mH125.123456.root ] || [ $runGen ]
#		then
#			echo "Running GEN for MainSig1"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=0 --toysFrequentist -t 500 --expectSignal 0 -n MainSig0 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_${year}_p2_2_alt,${region}_${year}_p1_2_alt #> $regionPATH/combineLog_MainSig0.out #2>&1
#		fi
#		if [ ! -e $regionPATH/higgsCombineAltSig1.GenerateOnly.mH125.123456.root ] || [ $runGen ]
#		then
#			echo "Running GEN for AltSig0"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=1 --toysFrequentist -t 500 --expectSignal 1 -n AltSig1 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_p1_1 #> $regionPATH/combineLog_AltSig1.out 2>&1
#		fi
#		if [ ! -e $regionPATH/higgsCombineAltSig0.GenerateOnly.mH125.123456.root ] || [ $runGen ]
#		then
#			echo "Running GEN for AltSig1"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M GenerateOnly --setParameters pdf_index_${region}_${year}=1 --toysFrequentist -t 500 --expectSignal 0 -n AltSig0 --saveToys -m 125 --freezeParameters pdf_index_${region}_${year},${region}_p1_1 #> $regionPATH/combineLog_AltSig0.out 2>&1
#		fi
#		if [ ! -e $regionPATH/higgsCombineMainSig1Main.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig1Main.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		then
#			echo "M1M"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0,${region}_${year}_p2_2_alt=0,${region}_${year}_p1_2_alt=0 --toysFile $regionPATH/higgsCombineMainSig1.GenerateOnly.mH125.123456.root -n MainSig1Main --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_${year}_p2_2_alt,${region}_${year}_p1_2_alt --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p1_1 --saveNormalizations #> $regionPATH/combineLog_MainSig1Main.out #2>&1
#		fi
#		if [ ! -e $regionPATH/higgsCombineMainSig0Main.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig0Main.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		then
#			echo "M0M"		
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0,${region}_${year}_p2_2_alt=0,${region}_${year}_p1_2_alt=0 --toysFile $regionPATH/higgsCombineMainSig0.GenerateOnly.mH125.123456.root -n MainSig0Main --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_${year}_p2_2_alt,${region}_${year}_p1_2_alt --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p1_1 --saveNormalizations #> $regionPATH/combineLog_MainSig0Main.out #2>&1
#		fi
#		#if [ ! -e $regionPATH/higgsCombineMainSig1Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig1Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		#then	
#		#	echo "M1A"	
#		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineMainSig1.GenerateOnly.mH125.123456.root -n MainSig1Alt --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy #> $regionPATH/combineLog_MainSig1Main.out #2>&1
#		#fi
#		#if [ ! -e $regionPATH/higgsCombineMainSig0Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineMainSig0Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		#then
#		#	echo "M0A"		
#		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineMainSig0.GenerateOnly.mH125.123456.root -n MainSig0Alt --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy #> $regionPATH/combineLog_MainSig1Main.out #2>&1
#		#fi
#		if [ ! -e $regionPATH/higgsCombineAltSig1Main.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig1Main.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		then
#			echo "A1M"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineAltSig1.GenerateOnly.mH125.123456.root -n AltSig1Main --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p1_1 --saveNormalizations #> $regionPATH/combineLog_MainSig1Main.out #2>&1
#		fi
#		if [ ! -e $regionPATH/higgsCombineAltSig0Main.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig0Main.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		then
#			echo "A0M"
#			combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=0 --toysFile $regionPATH/higgsCombineAltSig0.GenerateOnly.mH125.123456.root -n AltSig0Main --toysFrequentist -t 500  --rMin -10 --rMax 10 --freezeParameters pdf_index_${region}_${year} --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy --trackParameters ${region}_p1_1 --saveNormalizations #> $regionPATH/combineLog_MainSig1Main.out #2>&1
#		fi
#		#if [ ! -e $regionPATH/higgsCombineAltSig1Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig1Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		#then
#		#	echo "A1A"
#		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=1,${region}_p1_1=0 --toysFile $regionPATH/higgsCombineAltSig1.GenerateOnly.mH125.123456.root -n AltSig1Alt -t 500 --rMin -5 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_p1_1 --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy #> $regionPATH/combineLog_AltSig1Alt.out #2>&1
#		#fi
#		#if [ ! -e $regionPATH/higgsCombineAltSig0Alt.FitDiagnostics.mH120.123456.root ] || [ $(stat -c%s $regionPATH/higgsCombineAltSig0Alt.FitDiagnostics.mH120.123456.root) -lt 500 ] || [ $runFit ]
#		#then
#		#	echo "A0A"
#		#	combine $wsPATH/SVJ_mZprime3000_mDark20_rinv03_alphapeak_${region}_${year}_template_bias.txt -M FitDiagnostics --setParameters pdf_index_${region}_${year}=1,${region}_p1_1=0 --toysFile $regionPATH/higgsCombineAltSig0.GenerateOnly.mH125.123456.root -n AltSig0Alt -t 500 --rMin -5 --rMax 10 --freezeParameters pdf_index_${region}_${year},${region}_p1_1 --cminDefaultMinimizerStrategy 0 --robustFit 1 --minos none --verbose 4 --cminDefaultMinimizerType Minuit --cminDefaultMinimizerAlgo Simplex --savePredictionsPerToy #> $regionPATH/combineLog_AltSig0Alt.out #2>&1
#		#fi
#		cd ..
#	done
#done



