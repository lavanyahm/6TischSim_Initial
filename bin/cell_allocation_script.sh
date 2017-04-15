
cp schedules_block.csv schedules.csv

python runSimOneCPU.py --numFlows 2 --deadLineFlow1 15 --deadLineFlow2 15 --pkPeriod 0.15  --isDelayConstraint --numRuns 100 --enableCellAllocation
python runSimOneCPU.py --numFlows 2 --deadLineFlow1 20 --deadLineFlow2 20 --pkPeriod 0.2  --isDelayConstraint --numRuns 100 --enableCellAllocation
python runSimOneCPU.py --numFlows 2 --deadLineFlow1 30 --deadLineFlow2 30 --pkPeriod 0.3  --isDelayConstraint --numRuns 100 --enableCellAllocation
sleep 1
python parse_data.py

DATE=`date +%F_%H%M%S`
directory_name="cell_allocation_block_$DATE"
if [ ! -d "$DIRECTORY" ]; then
# Control will enter here if $DIRECTORY doesn't exist.
	mkdir $directory_name/
	mv  simData $directory_name/
	mv  runSim.log* $directory_name/
	mv  parseResults $directory_name/
else 
	echo "Connot Create Directry...Directry Exits!!!!   "
	exit
fi	

sleep 2
cp schedules_alternate.csv schedules.csv

sleep 1
python runSimOneCPU.py --numFlows 2 --deadLineFlow1 15 --deadLineFlow2 15 --pkPeriod 0.15  --isDelayConstraint --numRuns 100 --enableCellAllocation
python runSimOneCPU.py --numFlows 2 --deadLineFlow1 20 --deadLineFlow2 20 --pkPeriod 0.2  --isDelayConstraint --numRuns 100 --enableCellAllocation
python runSimOneCPU.py --numFlows 2 --deadLineFlow1 30 --deadLineFlow2 30 --pkPeriod 0.3  --isDelayConstraint --numRuns 100 --enableCellAllocation
sleep 1
python parse_data.py

DATE=`date +%F_%H%M%S`
directory_name="cell_allocation_alternate_$DATE"
if [ ! -d "$DIRECTORY" ]; then
# Control will enter here if $DIRECTORY doesn't exist.
	mkdir $directory_name/
	mv  simData $directory_name/
	mv  runSim.log* $directory_name/
	mv  parseResults $directory_name/
else 
	echo "Connot Create Directry...Directry Exits!!!!   "
	exit
fi	

