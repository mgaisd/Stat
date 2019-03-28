import os
import subprocess
import optparse

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

#vec1 = ("1000", "20", "03", "02")
#vec2 = ("2000", "20", "03", "02")
#vec3 = ("3000", "20", "03", "02")
#vec4 = ("4000", "20", "03", "02")
#vec5 = ("3000", "1", "03", "02")
#vec6 = ("3000", "50", "03", "02")
#vec7 = ("3000", "100", "03", "02")
#vec8 = ("3000", "20", "01", "02")
#vec9 = ("3000", "20", "05", "02")
#vec10 = ("3000", "20", "07", "02")
#vec11 = ("3000", "20", "03", "01")
#vec12 = ("3000", "20", "03", "05")
#vec13 = ("3000", "20", "03", "1")

#points = [vec1, vec2, vec3, vec4, vec5, vec6, vec7, vec8, vec9, vec10, vec11, vec12, vec13]

vec1 = ("500", "20", "03", "peak")
vec2 = ("600", "20", "03", "peak")
vec3 = ("700", "20", "03", "peak")
vec4 = ("800", "20", "03", "peak")
vec5 = ("900", "20", "03", "peak")
vec6 = ("1000", "20", "03", "peak")
vec7 = ("1100", "20", "03", "peak")
vec8 = ("1200", "20", "03", "peak")
vec9 = ("1300", "20", "03", "peak")
vec10 = ("1400", "20", "03", "peak")
vec11 = ("1500", "20", "03", "peak")
vec12 = ("1600", "20", "03", "peak")
vec13 = ("1700", "20", "03", "peak")
vec14 = ("1800", "20", "03", "peak")
vec15 = ("1900", "20", "03", "peak")
vec16 = ("2000", "20", "03", "peak")
vec17 = ("2100", "20", "03", "peak")
vec18 = ("2200", "20", "03", "peak")
vec19 = ("2300", "20", "03", "peak")
vec20 = ("2400", "20", "03", "peak")
vec21 = ("2500", "20", "03", "peak")
vec22 = ("2600", "20", "03", "peak")
vec23 = ("2700", "20", "03", "peak")
vec24 = ("2800", "20", "03", "peak")
vec25 = ("2900", "20", "03", "peak")
vec26 = ("3000", "20", "03", "peak")
vec27 = ("3100", "20", "03", "peak")
vec28 = ("3200", "20", "03", "peak")
vec29 = ("3300", "20", "03", "peak")
vec30 = ("3400", "20", "03", "peak")
vec31 = ("3500", "20", "03", "peak")
vec32 = ("3600", "20", "03", "peak")
vec33 = ("3700", "20", "03", "peak")
vec34 = ("3800", "20", "03", "peak")
vec35 = ("3900", "20", "03", "peak")
vec36 = ("4000", "20", "03", "peak")
vec37 = ("4100", "20", "03", "peak")
vec38 = ("4200", "20", "03", "peak")
vec39 = ("4300", "20", "03", "peak")
vec40 = ("4400", "20", "03", "peak")
#vec41 = ("4500", "20", "03", "peak")
vec41 = ("3000", "20", "0", "peak")

#points = [vec1, vec2, vec3, vec4, vec5, vec6, vec7, vec8, vec9, vec10, vec11, vec12, vec13, vec14, vec15, vec16, vec17, vec18, vec19, vec20, vec21, vec22, vec23, vec24, vec25, vec26, vec27, vec28, vec29, vec30, vec31, vec32, vec33, vec34, vec35, vec36, vec37, vec38, vec39, vec40, vec41]

points = [vec26]


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

                    runCombine("combine -M Asymptotic -S " + opt.syst + " -n SVJ_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha + "_" + cat + " -m %s SVJ_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha  + "_" + cat +".txt", "asymptotic_mZprime" + mZprime + "_mDark" + mDark + "_rinv" + rinv + "_alpha" + alpha  + "_" + cat + ".log")  
                    
                    if(opt.sig > 0): 
                        runCombine("combine -M ProfileLikelihood -S " + opt.syst + " -n SVJ" + post + 
                                   " -m %s --signif --pvalue -t 1000 --toysFreq --expectSignal=1 SVJ" + post + ".txt",
                                   "profileLikelihood" + post + ".log")
                    
            os.chdir("..");
