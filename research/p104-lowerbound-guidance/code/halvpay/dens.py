# HALVPAY dens.py: 2-adic profile of the FANOUT56 run values (own code)
import pickle, collections
from fractions import Fraction as Fr
d=pickle.load(open(__import__('sys').argv[1],'rb')); prog=d['prog']; init=d['init']
def v2(x):
    x=Fr(x); n,dd=x.numerator,x.denominator; k=0
    if n==0: return 99
    while n%2==0: n//=2; k+=1
    while dd%2==0: dd//=2; k-=1
    return k
reg={k:[f,dict(c)] for k,(f,c) in init.items()}
print('init regs',len(reg),collections.Counter(k[0] for k in reg))
print('init val min v2',collections.Counter(min([v2(v) for v in c.values()] or [99]) for f,c in reg.values()))
mind=collections.Counter(); worst=0; oddden=0
for t,op in enumerate(prog):
    if op[0]=='INIT': reg[op[1]]=[op[2],dict(op[3])]
    elif op[0]=='MOVE': reg[op[1]][0]=op[2]
    elif op[0]=='CLEAR': del reg[op[1]]
    elif op[0]=='ADD':
        r,c,s=op[1],op[2],op[3]
        for k,v in reg[s][1].items(): reg[r][1][k]=reg[r][1].get(k,0)+c*v
        reg[r][1]={k:v for k,v in reg[r][1].items() if v!=0}
        m=min([v2(v) for v in reg[r][1].values()] or [99]); mind[m]+=1
        oddden+=any(Fr(v).denominator%2==1 and Fr(v).denominator>1 for v in reg[r][1].values())
print('post-ADD min v2 of target value',sorted(mind.items())); print('ADDs leaving odd-denominator entries',oddden)
