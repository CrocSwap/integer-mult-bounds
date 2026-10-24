"""Independent literal-event interpreter for the frozen candidate review.
No imports from A emitter or upstream native_core. Normalized inherited source
warp semantics are a premise, not an independent physical audit of those warps.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from fractions import Fraction as Q
from collections import Counter

def need(v,m):
 if not v: raise ValueError(m)
def accumulate(dst,src,factor):
 for key,value in tuple(src.items()):
  result=dst.get(key,Q(0))+factor*value
  if result:dst[key]=result
  elif key in dst:del dst[key]
def owner(ref):
 kind,index=ref
 need(kind in ('C','L'),'Unknown owner kind')
 if kind=='C':need(index==0,'Only existing ownedC0');return 632
 need(0<=index<632,'Arbitrary persistent owner index');return index

def replay(c,program):
 states=[{(i,()):Q(1)} for i in range(632)]+[{}]
 frames=list(c['start'])+[None]
 bill=Counter();maximum=Q(1);events=Counter()
 for at,e in enumerate(program):
  kind=e[0];events[kind]+=1
  if kind=='scalar':
   gate,frame=e[1:];op=gate[0];dst=owner(gate[1])
   if op=='clear':
    need(dst==632,'Borrowed erasure');states[dst]={};frames[dst]=frame
   else:
    need(frames[dst]==frame,('Scalar target chart',at))
    if op in ('add','copy'):
     src=owner(gate[2]);need(frames[src]==frame,('Scalar source chart',at))
     if op=='copy':need(dst==632,'Borrowed overwrite');states[dst]=states[src].copy()
     else:
      need(src!=dst,'Self ADD')
      accumulate(states[dst],states[src],Q(gate[3],gate[4]))
    elif op=='scale':states[dst]={k:Q(gate[2],gate[3])*v for k,v in states[dst].items()}
    else:raise ValueError('Unknown scalar gate')
    maximum=max(maximum,sum(abs(v) for v in states[dst].values()))
  elif kind=='warp':
   _,ref,gate,start,end=e;dst=owner(ref)
   need(frames[dst]==start,('Warp source chart',at))
   updated={}
   for (i,word),v in states[dst].items():
    new=word[:-1] if word and word[-1]==-gate else word+(gate,)
    k=(i,new);updated[k]=updated.get(k,Q(0))+v
   states[dst]={k:v for k,v in updated.items() if v};frames[dst]=end
  elif kind=='climb':
   _,_,dst,start,end,r=e
   need(0<=dst<632,'Persistent climb owner')
   need(frames[dst]==start,('Climb source chart',at))
   need(r>0 and r==len(c['frames'][end])-len(c['frames'][start]),'Climb paid rank')
   frames[dst]=end;bill[r]+=1
  elif kind=='center':
   _,index,start,end,r=e;need(index==0,'Existing owned center only');dst=632
   need(frames[dst]==start,('Owned transport source chart',at))
   need(r==abs(len(c['frames'][end])-len(c['frames'][start])),'Owned Gaussian paid rank')
   bill[r]+=1;frames[dst]=end
  else:need(kind in ('phase','adapter','residual_adapter'),'Unknown literal event')
 need(frames[:632]==c['final'],'All632 output charts')
 need(not states[632],'Owned C0 returnedzero')
 return states,bill,maximum,events

def expected(F,back):
 out=[{(i,()):Q(1)} for i in range(632)]
 for i in range(112):
  for j in range(112):
   coeff=-F[j][i] if back else F[i][j]
   if coeff:accumulate(out[i if back else 112+i],{((112+j) if back else j,()):Q(1)},coeff)
 return out
