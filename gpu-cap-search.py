import numpy as np 
import os
from itertools import combinations
import cupy as cp
'''
Python file for recursively finding max d-caps in F_q^n
TODO: Update logic to match that of brute-force.py after update.
'''

''' Unused Code
def generate_basis(dim, index):
    arr = np.zeros(dim, dtype = int)
    arr[index] = 1
    return arr

def generate_all_basis(dim, field_size):
    collection = []
    for i in range(dim):
        collection.append(generate_basis(dim, i))
    return collection
'''

def generate_vector(dim, field_size, index):
    vec = np.zeros(dim, dtype=int)
    for i in range(dim):
        vec[dim - 1 - i] = index // (field_size ** (i)) % field_size
    return vec


def add_cuda(field_size, *args):
    return cp.mod(cp.sum(cp.array(args), dim=0),field_size)

dim = 3
field_size = 3
cache = [None] * (field_size ** dim)

debug_log = open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) +"_debug.txt", 'w+')

# TODO Write a better implementation of linear check
def cap_isLinear(cap, dim, field_size):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            #Assume that the list was a cap before adding a new element. Therefore, only need to check that last element is not a cap. 
            if not add_cuda(field_size, cap[i], cap[j], cap[len(cap) - 1]).any():
                return True
    return False

def cap_isPlanar(cap, dim, field_size):
    for i, vec in enumerate(cap[:-1]):
        for j in range(i + 1, len(cap) - 1):
            for k in range(j + 1, len(cap) - 1):
                if not add_cuda(field_size, cap[i], cap[j], -cap[k], -cap[-1]).any():
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



def find_maximum_cap(dim, field_size, current_sum=cp.zeros(dim, dtype=int), current_cap=[], current_index=0, cap_validity=cap_isLinear):
    '''dim = size of vector
        field_size = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    if len(current_cap) > field_size - 1 and cap_validity(current_cap, dim, field_size): 
        #debug_log.write("Reached stop condition with: {}".format(current_cap))
        current_cap.pop()
        debug_log.write("{}\n".format(current_cap))
        return current_cap

    maximum_cap = []
    global cache

    for i in range(current_index, field_size ** dim):
        if cache[i] is None:
            current_vec = generate_vector(dim, field_size, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]

        #print("Current cap before: {}".format(current_cap))
        current_cap.append(current_vec)
        current_sum = add_cuda(current_vec, current_sum, field_size)
        #print("Current cap: {}".format(current_cap))
        #print("current sum: {}".format(current_sum))
        
        maximal_cap = find_maximum_cap(dim, field_size, current_sum.copy(), current_cap.copy(), i + 1)
        current_cap.pop()

        if len(maximal_cap) > len(maximum_cap):
            maximum_cap = maximal_cap
    return maximum_cap

maximum_cap = find_maximum_cap(dim, field_size)

with open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) +"_solution.txt", 'w+') as file:
    file.write("A maximum cap for d = {}, F = {}, has size {} and is: {}".format(dim, field_size, len(maximum_cap), maximum_cap))
    file.close()

debug_log.close()

'''
Temp Log:
    Changed the add operations to be run on GPU 

    Issues:
    Check isn't complete for anything other than a 1-cap in F3_^n
'''