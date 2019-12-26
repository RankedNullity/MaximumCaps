'''
Python module for finding maximum d-caps in F_q^n by adding each possible point to the cap, and continuing only if the cap
is still valid. Stops when the cap is not. Slow sequentially due to large search space. CURRENTLY NOT-MAINTAINED.

Jaron Wang
'''
import numpy as np 
import os
import os.path as path
import pickle
import sys
from affine_space_core import *

n = 3 if len(sys.argv) < 3 else int(sys.argv[2])
q = 3 if len(sys.argv) < 3 else int(sys.argv[1])
cache = [None] * (q ** n)

if not __debug__:
    debug_file = os.getcwd() + "\\results\\" + str(q) + "_" + str(n) +"_debug.txt"
    debug_log = open(debug_file, 'w+')    


"""Checks if the given cap is linear"""
def cap_isLinear(cap, n, q):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            #Assume that the list was a cap before adding a new element. Therefore, only need to check that last element is not a cap. 
            if not add_affine(q, cap[i], cap[j], cap[len(cap) - 1]).any():
                return True
    return False

""" Checks if the given cap is planar"""
def cap_isPlanar(cap, n, q):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            for k in range(j + 1, len(cap) - 1):
                if not add_affine(q, cap[i], cap[j], -cap[k], -cap[-1]).any():
                    return True
    return False

''' Generalized method for checking if the cap is a q-flat. UNFINISHED'''
def is_q_flat(cap, n, q):
    pass 


"""Gets the appropriate verifier for a given d."""
def find_verifier(d):
    if d==1:
        return cap_isLinear
    elif d==2:
        return cap_isPlanar
    else:
        return is_q_flat

'''Mutates set to be the accurate hashset for the given cap.'''
def fill_initial_set(cap, set, n, q):
    for vec in cap:
        index= vector_to_index(vec, n, q)
        set[index] = True
    return set

"""Finds the maximum d-cap in F_q^n with the given parameters."""
def find_maximum_cap(n, q, d=1, current_cap= [np.zeros(n, dtype=int)], current_index=1, illegal_check=cap_isLinear):
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


if not __debug__:
    print("Generating debug results")
    if n > 1:
        initial_cap = [np.zeros(n, dtype=int), generate_basis(n,0), generate_basis(n, 1)]
    else:
        initial_cap = [np.zeros(n, dtype=int)]
    maximum_cap = find_maximum_cap(n, q, current_cap=initial_cap)
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
        maximum_cap = find_maximum_cap(n, q, current_cap=initial_cap)

        with open(os.getcwd() + "\\results\\" + str(q) + "_" + str(n) + ".dat", "wb") as file:
            pickle.dump(maximum_cap, file)

response = "A maximum cap for d = {}, F = {}, has size {} and is: {}".format(n, q, len(maximum_cap), maximum_cap)
print(response)

