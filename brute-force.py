import numpy as np 
import os
from itertools import combinations
import os.path as path
import pickle
import sys
'''
Python file for recursively finding 

'''

''' Unused Code
@vectorize(['int32(int32, int32)'], target='cuda')
def vectorized_add(a, b):
    return a + b



def generate_all_basis(dim, field_size):
    collection = []
    for i in range(dim):
        collection.append(generate_basis(dim, i))
    return collection

@vectorize(['int32(int32, int32, int32)'], target='cuda')
def vectorized_add(a, b, field_size):
    return a + b % field_size
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

def vectorized_add_nocuda(a, b, field_size):
    return np.mod(a + b, field_size)

def triplet_add_nocuda(a, b, c, field_size):
    return np.mod(a + b + c, field_size)

dim = 3 if len(sys.argv) < 3 else int(sys.argv[2])
field_size = 3 if len(sys.argv) < 3 else int(sys.argv[1])
cache = [None] * (field_size ** dim)

debug_log = open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) +"_debug.txt", 'w+')

# TODO Write a better implementation of linear check
def bad_cap_isLinear(cap, dim, field_size):
    for i, vec in enumerate(cap[:-1]):
        if not (cap[-1] - vec).any():
            return True
        for j in range(i + 1, len(cap) - 1):
            #Assume that the list was a valid cap before adding a new element. Therefore, only need to check that last element is not a cap. 
            if not triplet_add_nocuda(vec, cap[j], cap[-1], field_size).any():
                return True
    return False

def find_maximum_cap(dim, field_size, current_sum=np.zeros(dim, dtype=int), current_cap=[], current_index=0):
    '''dim = size of vector
        field_size = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    if len(current_cap) > field_size - 1 and bad_cap_isLinear(current_cap, dim, field_size): 
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
        current_sum = vectorized_add_nocuda(current_vec, current_sum, field_size)
        #print("Current cap: {}".format(current_cap))
        #print("current sum: {}".format(current_sum))
        
        maximal_cap = find_maximum_cap(dim, field_size, current_sum.copy(), current_cap.copy(), i + 1)
        current_cap.pop()

        if len(maximal_cap) > len(maximum_cap):
            maximum_cap = maximal_cap
    return maximum_cap

answer_file = os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) + "_solution.txt"
previous_sol =  os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim - 1) + ".dat"


if path.exists(answer_file):
    f = open(answer_file, "r")
    for line in f:
        print(line)
    f.close()
else:
    if path.exists(previous_sol):
        with open(previous_sol, 'rb') as f:
            previous_sol = pickle.load(f)
        for i, vec in enumerate(previous_sol):
            previous_sol[i] = np.concatenate((vec, np.zeros(1)), axis = None)
        maximum_cap = find_maximum_cap(dim, field_size, current_cap = previous_sol)
    else:
        maximum_cap = find_maximum_cap(dim, field_size, current_cap= [generate_basis(dim, 0)])

    response = "A maximum cap for d = {}, F = {}, has size {} and is: {}".format(dim, field_size, len(maximum_cap), maximum_cap)
    print(response)
    with open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) + "_solution.txt", 'w+') as file:
        file.write(response)

    with open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) + ".dat", "wb") as file:
        pickle.dump(maximum_cap, file)


debug_log.close()
