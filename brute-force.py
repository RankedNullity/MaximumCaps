import numpy as np 
from numba import vectorize
import os

@vectorize(['int32(int32, int32)'], target='cuda')
def vectorized_add(a, b):
    return a + b

def generate_basis(dim, index):
    arr = np.zeros(dim, dtype = int)
    arr[index] = 1
    return arr

def generate_all_basis(dim, field_size):
    collection = []
    for i in range(dim):
        collection.append(generate_basis(dim, i))
    return collection

def generate_vector(dim, field_size, index):
    vec = np.zeros(dim, dtype=int)
    for i in range(dim):
        vec[dim - 1 - i] = index // (field_size ** (i)) % field_size
    return vec

@vectorize(['int32(int32, int32, int32)'], target='cuda')
def vectorized_add(a, b, field_size):
    return a + b % field_size

def vectorized_add_nocuda(a, b, field_size):
    return np.mod(a + b, field_size)

dim = 2
field_size = 3
cache = [None] * (field_size ** dim)

debug_log = open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) +"_debug.txt", 'w+')

def find_maximum_cap(dim, field_size, current_sum=np.zeros(dim, dtype=int), current_cap=[], current_index=0):
    '''dim = size of vector
        field_size = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    if np.count_nonzero(current_sum) < dim  and len(current_cap) > 1: 
        debug_log.write("Reached stop condition with: {}".format(current_cap))
        current_cap.pop()
        debug_log.write("Cap: {} \n".format(current_cap))
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
        print("Current cap: {}".format(current_cap))
        print("current sum: {}".format(current_sum))
        
        maximal_cap = find_maximum_cap(dim, field_size, current_sum.copy(), current_cap.copy(), i + 1)
        current_cap.pop()

        if len(maximal_cap) > len(maximum_cap):
            maximum_cap = maximal_cap

    return maximum_cap


maximum_cap = find_maximum_cap(dim, field_size)

with open(os.getcwd() + "\\logs\\" + str(field_size) + "_" + str(dim) +".txt", 'w+') as file:
    file.write("A maximum cap for d = {}, F = {}, has size {} and is: {}".format(dim, field_size, len(maximum_cap), maximum_cap))
    file.close()

debug_log.close()