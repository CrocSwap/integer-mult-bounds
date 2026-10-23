# usage: k9chunk.py FILE I N : run SERVE2's k9b.graphic(.,9) on distinct served sets I, I+N, I+2N, ... of FILE (cwd has setup2.py, data.txt, k9b.py)
import sys; fn,i,n=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]); sys.argv=['x']
import k9b
sets=list(k9b.parse(fn)); mine=sets[i::n]; g=0
for t in mine:
    if k9b.graphic(t,9): g+=1
print('CHUNK',i,'sets',len(mine),'graphic',g,'total',len(sets))
