import numpy as np 
import os
import os.path as path
import pickle
import sys
import copy
from itertools import combinations
'''
Python file for recursively finding maximum d-caps in F_q^n by eliminating the invalid 

'''

n = 3 if len(sys.argv) < 4 else int(sys.argv[3])
q = 3 if len(sys.argv) < 4 else int(sys.argv[2])
d = 1 if len(sys.argv) < 4 else int(sys.argv[1])
cache = [None] * (q ** n)

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


if not __debug__:
    debug_file = os.getcwd() + "\\logs\\" + str(q) + "_" + str(n) +"_debug.txt"
    debug_log = open(debug_file, 'w+')


def fill_initial_set(cap, set, n=n, q=q, d=d):
    '''Mutates set to be the accurate hashset for the given cap.'''
    for vec in cap:
        index= vector_to_index(vec, n, q)
        set[index] = False

    return set

def update_validset(cap, validset, d, q, n):
    for i in range (1, d+1):
        for comb in combinations(cap[:-1], i):
            comb += cap[-1]
            mark_visible(validset, comb, d,q,n)
    
def complete_update_validset(cap, validset, d, q, n):
    for i in range(1, d + 1):
        for comb in combinations(cap, i + 1):
            mark_visible(validset, comb, d,q,n)

# TODO: Write this method
def mark_visible(validset, points, d=2, q=3, n=3):
    pass


'''Unused Method
def remove_changes(validset, changeset):
    return [True if not v and c else False for v, c in zip(validset, changeset)]
'''

# Change hashset to be index - > (whether or not that index is valid)
valid_set = [True] * (q ** n)

def find_maximum_cap(n, q, d=1, current_cap=[np.zeros(n, dtype=int)], current_index=1, hashset=None):
    '''n = size of vector
        q = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    print("current cap: {} | Current validset: {}".format(current_cap, hashset))
    if current_index >= q ** n:
        print("reached end with cap: {}".format(current_cap))
        return current_cap
    global cache

    maximum_cap = current_cap
    for i in range(current_index, q ** n):
        if cache[i] is None:
            current_vec = index_to_vector(n, q, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]

        #print("Current cap before: {}".format(current_cap))
        if hashset[i]:
            vs_new = copy.deepcopy(hashset) 
            current_cap.append(current_vec)
            vs_new[i] = False
            update_validset(current_cap, vs_new, d, q, n)
            maximal_cap = find_maximum_cap(n, q, d, current_cap.copy(), i + 1, hashset=vs_new)
            current_cap.pop()
            if len(maximal_cap) > len(maximum_cap):
                maximum_cap = maximal_cap

    return maximum_cap

if not __debug__:
    print("Generating debug logs")
    if n > 1:
        initial_cap = [np.zeros(n, dtype=int), generate_basis(n,0), generate_basis(n, 1)]
    else:
        initial_cap = [np.zeros(n, dtype=int)]
    starter_hashset = fill_initial_set(initial_cap, valid_set, n, q)
    maximum_cap = find_maximum_cap(n, q, current_cap=initial_cap, hashset= starter_hashset)
    debug_log.close()   
else:
    previous_sol = os.getcwd() + "\\logs\\" + str(q) + "_" + str(n - 1) + ".dat"
    current_sol = os.getcwd() + "\\logs\\" + str(q) + "_" + str(n) + ".dat"
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
                initial_cap[i] = np.concatenate((vec, np.zeros(1)), axis = None).astype(int)
        elif n > 1:
            initial_cap = [np.zeros(n, dtype=int), generate_basis(n,0), generate_basis(n, 1)]
        else:
            initial_cap = [np.zeros(n, dtype=int)]

        starter_hashset = fill_initial_set(initial_cap, valid_set, n, q)
        maximum_cap = find_maximum_cap(n, q, current_cap=initial_cap, hashset= starter_hashset)

        with open(os.getcwd() + "\\logs\\" + str(q) + "_" + str(n) + ".dat", "wb") as file:
            pickle.dump(maximum_cap, file)

response = "A maximum cap for d = {}, F = {}^{}, has size {} and is: {}".format(d, q, n, len(maximum_cap), maximum_cap)
print(response)


## TODO FOR CODE
# Decide between parallelizing depth+1 check vs. removing all invalid points
    # Removing all the invalid points is faster when I can split the calculations of the points into different processes.
    # To remove all the invalid points, I need to find a indexing of the points on the d-dimensional flat which is constructed by an arbitrary (d+1) points