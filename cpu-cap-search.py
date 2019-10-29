import numpy as np 
import os
from itertools import combinations
import os.path as path
import pickle
import sys
'''
Python file for recursively finding maximum d-caps in F_q^n

'''

def generate_basis(dim, index):
    arr = np.zeros(dim, dtype = int)
    arr[index] = 1
    return arr

def generate_vector(dim, field_size, index):
    vec = np.zeros(dim, dtype=int)
    for i in range(dim):
        vec[dim - 1 - i] = index // (field_size ** (i)) % field_size
    return vec

def add_nocuda(field_size, *args):
    #print("args: {}".format(args))
    #print("summing along axis 0: {}".format(np.mod(np.sum(np.array(args), axis=0),field_size)))
    return np.mod(np.sum(np.array(args), axis=0),field_size)

dim = 3 if len(sys.argv) < 3 else int(sys.argv[2])
field_size = 3 if len(sys.argv) < 3 else int(sys.argv[1])
cache = [None] * (field_size ** dim)

if not __debug__:
    debug_file = os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) +"_debug.txt"
    debug_log = open(debug_file, 'w+')
    

def cap_isLinear(cap, dim, field_size):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            #Assume that the list was a cap before adding a new element. Therefore, only need to check that last element is not a cap. 
            if not add_nocuda(field_size, cap[i], cap[j], cap[len(cap) - 1]).any():
                return True
    return False

def cap_isPlanar(cap, dim, field_size):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            for k in range(j + 1, len(cap) - 1):
                if not add_nocuda(field_size, cap[i], cap[j], -cap[k], -cap[-1]).any():
                    return True
    return False

''' Generalized method for checking if the cap is a q-flat. Very slow'''
def is_q_flat(cap, dim, field_size):
    pass 

def find_verifier(d):
    if d==1:
        return cap_isLinear
    elif d==2:
        return cap_isPlanar
    else:
        return

def convert_to_index(vector, dim, field_size):
    assert(dim == len(vector))
    index = 0
    for i in range(0, dim):
        index += vector[dim - 1 - i] * (field_size ** i)
    return index

def fill_initial_set(cap, set, dim, field_size):
    for vec in cap:
        index= convert_to_index(vec, dim, field_size)
        set[index] = True
    return set


# TODO: Replace current cap with a hashset so the check is cheaper and duplicates are avoided.
def find_maximum_cap(dim, field_size, d=1, current_cap= [np.zeros(dim, dtype=int)], current_index=1, illegal_check=cap_isLinear, 
                    hashset=None):
    '''dim = size of vector
        field_size = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    #print(current_cap)
    if len(current_cap) > field_size - 1 and illegal_check(current_cap, dim, field_size): 
        if not __debug__:
            debug_log.write("{}\n".format(current_cap))
        return current_cap[:-1]

    maximum_cap = []
    global cache

    for i in range(current_index, field_size ** dim):
        if cache[i] is None:
            current_vec = generate_vector(dim, field_size, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]

        #print("Current cap before: {}".format(current_cap))
        if not hashset[i]:
            current_cap.append(current_vec)
            hashset[i] = True
            #print("Current cap: {}".format(current_cap))
            #print("current sum: {}".format(current_sum))
            maximal_cap = find_maximum_cap(dim, field_size, d, current_cap.copy(), i + 1, hashset=hashset)
            hashset[i] = False
            current_cap.pop()
        else:
            maximal_cap = current_cap

        if len(maximal_cap) > len(maximum_cap):
            maximum_cap = maximal_cap
    return maximum_cap

EMPTY_HASHSET = [False] * (field_size ** dim)

if not __debug__:
    print("Generating debug logs")
    if dim > 1:
        initial_cap = [np.zeros(dim, dtype=int), generate_basis(dim,0), generate_basis(dim, 1)]
        maximum_cap = find_maximum_cap(dim, field_size, current_cap= initial_cap, current_index=2, hashset=fill_initial_set(initial_cap, EMPTY_HASHSET, dim, field_size))
    else:
        initial_cap = [np.zeros(dim, dtype=int)]
        maximum_cap = find_maximum_cap(dim, field_size, current_cap=initial_cap, hashset= fill_initial_set(initial_cap, EMPTY_HASHSET, dim, field_size))

    debug_log.close()   
else:
    previous_sol =  os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim - 1) + ".dat"
    current_sol = os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) + ".dat"
    if path.exists(current_sol):
        print("Solution previously found.")
        with open(current_sol, 'rb') as f:
            maximum_cap = pickle.load(f)
    else:
        if path.exists(previous_sol):
            print("Continuing search using lower dimensional embedded cap")
            with open(previous_sol, 'rb') as f:
                previous_sol = pickle.load(f)
            for i, vec in enumerate(previous_sol):
                previous_sol[i] = np.concatenate((vec, np.zeros(1)), axis = None)
            maximum_cap = find_maximum_cap(dim, field_size, current_cap = previous_sol, hashset=fill_initial_set(previous_sol, EMPTY_HASHSET, dim, field_size))
        elif dim > 1:
            initial_cap = [np.zeros(dim, dtype=int), generate_basis(dim,0), generate_basis(dim, 1)]
            maximum_cap = find_maximum_cap(dim, field_size, current_cap= initial_cap, current_index=2, hashset=fill_initial_set(initial_cap, EMPTY_HASHSET, dim, field_size))
        else:
            initial_cap = [np.zeros(dim, dtype=int)]
            maximum_cap = find_maximum_cap(dim, field_size, current_cap=initial_cap, hashset= fill_initial_set(initial_cap, EMPTY_HASHSET, dim, field_size))

        with open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) + ".dat", "wb") as file:
            pickle.dump(maximum_cap, file)

response = "A maximum cap for d = {}, F = {}, has size {} and is: {}".format(dim, field_size, len(maximum_cap), maximum_cap)
print(response)

