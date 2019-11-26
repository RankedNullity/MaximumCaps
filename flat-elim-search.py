import numpy as np 
import os
import os.path as path
import pickle
import sys
import copy
from itertools import combinations, permutations
from multiprocessing import Array, Process
import time
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
    print("Generating coefficients for d = {} , q = {}, n = {}".format(d,q,n))
    #print("coeffs: {}".format(set(good_coeffs)))
    return set(good_coeffs)

def generate_basis(n, index):
    arr = np.zeros(n, dtype = int)
    arr[index] = 1
    return arr

def index_to_vector(n, q, index):
    '''Converts an index to the vector in F_q^n'''
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
    n = 3 if len(sys.argv) < 4 else int(sys.argv[3])
    q = 3 if len(sys.argv) < 4 else int(sys.argv[2])
    d = 2 if len(sys.argv) < 4 else int(sys.argv[1])
    debug_file = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n) + "_debug.txt"
    debug_log = open(debug_file, 'w+')

def update_validset(cap, validset, d, q, n, coeff_list):
    sm_set = Array('i', validset, lock=False)
    processes = []
    #print("cap: {}".format(cap))
    for comb in combinations(cap[:-1], d):
        g = list(comb)
        g.append(cap[-1])
        p = Process(target=mark_visible, args=(sm_set, g, coeff_list, q, n ))
        processes.append(p)
        p.start() 
    
    for p in processes:
        p.join()
    #print ("Validset: {} | sm_set: {}".format(valid_set, sm_set[:]))
    #print("New Validset: {}".format([True if x == 1 else False for x in sm_set]))
    return [True if x == 1 else False for x in sm_set]

def complete_update_validset(cap, validset, d, q, n, coeff_list):
    sm_set = Array('i', validset, lock=False)
    processes = []
    #print("cap: {}".format(cap))
    for i in range(1, d+1):
        for comb in combinations(cap, i + 1):
            p = Process(target=mark_visible, args=(sm_set, list(comb), coeff_list, q, n))
            processes.append(p)
            p.start()
    
    for p in processes:
        p.join()
    #print ("Validset: {} | sm_set: {}".format(valid_set, sm_set[:]))
    #print("New Validset: {}".format([True if x == 1 else False for x in sm_set]))
    return [True if x == 1 else False for x in sm_set]

def mark_visible(shared_memory_set, points, coeff_list, q=3, n=3):
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
            
def find_maximum_cap(n, q, d, coeff_list, current_cap=[], current_index=1, hashset=None, maximum_caps=[], cache=[], depth = []):
    '''n = size of vector
        q = possible values in vector
        current_sum = vector with the sum of each vector in the field.
        '''
    if not __debug__:
        debug_log.write("current cap: {} \nCurrent validset: {}\n".format(current_cap, hashset))

    maximum_cap = current_cap
    for i in range(current_index, q ** n):
        if cache[i] is None:
            current_vec = index_to_vector(n, q, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]
            #print("Using Cached value")
        print("Currently Searching (depth, index):", end='')
        for dep in enumerate(depth):
            print(" {} |".format(dep), end='')
        print("", end='\r')    
        if hashset[i]:
            current_cap.append(current_vec)
            if len(current_cap) > d:
                #print("full. len = {} | d = {}".format(len(current_cap), d))
                vs_new = update_validset(current_cap, hashset, d, q, n, coeff_list=coeff_list)
            else:
                #print("not full")
                vs_new = complete_update_validset(current_cap, hashset, len(current_cap), q, n, coeff_list=coeff_list)
            maximal_cap, _ = find_maximum_cap(n, q, d, current_cap=current_cap.copy(), current_index=i + 1, hashset=vs_new, coeff_list=coeff_list, cache=cache, depth=depth + [i])
            current_cap.pop()
            if len(maximal_cap) > len(maximum_cap):
                maximum_caps = []
                maximum_cap = maximal_cap
            if len(maximal_cap) >= len(maximum_cap):
                maximum_caps.append(maximal_cap)
    if maximum_caps == []:
        maximum_caps.append(maximum_cap)
    
    return maximum_cap, maximum_caps

if __name__ == '__main__':
    if not __debug__:
        if d > n:
            d = n
        coeff_list = generate_coeffs(d, q, n)
        valid_set = [True] * (q ** n)
        cache = [None] * (q ** n)
        print("Generating debug logs")
        start_time = time.time()
        if n > 1:
            initial_cap = [np.zeros(n, dtype=int), generate_basis(n,0), generate_basis(n, 1)]
        else:
            initial_cap = [np.zeros(n, dtype=int)]
        starter_hashset = complete_update_validset(initial_cap, valid_set,d,q,n, coeff_list)
        maximum_cap, maximum_caps = find_maximum_cap(n, q, d, current_cap=initial_cap, hashset= starter_hashset, coeff_list=coeff_list, cache=cache)
        debug_log.close()   
        print("This took {} seconds".format(time.time() - start_time))
        response = "A maximum cap for d = {}, F = {}^{}, has size {} and is: {}".format(d, q, n, len(maximum_cap), maximum_cap)
        print(response)
    else:
        def save_caps(d, q, n):
            print("--------------------------------Starting search for {}-cap in F_{}^{}----------------------------".format(d,q,n))
            valid_set = [True] * (q ** n)
            coeff_list = generate_coeffs(d, q, n)
            cache = [None] * (q ** n)
            previous_sol = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n - 1) + ".dat"
            current_sol = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n) + ".dat"
            complete_log = os.getcwd() + "\\logs\\" + str(d)+ '_' + str(q) + "_" + str(n) + "_all.dat"
            if path.exists(complete_log):
                print("Solution previously found.")
                with open(complete_log, 'rb') as f:
                    maximum_caps = pickle.load(f)
            else:
                if d == n:
                    maximum_cap = [np.zeros(n, dtype=int)] + [generate_basis(n, i) for i in range(n)]
                    maximum_caps = [maximum_cap]
                    print("d = n, so any {} points is a cap.".format(d + 1))
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
                    print("Starting Search...")
                    starter_hashset = complete_update_validset(initial_cap, valid_set, d, q, n, coeff_list)
                    maximum_cap, maximum_caps = find_maximum_cap(n, q, d, current_cap=initial_cap, hashset= starter_hashset, coeff_list=coeff_list, cache=cache)
                    print()

                with open(current_sol,'wb') as file:
                    pickle.dump(maximum_cap, file)
                with open(complete_log, "wb") as file:
                        pickle.dump(maximum_caps, file)
            print("{} caps of size {} were found.".format(len(maximum_caps), len(maximum_caps[0])))
            print("Example Cap: {}".format(maximum_caps[0]))
            return maximum_caps

        if len(sys.argv) != 2:
            if len(sys.argv) == 4:
                n = int(sys.argv[3])
                q = int(sys.argv[2])
                d = int(sys.argv[1])
                if d > n:
                    d = n
            else:
                d = 1
                q = 3
                n = 2 
            maximum_cap = save_caps(d,q,n)
        else:
            n = int(sys.argv[1])
            q = 3
            if n <= 0:
                n = 0
                while(True):
                    n += 1
                    for d in range(n, 0, -1):
                        max_caps = save_caps(d,q,n)
                        print()
            else:
                for d in range(n, 0, -1):
                    max_caps = save_caps(d,q,n)
                    print()

            
    