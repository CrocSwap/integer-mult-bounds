# NETTENSOR osip.py (own code): exact minimisation of the one-sided level/clique floor (Theorem OS, NT.md sec 3).
import itertools, math
N={0:0,1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:60,9:104}
kap={b:min(13,N[9-b]) for b in range(1,9)}   # cliques met by a flat b^perp (trivial cap)
best=(10**9,None)
def val(nb):
    tot=0; prof=[]
    for l in range(1,10):
        hits=sum(kap[b]*nb[b] for b in range(max(l,1),9))
        need = 8-min(8,hits//13) if l<=8 else 0
        c=max(need, nb.get(l-1,0) if l>=2 else 0)
        tot+=c; prof.append(c)
    return tot,prof
R=range(0,27)
for n5 in R:
  for n4 in range(0,15):
    for n3 in range(0,10):
      for n6 in range(0,30):
        for n7 in (0,10,20,30,40,52):
          for n2 in (0,2,4,8):
            nb={1:0,2:n2,3:n3,4:n4,5:n5,6:n6,7:n7,8:0}
            v,p=val(nb)
            if v<best[0]: best=(v,nb,p)
print('one-sided level/clique floor:',best)
