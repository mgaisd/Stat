import ROOT
import os, sys
import optparse
from Stat.Limits.settings import *
from Stat.Limits.datacards import *

print sigpoints


channels = ["BDT0", "BDT1", "BDT2", "CRBDT0", "CRBDT1", "CRBDT2"]

path = "/t3home/decosa/SVJ/CMSSW_8_1_0/src/ttDM/stat/test/"

usage = 'usage: %prog -p histosPath -o outputFile'
parser = optparse.OptionParser(usage)
parser.add_option('-i', '--input', dest='ifile', type='string', default= path + "histos.root",help='Where can I find input histos? Default is histos.root')
parser.add_option("-o","--outdir",dest="outdir",type="string",default="outdir",help="Name of the output directory where to store datacards. Default is outdir")
parser.add_option("-m","--mode",dest="mode",type="string",default="hist",help="Kind of shape analysis: parametric fit or fit to histos?. Default is hist")

(opt, args) = parser.parse_args()
sys.argv.append('-b')


ifilename = opt.ifile
outdir = opt.outdir
mode = opt.mode

signals = []

for p in sigpoints:

    mZprime=p[0]
    mDark=p[1]
    rinv=p[2]
    alpha=p[3]

    print "Creating datacards for mZprime = ", mZprime, " GeV, mDark = ", mDark, " GeV, rinv = ", rinv, " , alpha = ", alpha
    signal  = "SVJ_mZprime%s_mDark%s_rinv%s_alpha%s" % (mZprime, mDark, rinv, alpha) 
    signals.append(signal)


for s in signals:

    for ch in channels:
        getCard(s, ch, ifilename, outdir, mode)
