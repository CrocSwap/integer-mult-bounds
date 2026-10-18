"""Input-column macro oracle; does not import the emitter or row engine."""
from fractions import Fraction as F

def primitive_columns(ops,n):
 out=[]
 for j in range(n):
  x=[F(int(i==j)) for i in range(n)]
  for z in ops:
   k,t=z[:2]
   if k=='copy':x[t]=x[z[2]]
   elif k=='clear':x[t]=F(0)
   elif k=='add':x[t]+=x[z[2]]
   elif k=='subtract':x[t]-=x[z[2]]
   elif k=='double':x[t]*=2
   elif k=='halve':x[t]/=2
   elif k=='negate':x[t]=-x[t]
   else:raise ValueError('unknown primitive')
  out.append(x)
 return out

def macro_columns(macros,n):
 result=[]
 for j in range(n):
  x={j:F(1)}
  for e in macros:
   if e[0]=='add':v=x.get(e[1],F(0))+F(e[3],e[4])*x.get(e[2],F(0))
   elif e[0]=='scale':v=F(e[2],e[3])*x.get(e[1],F(0))
   else:raise ValueError('unknown macro')
   if v:x[e[1]]=v
   else:x.pop(e[1],None)
  result.append(x)
 return result
