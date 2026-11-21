# JOINTDR: t7669 owned->public->owned relays: carrier kind, ascent e = dim(read chart) - dim(write chart). stdlib.
import sys
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import Counter, defaultdict
W=pk.load('<word-rung-package>/data/t7669.json.gz')
n=W['public']; F=W['frames']; dim=[len(b) for b in F]; P=W['program']
live=W['live']; H=W['hosted']
kind={}
for p,r in enumerate(live): kind[r]='X'; kind[r+112]='Y'
for j,p in enumerate(H['Dports']): kind[H['X2'][j]]='X2'; kind[H['Y2'][j]]='Y2'
def K(r): return kind.get(r,'H') if r<n else 'O'
cur=list(W['initial'])+[None]*W['owned_fields']
lid={}; cnt=0; ltype={}  # lifetime -> 'U'/'D'/'-'
moves=defaultdict(list)
for e in P:
    if e[0]=='INIT': cnt+=1; lid[e[1]]=cnt
    elif e[0]=='MOVE' and e[1]>=n: moves[lid[e[1]]].append(dim[e[3]]-dim[e[2]])
    elif e[0]=='CLEAR': del lid[e[1]]
for l,m in moves.items(): ltype[l]='U' if m[0]>0 else 'D'
cur=list(W['initial'])+[None]*W['owned_fields']; lid={}; cnt=0
writers=defaultdict(dict)   # public -> {lifetime: dim at last write}
edges=Counter(); ex=Counter()
for e in P:
    op,r=e[0],e[1]
    if op=='INIT': cnt+=1; lid[r]=cnt; cur[r]=e[2]
    elif op=='CLEAR': cur[r]=None; del lid[r]
    elif op=='MOVE': cur[r]=e[3]
    elif op in('ADD','COPY'):
        s=e[2]; f=e[4]
        if s>=n and r<n:   # owned writes public
            writers[r][lid[s]]=dim[f]
        if s<n and r>=n:   # owned reads public
            k=lid[r]
            for j,dw in writers[s].items():
                if j==k: continue
                tj=ltype.get(j,'-'); tk=ltype.get(k,'-')
                edges[(tj,tk,K(s))]+=1; ex[(tj,tk,K(s),dim[f]-dw)]+=1
print('relay edges (writer type, reader type, carrier kind): count'); 
for k,v in sorted(edges.items()): print(' ',k,v)
print('with ascent e:')
for k,v in sorted(ex.items()): print(' ',k,v)
