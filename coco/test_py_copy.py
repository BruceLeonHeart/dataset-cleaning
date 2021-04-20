import numpy
import copy

a=[]

for i in range(10):
    a.append(i)

b =copy.deepcopy(a)
c =copy.deepcopy(a)

b[0] = 10
c[1] = 20

print(b)
print(c)
