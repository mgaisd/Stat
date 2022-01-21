#!/bin/bash

./impacts.sh 3100 /store/user/pedrok/SVJ2017/Limits/datacards_Oct26/ "-t -1 --expectSignal 0" asimovSig0
./impacts.sh 3100 /store/user/pedrok/SVJ2017/Limits/datacards_Oct26/ "-t -1 --expectSignal 0.5871519" asimovSigRexp cut
./impacts.sh 3100 /store/user/pedrok/SVJ2017/Limits/datacards_Oct26/ "-t -1 --expectSignal 0.0780079" asimovSigRexp bdt
