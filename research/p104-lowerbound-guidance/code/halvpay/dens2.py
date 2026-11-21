# HALVPAY dens2.py: which ops create den-4 values (own code)
import pickle, collections, sys
from fractions import Fraction as Fr
d=pickle.load(open(sys.argv[1],'rb')); prog=d['prog']; init=d['init']
def v2(x):
    x=Fr(x); n,dd=x.numerator,x.denominator; k=0
    if n==0: return 99
    while n%2==0: n//=2; k+=1
    while dd%2==0: dd//=2; k-=1
    return k
reg={k:[f,dict(c)] for k,(f,c) in init.items()}
first=collections.Counter(); ex=[]
for t,op in enumerate(prog):
    if op[0]=='INIT': reg[op[1]]=[op[2],dict(op[3])]
    elif op[0]=='MOVE': reg[op[1]][0]=op[2]
    elif op[0]=='CLEAR': del reg[op[1]]
    elif op[0]=='ADD':
        r,c,s=op[1],op[2],op[3]
        before=min([v2(v) for v in reg[r][1].values()] or [99])
        for k,v in reg[s][1].items(): reg[r][1][k]=reg[r][1].get(k,0)+c*v
        reg[r][1]={k:v for k,v in reg[r][1].items() if v!=0}
        m=min([v2(v) for v in reg[r][1].values()] or [99])
        if m<-1 and before>=-1:
            first[(r[0],s[0],v2(c))]+=1
            if len(ex)<3: ex.append((t,op[:3],str(op[3]),{str(k):str(v) for k,v in list(reg[r][1].items())[:6]}))
print(first.most_common(20)); print(ex)
# U w-vectors
for t,op in enumerate(prog[:400]):
    if op[0]=='ADD' and op[1][0]=='U': print('U add scalar',op[2],op[3]); break
