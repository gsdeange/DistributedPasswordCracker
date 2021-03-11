#!/bin/bash
echo "Running the Rainbow Table Attacks"

#clear the rainbow table results file
> rainbowAttackResults.txt

#specify the number of cores to run
numCores=4
#specify the password length
passLength=2

#OUTSIDE loop - Core counts (1-12 cores)
for (( cores=1; cores<=$numCores; cores++ ))
do

#INSIDE loop - Password length:
for (( length=1; length<=$passLength; length++ ))
do 
echo " ------- Running Rainbow Table attack with $cores cores and password length: $length -------- " >> rainbowAttackResults.txt

python3 main.py rainbow $length allChars $cores >> rainbowAttackResults.txt

echo "\n\n"

done
done

#python3 dictAttack.py
echo "finished... outputted results in rainbowAttackResults.txt"