# Stat

## Updated method

Fisher testing and datacard writing are split into three jobs.

First, do all the fits:
```
python createFits.py
```

Second, to do the F-tests and generate the workspaces:
```
python createFtest.py
```

Third, create the datacards:
```
python createDatacardsOnly.py
```

for Condor submission:
make sure to change directories in the following files:
* Stat/Limits/test/condorScripts/scramTarEos.sh : lines 19, 27
* Stat/Limits/test/condorScripts/ftest.sh : lines 7, 37
* Stat/Limits/test/condorScripts/ftest.jdl : line 10 
* Stat/Limits/test/condorScripts/allFits.sh : lines 7, 37
* Stat/Limits/test/condorScripts/allFits.jdl : line 11 
* Stat/Limits/test/condorScripts/datacardsOnly.sh : lines 7, 48 (the jdl doesn't require any change)
* Stat/Limits/python/datacardsOnly.py : line 636

step 1, do all fits:
```
condor_submit allFits.jdl
```

step 2, do F-tests:
```
condor_submit ftest.jdl
```

step 3, create datacards:
```
condor_submit datacardsOnly.jdl
```

step 4, run the combine commands to do the bias testing:
```
condor_submit combine_FourStepBias.jdl
```


