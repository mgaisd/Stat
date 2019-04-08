import os
import subprocess
import optparse
from Stat.Limits.settings import *

usage = 'usage: %prog [--cat N]'
parser = optparse.OptionParser(usage)
#parser.add_option('', '--mzprime', dest='mzprime', type='int', default = 1, help='Mediator mass')
#parser.add_option('', '--mdark', dest='mdark', type='int', default = 1, help='Dark mass')
parser.add_option("-c","--channel",dest="ch",type="string",default="all",help="Indicate channels of interest. Default is all")
parser.add_option("-y","--years",dest="years",type="string",default="2016",help="Indicate years of interest. Default is 2016")
parser.add_option('-s', '--syst', dest='syst', type='string', default = '1', help='Set the flag to 0 to remove systematics')
parser.add_option('-m', '--method', dest='method', type='string', default = 'hist', help='Run a single method (all, hist, template)')
parser.add_option('-S', '--sig', dest='sig', type='int', default = 0, help='Set the flag to 1 to enable significance computation')
parser.add_option('-d', '--dir', dest='dir', type='string', default = 'outdir', help='datacards direcotry')
parser.add_option('',"--runSingleCat",dest="runSingleCat",action='store_true', default=False)

(opt, args) = parser.parse_args()
#interaction = opt.interaction


path_ = "/t3home/decosa/SVJ/CMSSW_8_1_0/src/Stat/Limits/test/"
path_ += opt.dir


years = ["2016", "2017"]
if opt.years != "all": 
    y_clean = opt.years.replace(" ", "")
    years = y_clean.split(",")

categories = ["BDT0", "BDT1", "BDT2", "CRBDT0", "CRBDT1", "CRBDT2"]
methods = ["hist", "template"]
if opt.ch != "all": 
    ch_clean = opt.ch.replace(" ", "")
    categories = ch_clean.split(",")

if opt.method != "all": 
    meth_clean = opt.method.replace(" ", "")
    methods = meth_clean.split(",")
    


for y in years: 
    categories = [c + "_" + y for c in categories]

print "Combinining the following categories: ", categories


def runCombine(cmdStr, logFile):
    "run combine for a specific case"

    cmd = (cmdStr % mZprime)
    print os.getcwd()
    print cmd
    #writer = open(logFile, 'w') 
    #process = subprocess.call(cmd, shell = True, stdout=writer)
    print cmd + " 2>&1 | tee " + logFile
    os.system(cmd + " 2>&1 | tee " + logFile)
    return


points = [vec1, vec2, vec3, vec4, vec5, vec6, vec7, vec8, vec9, vec10, vec11, vec12, vec13, vec14, vec15, vec16, vec17, vec18, vec19, vec20, vec21, vec22, vec23, vec24, vec25, vec26, vec27, vec28, vec29, vec30, vec31, vec32, vec33, vec34, vec35, vec36, vec37, vec38, vec39, vec40, vec41]

#points = [vec26]


os.chdir(opt.dir)

for point in points:
    if 1>0:
        mZprime=point[0]
        mDark=point[1]
        rinv=point[2]
        alpha=point[3]
        
        print "evaluate limit for mZprime = ", mZprime, " GeV, mDark = ", mDark, " GeV, rinv = ", rinv, " , alpha = ", alpha 

        path = ("%s/SVJ_mZprime%s_mDark%s_rinv%s_alpha%s" % (path_, mZprime, mDark, rinv, alpha) ) 
        print "path: ", path
        if(os.path.exists(path)):
            os.chdir(path)
            for method in methods:
                if len(categories)>1: 
                    cmd = "combineCards.py SVJ_mZprime%s_mDark%s_rinv%s_alpha%s_*_%s.txt > SVJ_mZprime%s_mDark%s_rinv%s_alpha%s_%s.txt" % (mZprime, mDark, rinv, alpha, method, mZprime, mDark, rinv, alpha, method)
                    print cmd
                    os.system(cmd)
                    runCombine("combine -M Asymptotic -S " + opt.syst + " -n SVJ_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha + " -m %s SVJ_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha  + "_"  + method + ".txt", "asymptotic_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha  + "_" + method + ".log")  
            
                for cat in categories:
                    print "category: " + ("all" if cat=="" else cat)
                    cat = cat+"_"+method

                    if(opt.runSingleCat): runCombine("combine -M Asymptotic -S " + opt.syst + " -n SVJ_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha + "_" + cat + " -m %s SVJ_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha  + "_" + cat +".txt", "asymptotic_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha  + "_" + cat + ".log")  
                    
                    if(opt.runSingleCat and opt.sig > 0): 
                        runCombine("combine -M ProfileLikelihood -S " + opt.syst + " -n SVJ" + post + 
                                   " -m %s --signif --pvalue -t 1000 --toysFreq --expectSignal=1 SVJ" + post + ".txt",
                                   "profileLikelihood" + post + ".log")
                    
            os.chdir("..");
