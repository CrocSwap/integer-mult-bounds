# JOINTDR: t7669 owned lifetimes: move dim sequences, up/down mix. stdlib.
import pickle,sys
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import Counter
W=pk.load('<word-rung-package>/data/t7669.json.gz')
F=W['frames']; dim=[len(b) for b in F]
L=pickle.load(open('../gapmap/lifes.pkl','rb'))['lifes']
shapes=Counter(); up=dn=0; mixed=[]
for i,l in L.items():
    mv=[(dim[e[1]],dim[e[2]]) for e in l['evs'] if e[0]=='move']
    if not mv: continue
    s=''.join('U' if b>a else 'D' for a,b in mv)
    shapes[s]+=1
    u=sum(b-a for a,b in mv if b>a); d=sum(a-b for a,b in mv if a>b); up+=u; dn+=d
    if 'U' in s and 'D' in s: mixed.append((i,mv))
print('owned lifetimes with moves',sum(shapes.values()),'A_own',up,'D_own',dn)
print('shapes',dict(shapes))
for i,mv in mixed: print('mixed',i,mv)
