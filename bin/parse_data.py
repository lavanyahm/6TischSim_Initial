#!/usr/bin/python2.7

import re
import sys
import numpy
import os
import glob
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np 
##############################################################
#SIMULATION PARAMETERS:
DATADIR       = 'simData'
noOfCycles = 0
noOfRuns   = 0
noOfFlows   = 0


def getCumulativeAverage(a):
	lB = [sum(a[0:i+1]) for i in range(len(a))]
	return lB


def getValuesPerCycle(infilepath, elemName):

	valuesPerCycle = {}

	col_elemName    = None
	col_cycleNum      = None

	with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('# '):
                    # col_elemName, col_runNum
                    elems        = re.sub(' +',' ',line[2:]).split()
                    numcols      = len(elems)
                    col_elemName = elems.index(elemName)
                    col_cycleNum   = elems.index('cycle')
                    break

	# parse data
	with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                m       = re.search('\s+'.join(['([\.0-9]+)']*numcols),line.strip())
                cycleNum  = int(m.group(col_cycleNum+1))
                try:
                    elem         = float(m.group(col_elemName+1))
                except:
                    try:
                        elem     =   int(m.group(col_elemName+1))
                    except:
                        elem     =       m.group(col_elemName+1)

                if (cycleNum) not in valuesPerCycle:
                    valuesPerCycle[cycleNum] = []
                valuesPerCycle[cycleNum] += [elem]

	return valuesPerCycle


def getAverageOfCycle(valuesPerCycle):
	i = 0
	avg_cycle = [];
	while i < noOfCycles:
		avg_cycle.append(sum(valuesPerCycle[i]) / float(len(valuesPerCycle[i])))
		i+=1

	return avg_cycle


def calculatePDR(gen, reach):
	pdr = [x/y if y!= 0 else 0 for x,y in zip(reach,gen)]

	return pdr


#Calculate the ratio of control pakts verse data+control
def calculatePktRatio(control, total):
	ratio = [x/y if y!= 0 else 0 for x,y in zip(control,total)]

	return ratio
 
def _getsteadyState(pdr_list):
    steadyState = 0
    

    return steadyState

def getData(value, infilepath, outfilepath):
	cycles = range(1, noOfCycles)
	if value == 'pdr':
		flow   = 1
		pdr_list = []
		while flow < noOfFlows + 1:
			elemName      = 'appGenerated' + "_F" + str(flow) 
			valPerCycle   = getValuesPerCycle(infilepath, elemName)
			avgCycle      = getAverageOfCycle(valPerCycle)
			generated     = getCumulativeAverage(avgCycle)

			elemName      = 'appReachesDagroot' + "_F" + str(flow)
			valPerCycle   = getValuesPerCycle(infilepath, elemName)
			avgCycle      = getAverageOfCycle(valPerCycle)
			reached       = getCumulativeAverage(avgCycle)

			pdr = calculatePDR(generated, reached)

			pdr_list.append(pdr)
			flow += 1


       	        filename = outfilepath +"_pdr"	  
		with open(filename,'w') as f:
			for i in range(noOfCycles-1):
				if noOfFlows == 1: 
            				f.write('%d \t%f\n' % (cycles[i], pdr_list[0][i]))
                                          
				elif noOfFlows == 2:
            				f.write('%d \t%f \t%f\n' % (cycles[i], pdr_list[0][i], pdr_list[1][i]))
                                        
				elif noOfFlows == 3:
            				f.write('%d \t%f \t%f \t%f \n' % (cycles[i], pdr_list[0][i], pdr_list[1][i],pdr_list[2][i]))
				else :
            				f.write('%d \t%f \t%f \t%f \t%f \n' % (cycles[i], pdr_list[0][i], pdr_list[1][i],pdr_list[2][i],pdr_list[3][i]))
      
                i = 0 
                steadyStates = [] 
                for i in  range(noOfFlows):
                    pList =pdr_list[i]  
                    steadyState = pList[0] 
                    for item in pList:
		 	 if (item >=  (steadyState + (steadyState * 0.05))) or (item <= (steadyState - (steadyState * 0.05))):
           	             steadyState = item
                    steadyStates.append(steadyState)                    
		ss = max(steadyStates)
                steadyState ='steadyState=' + str(ss) 
                
                plot = "gnuplot -e " + "\"inFilename='" + filename +"';"+"StudyState='"+steadyState +"';" + "outFilename='" + filename + ".png';yLabel='PDR'\"" +" "+ "plotGraph.gp"      
		from os import system
		system(plot)
 
	elif value == 'numTxCells':
		elemName      = 'numTxCells'
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		numTxCells    = getAverageOfCycle(valPerCycle)
	#	avgCycle      = getAverageOfCycle(valPerCycle)
	#	numTxCells    = getCumulativeAverage(avgCycle)

       	        filename = outfilepath +"_txCells"	  
		with open(filename,'w') as f:
			for i in range(noOfCycles-1): 
            			f.write('%d \t%f\n' % (cycles[i], numTxCells[i]))
                plot = "gnuplot -e " + "\"inFilename='" + filename +"';"+ "outFilename='" + filename + ".png';yLabel='numTxCells'\"" + " " + "plotGraph.gp"      
		from os import system
		system(plot)
	elif value == 'droppedDelayExceed':
		flow   = 1
		exceed_list = []
		while flow < noOfFlows + 1:
			elemName      = 'droppedDelayExceed' + "_F" + str(flow)
			valPerCycle   = getValuesPerCycle(infilepath, elemName)
			avgCycle      = getAverageOfCycle(valPerCycle)
			droppedDelayExceed    = getCumulativeAverage(avgCycle)

			exceed_list.append(droppedDelayExceed)
			flow += 1

		filename = outfilepath +"_droppedDelayExceed"	  
		with open(filename,'w') as f:
			for i in range(noOfCycles-1): 
				if noOfFlows == 1: 
					f.write('%d \t%f\n' % (cycles[i], exceed_list[0][i]))
				elif noOfFlows == 2: 
					f.write('%d \t%f \t%f\n' % (cycles[i], exceed_list[0][i], exceed_list[1][i]))
				elif noOfFlows == 3: 
					f.write('%d \t%f \t%f \t%f \n' % (cycles[i], exceed_list[0][i], exceed_list[1][i],exceed_list[2][i]))
				else: 
					f.write('%d \t%f \t%f \t%f \t%f \n' % (cycles[i], exceed_list[0][i], exceed_list[1][i],exceed_list[2][i],exceed_list[3][i]))
                plot = "gnuplot -e " + "\"inFilename='" + filename +"';"+ "outFilename='" + filename + ".png';yLabel='droppedDelayExceed'\"" + " " + "plotGraph.gp"      
		from os import system
		system(plot)
	elif value == 'aveLatency':
		flow   = 1
		latency_list = []
		while flow < noOfFlows + 1:
			elemName      = 'aveLatency' + "_F" + str(flow)
			valPerCycle   = getValuesPerCycle(infilepath, elemName)
			aveLatency    = getAverageOfCycle(valPerCycle)
			#avgCycle      = getAverageOfCycle(valPerCycle)
			#droppedDelayExceed    = getCumulativeAverage(avgCycle)

			latency_list.append(aveLatency)
			flow += 1

		filename = outfilepath +"_aveLatency"	  
		with open(filename,'w') as f:
			for i in range(noOfCycles-1): 
				if noOfFlows == 1: 
					f.write('%d \t%f\n' % (cycles[i], latency_list[0][i]))
				elif noOfFlows == 2: 
					f.write('%d \t%f \t%f\n' % (cycles[i], latency_list[0][i], latency_list[1][i]))
				elif noOfFlows == 3:  
					f.write('%d \t%f \t%f \t%f \n' % (cycles[i], latency_list[0][i], latency_list[1][i],latency_list[2][i]))
				else :  
					f.write('%d \t%f \t%f \t%f \t%f\n' % (cycles[i], latency_list[0][i], latency_list[1][i],latency_list[2][i],latency_list[3][i]))
                plot = "gnuplot -e " + "\"inFilename='" + filename +"';"+ "outFilename='" + filename + ".png';yLabel='aveLatency'\"" + " " + "plotGraph.gp"      
		from os import system
		system(plot)
	elif value == 'droppedMacRetries':
		flow   = 1
		retries_list = []
		while flow < noOfFlows + 1:
			elemName      = 'droppedMacRetries' + "_F" + str(flow)
			valPerCycle   = getValuesPerCycle(infilepath, elemName)
			avgCycle      = getAverageOfCycle(valPerCycle)
			droppedMacRetries    = getCumulativeAverage(avgCycle)

			retries_list.append(droppedMacRetries)
			flow += 1

		filename = outfilepath +"_droppedMacRetries"	  
		with open(filename,'w') as f:
			for i in range(noOfCycles-1): 
				if noOfFlows == 1: 
					f.write('%d \t%f\n' % (cycles[i], retries_list[0][i]))
				elif noOfFlows == 2: 
					f.write('%d \t%f \t%f\n' % (cycles[i], retries_list[0][i], retries_list[1][i]))
				elif noOfFlows == 3:  
					f.write('%d \t%f \t%f \t%f \n' % (cycles[i], retries_list[0][i], retries_list[1][i],retries_list[2][i]))
				else :  
					f.write('%d \t%f \t%f \t%f \t%f\n' % (cycles[i], retries_list[0][i], retries_list[1][i],retries_list[2][i],retries_list[3][i]))
                plot = "gnuplot -e " + "\"inFilename='" + filename +"';"+ "outFilename='" + filename + ".png';yLabel='droppedMacRetries'\"" + " " + "plotGraph.gp"      
		from os import system
		system(plot)



	elif value == 'traffic_char':
		pktRatio_list = []

		elemName      = 'pktSent'  
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		noPktSent    = getCumulativeAverage(avgCycle)

		elemName      = 'pktRecived'  
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		noPktRecived      = getCumulativeAverage(avgCycle)

		elemName      = 'sixtop_cell_reservation_request'
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		no6topRequest = getCumulativeAverage(avgCycle)

		elemName      = 'sixtop_cell_reservation_response'
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		no6topResponse = getCumulativeAverage(avgCycle)

		elemName      = 'rplTxDIO'  
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		noTxDio     = getCumulativeAverage(avgCycle)

		elemName      = 'rplRxDIO' 
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		noRxDio       = getCumulativeAverage(avgCycle)

		elemName      = 'updatePDRStatus'  
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		noPCERecived  = getCumulativeAverage(avgCycle)

		'''
		elemName      = 'updatePktStatus' 
		valPerCycle   = getValuesPerCycle(infilepath, elemName)
		avgCycle      = getAverageOfCycle(valPerCycle)
		noPceSent     = getCumulativeAverage(avgCycle)
	        '''	
                control =[a + b + c + d + e  for a,b,c,d,e in zip(noPCERecived,noRxDio, noTxDio,no6topResponse,no6topRequest)]
                  
                total   = [a + b + c  for a,b,c  in zip(control,noPktSent,noPktRecived)]
                #import pdb;pdb.set_trace();
		pktRatio = calculatePktRatio(control,total)
		pktRatio_list.append(pktRatio)
       	        filename = outfilepath +"_trafficChar"	  
		with open(filename,'w') as f:
			for i in range(noOfCycles-1):
            			f.write('%d \t%f\n' % (cycles[i],  pktRatio_list[0][i]))
                plot = "gnuplot -e " + "\"inFilename='" + filename +"';"+ "outFilename='" + filename + ".png';yLabel='pktRatio'\"" + " " + "plotGraph.gp"      
		from os import system
		system(plot)

def getNoCycles(infilepath):
	with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('## '):
                	m = re.search('numCyclesPerRun\s+=\s+([\.0-9]+)',line)
                        if m:
                            return int(m.group(1))

def getNoFlows(infilepath):
	with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('## '):
                	m = re.search('numFlows\s+=\s+([\.0-9]+)',line)
                        if m:
                            return int(m.group(1))
			
def isDelayConstraintEnabled(infilepath):
  	enabled = False
	with open(infilepath,'r') as f:
            for line in f:
                if line.startswith('## '):
                	m = re.search('isDelayConstraint\s+=\s+True',line)
                        if m:
			    enabled = True
                            return enabled
			
def main():
    inputFiles = [] 
    inputFiles =  binDataFiles()
	#if len(sys.argv) != 3:
	#	print 'Format: parse_data <inFileName> <outFileName>'
	#	exit(0)
    for filepath in inputFiles:
        infilepath = filepath
        lefttMost = filepath.replace(DATADIR,'',1)       
        outfilename = lefttMost.replace('output.dat','',1)
       
        outfilename = outfilename.replace('/','',2)
	dirname = 'parseResults'
	if not os.path.exists(dirname):
            os.makedirs(dirname)

	outfilepath = os.path.join(dirname, outfilename)

	global noOfCycles
	global noOfFlows

	noOfCycles = getNoCycles(infilepath)
	noOfFlows   = getNoFlows(infilepath)

	getData('pdr', infilepath, outfilepath)	
	getData('numTxCells', infilepath, outfilepath)	
	getData('droppedMacRetries', infilepath, outfilepath)	
	getData('aveLatency', infilepath, outfilepath)	
        getData('traffic_char',infilepath,outfilepath)
       
	if isDelayConstraintEnabled(infilepath):
		getData('droppedDelayExceed', infilepath, outfilepath)	


#-----------------------------------------------------------------------#
#Read data files ::Lavanya
#----------------------------------------------------------------------#

def binDataFiles():
    '''
    bin the data files according to the otfThreshold and pkPeriod.
    
    Returns a dictionary of format:
    {
        (otfThreshold,pkPeriod): [
            filepath,
            filepath,
            filepath,
        ]
    }
    '''
    infilepaths    = glob.glob(os.path.join(DATADIR,'**','*.dat'))
    
    dataBins       = {}
    for infilepath in infilepaths:
        with open(infilepath,'r') as f:
            for line in f:
                if not line.startswith('## ') or not line.strip():
                    continue
                # otfThreshold
                m = re.search('otfThreshold\s+=\s+([\.0-9]+)',line)
                if m:
                    otfThreshold = float(m.group(1))
                # pkPeriod
                m = re.search('pkPeriod\s+=\s+([\.0-9]+)',line)
                if m:
                    pkPeriod     = float(m.group(1))
               # else:
                #    pkPeriod     = 'NA'
            if (otfThreshold,pkPeriod) not in dataBins:
                dataBins[(otfThreshold,pkPeriod)] = []
            dataBins[(otfThreshold,pkPeriod)] += [infilepath]
    
    inputFiles  = []
    for ((otfThreshold,pkPeriod),filepaths) in dataBins.items():
       # output         += ['otfThreshold={0} pkPeriod={1}'.format(otfThreshold,pkPeriod)]
        for f in filepaths:
            #output     += ['   {0}'.format(f)]
             inputFiles.append(f)
    #inputFiles  = ','.join(inputFiles)
    return inputFiles    

def plotgragh():
 
    fig = matplotlib.pyplot.figure()
    matplotlib.pyplot.ylim(ymin=ymin,ymax=ymax)
    matplotlib.pyplot.xlabel('Time in Cycles')
    matplotlib.pyplot.ylabel(ylabel)
    for period in pkPeriods:
        
        d = {}
        for ((otfThreshold,pkPeriod),data) in plotData.items():
            if pkPeriod==period:
                d[otfThreshold] = data
        x     = d[otfThreshold]['x']
        y     = d[otfThreshold]['y']
        yerr  = d[otfThreshold]['yerr']
        
        matplotlib.pyplot.errorbar(
            x        = x,
            y        = y,
            yerr     = yerr,
            color    = COLORS_PERIOD[period*100],
            ls       = LINESTYLE_PERIOD[period*100],
            ecolor   = ECOLORS_PERIOD[period*100],
            label    = 'packet period {0}s'.format(period)
        )
    matplotlib.pyplot.legend(prop={'size':10})
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'{0}.png'.format(filename)))
    matplotlib.pyplot.savefig(os.path.join(DATADIR,'{0}.eps'.format(filename)))



           
if __name__=="__main__":
    main()
