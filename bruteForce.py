from itertools import product
import ray
import time

#input: password, pwdLength, alphabet
#output: returns cracked password
def bruteForce(password, pwdLength, alphabet):
  startTime = time.time()
  resultTime = 0
  for i in range(pwdLength+1):
    for attempt in product(alphabet, repeat=i):
      if(''.join(attempt) == password):
        resultTime = time.time() - startTime
  return resultTime

@ray.remote
def bruteForceDistributedHelper(start, end, pw, pwLen, alphabet):
    i = start
    startTime = time.time()
    while i < end:
        for j in range(pwLen):
            for attempt in product(alphabet, repeat=j):
                if(alphabet[i]+''.join(attempt) == pw):
                    return time.time() - startTime
        i += 1
    return -1

def bruteForceDistributed(password, pwdLength, alphabet, cores):
    space = len(alphabet)//cores
    result_ids = []
    for i in range(cores):
        if (i+1) == cores:
            result_ids.append(bruteForceDistributedHelper.remote(i*space, len(alphabet), password, pwdLength, alphabet))
        else:
            result_ids.append(bruteForceDistributedHelper.remote(i*space, (i*space)+space, password, pwdLength, alphabet))
    ray.wait(result_ids)

    for timer in ray.get(result_ids):
      print(timer)
