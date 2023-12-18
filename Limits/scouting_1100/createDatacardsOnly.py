import os, sys
#from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
import ROOT
from Stat.Limits.datacarding import *

'''
parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument('-i', '--input', dest='ifile', type=str, default= "root://cmseos.fnal.gov//store/user/pedrok/SVJ2017/Datacards/trig4/sigfull/",help='Where can I find input histos? trig4/sigfull = new (24 July 2020) files created by Kevin')
parser.add_argument('-w', '--workspaceDir', dest='workspaceDir', type=str, default="root://cmseos.fnal.gov//store/user/cfallon/datacards_aCrit07/",help='Location of F-test output files ws_{}.root')
parser.add_argument("-m","--mode",dest="mode",type=str,default="hist",help="Kind of shape analysis: parametric fit or fit to histos?")
parser.add_argument("-Z", "--zMass", dest="mZ", type=str,help="Mass [GeV] of the Z' in MC signal. range: [500, 4400] in steps of 100, inclusive", default='2900')
parser.add_argument("-D", "--dMass", dest="mD", type=str, help="Mass [GeV] of dark quarks in MC signal", default = '20')
parser.add_argument("-R", "--rInv", dest="rI", type=str, help="Fraction of invisible particles in MC signal", default = '03')
parser.add_argument("-A", "--aDark", dest="aD", type=str, help="alphaDark value in MC signal. Options: 'low', 'peak', 'high'", default = "peak")
parser.add_argument("-t", "--test", dest="bias", action="store_true", default=False)
parser.add_argument("-s", "--noSys",dest="doSys",action='store_false', default=True)
opt = parser.parse_args()
sys.argv.append('-b')
'''

channels = ["sr"]
sigpoints = []
ifilename = sys.argv[1]
signals = []

sigpoints.append([sys.argv[2], "20", "0.3", "peak"])

for p in sigpoints:
    mZprime=p[0]
    mDark=p[1]
    rinv=p[2]
    alpha=p[3]
    print "Creating datacards for mZprime = ", mZprime, " GeV, mDark = ", mDark, " GeV, rinv = ", rinv, " , alpha = ", alpha
    #signal  = "SVJ_mZprime%s_mDark%s_rinv%s_alpha%s" % (mZprime, mDark, rinv, alpha) 
    signal = "SVJ%s" % (mZprime)
    signals.append(signal)

ifile = ROOT.TFile.Open(ifilename)
print("Opening file ", ifilename)
ifile.cd()
    
years = []   

for o in ROOT.gDirectory.GetListOfKeys():
    y = o.ReadObj().GetName().split("_")[0].replace("scsvj","")
    if y not in years:
        years.append(y)
    
bins = []

for y in years:
    for c in channels:
        #bins.append("scsvj"+y+"_"+c+"__XXX"+"__nominal")
        bins.append("scsvj"+y+"_"+c)
print(bins)    

#cmd = "rm ws.root"
#os.system(cmd)

for s in signals:
    mode = "template" #swap between template and histo(in code only !template)
    doSys = True
    for b in bins:
        getCard(s, b, ifilename, mode, doSys)
