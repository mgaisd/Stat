import subprocess
import sys

ifile=sys.argv[1]
ofile=sys.argv[1].split(".")[0] + ".png"
print(ifile, ofile)

subprocess.call("convert %s %s"%(ifile, ofile),shell=True)
