# Stat
Machinery to produce datacards and run limits


To convert input files to combine-friendly format:

> python collectHistos.py  -i inputFolfer/ -o histos.root

The script will retrieve the year from the histos names.
In order to merge 2016 and 2017 root file, do:

> hadd histosFile.root histos2016.root histos2017.root

This file will be given as input to createDatacards.py script
to create a set of datacrds, for each region and for the combination

> python createDatacards -i histosFile.root -d outdir -m mode (hist or template) -c channels (list of regions, or all for including all of them) -u (to unblind)

To run all limits together in local: 

> python runCombine.py -c channel -y year -m method -d outdir 

To run all limits on the batch queques:

>  python batchLimits.py -c channel -y year -m method -d outdir 
 
> python getLimitData.py -y 2016 -d limitsRun2_v2/ -m template

> python brazilPlot.py -y year -m template 


# Updated method
Be warned, the following is super cobbled together with bits of twig and some string

Fisher testing and datacard writing are split into two jobs.
First, to do the F-tests and generate the workspaces:

> python createDatacardsFtest_pt1.py

Options

> -i inputFile directory, default is store/user/pedrok/SVJ2017/Datacards/trig4/sigfull

> -d output directory. unused?

> -m mode. default is hist, but template is more commonly used.

> -t test, Bool flag. without -t, no bias testing is done

> -u unblind Bool flag, also unused


After part1 is done running, run part2:
> python createDatacardsFtest_pt2.py

options

> -i inputFile directory, default is store/user/pedrok/SVJ2017/Datacards/trig4/sigfull

> -d output directory. unused?

> -m mode. default is hist, but template is more commonly used.

> -Z, -D, -R, -A specifify which signal to use. defaults are 2900, 20, 03, peak

> -t test, Bool flag. without -t, no bias testing is done

> -u unblind Bool flag, also unused


for Condor submission:
make sure to change directories in the following files:
Stat/Limits/test/condorScripts/scramTarEos.sh : lines 19, 27
Stat/Limits/test/condorScripts/datacardCreationFtest_pt1.sh : lines 7, 37
Stat/Limits/test/condorScripts/datacardCreationFtest_pt1.jdl : line 10 
Stat/Limits/test/condorScripts/datacardCreationFtest_pt2.sh : lines 7, 48 (the pt2.jdl doesn't require any change)
Stat/Limits/python/datacardsFtest_pt2.py : line 636

step 1 is to create the workspace:
> condor_submit datacardCreation_pt1.jdl

step 2 is to write the datacards:
> condor_submit datacardCreation_pt2.jdl

step 3 is to run the combine commands to do the bias testing:
> condor_submit combine_FourStepBias.jdl


