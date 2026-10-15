"""consolidate odd 48-bins: move their 4s into 5-holes, gather the rest into one bin. argv: FILL_IN PROV FILL_OUT"""
import sys,json,gzip,random,collections,os;sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fillbase import *
pv=json.load(open(sys.argv[2]));widths=pv['widths'];paid={k:{int(a):b for a,b in v.items()} for k,v in pv['paid'].items()}
rows=[list(x) for x in read(sys.argv[1])['rows']]
win={}
for key,(cap,times) in windows.items():
    r,ch=map(int,key.split(','));ts=sorted(times);win[r,ch]=(cap,ts[0],ts[-1])
wid=[widths[dispatch[tuple(order[x[0]])]][x[1]] for x in rows]
B=lambda i:tuple(rows[i][2:5])
members=collections.defaultdict(set);used=collections.Counter();cf=collections.defaultdict(collections.Counter)
for i in range(len(rows)):members[B(i)].add(i);used[B(i)]+=wid[i];cf[rows[i][0]][family(*B(i))]+=1
def can(i,b):
    cap,lo,hi=win[b[:2]];t=rows[i][0]
    return lo<=t<=hi and used[b]+wid[i]<=cap and cf[t][family(*b)]==0
def move(i,b):
    o=B(i);t=rows[i][0];members[o].discard(i);used[o]-=wid[i];cf[t][family(*o)]-=1
    rows[i][2],rows[i][3],rows[i][4]=b;members[b].add(i);used[b]+=wid[i];cf[t][family(*b)]+=1
odd=[b for b in members if win[b[:2]][0]==48 and 0<48-used[b] and any(wid[i]==4 for i in members[b]) and used[b]<48-0 and not all(wid[i]==9 for i in members[b])]
odd=[b for b in odd if sorted(wid[i] for i in members[b])[-1]<9]
print('odd bins',[(b,sorted(wid[i] for i in members[b])) for b in odd])
holes=[b for b in members if win[b[:2]][0]==32 and used[b]==27]+[(r,ch,p) for (r,ch) in win if win[r,ch][0]==32 for p in range(112) if (r,ch,p) not in members]
moved=0
for b in odd:
    for i in sorted(members[b]):
        if wid[i]!=4:continue
        for hb in holes:
            if used[hb]==27 and can(i,hb):move(i,hb);moved+=1;break
print('moved 4s',moved,[(b,sorted(wid[i] for i in members[b])) for b in odd])
# gather the rest into one of the odd bins
for tgt in odd:
    for b in odd:
        if b==tgt:continue
        for i in sorted(members[b]):
            if can(i,tgt):move(i,tgt)
print('after gather',[(b,sorted(wid[i] for i in members[b])) for b in odd])
rows=compact(rows,lambda r:widths[dispatch[tuple(order[r[0]])]][r[1]])
idle,H=check(rows,widths,paid);print('idle',dict(sorted(idle.items())),'kappa',kappa(H))
open(sys.argv[3],'wb').write(gzip.compress(json.dumps(dict(columns=fill['columns'],dispatch_overrides=fill['dispatch_overrides'],rows=rows),separators=(',',':')).encode()))
