import sys
from lcabound import run_prefix
X={(('X',),):1};Y={(('Y',),):1}
for k in range(1,34):
    R=max((k-1).bit_length(),1)+3
    PX={tuple(range(k-1,-1,-1))+(('X',),):1}
    row=[]
    for s in (1,-1):
        for name,a,b in (('00',None,None),('X0',X,None),('0Y',None,Y),('XY',X,Y),('XPX',X,PX)):
            row.append(f"{'+' if s>0 else '-'}{name}={run_prefix(k,s,a,b,R)}")
    print(k,(k-1).bit_length(),' '.join(row))
