"""HALVPAY gauge.py: gauge U,H,GH registers by 2 (store 2*value) in the FANOUT56 runs and replay exactly:
reports min 2-adic valuation of all values (den<=2 <=> min v2 >= -1), scalar valuation classes, owned ascents/descents,
and that the gauged program reaches the gauged targets.  Gauged ADD r += c s becomes r += (g_r/g_s) c s."""
import pickle, collections, sys
from fractions import Fraction as Fr
d=pickle.load(open(sys.argv[1],'rb')); prog=d['prog']; init=d['init']; tg=d['targets']
g=lambda r: Fr(2) if r[0] in ('U','H','GH') else Fr(1)
def v2(x):
    x=Fr(x); n,dd=x.numerator,x.denominator; k=0
    if n==0: return 99
    while n%2==0: n//=2; k+=1
    while dd%2==0: dd//=2; k-=1
    return k
fd=lambda F: len(F).bit_length()-1
reg={k:[f,{a:g(k)*v for a,v in c.items()}] for k,(f,c) in init.items()}
mv=collections.Counter(); sc=collections.Counter(); worst=0; asc=desc=0; own=set(); halv_by=collections.Counter()
for op in prog:
    if op[0]=='INIT': reg[op[1]]=[op[2],{a:g(op[1])*v for a,v in op[3].items()}]; own.add(op[1])
    elif op[0]=='MOVE':
        r=op[1]; a,b=fd(reg[r][0]),fd(op[2]); reg[r][0]=op[2]
        if r in own: asc+=max(0,b-a); desc+=max(0,a-b)
    elif op[0]=='CLEAR': del reg[op[1]]; own.discard(op[1])
    elif op[0]=='ADD':
        r,c,s=op[1],op[2],op[3]; c2=g(r)/g(s)*Fr(c); k=v2(c2); sc[min(k,1)]+=1
        if k<0: halv_by[(r[0],s[0],fd(reg[r][0]))]+=1
        for a,v in reg[s][1].items(): reg[r][1][a]=reg[r][1].get(a,0)+c2*v
        reg[r][1]={a:v for a,v in reg[r][1].items() if v!=0}
        worst=min(worst,min([v2(v) for v in reg[r][1].values()] or [99]))
miss=sum(1 for r,(f,c) in tg.items() if reg[r][0]!=f or reg[r][1]!={a:g(r)*v for a,v in c.items()})
print(sys.argv[1],'min v2 over run',worst,'| scalar v2 classes',dict(sc),'| owned asc',asc,'desc',desc,'| target misses',miss)
print(' halving ADDs by (dst type, src type, chart dim):',sorted(halv_by.items(),key=lambda t:-t[1])[:12])
