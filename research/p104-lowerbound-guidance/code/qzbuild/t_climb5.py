from qzclimb2 import *
k=int(sys.argv[1]); n=2*k-2
masks=[set(range(t,k)) for t in range(k-1) for _ in range(2)]
masks=[set(range(max(0,j-1) if False else 0,k)) for j in range(0)]
# chain masks: roles 2j,2j+1 first covered at stage j (j=0..k-2), U_1 = first 2 roles etc; last stage adds none
masks=[]
for j in range(1,k):     # time j covers roles 2j-2,2j-1 first
    masks += [set(range(j-1,k))]*2
pieces=[]
for t in range(k):
    cnt=sum(1 for M in masks if t in M)-2
    pieces += [frozenset({t})]*cnt
order=tuple(range(k)); place={i:min(S)+1 for i,S in enumerate(pieces)}
cur=climb2(n,k,masks,pieces,order,place)
