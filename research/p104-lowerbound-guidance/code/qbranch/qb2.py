# QBRANCH qb2: extract #7113 per-role masks and paid pieces (IDLE sets), thin QUERY units; compare to invoice
import json
from collections import Counter,defaultdict
from decimal import Decimal as Dm, getcontext; getcontext().prec=40
C=json.load(open('cards/WILD/MONOCALLER/7113_CALLER.json'))
s=Dm('0.99'); p=lambda x: Dm(x)**s
out={}
for t,v in C['types'].items():
    off=v['offset']; masks=[]
    for i,d in enumerate(v['diagonal']): masks.append((d[0],[j for j,b in enumerate(d[2:]) if b]))
    out[t]=masks
pieces={t:defaultdict(list) for t in out}; queries=Counter()
for e in C['events']:
    if e[0]=='J' or e[1] not in('IDLE_ONE','IDLE_ODD','QUERY'): continue
    if e[1]=='QUERY': queries[e[0]]+=1; continue
    pieces[e[0]][e[2]].append(tuple(e[3]))
for t in out:
    off=C['types'][t]['offset']
    print('TYPE',t,'ports',len(C['types'][t]['ports']),'queries',queries[t],'offset',off)
    for i,(ex,m) in enumerate(out[t]):
        ps=pieces[t].get(off+i,[]); print(i,'exp',ex,'D',len(m),'mask',m[0] if m else '-',m[-1] if m else '-','pieces',[(len(q),min(q),max(q)) for q in ps])
print('---- invoice check')
k=17
tot=0
for t in out:
    off=C['types'][t]['offset']; T=P=Dm(0)
    for i,(ex,m) in enumerate(out[t]):
        T+=p(8*len(m)+(ex%2))
        for q in pieces[t].get(off+i,[]): P+=p(8*len(q))
    q=queries[t]; P+=q
    n=len(out[t]); ports=len(C['types'][t]['ports'])
    print(t,'roles',n,'T',float(T),'P(incl thin)',float(P),'ports',ports)
    tot+=ports*(T-P)
print('per-call chat = (sum ports (T-P))/17 -400*8^s =',float(tot/17-400*p(8)))
for t in out:
    off=C['types'][t]['offset']; T=P=Dm(0)
    for i,(ex,m) in enumerate(out[t]):
        T+=p(8*len(m)+(ex%2))
        for q in pieces[t].get(off+i,[]): P+=p(8*len(q))
    P+=queries[t]
    print(t,'F=T-P-34*8^s =',float(T-P-34*p(8)),'F*104/17 =',float((T-P-34*p(8))*104/17))
