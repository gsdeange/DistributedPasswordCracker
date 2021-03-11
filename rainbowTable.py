import hashlib 
import ray
import math
import time
import os
 
#################################################################################################
#globals
 
columnLength = 1 # Using lengh of 1 for quick results. In reality, it would be a lentgh around 10,000
 
################################################################################################
 
# Only using getSha1 for quicker results. Does not represent real world
def getSha1(word):
    result = hashlib.sha1(word.encode()).hexdigest()
    return result
 
def getSha224(word):
    result = hashlib.sha224(word.encode()).hexdigest()
    return result
 
def getSha256(word):
    result = hashlib.sha256(word.encode()).hexdigest()
    return result 
 
def getSha384(word):
    result = hashlib.sha384(word.encode()).hexdigest()
    return result
 
def getSha512(word):
    result = hashlib.sha512(word.encode()).hexdigest()
    return result
 
def getMd5(word):
    result = hashlib.md5(word.encode()).hexdigest()
    return result 
 
################################################################################################
 
def generateBytes(hashValue):
    results = []
    remaining = int(hashValue, 16)
    while remaining > 0:
        results.append(remaining % 256)
        remaining //= 256
    return results
 
def reduce(hashValue, column, passwordLength, validChars):
    results = ""
    hashBytes = generateBytes(hashValue)
    for i in range(passwordLength):
        index = hashBytes[(i + column) % len(hashBytes)]
        newCharacter = validChars[index % len(validChars)]
        results += newCharacter
    return results
 
def generateChain(password, columns, hashFunc, validChars):
    for column in range(columns):
        hashValue = hashFunc(password)
        password = reduce(hashValue, column, len(password), validChars)
    return hashValue
 
##################################################################################
 
def generateFinalHash(startHash, startColumn, passwordLength, columns, hashFunc, validChars):
    hashValue = startHash
    for col in range(startColumn, columns - 1):
        hashValue = hashFunc(reduce(hashValue, col, passwordLength, validChars))
    return hashValue
 
def validatePassword(startPassword, startHash, hashFunc, validChars):
    hashValue = hashFunc(startPassword)
 
    if hashValue == startHash:
        return startPassword
    column = 0
    password = startPassword
 
    while column < columnLength:
        password = reduce(hashValue, column, len(password), validChars)
        hashValue = hashFunc(password)
        if hashValue == startHash:
            return password
        column += 1
    return None
##########################################################################
def compareHash(hashValue):
    result = []
    with open('tempChains') as f:
        for chain_pwd in f:
            chain_pwd = chain_pwd.strip().split(',', 1)
            if chain_pwd[0] == hashValue:
                result.append(chain_pwd[1])
    return result
 
def crackHash(startHash, hashFunc, validChars, passwordLength):
    startTime = time.time()
    for col in range(columnLength, -1, -1):
        hashValue = generateFinalHash(startHash, col, passwordLength, columnLength, hashFunc, validChars)
        possible = compareHash(hashValue)
        for password in possible:
            # Check to make sure the password is the real password
            resultPassword = validatePassword(password, startHash, hashFunc, validChars)
            if resultPassword != None:
                return time.time() - startTime
    return -1
 
################################################################################################
################################################################################################
################################################################################################
def generatePasswords(passwordLength, validChars):
    f = open('tempPwd', 'w')
    charCount = len(validChars)
    for i in range(charCount**passwordLength):
        word = ""
        for j in range(passwordLength):
            word = validChars[i % charCount] + word
            i //= charCount
        f.write(word + '\n')
    f.close()
 
def generateChainFiles(hashFunc, validChars):
    f = open('tempPwd', 'r')
    chainFile = open('tempChains', 'w')
    for word in f.readlines():
        hashValue = generateChain(word.strip(), columnLength, hashFunc, validChars)
        chainFile.write(str(hashValue) + ',' + word)
    f.close()
 
def generateRainbowTable(pwdLen, validChars, hashFunc):
    # Start timeing creation of password permutations
    start = time.time()
    generatePasswords(pwdLen, validChars)
    genTime = time.time()- start
    print("Generated Password List in :", genTime, 'seconds')
    time.sleep(0.1)
 
    # Start timing chain creation
    start = time.time()
    generateChainFiles(hashFunc, validChars)
    chainTime = time.time() - start
    print("Generated Chain List in :", chainTime, 'seconds')
    time.sleep(0.1)
    return genTime + chainTime
 
################################################################################################
################################################################################################
#DISTRIBUTED FUNCTIONS
################################################################################################
################################################################################################
@ray.remote
def generatePasswordsDis(passwordLength, startChars, validChars, fileNo=0):
    f = open('tempPwd' + str(passwordLength) + '-' + str(fileNo), 'w')
    charCount = len(validChars)
 
    for startChar in startChars:
        for i in range(charCount**(passwordLength-1)):
            subWord = ""
            for j in range(passwordLength-1):
                subWord = validChars[i % charCount] + subWord
                i //= charCount
            f.write(startChar + subWord + '\n')
    f.close()
 
def generatePwdListDis(passwordLength, validChars, coreCount):
    tempFiles = []
    results_ids = []
    splitLen = math.ceil(len(validChars) // coreCount)
    startCharIndex = 0
    endCharIndex = splitLen
    startTime = time.time()
 
    # Split into cores - 1 processes
    for i in range(coreCount - 1):
        tempFiles.append('tempPwd' + str(passwordLength) + '-' + str(i))
        startChars = validChars[startCharIndex:endCharIndex]
        startCharIndex = endCharIndex
        endCharIndex = endCharIndex + splitLen
        results_ids.append(generatePasswordsDis.remote(passwordLength, startChars, validChars, i))
 
    # The last core will work with a smaller dataset if set cant be split evenly
    tempFiles.append('tempPwd' + str(passwordLength) + '-' + str(i))
    startCharIndex = endCharIndex
    startChars = validChars[startCharIndex:len(validChars)]
    results_ids.append(generatePasswordsDis.remote(passwordLength, startChars, validChars, i + 1))
 
    # Needs to Wait
    ray.wait(results_ids)
    return time.time() - startTime
################################################################################################
 
@ray.remote
def generateChainsDis(pwdFile, hashFunc, validChars, fileNo, pwdLen):
    f = open(pwdFile, 'r')
    chainFile = open('tempChain' + str(pwdLen) + '-' + str(fileNo), 'w')
 
    for word in f.readlines():
        hashValue = generateChain(word.strip(), columnLength, hashFunc, validChars)
        chainFile.write(str(hashValue) + ',' + word)
    f.close()
    chainFile.close()
 
def generateChainList(hashFunc, validChars, coreCount, pwdLen):
    results_ids = []
    for i in range(coreCount):
        results_ids.append(generateChainsDis.remote('tempPwd' + str(pwdLen) + '-' + str(i), hashFunc, validChars, i, pwdLen))
    ray.wait(results_ids)
 
def generateRainbowTableDis(pwdLen, validChars, hashFunc, coreCount):
    # Start timeing creation of password permutations
    start = time.time()
    for i in range(pwdLen):
        generatePwdListDis(i + 1, validChars, coreCount)
    tableTime = time.time() - start
    print("Generated Password List in :", tableTime, 'seconds')
    time.sleep(0.1)
 
    # Start timing chain creation
    start = time.time()
    for i in range(pwdLen):
        generateChainList(hashFunc, validChars, coreCount, i + 1)
    chainTime = time.time() - start
    print("Generated Chain List in :", chainTime, 'seconds')
    time.sleep(0.1)
    return chainTime + tableTime
 
################################################################################################
@ray.remote
def compareHashDis(hashValue, chainFiles):
    result = []
    for fileName in chainFiles:
        with open(fileName) as f:
            for chain_pwd in f:
                chain_pwd = chain_pwd.strip().split(',', 1)
                if chain_pwd[0] == hashValue:
                    result.append(chain_pwd[1])
    return result
 
def crackHashDis(startHash, hashFunc, validChars, passwordLength, coreCount):
    results_ids = []
    chainFiles = []
 
    for (dirpath, dirnames, filenames) in os.walk('./'):
        for fileName in filenames:
            if 'tempChain' in fileName:
                chainFiles.append(fileName)
 
    splitLen = len(chainFiles) // coreCount
    firstFile = 0
    lastFile = splitLen
    startTime = time.time()
 
    for column in range(columnLength, -1, -1):
        hashValue = generateFinalHash(startHash, column, passwordLength, columnLength, hashFunc, validChars)
        for i in range(coreCount):
            results_ids.append(compareHashDis.remote(hashValue, chainFiles[firstFile:lastFile]))
            firstFile = lastFile
            lastFile = lastFile + splitLen
        ray.wait(results_ids)
        for possible in ray.get(results_ids):
            for password in possible:
                resultPassword = validatePassword(password, startHash, hashFunc, validChars)
                if resultPassword != None:
                    return time.time() - startTime
    return -1