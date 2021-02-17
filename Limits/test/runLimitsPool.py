import os,sys,subprocess,shlex
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from multiprocessing import Pool
import getBiasArgs
from Stat.Limits.bruteForce import makeVarInfoList

# make status messages useful
def fprint(msg):
    import sys
    print(msg)
    sys.stdout.flush()

def alpha_val(val):
    result = 0
    if val=="peak": result = -2
    elif val=="high": result = -1
    elif val=="low": result = -3
    else: result = float(val)
    return result

def get_signame(mass):
    return "SVJ_mZprime{}_mDark20_rinv03_alphapeak".format(mass)

def getInitFromBF(fname, pdfname):
    import ROOT as r
    r.gSystem.Load("libHiggsAnalysisCombinedLimit.so")
    file = r.TFile.Open(fname)
    ws = file.Get(default_ws)
    pdf = ws.pdf(pdfname)

    pars = makeVarInfoList(pdf.getPars())
    setargs = ["{}={}".format(p.name,p.val) for p in pars]
    return setargs

with open('dict_xsec_Zprime.txt','r') as xfile:
    xsecs = {int(xline.split('\t')[0]): float(xline.split('\t')[1]) for xline in xfile}

default_ws = "SVJ"

default_masses = [
1500,
1700,
1900,
2100,
2300,
2500,
2700,
2900,
3100,
3300,
3500,
3700,
3900,
4100,
4300,
4500,
4700,
4900,
5100,
]

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
parser.add_argument("-r", "--regions", dest="regions", type=str, default=["cut","bdt"], nargs="+", help="list of combined regions")
parser.add_argument("-n", "--npool", dest="npool", type=int, default=6, help="number of processes")
parser.add_argument("-D", "--dry-run", dest="dry_run", default=False, action='store_true', help="dry run (print commands but don't execute)")
parser.add_argument("-f", "--freezeNorm", dest="freezeNorm", default=False, action="store_true", help="freeze bkg normalization to data")
parser.add_argument("-m", "--mod", dest="mod", type=str, default=[], choices=["Alt","S0","Nostat","Calls"], nargs="*", help="modification(s)")
parser.add_argument("-j", "--just-hadd", dest="just_hadd", default=False, action="store_true", help="don't run any combine commands, just hadd")
parser.add_argument("--no-hadd", dest="no_hadd", default=False, action="store_true", help="don't hadd")
parser.add_argument("-M", "--manualCLs", dest="manualCLs", default=False, action='store_true', help="use manual CLs algorithm")
init_group = parser.add_mutually_exclusive_group()
init_group.add_argument("-i", "--initCLs", dest="initCLs", default=False, action='store_true', help="use initialized CLs algorithm")
init_group.add_argument("-I", "--init", dest="init", default=False, action='store_true', help="use existing initial values of parameters")
parser.add_argument("--extra", dest="extra", type=str, default="", help="extra args for manual CLs")
parser.add_argument("--masses", dest="masses", type=int, default=default_masses, nargs="*", help="masses")
parser.add_argument("-N", "--name", dest="name", type=str, default="Test", help="name for combine files")
parser.add_argument("-s", "--suff", dest="suff", type=str, default="", help="suffix to pick different version of datacards")
args = parser.parse_args()

pwd = os.getcwd()

def runCmd(args):
    output = ""
    try:
        output += subprocess.check_output(shlex.split(args),stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output += e.output
    return output

def doLimit(mass):
    signame = get_signame(mass)
    os.chdir(os.path.join(pwd,signame))

    params = {
        "xsec": xsecs[mass],
        "mZprime": mass,
        "mDark": 20,
        "rinv": 0.3,
        "alpha": alpha_val("peak"),
    }
    setargs = []
    trkargs = []
    treargs = []
    extargs = ""
    for p,v in params.iteritems():
        setargs.append(p+"="+str(v))
        trkargs.append(p)
        extargs = extargs+p+" extArg "+str(v)+"\n"
    frzargs = trkargs[:]

    fn = 1 if "Alt" in args.mod else 0
    for region in regions:
        fname = "ws_{}_{}_2018_template.root".format(signame, region)
        biasargs = getBiasArgs.main(fname, default_ws, region, fn, verbose=False)
        setargs.extend(biasargs['SetArg'])
        frzargs.extend(biasargs['FrzArg'])
        trkargs.extend(biasargs['TrkArg'])
        treargs.extend(biasargs['TrkArg'])
        if args.init:
            setargs.extend(getInitFromBF(fname, "Bkg{}_{}_2018".format("_Alt" if "Alt" in args.mod else "", region)))

    for ch in ["ch1","ch2"]:
        normargs = ["n_exp_bin{}_proc_roomultipdf".format(ch),"shapeBkg_roomultipdf_{}__norm".format(ch),"n_exp_final_bin{}_proc_roomultipdf".format(ch),"n_exp_final_bin{}_proc_SVJ_mZprime{}_mDark20_rinv03_alphapeak".format(ch,mass)]
        trkargs.extend(normargs)
        treargs.extend(normargs)
        if args.freezeNorm: frzargs.append("shapeBkg_roomultipdf_{}__norm".format(ch))

    if "S0" in args.mod:
        frzargs.append("allConstrainedNuisances")
    if "Nostat" in args.mod:
        frzargs.append("rgx{mcstat_.*}")

    cargs = "--setParameters "+','.join(setargs)+" --freezeParameters "+','.join(frzargs)+" --trackParameters "+','.join(trkargs)+" --trackErrors "+','.join(treargs)+" --keyword-value ana="+combo+" -n "+cname
    if "Calls" in args.mod:
        cargs += " --X-rtd MINIMIZER_MaxCalls=100000"
    datacards = []
    for region in regions:
        datacards.append(signame+"_{}_2018_template_bias{}.txt".format(region,args.suff))
    dcfname = "datacard_{}_{}.txt".format(mass,combo)

    outputs = []
    fprint("Calculating limit for {}...".format(mass))
    # combine cards
    command = "combineCards.py "+" ".join(datacards)+" > "+dcfname
    outputs.append(command)
    if not args.dry_run:
        os.system(command)
        # add ext args
        with open(dcfname,'a') as dcfile:
            dcfile.write(extargs)
    # run combine
    cargs += " -d "+dcfname
    if args.manualCLs:
        extra = args.extra[:]
        # to use initCLs and manualCLs together, specify params to extract
        if args.initCLs:
            extra += " -i shapeBkg high low"
        command = 'python ../manualCLs.py {} -a "{}" -n {}'.format(extra,cargs,combo+"_"+cname)
    else:
        command = "combine -M AsymptoticLimits "+cargs
    outputs.append(command)
    if not args.dry_run: 
        outputs.append(runCmd(command))
    os.chdir(pwd)

    return outputs

cname = args.name[:]
if len(args.mod)>0: cname += ''.join(args.mod)
if args.freezeNorm: cname += "Frz"
if args.manualCLs and not "-A" in args.extra: cname += "Manual"
if args.init: cname += "BFInit"
if args.initCLs: cname += "Init"
if "-b" in args.extra: cname += "Bonly"
if "-s" in args.extra: cname += "Syst"

combos = {
"cut": ["highCut","lowCut"],
"bdt": ["highSVJ2","lowSVJ2"],
}
for combo,regions in combos.iteritems():
    if not combo in args.regions: continue
    if not args.just_hadd:
        if args.npool==0:
            for outputs in [doLimit(mass) for mass in args.masses]:
                fprint('\n'.join(outputs))
        else:
            p = Pool(args.npool if not args.dry_run else 1)
            for outputs in p.imap_unordered(doLimit, args.masses):
                fprint('\n'.join(outputs))
            p.close()
            p.join()

    outfiles = []
    for mass in args.masses:
        signame = get_signame(mass)
        mname = "ManualCLs" if args.manualCLs and not "-A" in args.extra else "AsymptoticLimits"
        sname = "StepA" if args.manualCLs and "-A" in args.extra else ""
        fname = signame+"/higgsCombine"+sname+cname+"."+mname+".mH120.ana"+combo+".root"
        append = False
        if args.dry_run:
            append = True
        else:
            # check if limit converged
            from ROOT import TFile, TTree
            f = TFile.Open(fname)
            if f==None: continue
            t = f.Get("limit")
            if t==None: continue
            # 5 expected + 1 observed (+ prefit sometimes)
            append = t.GetEntries() >= 6
        if append: outfiles.append(fname)
        else: fprint("Warning: {} limit for mZprime = {} did not converge".format(combo, mass))

    # combine outfiles
    if not args.no_hadd:
        os.chdir(pwd)
        outname = "limit_"+combo+cname[4:]+".root"
        command = "hadd -f2 "+outname+''.join(" "+ofn for ofn in outfiles)
        fprint(command)
        if not args.dry_run: os.system(command)
