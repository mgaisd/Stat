import ROOT
import json

#changed to no longer need the settings.py file
# files now saved to base directory and exported to EOS after jobs completion

#ftest.py - part I of seperating ftests from datacard writing
# this part will create a ws.root file containing the two histograms and two funcs as well as funcs' parameters


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

#*******************************************************#
#                                                       #
#                     Utility Functions                 #
#                                                       #
#*******************************************************#

isData = True

def getRate(ch, process, ifile):
       hName = ch + "/"+ process
       print(hName)
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
      
       frame = variable.frame(ROOT.RooFit.Title(""))
       dataset.plotOn(frame, RooFit.Invisible())
       print(fitRes[0])
       if len(fitRes) > 0: graphFit = model.plotOn(frame, RooFit.VisualizeError(fitRes[0], 1, False), RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("FL"), RooFit.Range("Full"))

       model.plotOn(frame, RooFit.Normalization(norm if norm>0 else dataset.sumEntries(), ROOT.RooAbsReal.NumEvent), RooFit.LineColor(ROOT.kBlue), RooFit.FillColor(ROOT.kOrange), RooFit.FillStyle(1001), RooFit.DrawOption("L"), RooFit.Name(model.GetName()),  RooFit.Range("Full"))
       model.paramOn(frame, RooFit.Label(model.GetTitle()), RooFit.Layout(0.45, 0.95, 0.94), RooFit.Format("NEAU"))
       
       graphData = dataset.plotOn(frame, RooFit.DataError(ROOT.RooAbsData.Poisson if isData else ROOT.RooAbsData.SumW2), RooFit.DrawOption("PE0"), RooFit.Name(dataset.GetName()))

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
              
              roochi2_small = format(roochi2, '.2f')
              txt = ROOT.TText(0.65, 0.7, "chiSquared: " + str(roochi2_small))              
              txt.SetNDC()
              txt.SetTextSize(0.04) 
              txt.SetTextColor(ROOT.kRed) 
              txt.Draw()

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

       # calculate RSS
       res, rss, chi1, chi2 = 0, 0., 0., 0., 

       xmin, xmax = array('d', [0.]), array('d', [0.])
       dataset.getRange(variable, xmin, xmax)
       ratioHist = ROOT.TH1F("RatioPlot", "Ratio Plot", hist.GetN(), xmin_, xmax_)
       ROOT.SetOwnership(ratioHist, False)

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

              txt = ROOT.TText(0.65, 0.7, "chiSquared: " + str(roochi2_small))              
              txt.SetNDC()
              txt.SetTextSize(0.04) 
              txt.SetTextColor(ROOT.kRed) 
              txt.Draw()

              txt_2 = ROOT.TText(0.65, 0.65, "prob: " + str(roopro_small))              
              txt_2.SetNDC()
              txt_2.SetTextSize(0.04) 
              txt_2.SetTextColor(ROOT.kRed) 
              txt_2.Draw();

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
       # then divide A by B, and plot in Red
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

def getCard(sig, ch, ifilename, doModelling, mode = "histo", bias = False, verbose = False):
       try:
              ifile = ROOT.TFile.Open(ifilename)
       except IOError:
              print "Cannot open ", ifilename
       else:
              print "Opening file ",  ifilename
              ifile.cd()


       print "BIAS?", bias
       carddir = ""

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
              xvarmin = 1500.
              xvarmax = 8000.
              mT = RooRealVar(  "mH"+ch,    "m_{T}", xvarmin, xvarmax, "GeV")
              binMin = histData.FindBin(xvarmin)
              binMax = histData.FindBin(xvarmax)
              bkgData = RooDataHist("bkgdata", "MC Bkg",  RooArgList(mT), histBkgData, 1.)
              obsData = RooDataHist("data_obs", "Data",  RooArgList(mT), histData, 1.)
              sigData = RooDataHist("sigdata", "MC Sig",  RooArgList(mT), histSig, 1.)
              print "SUM ENTRIES: ", sigData.sumEntries()
              print "Bkg Integral: ", histData.Integral() 
              nBkgEvts = histBkgData.Integral(binMin, binMax)
              nDataEvts = histData.Integral(binMin, binMax)
              nSigEvts = histSig.Integral(binMin, binMax)

              print "channel: ", ch
              normBkg = RooRealVar("Bkg_"+ch+"_norm", "Number of background events", nBkgEvts, 0., 2.e4)
              normData = RooRealVar("Data_"+ch+"_norm", "Number of background events", nDataEvts, 0., 2.e4)
              ch_red = ch[:-5]
              modelName = "Bkg_"+ch
              modelAltName =  "Bkg_Alt_"+ch
              
              if(doModelling):
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
                            lowerLimit = -20
                            upperLimit = 100


                     p1_1 = RooRealVar(ch_red + "_p1_1", "p1", 1., lowerLimit, upperLimit)
                     p1_2 = RooRealVar(ch_red + "_p1_2", "p1", 1., lowerLimit, upperLimit)
                     p1_3 = RooRealVar(ch_red + "_p1_3", "p1", 1., lowerLimit, upperLimit)
                     p1_4 = RooRealVar(ch_red + "_p1_4", "p1", 1., lowerLimit, upperLimit)

                     p2_1 = RooRealVar(ch_red + "_p2_1", "p2", 1., lowerLimit, upperLimit)
                     p2_2 = RooRealVar(ch_red + "_p2_2", "p2", 1., lowerLimit, upperLimit)
                     p2_3 = RooRealVar(ch_red + "_p2_3", "p2", 1., lowerLimit, upperLimit)
                     p2_4 = RooRealVar(ch_red + "_p2_4", "p2", 1., lowerLimit, upperLimit)

                     p3_2 = RooRealVar(ch_red + "_p3_2", "p3", 1., lowerLimit, upperLimit)
                     p3_3 = RooRealVar(ch_red + "_p3_3", "p3", 1., lowerLimit, upperLimit)
                     p3_4 = RooRealVar(ch_red + "_p3_4", "p3", 1., lowerLimit, upperLimit)

                     p4_3 = RooRealVar(ch_red + "_p4_3", "p4", 1., lowerLimit, upperLimit)
                     p4_4 = RooRealVar(ch_red + "_p4_4", "p4", 1., lowerLimit, upperLimit)

                     p5_4 = RooRealVar(ch_red + "_p5_4", "p5", 1., lowerLimit, upperLimit)


                     #Function from Theorists, combo testing, sequence E, 1, 11, 12, 22
                     # model NM has N params on 1-x and M params on x. exponents are (p_i + p_{i+1} * log(x))
                     # these are the RooGenericPdf verisons, convert to RooParametricShapeBinPdf below
                     modelBkg1_rgp = RooGenericPdf(modelName+"1_rgp", "Thry. fit (11)", "pow(1 - @0/13000, @1) * pow(@0/13000, -(@2))",                                                                  RooArgList(mT, p1_1, p2_1))
                     modelBkg2_rgp = RooGenericPdf(modelName+"2_rgp", "Thry. fit (12)", "pow(1 - @0/13000, @1) * pow(@0/13000, -(@2+@3*log(@0/13000)))",                                                 RooArgList(mT, p1_2, p2_2, p3_2))
                     #modelBkg3_rgp = RooGenericPdf(modelName+"3_rgp", "Thry. fit (13)", "pow(1 - @0/13000, @1) * pow(@0/13000, -(@2+@3*log(@0/13000)+@4*pow(log(@0/13000),2)))",                         RooArgList(mT, p1_3, p2_3, p3_3, p4_3))
                     #modelBkg4_rgp = RooGenericPdf(modelName+"4_rgp", "Thry. fit (14)", "pow(1 - @0/13000, @1) * pow(@0/13000, -(@2+@3*log(@0/13000)+@4*pow(log(@0/13000),2)+@5*pow(log(@0/13000),3)))", RooArgList(mT, p1_4, p2_4, p3_4, p4_4, p5_4))
                     modelBkg3_rgp = RooGenericPdf(modelName+"3_rgp", "Thry. fit (22)", "pow(1 - @0/13000, @1+@2*log(@0/13000)) * pow(@0/13000, -(@3+@4*log(@0/13000)))",                         RooArgList(mT, p1_3, p2_3, p3_3, p4_3))
                     modelBkg4_rgp = RooGenericPdf(modelName+"4_rgp", "Thry. fit (32)", "pow(1 - @0/13000, @1+@2*log(@0/13000)+@3*pow(log(@0/13000),2)) * pow(@0/13000, -(@4+@5*log(@0/13000)))", RooArgList(mT, p1_4, p2_4, p3_4, p4_4, p5_4))
                     #modelBkg4_rgp = RooGenericPdf(modelName+"4_rgp", "Thry. fit (41)", "pow(1 - @0/13000, @1+@2*log(@0/13000)+@3*pow(log(@0/13000),2)+@4*pow(log(@0/13000),3)) * pow(@0/13000, -@5)", RooArgList(mT, p1_4, p2_4, p3_4, p4_4, p5_4))
                     modelBkg1 = RooParametricShapeBinPdf(modelName+"1", "Thry. Fit (11)", modelBkg1_rgp, mT, RooArgList(p1_1, p2_1), histBkgData)
                     modelBkg2 = RooParametricShapeBinPdf(modelName+"2", "Thry. Fit (12)", modelBkg2_rgp, mT, RooArgList(p1_2, p2_2, p3_2), histBkgData)
                     #modelBkg3 = RooParametricShapeBinPdf(modelName+"3", "Thry. Fit (13)", modelBkg3_rgp, mT, RooArgList(p1_3, p2_3, p3_3, p4_3), histBkgData)
                     #modelBkg4 = RooParametricShapeBinPdf(modelName+"4", "Thry. Fit (14)", modelBkg4_rgp, mT, RooArgList(p1_4, p2_4, p3_4, p4_4, p5_4), histBkgData)
                     modelBkg3 = RooParametricShapeBinPdf(modelName+"3", "Thry. Fit (22)", modelBkg3_rgp, mT, RooArgList(p1_3, p2_3, p3_3, p4_3), histBkgData)
                     modelBkg4 = RooParametricShapeBinPdf(modelName+"4", "Thry. Fit (32)", modelBkg4_rgp, mT, RooArgList(p1_4, p2_4, p3_4, p4_4, p5_4), histBkgData)
                     #modelBkg4 = RooParametricShapeBinPdf(modelName+"4", "Thry. Fit (41)", modelBkg4_rgp, mT, RooArgList(p1_4, p2_4, p3_4, p4_4, p5_4), histBkgData)

                     RSS = {}
                     fitrange = "Full"
                     #if (ch == "highSVJ1_2016"): fitrange = "Low,High"

                     fitRes1 = modelBkg1.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes2 = modelBkg2.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes3 = modelBkg3.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     fitRes4 = modelBkg4.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                     orderBkg = [len(fitRes1.floatParsFinal()),len(fitRes2.floatParsFinal()),len(fitRes3.floatParsFinal()),len(fitRes4.floatParsFinal())]
                     
                     xframe = mT.frame(ROOT.RooFit.Title("extended ML fit example"))

                     c1 = ROOT.TCanvas()
                     c1.cd()
                     obsData.plotOn(xframe, RooFit.Name("obsData"))

                     modelBkg1.plotOn(xframe, RooFit.Name("modelBkg1"), ROOT.RooFit.LineColor(ROOT.kPink + 6), RooFit.Range("Full"))
                     modelBkg2.plotOn(xframe, RooFit.Name("modelBkg2"), ROOT.RooFit.LineColor(ROOT.kBlue -4), RooFit.Range("Full"))
                     modelBkg3.plotOn(xframe, RooFit.Name("modelBkg3"), ROOT.RooFit.LineColor(ROOT.kRed -4), RooFit.Range("Full"))
                     modelBkg4.plotOn(xframe, RooFit.Name("modelBkg4"), ROOT.RooFit.LineColor(ROOT.kGreen +1), RooFit.Range("Full"))
                     #modelBkg1.paramOn(xframe, RooFit.Name("modelBkg1"), RooFit.Layout(0.0,0.5,0.5))
                     #modelBkg2.paramOn(xframe, RooFit.Name("modelBkg2"), RooFit.Layout(0.5,1.0,0.5))
                     #modelBkg3.paramOn(xframe, RooFit.Name("modelBkg3"), RooFit.Layout(0.0,0.5,0.25))
                     #modelBkg4.paramOn(xframe, RooFit.Name("modelBkg4"), RooFit.Layout(0.5,1.0,0.25))

                     chi2s_bkg1 = xframe.chiSquare("modelBkg1", "obsData",1)
                     chi2s_bkg2 = xframe.chiSquare("modelBkg2", "obsData",2)
                     chi2s_bkg3 = xframe.chiSquare("modelBkg3", "obsData",3)
                     chi2s_bkg4 = xframe.chiSquare("modelBkg4", "obsData",4)

                     xframe.SetMinimum(0.0002)
                     xframe.Draw()

                     txt1 = ROOT.TText(2000., 10., "model1, nP {}, chi2: {}".format(orderBkg[0],chi2s_bkg1))
                     txt1.SetTextSize(0.04) 
                     txt1.SetTextColor(ROOT.kPink+6) 
                     xframe.addObject(txt1) 
                     txt2 = ROOT.TText(2000., 1, "model2, nP {}, chi2: {}".format(orderBkg[1],chi2s_bkg2))
                     txt2.SetTextSize(0.04) 
                     txt2.SetTextColor(ROOT.kBlue-4) 
                     xframe.addObject(txt2) 
                     txt3 = ROOT.TText(2000., 0.1, "model3, nP {}, chi2: {}".format(orderBkg[2],chi2s_bkg3))
                     txt3.SetTextSize(0.04) 
                     txt3.SetTextColor(ROOT.kRed-4) 
                     xframe.addObject(txt3) 
                     txt4 = ROOT.TText(2000., 0.01, "model4, nP {}, chi2: {}".format(orderBkg[3],chi2s_bkg4))
                     txt4.SetTextSize(0.04) 
                     txt4.SetTextColor(ROOT.kGreen+1) 
                     xframe.addObject(txt4) 
                     txt1.Draw()
                     txt2.Draw()
                     txt3.Draw()
                     txt4.Draw()

                     c1.SetLogy()
                     c1.SaveAs("TestAfterFit_"+ch+".pdf")

                     RSS[fitRes1.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelBkg1, obsData,  [fitRes1], carddir, nDataEvts)
                     RSS[fitRes2.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelBkg2, obsData,  [fitRes2], carddir, nDataEvts)
                     RSS[fitRes3.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelBkg3, obsData,  [fitRes3], carddir, nDataEvts)
                     RSS[fitRes4.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelBkg4, obsData,  [fitRes4], carddir, nDataEvts)
                     print RSS[2]

                     #**********************************************************
                     #                    ALTERNATIVE MODEL                    *
                     #**********************************************************
                     if bias:

                            # alternative function is Silvio's nominal function, but with +1 instead of -1
                            normAlt = RooRealVar("Bkg_"+ch+"alt_norm", "Number of background events", nBkgEvts, 0., 2.e4)
                            normData = RooRealVar("Data_"+ch+"alt_norm", "Number of background events", nDataEvts, 0., 2.e4) 

                            lowAlt = -100
                            highAlt = 100
                            if "high" in ch_red:
                                   lowAlt = -1000
                                   highAlt = 1000
                            fitrange = "Full"
                            # Kevin's Brute Force Method, implimented by Colin
                            # do only for highCut 3param.
                            # Fit all combinations of p_i = -10, -1, -0.1, 0.1, 1, 10, save the best chi2
                            reportAltExtra = ""
                            alt3InitParam = []
                            if (("highCut" in ch_red) and (False)):
                            #test from 2021-Jan-1 showed that the combination -1.0, -0.1, -0.1 is best.
                                   listOfInits = [-10., -1., -0.1, 0.1, 1.0, 10]
                                   #alt1chi = 200
                                   #alt2chi = 200
                                   alt3chi = 200
                                   #alt4chi = 200
                                   #alt1InitParam = []
                                   #alt2InitParam = []
                                   #alt4InitParam = []
                                   #for p1i in listOfInits:
                                   #       #Set up new parameters
                                   #       temp_p1_1_alt = RooRealVar(ch_red + "_p1_1_alt", "p1", p1i, lowAlt, highAlt)
                                   #       #set up temp functions to test
                                   #       temp_modelAlt1_rgp = RooGenericPdf(modelAltName+"1_rgp", "Alt. Reparam (1 par.)", "exp(@1*(@0/13000))", RooArgList(mT, temp_p1_1_alt))
                                   #       temp_modelAlt1 = RooParametricShapeBinPdf(modelAltName+"1", "Alt. Fit 1par", temp_modelAlt1_rgp, mT, RooArgList(temp_p1_1_alt), histBkgData)
                                   #       temp_fitRes1_alt = temp_modelAlt1.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                                   #       if temp_modelAlt1.createChi2(obsData) < alt1chi: #if chi2 is better than before...
                                   #              #... keep best fit based on chi2
                                   #              alt1chi = temp_modelAlt1.createChi2(obsData)
                                   #             #alt1InitParam.clear()
                                   #             alt1InitParam = [p1i]
                                   #              modelAlt1_rpg = temp_modelAlt1_rgp
                                   #              modelAlt1 = temp_modelAlt1
                                   #              fitRes1_alt = temp_fitRes1_alt
                                   #              p1_1_alt = temp_p1_1_alt
       
                                   #for p1i in listOfInits:
                                   #       for p2i in listOfInits:
                                   #              #Set up new parameters
                                   #              temp_p1_2_alt = RooRealVar(ch_red + "_p1_2_alt", "p1", p1i, lowAlt, highAlt)
                                   #              temp_p2_2_alt = RooRealVar(ch_red + "_p2_2_alt", "p2", p2i, lowAlt, highAlt)
                                   #              #set up temp functions to test
                                   #              temp_modelAlt2_rgp = RooGenericPdf(modelAltName+"2_rgp", "Alt. Reparam (2 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2)", RooArgList(mT, temp_p1_2_alt, temp_p2_2_alt))
                                   #              temp_modelAlt2 = RooParametricShapeBinPdf(modelAltName+"2", "Alt. Fit 2par", temp_modelAlt2_rgp, mT, RooArgList(temp_p1_2_alt, temp_p2_2_alt), histBkgData)
                                   #              temp_fitRes2_alt = temp_modelAlt2.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                                   #              if temp_modelAlt2.createChi2(obsData) < alt2chi: #if chi2 is better than before...
                                   #                     #... keep best fit based on chi2
                                   #                     alt2chi = temp_modelAlt2.createChi2(obsData)
                                   #                     #alt2InitParam.clear()
                                   #                     alt2InitParam = [p1i, p2i]
                                   #                     modelAlt2_rpg = temp_modelAlt2_rgp
                                   #                     modelAlt2 = temp_modelAlt2
                                   #                     fitRes2_alt = temp_fitRes2_alt
                                   #                     p1_2_alt = temp_p1_2_alt
                                   #                     p2_2_alt = temp_p2_2_alt
       
                                   for p1i in listOfInits:
                                          for p2i in listOfInits:
                                                 for p3i in listOfInits:
                                                        #Set up new parameters
                                                        temp_p1_3_alt = RooRealVar(ch_red + "_p1_3_alt", "p1", p1i, lowAlt, highAlt)
                                                        temp_p2_3_alt = RooRealVar(ch_red + "_p2_3_alt", "p2", p2i, lowAlt, highAlt)
                                                        temp_p3_3_alt = RooRealVar(ch_red + "_p3_3_alt", "p3", p3i, lowAlt, highAlt)
                                                        #set up temp functions to test
                                                        temp_modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Alt. Reparam (3 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)))", RooArgList(mT, temp_p1_3_alt, temp_p2_3_alt, temp_p3_3_alt))
                                                        temp_modelAlt3 = RooParametricShapeBinPdf(modelAltName+"3", "Alt. Fit 3par", temp_modelAlt3_rgp, mT, RooArgList(temp_p1_3_alt, temp_p2_3_alt, temp_p3_3_alt), histBkgData)
                                                        temp_fitRes3_alt = temp_modelAlt3.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                                                        reportAltExtra += "{} {} {} {}\n".format(p1i, p2i, p3i, temp_modelAlt3.createChi2(obsData).getValV())
                                                        if temp_modelAlt3.createChi2(obsData).getValV() < alt3chi: #if chi2 is better than before...
                                                               #... keep best fit based on chi2
                                                               alt3chi = temp_modelAlt3.createChi2(obsData).getValV()
                                                               #alt3InitParam.clear()
                                                               alt3InitParam = [p1i,p2i,p3i]
                                                               modelAlt3_rpg = temp_modelAlt3_rgp
                                                               modelAlt3 = temp_modelAlt3
                                                               fitRes3_alt = temp_fitRes3_alt
                                                               p1_3_alt = temp_p1_3_alt
                                                               p2_3_alt = temp_p2_3_alt
                                                               p3_3_alt = temp_p3_3_alt
       
                                   #for p1i in listOfInits:
                                   #       for p2i in listOfInits:
                                   #              for p3i in listOfInits:
                                   #                     for p4i in listOfInits:
                                   #                            #Set up new parameters
                                   #                            temp_p1_4_alt = RooRealVar(ch_red + "_p1_4_alt", "p1", p1i, lowAlt, highAlt)
                                   #                            temp_p2_4_alt = RooRealVar(ch_red + "_p2_4_alt", "p2", p2i, lowAlt, highAlt)
                                   #                            temp_p3_4_alt = RooRealVar(ch_red + "_p3_4_alt", "p3", p3i, lowAlt, highAlt)
                                   #                            temp_p4_4_alt = RooRealVar(ch_red + "_p4_4_alt", "p4", p4i, lowAlt, highAlt)
                                   #                            #set up temp functions to test
                                   #                            temp_modelAlt4_rgp = RooGenericPdf(modelAltName+"4_rgp", "Alt. Reparam (4 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)*(1+@4*log(@0/13000))))", RooArgList(mT, temp_p1_4_alt, temp_p2_4_alt, temp_p3_4_alt, temp_p4_4_alt))
                                   #                            temp_modelAlt4 = RooParametricShapeBinPdf(modelAltName+"4", "Alt. Fit 4par", temp_modelAlt4_rgp, mT, RooArgList(temp_p1_4_alt, temp_p2_4_alt, temp_p3_4_alt, temp_p4_4_alt), histBkgData)
                                   #                            temp_fitRes4_alt = temp_modelAlt4.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                                   #                            if temp_modelAlt4.createChi2(obsData) < alt4chi: #if chi2 is better than before...
                                   #                                   #... keep best fit based on chi2
                                   #                                   alt4chi = temp_modelAlt4.createChi2(obsData)
                                   #                                   #alt4InitParam.clear()
                                   #                                   alt4InitParam = [p1i,p2i,p3i,p4i]
                                   #                                   modelAlt4_rpg = temp_modelAlt4_rgp       
                                   #                                   modelAlt4 = temp_modelAlt4
                                   #                                   fitRes4_alt = temp_fitRes4_alt
                                   #                                   p1_4_alt = temp_p1_4_alt
                                   #                                   p2_4_alt = temp_p2_4_alt
                                   #                                   p3_4_alt = temp_p3_4_alt
                                   #                                   p4_4_alt = temp_p4_4_alt
                                   #end kevin's brute force method
                            else:
                                   p1i = 1.
                                   p2i = 1.
                                   p3i = 1.
                                   if "highCut" in ch_red:
                                          p1i = -1.
                                          p2i = -0.1
                                          p3i = -0.1
                                   p1_3_alt = RooRealVar(ch_red + "_p1_3_alt", "p1", p1i, lowAlt, highAlt)
                                   p2_3_alt = RooRealVar(ch_red + "_p2_3_alt", "p2", p2i, lowAlt, highAlt)
                                   p3_3_alt = RooRealVar(ch_red + "_p3_3_alt", "p3", p3i, lowAlt, highAlt)
                                   modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Alt. Reparam (3 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)))", RooArgList(mT, p1_3_alt, p2_3_alt, p3_3_alt))
                                   modelAlt3 = RooParametricShapeBinPdf(modelAltName+"3", "Alt. Fit 3par", modelAlt3_rgp, mT, RooArgList(p1_3_alt, p2_3_alt, p3_3_alt), histBkgData)
                                   fitRes3_alt = modelAlt3.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                            

                            p1i = 1.
                            p2i = 1.
                            p3i = 1.
                            p4i = 1.
                            p1_1_alt = RooRealVar(ch_red + "_p1_1_alt", "p1", p1i, lowAlt, highAlt)

                            p1_2_alt = RooRealVar(ch_red + "_p1_2_alt", "p1", p1i, lowAlt, highAlt)
                            p2_2_alt = RooRealVar(ch_red + "_p2_2_alt", "p2", p2i, lowAlt, highAlt)

                            #p1_3_alt = RooRealVar(ch_red + "_p1_3_alt", "p1", p1i, lowAlt, highAlt)
                            #p2_3_alt = RooRealVar(ch_red + "_p2_3_alt", "p2", p2i, lowAlt, highAlt)
                            #p3_3_alt = RooRealVar(ch_red + "_p3_3_alt", "p3", p3i, lowAlt, highAlt)

                            p1_4_alt = RooRealVar(ch_red + "_p1_4_alt", "p1", p1i, lowAlt, highAlt)
                            p2_4_alt = RooRealVar(ch_red + "_p2_4_alt", "p2", p2i, lowAlt, highAlt)
                            p3_4_alt = RooRealVar(ch_red + "_p3_4_alt", "p3", p3i, lowAlt, highAlt)
                            p4_4_alt = RooRealVar(ch_red + "_p4_4_alt", "p4", p4i, lowAlt, highAlt)

                            #p2_1_alt = RooRealVar(ch_red + "_p2_1_alt", "p2", 1., -50., 50.)
                            #p3_2_alt = RooRealVar(ch_red + "_p3_2_alt", "p3", 1., -50., 50.)
                            #p4_3_alt = RooRealVar(ch_red + "_p4_3_alt", "p4", 1., -50., 50.)
                            #p5_4_alt = RooRealVar(ch_red + "_p5_4_alt", "p5", 1., -50., 50.)



                            # Dijet Function Alt
                            #modelAlt1_rgp = RooGenericPdf(modelAltName+"1_rgp", "Dij. fit (1 par.)", "pow(1 - @0/13000, abs(@1)) ", RooArgList(mT, p1_1_alt))
                            #modelAlt2_rgp = RooGenericPdf(modelAltName+"2_rgp", "Dij. fit (2 par.)", "pow(1 - @0/13000, abs(@1)) * pow(@0/13000, -abs(@2))", RooArgList(mT, p1_2_alt, p2_2_alt))
                            #modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Dij. fit (3 par.)", "pow(1 - @0/13000, abs(@1)) * pow(@0/13000, -abs(@2)-abs(@3)*log(@0/13000))", RooArgList(mT, p1_3_alt, p2_3_alt, p3_3_alt))
                            #modelAlt4_rgp = RooGenericPdf(modelAltName+"4_rgp", "Dij. fit (4 par.)", "pow(1 - @0/13000, abs(@1)) * pow(@0/13000, -abs(@2)-log(@0/13000)*(abs(@3) + abs(@4)* log(@0/13000)))", RooArgList(mT, p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt))

                            # New Alt Function
                            #modelAlt1_rgp = RooGenericPdf(modelAltName+"1_rgp", "Alt. fit (1 par.)", "exp(@1*(@0/13000))", RooArgList(mT, p1_1_alt))
                            #modelAlt2_rgp = RooGenericPdf(modelAltName+"2_rgp", "Alt. fit (2 par.)", "exp(@1*(@0/13000)+@2*log(@0/13000))", RooArgList(mT, p1_2_alt, p2_2_alt))
                            #modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Alt. fit (3 par.)", "exp(@1*(@0/13000)+@2*log(@0/13000)+@3*pow(log(@0/13000),2))", RooArgList(mT, p1_3_alt, p2_3_alt, p3_3_alt))
                            #modelAlt4_rgp = RooGenericPdf(modelAltName+"4_rgp", "Alt. fit (4 par.)", "exp(@1*(@0/13000)+@2*log(@0/13000)+@3*pow(log(@0/13000),2)+@4*pow(log(@0/13000),3))", RooArgList(mT, p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt))

                            # New Alt Function, reparameterized, decoupled
                            modelAlt1_rgp = RooGenericPdf(modelAltName+"1_rgp", "Alt. Reparam (1 par.)", "exp(@1*(@0/13000))", RooArgList(mT, p1_1_alt))
                            modelAlt2_rgp = RooGenericPdf(modelAltName+"2_rgp", "Alt. Reparam (2 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2)", RooArgList(mT, p1_2_alt, p2_2_alt))
                            #modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Alt. Reparam (3 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)))", RooArgList(mT, p1_3_alt, p2_3_alt, p3_3_alt))
                            modelAlt4_rgp = RooGenericPdf(modelAltName+"4_rgp", "Alt. Reparam (4 par.)", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)*(1+@4*log(@0/13000))))", RooArgList(mT, p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt))

                            modelAlt1 = RooParametricShapeBinPdf(modelAltName+"1", "Alt. Fit 1par", modelAlt1_rgp, mT, RooArgList(p1_1_alt), histBkgData)
                            modelAlt2 = RooParametricShapeBinPdf(modelAltName+"2", "Alt. Fit 2par", modelAlt2_rgp, mT, RooArgList(p1_2_alt, p2_2_alt), histBkgData)
                            #modelAlt3 = RooParametricShapeBinPdf(modelAltName+"3", "Alt. Fit 3par", modelAlt3_rgp, mT, RooArgList(p1_3_alt, p2_3_alt, p3_3_alt), histBkgData)
                            modelAlt4 = RooParametricShapeBinPdf(modelAltName+"4", "Alt. Fit 4par", modelAlt4_rgp, mT, RooArgList(p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt), histBkgData)

                            #modelAlt1_rgp = RooGenericPdf(modelAltName+"1_rgp", "Thry. (expandDenom2)", "pow(@0/13000, -@1) * pow(1 - @0/13000, @2)", RooArgList(mT, p1_1_alt, p2_1_alt))
                            #modelAlt2_rgp = RooGenericPdf(modelAltName+"2_rgp", "Thry. (expandDenom3)", "pow(@0/13000, -@1 - @3*log(@0/13000) ) * pow(1 - @0/13000, @2)", RooArgList(mT, p1_2_alt, p2_2_alt, p3_2_alt))
                            #modelAlt3_rgp = RooGenericPdf(modelAltName+"3_rgp", "Thry. (expandDenom4)", "pow(@0/13000, -@1 - @3*log(@0/13000) - @4*pow(log(@0/13000),2) ) * pow(1 - @0/13000, @2)", RooArgList(mT, p1_3_alt, p2_3_alt, p3_3_alt, p4_3_alt))
                            #modelAlt4_rgp = RooGenericPdf(modelAltName+"4_rgp", "Thry. (expandDenom5)", "pow(@0/13000, -@1 - @3*log(@0/13000) - @4*pow(log(@0/13000),2) - @5*pow(log(@0/13000),3) ) * pow(1 - @0/13000, @2)", RooArgList(mT, p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt, p5_4_alt))
                            #modelAlt1 = RooParametricShapeBinPdf(modelAltName+"1", "Thry. (expandDenom2)", modelBkg1_rgp, mT, RooArgList(p1_1_alt, p2_1_alt), histBkgData)
                            #modelAlt2 = RooParametricShapeBinPdf(modelAltName+"2", "Thry. (expandDenom3)", modelBkg2_rgp, mT, RooArgList(p1_2_alt, p2_2_alt, p3_2_alt), histBkgData)
                            #modelAlt3 = RooParametricShapeBinPdf(modelAltName+"3", "Thry. (expandDenom4)", modelBkg3_rgp, mT, RooArgList(p1_3_alt, p2_3_alt, p3_3_alt, p4_3_alt), histBkgData)
                            #modelAlt4 = RooParametricShapeBinPdf(modelAltName+"4", "Thry. (expandDenom5)", modelBkg4_rgp, mT, RooArgList(p1_4_alt, p2_4_alt, p3_4_alt, p4_4_alt, p5_4_alt), histBkgData)
                     
                            RSS_alt = {}
                            #if (ch == "highSVJ1_2016"): fitrange = "Low,High"
                            fitRes1_alt = modelAlt1.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                            fitRes2_alt = modelAlt2.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                            #fitRes3_alt = modelAlt3.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))
                            fitRes4_alt = modelAlt4.fitTo(obsData, RooFit.Extended(True), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange))

                            RSS_alt[fitRes1_alt.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelAlt1, obsData,  [fitRes1_alt], carddir,  nDataEvts, label = "alt")
                            RSS_alt[fitRes2_alt.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelAlt2, obsData,  [fitRes2_alt], carddir,  nDataEvts, label = "alt")
                            RSS_alt[fitRes3_alt.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelAlt3, obsData,  [fitRes3_alt], carddir,  nDataEvts, label = "alt")
                            RSS_alt[fitRes4_alt.floatParsFinal().getSize()] = getRSS(sig, ch, mT, modelAlt4, obsData,  [fitRes4_alt], carddir,  nDataEvts, label = "alt")
                            
                            drawTwoFuncs(sig, ch, mT, modelBkg1, modelAlt1, obsData, [fitRes1, fitRes1_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg1, modelAlt2, obsData, [fitRes1, fitRes2_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg1, modelAlt3, obsData, [fitRes1, fitRes3_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg1, modelAlt4, obsData, [fitRes1, fitRes4_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg2, modelAlt1, obsData, [fitRes2, fitRes1_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg2, modelAlt2, obsData, [fitRes2, fitRes2_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg2, modelAlt3, obsData, [fitRes2, fitRes3_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg2, modelAlt4, obsData, [fitRes2, fitRes4_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg3, modelAlt1, obsData, [fitRes3, fitRes1_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg3, modelAlt2, obsData, [fitRes3, fitRes2_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg3, modelAlt3, obsData, [fitRes3, fitRes3_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg3, modelAlt4, obsData, [fitRes3, fitRes4_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg4, modelAlt1, obsData, [fitRes4, fitRes1_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg4, modelAlt2, obsData, [fitRes4, fitRes2_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg4, modelAlt3, obsData, [fitRes4, fitRes3_alt], carddir,  nDataEvts, label = "dual")
                            drawTwoFuncs(sig, ch, mT, modelBkg4, modelAlt4, obsData, [fitRes4, fitRes4_alt], carddir,  nDataEvts, label = "dual")

                            length = 1
                            if(length<2):
                                   xframeAlt = mT.frame(ROOT.RooFit.Title("extended ML fit example"))

                                   c2 = ROOT.TCanvas()
                                   c2.cd()
                                   obsData.plotOn(xframeAlt, RooFit.Name("obsData"))

                                   modelAlt1.plotOn(xframeAlt, RooFit.Name("modelAlt1"), ROOT.RooFit.LineColor(ROOT.kPink))
                                   modelAlt2.plotOn(xframeAlt, RooFit.Name("modelAlt2"), ROOT.RooFit.LineColor(ROOT.kBlue))
                                   modelAlt3.plotOn(xframeAlt, RooFit.Name("modelAlt3"), ROOT.RooFit.LineColor(ROOT.kRed))
                                   modelAlt4.plotOn(xframeAlt, RooFit.Name("modelAlt4"), ROOT.RooFit.LineColor(ROOT.kGreen))

                                   chi2s_alt1 = xframeAlt.chiSquare("modelAlt1", "obsData",1)
                                   chi2s_alt2 = xframeAlt.chiSquare("modelAlt2", "obsData",2)
                                   chi2s_alt3 = xframeAlt.chiSquare("modelAlt3", "obsData",3)
                                   chi2s_alt4 = xframeAlt.chiSquare("modelAlt4", "obsData",4)

                                   xframeAlt.SetMinimum(0.002)
                                   xframeAlt.Draw()

                                   c2.SetLogy()
                                   c2.SaveAs("TestAfterFit_"+ch+"_Alt.pdf")



                     #*******************************************************#
                     #                                                       #
                     #                         Fisher                        #
                     #                                                       #
                     #*******************************************************#


                     ofile = open("FisherTest_%s.txt"%(ch),"w")
                     report = "Results from Fisher Test for category %s \n" % (ch)
                     #{"chiSquared":roochi2,"chi2" : chi2, "chi1" : chi1, "rss" : rss, "res" : res, "nbins" : hist.GetN(), "npar" : npar}
                     report += "func\tchi2\trss\tnBins\tnPar \n"
                     nParMin = RSS[fitRes1.floatParsFinal().getSize()]['npar']
                     for i in xrange(nParMin, nParMin+len(RSS)):
                            report += "   %i\t%.2f\t%.2f\t%i\t%i\n" % (i, RSS[i]['chiSquared'],RSS[i]['rss'],RSS[i]['nbins'],RSS[i]['npar'])
                     report += "*******************************************************\n"
                     report += "fTest = ((RSS1-RSS2)/(npar2-npar1))/(RSS2/(nBins-npar2))\n"
                     report += "*******************************************************\n"


                     order = 0
                     print "-"*25
                     print "function & $\\chi^2$ & RSS & ndof & F-test & result \\\\"
                     print "\\hline"
                     # BEGIN NEW WAY, tests in a 'single elimination' bracket
                     # begin with 1v2, test the `winner' vs 3, then test that winner vs 4. 
                     # which ever function wins the vs 4 test, is the function we use.
                     aCrit = 0.05
                     RTDict = {}
                     FDict = {}
                     for o1 in xrange(nParMin, nParMin+len(RSS)-1):
                            for o2 in xrange(o1+1,nParMin+len(RSS)):
                                   print(o1, o2)
                                   RTDict[str(o1)+"v"+str(o2)], FDict[str(o1)+"v"+str(o2)] = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], RSS[o1]['npar'], RSS[o2]['npar'], RSS[o2]["nbins"])
                                   report += "%d par vs %d par: CL=%.5f F_t=%.5f\n" % (RSS[o1]['npar'], RSS[o2]['npar'], RTDict[str(o1)+"v"+str(o2)], FDict[str(o1)+"v"+str(o2)])

                     if RTDict["{}v{}".format(RSS[nParMin]['npar'],RSS[nParMin+1]['npar'])] > aCrit:
                            if RTDict["{}v{}".format(RSS[nParMin]['npar'],RSS[nParMin+2]['npar'])] > aCrit:
                                   if RTDict["{}v{}".format(RSS[nParMin]['npar'],RSS[nParMin+3]['npar'])] > aCrit:
                                          order = RSS[RSS[nParMin]['npar']]['npar']
                                   else:
                                          order = RSS[RSS[nParMin+3]['npar']]['npar']
                            else:
                                   if RTDict["{}v{}".format(RSS[nParMin+2]['npar'],RSS[nParMin+3]['npar'])] > aCrit:
                                          order = RSS[RSS[nParMin+2]['npar']]['npar']
                                   else:
                                          order = RSS[RSS[nParMin+3]['npar']]['npar']
                     else:
                            if RTDict["{}v{}".format(RSS[nParMin+1]['npar'],RSS[nParMin+2]['npar'])] > aCrit:
                                   if RTDict["{}v{}".format(RSS[nParMin+1]['npar'],RSS[nParMin+3]['npar'])] > aCrit:
                                          order = RSS[RSS[nParMin+1]['npar']]['npar']
                                   else:
                                          order = RSS[RSS[nParMin+3]['npar']]['npar']
                            else:
                                   if RTDict["{}v{}".format(RSS[nParMin+2]['npar'],RSS[nParMin+3]['npar'])] > aCrit:
                                          order = RSS[RSS[nParMin+2]['npar']]['npar']
                                   else:
                                          order = RSS[RSS[nParMin+3]['npar']]['npar']
                     #OLD WAY OF DOING IT, only does n vs n+1
                     #for o1 in xrange(1, len(RSS)):
                     #       o2 = o1+1
                     #
                     #       CL = fisherTest(RSS[o1]['rss'], RSS[o2]['rss'], RSS[o1]['npar'], RSS[o2]['npar'], RSS[o2]["nbins"])
                     #
                     #       print "%d par vs %d par CL=%.2f  \n" % (RSS[o1]['npar'], RSS[o2]['npar'], CL),
                     #       report += "%d par vs %d par: CL=%.2f \n" % (RSS[o1]['npar'], RSS[o2]['npar'], CL)
                     #       if CL > 0.10: # The function with less parameters is enough
                     #              if not order:
                     #                     order = o1
                     #                     print "%d par are sufficient" % (RSS[o1]['npar'])
                     #                     #report += "%d par are sufficient \n" % (o1)
                     #       else:
                     #              print "%d par are needed" % (RSS[o2]['npar']),
                     #
                     #       print "\\\\"
                     moreParFlag = 0
                     if order == 0:
                            order = RSS[nParMin+3]["npar"]
                            moreParFlag = 1
                     print "\\hline"
                     print "-"*25   
                     print "Order is", order, "("+ch+")"
                     report += "Order is %d (%s)\n" % (order, ch)
                     report += ("2 param: " + ", ".join(['%.2f']*len(RSS[nParMin]["parVals"])) + "\n") % tuple(RSS[nParMin]["parVals"])
                     report += ("3 param: " + ", ".join(['%.2f']*len(RSS[nParMin+1]["parVals"])) + "\n") % tuple(RSS[nParMin+1]["parVals"])
                     report += ("4 param: " + ", ".join(['%.2f']*len(RSS[nParMin+2]["parVals"])) + "\n") % tuple(RSS[nParMin+2]["parVals"])
                     report += ("5 param: " + ", ".join(['%.2f']*len(RSS[nParMin+3]["parVals"])) + "\n") % tuple(RSS[nParMin+3]["parVals"])
                     report += "%d (%d) par are sufficient\n" % (RSS[order]['npar'], order)
                     if moreParFlag: report += "BUT really, more Pars are needed!"
                     for i in range(nParMin, nParMin+4):
                            report += "model%i chi2: %.2f\n" % (i, RSS[i]['chiSquared'])

                     ofile.write(report)
                     ofile.close()

                     if bias: 
                            print "Running in BIAS mode"

                            ofile_alt = open("FisherTest_alt_%s.txt"%(ch),"w")
                            report = "Results from Fisher Test on the alternative function for category %s \n" % (ch)
                            report += "func\tchi2\trss\tnBins\tnPar \n"
                            nParMin_alt = RSS_alt[fitRes1_alt.floatParsFinal().getSize()]['npar']
                            for i in xrange(nParMin_alt, nParMin_alt+len(RSS_alt)):
                                   report += "   %i\t%.2f\t%.2f\t%i\t%i\n" % (i, RSS_alt[i]['chiSquared'],RSS_alt[i]['rss'],RSS_alt[i]['nbins'],RSS_alt[i]['npar'])
                            report += "*******************************************************\n"
                            report += "fTest = ((RSS1-RSS2)/(npar2-npar1))/(RSS2/(nBins-npar2))\n"
                            report += "*******************************************************\n"
                            report += " Best Chi2 initial values from Brute Force \n"
                            #report += "f1 {}".format(alt1InitParam[0])
                            #report += "f2 {} {}".format(alt2InitParam[0],alt2InitParam[1])
                            report += "f3 {}\n".format(alt3InitParam)
                            report += reportAltExtra
                            #report += "f4 {} {} {} {}".format(alt4InitParam[0],alt4InitParam[1],alt4InitParam[2],alt4InitParam[3])


                            order_alt = 0
                            print "-"*25
                            print "function & $\\chi^2$ & RSS & ndof & F-test & result \\\\"
                            print "\\hline"
                            # BEGIN NEW WAY, tests in a 'single elimination' bracket
                            # begin with 1v2, test the `winner' vs 3, then test that winner vs 4. 
                            # which ever function wins the vs 4 test, is the function we use.
                            RTDict_alt = {}
                            FDict_alt = {}
                            for o1 in xrange(nParMin_alt, nParMin_alt+len(RSS_alt)-1):
                                   for o2 in xrange(o1+1,nParMin_alt+len(RSS_alt)):
                                          RTDict_alt[str(o1)+"v"+str(o2)], FDict_alt[str(o1)+"v"+str(o2)] = fisherTest(RSS_alt[o1]['rss'], RSS_alt[o2]['rss'], RSS_alt[o1]['npar'], RSS_alt[o2]['npar'], RSS_alt[o2]["nbins"])
                                          report += "%d par vs %d par: CL=%.5f F_t=%.5f\n" % (RSS_alt[o1]['npar'], RSS_alt[o2]['npar'], RTDict_alt[str(o1)+"v"+str(o2)], FDict_alt[str(o1)+"v"+str(o2)])

                            if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt]['npar'],RSS_alt[nParMin_alt+1]['npar'])] > aCrit:
                                   if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt]['npar'],RSS_alt[nParMin_alt+2]['npar'])] > aCrit:
                                          if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt]['npar'],RSS_alt[nParMin_alt+3]['npar'])] > aCrit:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt]['npar']]['npar']
                                          else:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+3]['npar']]['npar']
                                   else:
                                          if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt+2]['npar'],RSS_alt[nParMin_alt+3]['npar'])] > aCrit:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+2]['npar']]['npar']
                                          else:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+3]['npar']]['npar']
                            else:
                                   if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt+1]['npar'],RSS_alt[nParMin_alt+2]['npar'])] > aCrit:
                                          if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt+1]['npar'],RSS_alt[nParMin_alt+3]['npar'])] > aCrit:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+1]['npar']]['npar']
                                          else:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+3]['npar']]['npar']
                                   else:
                                          if RTDict_alt["{}v{}".format(RSS_alt[nParMin_alt+2]['npar'],RSS_alt[nParMin_alt+3]['npar'])] > aCrit:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+2]['npar']]['npar']
                                          else:
                                                 order_alt = RSS_alt[RSS_alt[nParMin_alt+3]['npar']]['npar']

                            #OLD WAY OF DOING IT, only does n vs n+1
                            #for o1 in xrange(1, len(RSS)):
                            #       #o2 = o1+1
                            #       for o2 in xrange(o1+1,len(RSS)+1):
                            #
                            #              CL = fisherTest(RSS_alt[o1]['rss'], RSS_alt[o2]['rss'], RSS_alt[o1]['npar'], RSS_alt[o2]['npar'], RSS_alt[o2]["nbins"])
                            #
                            #              print "%d par vs %d par CL=%.5f  \n" % (RSS_alt[o1]['npar'], RSS_alt[o2]['npar'], CL),
                            #              report += "%d par vs %d par: CL=%.5f \n" % (RSS_alt[o1]['npar'], RSS_alt[o2]['npar'], CL)
                            #              if CL > 0.1: # The function with less parameters is enough
                            #                     if not order_alt:
                            #                            order_alt = o1
                            #                            print "%d par are sufficient" % (RSS_alt[o1]['npar'])
                            #                            #report += "%d par are sufficient \n" % (o1)
                            #              else:
                            #                     print "%d par are needed" % (RSS_alt[o2]['npar']),
                            #
                            #              print "\\\\"
                            #END OLD WAY OF DOING IT
                            moreParFlag_alt = 0
                            if order_alt == 0:
                                   order_alt = 4
                                   moreParFlag_alt = 1
                            print "\\hline"
                            print "-"*25   
                            print "Order is", order_alt, "("+ch+")"
                            report += "Order is %d (%s)\n" % (order_alt, ch)
                            report += ("alt 1: " + ", ".join(['%.2f (%.2f)']*len(RSS_alt[nParMin_alt]["parVals"])) + "\n") % tuple(altMerge(RSS_alt[nParMin_alt]["parVals"],RSS_alt[nParMin_alt]["parErr"]))
                            report += ("alt 2: " + ", ".join(['%.2f (%.2f)']*len(RSS_alt[nParMin_alt+1]["parVals"])) + "\n") % tuple(altMerge(RSS_alt[nParMin_alt+1]["parVals"],RSS_alt[nParMin_alt+1]["parErr"]))
                            report += ("alt 3: " + ", ".join(['%.2f (%.2f)']*len(RSS_alt[nParMin_alt+2]["parVals"])) + "\n") % tuple(altMerge(RSS_alt[nParMin_alt+2]["parVals"],RSS_alt[nParMin_alt+2]["parErr"]))
                            report += ("alt 4: " + ", ".join(['%.2f (%.2f)']*len(RSS_alt[nParMin_alt+3]["parVals"])) + "\n") % tuple(altMerge(RSS_alt[nParMin_alt+3]["parVals"],RSS_alt[nParMin_alt+3]["parErr"]))
                            report += "%d par are sufficient\n" % (RSS_alt[order_alt]['npar'])
                            if moreParFlag_alt: report += "BUT really, more Pars are needed!"
                            iPar, iPar_alt = nParMin, nParMin_alt
                            for i in range(1,5):
                                   report += "model%i chi2, chi2_alt: %.2f %.2f\n" % (i, RSS[iPar]['chiSquared'],RSS_alt[iPar_alt]['chiSquared'])
                                   iPar+=1
                                   iPar_alt+=1

                            ofile_alt.write(report)
                            ofile_alt.close()
                     #temporarily change order based on which ever one is higher
                     #if (order_alt > order):
                     #       order = order_alt
                     #else:
                     #       order_alt = order
                     # force to use model4 (32 or 41)
                     #order = 5
                     if order==RSS[nParMin]['npar']:
                            modelBkg = modelBkg1#.Clone("Bkg")
                            #normzBkg = normzBkg2#.Clone("Bkg_norm")
                            fitRes = fitRes1
                     elif order==RSS[nParMin+1]['npar']:
                            modelBkg = modelBkg2#.Clone("Bkg")
                            #normzBkg = normzBkg2#.Clone("Bkg_norm")
                            fitRes = fitRes2
                     elif order==RSS[nParMin+2]['npar']:
                            modelBkg = modelBkg3#.Clone("Bkg")
                            #normzBkg = normzBkg3#.Clone("Bkg_norm")
                            fitRes = fitRes3
                     elif order==RSS[nParMin+3]['npar']:
                            modelBkg = modelBkg4#.Clone("Bkg")
                            #normzBkg = normzBkg4#.Clone("Bkg_norm")
                            fitRes = fitRes4
                     else:
                            print "Functions with", RSS[nParMin+3]['npar']+1, "or more parameters are needed to fit the background"
                            exit()

                     modelBkg.SetName(modelName)
                     normData.SetName(modelName+"_norm")


                     #*******************************************************#
                     #                                                       #
                     #                  Saving RooWorkspace                  #
                     #                                                       #
                     #*******************************************************#

                     wsfilename = "ws_{}.root".format(ch_red)
                     wfile_ = ROOT.TFile(wsfilename)
                     w_ = wfile_.FindObjectAny("BackgroundWS")
                     if not w_.__nonzero__() :  w_ = RooWorkspace("BackgroundWS", "workspace")
                     else:  w_ =  wfile_.Get("BackgroundWS")
                     print "Storing ", modelName
                     getattr(w_, "import")(modelBkg, RooFit.Rename(modelBkg.GetName())) #Bkg func with optimal num Paras

                     getattr(w_, "import")(obsData, RooFit.Rename("data_obs")) # data_obs histogram


                     if bias:
                            if order_alt==RSS_alt[nParMin_alt]['npar']:
                                   print "Alt Model is modelAlt1"
                                   modelAlt = modelAlt1#.Clone("Alt")
                                   fitRes = fitRes1_alt
                            elif order_alt==RSS_alt[nParMin_alt+1]['npar']:
                                   print "Alt Model is modelAlt2"
                                   modelAlt = modelAlt2#.Clone("Alt")
                                   fitRes = fitRes2_alt
                            elif order_alt==RSS_alt[nParMin_alt+2]['npar']:
                                   print "Alt Model is modelAlt3"
                                   modelAlt = modelAlt3#.Clone("Alt")
                                   fitRes = fitRes3_alt
                            elif order_alt==RSS_alt[nParMin_alt+3]['npar']:
                                   print "Alt Model is modelAlt4"
                                   modelAlt = modelAlt4#.Clone("Alt")
                                   fitRes = fitRes4_alt
                            else:
                                   print "Functions with", RSS_alt[nParMin_alt+3]['npar']+1, "or more parameters are needed to fit the background"
                                   exit()
                            modelAlt.SetName(modelAltName)
                            normAlt.SetName(modelAltName+"_norm")
                            getattr(w_, "import")(modelAlt, RooFit.Rename(modelAlt.GetName())) # Alt func with optimal num Paras

                     wstatus = w_.writeToFile(wsfilename, False)




