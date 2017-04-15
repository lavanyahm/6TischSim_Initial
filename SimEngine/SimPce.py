#!/usr/bin/python
'''
\a author Lavanya
'''

#============================ logging =========================================

import logging
import threading
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
log = logging.getLogger('SimPce')
log.setLevel(logging.ERROR)
log.addHandler(NullHandler())

#============================ imports =========================================
import math


import SimEngine
import SimSettings
import Mote
#============================ defines =========================================

#============================ body ============================================

class SimPce(object):
    
    #===== start singleton
    _instance      = None
    _init          = False
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SimPce,cls).__new__(cls, *args, **kwargs)
        return cls._instance
    #===== end singleton
    
    def __init__(self,runNum = None,failIfNotInit=False ):
	print 'Init SimPce'

        #===== start singleton
        if self._init:
            return
        self._init = True
        #===== end singleton
        self.dataLock                       = threading.RLock()

        # store params
        self.runNum                         = runNum

        # local variables
        self.engine                         = SimEngine.SimEngine()
        self.settings                       = SimSettings.SimSettings()
        
        self.TotalPktReachedDagroot         =0
        self.TotalPktSent                   =0        
         
        #IISc_algo
        self.locParStatus                   =[ ] #Lcoation and Parant status of Mote       
        self.perFlowData                    =[ ]
        #self.expectedPdr		    =[0.9,0.7]	         
	self.flowDebtList		    =[ ]
        self.numMotes                       =0
        self.fileContent                    =[]
	self.motes = [Mote.Mote(id) for id in range(self.settings.numMotes)]  #Need to change as Self.Engine.motes
	self.numFlows                       = self.settings.numFlows    
	        
        self.expectedPdr		    =[ ]
	self.expectedPdr.append (self.settings.expectedPdrFlow1)        	         
	self.expectedPdr.append (self.settings.expectedPdrFlow2)        	         
	self.expectedPdr.append (self.settings.expectedPdrFlow3)
        self.expectedPdr.append (self.settings.expectedPdrFlow4)        	        
        self._stats_resetpktStats()

	self.schedules			    = {}	



    def destroy(self):
        # destroy my own instance
        self._instance                      = None
        self._init                          = False
        
    def readSchedulesFile(self):
	with self.dataLock:
	    fContent = [line.rstrip() for line in open("schedules.csv")]

            self.schedules = dict(line.split(':') for line in fContent)

    def get_slots(self,node, parent, dir):
	key = str(node) + ',' + str(parent) + ',' + dir

	schedule = self.schedules[key]
	schedule_list = [int(cell) for cell in schedule.split(',')]

	return len(schedule_list), schedule_list
    
    def readTopologyFile(self):
       with self.dataLock:
        with open("Topology5Motes.csv") as f:
         fContent = f.readlines()
         f.close()
         self.numMotes =0
         for line in fContent:
               line = line.rstrip()
               tBuffer = line.split("\t")
               self.fileContent.insert ( int(tBuffer[0]),tBuffer)
               self.numMotes  += 1
         print "Pce :: Num of Mote :",self.numMotes
         self.settings.numMotes = self.numMotes
	
 
    def _stats_resetpktStats(self):
        with self.dataLock:
          self.pktstats={
          
          }
          for i in range (1, self.numFlows+1):
              appGenerated          = "appGenerated_F" + str(i)
              appReachesDagroot     = "appReachesDagroot_F" +str(i)
	      appPDRDebt                = "appPDRDebt_F" +str(i)
              
              self.pktstats[appGenerated]      =        0   # number of packets app layer generated
              self.pktstats[appReachesDagroot] =        0   # number of packets received at the DAGroot
              self.pktstats[appPDRDebt] =        0   # PDR Flow



    def stats_updatePktStatus(self,name):
       with self.dataLock:
            self.pktstats[name] += 1
        #    self._updatePDRDebt()  #For  Default update  uncomment the line
            self._printActualPDRDebt()

    def _printActualPDRDebt(self):
	self.motes[1]._log(self.motes[1].INFO, "[app], Actual PDR Debt",)       

        with self.dataLock:
            for i  in range (1, self.numFlows+1): 
                 appGenerated              = "appGenerated_F" + str(i)
                 appReachesDagroot         = "appReachesDagroot_F" +str(i)
                 appPDRDebt                = "appPDRDebt_F"  + str(i)

                 numAppGene      = self.pktstats [appGenerated]   
                 numAppReached   = self.pktstats [appReachesDagroot]
                 if numAppGene != 0:    
                    debt  =  self.expectedPdr[i-1]  - ( numAppReached / float (numAppGene) )
		 self.motes[1]._log(self.motes[1].INFO, "[app], Actual PDR Debt: flow: {0}, debt: {1}", (i,debt),)  
		 self.motes[1]._log(self.motes[1].INFO, "[app], Flow: Reached: {0}, generated: {1}", (numAppReached,numAppGene),)  
    
    def _updatePDRDebt(self):
	#print "Updating PDR Debt at asn :",self.engine.getAsnDebt
	self.motes[1]._log(self.motes[1].INFO, "[app], Updating PDR Debt",)       
        i = 1
        while i < self.settings.numMotes:
               self.motes[1]._stats_incrementMoteStats('updatePDRStatus')
               i += 1
        with self.dataLock:
            for i  in range (1, self.numFlows+1): 
                 appGenerated              = "appGenerated_F" + str(i)
                 appReachesDagroot         = "appReachesDagroot_F" +str(i)
                 appPDRDebt                = "appPDRDebt_F"  + str(i)

                 numAppGene      = self.pktstats [appGenerated]   
                 numAppReached   = self.pktstats [appReachesDagroot]
                 if numAppGene != 0:    
                    self.pktstats [appPDRDebt]  =  self.expectedPdr[i-1]  - ( numAppReached / float (numAppGene) )

        self._schedule_updatePDR()
    
    def  getPDRDebt(self):
         with self.dataLock:
	      flowPDR ={ 
              }
              for i  in range (1, self.numFlows+1):
                  appPDRDebt     = "appPDRDebt_F" +str(i)
                  flowPDR [i] = self.pktstats[appPDRDebt]
              return flowPDR
                
    def _schedule_updatePDR(self):
	print 'Scheduling Update PDR'
        with self.dataLock:
            self.engine.scheduleIn(
                delay       = 0.1, #Change  update period
                cb          = self._updatePDRDebt,
                uniqueTag   = (None,'_updatePDRDebt'),
                priority    = 6,
            )

