#!/usr/bin/python
'''
\brief Plots statistics with a selected parameter. 

\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
\author Kazushi Muraoka <k-muraoka@eecs.berkeley.edu>
\author Nicola Accettura <nicola.accettura@eecs.berkeley.edu>
\author Xavier Vilajosana <xvilajosana@eecs.berkeley.edu>
'''

#============================ adjust path =====================================

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('plotStatsVsParameter')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================

import os
import re
import glob
import sys
import math

import numpy
import scipy
import scipy.stats

import logging.config
import matplotlib.pyplot
import argparse

#============================ defines =========================================

CONFINT = 0.95

COLORS = [
   '#0000ff', #'b'
   '#ff0000', #'r'
   '#008000', #'g'
   '#bf00bf', #'m'
   '#000000', #'k'
   '#ff0000', #'r'

]

LINESTYLE = [
    '--',
    '-.',
    ':',
    '-',
    '-',
    '-',
]

ECOLORS= [
   '#0000ff', #'b'
   '#ff0000', #'r'
   '#008000', #'g'
   '#bf00bf', #'m'
   '#000000', #'k'
   '#ff0000', #'r'
]

#============================ body ============================================

def parseCliOptions():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument( '--statsName',
        dest       = 'statsName',
        nargs      = '+',
        type       = str,
        default    = 'numTxCells',
        help       = 'Name of the statistics to be used as y axis.',
    )
    
    options        = parser.parse_args()
    
    return options.__dict__

#===== statistics vs cycle

def plot_statsVsCycle(statsName):
    
    dataDirs = []
    for dataDir in os.listdir(os.path.curdir):
        if os.path.isdir(dataDir):
            if (statsName == 'probableCollisions' or statsName == 'effectiveCollidedTxs') and dataDir=='no interference':
                continue
            dataDirs += [dataDir]
    
    stats      = {}
    
    # One curve is generated by each output.da
    for dataDir in dataDirs: 

        # assume that each dataDir has one directory which includes one file
        #for dir in os.listdir(dataDir):
            
        for infilename in glob.glob(os.path.join(dataDir,'*.dat')):
            
            # find numCyclesPerRun    
            with open(infilename,'r') as f:
                for line in f:
                    
                    if line.startswith('##'):
                        
                        # numCyclesPerRun
                        m = re.search('numCyclesPerRun\s+=\s+([\.0-9]+)',line)
                        if m:
                            numCyclesPerRun    = int(m.group(1))
            
            # find colnumcycle
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('# '):
                        elems                   = re.sub(' +',' ',line[2:]).split()
                        numcols                 = len(elems)
                        colnumstatsName         = elems.index(statsName)
                        colnumcycle             = elems.index('cycle')
                        colnumrunNum            = elems.index('runNum')                
                        break
                
            # parse data
            statsPerFile = {}
            previousCycle  = None
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    m = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                    stat                = int(m.group(colnumstatsName+1))
                    cycle               = int(m.group(colnumcycle+1))
                    runNum              = int(m.group(colnumrunNum+1))
                    
                    if cycle not in statsPerFile:
                         statsPerFile[cycle] = []
                    statsPerFile[cycle] += [stat]
                        
                    if cycle==0 and previousCycle and previousCycle!=numCyclesPerRun-1:
                        print 'runNum({0}) in {1} is incomplete data'.format(runNum-1,dir)
                        
                    previousCycle = cycle
                        
                                    
            stats[dataDir] = statsPerFile
            
    
    xlabel         = 'slotframe cycles'
    
    if statsName == 'numTxCells':
        ylabel = 'Tx cells'
    elif statsName == 'scheduleCollisions':
        ylabel = 'schedule collisions'
    elif statsName == 'droppedAppFailedEnqueue':
        ylabel = 'dropped packets due to full queue'
    elif statsName == 'effectiveCollidedTxs':
        ylabel = 'potentially colliding transmitters'
    elif statsName == 'probableCollisions':
        ylabel = 'probable collisions'
    else:
        ylabel = statsName
    
    outfilename    = 'output_{}_cycle'.format(statsName)
    
    # plot figure for  
    genStatsVsCyclePlots(
        stats,
        dirs           = dataDirs,
        outfilename    = outfilename,
        xlabel         = 'slotframe cycles',
        ylabel         = ylabel,
        ymax           = 20,
        ymin           = -0.000001
    )

#===== dropped packets vs cycle

def plot_droppedPacketsVsCycle():
    
    dataDirs = []
    for dataDir in os.listdir(os.path.curdir):
        if os.path.isdir(dataDir):
            dataDirs += [dataDir]
    
    stats      = {}
    
    # One curve is generated by each output.da
    for dataDir in dataDirs: 

        # assume that each dataDir has one directory which includes one file
        #for dir in os.listdir(dataDir):
            
        for infilename in glob.glob(os.path.join(dataDir,'*.dat')):
            
            # find numCyclesPerRun    
            with open(infilename,'r') as f:
                for line in f:
                    
                    if line.startswith('##'):
                        
                        # numCyclesPerRun
                        m = re.search('numCyclesPerRun\s+=\s+([\.0-9]+)',line)
                        if m:
                            numCyclesPerRun    = int(m.group(1))
            
            # find colnumcycle
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('# '):
                        elems                         = re.sub(' +',' ',line[2:]).split()
                        numcols                       = len(elems)
                        colnumdroppedAppFailedEnqueue = elems.index('droppedAppFailedEnqueue')
                        colnumdroppedMacRetries       = elems.index('droppedMacRetries')
                        colnumcycle                   = elems.index('cycle')
                        colnumrunNum                  = elems.index('runNum')                
                        break
                
            # parse data
            statsPerFile = {}
            previousCycle  = None
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    m = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                    droppedAppFailedEnqueue = int(m.group(colnumdroppedAppFailedEnqueue+1))
                    droppedMacRetries       = int(m.group(colnumdroppedMacRetries+1))
                    cycle                   = int(m.group(colnumcycle+1))
                    runNum                  = int(m.group(colnumrunNum+1))
                    
                    if cycle not in statsPerFile:
                         statsPerFile[cycle] = []
                    statsPerFile[cycle] += [droppedAppFailedEnqueue+droppedMacRetries]
                        
                    if cycle==0 and previousCycle and previousCycle!=numCyclesPerRun-1:
                        print 'runNum({0}) in {1} is incomplete data'.format(runNum-1,dir)
                        
                    previousCycle = cycle
                        
                                    
            stats[dataDir] = statsPerFile
            
    
    xlabel = 'slotframe cycles'
    ylabel = 'dropped packets'
    outfilename    = 'output_dropped_cycle'
    
    # plot figure for  
    genStatsVsCyclePlots(
        stats,
        dirs           = dataDirs,
        outfilename    = outfilename,
        xlabel         = xlabel,
        ylabel         = ylabel,
        ymin           = -0.000001
    )

#===== signaling for 6top housekeeping vs cycle

def plot_topHousekeepingSignalingVsCycle():
    
    PACKETS_PER_SIGNALING = 3
    
    dataDirs = []
    for dataDir in os.listdir(os.path.curdir):
        if os.path.isdir(dataDir):
            if dataDir=='no housekeeping' or dataDir=='no interference':
                continue
            dataDirs += [dataDir]
    
    stats      = {}
    
    # One curve is generated by each output.da
    for dataDir in dataDirs: 

        # assume that each dataDir has one directory which includes one file
        #for dir in os.listdir(dataDir):
            
        for infilename in glob.glob(os.path.join(dataDir,'*.dat')):
            
            # find numCyclesPerRun    
            with open(infilename,'r') as f:
                for line in f:
                    
                    if line.startswith('##'):
                        
                        # numCyclesPerRun
                        m = re.search('numCyclesPerRun\s+=\s+([\.0-9]+)',line)
                        if m:
                            numCyclesPerRun    = int(m.group(1))
            
            # find colnumcycle
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('# '):
                        elems                         = re.sub(' +',' ',line[2:]).split()
                        numcols                       = len(elems)
                        colnumtopTxRelocatedCells     = elems.index('topTxRelocatedCells')
                        colnumtopTxRelocatedBundles   = elems.index('topTxRelocatedBundles')
                        colnumcycle                   = elems.index('cycle')
                        colnumrunNum                  = elems.index('runNum')                
                        colnumtopRxRelocatedCells     = None
                        if 'topRxRelocatedCells' in elems:
                            colnumtopRxRelocatedCells       = elems.index('topRxRelocatedCells')

                        break
                
            # parse data
            statsPerFile = {}
            previousCycle  = None
            with open(infilename,'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue
                    m = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                    topTxRelocatedCells     = int(m.group(colnumtopTxRelocatedCells+1))
                    topTxRelocatedBundles   = int(m.group(colnumtopTxRelocatedBundles+1))
                    
                    topRxRelocatedCells     = 0
                    if colnumtopRxRelocatedCells:
                        topRxRelocatedCells     = int(m.group(colnumtopRxRelocatedCells+1))
                    
                    cycle                   = int(m.group(colnumcycle+1))
                    runNum                  = int(m.group(colnumrunNum+1))
                    
                    if cycle not in statsPerFile:
                         statsPerFile[cycle] = []
                    statsPerFile[cycle] += [PACKETS_PER_SIGNALING*(topTxRelocatedCells+topTxRelocatedBundles+topRxRelocatedCells)]
                        
                    if cycle==0 and previousCycle and previousCycle!=numCyclesPerRun-1:
                        print 'runNum({0}) in {1} is incomplete data'.format(runNum-1,dir)
                        
                    previousCycle = cycle
                        
                                    
            stats[dataDir] = statsPerFile
            
    
    xlabel = 'slotframe cycles'
    ylabel = 'signaling packets for 6top housekeeping'
    outfilename    = 'output_signaling_cycle'
    
    # plot figure for  
    genStatsVsCyclePlots(
        stats,
        dirs           = dataDirs,
        outfilename    = outfilename,
        xlabel         = xlabel,
        ylabel         = ylabel,
        ymax           = 20,
        ymin           = -0.000001
    )

#============================ plotters ========================================
 
def genStatsVsCyclePlots(vals, dirs, outfilename, xlabel, ylabel, xmin=False, xmax=False, ymin=False, ymax=False, log = False):

    # print
    print 'Generating {0}...'.format(outfilename),
    
    matplotlib.pyplot.figure()
    matplotlib.pyplot.xlabel(xlabel, fontsize='large')
    matplotlib.pyplot.ylabel(ylabel, fontsize='large')
    if log:
        matplotlib.pyplot.yscale('log')

    for dataDir in dirs:
        # calculate mean and confidence interval
        meanPerParameter    = {}
        confintPerParameter = {}
        for (k,v) in vals[dataDir].items():
            a                        = 1.0*numpy.array(v)
            n                        = len(a)
            se                       = scipy.stats.sem(a)
            m                        = numpy.mean(a)
            confint                  = se * scipy.stats.t._ppf((1+CONFINT)/2., n-1)
            meanPerParameter[k]      = m
            confintPerParameter[k]   = confint
    
        # plot
        x         = sorted(meanPerParameter.keys())
        y         = [meanPerParameter[k] for k in x]
        yerr      = [confintPerParameter[k] for k in x]
        
        if dataDir == 'tx-housekeeping':
            index = 0
        elif dataDir == 'rx-housekeeping':
            index = 1
        elif dataDir == 'tx-rx-housekeeping':
            index = 2
        elif dataDir == 'no housekeeping':
            index = 3
        elif dataDir == 'no interference':
            index = 4
        
        matplotlib.pyplot.errorbar(
            x        = x,
            y        = y,
            #yerr     = yerr,
            color    = COLORS[index],
            ls       = LINESTYLE[index],
            ecolor   = ECOLORS[index],
            label    = dataDir
        )
        
        datafile=open(outfilename+'.dat', "a")
        print >> datafile,dataDir
        print >> datafile,xlabel,x
        print >> datafile,ylabel,y
        #print >> datafile,'conf. inverval',yerr
    
    matplotlib.pyplot.legend(prop={'size':12},loc=0)
    if xmin:
        matplotlib.pyplot.xlim(xmin=xmin)
    if xmax:
        matplotlib.pyplot.xlim(xmax=xmax)
    if ymin:
        matplotlib.pyplot.ylim(ymin=ymin)
    if ymax:
        matplotlib.pyplot.ylim(ymax=ymax)

    matplotlib.pyplot.savefig(outfilename + '.png')
    matplotlib.pyplot.savefig(outfilename + '.eps')    
    matplotlib.pyplot.close('all')
    
    # print
    print 'done.'

#============================ main ============================================
def main():
    
    # parse CLI option
    options      = parseCliOptions()
    statsName    = options['statsName']
    
    for statsName in options['statsName']:
        # stats vs cycle
        plot_statsVsCycle(statsName)
    
    # plot dropped packets vs cycle
    plot_droppedPacketsVsCycle()
    
    # plot singaling for 6top housekeeping vs cycle
    plot_topHousekeepingSignalingVsCycle()
    
if __name__=="__main__":
    main()
