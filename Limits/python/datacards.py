import ROOT
import os, sys
from Stat.Limits.settings import *


#*******************************************************#
#                                                       #
#   getRate(process, ifile)                             #
#                                                       #
#   getCard(sig, ch, ifilename, outdir)                 #
#                                                       #
#*******************************************************#


#*******************************************************#
#                                                       #
#                     Utility Functions                 #
#                                                       #
#*******************************************************#


def getRate(ch, process, ifile):
       hName = ch + "/"+ process
       h = ifile.Get(hName)
       return h.Integral()




#*******************************************************#
#                                                       #
#                      Datacard                         #
#                                                       #
#*******************************************************#

def getCard(sig, ch, ifilename, outdir):

       try:
              ifile = ROOT.TFile.Open(ifilename)
       except IOError:
              print "Cannot open ", ifilename
       else:
              print "Opening file ",  ifilename
              ifile.cd()


       binString = (("%-43s") % (ch) ) * (len(processes)+1)

       rates = {}
       procLine = ""
       procNumbLine = ""
       rateLine = ""

       i = 1
       for p in processes:
              rates[p] = getRate(ch, p, ifile)
              procNumbLine += ("%-43s") % (i)
              procLine += ("%-43s") % (p)
              rateLine += ("%-43.1f") % (rates[p])
              i+=1

       rates["data_obs"] = getRate(ch, "data_obs", ifile)
       rates[sig] = getRate(ch, sig, ifile)

       card  = "imax 1 number of channels \n"
       card += "jmax * number of backgrounds \n"
       card += "kmax * number of nuisance parameters\n"
       card += "-----------------------------------------------------------------------------------\n"
       card += "shapes   *      *   %s    %s    %s\n" % (ifilename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_SYSTEMATIC")
       #card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (modelBkg.GetName(), channel, WORKDIR, category, "VH_2016:$PROCESS")
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin               %s\n" % ch
       card += "observation       %0.d\n" % (rates["data_obs"])
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin                                     %-43s\n" % (binString)
       card += "process                                 %-43s%-43s\n" % (sig, procLine) #"roomultipdf"
       card += "process                                 %-43s%-43s\n" % ("0", procNumbLine)
       card += "rate                                    %-43.6f%-43s\n" % (rates[sig], rateLine) #signalYield[m].getVal(), nevents
       card += "-----------------------------------------------------------------------------------\n"

       for sysName,sysValue  in syst.iteritems():
              card += "%-20s%-20s" % (sysName, sysValue[0])
              if (sysValue[0]=="lnN" and sysValue[1]=="all"): card += "%-20s" % (sysValue[2]) * (len(processes) + 1)
              elif (sysValue[0]=="lnN" and not sysValue[1]=="all"):
                     hsysName =  "_" + sysName  
                     hsysNameUp = "_" + sysName + "UP"  
                     hsysNameDown = "_" + sysName + "DOWN" 
                     sigSys = (getRate(ch, sig+hsysNameUp, ifile) - getRate(ch, sig+hsysNameDown, ifile))/ getRate(ch, sig+hsysName, ifile)
                     card += "%-20s" % (sigSys)
                     for p in processes:
                            bkgSys = (getRate(ch, p+hsysNameUp, ifile) - getRate(ch, p+hsysNameDown, ifile))/ getRate(ch, p+hsysName, ifile)
                            card += "%-20s" % (bkgSys)
              elif(sysValue[0]=="shape"):card += "%-20s" % ("-") * (len(processes) + 1)
              card += "\n"

       card += "%-20s%-20s%-20d\n " % (ch, "autoMCStats", 0)

       if not os.path.isdir(outdir): os.system('mkdir ' +outdir)
       if not os.path.isdir(outdir + "/" + sig): os.system('mkdir ' +outdir + "/" + sig)

       carddir = outdir+  "/" + sig + "/"
       outname =  "%s%s_%s.txt" % (carddir, sig, ch)
       cardfile = open(outname, 'w')
       cardfile.write(card)
       cardfile.close()

       
       print card
       return card




