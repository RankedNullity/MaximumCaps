
'''
count = 0
# i j
# k n
l = []

dim_size = 5

for i in range(dim_size):
    for j in range(dim_size):
        for k in range(dim_size):
            for n in range(dim_size):
                if (i * n - j * k) % dim_size != 0:
                    l.append((i, j, k, n))
                    count += 1

print(count)
print(l)
print(len(l))

if not __debug__:
    print("Debug")
else: 
    print("No debug")

'''
from multiprocessing import Array, Process
from itertools import combinations, permutations
def f(n, a):
    for i in range(len(a)):
        a[i] = False


if __name__ == '__main__':
    bool_array = [True] * 10
    arg = Array('b', bool_array, lock=False)

    p = Process(target=f, args=(5, arg))
    p.start()
    p.join()

    print(arg[:])
    print(bool_array)

    print(set(permutations([2,2,0])))