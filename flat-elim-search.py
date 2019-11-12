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

def add_nocuda(q, *args):
    return np.mod(np.sum(np.array(args), axis=0), q)

def generate_coeffs(d, q, n):
    l =[]
    for i in range(q):
        l += [i] * (d+1)

    good_coeffs = []
    for comb in permutations(l, d+1):
        if add_nocuda(q, *comb) == 1:
            good_coeffs.append(comb)
    #print(set(good_coeffs))
    return set(good_coeffs)
    

n = 3 if len(sys.argv) < 4 else int(sys.argv[3])
q = 3 if len(sys.argv) < 4 else int(sys.argv[2])
d = 2 if len(sys.argv) < 4 else int(sys.argv[1])

cache = [None] * (q ** n)
if d > n:
    d = n

coeff_list = generate_coeffs(d, q, n)

def generate_basis(n, index):
    arr = np.zeros(n, dtype = int)
    arr[index] = 1
    return arr

def index_to_vector(n, q, index):
    vec = np.zeros(n, dtype=int)
    for i in range(n):
        vec[n - 1 - i] = index // (q ** (i)) % q
    return vec

def vector_to_index(vector, q, n):
    '''Takes the vector and converts it to the unique index under F_{fieldsize}^{n}'''
    assert(n == len(vector))
    index = 0
    for i in range(0, n):
        index += vector[n - 1 - i] * (q ** i)
    return int(index)


if not __debug__:
    debug_file = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n) + "_debug.txt"
    debug_log = open(debug_file, 'w+')


def fill_initial_set(cap, vset, n=n, q=q, d=d):
    '''Mutates set to be the accurate hashset for the given cap.'''
    for vec in cap:
        index= vector_to_index(vec, q, n)
        vset[index] = False

    return vset

def update_validset(cap, validset, d, q, n):
    sm_set = Array('i', validset, lock=False)
    processes = []
    #print("cap: {}".format(cap))
    for comb in combinations(cap[:-1], d):
        g = list(comb)
        g.append(cap[-1])
        p = Process(target=mark_visible, args=(sm_set, g, q, n))
        processes.append(p)
        p.start() 
    
    for p in processes:
        p.join()
    #print ("Validset: {} | sm_set: {}".format(valid_set, sm_set[:]))
    #print("New Validset: {}".format([True if x == 1 else False for x in sm_set]))
    return [True if x == 1 else False for x in sm_set]

def complete_update_validset(cap, validset, d, q, n):
    sm_set = Array('i', validset, lock=False)
    processes = []
    #print("cap: {}".format(cap))
    for comb in combinations(cap, d + 1):
        p = Process(target=mark_visible, args=(sm_set, list(comb), q, n))
        processes.append(p)
        p.start() 
    
    for p in processes:
        p.join()
    #print ("Validset: {} | sm_set: {}".format(valid_set, sm_set[:]))
    #print("New Validset: {}".format([True if x == 1 else False for x in sm_set]))
    return [True if x == 1 else False for x in sm_set]

def mark_visible(shared_memory_set, points, q=3, n=3):
    '''
        Takes a set of points and marks every point which lies on the d-flat which is constructed by the (d+1) points
        and marks the corresponding index in shared_memory_set as False. 

        points: list of d+1 points which make a d-flat.
        shared_memory_set: multiprocessing.Array(b, validset)
    '''
    #print(shared_memory_set[:])
    #print("Coeffs: {}".format(coeff_list))
    #print("Points: {}".format(points))
    
    for coeff in coeff_list:
        dotprod = [a * b for a,b in zip(coeff, points)]
        point = add_nocuda(q, *dotprod)
        #print("removing: {}".format(point))
        #print("Points: {} | coeff: {}".format(points, coeff))
        #print(" weird dot :{}".format([a * b for a,b in zip(coeff, points)]))
        #print("Point: {}".format(point))
        index = vector_to_index(point, q, n)
        #print("removing index: {}".format(index))
        shared_memory_set[index] = 0
            

def find_maximum_cap(n, q, d, current_cap=[np.zeros(n, dtype=int)], current_index=1, hashset=None):
    '''n = size of vector
        q = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    if not __debug__:
        debug_log.write("current cap: {} \nCurrent validset: {}".format(current_cap, hashset))
    
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
        starter_hashset = complete_update_validset(initial_cap, valid_set,d,q,n)
        maximum_cap = find_maximum_cap(n, q, d, current_cap=initial_cap, hashset= starter_hashset)
        debug_log.close()   
    else:
        previous_sol = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n - 1) + ".dat"
        current_sol = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n) + ".dat"
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

            starter_hashset = complete_update_validset(initial_cap, valid_set, d, q, n)
            maximum_cap = find_maximum_cap(n, q, d, current_cap=initial_cap, hashset= starter_hashset)

            with open(os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n) + ".dat", "wb") as file:
                pickle.dump(maximum_cap, file)

    response = "A maximum cap for d = {}, F = {}^{}, has size {} and is: {}".format(d, q, n, len(maximum_cap), maximum_cap)
    print(response)
