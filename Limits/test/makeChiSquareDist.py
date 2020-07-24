import ROOT as rt
import os
rt.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
rt.gStyle.SetOptStat(111111)
rt.gStyle.SetOptFit(1011)
rt.gStyle.SetPalette(rt.kRainBow)

# runover each SR to fit all 100 toys to the main function
eosArea = "root://cmsxrootd.fnal.gov//store/user/cfallon/biasStudies_FourStepBias_jul21/"


listOfParams1 = [
['3000', '20', '03', 'peak'],
['1500', '20', '03', 'peak'],
['1600', '20', '03', 'peak'],
['1700', '20', '03', 'peak'],
['1800', '20', '03', 'peak'],
['1900', '20', '03', 'peak'],
['2000', '20', '03', 'peak'],
['2100', '20', '03', 'peak'],
['2200', '20', '03', 'peak'],
['2300', '20', '03', 'peak'],
['2400', '20', '03', 'peak'],
['2500', '20', '03', 'peak'],
['2600', '20', '03', 'peak'],
['2700', '20', '03', 'peak'],
['2800', '20', '03', 'peak'],
['2900', '20', '03', 'peak']]

listOfParams2 = [
['3100', '20', '03', 'peak'],
['3200', '20', '03', 'peak'],
['3300', '20', '03', 'peak'],
['3400', '20', '03', 'peak'],
['3500', '20', '03', 'peak'],
['3600', '20', '03', 'peak'],
['3700', '20', '03', 'peak'],
['3800', '20', '03', 'peak'],
['3900', '20', '03', 'peak'],
['4000', '20', '03', 'peak'],
['4100', '20', '03', 'peak'],
['4200', '20', '03', 'peak'],
['4300', '20', '03', 'peak'],
['4400', '20', '03', 'peak'],
['4500', '20', '03', 'peak'],
['3000', '1', '03', 'peak']]

listOfParams3 = [
['3000', '5', '03', 'peak'],
['3000', '10', '03', 'peak'],
['3000', '30', '03', 'peak'],
['3000', '40', '03', 'peak'],
['3000', '50', '03', 'peak'],
['3000', '60', '03', 'peak'],
['3000', '70', '03', 'peak'],
['3000', '80', '03', 'peak'],
['3000', '90', '03', 'peak'],
['3000', '100', '03', 'peak'],
['3000', '20', '0', 'peak'],
['3000', '20', '01', 'peak'],
['3000', '20', '02', 'peak'],
['3000', '20', '04', 'peak'],
['3000', '20', '05', 'peak'],
['3000', '20', '06', 'peak']]

listOfParams4 = [
['3000', '20', '07', 'peak'],
['3000', '20', '08', 'peak'],
['3000', '20', '09', 'peak'],
['3000', '20', '1', 'peak'],
['3000', '20', '03', 'low'],
['3000', '20', '03', 'high']]

listOfParams5 = [
['2200', '20', '03', 'peak'],
['2400', '20', '03', 'peak']]

baseline = [['3000', '20', '03', 'peak']]

#regions = ["lowSVJ2","highSVJ2"]
regions = ["lowCut","lowSVJ2","highCut","highSVJ2"]
#expSig = ""# "" for excpSig = 0, "_expSig1" for expSig = 1, add "_extra" for SVJ options, or nothing for Dijet options
#n = 0 if expSig == "" else int(expSig.split("_")[1][-1:])

pae = ""
pae2 = ""
for sigPars in baseline:
	SVJNAME = "SVJ_mZprime{}_mDark{}_rinv{}_alpha{}".format(sigPars[0],sigPars[1],sigPars[2],sigPars[3])
	print("************************",SVJNAME,"************************")
	print("files to be opened from: " + eosArea + SVJNAME)
	for region in regions:
		print("/ws_SVJ_mZprime3000_mDark20_rinv03_alphapeak_{}_2018_template.root".format(region))
		wsFile = rt.TFile.Open(eosArea+SVJNAME+"/ws_SVJ_mZprime3000_mDark20_rinv03_alphapeak_{}_2018_template.root".format(region),"read")
		# signal is a RooDataHist within SVJ RooWorkspace
		svjWS = wsFile.Get("SVJ")
		sigDataSet = rt.RooDataHist()
		sigDataSet = svjWS.data("SVJ_mZprime3000_mDark20_rinv03_alphapeak")
		sigHist = sigDataSet.createHistogram("mH")
		for expSig in ["Sig0GenMainFitMain","Sig1GenMainFitMain","Sig0GenAltFitMain","Sig1GenAltFitMain","Sig0GenMainFitAlt","Sig1GenMainFitAlt","Sig0GenAltFitAlt","Sig1GenAltFitAlt"]:
			for combineOpts in [""]:#["OptS","OptD"]:
				bigName = region+combineOpts+expSig
				n = int(expSig[3])
				print("/fitDiagnostics"+bigName+".root")
				print("/higgsCombine"+bigName+".FitDiagnostics.mH120.123456.root")
				print("/higgsCombine"+bigName.split("Fit")[0]+".MultiDimFit.mH120.root")
				fitDiagFile = rt.TFile.Open(eosArea + SVJNAME + "/fitDiagnostics"+bigName+".root","read")
				fitOnlyFile = rt.TFile.Open(eosArea + SVJNAME + "/higgsCombine"+bigName+".FitDiagnostics.mH120.123456.root","read")
				mdfFile = rt.TFile.Open(eosArea + SVJNAME + "/higgsCombine"+bigName.split("Fit")[0]+".MultiDimFit.mH120.root","read")
				wsMDF = mdfFile.Get("w")
				snapshotArgList = wsMDF.getSnapshot("MultiDimFit")
				#dataObsFile = rt.TFile.Open(eosArea + SVJNAME + "/ws_"+SVJNAME+"_"+region+"_2018_template.root","read")
				#if (type(fitDiagFile) == type(rt.TFile())) or (type(fitOnlyFile) == type(rt.TFile())) or(type(dataObsFile) == type(rt.TFile())):
				if (type(fitDiagFile) == type(rt.TFile())) or (type(fitOnlyFile) == type(rt.TFile())):
					continue
				#svjWs = dataObsFile.Get("SVJ")
				#data = rt.RooDataHist()
				#data = svjWs.data("data_obs")
				#genPdf = svjWs.pdf("Bkg_"+region+"_2018")
				tree = fitDiagFile.Get("tree_fit_sb")
				limit = fitOnlyFile.Get("limit")
				
				chi2Div = 1.55

				rDownLim = -5
				rUpLim = 5
				downLimitrErr = 0
				upLimitrErr = 3
				downLimitRMU = -7
				upLimitRMU = 7
				parLimDown1 = -50
				parLimUp1 = 50
				parLimDown2 = -50
				parLimUp2 = 50
				parLimDown3 = -50
				parLimUp3 = 50
				parLimDown4 = -50
				parLimUp4 = 50
				chi2LimitDown = 0
				chi2LimitUp = 500
				if region == "highCut":
					nPar = 3
					nParAlt = 4
					eitLimitUp = 12000 # events in toy
					eitLimitDown = 10000
				elif region == "highSVJ2":
					nPar = 1
					nParAlt = 1
					eitLimitUp = 1000 # events in toy
					eitLimitDown = 0
				elif region == "lowCut":
					nPar = 2
					nParAlt = 3
					eitLimitUp = 80000 # events in toy
					eitLimitDown = 70000
				elif region == "lowSVJ2":
					nPar = 2
					nParAlt = 2
					eitLimitUp = 2000 # events in toy
					eitLimitDown = 0

				
				nBins = 50
				rHist = rt.TH1F("rHist","r, all Events",nBins,rDownLim,rUpLim)
				rHistChi2Up = rt.TH1F("rHistChi2Up","r, chi2 > {}".format(chi2Div),nBins,rDownLim,rUpLim)
				rHistChi2Down = rt.TH1F("rHistChi2Down","r, chi2 < {}".format(chi2Div),nBins,rDownLim,rUpLim)

				rErrHist = rt.TH1F("rErrHist","rErr, all Events",nBins,downLimitrErr,upLimitrErr)
				rErrHistChi2Up = rt.TH1F("rErrHistChi2Up","rErr, chi2 > {}".format(chi2Div),nBins,downLimitrErr,upLimitrErr)
				rErrHistChi2Down = rt.TH1F("rErrHistChi2Down","rErr, chi2 < {}".format(chi2Div),nBins,downLimitrErr,upLimitrErr)

				rmuHist = rt.TH1F("rmuHist","(r-{})/rErr, all Events".format(n),nBins,downLimitRMU,upLimitRMU)
				rmuHistChi2Up = rt.TH1F("rmuHistChi2Up","(r-{})/rErr, chi2 > {}".format(n,chi2Div),nBins,downLimitRMU,upLimitRMU)
				rmuHistChi2Down = rt.TH1F("rmuHistChi2Down","(r-{})/rErr, chi2 < {}".format(n,chi2Div),nBins,downLimitRMU,upLimitRMU)

				p1Hist = rt.TH1F("p1Hist","p1, all events", nBins,parLimDown1,parLimUp1)
				p1HistChi2Up = rt.TH1F("p1HistChi2Up","p1, chi2 > {}".format(chi2Div), nBins,parLimDown1,parLimUp1)
				p1HistChi2Down = rt.TH1F("p1HistChi2Down","p1, chi2 < {}".format(chi2Div), nBins,parLimDown1,parLimUp1)

				p2Hist = rt.TH1F("p2Hist","p2, all events", nBins,parLimDown2,parLimUp2)
				p2HistChi2Up = rt.TH1F("p2HistChi2Up","p2, chi2 > {}".format(chi2Div), nBins,parLimDown2,parLimUp2)
				p2HistChi2Down = rt.TH1F("p2HistChi2Down","p2, chi2 < {}".format(chi2Div), nBins,parLimDown2,parLimUp2)

				p3Hist = rt.TH1F("p3Hist","p3, all events", nBins,parLimDown3,parLimUp3)
				p3HistChi2Up = rt.TH1F("p3HistChi2Up","p3, chi2 > {}".format(chi2Div), nBins,parLimDown3,parLimUp3)
				p3HistChi2Down = rt.TH1F("p3HistChi2Down","p3, chi2 < {}".format(chi2Div), nBins,parLimDown3,parLimUp3)

				p4Hist = rt.TH1F("p4Hist","p4, all events", nBins,parLimDown4,parLimUp4)
				p4HistChi2Up = rt.TH1F("p4HistChi2Up","p4, chi2 > {}".format(chi2Div), nBins,parLimDown4,parLimUp4)
				p4HistChi2Down = rt.TH1F("p4HistChi2Down","p4, chi2 < {}".format(chi2Div), nBins,parLimDown4,parLimUp4)

				chi2Hist = rt.TH1F("chi2Hist","chi2, all events", nBins, chi2LimitDown, chi2LimitUp)
				chi2HistChi2Up = rt.TH1F("chi2HistChi2Up","chi2, chi2 > {}".format(chi2Div), nBins, chi2LimitDown, chi2LimitUp)
				chi2HistChi2Down = rt.TH1F("chi2HistChi2Down","chi2, chi2 < {}".format(chi2Div), nBins, chi2LimitDown, chi2LimitUp)

				eitHist = rt.TH1F("eitHist","Events in Toy, all events", nBins, eitLimitDown, eitLimitUp)
				eitHistChi2Up = rt.TH1F("eitHistChi2Up","eit, chi2 > {}".format(chi2Div), nBins, eitLimitDown, eitLimitUp)
				eitHistChi2Down = rt.TH1F("eitHistChi2Down","eit, chi2 < {}".format(chi2Div), nBins, eitLimitDown, eitLimitUp)

				rHist.SetLineColor(rt.kBlack)
				rHistChi2Up.SetLineColor(rt.kBlue)
				rHistChi2Down.SetLineColor(rt.kRed)
				rErrHist.SetLineColor(rt.kBlack)
				rErrHistChi2Up.SetLineColor(rt.kBlue)
				rErrHistChi2Down.SetLineColor(rt.kRed)
				rmuHist.SetLineColor(rt.kBlack)
				rmuHistChi2Up.SetLineColor(rt.kBlue)
				rmuHistChi2Down.SetLineColor(rt.kRed)
				p1Hist.SetLineColor(rt.kBlack)
				p1HistChi2Up.SetLineColor(rt.kBlue)
				p1HistChi2Down.SetLineColor(rt.kRed)
				p2Hist.SetLineColor(rt.kBlack)
				p2HistChi2Up.SetLineColor(rt.kBlue)
				p2HistChi2Down.SetLineColor(rt.kRed)
				p3Hist.SetLineColor(rt.kBlack)
				p3HistChi2Up.SetLineColor(rt.kBlue)
				p3HistChi2Down.SetLineColor(rt.kRed)
				p4Hist.SetLineColor(rt.kBlack)
				p4HistChi2Up.SetLineColor(rt.kBlue)
				p4HistChi2Down.SetLineColor(rt.kRed)
				chi2Hist.SetLineColor(rt.kBlack)
				chi2HistChi2Up.SetLineColor(rt.kBlue)
				chi2HistChi2Down.SetLineColor(rt.kRed)
				eitHist.SetLineColor(rt.kBlack)
				eitHistChi2Up.SetLineColor(rt.kBlue)
				eitHistChi2Down.SetLineColor(rt.kRed)

				rHist.SetLineWidth(2)
				rHistChi2Up.SetLineWidth(2)
				rHistChi2Down.SetLineWidth(2)
				rErrHist.SetLineWidth(2)
				rErrHistChi2Up.SetLineWidth(2)
				rErrHistChi2Down.SetLineWidth(2)
				rmuHist.SetLineWidth(2)
				rmuHistChi2Up.SetLineWidth(2)
				rmuHistChi2Down.SetLineWidth(2)
				p1Hist.SetLineWidth(2)
				p1HistChi2Up.SetLineWidth(2)
				p1HistChi2Down.SetLineWidth(2)
				p2Hist.SetLineWidth(2)
				p2HistChi2Up.SetLineWidth(2)
				p2HistChi2Down.SetLineWidth(2)
				p3Hist.SetLineWidth(2)
				p3HistChi2Up.SetLineWidth(2)
				p3HistChi2Down.SetLineWidth(2)
				p4Hist.SetLineWidth(2)
				p4HistChi2Up.SetLineWidth(2)
				p4HistChi2Down.SetLineWidth(2)
				chi2Hist.SetLineWidth(2)
				chi2HistChi2Up.SetLineWidth(2)
				chi2HistChi2Down.SetLineWidth(2)
				eitHist.SetLineWidth(2)
				eitHistChi2Up.SetLineWidth(2)
				eitHistChi2Down.SetLineWidth(2)
				


				#snapshotArgList
				# var names are <region>_p<i>_<nPar>
				mdfParList = [0,0,0,0]
				mdfParListAlt = [0,0,0,0]
				for i in [1,2,3,4]:
					if i <= nPar:
						mdfParList[i-1] = snapshotArgList.getRealValue(region+"_p"+str(i)+"_"+str(nPar))
					if i <= nParAlt:
						mdfParListAlt[i-1] = snapshotArgList.getRealValue(region+"_p"+str(i)+"_"+str(nParAlt)+"_alt")

				pae+="{} {} {} {} {} {} {} {} {} {}\n".format(region, expSig,mdfParList[0],mdfParList[1],mdfParList[2],mdfParList[3],mdfParListAlt[0],mdfParListAlt[1],mdfParListAlt[2],mdfParListAlt[3] )
					

				listOfFuncs = []
				nPass = 0
				nTotal = 0
				for iEvt in range(limit.GetEntries()):
					limit.GetEvent(iEvt)
					if limit.quantileExpected != -1:
						continue
					tree.GetEvent(limit.iToy)
					toy = fitOnlyFile.Get("toys/toy_{}".format(limit.iToy))
					#toyExp = getattr(tree,"n_exp_final_bin"+region+"_2018_proc_roomultipdf")
					toyExp = toy.sumEntries()

					rHistVal = tree.r
					rErrHistVal = tree.rErr
					if rErrHistVal == 0:
						continue
					rmuHistVal = (tree.r-int(n))/tree.rErr
					if bigName[-3:] != "Alt": #for fitting at Main func
						if nPar == 1:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_1")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * pow(x/13000, -[1])",1500,8000))
						elif nPar == 2:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_2")
							p2 = getattr(limit,"trackedParam_"+region+"_p2_2")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * pow(1 - x/13000, [2]) * pow(x/13000, -[1])",1500,8000))
						elif nPar == 3:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_3")
							p2 = getattr(limit,"trackedParam_"+region+"_p2_3")
							p3 = getattr(limit,"trackedParam_"+region+"_p3_3")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * pow(1 - x/13000, [2]) * pow(x/13000, -[1]-[3]*log(x/13000))",1500,8000))
						else:
							print("nPar is not 1, 2, nor 3!")
							exit(0)
					elif bigName[-3:] == "Alt": #for fitting with Alt Func
						if nParAlt == 1:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_1_alt")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * exp([1]*x/13000)",1500,8000))
						elif nParAlt == 2:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_2_alt")
							p2 = getattr(limit,"trackedParam_"+region+"_p2_2_alt")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * exp([1]*x/13000 + [2]*log(x/13000))",1500,8000))
						elif nParAlt == 3:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_3_alt")
							p2 = getattr(limit,"trackedParam_"+region+"_p2_3_alt")
							p3 = getattr(limit,"trackedParam_"+region+"_p3_3_alt")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * exp([1]*x/13000 + [2]*log(x/13000) + [3]*pow(log(x/13000),2))",1500,8000))
						elif nParAlt == 4:
							p1 = getattr(limit,"trackedParam_"+region+"_p1_4_alt")
							p2 = getattr(limit,"trackedParam_"+region+"_p2_4_alt")
							p3 = getattr(limit,"trackedParam_"+region+"_p3_4_alt")
							p4 = getattr(limit,"trackedParam_"+region+"_p4_4_alt")
							listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[0] * exp([1]*x/13000 + [2]*log(x/13000) + [3]*pow(log(x/13000),2) + [4]*pow(log(x/13000),3))",1500,8000))
						else:
							print("nParAlt is not 1, 2, 3, nor 4!")
							exit(0)

					if bigName[-3:] == "Alt": nPar = nParAlt
					listOfFuncs[-1].SetParameter(1,p1)
					if nPar >= 2:
						listOfFuncs[-1].SetParameter(2,p2)
					if nPar >= 3:
						listOfFuncs[-1].SetParameter(3,p3)
					if nPar >= 4:
						listOfFuncs[-1].SetParameter(4,p4)
					# pdf's in RooFit do not have a normlization factor (i.e., Sum(allspace) of pdf = 1)
					# so we need to scale it to our dataset.
					# first, set norm to 1, and we know the number of events in the toy)
					# then scale the function by numEvents divided by intergral of function without a normialztion
					# i.e., first normalize to 1 (divide by integral), then scale to numEvents
					# factor of 50 is becaue our bins are 50 GeV wide
					norm = 1
					listOfFuncs[-1].SetParameter(0,norm)
					denom = listOfFuncs[-1].Integral(1500,8000) 
					if denom > 0:
						norm = toyExp/listOfFuncs[-1].Integral(1500,8000)*50
					else:
						continue
					listOfFuncs[-1].SetParameter(0,norm)
					chi2 = 0
					for iBin in range(toy.numEntries()):
						toy.get(iBin)
						x = toy.get(iBin).getRealValue("mH")
						Ei = listOfFuncs[-1].Eval(x) + rHistVal*sigHist.GetBinContent(iBin)
						#Ei = listOfFuncs[-1].Eval(x)
						Oi = toy.weight()
						
						#print(x, Oi, Ei)
						try:
							chi2 += ((Oi-Ei)**2)/Ei
						except ZeroDivisionError:
							chi2 += 0
					ndf = 130 - nPar - 2 # bins in mT histo, minus nPar, minus 2 (for normalization and r_ext)
					chi2Hist.Fill(chi2)
					#print(chi2, ndf, chi2/ndf)

					rHist.Fill(rHistVal)
					rErrHist.Fill(rErrHistVal)
					rmuHist.Fill(rmuHistVal)
					p1Hist.Fill(p1)
					if nPar >= 2:
						p2Hist.Fill(p2)
					if nPar >= 3:
						p3Hist.Fill(p3)
					if nPar >= 4:
						p4Hist.Fill(p4)
					eitHist.Fill(toyExp)

					varCheck = (rt.Math.chisquared_cdf_c(chi2, ndf) > 0.05) # pass means chi2 is lower than crit value of alpha = 0.05
					nTotal += 1
					nPass += int(varCheck)
					#varCheck = (chi2/ndf < chi2Div)

					rHistChi2Up.Fill(rHistVal, varCheck)
					rErrHistChi2Up.Fill(rErrHistVal, varCheck)
					rmuHistChi2Up.Fill(rmuHistVal, varCheck)
					p1HistChi2Up.Fill(p1, varCheck)
					if nPar >= 2:
						p2HistChi2Up.Fill(p2, varCheck)
					if nPar >= 3:
						p3HistChi2Up.Fill(p3, varCheck)
					if nPar >= 4:
						p4HistChi2Up.Fill(p4, varCheck)
					chi2HistChi2Up.Fill(chi2, varCheck)
					eitHistChi2Up.Fill(toyExp, varCheck)

					rHistChi2Down.Fill(rHistVal, not varCheck)
					rErrHistChi2Down.Fill(rErrHistVal, not varCheck)
					rmuHistChi2Down.Fill(rmuHistVal, not varCheck)
					p1HistChi2Down.Fill(p1, not varCheck)
					if nPar >= 2:
						p2HistChi2Down.Fill(p2, not varCheck)
					if nPar >= 3:
						p3HistChi2Down.Fill(p3, not varCheck)
					if nPar >= 4:
						p4HistChi2Down.Fill(p4, not varCheck)
					chi2HistChi2Down.Fill(chi2, not varCheck)
					eitHistChi2Down.Fill(toyExp, not varCheck)

				#pae += "\n {} {} {} {} {}".format(sigPars, region, expSig, nTotal, nPass)
				c1 = rt.TCanvas("c1","c1",1500,1500)
				c1.Divide(3,3)

				if nPar < 4:
					doLeg = True
					iPlot1 = 7
					iPlot2 = 8
					iPlot3 = 9
				else:
					doLeg = False
					iPlot1 = 6
					iPlot2 = 7
					iPlot3 = 8
					iPlot4 = 9
				c1.cd(1)
				rHist.Draw("hist")
				rHistChi2Up.Draw("hist same")
				rHistChi2Down.Draw("hist same")
				c1.cd(2)
				rErrHist.Draw("hist")
				rErrHistChi2Up.Draw("hist same")
				rErrHistChi2Down.Draw("hist same")
				c1.cd(3)
				rmuHist.Draw("hist")
				rmuHistChi2Up.Draw("hist same")
				rmuHistChi2Down.Draw("hist same")
				c1.cd(4)
				eitHist.Draw("hist")
				eitHistChi2Up.Draw("hist same")
				eitHistChi2Down.Draw("hist same")
				c1.cd(iPlot1)
				p1Hist.Draw("hist")
				p1HistChi2Up.Draw("hist same")
				p1HistChi2Down.Draw("hist same")
				if nPar >= 2:
					c1.cd(iPlot2)
					p2Hist.Draw("hist")
					p2HistChi2Up.Draw("hist same")
					p2HistChi2Down.Draw("hist same")
				if nPar >= 3:
					c1.cd(iPlot3)
					p3Hist.Draw("hist")
					p3HistChi2Up.Draw("hist same")
					p3HistChi2Down.Draw("hist same")
				if nPar >= 4:
					c1.cd(iPlot4)
					p4Hist.Draw("hist")
					p4HistChi2Up.Draw("hist same")
					p4HistChi2Down.Draw("hist same")
				
				c1.cd(5)
				chi2Hist.Draw("hist")
				chi2HistChi2Up.Draw("hist same")
				chi2HistChi2Down.Draw("hist same")
				chi2Func_test = rt.TF1("chi2Func","ROOT::Math::chisquared_pdf(x,{},0)".format(ndf),chi2LimitDown,chi2LimitUp)
				chi2Norm = chi2Hist.GetBinContent(chi2Hist.GetMaximumBin())/chi2Func_test.GetMaximum()
				#chi2Func = rt.TF1("chi2Func","{}*({}/{}) * ROOT::Math::chisquared_pdf(x,{},0)".format(50,10,nBins,ndf,ndf),chi2LimitDown,chi2LimitUp)
				chi2Func = rt.TF1("chi2Func","{}*ROOT::Math::chisquared_pdf(x,{},0)".format(chi2Norm,ndf),chi2LimitDown,chi2LimitUp)
				chi2Func.SetLineColor(rt.kGreen)
				chi2Func.Draw("same")
				if doLeg:
					c1.cd(6)
					leg = rt.TLegend(0.0,0.0,1.0,1.0)
					chi2Func.Draw("axis")
					leg.SetHeader("Legend","C")
					leg.AddEntry(rHist,"All Events","l")
					leg.AddEntry(rHistChi2Up,"Low #chi^2 Events","l")
					leg.AddEntry(rHistChi2Down,"High #chi^2 Events","l")
					leg.AddEntry(chi2Func, "Ideal #chi^2 Distribtuion","l")
					leg.Draw()
				#c1.SaveAs("../condorTests/chi2Dist/"+SVJNAME+"_"+region+expSig+".png")
				c1.SaveAs("../FourStepBias_jul21/plots/"+SVJNAME+"_"+bigName+".png")
				
				c2 = rt.TCanvas("c2","c2",1500,1500)
				rmuHist.Draw("hist")
				if rmuHist.GetEntries() > 0:
					rmuHist.Fit("gaus",'','PLC',-5,5)
					rmuHist.GetFunction("gaus").SetLineColor(rt.kBlue-5)
					rmuHist.GetFunction("gaus").SetLineWidth(8)
					pae2 += "{} {} {} {} {}\n".format(region, expSig, rmuHist.GetFunction("gaus").GetParameter(0),rmuHist.GetFunction("gaus").GetParameter(1),rmuHist.GetFunction("gaus").GetParameter(2) )
				rmuHist.Draw("func same")
				rmuHistChi2Up.Draw("hist same")
				rmuHistChi2Down.Draw("hist same")
				c2.SaveAs("../FourStepBias_jul21/plots/"+SVJNAME+"_"+bigName+"_pullOnly.png")

				fitDiagFile.Close()
				fitOnlyFile.Close()
				#dataObsFile.Close()






print(pae) 
print(pae2)


















