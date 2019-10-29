

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