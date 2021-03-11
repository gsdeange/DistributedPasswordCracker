#!/bin/bash
echo "Running the dictionaryAttacks"

#clear the dictAttack results file
> dictAttackResults.txt

#specify the number of cores to run
numCores=4
#specify the password length (numCombos)
passLength=2

#OUTSIDE loop - Core counts (1-12 cores)
for (( cores=1; cores<=$numCores; cores++ ))
do
#echo "Running dictionaryAttack with core count: $counter " > dictAttackResults.txt

#INSIDE loop - Password length:
for (( length=1; length<=$passLength; length++ ))
do 
echo " ------- Running Dict attack with $cores cores and password length: $length -------- " >> dictAttackResults.txt

python3 main.py dict $length $cores >> dictAttackResults.txt

echo "\n\n"

done
done

#python3 dictAttack.py
echo "finished... outputted results in dictAttackResults.txt"