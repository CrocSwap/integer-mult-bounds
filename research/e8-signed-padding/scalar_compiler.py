"""Exact PR390 scalar coefficient expansion; original supplier notices retained."""
from fractions import Fraction as Q

def lower_scalar(e):
 if e[0] in ['copy','clear']:return [e]
 assert e[0]=='add';t,src,a,b=e[1:];assert t!=src and t[0]!='W' and src[0]!='W'
 W=('W',0);out=[('clear',W)]
 for bit in bin(abs(a))[2:]:
  out.append(('double',W))
  if bit=='1':out.append(('accumulate',W,src,1))
 for prime,tag in [(2,'halve'),(3,'divide3')]:
  while b%prime==0:b//=prime;out.append((tag,W))
 assert b==1
 return out+[('accumulate',t,W,1 if a>0 else -1),('clear',W)]

def primitive_bound(e):return len(lower_scalar(e))

def check_lowered_coefficient(a,b):
 t,src,W=('L',0),('L',1),('W',0);state={t:[Q(1),Q(0)],src:[Q(0),Q(1)],W:[Q(0),Q(0)]}
 for op in lower_scalar(('add',t,src,a,b)):
  tag,r=op[:2]
  if tag=='clear':state[r]=[Q(0),Q(0)]
  elif tag=='accumulate':state[r]=[x+op[3]*y for x,y in zip(state[r],state[op[2]])]
  else:
   scale={'double':Q(2),'halve':Q(1,2),'divide3':Q(1,3)}[tag];state[r]=[scale*x for x in state[r]]
 assert state[t]==[Q(1),Q(a,b)] and state[src]==[Q(0),Q(1)] and state[W]==[Q(0),Q(0)]
