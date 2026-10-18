"""Numeric input-column D oracle; no producer or row-engine imports."""
def columns(gates,n):
 out=[]
 flat=[(d,s) for _,d,ss in gates for s in ss]
 for j in range(n):
  state=1<<j
  for d,s in flat:
   if state>>s&1:state^=1<<d
  out.append(state)
 return out

def inspect(gates,v,R):
 n=2*v+R;out=columns(gates,n);mask=(1<<v)-1;N=[0]*v
 for j,state in enumerate(out):
  delta=state^(1<<j)
  if j<2*v:
   if delta:raise ValueError('independent source/target column changed')
  else:
   if delta&~(mask<<v):raise ValueError('independent helper restoration failed')
   for t in range(v):
    if delta>>(v+t)&1:N[t]|=1<<(j-2*v)
 return N
