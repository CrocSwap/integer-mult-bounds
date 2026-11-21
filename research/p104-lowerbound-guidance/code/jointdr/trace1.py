import sys
sys.path.insert(0,'<word-rung-package>/tools')
import pricekit as pk
from collections import defaultdict
W=pk.load('<word-rung-package>/data/t7669.json.gz')
n=W['public']; F=W['frames']; dim=[len(b) for b in F]; P=W['program']
live=W['live']; H=W['hosted']
mains=set(live)|{r+112 for r in live}|set(H['X2'])|set(H['Y2'])
lid={}; cnt=0; ltype={}; moves=defaultdict(list)
for e in P:
    if e[0]=='INIT': cnt+=1; lid[e[1]]=cnt
    elif e[0]=='MOVE' and e[1]>=n: moves[lid[e[1]]].append(dim[e[3]]-dim[e[2]])
    elif e[0]=='CLEAR': del lid[e[1]]
for l,m in moves.items(): ltype[l]='U' if m[0]>0 else 'D'
lid={}; cnt=0; writers=defaultdict(dict); found=None
for i,e in enumerate(P):
    op,r=e[0],e[1]
    if op=='INIT': cnt+=1; lid[r]=cnt
    elif op=='CLEAR': del lid[r]
    elif op in('ADD','COPY'):
        s=e[2]; f=e[4]
        if s>=n and r<n and r not in mains: writers[r][lid[s]]=(dim[f],i)
        if s<n and r>=n and s not in mains:
            for j,(dw,iw) in writers[s].items():
                if ltype.get(j)=='D' and lid[r] not in ltype and dim[f]-dw==int(sys.argv[1]) and found is None: found=(s,iw,i,r)
s,iw,ir,rr=found; print('helper',s,'write at',iw,'read at',ir,'reader reg',rr)
regs={s}
for i,e in enumerate(P):
    if e[1]==s or (len(e)>2 and e[0] in('ADD','COPY') and e[2]==s): 
        print(i,e, [dim[x] for x in e[2:4]] if e[0]=='MOVE' else dim[e[4]] if e[0] in ('ADD','COPY') else '')
