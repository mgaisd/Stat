#! /usr/bin/env python
import sys
import os
import commands
import string
import optparse
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import ROOT as rt
from Stat.Limits.settings import *


# open root file from Kevin's EOS area
# print limits
# exit
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-f", "--file", dest="fName", type=str, required=True, help="fileName")
parser.add_argument("-z", "--mZprime", dest="mZprime", type=int, required=True, help="mZprime")
args = parser.parse_args()

_file = rt.TFile.Open("root://cmseos.fnal.gov//store/user/pedrok/SVJ2017/Limits/datacards_07tsb_sys/{}".format(args.fName),"read")

limitTree = _file.Get("limit")

#limitTree.Scan("limit:trackedParam_mZprime","quantileExpected==0.5")

for iEvt in range(limitTree.GetEntries()):
	limitTree.GetEvent(iEvt)
	if limitTree.quantileExpected == 0.5 and limitTree.trackedParam_mZprime == args.mZprime:
		if limitTree.limit <= 5.0:
			print "{}".format(limitTree.limit)
		else:
			print("5")
_file.Close()
