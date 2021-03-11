import time
import sys
import os
from random import randrange, randint
import bruteForce
import dictAttack
import rainbowTable
import ray
import multiprocessing
import csv


word_list = dictAttack.getDictionary('dicWords.txt')
word_list = ['hello', 'world', 'SQL', 'NOSQL', 'Sun', 'Moon']
word_list = dictAttack.getDictionary('commonPasswords.txt')

lower = "abcdefghijklmnopqrstuvwxyz"
upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
numbers = "0123456789"
specials = '~!@#$%^&*()_+[{]};"<>?,./-='

alpha = lower + upper
alphaNumeric = lower + upper + numbers
allChars = lower + upper + numbers + specials

inputAlpha = {"lower" : lower, "upper" : upper, "numbers" : numbers,"specials" :  specials, "alpha" : alpha, "alphaNumeric" : alphaNumeric, "allChars" : allChars,}

def printError(specific=None):
  print("Usage: main.py attack method <password length> <alphabet> <core-count>")
  if specific:
    print("ERROR -", specific)
  sys.exit(1)

def validateInput(argv):
  cores = 1
  if len(sys.argv) == 1:
    printError()
  if argv[1] == "dict":
    if len(sys.argv) != 4:
      printError("[dict] <password length> <core-count>")
    elif not argv[2].isdigit():
      printError("password length (number of words) must be an integer")
    elif not argv[3].isdigit():
      printError("core parameter needs to be a digit between 1 and the number of system cores/threads")
    elif (int(argv[3]) > multiprocessing.cpu_count()):
      printError("core input is greater than number of system core/threads")
    cores = argv[3]
    return cores
  elif(len(sys.argv) != 5):
      printError("incorrect number of inputs")
  if not argv[4].isdigit():
      printError("core parameter needs to be a digit between 1 and the number of system cores/threads")
  elif argv[1] not in ["brute","dict","rainbow"]:
    printError("avaliable attack methods: [brute, dict, rainbow]")
  elif (not argv[2].isdigit()) or (int(argv[2])<1 or int(argv[2])>64):
    printError("password length must be an integer between 1 and 64")
  elif (argv[3] not in inputAlpha):
    printError("avaliable alphabets: [lower, upper, numbers, specials, alpha, alphaNumeric, allChars]")
  elif (int(argv[4]) > multiprocessing.cpu_count()):
    printError("core input is greater than number of system core/threads")
  cores = argv[4]
  return cores

def randomPassword(pwdLength, validChars):
    pwd = ""
    charsLength = len(validChars)
    for i in range(pwdLength):
        pwd += validChars[randrange(charsLength)]
    return pwd

def randomDictPassword(wordNum):
  password = ""
  wordList = [word for line in open("commonPasswords.txt", 'r') for word in line.split()]
  for i in range(wordNum):
    password += wordList[randint(0, len(wordList) - 1)]
  return password




def main(argv):
  writeHeader = False
  cores = int(validateInput(argv))
  if cores > 1:
    ray.init(num_cpus=cores)
  method = sys.argv[1]
  

  if method == "dict":
    numCombos = int(sys.argv[2])
    dictpassword = randomDictPassword(numCombos)
    print("Generated password:", dictpassword)
    start = time.time()
    if ray.is_initialized():
      dictAttack.dictAttackDistributed(dictpassword, word_list, cores, numCombos)
    else:
      dictAttack.dictAttack2(dictpassword, word_list, numCombos)
    resultTime = time.time()-start
    print("Cracked password:", resultTime, "seconds")
    
    #### OUTPUT TO CSV FILE ####
    if not os.path.isfile('dictResult.csv'):
      writeHeader = True
    with open('dictResult.csv', 'a') as file:
      writer = csv.writer(file)
      if writeHeader:
        writer.writerow(['Core', 'Number of Combos', 'Time(s)'])  # file doesn't exist yet, write a header
      writer.writerow([cores, numCombos, resultTime])

  else:
    pwdLength = int(sys.argv[2])
    alphabet = inputAlpha[sys.argv[3]]
    password = randomPassword(pwdLength, alphabet)
    print("Generated password:", password)

    if method == "brute":
      start = time.time()
      if ray.is_initialized():
        crackedTime = bruteForce.bruteForceDistributed(password, pwdLength, alphabet, cores)
      else:
        crackedTime = bruteForce.bruteForce(password, pwdLength, alphabet)
      worstTime = time.time()-start
      print("Cracked password:", crackedTime, "seconds")
      print("Worst Case:", worstTime, "seconds")


      #### OUTPUT TO CSV FILE ####
      if not os.path.isfile('bruteResult.csv'):
        writeHeader = True

      with open('bruteResult.csv', 'a') as file:
        writer = csv.writer(file)
        if writeHeader:
          writer.writerow(['Core', 'Password Length', 'Cracked Time(s), Worst Time(s)'])  # file doesn't exist yet, write a header
        writer.writerow([cores, pwdLength, crackedTime, worstTime])
    
    elif method == "rainbow":
      startHash = rainbowTable.getSha1(password)
      if ray.is_initialized():
        rainbowTable.generateRainbowTableDis(pwdLength, alphabet, rainbowTable.getSha1, cores)
        start = time.time()
        for i in range(pwdLength):
          rainbowTable.crackHashDis(startHash, rainbowTable.getSha1, alphabet, i + 1, cores)
      else:
        rainbowTable.generateRainbowTable(pwdLength, alphabet, rainbowTable.getSha1)
        start = time.time()
        for i in range(pwdLength):
          rainbowTable.crackHash(startHash, rainbowTable.getSha1, alphabet, i + 1)
      resultTime = time.time() - start
      print("Cracked password:", resultTime, "seconds")

      #### OUTPUT TO CSV FILE ####
      if not os.path.isfile('rainbowResult.csv'):
        writeHeader = True
      with open('rainbowResult.csv', 'a') as file:
        writer = csv.writer(file)
        if writeHeader:
          writer.writerow(['Core', 'Password Length', 'Time(s)'])  # file doesn't exist yet, write a header
        writer.writerow([cores, pwdLength, resultTime])
      os.system('rm temp*')

  ray.shutdown()
if __name__ == "__main__":
  main(sys.argv)