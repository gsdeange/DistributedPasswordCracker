from itertools import product
import ray


def getDictionary(filename):
  with open(filename) as f:
    lines = f.read().splitlines()
  return list(set(lines))

#original simple dictionary attack, not used but here for reference
def dictAttack(password, dictionary):
  for i in range(len(dictionary)):
    if(dictionary[i] == password):
      print("password found: ", dictionary[i])
      pass

"""modified attack to include multiple words
Can be done with either combinations or permutations, permuations generates more possibilities"""
def dictAttack2(password, dictionary, numCombos):
  for i in range(1, numCombos):
    for attempt in product(dictionary, repeat = i):
      guess = ''.join(attempt)
      #print(guess)
      #print(guess, end='\r')
      if(guess == password):
        print("password found: ", guess)
        return guess


@ray.remote
def dictAttackSegment(password, segment, dictionary, numCombos):
   guess = ""
   for word in segment:
      #print("segment word: ", word)
      if(word == password):
         #print("password found: ", word)
         return word
      else:
         for i in range(1, numCombos):
            for attempt in product(dictionary, repeat = i):
               guess = word+ ''.join(attempt)
               #print(" guess: ", guess)
               if(guess == password):
                  #print("password found: ", guess)
                  return guess
   return None

def dictAttackDistributed(password, dictionary, numCores, numCombos):
   result_ids = []
   passwords = []
   increment = int(len(dictionary)/numCores)
   lower = 0
   upper = int(len(dictionary)/numCores)
   for core in range(numCores):
      lower = (core*increment)
      upper = ((core+1)*increment)-1
      #print("lower: ", lower, " upper: ", upper)
      result_ids.append(dictAttackSegment.remote(password, dictionary[lower:upper], dictionary, numCombos))
      
   for attempt in ray.get(result_ids):
      if attempt is not None:
         print("password found: ", attempt)
      passwords.append(attempt)
      
   #print("Possible Passwords: ", passwords)







  
      


      