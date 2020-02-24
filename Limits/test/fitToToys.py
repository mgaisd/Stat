import ROOT as rt
import random
rt.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
rt.gStyle.SetOptStat(111111)
rt.gStyle.SetOptFit(1011)

# runover each SR to fit all 100 toys to the main function

regions = ["lowCut"]#,"lowSVJ1","lowSVJ2","highCut","highSVJ1","highSVJ2"]
#regions = ["lowSVJ1","lowSVJ2","highSVJ1","highSVJ2"]
#regions = ["lowSVJ2"]

# Generate plots of fit_status, r, rErr, and (r-STR)/rErr for all, fit_status <300, and fit_status==0

copyToExcel = "Region & Toy & Sig & Fit & HistMean & HistStdDev & FitMean & FitStdDev\\\\\n"

for region in regions:
	for toyFunc in ["Main","Alt"]:
		for sigStr in ["Sig0"]:
			for fitFunc in ["Main"]:
				halfName = toyFunc+sigStr
				fullName = toyFunc+sigStr+fitFunc
				n = sigStr[3]
				fitDiagFile = rt.TFile.Open("cards_Feb21_Thry/SVJ_mZprime3000_mDark20_rinv03_alphapeak/"+region+"/fitDiagnostics"+fullName+".root","read")
				genOnlyFile = rt.TFile.Open("cards_Feb21_Thry/SVJ_mZprime3000_mDark20_rinv03_alphapeak/"+region+"/higgsCombine"+halfName+".GenerateOnly.mH125.123456.root","read")
				dataObsFile = rt.TFile.Open("cards_Feb21_Thry/SVJ_mZprime3000_mDark20_rinv03_alphapeak/ws_SVJ_mZprime3000_mDark20_rinv03_alphapeak_"+region+"_2018_template.root","read")
				svjWs = dataObsFile.Get("SVJ")
				data = rt.RooDataHist()
				data = svjWs.data("data_obs")
				fitPdf = svjWs.pdf("Bkg_"+region+"_2018")
				if float(fitDiagFile.GetSize()) < 20000:
					print("="*25)
					print("{} {} could not be drawn".format(region, fullName))
					print("="*25)
					continue
				tree = fitDiagFile.Get("tree_fit_sb")
				c1 = rt.TCanvas("c1","c1",1000,1000)
				c1.Divide(2,2)
				c1.cd(1)
				selection = "" #"fit_status==0||fit_status==1"
				tree.Draw("r>>h1(60,-10,10)",selection)
				rt.gDirectory.Get("h1").SetLineColor(rt.kBlack)
				rt.gDirectory.Get("h1").SetLineWidth(2)
				#tree.Draw("r>>h1p","r>0","same")
				#rt.gDirectory.Get("h1p").SetLineColor(rt.kRed)
				rt.gDirectory.Get("h1").SetAxisRange(0,rt.gDirectory.Get("h1").GetMaximum()*1.1,"Y")
				rt.gPad.Update()
				c1.cd(2)
				tree.Draw("rErr>>h2(100,0,10)",selection)
				rt.gDirectory.Get("h2").SetLineColor(rt.kBlack)
				rt.gDirectory.Get("h2").SetLineWidth(2)
				#tree.Draw("rErr>>h2p","r>0","same")
				#rt.gDirectory.Get("h2p").SetLineColor(rt.kRed)
				rt.gDirectory.Get("h2").SetAxisRange(0,rt.gDirectory.Get("h2").GetMaximum()*1.1,"Y")
				rt.gPad.Update()
				c1.cd(3)
				frame = rt.RooPlot(svjWs.var("mH"),1500.,3800.,23)
				#frame = rt.RooPlot(svjWs.var("mH"),1500.,6000.,45)
				frame.SetTitle("data, random toy, inital fit")
				rt.gPad.SetLogy()
				data.plotOn(frame, rt.RooFit.MarkerColor(rt.kBlack))
				fitPdf.plotOn(frame,rt.RooFit.LineColor(rt.kMagenta))
				toy = genOnlyFile.Get("toys/toy_{}".format(random.randint(1,100)))
				toy.plotOn(frame,rt.RooFit.MarkerColor(rt.kBlue))
				frame.SetAxisRange(0.001,50000,"Y")
				frame.Draw()
				c1.cd(4)
				tree.Draw("(r-"+n+")/rErr>>h3(100,-10,10)",selection)
				rt.gDirectory.Get("h3").SetLineColor(rt.kBlack)
				rt.gDirectory.Get("h3").SetLineWidth(2)
				#tree.Draw("(r-"+n+")/rErr>>h3p","r>0","same")
				#rt.gDirectory.Get("h3p").SetLineColor(rt.kRed)
				rt.gDirectory.Get("h3").SetAxisRange(0,rt.gDirectory.Get("h3").GetMaximum()*1.1,"Y")
				rt.gPad.Update()
				gaus = rt.TF1("gaus","gaus(0)", rt.gDirectory.Get("h3").GetMean()-2*rt.gDirectory.Get("h3").GetStdDev(), rt.gDirectory.Get("h3").GetMean()+2*rt.gDirectory.Get("h3").GetStdDev())
				rt.gDirectory.Get("h3").Fit("gaus","R")
				gaus.SetLineColor(rt.kBlue)
				gaus.Draw("same")
				copyToExcel += "{} & {} & {} & {} & {} & {} & {} & {} \\\\\n".format(region, toyFunc,sigStr,fitFunc,rt.gDirectory.Get("h3").GetMean(),rt.gDirectory.Get("h3").GetStdDev(),gaus.GetParameter(1),gaus.GetParameter(2))
				c1.cd(0)
				title = rt.TPaveText(0.3,0.5,0.7,0.53)
				title.AddText("{} {}".format(region, fullName))
				title.Draw()
				c1.SaveAs("cards_Feb21_Thry/SVJ_mZprime3000_mDark20_rinv03_alphapeak/plots/"+region+"_fit_status_"+fullName+"_plots.png")
				c2 = rt.TCanvas("c2","c2",1000,1000)
				#frame2 = rt.RooPlot(svjWs.var("mH"),1500.,6000.,45)
				frame2 = rt.RooPlot(svjWs.var("mH"),1500.,3800.,23)
				for iToy in range(1,101):
					genOnlyFile.Get("toys/toy_{}".format(iToy)).plotOn(frame2,rt.RooFit.LineColor(rt.kMagenta),rt.RooFit.MarkerColor(rt.kMagenta))
				data.plotOn(frame2, rt.RooFit.MarkerColor(rt.kBlack))
				frame2.Draw()
				c2.SaveAs("cards_Feb21_Thry/SVJ_mZprime3000_mDark20_rinv03_alphapeak/plots/"+region+"_AllToys_"+fullName+".png")

				fitDiagFile.Close()
				genOnlyFile.Close()
				dataObsFile.Close()
print(copyToExcel)
























