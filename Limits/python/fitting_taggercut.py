import ROOT
from ROOT import RooRealVar, RooDataHist, RooArgList, RooGenericPdf, RooBernstein, RooExtendPdf, RooCmdArg, RooWorkspace, RooFit, RooDataSet, RooArgSet, RooCategory, RooFitResult, RooCurve, RooParametricShapeBinPdf
import json
import os, sys
from array import array
import copy, math, pickle
import collections
import numpy as np
from numpy import ndarray
from bruteForce import VarInfo, PdfInfo, varToInfo, bruteForce, silence
#silence()

mopt = ROOT.Math.MinimizerOptions()
mopt.SetMaxFunctionCalls(100000)
mopt.SetMaxIterations(100000)

def getHist(ch, process, ifile):
       hName = ch.replace("XXX",process)
       print(hName)
       h = ifile.Get(hName)
       h.SetDirectory(0)
       return h

def getCard(sig, cat, ifilename):
       ifile = ROOT.TFile.Open(ifilename)

       hist = getHist(cat, sig, ifile)
       histBkgData = getHist(cat, "QCD", ifile)
       histData = getHist(cat, "data_obs", ifile)

       print("channel ", cat)
       print("signal ", sig)

       xvarmin = 720.
       xvarmax = 1700.
       mT = RooRealVar("mH"+cat.replace("XXX","QCD"),"m_{T}",xvarmin,xvarmax,"GeV")
       binMin = histData.FindBin(xvarmin)
       binMax = histData.FindBin(xvarmax)
       obsData = RooDataHist("data_obs","Data",RooArgList(mT),histData,1.)
       print("Bkg Integral: ", histData.Integral())
       nBkgEvts = histBkgData.Integral(binMin, binMax)
       nDataEvts = histData.Integral(binMin, binMax)
       
       normBkg = RooRealVar("Bkg_"+cat.replace("XXX","QCD")+"_norm", "Number of background events", nBkgEvts, 0., 2.e6)
       normData = RooRealVar("Data_"+cat.replace("XXX","QCD")+"_norm", "Number of background events", nDataEvts, 0., 2.e6)
       modelName = "Bkg_"+cat.replace("XXX","QCD")
       modelAltName =  "Bkg_Alt_"+cat.replace("XXX","QCD")

       lowerLimit = -20
       upperLimit = 150

       p1_1 = RooRealVar(cat.replace("__XXX__nominal","") + "_p1_1", "p1", 1., lowerLimit, upperLimit)
       p1_2 = RooRealVar(cat.replace("__XXX__nominal","") + "_p1_2", "p1", 1., lowerLimit, upperLimit)
       p1_3 = RooRealVar(cat.replace("__XXX__nominal","") + "_p1_3", "p1", 1., lowerLimit, upperLimit)
       p1_4 = RooRealVar(cat.replace("__XXX__nominal","") + "_p1_4", "p1", 1., lowerLimit, upperLimit)

       p2_1 = RooRealVar(cat.replace("__XXX__nominal","") + "_p2_1", "p2", 1., lowerLimit, upperLimit)
       p2_2 = RooRealVar(cat.replace("__XXX__nominal","") + "_p2_2", "p2", 1., lowerLimit, upperLimit)
       p2_3 = RooRealVar(cat.replace("__XXX__nominal","") + "_p2_3", "p2", 1., lowerLimit, upperLimit)
       p2_4 = RooRealVar(cat.replace("__XXX__nominal","") + "_p2_4", "p2", 1., lowerLimit, upperLimit)
       
       p3_2 = RooRealVar(cat.replace("__XXX__nominal","") + "_p3_2", "p3", 1., lowerLimit, upperLimit)
       p3_3 = RooRealVar(cat.replace("__XXX__nominal","") + "_p3_3", "p3", 1., lowerLimit, upperLimit)
       p3_4 = RooRealVar(cat.replace("__XXX__nominal","") + "_p3_4", "p3", 1., lowerLimit, upperLimit)
       
       p4_3 = RooRealVar(cat.replace("__XXX__nominal","") + "_p4_3", "p4", 1., lowerLimit, upperLimit)
       p4_4 = RooRealVar(cat.replace("__XXX__nominal","") + "_p4_4", "p4", 1., lowerLimit, upperLimit)
       
       p5_4 = RooRealVar(cat.replace("__XXX__nominal","") + "_p5_4", "p5", 1., lowerLimit, upperLimit)


       modelBkg1_rgp = RooGenericPdf(modelName+"1_rgp", "Thry. fit (11)", "pow(1 - @0/13000, @1) * pow(@0/13000, -(@2))", RooArgList(mT, p1_1, p2_1))
       modelBkg2_rgp = RooGenericPdf(modelName+"2_rgp", "Thry. fit (12)", "pow(1 - @0/13000, @1) * pow(@0/13000, -(@2+@3*log(@0/13000)))", RooArgList(mT, p1_2, p2_2, p3_2))
       modelBkg3_rgp = RooGenericPdf(modelName+"3_rgp", "Thry. fit (22)", "pow(1 - @0/13000, @1+@2*log(@0/13000)) * pow(@0/13000, -(@3+@4*log(@0/13000)))", RooArgList(mT, p1_3, p2_3, p3_3, p4_3))
       modelBkg4_rgp = RooGenericPdf(modelName+"4_rgp", "Thry. fit (32)", "pow(1 - @0/13000, @1+@2*log(@0/13000)+@3*pow(log(@0/13000),2)) * pow(@0/13000, -(@4+@5*log(@0/13000)))", RooArgList(mT, p1_4, p2_4, p3_4, p4_4, p5_4))


       modelBkg = [
              RooParametricShapeBinPdf(modelName+"1", "Thry. Fit (11)", modelBkg1_rgp, mT, RooArgList(p1_1, p2_1), histBkgData),
              RooParametricShapeBinPdf(modelName+"2", "Thry. Fit (12)", modelBkg2_rgp, mT, RooArgList(p1_2, p2_2, p3_2), histBkgData),
              RooParametricShapeBinPdf(modelName+"3", "Thry. Fit (22)", modelBkg3_rgp, mT, RooArgList(p1_3, p2_3, p3_3, p4_3), histBkgData),
              RooParametricShapeBinPdf(modelName+"4", "Thry. Fit (32)", modelBkg4_rgp, mT, RooArgList(p1_4, p2_4, p3_4, p4_4, p5_4), histBkgData),
       ]

       #modelBkg = [
       #       RooParametricShapeBinPdf(modelName+"1", "Thry. Fit (11)", modelBkg1_rgp, mT, RooArgList(p1_1, p2_1), histData),
       #       RooParametricShapeBinPdf(modelName+"2", "Thry. Fit (12)", modelBkg2_rgp, mT, RooArgList(p1_2, p2_2, p3_2), histData),
       #       RooParametricShapeBinPdf(modelName+"3", "Thry. Fit (22)", modelBkg3_rgp, mT, RooArgList(p1_3, p2_3, p3_3, p4_3), histData),
       #       RooParametricShapeBinPdf(modelName+"4", "Thry. Fit (32)", modelBkg4_rgp, mT, RooArgList(p1_4, p2_4, p3_4, p4_4, p5_4), histData),
       #]


       fitrange = "Full"
       fitRes = [modelBkg[i].fitTo(obsData, RooFit.Extended(False), RooFit.Save(1), RooFit.SumW2Error(True), RooFit.Strategy(2), RooFit.Minimizer("Minuit2"), RooFit.PrintLevel(2), RooFit.Range(fitrange)) for i in range(len(modelBkg))]


       #**********************************************************                                                                                                                            
       #                    ALTERNATIVE MODEL                    *                                                                                                                            
       #**********************************************************         
       normAlt = RooRealVar("Bkg_"+cat.replace("XXX","QCD")+"alt_norm", "Number of background events", nBkgEvts, 0., 2.e6)
       normData = RooRealVar("Data_"+cat.replace("XXX","QCD")+"alt_norm", "Number of background events", nDataEvts, 0., 2.e6)

       lowAlt = -100
       highAlt = 150


       pdfsAlt = [
              PdfInfo(modelAltName+"1", "Alt. Fit 1par", "exp(@1*(@0/13000))", hist=histBkgData,
                      x = varToInfo(mT, True),
                      pars = [
                             VarInfo(cat.replace("__XXX__nominal","") + "_p1_1_alt", "p1", 1., lowAlt, highAlt, 0, "", False),
                      ],
               ),
              PdfInfo(modelAltName+"2", "Alt. Fit 2par", "exp(@1*(@0/13000)) * pow(@0/13000,@2)", hist=histBkgData,
                      x = varToInfo(mT, True),
                      pars = [
                             VarInfo(cat.replace("__XXX__nominal","") + "_p1_2_alt", "p1", 1., lowAlt, highAlt, 0, "", False),
                             VarInfo(cat.replace("__XXX__nominal","") + "_p2_2_alt", "p2", 1., lowAlt, highAlt, 0, "", False),
                      ],
               ),
              PdfInfo(modelAltName+"3", "Alt. Fit 3par", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)))", hist=histBkgData,
                      x = varToInfo(mT, True),
                      pars = [
                             VarInfo(cat.replace("__XXX__nominal","") + "_p1_3_alt", "p1", 1., lowAlt, highAlt, 0, "", False),
                             VarInfo(cat.replace("__XXX__nominal","") + "_p2_3_alt", "p2", 1., lowAlt, highAlt, 0, "", False),
                             VarInfo(cat.replace("__XXX__nominal","") + "_p3_3_alt", "p3", 1., lowAlt, highAlt, 0, "", False),
                      ],
               )#,
              #PdfInfo(modelAltName+"4", "Alt. Fit 4par", "exp(@1*(@0/13000)) * pow(@0/13000,@2*(1+@3*log(@0/13000)*(1+@4*log(@0/13000))))", hist=histBkgData,
              #        x = varToInfo(mT, True),
              #        pars = [
              #               VarInfo(cat.replace("XXX","QCD") + "_p1_4_alt", "p1", 1., lowAlt, highAlt, 0, "", False),
              #               VarInfo(cat.replace("XXX","QCD") + "_p2_4_alt", "p2", 1., lowAlt, highAlt, 0, "", False),
              #               VarInfo(cat.replace("XXX","QCD") + "_p3_4_alt", "p3", 1., lowAlt, highAlt, 0, "", False),
              #               VarInfo(cat.replace("XXX","QCD") + "_p4_4_alt", "p4", 1., lowAlt, highAlt, 0, "", False),
              #        ],
              # )
       ]
       modelAlt = []
       objsAlt = []
       fitResAlt = []

       for pdfAlt in pdfsAlt:
              print("---------------TEST----------------")
              print("fit ",pdfAlt.name)
              # truncate brute force at 3 param (4 takes too long, has some segfaults)                                                                                                    
              #mtmp, otmp, ftmp = bruteForce(pdfAlt, obsData, initvals, npool, [3,1.], 2)                                                                                                 
              mtmp, otmp, ftmp = bruteForce(pdfAlt, obsData, [1.0] , 1, None, 2)
              modelAlt.append(mtmp)
              objsAlt.append(otmp)
              fitResAlt.append(ftmp)

              #*******************************************************#                                                                                                                                                  #                                                       #                                                                                                                                    
              #                  Saving RooWorkspace                  #                                                                                                                                    
              #                                                       #                                                                                                                                    
              #*******************************************************#                                                                                                                                     

              rfilename = "fitResults.root"
              rfile_ = ROOT.TFile.Open(rfilename, "RECREATE")
              w_ = RooWorkspace("FitWS", "workspace")
              getattr(w_, "import")(obsData)
              for i in range(len(modelBkg)):
                     getattr(w_, "import")(modelBkg[i])
                     fitRes[i].Write()
              for i in range(len(modelAlt)):
                     getattr(w_, "import")(modelAlt[i])
                     fitResAlt[i].Write()
              rfile_.Close()

              wsfilename = "ws_allFits.root"
              wstatus = w_.writeToFile(wsfilename, True)