import sys
import ROOT
from Stat.Limits.ftesting import *

channels = ["sr"]

ifilename = sys.argv[1]

ifile = ROOT.TFile.Open(ifilename)
print("Opening file ",ifilename)
ifile.cd()

years = []
for o in ROOT.gDirectory.GetListOfKeys():
    y = o.ReadObj().GetName().split("_")[0].replace("scsvj","")
    if y not in years:
        years.append(y)

bins = []
for y in years:
    for c in channels:
        bins.append("scsvj"+y+"_"+c+"__XXX"+"__nominal")

print(bins)

useChi2 = False
doplots = True

for b in bins:
    getCard(b, useChi2, doplots)

