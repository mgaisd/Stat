import ROOT
import json

#changed to no longer need the settings.py file
# -syst list is created here
# -rateParams list is created here
# -processes list is created here
# files now saved to base directory and exported to EOS after jobs completion


from ROOT import RooRealVar, RooDataHist, RooArgList, RooGenericPdf, RooBernstein, RooExtendPdf, RooCmdArg, RooWorkspace, RooFit, RooDataSet, RooArgSet, RooCategory, RooFitResult, RooCurve, RooParametricShapeBinPdf
import os, sys
from array import array
import copy, math, pickle
import collections
import numpy as np
from numpy import ndarray

ROOT.TH1.SetDefaultSumw2()
ROOT.TH1.AddDirectory(False)
ROOT.gROOT.SetStyle('Plain')
ROOT.gROOT.SetBatch()
ROOT.gStyle.SetPadBorderMode(0)
ROOT.gStyle.SetPadColor(0)


syst = collections.OrderedDict()
syst["lumi"] = ("lnN", "sig", 1.026) 

rateParams = {}
rateParams["lowSVJ1_2018"] = "TMath::Power(TMath::Range(0.01,0.99,@0),1)*TMath::Power(1-TMath::Range(0.01,0.99,@0*%s),1)/(TMath::Power(1-%s,1))"
rateParams["lowSVJ2_2018"] = "TMath::Power(TMath::Range(0.01,0.99,@0),2)*TMath::Power(1-TMath::Range(0.01,0.99,@0*%s),0)/(TMath::Power(1-%s,0))"
rateParams["highSVJ1_2018"] = "TMath::Power(TMath::Range(0.01,0.99,@0),1)*TMath::Power(1-TMath::Range(0.01,0.99,@0*%s),1)/(TMath::Power(1-%s,1))"
rateParams["highSVJ2_2018"] = "TMath::Power(TMath::Range(0.01,0.99,@0),2)*TMath::Power(1-TMath::Range(0.01,0.99,@0*%s),0)/(TMath::Power(1-%s,0))"


processes = ["QCD"]

#ROOT.Math.MinimizerOptions.SetDefaultTolerance(1e-3); 
#ROOT.Math.MinimizerOptions.SetDefaultPrecision(1e-8)
#*****************************************************
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

isData = True

def getRate(ch, process, ifile):
       hName = ch + "/"+ process
       h = ifile.Get(hName)
       #return h.Integral()
       return h.Integral(1,h.GetXaxis().GetNbins()-1)
       #return h.Integral(1,91)

def getHist(ch, process, ifile):
       hName = ch + "/"+ process
       print "Histo Name ", hName
       h = ifile.Get(hName)
       h.SetDirectory(0)
       return h




def getEfficiency(sig, channels, ifilename):

       try:
              ifile = ROOT.TFile.Open(ifilename)
       except IOError:
              print "Cannot open ", ifilename
       else:
              print "Opening file ",  ifilename
              ifile.cd()
              
       cdfilename = os.getcwd()+"/"+ifilename
       
       rates = {}
       for ch in channels:

              rates[ch] = getRate(ch, sig, ifile)

       sumjets = sum(rates.itervalues())*2
       print sumjets

       evts2SVJ = sum(i for ch, i in rates.iteritems() if "SVJ2" in ch)
       print evts2SVJ
       evts1SVJ = sum(i for ch, i in rates.iteritems() if "SVJ1" in ch)

       num = evts1SVJ + (2 * evts2SVJ)
       
       eff = num/sumjets
       return eff




def getRSS(sig, ch, variable, model, dataset, fitRes, carddir,  norm = -1, label = "nom"):
       name = model.GetName()
       npar = fitRes[0].floatParsFinal().getSize() if len(fitRes)>0 else 0
       #order = int(name[-1])
       order = npar
       varArg = ROOT.RooArgSet(variable)
      
       #frame = variable.frame()
       frame = variable.frame(ROOT.RooFit.Title(""))
       dataset.plotOn(frame, RooFit.Invisible())
       print("TEST A================================" + ch)
       print(fitRes[0].GetName())
       fitRes[0].Print()
       print("TEST B================================" + sig)
       #if len(fitRes) > 0: model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Range("Full"))
       if len(fitRes) > 0: graphFit = model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Range("Full"))

       print("TEST c================================")
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
    
       roochi2 = frame.chiSquare(model.GetName(), dataset.GetName(),npar)#dataset.GetName(), model.GetName()) #model.GetName(), dataset.GetName()
       print "forcing bins: 65"
       nbins = 65
       chi = roochi2 * ( nbins - npar)
       print "pls: ", chi,  nbins
       roopro = ROOT.TMath.Prob(chi, nbins - npar)

       frame.SetMaximum(frame.GetMaximum()*10.)
       frame.SetMinimum(0.1)
       print "==========> len(sig): ", len(sig)
       length = 1
       if(length<2):

              c = ROOT.TCanvas("c_"+ch+model.GetName(), ch, 800, 800)

              c.cd()
              pad1 = ROOT.TPad("pad1", "pad1", 0., 0.35, 1., 1.0)
              ROOT.SetOwnership(pad1, False)
              pad1.SetBottomMargin(0.)
              pad1.SetGridx()
              pad1.SetGridy()
              pad1.SetLogy()
              pad1.Draw()
              pad1.cd()

              frame.Draw()
              frame.SetTitle("")
              
              #txt = ROOT.TText(2500, 1000, "chiSquared: " + str(roochi2))
              #txt = ROOT.TText(2500, 6., "chiSquared: " + str(roochi2))
              roochi2_small = format(roochi2, '.2f')
              txt = ROOT.TText(0.65, 0.7, "chiSquared: " + str(roochi2_small))              
              txt.SetNDC()
              txt.SetTextSize(0.04) 
              txt.SetTextColor(ROOT.kRed) 
              txt.Draw();

              #txt_2 = ROOT.TText(2500, 800, "Prob: " + str(roopro))
              #txt_2 = ROOT.TText(2500, 2., "Prob: " + str(roopro))
              roopro_small = format(roopro, '.2f')
              txt_2 = ROOT.TText(0.65, 0.65, "prob: " + str(roopro_small))              
              txt_2.SetNDC()
              txt_2.SetTextSize(0.04) 
              txt_2.SetTextColor(ROOT.kRed) 
              txt_2.Draw();
              
              c.cd()
              c.Update()
              c.cd()
              pad2 = ROOT.TPad("pad2", "pad2", 0, 0.1, 1, 0.3)
              ROOT.SetOwnership(pad2, False)
              pad2.SetTopMargin(0);
              pad2.SetBottomMargin(0.25);
              pad2.SetGridx();
              pad2.SetGridy();
              pad2.Draw();
              pad2.cd()
              pad2.Clear()
       #frame.Draw()
              c.Update()
              c.Modified()

              frame_res = variable.frame(ROOT.RooFit.Title(""))
              frame_res.addPlotable(pulls, "P")
              frame_res.GetYaxis().SetRangeUser(-3.5, 3.5)
              frame_res.SetTitle("")
              frame_res.GetYaxis().SetTitle("(N^{data}-f(i))/#sigma")
              frame_res.GetYaxis().SetTitleOffset(.3)
              frame_res.GetXaxis().SetTitleOffset(1.)
              frame_res.GetYaxis().SetTitleSize(.13)
              frame_res.GetXaxis().SetTitle("m_{T} (GeV)")
              frame_res.GetXaxis().SetTitleSize(.13)
              frame_res.GetXaxis().SetLabelSize(.12)
              frame_res.GetYaxis().SetLabelSize(.12)
              frame_res.Draw("e0SAME")
              frame_res.SetTitle("")

       hist = graphData.getHist()
       xmin_ = graphData.GetXaxis().GetXmin()
       xmax_ = graphData.GetXaxis().GetXmax()
       
       length = 1
       if(length<2):
              c.Update()
              c.Range(xmin_, -3.5, xmax_, 3.5)
              line = ROOT.TLine(xmin_, 0., xmax_, 0.)
              line.SetLineColor(ROOT.kRed)
              line.SetLineWidth(2)
              line.Draw("same")
                            
              c.SaveAs(carddir+"Residuals/Residuals_"+ch+"_"+name+"_log.pdf")              
              '''             
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
              
              txt = ROOT.TText(3000, 4., "chiSquared: " + str(roochi2))
              txt.SetTextSize(0.04) 
              txt.SetTextColor(ROOT.kRed) 
              txt.Draw()
              
              c2.cd()
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

              '''
       # calculate RSS
       res, rss, chi1, chi2 = 0, 0., 0., 0., 

       xmin, xmax = array('d', [0.]), array('d', [0.])
       dataset.getRange(variable, xmin, xmax)
#       print "N bins: ", hist.GetN()
       #nBins = graphData.GetNbinsX()
       ratioHist = ROOT.TH1F("RatioPlot", "Ratio Plot", hist.GetN(), xmin_, xmax_)
       ROOT.SetOwnership(ratioHist, False)

 #      ratioHist.SetBins(nBins, graphData.GetXaxis().GetXbins().GetArray())

       #hist.Dump()
       #ratioHist.Dump()
       #ratioHist.Print('all')

       sumErrors = 0
       graphFit.Print()
       #print(graphFit.GetKeys())
       fitmodel = graphFit.getHist()
       fitmodel_curve = graphFit.getCurve(name+"_rgp_Norm[mH]_errorband")
       if label == "alt":
              fitmodel_curve = graphFit.getCurve("Bkg_Alt_"+str(ch)+str(order)+"_rgp_Norm[mH]_errorband")
       print "fitmodel_curve: {}".format(str(ch)+str(order)+name)
       fitmodel_curve.Print()

       c_x = np.ndarray(fitmodel_curve.GetN(), 'd', fitmodel_curve.GetX())
       c_y_all = np.ndarray(fitmodel_curve.GetN(), 'd', fitmodel_curve.GetY())
       c_y_up = c_y_all[0:len(c_y_all)/2]
       c_y_down = list(reversed(c_y_all[len(c_y_all)/2+1:]))
       
       def findClosestLowerBin(x, bins):
              for ib in range(len(bins)):
                     if bins[ib] > x:
                            return ib-1

       
       for i in xrange(0, hist.GetN()):
              
              print "bin x and y: ",  hist.GetX()[i], hist.GetY()[i]
              print hist.GetN(), fitmodel_curve.GetN()
              err_up = c_y_up[findClosestLowerBin(hist.GetX()[i], c_x)]
              err_down = c_y_down[findClosestLowerBin(hist.GetX()[i], c_x)]
              
              print "x, y, eyup, eydo: ", hist.GetX()[i], hist.GetY()[i], err_up, err_down
              if(hist.GetY()[i]>0):
                     diffErrors = abs(err_up - err_down)/hist.GetY()[i]
              else:
                     diffErrors = 0
              sumErrors += diffErrors
              
              hx, hy = hist.GetX()[i], hist.GetY()[i]
              hey = hist.GetErrorY(i)
              hexlo, hexhi = hist.GetErrorXlow(i), hist.GetErrorXhigh(i)
              ry = residuals.GetY()[i]
              pull = pulls.GetY()[i]
              resi = residuals.GetY()[i]

              if (hx - hexlo) > xmax[0] and hx + hexhi > xmax[0]:
                     continue

              if hy <= 0.:
                     continue
              
              res += ry
              rss += ry**2 

              chi1 += abs(pull)
              chi2 += abs((resi**2)/pull)


              ratioHist.SetBinContent(i+1, (ry - hy)/(-1*hy))
              ratioHist.SetBinError(i+1, (hey/ hy**2))
              ratioHist.Print('all')

       print "=======> sumErrors: ", sumErrors
        
       rss = math.sqrt(rss)
       parValList = []
       print(len(fitRes[0].floatParsFinal()))
       for iPar in range(len(fitRes[0].floatParsFinal())):
              print(iPar)
              parValList.append((fitRes[0].floatParsFinal().at(iPar)).getValV())
       out = {"chiSquared":roochi2,"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : hist.GetN(), "npar" : npar, "parVals": parValList}
       return out


def fisherTest(RSS1, RSS2, o1, o2, N):
       print "Testing functions with parameters o1 ", o1, " and o2 ", o2, " with RSS RSS1 ", RSS1, " and RSS2 ", RSS2, " and N ", N
       n1 = o1
       n2 = o2
       F = ((RSS1-RSS2)/(n2-n1)) / (RSS2/(N-n2))
       CL =  1.-ROOT.TMath.FDistI(F, n2-n1, N-n2)
       print "***************** Value of F, CL: ", F, CL
       return CL, F


#*******************************************************#
#                                                       #
#                      Datacard                         #
#                                                       #
#*******************************************************#

def getCard(sig, ch, ifilename, outdir, doModelling, mode = "histo", bias = False, verbose = False):


       ### Cmpute signal efficiencies 
       
       effname = "Efficiencies.txt"
       efile = open(effname, 'r')
       effline = efile.readline()

       effs = json.loads(effline)
       
       eff = effs[sig]

       try:
              ifile = ROOT.TFile.Open(ifilename)
       except IOError:
              print "Cannot open ", ifilename
       else:
              print "Opening file ",  ifilename
              ifile.cd()


       print "BIAS?", bias
       #workdir_ = ifilename.split("/")[:-1]
       #WORKDIR = "/".join(workdir_) + "/"
       carddir = outdir+  sig + "/"
       if not os.path.isdir(outdir): os.system('mkdir ' +outdir)
       if not os.path.isdir(carddir): os.system('mkdir ' +carddir)
       if not os.path.isdir(carddir + "plots/"): os.system('mkdir ' +carddir + "plots/")
       if not os.path.isdir(carddir + "Fisher/"): os.system('mkdir ' +carddir + "Fisher/")
       if not os.path.isdir(carddir + "Residuals/"): os.system('mkdir ' + carddir + "Residuals/") 

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
              histData = getHist(ch, "data_obs", ifile)
              print "channel ", ch             
              print "channel ", sig

              histSig = getHist(ch, sig, ifile)
              print "histSigData: ", histSig.Integral()
              #print "histBkgData: ", histBkgData.Integral()
              xvarmin = 1500.
              xvarmax = 8000.
              mT = RooRealVar(  "mH",    "m_{T}", xvarmin, xvarmax, "GeV")
              binMin = histData.FindBin(xvarmin)
              binMax = histData.FindBin(xvarmax)
              bkgData = RooDataHist("bkgdata", "MC Bkg",  RooArgList(mT), histBkgData, 1.)
              obsData = RooDataHist("data_obs", "Data",  RooArgList(mT), histData, 1.)
              sigData = RooDataHist("sigdata", "MC Sig",  RooArgList(mT), histSig, 1.)
              print "SUM ENTRIES: ", sigData.sumEntries()
              print "Bkg Integral: ", histData.Integral() 
              #nBkgEvts = histBkgData.Integral(1, histBkgData.GetXaxis().GetNbins()-1) 
              nBkgEvts = histBkgData.Integral(binMin, binMax)
              nDataEvts = histData.Integral(binMin, binMax)
              nSigEvts = histSig.Integral(binMin, binMax)
#              nBkgEvts = histData.Integral(1, histData.GetXaxis().GetNbins()-1)
#              nDataEvts = histData.Integral(1, histData.GetXaxis().GetNbins()-1) 
              #print "Bkg Events: ", nBkgEvts

              print "channel: ", ch
              normBkg = RooRealVar("Bkg_"+ch+"_norm", "Number of mc background events", nBkgEvts, 0., 2.e4)
              normData = RooRealVar("Data_"+ch+"_norm", "Number of data background events", nDataEvts, 0., 2.e4)
              ch_red = ch[:-5]
              modelName = "Bkg_"+ch
              modelAltName =  "Bkg_Alt_"+ch
              
              if(doModelling):
                     #ch_red = ch
                     print "channel: ", ch_red
                     lowerLimit = -50
                     upperLimit = 150
                     if "lowCut" in ch_red:
                            lowerLimit = -60  
                            upperLimit = 150  
                     if "highCut" in ch_red:
                            lowerLimit = -50 
                            upperLimit = 150  
                     if "lowSVJ2" in ch_red:
                            lowerLimit = -80  
                            upperLimit = 190  
                     if "highSVJ2" in ch_red:
                            lowerLimit = -60  
                            upperLimit = 190  
                     p1_11 = RooRealVar(ch_red + "_p1_11", "p1", 1., lowerLimit, upperLimit)
                     p2_11 = RooRealVar(ch_red + "_p2_11", "p2", 1., lowerLimit, upperLimit)

                     p1_21 = RooRealVar(ch_red + "_p1_21", "p1", 1., lowerLimit, upperLimit)
                     p2_21 = RooRealVar(ch_red + "_p2_21", "p2", 1., lowerLimit, upperLimit)
                     p3_21 = RooRealVar(ch_red + "_p3_21", "p3", 1., lowerLimit, upperLimit)

                     p1_12 = RooRealVar(ch_red + "_p1_12", "p1", 1., lowerLimit, upperLimit)
                     p2_12 = RooRealVar(ch_red + "_p2_12", "p2", 1., lowerLimit, upperLimit)
                     p3_12 = RooRealVar(ch_red + "_p3_12", "p3", 1., lowerLimit, upperLimit)

                     p1_31 = RooRealVar(ch_red + "_p1_31", "p1", 1., lowerLimit, upperLimit)
                     p2_31 = RooRealVar(ch_red + "_p2_31", "p2", 1., lowerLimit, upperLimit)
                     p3_31 = RooRealVar(ch_red + "_p3_31", "p3", 1., lowerLimit, upperLimit)
                     p4_31 = RooRealVar(ch_red + "_p4_31", "p4", 1., lowerLimit, upperLimit)

                     p1_22 = RooRealVar(ch_red + "_p1_22", "p1", 1., lowerLimit, upperLimit)
                     p2_22 = RooRealVar(ch_red + "_p2_22", "p2", 1., lowerLimit, upperLimit)
                     p3_22 = RooRealVar(ch_red + "_p3_22", "p3", 1., lowerLimit, upperLimit)
                     p4_22 = RooRealVar(ch_red + "_p4_22", "p4", 1., lowerLimit, upperLimit)

                     p1_13 = RooRealVar(ch_red + "_p1_13", "p1", 1., lowerLimit, upperLimit)
                     p2_13 = RooRealVar(ch_red + "_p2_13", "p2", 1., lowerLimit, upperLimit)
                     p3_13 = RooRealVar(ch_red + "_p3_13", "p3", 1., lowerLimit, upperLimit)
                     p4_13 = RooRealVar(ch_red + "_p4_13", "p4", 1., lowerLimit, upperLimit)

                     p1_41 = RooRealVar(ch_red + "_p1_41", "p1", 1., lowerLimit, upperLimit)
                     p2_41 = RooRealVar(ch_red + "_p2_41", "p2", 1., lowerLimit, upperLimit)
                     p3_41 = RooRealVar(ch_red + "_p3_41", "p3", 1., lowerLimit, upperLimit)
                     p4_41 = RooRealVar(ch_red + "_p4_41", "p4", 1., lowerLimit, upperLimit)
                     p5_41 = RooRealVar(ch_red + "_p5_41", "p5", 1., lowerLimit, upperLimit)

                     p1_32 = RooRealVar(ch_red + "_p1_32", "p1", 1., lowerLimit, upperLimit)
                     p2_32 = RooRealVar(ch_red + "_p2_32", "p2", 1., lowerLimit, upperLimit)
                     p3_32 = RooRealVar(ch_red + "_p3_32", "p3", 1., lowerLimit, upperLimit)
                     p4_32 = RooRealVar(ch_red + "_p4_32", "p4", 1., lowerLimit, upperLimit)
                     p5_32 = RooRealVar(ch_red + "_p5_32", "p5", 1., lowerLimit, upperLimit)

                     p1_23 = RooRealVar(ch_red + "_p1_23", "p1", 1., lowerLimit, upperLimit)
                     p2_23 = RooRealVar(ch_red + "_p2_23", "p2", 1., lowerLimit, upperLimit)
                     p3_23 = RooRealVar(ch_red + "_p3_23", "p3", 1., lowerLimit, upperLimit)
                     p4_23 = RooRealVar(ch_red + "_p4_23", "p4", 1., lowerLimit, upperLimit)
                     p5_23 = RooRealVar(ch_red + "_p5_23", "p5", 1., lowerLimit, upperLimit)

                     p1_14 = RooRealVar(ch_red + "_p1_14", "p1", 1., lowerLimit, upperLimit)
                     p2_14 = RooRealVar(ch_red + "_p2_14", "p2", 1., lowerLimit, upperLimit)
                     p3_14 = RooRealVar(ch_red + "_p3_14", "p3", 1., lowerLimit, upperLimit)
                     p4_14 = RooRealVar(ch_red + "_p4_14", "p4", 1., lowerLimit, upperLimit)
                     p5_14 = RooRealVar(ch_red + "_p5_14", "p5", 1., lowerLimit, upperLimit)

                     p1_15 = RooRealVar(ch_red + "_p1_15", "p1", 1., lowerLimit, upperLimit)
                     p2_15 = RooRealVar(ch_red + "_p2_15", "p2", 1., lowerLimit, upperLimit)
                     p3_15 = RooRealVar(ch_red + "_p3_15", "p3", 1., lowerLimit, upperLimit)
                     p4_15 = RooRealVar(ch_red + "_p4_15", "p4", 1., lowerLimit, upperLimit)
                     p5_15 = RooRealVar(ch_red + "_p5_15", "p5", 1., lowerLimit, upperLimit)
                     p6_15 = RooRealVar(ch_red + "_p6_15", "p6", 1., lowerLimit, upperLimit)

                     p1_24 = RooRealVar(ch_red + "_p1_24", "p1", 1., lowerLimit, upperLimit)
                     p2_24 = RooRealVar(ch_red + "_p2_24", "p2", 1., lowerLimit, upperLimit)
                     p3_24 = RooRealVar(ch_red + "_p3_24", "p3", 1., lowerLimit, upperLimit)
                     p4_24 = RooRealVar(ch_red + "_p4_24", "p4", 1., lowerLimit, upperLimit)
                     p5_24 = RooRealVar(ch_red + "_p5_24", "p5", 1., lowerLimit, upperLimit)
                     p6_24 = RooRealVar(ch_red + "_p6_24", "p6", 1., lowerLimit, upperLimit)

                     p1_33 = RooRealVar(ch_red + "_p1_33", "p1", 1., lowerLimit, upperLimit)
                     p2_33 = RooRealVar(ch_red + "_p2_33", "p2", 1., lowerLimit, upperLimit)
                     p3_33 = RooRealVar(ch_red + "_p3_33", "p3", 1., lowerLimit, upperLimit)
                     p4_33 = RooRealVar(ch_red + "_p4_33", "p4", 1., lowerLimit, upperLimit)
                     p5_33 = RooRealVar(ch_red + "_p5_33", "p5", 1., lowerLimit, upperLimit)
                     p6_33 = RooRealVar(ch_red + "_p6_33", "p6", 1., lowerLimit, upperLimit)

                     p1_42 = RooRealVar(ch_red + "_p1_42", "p1", 1., lowerLimit, upperLimit)
                     p2_42 = RooRealVar(ch_red + "_p2_42", "p2", 1., lowerLimit, upperLimit)
                     p3_42 = RooRealVar(ch_red + "_p3_42", "p3", 1., lowerLimit, upperLimit)
                     p4_42 = RooRealVar(ch_red + "_p4_42", "p4", 1., lowerLimit, upperLimit)
                     p5_42 = RooRealVar(ch_red + "_p5_42", "p5", 1., lowerLimit, upperLimit)
                     p6_42 = RooRealVar(ch_red + "_p6_42", "p6", 1., lowerLimit, upperLimit)

                     p1_51 = RooRealVar(ch_red + "_p1_51", "p1", 1., lowerLimit, upperLimit)
                     p2_51 = RooRealVar(ch_red + "_p2_51", "p2", 1., lowerLimit, upperLimit)
                     p3_51 = RooRealVar(ch_red + "_p3_51", "p3", 1., lowerLimit, upperLimit)
                     p4_51 = RooRealVar(ch_red + "_p4_51", "p4", 1., lowerLimit, upperLimit)
                     p5_51 = RooRealVar(ch_red + "_p5_51", "p5", 1., lowerLimit, upperLimit)
                     p6_51 = RooRealVar(ch_red + "_p6_51", "p6", 1., lowerLimit, upperLimit)

                     modelBkg11_rgp = RooGenericPdf(modelName+"_11_rgp", "Thry. (11)", "pow(1 - @0/13000, @1) * pow(@0/13000, -@2)", RooArgList(mT, p1_11, p2_11))
                     modelBkg21_rgp = RooGenericPdf(modelName+"_21_rgp", "Thry. (21)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) ) * pow(@0/13000, -@3)", RooArgList(mT, p1_21, p2_21, p3_21))
                     modelBkg31_rgp = RooGenericPdf(modelName+"_31_rgp", "Thry. (31)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) + @3*pow(log(@0/13000),2) ) * pow(@0/13000, -@4)", RooArgList(mT, p1_31, p2_31, p3_31, p4_31))
                     modelBkg41_rgp = RooGenericPdf(modelName+"_41_rgp", "Thry. (41)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) + @3*pow(log(@0/13000),2) + @4*pow(log(@0/13000),3) ) * pow(@0/13000, -@5)", RooArgList(mT, p1_41, p2_41, p3_41, p4_41, p5_41))
                     modelBkg12_rgp = RooGenericPdf(modelName+"_12_rgp", "Thry. (12)", "pow(1 - @0/13000, @1) * pow(@0/13000, -@2 - @3*log(@0/13000) )", RooArgList(mT, p1_12, p2_12, p3_12))
                     modelBkg13_rgp = RooGenericPdf(modelName+"_13_rgp", "Thry. (13)", "pow(1 - @0/13000, @1) * pow(@0/13000, -@2 - @3*log(@0/13000) - @4*pow(log(@0/13000),2) )", RooArgList(mT, p1_13, p2_13, p3_13, p4_13))
                     modelBkg14_rgp = RooGenericPdf(modelName+"_14_rgp", "Thry. (14)", "pow(1 - @0/13000, @1) * pow(@0/13000, -@2 - @3*log(@0/13000) - @4*pow(log(@0/13000),2) - @5*pow(log(@0/13000),3) )", RooArgList(mT, p1_14, p2_14, p3_14, p4_14, p5_14))
                     modelBkg22_rgp = RooGenericPdf(modelName+"_22_rgp", "Thry. (22)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) ) * pow(@0/13000, -@3 - @4*log(@0/13000) )", RooArgList(mT, p1_22, p2_22, p3_22, p4_22))
                     modelBkg32_rgp = RooGenericPdf(modelName+"_32_rgp", "Thry. (32)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) + @3*pow(log(@0/13000),2) ) * pow(@0/13000, -@4 - @5*log(@0/13000) )", RooArgList(mT, p1_32, p2_32, p3_32, p4_32, p5_32))
                     modelBkg23_rgp = RooGenericPdf(modelName+"_23_rgp", "Thry. (23)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) ) * pow(@0/13000, -@3 - @4*log(@0/13000) - @5*pow(log(@0/13000),2) )", RooArgList(mT, p1_23, p2_23, p3_23, p4_23, p5_23))

                     modelBkg15_rgp = RooGenericPdf(modelName+"_15_rgp", "Thry. (15)", "pow(1 - @0/13000, @1) * pow(@0/13000, -@2 - @3*log(@0/13000) - @4*pow(log(@0/13000),2) - @5*pow(log(@0/13000),3) - @6*pow(log(@0/13000),4) )", RooArgList(mT, p1_15, p2_15, p3_15, p4_15, p5_15, p6_15))
                     modelBkg24_rgp = RooGenericPdf(modelName+"_24_rgp", "Thry. (24)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) ) * pow(@0/13000, -@3 - @4*log(@0/13000) - @5*pow(log(@0/13000),2) - @6*pow(log(@0/13000),3) )", RooArgList(mT, p1_24, p2_24, p3_24, p4_24, p5_24, p6_24))
                     modelBkg33_rgp = RooGenericPdf(modelName+"_33_rgp", "Thry. (33)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) + @3*pow(log(@0/13000),2) ) * pow(@0/13000, -@4 - @5*log(@0/13000) - @6*pow(log(@0/13000),2) )", RooArgList(mT, p1_33, p2_33, p3_33, p4_33, p5_33, p6_33))
                     modelBkg42_rgp = RooGenericPdf(modelName+"_42_rgp", "Thry. (42)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) + @3*pow(log(@0/13000),2) + @4*pow(log(@0/13000),3) ) * pow(@0/13000, -@5 - @6*log(@0/13000))", RooArgList(mT, p1_42, p2_42, p3_42, p4_42, p5_42, p6_42))
                     modelBkg51_rgp = RooGenericPdf(modelName+"_51_rgp", "Thry. (51)", "pow(1 - @0/13000, @1 + @2*log(@0/13000) + @3*pow(log(@0/13000),2) + @4*pow(log(@0/13000),3) + @5*pow(log(@0/13000),4) ) * pow(@0/13000, -@6)", RooArgList(mT, p1_51, p2_51, p3_51, p4_51, p5_51, p6_51))



                     modelBkg11 = RooParametricShapeBinPdf(modelName+"_11", "Thry. (11)", modelBkg11_rgp, mT, RooArgList(p1_11, p2_11), histBkgData)
                     modelBkg21 = RooParametricShapeBinPdf(modelName+"_21", "Thry. (21)", modelBkg21_rgp, mT, RooArgList(p1_21, p2_21, p3_21), histBkgData)
                     modelBkg31 = RooParametricShapeBinPdf(modelName+"_31", "Thry. (31)", modelBkg31_rgp, mT, RooArgList(p1_31, p2_31, p3_31, p4_31), histBkgData)
                     modelBkg41 = RooParametricShapeBinPdf(modelName+"_41", "Thry. (41)", modelBkg41_rgp, mT, RooArgList(p1_41, p2_41, p3_41, p4_41, p5_41), histBkgData)
                     modelBkg12 = RooParametricShapeBinPdf(modelName+"_12", "Thry. (12)", modelBkg12_rgp, mT, RooArgList(p1_12, p2_12, p3_12), histBkgData)
                     modelBkg13 = RooParametricShapeBinPdf(modelName+"_13", "Thry. (13)", modelBkg13_rgp, mT, RooArgList(p1_13, p2_13, p3_13, p4_13), histBkgData)
                     modelBkg14 = RooParametricShapeBinPdf(modelName+"_14", "Thry. (14)", modelBkg14_rgp, mT, RooArgList(p1_14, p2_14, p3_14, p4_14, p5_14), histBkgData)
                     modelBkg22 = RooParametricShapeBinPdf(modelName+"_22", "Thry. (22)", modelBkg22_rgp, mT, RooArgList(p1_22, p2_22, p3_22, p4_22), histBkgData)
                     modelBkg32 = RooParametricShapeBinPdf(modelName+"_32", "Thry. (32)", modelBkg32_rgp, mT, RooArgList(p1_32, p2_32, p3_32, p4_32, p5_32), histBkgData)
                     modelBkg23 = RooParametricShapeBinPdf(modelName+"_23", "Thry. (23)", modelBkg23_rgp, mT, RooArgList(p1_23, p2_23, p3_23, p4_23, p5_23), histBkgData)

                     modelBkg15 = RooParametricShapeBinPdf(modelName+"_15", "Thry. (15)", modelBkg15_rgp, mT, RooArgList(p1_15, p2_15, p3_15, p4_15, p5_15, p6_15), histBkgData)
                     modelBkg24 = RooParametricShapeBinPdf(modelName+"_24", "Thry. (24)", modelBkg24_rgp, mT, RooArgList(p1_24, p2_24, p3_24, p4_24, p5_24, p6_24), histBkgData)
                     modelBkg33 = RooParametricShapeBinPdf(modelName+"_33", "Thry. (33)", modelBkg33_rgp, mT, RooArgList(p1_33, p2_33, p3_33, p4_33, p5_33, p6_33), histBkgData)
                     modelBkg42 = RooParametricShapeBinPdf(modelName+"_42", "Thry. (42)", modelBkg42_rgp, mT, RooArgList(p1_42, p2_42, p3_42, p4_42, p5_42, p6_42), histBkgData)
                     modelBkg51 = RooParametricShapeBinPdf(modelName+"_51", "Thry. (51)", modelBkg51_rgp, mT, RooArgList(p1_51, p2_51, p3_51, p4_51, p5_51, p6_51), histBkgData)

                     RSS = {}
                     fitrange = "Full"
                     #if (ch == "highSVJ1_2016"): fitrange = "Low,High"

                     fitRes11 = modelBkg11.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes21 = modelBkg21.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes31 = modelBkg31.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes41 = modelBkg41.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes12 = modelBkg12.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes13 = modelBkg13.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes14 = modelBkg14.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes22 = modelBkg22.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes32 = modelBkg32.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes23 = modelBkg23.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))

                     fitRes15 = modelBkg15.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes24 = modelBkg24.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes33 = modelBkg33.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes42 = modelBkg42.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes51 = modelBkg51.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     #orderBkg = [len(fitRes1.floatParsFinal()),len(fitRes2.floatParsFinal()),len(fitRes3.floatParsFinal()),len(fitRes4.floatParsFinal())]
                     
                     xframe = mT.frame(ROOT.RooFit.Title("extended ML fit example"))

                     c1 = ROOT.TCanvas()
                     c1.cd()
                     obsData.plotOn(xframe, RooFit.Name("obsData"))

                     #modelBkg11.plotOn(xframe, RooFit.Name("modelBkg11"), ROOT.RooFit.LineColor(ROOT.kBlack), RooFit.Range("Full"))
                     #modelBkg21.plotOn(xframe, RooFit.Name("modelBkg21"), ROOT.RooFit.LineColor(ROOT.kRed), RooFit.Range("Full"))
                     #modelBkg31.plotOn(xframe, RooFit.Name("modelBkg31"), ROOT.RooFit.LineColor(ROOT.kRed+1), RooFit.Range("Full"))
                     modelBkg41.plotOn(xframe, RooFit.Name("modelBkg41"), ROOT.RooFit.LineColor(ROOT.kRed+2), RooFit.Range("Full"))
                     #modelBkg12.plotOn(xframe, RooFit.Name("modelBkg12"), ROOT.RooFit.LineColor(ROOT.kBlue), RooFit.Range("Full"))
                     #modelBkg13.plotOn(xframe, RooFit.Name("modelBkg13"), ROOT.RooFit.LineColor(ROOT.kBlue+1), RooFit.Range("Full"))
                     #modelBkg14.plotOn(xframe, RooFit.Name("modelBkg14"), ROOT.RooFit.LineColor(ROOT.kBlue+2), RooFit.Range("Full"))
                     #modelBkg22.plotOn(xframe, RooFit.Name("modelBkg22"), ROOT.RooFit.LineColor(ROOT.kMagenta), RooFit.Range("Full"))
                     #modelBkg23.plotOn(xframe, RooFit.Name("modelBkg23"), ROOT.RooFit.LineColor(ROOT.kMagenta+1), RooFit.Range("Full"))
                     modelBkg32.plotOn(xframe, RooFit.Name("modelBkg32"), ROOT.RooFit.LineColor(ROOT.kMagenta+2), RooFit.Range("Full"))
                     modelBkg15.plotOn(xframe, RooFit.Name("modelBkg15"), ROOT.RooFit.LineColor(ROOT.kYellow), RooFit.Range("Full"))
                     modelBkg24.plotOn(xframe, RooFit.Name("modelBkg24"), ROOT.RooFit.LineColor(ROOT.kYellow+1), RooFit.Range("Full"))
                     #modelBkg33.plotOn(xframe, RooFit.Name("modelBkg33"), ROOT.RooFit.LineColor(ROOT.kYellow+2), RooFit.Range("Full"))
                     #modelBkg42.plotOn(xframe, RooFit.Name("modelBkg42"), ROOT.RooFit.LineColor(ROOT.kYellow+3), RooFit.Range("Full"))
                     #modelBkg15.plotOn(xframe, RooFit.Name("modelBkg51"), ROOT.RooFit.LineColor(ROOT.kYellow+4), RooFit.Range("Full"))

                     #chi2s_bkg11 = xframe.chiSquare("modelBkg11", "obsData",2)
                     #chi2s_bkg21 = xframe.chiSquare("modelBkg21", "obsData",3)
                     #chi2s_bkg31 = xframe.chiSquare("modelBkg31", "obsData",4)
                     #chi2s_bkg41 = xframe.chiSquare("modelBkg41", "obsData",5)
                     #chi2s_bkg12 = xframe.chiSquare("modelBkg12", "obsData",3)
                     #chi2s_bkg13 = xframe.chiSquare("modelBkg13", "obsData",4)
                     #chi2s_bkg14 = xframe.chiSquare("modelBkg14", "obsData",5)
                     #chi2s_bkg22 = xframe.chiSquare("modelBkg22", "obsData",4)
                     #chi2s_bkg32 = xframe.chiSquare("modelBkg32", "obsData",5)
                     #chi2s_bkg23 = xframe.chiSquare("modelBkg23", "obsData",5)
                     #chi2s_bkg15 = xframe.chiSquare("modelBkg15", "obsData",6)
                     #chi2s_bkg24 = xframe.chiSquare("modelBkg24", "obsData",6)
                     #chi2s_bkg33 = xframe.chiSquare("modelBkg33", "obsData",6)
                     #chi2s_bkg42 = xframe.chiSquare("modelBkg42", "obsData",6)
                     #chi2s_bkg51 = xframe.chiSquare("modelBkg51", "obsData",6)

                     xframe.SetMinimum(0.0002)
                     xframe.Draw()
                     c1.SetLogy()
                     c1.SaveAs(carddir+"plots/TestAfterFit_"+ch+".pdf")

                     RSS[11] = getRSS(sig, ch, mT, modelBkg11, obsData,  [fitRes11], carddir, nDataEvts)
                     RSS[21] = getRSS(sig, ch, mT, modelBkg21, obsData,  [fitRes21], carddir, nDataEvts)
                     RSS[31] = getRSS(sig, ch, mT, modelBkg31, obsData,  [fitRes31], carddir, nDataEvts)
                     RSS[41] = getRSS(sig, ch, mT, modelBkg41, obsData,  [fitRes41], carddir, nDataEvts)
                     RSS[12] = getRSS(sig, ch, mT, modelBkg12, obsData,  [fitRes12], carddir, nDataEvts)
                     RSS[13] = getRSS(sig, ch, mT, modelBkg13, obsData,  [fitRes13], carddir, nDataEvts)
                     RSS[14] = getRSS(sig, ch, mT, modelBkg14, obsData,  [fitRes14], carddir, nDataEvts)
                     RSS[22] = getRSS(sig, ch, mT, modelBkg22, obsData,  [fitRes22], carddir, nDataEvts)
                     RSS[32] = getRSS(sig, ch, mT, modelBkg32, obsData,  [fitRes32], carddir, nDataEvts)
                     RSS[23] = getRSS(sig, ch, mT, modelBkg23, obsData,  [fitRes23], carddir, nDataEvts)
                     RSS[15] = getRSS(sig, ch, mT, modelBkg15, obsData,  [fitRes15], carddir, nDataEvts)
                     RSS[24] = getRSS(sig, ch, mT, modelBkg24, obsData,  [fitRes24], carddir, nDataEvts)
                     RSS[33] = getRSS(sig, ch, mT, modelBkg33, obsData,  [fitRes33], carddir, nDataEvts)
                     RSS[42] = getRSS(sig, ch, mT, modelBkg42, obsData,  [fitRes42], carddir, nDataEvts)
                     RSS[51] = getRSS(sig, ch, mT, modelBkg51, obsData,  [fitRes51], carddir, nDataEvts)
                     



                     #*******************************************************#
                     #                                                       #
                     #                         Fisher                        #
                     #                                                       #
                     #*******************************************************#


                     ofile = open(carddir+"Fisher/FisherTest_%s.txt"%(ch),"w")
                     report = "fTest = ((RSS1-RSS2)/(npar2-npar1))/(RSS2/(nBins-npar2))\n"
                     report += "%s\n" % (ch)
                     #{"chiSquared":roochi2,"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : hist.GetN(), "npar" : npar}
                     report += "func\tchi2\trss\tnBins\tnPar\n"
                     for i in [11,21,31,41,12,13,14,22,32,23,15,24,33,42,51]:
                            report += "%i\t%.2f\t%.2f\t%i\t%i\n" % (i, RSS[i]['chiSquared'],RSS[i]['rss'],RSS[i]['nbins'],RSS[i]['npar'])
                     report += "func p1 p2 p3 p4 p5\n"
                     for i in [11,21,31,41,12,13,14,22,32,23,15,24,33,42,51]:
                            report += ("{} ".format(i) + ", ".join(['%.2f']*len(RSS[i]["parVals"])) + "\n") % tuple(RSS[i]["parVals"])

                     RTDict = {}
                     FDict = {}
                     pairs = [[11,21],[11,12],[11,31],[11,22],[11,13],[11,41],[11,32],[11,23],[11,14],[11,15],[11,24],[11,33],[11,42],[11,51],[21,31],[21,22],[21,41],[21,32],[21,23],[21,24],[21,33],[21,42],[21,51],[12,22],[12,13],[12,32],[12,23],[12,14],[12,15],[12,24],[12,33],[12,42],[31,41],[31,32],[31,33],[31,42],[31,51],[22,32],[22,23],[22,24],[22,33],[22,42],[13,23],[13,14],[13,15],[13,24],[13,33],[14,15],[14,24],[23,24],[23,33],[32,33],[32,42],[41,42],[41,51]]
                     report += "f1 f2 CL Ft\n"
                     for o1,o2 in pairs: # if RTDict (right tail) is larger than aCrit (0.05), use fewer paramters
                            #              RT large means Ftest statistic is 'normal' (i.e., fewer parameters is correct)
                            RTDict[str(o1)+"v"+str(o2)], FDict[str(o1)+"v"+str(o2)] = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], RSS[o1]['npar'], RSS[o2]['npar'], RSS[o2]["nbins"])
                            report += "%d %d %.5f %.5f\n" % (o1, o2, RTDict[str(o1)+"v"+str(o2)], FDict[str(o1)+"v"+str(o2)])
                     report += "f1 f2 f3 f4 result\n"
                     aCrit = 0.05
                     for funcs in [[11,12,13,14,15],[11,12,22,23,24],[11,12,13,23,24],[11,12,22,32,33],[11,12,13,14,24],[11,12,22,23,33],[11,12,13,23,33],[11,12,22,32,42],[11,21,22,23,24],[11,21,31,32,33],[11,21,22,32,33],[11,21,31,41,42],[11,21,22,23,33],[11,21,31,32,42],[11,21,22,32,42],[11,21,31,41,51],]:
                            order = -1
                            i = 0
                            j = 1
                            while order == -1:
                                   if RTDict["{}v{}".format(funcs[i],funcs[j])] > aCrit:
                                          j += 1
                                   else:
                                          i = j 
                                          j = i+1
                                   if j == len(funcs):
                                        order = funcs[i]

#                            if RTDict["{}v{}".format(a,b)] > aCrit:
#                                   if RTDict["{}v{}".format(a,c)] > aCrit:
#                                          if RTDict["{}v{}".format(a,d)] > aCrit:
#                                                 order = a
#                                          else:
#                                                 order = d
#                                   else:
#                                          if RTDict["{}v{}".format(c,d)] > aCrit:
#                                                 order = c
#                                          else:
#                                                 order = d
#                           else:
#                                  if RTDict["{}v{}".format(b,c)] > aCrit:
#                                          if RTDict["{}v{}".format(b,d)] > aCrit:
#                                                 order = b
#                                          else:
#                                                 order = d
#                                   else:
#                                          if RTDict["{}v{}".format(c,d)] > aCrit:
#                                                 order = c
#                                          else:
#                                                order = d
                            report +="{} {} {} {} {} {}\n".format(funcs[0],funcs[1],funcs[2],funcs[3],funcs[4],order)

# ALT FUNC
                     lowAlt = -60 # -40, -46, -44, -53
                     highAlt = 10 #   5,   5,   4,   5
                     #if "highCut" in ch_red:
                     #       lowerLimit_p1_3 = -20 
                     #       upperLimit_p1_3 = 100
                     #       lowerLimit_p2_3 = -40 
                     #       upperLimit_p2_3 = 10
                     #       lowerLimit_p3_3 = -20  
                     #       upperLimit_p3_3 = 10
                     #else:
                     #       lowerLimit_p1_3 = lowAlt
                     #       upperLimit_p1_3 = highAlt
                     #       lowerLimit_p2_3 = lowAlt 
                     #       upperLimit_p2_3 = highAlt
                     #       lowerLimit_p3_3 = lowAlt 
                     #       upperLimit_p3_3 = highAlt

                     p1_1 = RooRealVar(ch_red + "_p1_1", "p1", 1., lowAlt, highAlt)

                     p1_2 = RooRealVar(ch_red + "_p1_2", "p1", 1., lowAlt, highAlt)
                     p2_2 = RooRealVar(ch_red + "_p2_2", "p2", 1., lowAlt, highAlt)

                     p1_3 = RooRealVar(ch_red + "_p1_3", "p1", 1., lowAlt, highAlt)
                     p2_3 = RooRealVar(ch_red + "_p2_3", "p2", 1., lowAlt, highAlt)
                     p3_3 = RooRealVar(ch_red + "_p3_3", "p3", 1., lowAlt, highAlt)
                     #p1_3 = RooRealVar(ch_red + "_p1_3", "p1", 1., lowerLimit_p1_3, upperLimit_p1_3)
                     #p2_3 = RooRealVar(ch_red + "_p2_3", "p2", 1., lowerLimit_p2_3, upperLimit_p2_3)
                     #p3_3 = RooRealVar(ch_red + "_p3_3", "p3", 1., lowerLimit_p3_3, upperLimit_p3_3)

                     p1_4 = RooRealVar(ch_red + "_p1_4", "p1", 1., lowAlt, highAlt)
                     p2_4 = RooRealVar(ch_red + "_p2_4", "p2", 1., lowAlt, highAlt)
                     p3_4 = RooRealVar(ch_red + "_p3_4", "p3", 1., lowAlt, highAlt)
                     p4_4 = RooRealVar(ch_red + "_p4_4", "p4", 1., lowAlt, highAlt)


                     #modelAlt1_rgp = RooGenericPdf(modelName+"_alt_1_rgp", "Alt. (1)", "exp(@0/13000 * @1)", RooArgList(mT, p1_1))
                     #modelAlt2_rgp = RooGenericPdf(modelName+"_alt_2_rgp", "Alt. (2)", "exp(@0/13000 * @1 + @2 * log(@0/13000))", RooArgList(mT, p1_2, p2_2))
                     #modelAlt3_rgp = RooGenericPdf(modelName+"_alt_3_rgp", "Alt. (3)", "exp(@0/13000 * @1 + @2 * log(@0/13000) + @3 * pow(log(@0/13000),2))", RooArgList(mT, p1_3, p2_3, p3_3))
                     #modelAlt4_rgp = RooGenericPdf(modelName+"_alt_4_rgp", "Alt. (4)", "exp(@0/13000 * @1 + @2 * log(@0/13000) + @3 * pow(log(@0/13000),2) + @4 * pow(log(@0/13000),3))", RooArgList(mT, p1_4, p2_4, p3_4, p4_4))
                     # New Alt Function, reparameterized, decoupled
                     modelAlt1_rgp = RooGenericPdf(modelAltName+"1_rgp", "Alt. Reparam (1 par.)", "exp(@1*(@0/13000))", RooArgList(mT, p1_1))
                     modelAlt2_rgp = RooGenericPdf(modelAltName+"2_rgp", "Alt. Reparam (2 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2)", RooArgList(mT, p1_2, p2_2))
                     modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Alt. Reparam (3 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)))", RooArgList(mT, p1_3, p2_3, p3_3))
                     modelAlt4_rgp = RooGenericPdf(modelAltName+"4_rgp", "Alt. Reparam (4 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)*(1+@4*log(@0/13000))))", RooArgList(mT, p1_4, p2_4, p3_4, p4_4))

                     modelAlt1 = RooParametricShapeBinPdf(modelName+"_alt_1", "Alt. (1)", modelAlt1_rgp, mT, RooArgList(p1_1), histBkgData)
                     modelAlt2 = RooParametricShapeBinPdf(modelName+"_alt_2", "Alt. (2)", modelAlt2_rgp, mT, RooArgList(p1_2, p2_2), histBkgData)
                     modelAlt3 = RooParametricShapeBinPdf(modelName+"_alt_3", "Alt. (3)", modelAlt3_rgp, mT, RooArgList(p1_3, p2_3, p3_3), histBkgData)
                     modelAlt4 = RooParametricShapeBinPdf(modelName+"_alt_4", "Alt. (4)", modelAlt4_rgp, mT, RooArgList(p1_4, p2_4, p3_4, p4_4), histBkgData)
                     fitrange = "Full"
                     #if (ch == "highSVJ1_2016"): fitrange = "Low,High"

                     fitRes1 = modelAlt1.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes2 = modelAlt2.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes3 = modelAlt3.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes4 = modelAlt4.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     #orderBkg = [len(fitRes1.floatParsFinal()),len(fitRes2.floatParsFinal()),len(fitRes3.floatParsFinal()),len(fitRes4.floatParsFinal())]
                     
                     xframe = mT.frame(ROOT.RooFit.Title("extended ML fit example"))

                     c1 = ROOT.TCanvas()
                     c1.cd()
                     obsData.plotOn(xframe, RooFit.Name("obsData"))

                     modelAlt1.plotOn(xframe, RooFit.Name("modelAlt1"), ROOT.RooFit.LineColor(ROOT.kBlack), RooFit.Range("Full"))
                     modelAlt2.plotOn(xframe, RooFit.Name("modelAlt2"), ROOT.RooFit.LineColor(ROOT.kRed), RooFit.Range("Full"))
                     modelAlt3.plotOn(xframe, RooFit.Name("modelAlt3"), ROOT.RooFit.LineColor(ROOT.kGreen), RooFit.Range("Full"))
                     modelAlt4.plotOn(xframe, RooFit.Name("modelAlt4"), ROOT.RooFit.LineColor(ROOT.kBlue), RooFit.Range("Full"))
                     
                     chi2s_bkg1 = xframe.chiSquare("modelAlt1", "obsData",1)
                     chi2s_bkg2 = xframe.chiSquare("modelAlt2", "obsData",2)
                     chi2s_bkg3 = xframe.chiSquare("modelAlt3", "obsData",3)
                     chi2s_bkg4 = xframe.chiSquare("modelAlt4", "obsData",4)
                     
                     xframe.SetMinimum(0.0002)
                     xframe.Draw()
                     c1.SetLogy()
                     c1.BuildLegend()
                     c1.SaveAs(carddir+"plots/TestAfterFit_"+ch+"_alt.pdf")

                     RSS[1] = getRSS(sig, ch, mT, modelAlt1, obsData,  [fitRes1], carddir, nDataEvts,label = "alt")
                     RSS[2] = getRSS(sig, ch, mT, modelAlt2, obsData,  [fitRes2], carddir, nDataEvts,label = "alt")
                     RSS[3] = getRSS(sig, ch, mT, modelAlt3, obsData,  [fitRes3], carddir, nDataEvts,label = "alt")
                     RSS[4] = getRSS(sig, ch, mT, modelAlt4, obsData,  [fitRes4], carddir, nDataEvts,label = "alt")
                      



                     #*******************************************************#
                     #                                                       #
                     #                         Fisher                        #
                     #                                                       #
                     #*******************************************************#


                     ofile = open(carddir+"Fisher/FisherTest_%s.txt"%(ch),"w")
                     #report = "fTest = ((RSS1-RSS2)/(npar2-npar1))/(RSS2/(nBins-npar2))\n"
                     report += "ALT FUNC TEST -------------------------"
                     report += "%s\n" % (ch)
                     #{"chiSquared":roochi2,"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : hist.GetN(), "npar" : npar}
                     report += "func\tchi2\trss\tnBins\tnPar\n"
                     for i in [1,2,3,4]:
                            report += "%i\t%.2f\t%.2f\t%i\t%i\n" % (i, RSS[i]['chiSquared'],RSS[i]['rss'],RSS[i]['nbins'],RSS[i]['npar'])
                     report += "func p1 p2 p3 p4 p5\n"
                     for i in [1,2,3,4]:
                            report += ("{} ".format(i) + ", ".join(['%.2f']*len(RSS[i]["parVals"])) + "\n") % tuple(RSS[i]["parVals"])

                     RTDict = {}
                     FDict = {}
                     pairs = [[1,2],[1,3],[1,4],[2,3],[2,4],[3,4]]
                     report += "f1 f2 CL Ft\n"
                     for o1,o2 in pairs: # if RTDict (right tail) is larger than aCrit (0.05), use fewer paramters
                            #              RT large means Ftest statistic is 'normal' (i.e., fewer parameters is correct)
                            RTDict[str(o1)+"v"+str(o2)], FDict[str(o1)+"v"+str(o2)] = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], RSS[o1]['npar'], RSS[o2]['npar'], RSS[o2]["nbins"])
                            report += "%d %d %.5f %.5f\n" % (o1, o2, RTDict[str(o1)+"v"+str(o2)], FDict[str(o1)+"v"+str(o2)])
                     report += "f1 f2 f3 f4 result\n"
                     aCrit = 0.05
                     for funcs in [[1,2,3,4]]:
                            order = -1
                            i = 0
                            j = 1
                            while order == -1:
                                   if RTDict["{}v{}".format(funcs[i],funcs[j])] > aCrit:
                                          j += 1
                                   else:
                                          i = j 
                                          j = i+1
                                   if j == len(funcs):
                                        order = funcs[i]

#                            if RTDict["{}v{}".format(a,b)] > aCrit:
#                                   if RTDict["{}v{}".format(a,c)] > aCrit:
#                                          if RTDict["{}v{}".format(a,d)] > aCrit:
#                                                 order = a
#                                          else:
#                                                 order = d
#                                   else:
#                                          if RTDict["{}v{}".format(c,d)] > aCrit:
#                                                 order = c
#                                          else:
#                                                 order = d
#                           else:
#                                  if RTDict["{}v{}".format(b,c)] > aCrit:
#                                          if RTDict["{}v{}".format(b,d)] > aCrit:
#                                                 order = b
#                                          else:
#                                                 order = d
#                                   else:
#                                          if RTDict["{}v{}".format(c,d)] > aCrit:
#                                                 order = c
#                                          else:
#                                                order = d
                            report +="{} {} {} {} {}\n".format(funcs[0],funcs[1],funcs[2],funcs[3],order)
                     ofile.write(report)
                     ofile.close()

