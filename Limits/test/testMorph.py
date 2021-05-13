from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from paramUtils import fprint, getParamNames, paramVal, makeSigDict, getSigname

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-s","--signal", dest="signal", metavar=tuple(getParamNames()), type=str, default=[], nargs=4, help="signal parameters")
parser.add_argument("-p","--param", dest="param", metavar=("paramName","value0","value1"), type=str, default=[], nargs=3, help="parameter and values for interpolation")
parser.add_argument("-m","--method", dest="method", type=str, default="none", choices=["none","integral","moment"], help="interpolation method")
parser.add_argument("-d","--dir", dest="dir", type=str, default="root://cmseos.fnal.gov//store/user/pedrok/SVJ2017/Limits/datacards_Mar29", help="datacard directory")
parser.add_argument("-r","--region", dest="region", type=str, required=True, help="signal region")
parser.add_argument("-u","--unc", dest="unc", type=str, default="", help="systematic uncertainty")
parser.add_argument("-y","--actualyield", dest="actualyield", default=False, action="store_true", help="use actual rather than interpolated yield, if available")
args = parser.parse_args()

import ROOT as r

sigdicts = [makeSigDict(args.signal),makeSigDict(args.signal),makeSigDict(args.signal)]
sigdicts[0][args.param[0]] = args.param[1]
sigdicts[1][args.param[0]] = args.param[2]

signals = [getSigname(sig) for sig in sigdicts]
yields = []
pdfs = []
for i in range(len(signals)):
    file = r.TFile.Open("{0}/{1}/ws_{1}_{2}_2018_template.root".format(args.dir,signals[i],args.region))
    signals[i] += ("_"+args.unc if len(args.unc)>0 else "")
    if file==None:
        pdfs.append(None)
        continue
    ws = file.Get("SVJ")
    sig = signals[i]
    hist = ws.data(sig)
    mT = ws.var("mH{}_2018".format(args.region))
    pdfs.append(r.RooHistPdf(sig,sig,r.RooArgSet(mT),hist))
    yields.append(hist.sum(0))

pval = paramVal(args.param[0],sigdicts[2][args.param[0]])
pmin = paramVal(args.param[0],sigdicts[0][args.param[0]])
pmax = paramVal(args.param[0],sigdicts[1][args.param[0]])

pvar = r.RooRealVar(args.param[0],args.param[0],pval,pmin,pmax)

if args.method=="none":
    interp = pdfs[2]
elif args.method=="integral":
    interp = r.RooIntegralMorph(signals[2],signals[2],pdfs[0],pdfs[1],mT,pvar)
elif args.method=="moment":
    pvec = r.TVectorD(2)
    pvec[0] = pmin
    pvec[1] = pmax
    interp = r.RooMomentMorph(signals[2],signals[2],pvar,r.RooArgList(mT),r.RooArgList(pdfs[0],pdfs[1]),pvec)

oname = "{}_{}".format(signals[2],args.method)
h_result = interp.createHistogram(oname, mT)

# interpolate yield
x_interp = r.std.vector(r.Double)()
x_interp += [pmin,pmax]
y_interp = r.std.vector(r.Double)()
y_interp += yields[:2]
interp = r.Math.Interpolator(x_interp,y_interp,r.Math.Interpolation.kLINEAR)
yieldnorm = interp.Eval(pval)
if args.actualyield:
    if len(yields)>2: yieldnorm = yields[2]
    else: fprint("Warning: actual yield requested, but not available; using interpolated yield")

# fix errors
h_result.Scale(yieldnorm/h_result.Integral())
for b in range(h_result.GetNbinsX()):
    bin = b+1
    h_result.SetBinError(bin, r.TMath.Sqrt(h_result.GetBinContent(bin)))

ofile = r.TFile.Open("{}_{}.root".format(oname,args.region),"RECREATE")
ofile.cd()
hdir = ofile.mkdir(args.region)
hdir.cd()
h_result.Write(oname)

