#!/bin/bash
echo "Running the brute force attacks"

#clear the brute Attack results file
> bruteAttackResults.txt

#specify the number of cores to run
numCores=4
#specify the password length (12-16 maybe?)
passLength=2

#OUTSIDE loop - Core counts (1-12 cores)
for (( cores=1; cores<=$numCores; cores++ ))
do

#INSIDE loop - Password length:
for (( length=1; length<=$passLength; length++ ))
do 
echo " ------- Running Brute Force attack with $cores cores and password length: $length -------- " >> bruteAttackResults.txt

python3 main.py brute $length allChars $cores >> bruteAttackResults.txt

echo "\n\n"

done
done

#python3 dictAttack.py
echo "finished... outputted results in bruteAttackResults.txt"