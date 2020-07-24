import ROOT as rt
rt.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
rt.gStyle.SetOptStat(0)
rt.gStyle.SetOptFit(1011)

# runover each SR to fit all 100 toys to the main function
eosArea = "root://cmsxrootd.fnal.gov//store/user/cfallon/biasStudies/"

listOfParams = [
['3000', '20', '03', 'peak']]
"""
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
['2900', '20', '03', 'peak'],
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
['3000', '1', '03', 'peak'],
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
['3000', '20', '06', 'peak'],
['3000', '20', '07', 'peak'],
['3000', '20', '08', 'peak'],
['3000', '20', '09', 'peak'],
['3000', '20', '1', 'peak'],
['3000', '20', '03', 'low'],
['3000', '20', '03', 'high']
]"""
#regions = ["lowSVJ2","highSVJ2"]
regions = ["lowCut","lowSVJ2","highCut","highSVJ2"]
#old pattern
#expSig = "_expSig1"# "", "_expSig1", "_expSig0_extra", or "_expSig1_extra"
#newpattern
expSig = "Sig0" # Sig0 or Sig1
funcs = "GenMainFitMain" # GenAltFitMain or GenMainFitMain

#setup four TGraphErrors, one for each varying-variable
vZ_m = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyZ_mean"}
vZ_s = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyZ_stdev"}
vD_m = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyD_mean"}
vD_s = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyD_stdev"}
vR_m = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyR_mean"}
vR_s = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyR_stdev"}
vA_m = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyA_mean"}
vA_s = {"lowCut":[[],[],[]],"lowSVJ2":[[],[],[]],"highCut":[[],[],[]],"highSVJ2":[[],[],[]], "name":"varyA_stdev"}

pae = "mz md ri ad region chi2 ndf\n"

pae2 = "mz md ri ad region nToysSuccessful\n"

for sigPars in listOfParams:
	SVJNAME = "SVJ_mZprime{}_mDark{}_rinv{}_alpha{}".format(sigPars[0],sigPars[1],sigPars[2],sigPars[3])
	print("************************",SVJNAME,"************************")
	#(re)set varyBools to all be false
	varyZ = False
	varyD = False
	varyR = False
	varyA = False
	zMass = int(sigPars[0])
	dMass = int(sigPars[1])
	rInvs = 1 if sigPars[2] == "1" else int(sigPars[2])*0.1
	if sigPars[3] == "peak":
		aDark = 1
	elif sigPars[3] == "low":
		aDark = 0.5
	elif sigPars[3] == "high":
		aDark = 1.5
	# baseline signal should be in every plot
	if [sigPars[0],sigPars[1],sigPars[2],sigPars[3]] == ['3000', '20', '03', 'peak']:
		varyZ = True
		varyD = True
		varyR = True
		varyA = True
	else: # if one parameter doesn't match baseline, then we're varying that parameter
		if sigPars[0] != "3000":
			varyZ = True
		if sigPars[1] != "20":
			varyD = True
		if sigPars[2] != "03":
			varyR = True
		if sigPars[3] != "peak":
			varyA = True
	for region in regions:
		print("************************",region, "************************")
                                           # new pattern: fitDiagnosticshighCutSig1GenMainFitMain.root
		fitDiagFile = rt.TFile.Open(eosArea + SVJNAME + "/fitDiagnostics"+region+expSig+funcs+".root","read")
		if type(fitDiagFile) == type(rt.TFile()):
			continue
		print(type(fitDiagFile))
		if float(fitDiagFile.GetSize()) < 20000:
			print("="*25)
			print("{} could not be drawn".format(region))
			print("="*25)
			continue
		tree = fitDiagFile.Get("tree_fit_sb")
		c1 = rt.TCanvas("c1","c1",1000,1000)
		selection = "fit_status==0" 
		injSig = int(expSig[-1:])
		print("INJSIG CHECK ************ ", str(injSig))
		tree.Draw("(r-{})/rErr>>h3(50,-5,5)".format(injSig),selection)
		pae2 += "{} {} {} {} {} {}\n".format(zMass, dMass, rInvs, aDark, region, rt.gDirectory.Get("h3").GetEntries())
		rt.gDirectory.Get("h3").SetLineColor(rt.kBlack)
		rt.gDirectory.Get("h3").SetLineWidth(2)
		rt.gDirectory.Get("h3").SetAxisRange(0,rt.gDirectory.Get("h3").GetMaximum()*1.1,"Y")
		rt.gPad.Update()
		gaus = rt.TF1("gaus","gaus(0)", -5, 5)
		#gaus = rt.TF1("gaus","gaus(0)", rt.gDirectory.Get("h3").GetMean()-2*rt.gDirectory.Get("h3").GetStdDev(), rt.gDirectory.Get("h3").GetMean()+2*rt.gDirectory.Get("h3").GetStdDev())
		rt.gDirectory.Get("h3").Fit("gaus","R")
		gaus.SetLineColor(rt.kBlue)
		gaus.Draw("same")
		c1.SaveAs("~/nobackup/SVJ/biasStudies2/CMSSW_10_2_13/src/Stat/Limits/test/condorTests/"+SVJNAME+"_"+region+expSig+funcs+".png")
		if gaus.GetNDF() == 0:
			pae += "{} {} {} {} {} {} {}\n".format(zMass, dMass, rInvs, aDark, region, gaus.GetChisquare(), gaus.GetNDF())
			continue
		#if rt.Math.chisquared_cdf_c(gaus.GetChisquare(), gaus.GetNDF()) < 0.05: # rightTail value is small means chi^2 is large.
		#	pae += "{} {} {} {} {} {} {} {}\n".format(zMass, dMass, rInvs, aDark, region, gaus.GetChisquare(), gaus.GetNDF(), rt.Math.chisquared_cdf_c(gaus.GetChisquare(), gaus.GetNDF()))
		#	continue
		if varyZ:
			vZ_m[region][0].append(zMass)
			vZ_m[region][1].append(gaus.GetParameter(1))
			vZ_m[region][2].append(gaus.GetParError(1))
			vZ_s[region][0].append(zMass)
			vZ_s[region][1].append(gaus.GetParameter(2))
			vZ_s[region][2].append(gaus.GetParError(2))
		if varyD:
			vD_m[region][0].append(dMass)
			vD_m[region][1].append(gaus.GetParameter(1))
			vD_m[region][2].append(gaus.GetParError(1))
			vD_s[region][0].append(dMass)
			vD_s[region][1].append(gaus.GetParameter(2))
			vD_s[region][2].append(gaus.GetParError(2))
		if varyR:
			vR_m[region][0].append(rInvs)
			vR_m[region][1].append(gaus.GetParameter(1))
			vR_m[region][2].append(gaus.GetParError(1))
			vR_s[region][0].append(rInvs)
			vR_s[region][1].append(gaus.GetParameter(2))
			vR_s[region][2].append(gaus.GetParError(2))
		if varyA:
			vR_m[region][0].append(aDark)
			vR_m[region][1].append(gaus.GetParameter(1))
			vR_m[region][2].append(gaus.GetParError(1))
			vR_s[region][0].append(aDark)
			vR_s[region][1].append(gaus.GetParameter(2))
			vR_s[region][2].append(gaus.GetParError(2))
			

		fitDiagFile.Close()
print(pae)
print(pae2)
for region in regions:
	for vec in [vZ_m, vD_m, vR_m, vA_m, vZ_s, vD_s, vR_s, vA_s]:
		out = open("../condorTests/tge/"+vec["name"]+"_"+region+expSig+funcs+".txt","w")
		for i in range(len(vec[region][0])):
			out.write("{} {} {}\n".format(vec[region][0][i], vec[region][1][i], vec[region][2][i]))
		out.close()













