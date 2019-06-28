
import ROOT
from ROOT import RooRealVar, RooDataHist, RooArgList, RooGenericPdf, RooExtendPdf, RooWorkspace, RooFit
import os, sys
from array import array
import copy, math, pickle

import numpy as np

from Stat.Limits.settings import *


ROOT.TH1.SetDefaultSumw2()
ROOT.TH1.AddDirectory(False)
ROOT.gROOT.SetStyle('Plain')
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetPadBorderMode(0)
ROOT.gStyle.SetPadColor(0)

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


isData = False

def getRate(ch, process, ifile):
       hName = ch + "/"+ process
       h = ifile.Get(hName)
       return h.Integral()

def getHist(ch, process, ifile):
       hName = ch + "/"+ process
       print "Histo Name ", hName
       h = ifile.Get(hName)
       h.SetDirectory(0)
       return h





def getRSS(ch, variable, model, dataset, fitRes,  norm = -1):
       name = model.GetName()
       order = int(name[-1])
       npar = fitRes[0].floatParsFinal().getSize() if len(fitRes)>0 else 0
       varArg = ROOT.RooArgSet(variable)
      
       frame = variable.frame()

       dataset.plotOn(frame, RooFit.Invisible())
       if len(fitRes) > 0: model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Range("Full"))
       model.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(model.GetName()),  RooFit.Range("Full"))
       model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.45, 0.95, 0.94), RooFit.Format("NEAU"))
       

       graphData = dataset.plotOn(frame, RooFit.DataError(ROOT.RooAbsData.Poisson if isData else ROOT.RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(dataset.GetName()))

       #(ROOT.TVirtualFitter.GetFitter()).GetConfidenceIntervals(model)       

       #f1 = ROOT.TF1(model)
       #f1.SetName("f")
       #f2 = ROOT.TF1(model)
       #f2.SetName("g")
       #nPar = f2.GetNpar()
       #errorpar = np.zeros(nPar)

       #f2.SetParErrors()
       #f3 = ROOT.TF1("error", "f/g")
       
       pulls = frame.pullHist(dataset.GetName(), model.GetName(), True)
       residuals = frame.residHist(dataset.GetName(), model.GetName(), False, True) # this is y_i - f(x_i)
    

       roochi2 = frame.chiSquare()#dataset.GetName(), model.GetName()) #model.GetName(), dataset.GetName()
       frame.SetMaximum(frame.GetMaximum()*1.2)
       frame.SetMinimum(0.01)
    
       print "==========================> minimum: ", frame.GetMinimum()

       c = ROOT.TCanvas("c_"+ch+model.GetName(), ch, 800, 800)

       c.cd()
       pad1 = ROOT.TPad("pad1", "pad1", 0., 0.35, 1., 1.0)
       ROOT.SetOwnership(pad1, False)
       pad1.SetBottomMargin(0.);
       pad1.SetGridx();
       pad1.SetGridy();
       pad1.SetLogy()
       pad1.Draw()
       pad1.cd()
       frame.Draw()
      
    
       c.cd()
       #pad1.SetLogy()       
       c.Update()
       c.cd()
       pad2 = ROOT.TPad("pad2", "pad2", 0, 0.05, 1, 0.3)
       ROOT.SetOwnership(pad2, False)
       pad2.SetTopMargin(0);
       pad2.SetBottomMargin(0.1);
       pad2.SetGridx();
       pad2.SetGridy();
       pad2.Draw();
       pad2.cd()
       pad2.Clear()
       #frame.Draw()
       c.Update()
       c.Modified()
       
       frame_res = variable.frame()

       frame_res.addPlotable(residuals, "P")
       frame_res.GetYaxis().SetRangeUser(-5., 5.)
       frame_res.GetYaxis().SetTitle("(N^{data}-f(i))/#sigma")

       frame_res.Draw("e0SAME")
       hist = graphData.getHist()
       xmin_ = graphData.GetXaxis().GetXmin()
       xmax_ = graphData.GetXaxis().GetXmax()
       c.Update()
       c.Range(xmin_, -5., xmax_, 5.)
       line = ROOT.TLine(xmin_, 0., xmax_, 0.)
       line.SetLineColor(ROOT.kRed)
       line.SetLineWidth(2)
       line.Draw("same")
       c.SaveAs( "Residuals/Residuals_"+ch+"_"+name+".pdf")


       c2 = ROOT.TCanvas("c2_"+ch+model.GetName(), ch, 800, 800)
       c2.cd()
       pad1_2 = ROOT.TPad("pad1_2", "pad1_2", 0., 0.35, 1., 1.0)
       ROOT.SetOwnership(pad1_2, False)
       pad1_2.SetBottomMargin(0.);
       pad1_2.SetGridx();
       pad1_2.SetGridy();
       pad1_2.SetLogy()
       pad1_2.Draw()
       pad1_2.cd()
       frame.Draw()
      

       c2.cd()
       #pad1_2.SetLogy()       
       c2.Update()
       c2.cd()
       pad2_2 = ROOT.TPad("pad2_2", "pad2_2", 0, 0.05, 1, 0.3)
       ROOT.SetOwnership(pad2_2, False)
       pad2_2.SetTopMargin(0);
       pad2_2.SetBottomMargin(0.1);
       pad2_2.SetGridx();
       pad2_2.SetGridy();
       pad2_2.Draw();
       pad2_2.cd()
       pad2_2.Clear()
       #frame.Draw()
       c2.Update()
       c2.Modified()



       # calculate RSS
       res, rss, chi1, chi2 = 0, 0., 0., 0., 

       xmin, xmax = array('d', [0.]), array('d', [0.])
       dataset.getRange(variable, xmin, xmax)
       print "N bins: ", hist.GetN()
       nBins = graphData.GetNbinsX()
       ratioHist = ROOT.TH1F("RatioPlot", "Ratio Plot", hist.GetN(), xmin_, xmax_)
       ROOT.SetOwnership(ratioHist, False)

       print "We get at point 5"
 #      ratioHist.SetBins(nBins, graphData.GetXaxis().GetXbins().GetArray())

       hist.Dump()
       ratioHist.Dump()
       ratioHist.Print('all')
       for i in xrange(0, hist.GetN()):
              print "CHECKING HISTO ", i

              print "bin content ", hist.GetY()[i]
	
	      hx, hy = hist.GetX()[i], hist.GetY()[i]
	      hey = hist.GetErrorY(i)
              hexlo, hexhi = hist.GetErrorXlow(i), hist.GetErrorXhigh(i)
              ry = residuals.GetY()[i]
              pull = pulls.GetY()[i] 


	      print hist.GetX()[i], hist.GetY()[i], hist.GetErrorXlow(i), hist.GetErrorXhigh(i)
              print residuals.GetY()[i]
              print pulls.GetY()[i]

	      if (hx - hexlo) > xmax[0] and hx + hexhi > xmax[0]:
		continue

              if hy <= 0.:
                continue
              
              res += ry
              print "residuals ", ry
              rss += ry**2 

	      print pull
	      chi1 += abs(pull)
              chi2 += pull*2

              print " Residual: ", ry, "Bin Content: ", hy, " new bin: ", (ry-hy)/(-1*hy)

              ratioHist.SetBinContent(i+1, (ry - hy)/(-1*hy))
	      print "ERROR: ", hey, hy**2
              ratioHist.SetBinError(i+1, (hey/ hy**2))
	      ratioHist.Print('all')
 	      
             # if hist.GetX()[i] - hist.GetErrorXlow(i) > xmax[0] and hist.GetX()[i] + hist.GetErrorXhigh(i) > xmax[0]: continue# and abs(pulls.GetY()[i]) < 5:
             # if hist.GetY()[i] <= 0.: continue
             # res += residuals.GetY()[i]
             # print "residuals ", residuals.GetY()[i]
             # rss += residuals.GetY()[i]**2

             # print pulls.GetY()[i]       
             # chi1 += abs(pulls.GetY()[i])
             # chi2 += pulls.GetY()[i]**2
             # print " Residual: ", residuals.GetY()[i], " Bin Content: ", hist.GetY()[i], " new bin: ", (residuals.GetY()[i] - hist.GetY()[i])/(-1 * hist.GetY()[i])
             # ratioHist.SetBinContent(i, (residuals.GetY()[i] - hist.GetY()[i])/(-1*hist.GetY()[i]))
             # print "ERROR: ", hist.GetHistogram().GetBinError(i)
             # ratioHist.SetBinError(i, (hist.GetHistogram().GetBinError(i)/ pow(hist.GetY()[i],2)))

       rss = math.sqrt(rss)
       out = {"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : hist.GetN(), "npar" : npar}
       #c.SaveAs(carddir + "/plots/Residuals_"+ch+"_"+name+".pdf")

     

       
       ratioHist.GetYaxis().SetRangeUser(0.,2.)
       ratioHist.GetYaxis().SetTitle("f(i)/N^{data}")
       #ratioHist.SetMarkerSize(2)
       ratioHist.SetMarkerStyle(20)
       ratioHist.Draw("PE")
       line2 = ROOT.TLine(xmin_, 1., xmax_, 1.)
       line2.SetLineColor(ROOT.kRed)
       line2.SetLineWidth(2)
       line2.Draw("same")

       c2.SaveAs( "Residuals/Residuals_"+ch+"_"+name+"_ratio.pdf")
       return out



def fisherTest(RSS1, RSS2, o1, o2, N):
       print "Testing functions with parameters o1 ", o1, " and o2 ", o2, " with RSS RSS1 ", RSS1, " and RSS2 ", RSS2, " and N ", N
       n1 = o1
       n2 = o2
       F = ((RSS1-RSS2)/(n2-n1)) / (RSS2/(N-n2))
       print "***************** Value of F: ", F
       CL =  1.-ROOT.TMath.FDistI(F, n2-n1, N-n2)
       return CL


#*******************************************************#
#                                                       #
#                      Datacard                         #
#                                                       #
#*******************************************************#

def getCard(sig, ch, ifilename, outdir, mode = "histo", unblind = False, verbose = False):


       try:
              ifile = ROOT.TFile.Open(ifilename)
       except IOError:
              print "Cannot open ", ifilename
       else:
              print "Opening file ",  ifilename
              ifile.cd()

       
       workdir_ = ifilename.split("/")[:-1]
       WORKDIR = "/".join(workdir_) + "/"
       carddir = outdir+  "/"  + sig + "/"
       if not os.path.isdir(outdir): os.system('mkdir ' +outdir)
       if not os.path.isdir(outdir + "/" + sig): os.system('mkdir ' +carddir) 
       if not os.path.isdir(outdir + carddir + "plots/"): os.system('mkdir ' +carddir + "plots/") 
       if not os.path.isdir(outdir + carddir + "Fisher/"): os.system('mkdir ' +carddir + "Fisher/") 


       hist_filename = os.getcwd()+"/"+ifilename
       hist = getHist(ch, sig, ifile)


       #*******************************************************#
       #                                                       #
       #                   Generate workspace                  #
       #                                                       #
       #*******************************************************#


    
       if(mode == "template"):

              ###ATT: CHECK BKG AND DATA NORMALIZATION AND DISTRIBUTION
              histBkgData = getHist(ch, "Bkg", ifile)
              histData = histBkgData
              if (unblind):  
                     print "BE CAREFULL: YOU ARE UNBLINDING"
                     histData = getHist(ch, "data_obs", ifile)
                     print "*********Number of data ", histData.Integral()
              print "channel ", ch             
              print "channel ", sig

              histSig = getHist(ch, sig, ifile)
              #print "histSigData: ", histSig.Integral()
              #print "histBkgData: ", histBkgData.Integral()
              mT = RooRealVar(  "m_T",    "m_{T}",          1500., 3800., "GeV")
              edge1 = 2000
              edge2 = 2200
              norm_tosub = 0
              for i in xrange(0, histData.GetNbinsX()):
                    if histData.GetBinContent(i) > 0. and  histData.GetBinError(i)/histData.GetBinContent(i) > 0.30: 
                           edge1 = histData.GetBinLowEdge(i)
                           edge2 = histData.GetBinLowEdge(i) + histData.GetBinWidth(i)
                           print "Excluded [", edge1," , ", edge2, "]"
                           norm_tosub +=  histData.GetBinContent(i)

              mT.setRange("Low", 1500, edge1)
              mT.setRange("High", edge2, 3800)
              bkgData = RooDataHist("bkgdata", "Data (MC Bkg)",  RooArgList(mT), histBkgData, 1.)
              obsData = RooDataHist("data_obs", "(pseudo) Data",  RooArgList(mT), histData, 1.)
              sigData = RooDataHist("sigdata", "Data (MC sig)",  RooArgList(mT), histSig, 1.)
              #print "Bkg Integral: ", histData.Integral() 
              nBkgEvts = histBkgData.Integral() - norm_tosub
              #print "Bkg Events: ", nBkgEvts
              normBkg = RooRealVar("Bkg_"+ch+"_norm", "Number of background events", nBkgEvts, 0., 2.e4)
              p1_1 = RooRealVar(ch + "_p1_1", "p1", 1., -1000., 1000.)
              p1_2 = RooRealVar(ch + "_p1_2", "p1", 1., -1000., 1000.)
              p1_3 = RooRealVar(ch + "_p1_3", "p1", 1., -1000., 1000.)
              p1_4 = RooRealVar(ch + "_p1_4", "p1", 1., -1000., 1000.)
              p2_2 = RooRealVar(ch + "_p2_2", "p2", 1., -1000., 1000.)
              p2_3 = RooRealVar(ch + "_p2_3", "p2", 1., -1000., 1000.)
              p2_4 = RooRealVar(ch + "_p2_4", "p2", 1., -1000., 1000.)
              p3_3 = RooRealVar(ch + "_p3_3", "p3", 1., -1000., 1000.)
              p3_4 = RooRealVar(ch + "_p3_4", "p3", 1., -1000., 1000.)
              p4_4 = RooRealVar(ch + "_p4_4", "p4", 1., -1000., 1000.)
              
              modelName = "Bkg_"+ch
              modelBkg1 = RooGenericPdf(modelName+"1", "Bkg. fit (1 par.)", "pow(1 + @0/13000, @1) ", RooArgList(mT, p1_1))
              modelBkg2 = RooGenericPdf(modelName+"2", "Bkg. fit (2 par.)", "pow(1 + @0/13000, @1) * pow(@0/13000, -@2)", RooArgList(mT, p1_2, p2_2))
              modelBkg3 = RooGenericPdf(modelName+"3", "Bkg. fit (3 par.)", "pow(1 + @0/13000, @1) * pow(@0/13000, -@2-@3*log(@0/13000))", RooArgList(mT, p1_3, p2_3, p3_3))
              modelBkg4 = RooGenericPdf(modelName+"4", "Bkg. fit (4 par.)", "pow(1 + @0/13000, @1) * pow(@0/13000, -@2-log(@0/13000)*(@3 + @4* log(@0/13000)))", RooArgList(mT, p1_4, p2_4, p3_4, p4_4))



              RSS = {}
              fitrange = "Full"
              if (ch == "BDT1_2016"): fitrange = "Low,High"
              
              
              fitRes1 = modelBkg1.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1), RooFit.Range(fitrange))
              fitRes2 = modelBkg2.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1), RooFit.Range(fitrange))
              fitRes3 = modelBkg3.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1), RooFit.Range(fitrange))
              fitRes4 = modelBkg4.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1), RooFit.Range(fitrange))



              xframe = mT.frame(ROOT.RooFit.Title("extended ML fit example"))

              c1 = ROOT.TCanvas()
              c1.cd()
              bkgData.plotOn(xframe)

#              modelBkg1.plotOn(xframe,ROOT.RooFit.LineColor(ROOT.kGreen))
              modelBkg1.plotOn(xframe, ROOT.RooFit.LineColor(ROOT.kPink + 6), RooFit.Range("Full"))
              modelBkg2.plotOn(xframe, ROOT.RooFit.LineColor(ROOT.kBlue -4), RooFit.Range("Full"))
              modelBkg3.plotOn(xframe, ROOT.RooFit.LineColor(ROOT.kRed -4), RooFit.Range("Full"))
              modelBkg4.plotOn(xframe, ROOT.RooFit.LineColor(ROOT.kGreen +1), RooFit.Range("Full"))
              
              xframe.SetMinimum(0.0002)
              xframe.Draw()
              
              c1.SetLogy()
              c1.SaveAs(carddir+"/plots/TestAfterFit_"+ch+".pdf")



              RSS[1] = getRSS(ch, mT, modelBkg1, bkgData,  [fitRes1], nBkgEvts)
              RSS[2] = getRSS(ch, mT, modelBkg2, bkgData,  [fitRes2], nBkgEvts)
              RSS[3] = getRSS(ch, mT, modelBkg3, bkgData,  [fitRes3], nBkgEvts)
              RSS[4] = getRSS(ch, mT, modelBkg4, bkgData,  [fitRes4], nBkgEvts)
              
              print RSS[2]

              #**********************************************************
              #                    ALTERNATIVE MODEL                    *
              #**********************************************************
 
              p1_1_alt = RooRealVar(ch + "_p1_1_alt", "p1", 1., -1000., 1000.)
              p1_2_alt = RooRealVar(ch + "_p1_2_alt", "p1", 1., -1000., 1000.)
              p1_3_alt = RooRealVar(ch + "_p1_3_alt", "p1", 1., -1000., 1000.)
              p1_4_alt = RooRealVar(ch + "_p1_4_alt", "p1", 1., -1000., 1000.)
              p2_2_alt = RooRealVar(ch + "_p2_2_alt", "p2", 1., -1000., 1000.)
              p2_3_alt = RooRealVar(ch + "_p2_3_alt", "p2", 1., -1000., 1000.)
              p2_4_alt = RooRealVar(ch + "_p2_4_alt", "p2", 1., -1000., 1000.)
              p3_3_alt = RooRealVar(ch + "_p3_3_alt", "p3", 1., -1000., 1000.)
              p3_4_alt = RooRealVar(ch + "_p3_4_alt", "p3", 1., -1000., 1000.)
              p4_4_alt = RooRealVar(ch + "_p4_4_alt", "p4", 1, -1000., 1000.)

              
              modelAltName =  "Bkg_Alt_"+ch

              modelAlt1 = RooGenericPdf(modelAltName+"1", "Bkg. fit (1 par.)", "1. / pow( @0/13000, @1) ", RooArgList(mT, p1_1_alt))
              modelAlt2 = RooGenericPdf(modelAltName+"2", "Bkg. fit (2 par.)", "(exp(log( (@2 * @0/13000) + 1) ) )/ pow( @0/13000, @1) ", RooArgList(mT, p1_2_alt, p2_2_alt))
              modelAlt3 = RooGenericPdf(modelAltName+"3", "Bkg. fit (3 par.)", "(exp(log( (@2 * @0/13000) + 1) + @3 * @0/13000  ) )/ pow( @0/13000, @1) ", RooArgList(mT, p1_3_alt, p2_3_alt, p3_3_alt))
              modelAlt4 = RooGenericPdf(modelAltName+"4", "Bkg. fit (4 par.)", "(exp(log( (@2 * @0/13000) + 1) + @3 * @0/13000 + @4*pow(@0/13000, 2) ) )/ pow( @0/13000, @1) ", RooArgList(mT, p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt))


              RSS_alt = {}
              fitRes1_alt = modelAlt1.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1))
              fitRes2_alt = modelAlt2.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1))
              fitRes3_alt = modelAlt3.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1))
              fitRes4_alt = modelAlt4.fitTo(bkgData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1))


              # RSS_alt[2] = getRSS(ch, mT, modelAlt1, bkgData,  [fitRes1],  nBkgEvts)
              # RSS_alt[2] = getRSS(ch, mT, modelAlt2, bkgData,  [fitRes2],  nBkgEvts)
              #RSS_alt[3] = getRSS(ch, mT, modelAlt3, bkgData,  [fitRes3],  nBkgEvts)
              RSS_alt[4] = getRSS(ch, mT, modelAlt4, bkgData,  [fitRes4],  nBkgEvts)


              #xframeAlt = mT.frame(ROOT.RooFit.Title("extended ML fit example"))

              #c2 = ROOT.TCanvas()
              #c2.cd()
              #bkgData.plotOn(xframeAlt)

              #modelAlt1.plotOn(xframeAlt,ROOT.RooFit.LineColor(ROOT.kPink))
              #modelAlt2.plotOn(xframeAlt,ROOT.RooFit.LineColor(ROOT.kBlue))
              #modelAlt3.plotOn(xframeAlt,ROOT.RooFit.LineColor(ROOT.kRed))
              #modelAlt4.plotOn(xframeAlt,ROOT.RooFit.LineColor(ROOT.kGreen))
              
              #xframeAlt.SetMinimum(0.002)
              #xframeAlt.Draw()
              
              #c2.SetLogy()
              #c2.SaveAs(carddir+"/plots/TestAfterFit_"+ch+"_Alt.pdf")

              
             
              #*******************************************************#
              #                                                       #
              #                         Fisher                        #
              #                                                       #
              #*******************************************************#


              ofile = open(carddir+"/Fisher/FisherTest_%s.txt"%(ch),"w")
              report = "Results from Fisher Test for category %s \n" % (ch)
              report += "RSS1: %d \n" % ( RSS[1]['rss'])
              report += "RSS2: %d \n" % ( RSS[2]['rss'])
              report += "RSS3: %d \n" % (RSS[3]['rss'])
              report += "RSS4: %d \n" % (RSS[4]['rss'])
              report += "*******************************************************\n"

              
              order = 0
              print "-"*25
              print "function & $\\chi^2$ & RSS & ndof & F-test & result \\\\"
              print "\\hline"
              for o1 in xrange(1, 4):
                     o2 = min(o1+1 , 5)
              
                     CL = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], o1, o2, RSS[o1]["nbins"])
              
                     print "%d par vs %d par CL=%.2f  \n" % (o1, o2, CL),
                     report += "%d par vs %d par: CL=%.2f \n " % (o1, o2, CL)
                     if CL > 0.10: # The function with less parameters is enough
                            if not order:
                                   order = o1
                                   print "%d par are sufficient" % (o1)
                                   #report += "%d par are sufficient \n" % (o1)
                     else:
                            print "%d par are needed" % (o2),

                     print "\\\\"
              print "\\hline"
              print "-"*25   
              print "Order is", order, "("+ch+")"
              report += "Order is %d (%s)" % (order, ch)
              report += "%d par are sufficient" % (order)
              
              ofile.write(report)
              ofile.close()

              if order==1:
                     modelBkg = modelBkg1#.Clone("Bkg")
                     #modelAlt = modelBkg3#.Clone("BkgAlt")
                     #normzBkg = normzBkg2#.Clone("Bkg_norm")
                     fitRes = fitRes1
              elif order==2:
                     modelBkg = modelBkg2#.Clone("Bkg")
                     #modelAlt = modelBkg3#.Clone("BkgAlt")
                     #normzBkg = normzBkg2#.Clone("Bkg_norm")
                     fitRes = fitRes2
              elif order==3:
                     modelBkg = modelBkg3#.Clone("Bkg")
                     #modelAlt = modelBkg4#.Clone("BkgAlt")
                     #normzBkg = normzBkg3#.Clone("Bkg_norm")
                     fitRes = fitRes3
              elif order==4:
                     modelBkg = modelBkg4#.Clone("Bkg")
                     #modelAlt = modelBkg3#.Clone("BkgAlt")
                     #normzBkg = normzBkg4#.Clone("Bkg_norm")
                     fitRes = fitRes4
              else:
                     print "Functions with", order+1, "or more parameters are needed to fit the background"
                     exit()

              modelBkg.SetName(modelName)
              normBkg.SetName(modelName+"_norm")
              




              print "NormBkg ", nBkgEvts

              parSet = modelBkg.getParameters(bkgData)
              parSet.Print()
              argList = ROOT.RooArgList(parSet)
              parNames = [ argList[i].GetName() for i in xrange(0, len(parSet))]                                 


             # modelExt = RooExtendPdf(modelBkg.GetName(), modelBkg.GetTitle(), modelBkg, normzBkg)

              for i in xrange(0, len(parSet)):
                    print  argList[i].GetName(), "   ", argList[i].getVal()




              # create workspace
              w = RooWorkspace("SVJ", "workspace")
              # Dataset
              # ATT: include isData
              #getattr(w, "import")(bkgData, RooFit.Rename("Bkg"))
              getattr(w, "import")(obsData, RooFit.Rename("data_obs"))
              getattr(w, "import")(sigData, RooFit.Rename(sig))


              for i in xrange(hist.GetNbinsX()):
                     mcstatSysName = "mcstat_%s_%s_bin%d"  % (ch, sig, i+1)
                     #print mcstatSysName
                     #print sig + "_" + mcstatSysName + "Up"
                     mcstatSigUp = getHist(ch, sig + "_" + mcstatSysName + "Up", ifile)

                     #print "Integral  ", mcstatSigUp.Integral()
                     mcstatSigDown = getHist(ch, sig + "_" + mcstatSysName + "Down", ifile)
                     mcstatSigHistUp = RooDataHist(sig + "_" + mcstatSysName + "Up", "Data (MC sig)",  RooArgList(mT), mcstatSigUp, 1.)
                     mcstatSigHistDown = RooDataHist(sig + "_" + mcstatSysName + "Down", "Data (MC sig)",  RooArgList(mT), mcstatSigDown, 1.)
                     getattr(w, "import")(mcstatSigHistUp, RooFit.Rename(sig + "_" + mcstatSysName + "Up") )
                     getattr(w, "import")(mcstatSigHistDown, RooFit.Rename(sig + "_" + mcstatSysName + "Down") )

              
              for sysName,sysValue  in syst.iteritems():
                     if(sysValue[0]=="shape" and "mcstat" not in sysName):              
                            sysUp =  getHist(ch, sig + "_" + sysName + "Up", ifile)
                            sysDown =  getHist(ch, sig + "_" + sysName + "Down", ifile)
                            #print "==> Trigg sys name: ", sig + "_" + sysName + "Down"
                            sysSigHistUp = RooDataHist(sig + "_" + sysName + "Up", sysName + " uncertainty",  RooArgList(mT), sysUp, 1.)
                            sysSigHistDown = RooDataHist(sig + "_" + sysName + "Down", sysName + " uncertainty",  RooArgList(mT), sysDown, 1.)
                            getattr(w, "import")(sysSigHistUp, RooFit.Rename(sig + "_" + sysName + "Up") )
                            getattr(w, "import")(sysSigHistDown, RooFit.Rename(sig + "_" + sysName + "Down") )
                            


              #else: getattr(w, "import")(setToys, RooFit.Rename("data_obs"))
              getattr(w, "import")(modelBkg, RooFit.Rename(modelBkg.GetName()))
              #getattr(w, "import")(modelAlt, RooFit.Rename(modelAlt.GetName()))
              #getattr(w, "import")(normzBkg, RooFit.Rename(normzBkg.GetName()))
              wstatus = w.writeToFile("%sws_%s_%s_%s.root" % (carddir, sig, ch, mode), True)

              if wstatus == False : print "Workspace", "%sws_%s_%s_%s.root" % (carddir, sig, ch, mode) , "saved successfully"
              else: print "Workspace", "%sws_%s_%s_%s.root" % (carddir, sig, ch, mode) , "not saved successfully"
              workfile = "./ws_%s_%s_%s.root" % ( sig, ch, mode)
              # ======   END MODEL GENERATION   ======       
              if(verbose):w.Print()


       rates = {}
       procLine = ""
       procNumbLine = ""
       rateLine = ""
       binString = ""

       if(mode == "template"):       

              processes.append("Bkg")
              processes[:-1] = []
              rates["Bkg"] = nBkgEvts
              procLine += ("%-43s") % (modelBkg.GetName())
              rateLine += ("%-43s") % (rates["Bkg"])
              binString += (("%-43s") % (ch) ) * (2)
              procNumbLine = 1 
              
       else:
              i = 1
              bkgrate = 0
              for p in processes:
                     rates[p] = getRate(ch, p, ifile)
                     bkgrate =  rates[p]
                     procNumbLine += ("%-43s") % (i)
                     procLine += ("%-43s") % (p)
                     rateLine += ("%-43.1f") % (bkgrate)
                     i+=1
              binString += (("%-43s") % (ch) ) * (len(processes)+1)


       if ((not unblind) and (mode == "template")): 
              print "N.B: We are in blind mode. Using MC bkg data for data_obs"
              rates["data_obs"] = getRate(ch, "Bkg", ifile)
              print "Pseudo data rate: ", rates["data_obs"]
       else: rates["data_obs"] = getRate(ch, "data_obs", ifile)
        
       rates[sig] = getRate(ch, sig, ifile)



       card  = "imax 1 number of channels \n"
       card += "jmax * number of backgrounds \n"
       card += "kmax * number of nuisance parameters\n"
       card += "-----------------------------------------------------------------------------------\n"

       if(mode == "template"):
              #              card += "shapes   %s  %s    %s    %s    %s\n" % (sig, ch, ifilename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_SYSTEMATIC")
              #              card += "shapes            %-15s  %-5s    %s%s.root    %s\n" % (sig, ch, WORKDIR, ch, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s\n" % (modelBkg.GetName(), ch, workfile, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s    %s\n" % (sig, ch, workfile, "SVJ:$PROCESS", "SVJ:$PROCESS_$SYSTEMATIC")
              card += "shapes   %s  %s    %s    %s\n" % ("data_obs", ch, workfile, "SVJ:$PROCESS")

       else:  
              card += "shapes   *      *   %s    %s    %s\n" % (hist_filename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_$SYSTEMATIC")
              card += "shapes   data_obs      *   %s    %s\n" % (hist_filename, "$CHANNEL/$PROCESS")
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin               %s\n" % ch
       print "===> Observed data: ", rates["data_obs"]
       card += "observation       %0.d\n" % (rates["data_obs"])
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin                                     %-43s\n" % (binString)
       card += "process                                 %-43s%-43s\n" % (sig, procLine) #"roomultipdf"
       card += "process                                 %-43s%-43s\n" % ("0", procNumbLine)
       card += "rate                                    %-43.6f%-43s\n" % (rates[sig], rateLine) #signalYield[m].getVal(), nevents
       card += "-----------------------------------------------------------------------------------\n"



       for sysName,sysValue  in syst.iteritems():

              if(sysValue[0]=="lnN"): 
                     card += "%-20s%-20s" % (sysName, sysValue[0])
                     if(sysValue[1]=="all"and len(sysValue)>2):
                            if(mode == "template"): card += "%-20s" % (sysValue[2]) * (2)
                            else: card += "%-20s" % (sysValue[2]) * (len(processes) + 1)

                     else:
                            if (sysValue[1]=="all"):
                                   sysValue[1] = copy.deepcopy(processes)
                                   sysValue[1].append(sig)

                            hsysName =  "_" + sysName  
                            hsysNameUp = "_" + sysName + "UP"  
                            hsysNameDown = "_" + sysName + "DOWN" 
                                                        #print "Applying syst on ", sysValue[1]
                            if("sig" in sysValue[1]):
                                   if(getRate(ch, sig, ifile) != 0.): sigSys = abs((getRate(ch, sig+hsysNameUp, ifile) - getRate(ch, sig+hsysNameDown, ifile))/ (2* getRate(ch, sig, ifile)))
                                   else: sigSys = 1
                                   if(sigSys<1.and sigSys >0.): sigSys = sigSys + 1
                                   card += "%-20s" % (sigSys)
                            else:  card += "%-20s" % ("-")
                            for p in processes:
                                   if (p in sysValue[1]):
                                          if (getRate(ch, p, ifile) != 0.): bkgSys = abs((getRate(ch, p+hsysNameUp, ifile) - getRate(ch, p+hsysNameDown, ifile))/ (2* getRate(ch, p, ifile)) )
                                          else: bkgSys = 1
                                          if(bkgSys<1.and bkgSys >0.): bkgSys = bkgSys + 1
                                          card += "%-20s" % (bkgSys)
                                   else:  card += "%-20s" % ("-")



              elif(sysValue[0]=="lnU"):
                     card += "%-20s%-20s%-20s%-20s" % (sysName, sysValue[0], "-", sysValue[2])
              elif(sysValue[0]=="shape"):
                     if("mcstat" not in sysName):
                            card += "%-20s     shape     " % (sysName)
                            if ("sig" in sysValue[1]): card += "%-20s" % ( "1") 
                            else: card += "%-20s" % ( "-") 
                            for p in processes:
                                   if (p in sysValue[1]): card += "%-20s" % ( "1") 
                                   else: card += "%-20s" % ( "-") 
              

                     else:
                            # CAMBIARE NOME DELLA SYST                     
                            for samp in sysValue[1]:
                                   sampName = ""
                                   line = ""
                                   if (samp == "sig" or samp == "Sig"): 
            
                                          line = "%-20s" % ( "1") 
                                          line += "%-20s" % ("-") * (len(processes)) 
                                          sampName = sig
                                   elif(mode != "template"):
                                          
                                          line = "%-20s" % ( "-") 
                                          lineProc = ["%-20s" % ( "-") for x in xrange (len(processes))]
                                          if samp in processes: 
                                                 index = processes.index(samp)  
                                                 lineProc[index] = "1"
                                                 
                                          lineProc = "         ".join(lineProc)
                                          line += lineProc
                                          sampName =  samp

                                   else: continue


                                   for i in xrange(hist.GetNbinsX()):

                                          sysName = "mcstat_%s_%s_bin%d      "  % (ch, sampName, i+1)
                                          card += "%-20s   shape   " % (sysName)
                                          card += line
                                          card += "\n"        

              card += "\n"
       

       for par in parNames: card += "%-20s%-20s\n" % (par, "flatParam")

      # card += "\n"





       outname =  "%s%s_%s_%s.txt" % (carddir, sig, ch, mode)
       cardfile = open(outname, 'w')
       cardfile.write(card)
       cardfile.close()


    

       #print card
       return card




