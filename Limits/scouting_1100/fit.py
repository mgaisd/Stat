import sys
import ROOT
from Stat.Limits.fitting import *


channels = ["sr"]

ifilename = sys.argv[1]
sigpoints = []
sigpoints.append([sys.argv[2],"20","0.3","peak"])

signals = []
for p in sigpoints:
    mZprime = p[0]
    mDark=p[1]
    rinv = p[2]
    alpha = p[3]
    print("Creating datacards for mZprime = ", mZprime, " GeV, mDark = ", mDark, " GeV, rinv = ", rinv, " , alpha = ", alpha)
    #signal = "SVJ%s_mDark%s_rinv%s_alpha%s" % (mZprime, mDark, rinv, alpha)
    signal = "SVJ%s" % (mZprime)
    signals.append(signal)                     

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

for s in signals:
    for b in bins:
        getCard(s, b, ifilename)

