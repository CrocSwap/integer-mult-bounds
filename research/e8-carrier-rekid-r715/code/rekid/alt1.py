import os,sys,pickle,itertools
os.environ['E8COORD']='ham'
import frames as Fm, e8lib as E, ham1
h=pickle.load(open('h865.pkl','rb'))
V=120
N=len(h.content)
# index by content
bycont={}
for u in range(N): bycont.setdefault(h.content[u],[]).append(u)
# all pairs x<y (including sources) with xor content equal to some symbol content
from collections import Counter
alts=Counter(); tot=0
pairs=0
cnt={}
for x in range(N):
    cx=h.content[x]
    for y in range(x+1,N):
        c=cx^h.content[y]
        if c in bycont:
            for w in bycont[c]:
                if w==x or w==y or w<V: continue
                # frame constraint
                f,d=Fm.closure(h.frame[x]|h.frame[y])
                if Fm.inside(f,h.frame[w]):
                    cnt.setdefault(w,[]).append((x,y,f==h.frame[w]))
print('symbols with alternative decompositions',len(cnt),'of',N-V)
cur={w:tuple(sorted(h.kids[w])) for w in range(V,N)}
multi=Counter()
for w,l in cnt.items():
    nonself=[(x,y,e) for x,y,e in l if tuple(sorted((x,y)))!=cur[w]]
    multi[len(nonself)]+=1
print(sorted(multi.items()))
# examples with overlap (non-disjoint x,y)
ov=0
for w,l in cnt.items():
    for x,y,e in l:
        if h.content[x]&h.content[y]: ov+=1
print('alternatives with overlapping (cancelling) kids',ov)
sz=lambda u: bin(h.content[u]).count('1')
pat=Counter()
for w,l in cnt.items():
    for x,y,e in l:
        if h.content[x]&h.content[y]:
            ov=bin(h.content[x]&h.content[y]).count('1')
            pat[(('w',sz(w),h.dim[w]),('x',sz(x),h.dim[x]),('y',sz(y),h.dim[y]),'ov',ov,'frameEq',e)]+=1
for k,v in sorted(pat.items(),key=str): print(k,v)
