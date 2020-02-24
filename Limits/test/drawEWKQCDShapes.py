
import ROOT as rt
rt.gStyle.SetOptStat(0)

rootInput = rt.TFile.Open("datacard.root","read")

endResult = "Region Group Chi2 ndf norm lin log" + "\n"

for region in ["lowCut","lowSVJ2","highCut","highSVJ2"]:
	if "SVJ2" in region:
		mtCut = 3800
		ndf = 20
	else:
		mtCut = 6000
		ndf = 42
	
	qcdHist = rootInput.Get(region+"_2018/QCD")
	ttjHist = rootInput.Get(region+"_2018/TT")
	wjeHist = rootInput.Get(region+"_2018/WJets")
	zjeHist = rootInput.Get(region+"_2018/ZJets")
	for iBin in range(qcdHist.GetNbinsX()+1): # .FillRandom doesn't like negative bin values in reference histo
		if qcdHist.GetBinContent(iBin) < 0:   # smallest value is about -0.02 in some TTJ histos
			qcdHist.SetBinContent(iBin,0)
		if ttjHist.GetBinContent(iBin) < 0:
			ttjHist.SetBinContent(iBin,0)
		if wjeHist.GetBinContent(iBin) < 0:
			wjeHist.SetBinContent(iBin,0)
		if zjeHist.GetBinContent(iBin) < 0:
			zjeHist.SetBinContent(iBin,0)

	qcdToy = qcdHist.Clone("qcdToy")
	ttjToy = ttjHist.Clone("ttjToy")
	wjeToy = wjeHist.Clone("wjeToy")
	zjeToy = zjeHist.Clone("zjeToy")

	for iBin in range(qcdToy.GetNbinsX()+1): # Clone also saves bin data, set everything to 0
		qcdToy.SetBinContent(iBin,0)		# because chi^2 fit ignores bins with zero value AND zero error
		ttjToy.SetBinContent(iBin,0)
		wjeToy.SetBinContent(iBin,0)
		zjeToy.SetBinContent(iBin,0)
		qcdToy.SetBinError(iBin,0)
		ttjToy.SetBinError(iBin,0)
		wjeToy.SetBinError(iBin,0)
		zjeToy.SetBinError(iBin,0)

	qcdToy.FillRandom(qcdHist,int(qcdHist.Integral()))
	ttjToy.FillRandom(ttjHist,int(ttjHist.Integral()))
	wjeToy.FillRandom(wjeHist,int(wjeHist.Integral()))
	zjeToy.FillRandom(zjeHist,int(zjeHist.Integral()))


	#Q, T, QT, WZ, TWZ
	func_q = rt.TF1("fit_q","[2]*pow(1-x/13000,[0]+[1]*log(x/13000))",1500,mtCut)
	#func_q.SetParameter(0,10)
	#func_q.SetParLimits(0,0,100)
	#func_q.SetParameter(1,10)
	#func_q.SetParLimits(1,-100,100)
	#func_q.SetParameter(2,10000)
	#func_q.SetParLimits(2,0,10000)
	func_t = rt.TF1("fit_t","[2]*pow(1-x/13000,[0]+[1]*log(x/13000))",1500,mtCut)
	#func_t.SetParameter(0,10)
	#func_t.SetParLimits(0,0,100)
	#func_t.SetParameter(1,10)
	#func_t.SetParLimits(1,-100,100)
	#func_t.SetParameter(2,10)
	#func_t.SetParLimits(2,0,10000)
	func_qt = rt.TF1("fit_wt","[2]*pow(1-x/13000,[0]+[1]*log(x/13000))",1500,mtCut)
	#func_qt.SetParameter(0,10)
	#func_qt.SetParLimits(0,0,100)
	#func_qt.SetParameter(1,10)
	#func_qt.SetParLimits(1,-100,100)
	#func_qt.SetParameter(2,10)
	#func_qt.SetParLimits(2,0,10000)
	func_twz = rt.TF1("fit_twz","[2]*pow(1-x/13000,[0]+[1]*log(x/13000))",1500,mtCut)
	#func_twz.SetParameter(0,10)
	#func_twz.SetParLimits(0,0,100)
	#func_twz.SetParameter(1,10)
	#func_twz.SetParLimits(1,-100,100)
	#func_twz.SetParameter(2,10)
	#func_twz.SetParLimits(2,0,10000)
	func_wz = rt.TF1("fit_wz","[2]*pow(1-x/13000,[0]+[1]*log(x/13000))",1500,mtCut)
	#func_wz.SetParameter(0,10)
	#func_wz.SetParLimits(0,0,100)
	#func_wz.SetParameter(1,10)
	#func_wz.SetParLimits(1,-100,100)
	#func_wz.SetParameter(2,10)
	#func_wz.SetParLimits(2,0,10000)

	hist_q = qcdToy.Clone("hist_q")
	func_q.SetLineColor(hist_q.GetLineColor())
	hist_q.SetTitle("QCD {:.0f}".format(hist_q.Integral()))
	hist_q.Scale(1/hist_q.Integral())
	hist_q.Fit(func_q,"QR")

	hist_t = ttjToy.Clone("hist_t")
	func_t.SetLineColor(hist_t.GetLineColor())
	hist_t.SetTitle("TT {:.0f}".format(hist_t.Integral()))
	hist_t.Scale(1/hist_t.Integral())
	hist_t.Fit(func_t,"QR")

	hist_qt = qcdToy.Clone("hist_qt")
	func_qt.SetLineColor(hist_qt.GetLineColor())
	hist_qt.Add(ttjToy)
	hist_qt.SetTitle("QCD+TT {:.0f}".format(hist_qt.Integral()))
	hist_qt.Scale(1/hist_qt.Integral())
	hist_qt.Fit(func_qt,"QR")

	hist_twz = ttjToy.Clone("hist_twz")
	func_twz.SetLineColor(hist_twz.GetLineColor())
	hist_twz.Add(wjeToy)
	hist_twz.Add(zjeToy)
	hist_twz.SetTitle("T+W+Z {:.0f}".format(hist_twz.Integral()))
	hist_twz.Scale(1/hist_twz.Integral())
	hist_twz.Fit(func_twz,"QR")

	hist_wz = wjeToy.Clone("hist_wz")
	func_wz.SetLineColor(hist_wz.GetLineColor())
	hist_wz.Add(zjeToy)
	hist_wz.SetTitle("W+Z {:.0f}".format(hist_wz.Integral()))
	hist_wz.Scale(1/hist_wz.Integral())
	hist_wz.Fit(func_wz,"QR")

	endResult += region +"\tQ\t{:.2f}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(func_q.GetChisquare(),ndf,func_q.GetParameter(2),func_q.GetParameter(0),func_q.GetParameter(1)) + "\n"
	endResult += region +"\tT\t{:.2f}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(func_t.GetChisquare(),ndf,func_t.GetParameter(2),func_t.GetParameter(0),func_t.GetParameter(1)) + "\n"
	endResult += region +"\tQT\t{:.2f}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(func_qt.GetChisquare(),ndf,func_qt.GetParameter(2),func_qt.GetParameter(0),func_qt.GetParameter(1)) + "\n"
	endResult += region +"\tTWZ\t{:.2f}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(func_twz.GetChisquare(),ndf,func_twz.GetParameter(2),func_twz.GetParameter(0),func_twz.GetParameter(1)) + "\n"
	endResult += region +"\tWZ\t{:.2f}\t{}\t{:.2f}\t{:.2f}\t{:.2f}".format(func_wz.GetChisquare(),ndf,func_wz.GetParameter(2),func_wz.GetParameter(0),func_wz.GetParameter(1)) + "\n"

	c1 = rt.TCanvas("c1","c1",1000,1000)
	c1.SetLogy()
	hist_q.Draw()
	hist_t.Draw("same")
	hist_wz.Draw("same")
	c1.BuildLegend()
	c1.SaveAs("ewkqcd/q_t_wz_"+region+".png")

	hist_qt.Draw()
	hist_wz.Draw("same")
	c1.BuildLegend()
	c1.SaveAs("ewkqcd/qt_wz_"+region+".png")


	hist_q.Draw()
	hist_twz.Draw("same")
	c1.BuildLegend()
	c1.SaveAs("ewkqcd/q_twz_"+region+".png")

print(endResult)
