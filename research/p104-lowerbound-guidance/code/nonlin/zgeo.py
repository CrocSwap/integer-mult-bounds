from ncore import *
Gz=Z@G@Z.T
print('Gram of Z16 roots:\n',Gz)
# relations: subsets of Z16 summing to 0 mod 2
K=kernel(Zb.T)
print('mod-2 relations basis (weights):',[int(r.sum()) for r in K])
for r in K: print(''.join(map(str,r)))
