import numpy as np 
import os
import os.path as path
import pickle
import sys
import copy
from itertools import combinations, permutations
from multiprocessing import Array, Process
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
    return np.mod(np.sum(np.array(args), axis=0), q)

if not __debug__:
    debug_file = os.getcwd() + "\\logs\\" + str(q) + "_" + str(n) +"_debug.txt"
    debug_log = open(debug_file, 'w+')


def fill_initial_set(cap, vset, n=n, q=q, d=d):
    '''Mutates set to be the accurate hashset for the given cap.'''
    for vec in cap:
        index= vector_to_index(vec, n, q)
        vset[index] = False

    return vset

def update_validset(cap, validset, d, q, n):
    sm_set = Array('i', validset)
    processes = []
    for i in range (1, d + 1):
        for comb in combinations(cap[:-1], i):
            print("comb: {}".format(comb))
            print("cap: {}".format(cap[-1]))
            print("both: {}".format(list(comb).append(cap[-1])))
            comb += cap[-1]
            p = Process(target=mark_visible, args=(sm_set, comb, q, n))
            processes.append(p)
            p.start() 
    
    for p in processes:
        p.join()
    #print ("Validset: {} | sm_set: {}".format(valid_set, sm_set[:]))
    return [True if x == 1 else False for x in sm_set]
    
    
def complete_update_validset(cap, validset, d, q, n):
    sm_set = Array('i', validset)
    processes = []
    for i in range(1, d + 1):
        for comb in combinations(cap, i + 1):
            p = Process(target=mark_visible, args=(sm_set, comb, q, n))
            processes.append(p)
            p.start()

    for p in processes:
        p.join()

    return [True if x == 1 else False for x in sm_set]
    

# TODO: Write this method
def mark_visible(shared_memory_set, points, q=3, n=3):
    '''
        Takes a set of points and marks every point which lies on the d-flat which is constructed by the (d+1) points
        and marks the corresponding index in shared_memory_set as False. 

        points: list of d+1 points which make a d-flat.
        shared_memory_set: multiprocessing.Array(b, validset)
    '''
    # Note: I am aware this is bad code. I am just writing it like this to find the commonality so I can generalize the pattern.
    print(shared_memory_set)
    print(points)
    if len(points) == 2:
        print("Removing 1 cap with 2 points")
        all_add = set(permutations[2,2]) + set(permutations([0,1]))
        for coeff in all_add:
            point = add_nocuda(q, [a*b for a,b in zip(coeff, points)])
            print(point)
            shared_memory_set[vector_to_index(point)] = 0

    if len(points) == 3:
        all_add = set(permutations[2,2,0]) + set(permutations([0,0,1])) + set(permutations([1,1,2]))
        for coeff in all_add:
            point = add_nocuda(q, [a*b for a,b in zip(coeff, points)])
            shared_memory_set[vector_to_index(point)] = 0
            


def find_maximum_cap(n, q, d=1, current_cap=[np.zeros(n, dtype=int)], current_index=1, hashset=None):
    '''n = size of vector
        q = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    #print("current cap: {} | Current validset: {}".format(current_cap, hashset))
    
    global cache

    maximum_cap = current_cap

    if current_index >= q ** n:
        print("reached end with cap: {}".format(maximum_cap))
    for i in range(current_index, q ** n):
        if cache[i] is None:
            current_vec = index_to_vector(n, q, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]

        #print("Current cap before: {}".format(current_cap))
        if hashset[i]:
            current_cap.append(current_vec)
            vs_new = update_validset(current_cap, hashset, d, q, n)
            maximal_cap = find_maximum_cap(n, q, d, current_cap.copy(), i + 1, hashset=vs_new)
            current_cap.pop()
            if len(maximal_cap) > len(maximum_cap):
                maximum_cap = maximal_cap

    return maximum_cap

if __name__ == '__main__':
    valid_set = [True] * (q ** n)
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
