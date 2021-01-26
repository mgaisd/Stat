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

mopt = ROOT.Math.MinimizerOptions()
mopt.SetMaxFunctionCalls(100000)
mopt.SetMaxIterations(100000)


syst = collections.OrderedDict()
# uncertainties apply to signal only
# data doesn't get any (cause its data)
# and MC bkg is indirectly used (via the fits)
# and the uncertainties on the fit parameters take care of that
syst["lumi"] = ("lnN", "sig", 1.026)
syst["trig"] = ("lnN", "sig", 1.020)
syst["scale"] = ("lnN", "sig", 1.15)

syst["mcstat"] = ("shape", ["sig"])

syst["MC2016JEC"] = ("shape",["sig"])
syst["MC2016JER"] = ("shape",["sig"])
syst["MC2016puunc"] = ("shape",["sig"])
syst["MC2016trigfnunc"] = ("shape",["sig"])

syst["MC2017JEC"] = ("shape",["sig"])
syst["MC2017JER"] = ("shape",["sig"])
syst["MC2017puunc"] = ("shape",["sig"])
syst["MC2017trigfnunc"] = ("shape",["sig"])

syst["MC2018JEC"] = ("shape",["sig"])
syst["MC2018JER"] = ("shape",["sig"])
syst["MC2018puunc"] = ("shape",["sig"])
syst["MC2018trigfnunc"] = ("shape",["sig"])

syst["MCRun2JES"] = ("shape",["sig"])
syst["MCRun2pdfallunc"] = ("shape",["sig"])
syst["MCRun2psfsrunc"] = ("shape",["sig"])
syst["MCRun2psisrunc"] = ("shape",["sig"])

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

def altMerge(l1, l2):
	result = [None]*(len(l1)+len(l2))
	result[::2] = l1
	result[1::2] = l2
	return result


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
       order = int(name[-1])
       npar = fitRes[0].floatParsFinal().getSize() if len(fitRes)>0 else 0
       varArg = ROOT.RooArgSet(variable)
      
       #frame = variable.frame()
       frame = variable.frame(ROOT.RooFit.Title(""))
       dataset.plotOn(frame, RooFit.Invisible())
       print(fitRes[0])
       #if len(fitRes) > 0: model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Range("Full"))
       if len(fitRes) > 0: graphFit = model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Range("Full"))

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
              txt.Draw()

              #txt_2 = ROOT.TText(2500, 800, "Prob: " + str(roopro))
              #txt_2 = ROOT.TText(2500, 2., "Prob: " + str(roopro))
              roopro_small = format(roopro, '.2f')
              txt_2 = ROOT.TText(0.65, 0.65, "prob: " + str(roopro_small))              
              txt_2.SetNDC()
              txt_2.SetTextSize(0.04) 
              txt_2.SetTextColor(ROOT.kRed) 
              txt_2.Draw()
              
              c.cd()
              c.Update()
              c.cd()
              pad2 = ROOT.TPad("pad2", "pad2", 0, 0.1, 1, 0.34)
              ROOT.SetOwnership(pad2, False)
              pad2.SetTopMargin(0)
              pad2.SetBottomMargin(0.25)
              pad2.SetGridx()
              pad2.SetGridy()
              pad2.Draw()
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
                            
              c.SaveAs("Residuals_"+ch+"_"+name+"_log.pdf")              
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
       fitmodel = graphFit.getHist()
       fitmodel_curve = graphFit.getCurve("Bkg_"+str(ch)+str(order)+"_rgp_Norm[mH"+ch+"]_errorband")
       if label == "alt":
              fitmodel_curve = graphFit.getCurve("Bkg_Alt_"+str(ch)+str(order)+"_rgp_Norm[mH"+ch+"]_errorband")
       print "fitmodel_curve: "
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
       parErrList = []
       print(len(fitRes[0].floatParsFinal()))
       for iPar in range(len(fitRes[0].floatParsFinal())):
              print(iPar)
              parValList.append((fitRes[0].floatParsFinal().at(iPar)).getValV())
              parErrList.append((fitRes[0].floatParsFinal().at(iPar)).getError())
       out = {"chiSquared":roochi2,"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : hist.GetN(), "npar" : npar, "parVals": parValList, "parErr":parErrList}
       length=1
       if(length<2):

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
              frame.SetTitle("")

              #txt = ROOT.TText(2500, 6., "chiSquared: " + str(roochi2))
              #txt = ROOT.TText(2500, 1000, "chiSquared: " + str(roochi2))
              txt = ROOT.TText(0.65, 0.7, "chiSquared: " + str(roochi2_small))              
              txt.SetNDC()
              txt.SetTextSize(0.04) 
              txt.SetTextColor(ROOT.kRed) 
              txt.Draw()


              #txt_2 = ROOT.TText(2500, 800, "Prob: " + str(roopro))
              txt_2 = ROOT.TText(0.65, 0.65, "prob: " + str(roopro_small))              
              txt_2.SetNDC()
              #txt_2 = ROOT.TText(2500, 2., "Prob: " + str(roopro))
              txt_2.SetTextSize(0.04) 
              txt_2.SetTextColor(ROOT.kRed) 
              txt_2.Draw();


#              txt2 = ROOT.TText(3000, 1., "Error: "+  str(sumErrors))
#              txt2.SetTextSize(0.04) 
#              txt2.SetTextColor(ROOT.kOrange) 
              #txt2.Draw("same");
              
              c2.cd()
              c2.Update()
              c2.cd()
              pad2_2 = ROOT.TPad("pad2_2", "pad2_2", 0, 0.05, 1, 0.34)
              ROOT.SetOwnership(pad2_2, False)
              pad2_2.SetTopMargin(0);
              pad2_2.SetBottomMargin(0.25);
              pad2_2.SetGridx();
              pad2_2.SetGridy();
              pad2_2.Draw();
              pad2_2.cd()
              pad2_2.Clear()
       #frame.Draw()
              c2.Update()
              c2.Modified()
              frame.SetTitle("")

              ratioHist.GetYaxis().SetRangeUser(0.,2.)
              ratioHist.SetTitle("")
              ratioHist.GetYaxis().SetTitle("f(i)/N^{data}")
              ratioHist.GetXaxis().SetTitle("m_{T} (GeV)")
              ratioHist.GetYaxis().SetTitleSize(.13)
              ratioHist.GetYaxis().SetTitleOffset(.3)
              ratioHist.GetXaxis().SetTitleOffset(1.)
              ratioHist.GetXaxis().SetTitleSize(.13)
              ratioHist.GetXaxis().SetLabelSize(.12)
              ratioHist.GetYaxis().SetLabelSize(.12)

       #ratioHist.SetMarkerSize(2)
              ratioHist.SetMarkerStyle(20)
              ratioHist.Draw("PE")
              line2 = ROOT.TLine(xmin_, 1., xmax_, 1.)
              line2.SetLineColor(ROOT.kRed)
              line2.SetLineWidth(2)
              line2.Draw("same")
              frame.SetTitle("")

              c2.SaveAs("Residuals_"+ch+"_"+name + "_ratio_log.pdf")

       return out

def drawTwoFuncs(sig, ch, variable, modelA, modelB, dataset, fitRes, carddir,  norm = -1, label = "nom"):
       name = modelA.GetName()+"_"+modelB.GetName()
       varArg = ROOT.RooArgSet(variable)
      
       frame = variable.frame(ROOT.RooFit.Title(""))
       dataset.plotOn(frame, RooFit.Invisible())
       modelA.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineStyle(2), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kCyan), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Name(modelA.GetName()),  RooFit.Range("Full"))
       modelB.plotOn(frame, RooFit.VisualizeError(fitRes[1], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineStyle(2), RooFit.LineColor(ROOT.kRed),  RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Name(modelB.GetName()),  RooFit.Range("Full"))
       dataset.plotOn(frame, RooFit.DataError(ROOT.RooAbsData.Poisson if isData else ROOT.RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(dataset.GetName()))
       modelA.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.DrawOption("L"), RooFit.Name(modelA.GetName()),  RooFit.Range("Full"))
       modelB.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kRed), RooFit.DrawOption("L"), RooFit.Name(modelB.GetName()),  RooFit.Range("Full"))
       frame.SetMaximum(frame.GetMaximum()*10.)
       frame.SetMinimum(0.1)

       c = ROOT.TCanvas("c_"+ch+name, ch, 800, 800)
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
              
       txt = ROOT.TText(0.5, 0.7, modelA.GetName())              
       txt.SetNDC()
       txt.SetTextSize(0.04) 
       txt.SetTextColor(ROOT.kBlue) 
       txt.Draw()
       txt_2 = ROOT.TText(0.5, 0.8, modelB.GetName())              
       txt_2.SetNDC()
       txt_2.SetTextSize(0.04) 
       txt_2.SetTextColor(ROOT.kRed) 
       txt_2.Draw()

       c.cd()
       c.Update()
       c.cd()
       pad2 = ROOT.TPad("pad2", "pad2", 0, 0.1, 1, 0.3)
       ROOT.SetOwnership(pad2, False)
       pad2.SetTopMargin(0)
       pad2.SetBottomMargin(0.25)
       pad2.SetGridx()
       pad2.SetGridy()
       pad2.Draw()
       pad2.cd()
       pad2.Clear()

       frame_res = variable.frame(ROOT.RooFit.Title(""))
       frame_res.GetYaxis().SetRangeUser(-3.5, 3.5)
       frame_res.SetTitle("")
       frame_res.GetYaxis().SetTitle("Ratio Main/Alt")
       frame_res.GetYaxis().SetTitleOffset(.3)
       frame_res.GetXaxis().SetTitleOffset(1.)
       frame_res.GetYaxis().SetTitleSize(.13)
       frame_res.GetXaxis().SetTitle("m_{T} (GeV)")
       frame_res.GetXaxis().SetTitleSize(.13)
       frame_res.GetXaxis().SetLabelSize(.12)
       frame_res.GetYaxis().SetLabelSize(.12)
       frame_res.Draw("SAME")
       frame_res.SetTitle("")
       
       c.Update()
       c.Range(1500, -3.5, 8000, 3.5)
       # create two histograms, one for modelA (main) and one for modelB (alt)
       # then diving A by B, and plot in Red
       histA = ROOT.TH1F("histA","histA",65,1500,8000)
       histB = ROOT.TH1F("histB","histB",65,1500,8000)
       histA.Sumw2()
       histB.Sumw2()
       modelA.fillHistogram(histA, RooArgList(varArg))
       modelB.fillHistogram(histB, RooArgList(varArg))
       histA.Divide(histB)
       histA.SetLineColor(ROOT.kMagenta)
       histA.SetLineWidth(2)
       histA.Draw("hist c same")
       frame_res.GetYaxis().SetRangeUser(0.0, 2.0)
       
       c.Update()
       c.Modified()
       c.SaveAs("Residuals_"+ch+"_"+name+"_TwoFuncs_14.pdf")

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

def getCard(sig, ch, ifilename, outdir, doModelling, mode = "histo", bias = False, verbose = False, doSys = True):


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
       #carddir = outdir+  sig + "/"
       #carddir = sig + "/"
       carddir = ""
       #if not os.path.isdir(outdir): os.system('mkdir ' +outdir)
       #if not os.path.isdir(outdir + "/" + sig): os.system('mkdir ' +carddir)
       #if not os.path.isdir(outdir + carddir + "plots/"): os.system('mkdir ' +carddir + "plots/")
       #if not os.path.isdir(outdir + carddir + "Fisher/"): os.system('mkdir ' +carddir + "Fisher/")
       #if not os.path.isdir(outdir + carddir + "Residuals/"): os.system('mkdir ' + carddir + "Residuals/") 

       hist_filename = os.getcwd()+"/"+ifilename
       hist = getHist(ch, sig, ifile)

       


       #*******************************************************#
       #                                                       #
       #                   Generate workspace                  #
       #                                                       #
       #*******************************************************#
    
       if(mode == "template"):

              ch_red = ch[:-5]
              modelName = "Bkg_"+ch
              modelAltName =  "Bkg_Alt_"+ch
              histData = getHist(ch, "data_obs", ifile)
              histSig = getHist(ch, sig, ifile)
              xvarmin = 1500.
              xvarmax = 8000.
              binMin = histData.FindBin(xvarmin)
              binMax = histData.FindBin(xvarmax)
              nDataEvts = histData.Integral(binMin, binMax)
              nSigEvts = histSig.Integral(binMin, binMax)
              mT = RooRealVar(  "mH"+ch,    "m_{T}", xvarmin, xvarmax, "GeV")
              obsData = RooDataHist("data_obs", "Data",  RooArgList(mT), histData, 1.)
              sigData = RooDataHist("sigdata", "MC Sig",  RooArgList(mT), histSig, 1.)
              #*******************************************************#
              #                                                       #
              #                    Datacard Writing                   #
              #                                                       #
              #*******************************************************#
              wfile = ROOT.TFile.Open("root://cmseos.fnal.gov//store/user/cfallon/datacards_20Jan/ws_{}.root".format(ch_red))
              wBkg =  wfile.Get("BackgroundWS")
              print "workspace ", wBkg.Print()
              print "Model name: ", modelName
              modelBkg = wBkg.pdf(modelName)
              modelAlt = wBkg.pdf(modelAltName)
              normAlt = wBkg.pdf(modelAltName+"_norm")
              normData = wBkg.pdf(modelName+"_norm")
              parSet = modelBkg.getParameters(obsData)
              parSet.Print()
              argList = ROOT.RooArgList(parSet)
              parNames = [ argList[i].GetName() for i in xrange(0, len(parSet))]                                 


             # modelExt = RooExtendPdf(modelBkg.GetName(), modelBkg.GetTitle(), modelBkg, normzBkg)

              for i in xrange(0, len(parSet)):
                    print  argList[i].GetName(), "   ", argList[i].getVal()


              # BIAS STUDY
              # Generate pseudo data

              #setToys = RooDataSet()
              #setToys.SetName("data_toys")
              #setToys.SetTitle("Data (toys)")

              #if not isData:
              #       print " - Generating", nBkgEvts, "events for toy data"
              #       if bias: setToys = modelAlt.generateBinned(RooArgSet(mT), nBkgEvts, 0,0)
                     #fitRes = modelBkg.fitTo(setToys, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(1))

              if bias:
                     ROOT.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
                     from ROOT import RooMultiPdf
                     pdf_index_string = "pdf_index_%s" % (ch)
                     cat = RooCategory(pdf_index_string, "Index of Pdf which is active")
                     pdfs = RooArgList()
                     pdfs.add(modelBkg)
                     pdfs.add(modelAlt)
                     roomultipdf = RooMultiPdf("roomultipdf", "All Pdfs", cat, pdfs)
                     #normulti = RooRealVar("roomultipdf_norm", "Number of background events", nDataEvts, 0., 1.e6)
                     normulti = RooRealVar("roomultipdf_norm", "Number of background events", 1.0, 0., 1.e6)

              # create workspace
              w = RooWorkspace("SVJ", "workspace")
              # Dataset
              # ATT: include isData

              #getattr(w, "import")(obsData, RooFit.Rename("Bkg"))
              #if isData: getattr(w, "import")(obsData, RooFit.Rename("data_obs"))
              getattr(w, "import")(obsData, RooFit.Rename("data_obs"))
              #else: getattr(w, "import")(setToys, RooFit.Rename("data_obs"))
              #getattr(w, "import")(obsData, RooFit.Rename("data_obs"))
              getattr(w, "import")(sigData, RooFit.Rename(sig))
              
              if bias:
                     getattr(w, "import")(cat)#, RooFit.Rename(cat.GetName()))
                     getattr(w, "import")(normulti)#, RooFit.Rename(normulti.GetName()))
                     getattr(w, "import")(roomultipdf)#, RooFit.Rename(roomultipdf.GetName()))

              for i in xrange(hist.GetNbinsX()):
                     for year in ["2016","2017","2018"]:
                            mcstatSysName = "mcstat_%s_%s_MC%sbin%d"  % (ch, sig, year, i+1)
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
                     if not ((doSys == True) or (sysName == "lumi")):
                            continue # always include lumi, and only do others if doSys is True
                     if(sysValue[0]=="shape" and "mcstat" not in sysName):              
                            sysUp =  getHist(ch, sig + "_" + sysName + "Up", ifile)
                            sysDown =  getHist(ch, sig + "_" + sysName + "Down", ifile)
                            #print "==> Trigg sys name: ", sig + "_" + sysName + "Down"
                            sysSigHistUp = RooDataHist(sig + "_" + sysName + "Up", sysName + " uncertainty",  RooArgList(mT), sysUp, 1.)
                            sysSigHistDown = RooDataHist(sig + "_" + sysName + "Down", sysName + " uncertainty",  RooArgList(mT), sysDown, 1.)
                            getattr(w, "import")(sysSigHistUp, RooFit.Rename(sig + "_" + sysName + "Up") )
                            getattr(w, "import")(sysSigHistDown, RooFit.Rename(sig + "_" + sysName + "Down") )
                            


              #else: getattr(w, "import")(setToys, RooFit.Rename("data_obs"))
              getattr(w, "import")(modelBkg, (modelBkg.GetName()))
              if bias:
                     getattr(w, "import")(modelAlt, (modelAltName))
              #getattr(w, "import")(normzBkg, RooFit.Rename(normzBkg.GetName()))
              wstatus = w.writeToFile("ws_%s_%s_%s.root" % (sig, ch, mode), True)

              if wstatus == False : print "Workspace", "ws_%s_%s_%s.root" % (sig, ch, mode) , "saved successfully"
              else: print "Workspace", "ws_%s_%s_%s.root" % (sig, ch, mode) , "not saved successfully"
              workfile = "ws_%s_%s_%s.root" % ( sig, ch, mode)
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
              rates["Bkg"] = nDataEvts #nBkgEvts, Kevin asked to change to data yield, limits converge better
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


       rates["data_obs"] = getRate(ch, "data_obs", ifile)
       rates[sig] = getRate(ch, sig, ifile)
       if mode == "template":
              print "TEST sig: ", rates[sig], nSigEvts, binMax
              print "TEST bkg/obs: ", rates["data_obs"], nDataEvts, binMax




       card  = "imax 1 number of channels \n"
       card += "jmax * number of backgrounds \n"
       card += "kmax * number of nuisance parameters\n"
       card += "-----------------------------------------------------------------------------------\n"

       if(mode == "template"):
              #card += "shapes   %s  %s    %s    %s    %s\n" % (sig, ch, ifilename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_SYSTEMATIC")
              #card += "shapes   %-15s %-5s %s%s.root  %s\n" % (sig, ch, WORKDIR, ch, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s\n" % (modelBkg.GetName(), ch, workfile, "SVJ:$PROCESS")
              card += "shapes   %s  %s    %s    %s    %s\n" % (sig, ch, workfile, "SVJ:$PROCESS", "SVJ:$PROCESS_$SYSTEMATIC")
              card += "shapes   %s  %s    %s    %s\n" % ("data_obs", ch, workfile, "SVJ:$PROCESS")

       else:  
              card += "shapes   *      *   %s    %s    %s\n" % (hist_filename, "$CHANNEL/$PROCESS", "$CHANNEL/$PROCESS_$SYSTEMATIC")
              card += "shapes   data_obs      *   %s    %s\n" % (hist_filename, "$CHANNEL/$PROCESS")
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin               %s\n" % ch
       print "===> Observed data: ", rates["data_obs"]
       card += "observation       %.6f\n" % (rates["data_obs"]) 
       card += "-----------------------------------------------------------------------------------\n"
       card += "bin                                     %-43s\n" % (binString)
       card += "process                                 %-43s%-43s\n" % (sig, procLine) #"roomultipdf"
       card += "process                                 %-43s%-43s\n" % ("0", procNumbLine)
       card += "rate                                    %-43.6f%-43s\n" % (rates[sig], rateLine) #signalYield[m].getVal(), nevents
       card += "-----------------------------------------------------------------------------------\n"

       for sysName,sysValue  in syst.iteritems():
              print(sysName, sysValue, "testSystematicValues")
              if not ((doSys == True) or (sysName == "lumi")):
                  continue # always include lumi, and only do others if doSys is True
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
                            if("sig" in sysValue[1]):
                                   try:
                                          if(getRate(ch, sig, ifile) != 0.): sigSys = abs((getRate(ch, sig+hsysNameUp, ifile) - getRate(ch, sig+hsysNameDown, ifile))/ (2* getRate(ch, sig, ifile)))
                                   except AttributeError:
                                          sigSys = sysValue[2]
                                   if(sigSys < 1. and sigSys > 0.): sigSys = sigSys + 1
                                   card += "%-20s" % (sigSys)
                            else:  card += "%-20s" % ("-")
                            for p in processes:
                                   print(p, processes)
                                   if (p in sysValue[1]):
                                          if (getRate(ch, p, ifile) != 0.): bkgSys = abs((getRate(ch, p+hsysNameUp, ifile) - getRate(ch, p+hsysNameDown, ifile))/ (2* getRate(ch, p, ifile)) )
                                          else: bkgSys = 1
                                          if(bkgSys<1. and bkgSys >0.): bkgSys = bkgSys + 1
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
                                   # CAMBIARE NOME DELLA SYST      , change name of syst?               
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
                                          for year in ["2016","2017","2018"]:
                                                 sysName = "mcstat_%s_%s_MC%sbin%d      "  % (ch, sampName, year, i+1)
                                                 card += "%-20s   shape   " % (sysName)
                                                 card += line   
                                                 card += "\n"    
       
              card += "\n"
              
       if mode == "template":
              for par in parNames: card += "%-20s%-20s\n" % (par, "flatParam")

       #card += "SF            extArg     1 [0.75,1.25]\n"
       #card += "SF param 1 0.25\n"
       #for par, formula in rateParams.iteritems(): 
       #       formula = formula.replace("%s", '%.3f' % (eff))
       #       card += "%-20s %-20s %-20s %-20s %s %-20s\n" % (par + "_rate", "rateParam", ch, sig, formula, "SF")


      # card += "\n"

       outname =  "%s_%s_%s.txt" % (sig, ch, mode)
       cardfile = open(outname, 'w')
       cardfile.write(card)
       cardfile.close()

       if bias:
              card = card.replace(modelBkg.GetName(), "roomultipdf")
              card.replace("rate                                    %-20.6f%-20.6f\n" % (1, 1), "rate                                    %-20.6f%-20.6f\n" % (10, 1))
              card += "%-35s     discrete\n" % (pdf_index_string)
              outname = "%s_%s_%s_bias.txt" % (sig, ch, mode)
              cardfile = open(outname, 'w')
              cardfile.write(card)
              cardfile.close()
    

       #print card
       return card




