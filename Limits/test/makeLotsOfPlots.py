import ROOT as rt
import random
rt.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
rt.gStyle.SetOptStat(111111)
rt.gStyle.SetOptFit(1011)

# runover each SR to fit all 100 toys to the main function

regions = ["lowCut","lowSVJ1","lowSVJ2","highCut","highSVJ1","highSVJ2"]
#regions = ["lowSVJ1","lowSVJ2","highSVJ1","highSVJ2"]
#regions = ["lowSVJ2"]


for region in regions:
	for toyFunc in ["Main","Alt"]:
		for sigStr in ["Sig0"]:
			for fitFunc in ["Main"]:
				halfName = toyFunc+sigStr
				fullName = toyFunc+sigStr+fitFunc
				n = sigStr[3]
				fitDiagFile = rt.TFile.Open("cards_Feb12_3params/SVJ_mZprime3000_mDark20_rinv03_alphapeak/"+region+"/fitDiagnostics"+fullName+".root","read")
				fitOnlyFile = rt.TFile.Open("cards_Feb12_3params/SVJ_mZprime3000_mDark20_rinv03_alphapeak/"+region+"/higgsCombine"+fullName+".FitDiagnostics.mH120.123456.root","read")
				genOnlyFile = rt.TFile.Open("cards_Feb12_3params/SVJ_mZprime3000_mDark20_rinv03_alphapeak/"+region+"/higgsCombine"+halfName+".GenerateOnly.mH125.123456.root","read")
				dataObsFile = rt.TFile.Open("cards_Feb12_3params/SVJ_mZprime3000_mDark20_rinv03_alphapeak/ws_SVJ_mZprime3000_mDark20_rinv03_alphapeak_"+region+"_2018_template.root","read")
				svjWs = dataObsFile.Get("SVJ")
				data = rt.RooDataHist()
				data = svjWs.data("data_obs")
				if toyFunc == "Main":
					genPdf = svjWs.pdf("Bkg_"+region+"_2018")
				else:
					genPdf = svjWs.pdf("Bkg_Alt_"+region+"_2018")
				tree = fitDiagFile.Get("tree_fit_sb")
				limit = fitOnlyFile.Get("limit")
				
				chi2Div = 1.55
				#if region == "highSVJ1" and toyFunc == "Alt":
				#	chi2Div = -10
				#if region == "highSVJ2" and toyFunc == "Main":
				#	chi2Div = -2
				#if region == "lowSVJ1" and toyFunc == "Main":
				#	chi2Div = -2

				downLimitRMU = -10
				if (region == "lowSVJ1" or region=="lowCut") and toyFunc == "Alt":
					downLimitRMU = -40
				if region == "highSVJ1" and toyFunc == "Alt":
					downLimitRMU = -30

				if toyFunc == "Alt":
					upLimitrErr = 0.6
				if (toyFunc == "Main" and "SVJ2" in region):
					upLimitrErr = 1.0
				elif toyFunc == "Main":
					upLimitrErr = 10

				downLimitrErr = 0
				if region == "highSVJ2" and toyFunc == "Alt":
					downLimitrErr = 0.54
				
				nBins = 50
				rHist = rt.TH1F("rHist","r, all Events",nBins,-10,10)
				rHistChi2Up = rt.TH1F("rHistChi2Up","r, chi2 > {}".format(chi2Div),nBins,-10,10)
				rHistChi2Down = rt.TH1F("rHistChi2Down","r, chi2 < {}".format(chi2Div),nBins,-10,10)
				rErrHist = rt.TH1F("rErrHist","rErr, all Events",nBins,downLimitrErr,upLimitrErr)
				rErrHistChi2Up = rt.TH1F("rErrHistChi2Up","rErr, chi2 > {}".format(chi2Div),nBins,downLimitrErr,upLimitrErr)
				rErrHistChi2Down = rt.TH1F("rErrHistChi2Down","rErr, chi2 < {}".format(chi2Div),nBins,downLimitrErr,upLimitrErr)
				rmuHist = rt.TH1F("rmuHist","(r-mu)/rErr, all Events",nBins,downLimitRMU,10)
				rmuHistChi2Up = rt.TH1F("rmuHistChi2Up","(r-mu)/rErr, chi2 > {}".format(chi2Div),nBins,downLimitRMU,10)
				rmuHistChi2Down = rt.TH1F("rmuHistChi2Down","(r-mu)/rErr, chi2 < {}".format(chi2Div),nBins,downLimitRMU,10)
				#limitHist = rt.TH1F("limitHist","limit, all events",nBins,-4,4)
				#limitHistChi2Up = rt.TH1F("limitHistChi2Up","limit, chi2 > {}".format(chi2Div),nBins,-4,4)
				#limitHistChi2Down = rt.TH1F("limitHistChi2Down","limit, chi2 < {}".format(chi2Div),nBins,-4,4)
				#limitErrHist = rt.TH1F("limitErrHist","limitErr, all events",nBins,0,8)
				#limitErrHistChi2Up = rt.TH1F("limitErrHistChi2Up","limitErr, chi2 > {}".format(chi2Div),nBins,0,8)
				#limitErrHistChi2Down = rt.TH1F("limitErrHistChi2Down","limitErr, chi2 < {}".format(chi2Div),nBins,0,8)
				#limitmuHist = rt.TH1F("limitmuHist","(limit-mu)/limitErr, all Events",nBins,-10,10)
				#limitmuHistChi2Up = rt.TH1F("limitmuHistChi2Up","(limit-mu)/limitErr, chi2 > {}".format(chi2Div),nBins,-10,10)
				#limitmuHistChi2Down = rt.TH1F("limitmuHistChi2Down","(limit-mu)/limitErr, chi2 < {}".format(chi2Div),nBins,-10,10)
				p1Hist = rt.TH1F("p1Hist","p1, all events", nBins,-100,100)
				p1HistChi2Up = rt.TH1F("p1HistChi2Up","p1, chi2 > {}".format(chi2Div), nBins,-100,100)
				p1HistChi2Down = rt.TH1F("p1HistChi2Down","p1, chi2 < {}".format(chi2Div), nBins,-100,100)
				p2Hist = rt.TH1F("p2Hist","p2, all events", nBins,-500,500)
				p2HistChi2Up = rt.TH1F("p2HistChi2Up","p2, chi2 > {}".format(chi2Div), nBins,-500,500)
				p2HistChi2Down = rt.TH1F("p2HistChi2Down","p2, chi2 < {}".format(chi2Div), nBins,-500,500)
				chi2Hist = rt.TH1F("chi2Hist","chi2, all events", nBins, 0, 10)
				chi2HistChi2Up = rt.TH1F("chi2HistChi2Up","chi2, chi2 > {}".format(chi2Div), nBins, 0, 10)
				chi2HistChi2Down = rt.TH1F("chi2HistChi2Down","chi2, chi2 < {}".format(chi2Div), nBins, 0, 10)

				rHist.SetLineColor(rt.kBlack)
				rHistChi2Up.SetLineColor(rt.kBlue)
				rHistChi2Down.SetLineColor(rt.kRed)
				rErrHist.SetLineColor(rt.kBlack)
				rErrHistChi2Up.SetLineColor(rt.kBlue)
				rErrHistChi2Down.SetLineColor(rt.kRed)
				rmuHist.SetLineColor(rt.kBlack)
				rmuHistChi2Up.SetLineColor(rt.kBlue)
				rmuHistChi2Down.SetLineColor(rt.kRed)
				#limitHist.SetLineColor(rt.kBlack)
				#limitHistChi2Up.SetLineColor(rt.kBlue)
				#limitHistChi2Down.SetLineColor(rt.kRed)
				#limitErrHist.SetLineColor(rt.kBlack)
				#limitErrHistChi2Up.SetLineColor(rt.kBlue)
				#limitErrHistChi2Down.SetLineColor(rt.kRed)
				#limitmuHist.SetLineColor(rt.kBlack)
				#limitmuHistChi2Up.SetLineColor(rt.kBlue)
				#limitmuHistChi2Down.SetLineColor(rt.kRed)
				p1Hist.SetLineColor(rt.kBlack)
				p1HistChi2Up.SetLineColor(rt.kBlue)
				p1HistChi2Down.SetLineColor(rt.kRed)
				p2Hist.SetLineColor(rt.kBlack)
				p2HistChi2Up.SetLineColor(rt.kBlue)
				p2HistChi2Down.SetLineColor(rt.kRed)
				chi2Hist.SetLineColor(rt.kBlack)
				chi2HistChi2Up.SetLineColor(rt.kBlue)
				chi2HistChi2Down.SetLineColor(rt.kRed)

				rHist.SetLineWidth(2)
				rHistChi2Up.SetLineWidth(2)
				rHistChi2Down.SetLineWidth(2)
				rErrHist.SetLineWidth(2)
				rErrHistChi2Up.SetLineWidth(2)
				rErrHistChi2Down.SetLineWidth(2)
				rmuHist.SetLineWidth(2)
				rmuHistChi2Up.SetLineWidth(2)
				rmuHistChi2Down.SetLineWidth(2)
				#limitHist.SetLineWidth(2)
				#limitHistChi2Up.SetLineWidth(2)
				#limitHistChi2Down.SetLineWidth(2)
				#limitErrHist.SetLineWidth(2)
				#limitErrHistChi2Up.SetLineWidth(2)
				#limitErrHistChi2Down.SetLineWidth(2)
				#limitmuHist.SetLineWidth(2)
				#limitmuHistChi2Up.SetLineWidth(2)
				#limitmuHistChi2Down.SetLineWidth(2)
				p1Hist.SetLineWidth(2)
				p1HistChi2Up.SetLineWidth(2)
				p1HistChi2Down.SetLineWidth(2)
				p2Hist.SetLineWidth(2)
				p2HistChi2Up.SetLineWidth(2)
				p2HistChi2Down.SetLineWidth(2)
				chi2Hist.SetLineWidth(2)
				chi2HistChi2Up.SetLineWidth(2)
				chi2HistChi2Down.SetLineWidth(2)

				hist2D_chi2_rmu = rt.TH2F("hist2D_chi2_rmu","Chi2VsRMuErr;chi2;rmuerr",nBins, 0, 10, nBins, downLimitRMU,10)
				
				
				
				listOfFuncs = []
				for iEvt in range(limit.GetEntries()):
					limit.GetEvent(iEvt)
					if limit.quantileExpected != -1:
						continue
					tree.GetEvent(limit.iToy)
					toy = genOnlyFile.Get("toys/toy_{}".format(limit.iToy))
					toyExp = getattr(tree,"n_exp_final_bin"+region+"_2018_proc_roomultipdf")

					rHistVal = tree.r
					rErrHistVal = tree.rErr
					rmuHistVal = (tree.r-int(n))/tree.rErr
				#	limitHistVal = limit.limit
				#	limitErrHistVal = limit.limitErr
				#	limitmuHistVal = (limit.limit-int(n))/limit.limitErr
					norm = 1
					#if region != "highSVJ2":
					p1 = getattr(limit,"trackedParam_"+region+"_p1_3")
					p2 = getattr(limit,"trackedParam_"+region+"_p2_3")
					p3 = getattr(limit,"trackedParam_"+region+"_p3_3")
					#p4 = getattr(limit,"trackedParam_"+region+"_p4_4")
					#copyToExcel += "{} {} {} {} {}\n".format(region, toyFunc, sigStr, p1, p2)
					#listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[2]*pow(1 - x/13000, [0]+[1]*log(x/13000)) * pow(x/13000,-[3]-[4]*log(x/13000))",1500,3800))
					listOfFuncs.append(rt.TF1("iToy_"+str(iEvt),"[2]*pow(1 - x/13000, [0]+[1]*log(x/13000)) * pow(x/13000,-[3])",1500,3800))
					listOfFuncs[-1].SetParameter(0,p1)
					listOfFuncs[-1].SetParameter(1,p2)
					listOfFuncs[-1].SetParameter(2,norm)
					listOfFuncs[-1].SetParameter(3,p3)
					#listOfFuncs[-1].SetParameter(4,p4)
					# pdf's in RooFit do not have a normlization facotr (i.e., Sum(allspace) of pdf = 1)
					# so we need to scale it to our dataset.
					# first (above line), set norm to 1, and we know the number of events in the toy)
					# then scale the function by numEvents divided by intergral of function without a normialztion
					# i.e., first normalize to 1 (divide by integral), then scale to numEvents
					# factor of 100 is becaue our bins are 100 GeV wide
					listOfFuncs[-1].SetParameter(2,toyExp/listOfFuncs[-1].Integral(1500,3800)*100)
					chi2 = 0
					for iBin in range(toy.numEntries()):
						toy.get(iBin)
						x = toy.get(iBin).getRealValue("mH")
						Oi = toy.weight()
						Ei = listOfFuncs[-1].Eval(x)
						try:
							chi2 += ((Oi-Ei)**2)/Ei
						except ZeroDivisionError:
							chi2 += 0
					ndf = 20
					chi2Hist.Fill(chi2/ndf)
					#else:
					#	p1 = getattr(limit,"trackedParam_"+region+"_p1_1")
					#	p2 = -9
					#	listOfFuncs.append(rt.TF1("iToy_"+str(iEvt-1),"[1]*pow(1 - x/13000, [0])",1500,3800))
					#	listOfFuncs[-1].SetParameter(0,p1)
					#	listOfFuncs[-1].SetParameter(1,1)
					#	# pdf's in RooFit do not have a normlization facotr (i.e., Sum(allspace) of pdf = 1)
					#	# so we need to scale it to our dataset.
					#	# first (above line), set norm to 1, and we know the number of events in the toy)
					#	# then scale the function by numEvents divided by intergral of function without a normialztion
					#	# i.e., first normalize to 1 (divide by integral), then scale to numEvents
					#	# factor of 100 is becaue our bins are 100 GeV wide
					#	listOfFuncs[-1].SetParameter(1,toyExp/listOfFuncs[-1].Integral(1500,3800)*100)
					#	chi2 = 0
					#	for iBin in range(toy.numEntries()):
					#		toy.get(iBin)
					#		x = toy.get(iBin).getRealValue("mH")
					#		Oi = toy.weight()
					#		Ei = listOfFuncs[-1].Eval(x)
					#		chi2 += ((Oi-Ei)**2)/Ei
					#	ndf = 22
					#	chi2Hist.Fill(chi2/ndf)
					chi2Func = rt.TF1("chi2Func","{}*({}/{}) * ROOT::Math::chisquared_pdf(x,{},0)/{}".format(100,10,nBins,21,21),0,10)
					chi2Func.SetLineColor(rt.kGreen)

					rHist.Fill(rHistVal)
					rErrHist.Fill(rErrHistVal)
					rmuHist.Fill(rmuHistVal)
					#limitHist.Fill(limitHistVal)
					#limitErrHist.Fill(limitErrHistVal)
					#limitmuHist.Fill(limitmuHistVal)
					p1Hist.Fill(p1)
					p2Hist.Fill(p2)

					hist2D_chi2_rmu.Fill(chi2/ndf,rmuHistVal)

					varCheck = (chi2/ndf < chi2Div)
					#if region == "highSVJ1" and toyFunc == "Main":
					#	varCheck = (rHistVal > -3.2)

					rHistChi2Up.Fill(rHistVal, varCheck)
					rErrHistChi2Up.Fill(rErrHistVal, varCheck)
					rmuHistChi2Up.Fill(rmuHistVal, varCheck)
					#limitHistChi2Up.Fill(limitHistVal, varCheck)
					#limitErrHistChi2Up.Fill(limitErrHistVal, varCheck)
					#limitmuHistChi2Up.Fill(limitmuHistVal, varCheck)
					p1HistChi2Up.Fill(p1, varCheck)
					p2HistChi2Up.Fill(p2, varCheck)
					chi2HistChi2Up.Fill(chi2/ndf, varCheck)

					rHistChi2Down.Fill(rHistVal, not varCheck)
					rErrHistChi2Down.Fill(rErrHistVal, not varCheck)
					rmuHistChi2Down.Fill(rmuHistVal, not varCheck)
					#limitHistChi2Down.Fill(limitHistVal, not varCheck)
					#limitErrHistChi2Down.Fill(limitErrHistVal, not varCheck)
					#limitmuHistChi2Down.Fill(limitmuHistVal, not varCheck)
					p1HistChi2Down.Fill(p1, not varCheck)
					p2HistChi2Down.Fill(p2, not varCheck)
					chi2HistChi2Down.Fill(chi2/ndf, not varCheck)

				c1 = rt.TCanvas("c1","c1",2500,1000)
				c1.Divide(3,2)
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
				#c1.cd(6)
				#limitHist.Draw("hist")
				#limitHistChi2Up.Draw("hist same")
				#limitHistChi2Down.Draw("hist same")
				#c1.cd(7)
				#limitErrHist.Draw("hist")
				#limitErrHistChi2Up.Draw("hist same")
				#limitErrHistChi2Down.Draw("hist same")
				#c1.cd(8)
				#limitmuHist.Draw("hist")
				#limitmuHistChi2Up.Draw("hist same")
				#limitmuHistChi2Down.Draw("hist same")
				c1.cd(4)
				p1Hist.Draw("hist")
				p1HistChi2Up.Draw("hist same")
				p1HistChi2Down.Draw("hist same")
				c1.cd(5)
				p2Hist.Draw("hist")
				p2HistChi2Up.Draw("hist same")
				p2HistChi2Down.Draw("hist same")
				c1.cd(6)
				chi2Hist.Draw("hist")
				chi2HistChi2Up.Draw("hist same")
				chi2HistChi2Down.Draw("hist same")
				#chi2Func.Draw("same")
				c1.SaveAs("cards_Feb12_3params/SVJ_mZprime3000_mDark20_rinv03_alphapeak/plots/AA_"+region+"_"+fullName+"_10plots.png")
	
				c2 = rt.TCanvas("c2","c2",1000,1000)
				hist2D_chi2_rmu.Draw("colz")
				c2.SaveAs("cards_Feb12_3params/SVJ_mZprime3000_mDark20_rinv03_alphapeak/plots/BB_"+region+"_"+fullName+"_2dPlot.png")

				fitDiagFile.Close()
				genOnlyFile.Close()
				dataObsFile.Close()
























