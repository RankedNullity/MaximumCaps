import numpy as np 
import os
import os.path as path
import pickle
import sys
'''
Python file for recursively finding maximum d-caps in F_q^n

'''

def generate_basis(n, index):
    arr = np.zeros(n, dtype = int)
    arr[index] = 1
    return arr

def index_to_vector(n, q, index):
    vec = np.zeros(n, dtype=int)
    for i in range(n):
        vec[n - 1 - i] = index // (q ** (i)) % q
    return vec

def vector_to_index(vector, n, q):
    '''Takes the vector and converts it to the unique index under F_{fieldsize}^{n}'''
    assert(n == len(vector))
    index = 0
    for i in range(0, n):
        index += vector[n - 1 - i] * (q ** i)
    return index

def add_nocuda(q, *args):
    #print("args: {}".format(args))
    #print("summing along axis 0: {}".format(np.mod(np.sum(np.array(args), axis=0),q)))
    return np.mod(np.sum(np.array(args), axis=0),q)

n = 3 if len(sys.argv) < 3 else int(sys.argv[2])
q = 3 if len(sys.argv) < 3 else int(sys.argv[1])
cache = [None] * (q ** n)

if not __debug__:
    debug_file = os.getcwd() + "\\results\\" + str(q) + "_" + str(n) +"_debug.txt"
    debug_log = open(debug_file, 'w+')    

def cap_isLinear(cap, n, q):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            #Assume that the list was a cap before adding a new element. Therefore, only need to check that last element is not a cap. 
            if not add_nocuda(q, cap[i], cap[j], cap[len(cap) - 1]).any():
                return True
    return False

def cap_isPlanar(cap, n, q):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            for k in range(j + 1, len(cap) - 1):
                if not add_nocuda(q, cap[i], cap[j], -cap[k], -cap[-1]).any():
                    return True
    return False

''' Generalized method for checking if the cap is a q-flat. Very slow'''
def is_q_flat(cap, n, q):
    pass 

def find_verifier(d):
    if d==1:
        return cap_isLinear
    elif d==2:
        return cap_isPlanar
    else:
        return


def fill_initial_set(cap, set, n, q):
    '''Mutates set to be the accurate hashset for the given cap.'''
    for vec in cap:
        index= vector_to_index(vec, n, q)
        set[index] = True
    return set

def update_validset(cap, validset, d, n, q):
    # TODO: Find general way given d, n, and q
    # returns an array of changes, TRUE if (validset[i+1] == False and validset[i] == True)
    return 

def remove_changes(validset, changeset):
    return [True if not v and c else False for v, c in zip(validset, changeset)]

# Change hashset to be index - > (whether or not that index is valid)

def find_maximum_cap(n, q, d=1, current_cap= [np.zeros(n, dtype=int)], current_index=1, illegal_check=cap_isLinear, 
                    hashset=None):
    '''n = size of vector
        q = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    #print(current_cap)
    if len(current_cap) > q - 1 and illegal_check(current_cap, n, q): 
        if not __debug__:
            debug_log.write("{}\n".format(current_cap))
        return current_cap[:-1]

    maximum_cap = []
    global cache

    for i in range(current_index, q ** n):
        if cache[i] is None:
            current_vec = index_to_vector(n, q, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]

        #print("Current cap before: {}".format(current_cap))
        if not hashset[i]:
            current_cap.append(current_vec)
            hashset[i] = True
            #print("Current cap: {}".format(current_cap))
            maximal_cap = find_maximum_cap(n, q, d, current_cap.copy(), i + 1, hashset=hashset)
            hashset[i] = False
            current_cap.pop()
        else:
            maximal_cap = current_cap

        if len(maximal_cap) > len(maximum_cap):
            maximum_cap = maximal_cap
    return maximum_cap

EMPTY_HASHSET = [False] * (q ** n)

if not __debug__:
    print("Generating debug results")
    if n > 1:
        initial_cap = [np.zeros(n, dtype=int), generate_basis(n,0), generate_basis(n, 1)]
    else:
        initial_cap = [np.zeros(n, dtype=int)]
    starter_hashset = fill_initial_set(initial_cap, EMPTY_HASHSET, n, q)
    maximum_cap = find_maximum_cap(n, q, current_cap=initial_cap, hashset= starter_hashset)
    debug_log.close()   
else:
    previous_sol = os.getcwd() + "\\results\\" + str(q) + "_" + str(n - 1) + ".dat"
    current_sol = os.getcwd() + "\\results\\" + str(q) + "_" + str(n) + ".dat"
    if path.exists(current_sol):
        print("Solution previously found.")
        with open(current_sol, 'rb') as f:
            maximum_cap = pickle.load(f)
    else:
        if path.exists(previous_sol):
            print("Continuing search using lower dimensional embedded cap")
            with open(previous_sol, 'rb') as f:
                initial_cap = pickle.load(f)
            for i, vec in enumerate(initial_cap):
                initial_cap[i] = np.concatenate((vec, np.zeros(1)), axis = None)
        elif n > 1:
            initial_cap = [np.zeros(n, dtype=int), generate_basis(n,0), generate_basis(n, 1)]
        else:
            initial_cap = [np.zeros(n, dtype=int)]

        starter_hashset = fill_initial_set(initial_cap, EMPTY_HASHSET, n, q)
        maximum_cap = find_maximum_cap(n, q, current_cap=initial_cap, hashset= starter_hashset)

        with open(os.getcwd() + "\\results\\" + str(q) + "_" + str(n) + ".dat", "wb") as file:
            pickle.dump(maximum_cap, file)

response = "A maximum cap for d = {}, F = {}, has size {} and is: {}".format(n, q, len(maximum_cap), maximum_cap)
print(response)


## TODO FOR CODE
# Decide between parallelizing depth+1 check vs. removing all invalid points
    # Removing all the invalid points is faster when I can split the calculations of the points into different processes.
    # To remove all the invalid points, I need to find a indexing of the points on the d-dimensional flat which is constructed by an arbitrary (d+1) points