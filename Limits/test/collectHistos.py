
import ROOT
import os, sys
import optparse 



usage = 'usage: %prog -p histosPath -o outputFile'
parser = optparse.OptionParser(usage)
parser.add_option('-p', '--path', dest='path', type='string', default= "/t3home/decosa/SVJ/CMSSW_8_1_0/src/ttDM/stat/test/histos2016/",help='Where can I find input histos?')
parser.add_option("-o","--outputFile",dest="output",type="string",default="histos.root",help="Name of the output file collecting histos in Combine user frieldy schema. Default is histos.root")

(opt, args) = parser.parse_args()
sys.argv.append('-b')


path_ = opt.path
ofilename = opt.output

# List of histograms

histos = {"BDT0":"h_Mt_BDT0","BDT1" :"h_Mt_BDT1", "BDT2": "h_Mt_BDT2", "CRBDT0":"h_Mt_CRBDT0", "CRBDT1":"h_Mt_CRBDT1", "CRBDT2":"h_Mt_CRBDT2"}

# Creating output file

ofile = ROOT.TFile(ofilename,"RECREATE")
ofile.Close()



# Getting list of files in histos
print os.listdir(path_)
sampFiles = [f for f in os.listdir(path_) if (os.path.isfile(os.path.join(path_, f)) and f.endswith(".root") and f!=ofilename )]









for f in sampFiles: 

    try:
        ifile = ROOT.TFile.Open(path_ + f)
    except IOError:
        print "Cannot open ", f
    else:
        print "Opening file ",  f
        ifile.cd()
        

    samp = f.replace(".root", "")         
    ofile = ROOT.TFile(ofilename,"UPDATE")
    for k_, h_ in histos.iteritems():    
        h = ifile.Get(h_)
        if not os.path.isdir( k_):
            newsubdir = ofile.mkdir(k_)
        ofile.cd(k_)
        if(samp.startswith("Data")): samp = "data_obs"
        h.SetName(samp)
        h.Write(samp, ROOT.TObject.kWriteDelete)



    ofile.Write()
    ofile.Close()
