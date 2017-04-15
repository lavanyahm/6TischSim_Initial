#!/usr/bin/python

import os
import re
import glob
import pprint

import numpy
import scipy
import scipy.stats

 valuesPerRun = {} 
    infilepaths    = glob.glob(os.path.join(DATADIR,'**','*.dat'))
    for infilepath in infilepaths:

        # print
        print 'Parsing {0} for {1}...'.format(infilepath,elemName),

        # find col_elemName, col_runNum, cpuID
        col_elemName    = None
        col_runNum      = None
        cpuID           = None
        with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('# '):
                    # col_elemName, col_runNum
                    elems        = re.sub(' +',' ',line[2:]).split()
                    numcols      = len(elems)
                    col_elemName = elems.index(elemName)
                    break
        assert col_elemName!=None
