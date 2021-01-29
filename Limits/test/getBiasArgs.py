#!/usr/bin/env python

from __future__ import print_function
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

def get_param_names(region,fn):
    fnnames = ["main","alt"]
    params = {
        "main": {
            "highCut": (4,5),
            "lowCut": (1,2),
            "highSVJ2": (1,2),
            "lowSVJ2": (1,2),
        },
        "alt": {
            "highCut": (3,3),
            "lowCut": (2,2),
            "highSVJ2": (2,2),
            "lowSVJ2": (2,2),    
        },
    }
    fn = fnnames[fn]
    order = params[fn][region][0]
    n = params[fn][region][1]
    names = ["{}_p{}_{}{}".format(region.replace("_2018",""),i+1,order,'_'+fn if fn=="alt" else "") for i in range(n)]
    return names

def main(region, fn, suff):
    other_fn = int(not fn)
    indarg = "pdf_index_{}_2018".format(region)

    setargs = ["{}={}".format(indarg,fn)]
    frzargs = [indarg]+get_param_names(region,other_fn)
    trkargs = get_param_names(region,fn)

    args = [
        'SetArg{}="{}"'.format(suff,','.join(setargs)),
        'FrzArg{}="{}"'.format(suff,','.join(frzargs)),
        'TrkArg{}="{}"'.format(suff,','.join(trkargs)),
    ]
    print('\n'.join(args))

if __name__=="__main__":
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-r", "--region", dest="region", type=str, required=True, help="region name")
    parser.add_argument("-f", "--function", dest="function", type=int, required=True, choices=[0,1], help="function (0: main, 1: alt)")
    parser.add_argument("-s", "--suffix", dest="suffix", type=str, required=True, help="suffix for variable names")
    args = parser.parse_args()

    main(args.region, args.function, args.suffix)
