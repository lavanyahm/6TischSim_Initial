#!/usr/bin/python
'''
\brief Entry point to start a simulation.

A number of command-line parameters are available to modify the simulation
settings. Use '--help' for a list of them.

\author Thomas Watteyne <watteyne@eecs.berkeley.edu>
\author Kazushi Muraoka <k-muraoka@eecs.berkeley.edu>
\author Nicola Accettura <nicola.accettura@eecs.berkeley.edu>
\author Xavier Vilajosana <xvilajosana@eecs.berkeley.edu>
'''

#============================ adjust path =====================================

import os
import sys
if __name__=='__main__':
    here = sys.path[0]
    sys.path.insert(0, os.path.join(here, '..'))

#============================ logging =========================================

import logging
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('BatchSim')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================

import time
import itertools
import logging.config
import argparse
import threading

from SimEngine     import SimEngine,   \
                          SimSettings, \
                          SimStats
from SimGui        import SimGui

#============================ defines =========================================

#============================ helpers =========================================

def parseCliOptions():
    
    parser = argparse.ArgumentParser()
    # sim
    parser.add_argument('--gui',
        dest       = 'gui',
        action     = 'store_true',
        default    = False,
        help       = '[sim] Display the GUI.',
    )
    parser.add_argument( '--cpuID',
        dest       = 'cpuID',
        type       = int,
        default    = None,
        help       = '[sim] id of the CPU running this simulation (for batch).',
    )
    parser.add_argument( '--numRuns',
        dest       = 'numRuns',
        type       = int,
        default    = 100,
        help       = '[sim] Number of simulation runs.',
    )
    parser.add_argument( '--numCyclesPerRun',
        dest       = 'numCyclesPerRun',
        type       = int,
        default    = 1000,# * 60 *30,
        help       = '[simulation] Duration of a run, in slotframes.',
    )
    parser.add_argument('--simDataDir',
        dest       = 'simDataDir',
        type       = str,
        default    = 'simData',
        help       = '[simulation] Simulation log directory.',
    )
    # topology
    parser.add_argument( '--numMotes',
        dest       = 'numMotes',
        nargs      = '+',
        type       = int,
        default    = 10,
        help       = '[topology] Number of simulated motes.',
    )
    parser.add_argument( '--squareSide',
        dest       = 'squareSide',
        type       = float,
        default    = 2.000,
        help       = '[topology] Side of the deployment area (km).',
    )
    # app
    parser.add_argument( '--pkPeriod',
        dest       = 'pkPeriod',
        nargs      = '+',
        type       = float,
       # default    = [0.08,0.1,0.3],
        default    = 1.0,
        help       = '[app] Average period between two data packets (s).',
    )
    parser.add_argument( '--pkPeriodVar',
        dest       = 'pkPeriodVar',
        type       = float,
        default    = 0.05,
        help       = '[app] Variability of pkPeriod (0.00-1.00).',
    )
    parser.add_argument( '--burstTimestamp',
        dest       = 'burstTimestamp',
        nargs      = '+',
        type       = float,
#        default    = 20,
	default    = 5,
        help       = '[app] Timestamp when the burst happens (s).',
    )
    parser.add_argument( '--numPacketsBurst',
        dest       = 'numPacketsBurst',
        nargs      = '+',
        type       = int,
       # default    = 5,
	default    = None,
        help       = '[app] Number of packets in a burst, per node.',
    )
    # rpl
    parser.add_argument( '--dioPeriod',
        dest       = 'dioPeriod',
        type       = float,
        default    = 1.0,
        help       = '[rpl] DIO period (s).',
    )
    # otf
    parser.add_argument( '--otfThreshold',
        dest       = 'otfThreshold',
        nargs      = '+',
        type       = int,
        default    = 1,
        help       = '[otf] OTF threshold (cells).',
    )
    parser.add_argument( '--otfHousekeepingPeriod',
        dest       = 'otfHousekeepingPeriod',
        type       = float,
        default    = 1.0,
        help       = '[otf] OTF housekeeping period (s).',
    )
    # sixtop
    parser.add_argument( '--sixtopHousekeepingPeriod',
        dest       = 'sixtopHousekeepingPeriod',
        type       = float,
        default    = 1.0,
        help       = '[6top] 6top housekeeping period (s).',
    )
    parser.add_argument( '--sixtopPdrThreshold',
        dest       = 'sixtopPdrThreshold',
        type       = float,
        default    = 1.5,
        help       = '[6top] 6top PDR threshold.',
    )
    parser.add_argument('--sixtopNoHousekeeping',
        dest       = 'sixtopNoHousekeeping',
        nargs      = '+',
        type       = int,
        default    = 0,
        help       = '[6top] 1 to disable 6top housekeeping.',
    )
    parser.add_argument('--sixtopNoRemoveWorstCell',
        dest       = 'sixtopNoRemoveWorstCell',
        nargs      = '+',
        type       = int,
        default    = 0,
        help       = '[6top] 1 to remove random cell, not worst.',
    )
    # tsch
    parser.add_argument( '--slotDuration',
        dest       = 'slotDuration',
        type       = float,
        default    = 0.010,
        help       = '[tsch] Duration of a timeslot (s).',
    )
    parser.add_argument( '--slotframeLength',
        dest       = 'slotframeLength',
        type       = int,
        default    = 10,
        help       = '[tsch] Number of timeslots in a slotframe.',
    )
    # phy
    parser.add_argument( '--numChans',
        dest       = 'numChans',
        type       = int,
        default    = 16,
        help       = '[phy] Number of frequency channels.',
    )
    parser.add_argument( '--minRssi',
        dest       = 'minRssi',
        type       = int,
        default    = -97,
        help       = '[phy] Mininum RSSI with positive PDR (dBm).',
    )
    parser.add_argument('--noInterference',
        dest       = 'noInterference',
        nargs      = '+',
        type       = int,
        default    = 0,
        help       = '[phy] Disable interference model.',
    )
   #IISc  

    parser.add_argument('--numDefaultCells',
        dest       = 'numDefaultCells',
        nargs      = '+',
        type       = int,
        default    = 3,
        help       = '[otf] Default number of cells per Mote.',
    )
    parser.add_argument('--numFlows',
        dest       = 'numFlows',
        nargs      = '+',
        type       = int,
        default    = 2,
        help       = '[app] number of flows.',
    )

    parser.add_argument('--deadLineFlow1',
        dest       = 'deadlineFlow1',
        nargs      = '+',
        type       = int,
        default    = 90,
        help       = '[app] Dead Line for Flow1',
    )
    parser.add_argument('--deadLineFlow2',
        dest       = 'deadlineFlow2',
        nargs      = '+',
        type       = int,
        default    = 90,
        help       = '[app] Dead Line for Flow2',
    )
    parser.add_argument('--deadLineFlow3',
        dest       = 'deadlineFlow3',
        nargs      = '+',
        type       = int,
        default    = 90,
        help       = '[app] Dead Line for Flow3',
    )
    parser.add_argument('--deadLineFlow4',
        dest       = 'deadlineFlow4',
        nargs      = '+',
        type       = int,
        default    = 90,
        help       = '[app] Dead Line for Flow4',
    )


    parser.add_argument('--expectedPdrFlow1',
        dest       = 'expectedPdrFlow1',
        nargs      = '+',
        type       = float,
        default    = 0.90,
        help       = '[app] PDR Requirment  for Flow1',
    )

    parser.add_argument('--expectedPdrFlow2',
        dest       = 'expectedPdrFlow2',
        nargs      = '+',
        type       = float,
        default    = 0.90,
        help       = '[app] PDR Requirment  for Flow2',
    )

    parser.add_argument('--expectedPdrFlow3',
        dest       = 'expectedPdrFlow3',
        nargs      = '+',
        type       = float,
        default    = 0.90,
        help       = '[app] PDR Requirment  for Flow3',
    )
    parser.add_argument('--expectedPdrFlow4',
        dest       = 'expectedPdrFlow4',
        nargs      = '+',
        type       = float,
        default    = 0.90,
        help       = '[app] PDR Requirment  for Flow4',
    )
    parser.add_argument('--isDelayConstraint',
        dest       = 'isDelayConstraint',
        action     = 'store_true',
        default    = False,
        help       = '[app] is Delay Contraint  enabled .',
   )

    parser.add_argument('--enableMarkovPropagation',
        dest       = 'enableMarkovPropagation',
        action     = 'store_true',
        default    = False,
        help       = '[app] enable markov propagation model.',
   )

    parser.add_argument('--enableCellAllocation',
        dest       = 'enableCellAllocation',
        action     = 'store_true',
        default    = False,
        help       = '[app] enable cell allocation from given file',
   )

    options        = parser.parse_args()
    return options.__dict__

def printOrLog(simParam,output):
    if simParam['cpuID']!=None:
        with open('cpu{0}.templog'.format(simParam['cpuID']),'w') as f:
            f.write(output)
    else:
        print output

def runSims(options):
    # record simulation start time
    simStartTime   = time.time()
    
    # compute all the simulation parameter combinations
    combinationKeys     = sorted([k for (k,v) in options.items() if type(v)==list])
    simParams           = []
    for p in itertools.product(*[options[k] for k in combinationKeys]):
        simParam = {}
        for (k,v) in zip(combinationKeys,p):
            simParam[k] = v
        for (k,v) in options.items():
            if k not in simParam:
                simParam[k] = v
        simParams      += [simParam]
    
    # run a simulation for each set of simParams
    for (simParamNum,simParam) in enumerate(simParams):
        
         # record run start time
        runStartTime = time.time()
        
        #log('INFO',"[runsimOneCpu] {0} {1} :",(simParamNum,simParam ),)
        # run the simulation runs
        for runNum in xrange(simParam['numRuns']):
            output  = 'parameters {0}/{1}, run {2}/{3}'.format(
               simParamNum+1,
               len(simParams),
               runNum+1,
               simParam['numRuns']
            )

            printOrLog(simParam,output)
            
            # create singletons
            settings         = SimSettings.SimSettings(**simParam)
            settings.setStartTime(runStartTime)
            settings.setCombinationKeys(combinationKeys)
            simengine        = SimEngine.SimEngine(runNum)
            simstats         = SimStats.SimStats(runNum)
            
            # start simulation run
            simengine.start()
            
            # wait for simulation run to end
            simengine.join()
            
            # destroy singletons
            simstats.destroy()
            simengine.destroy()
            settings.destroy()
        
        # print
        output  = 'simulation ended after {0:.0f}s.'.format(time.time()-simStartTime)
        printOrLog(simParam,output)
#        self._log(self.INFO, "simulation ended  startTime{0} - endTime{1}.", ((simStartTime,time.time()),)


def log(severity,template,params=()):

        if   severity=='DEBUG':
            if not log.isEnabledFor(logging.DEBUG):
                return
            logfunc = log.debug
        elif severity=='INFO':
            if not log.isEnabledFor(logging.INFO):
                return
            logfunc = log.info
        elif severity=='WARNING':
            if not log.isEnabledFor(logging.WARNING):
                return
            logfunc = 'warning'
        elif severity=='ERROR':
            if not log.isEnabledFor(logging.ERROR):
                return
            logfunc = log.error
        else:
            raise NotImplementedError()

        output  = []
        output += [template.format(*params)]
        output  = ''.join(output)
        logfunc(output)








#============================ main ============================================

def main():
    #import pdb
    #pdb.set_trace()	
    # initialize logging
    logging.config.fileConfig('logging.conf')
    print"[runOneCPu]  Main"
    # parse CLI options
    options        = parseCliOptions()
    
    if options['gui']:
        # create the GUI
        gui        = SimGui.SimGui()
        
        # run simulations (in separate thread)
        simThread  = threading.Thread(target=runSims,args=(options,))
        simThread.start()
        
        # start GUI's mainloop (in main thread)
        gui.mainloop()
    else:        
        # run the simulations
        runSims(options)

if __name__=="__main__":
    main()
