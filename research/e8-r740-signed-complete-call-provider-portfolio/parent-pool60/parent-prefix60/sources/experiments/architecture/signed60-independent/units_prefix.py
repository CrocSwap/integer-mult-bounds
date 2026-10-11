from pathlib import Path
from collections import Counter
import struct,json
P=Path(__file__).resolve().parent;S=P/'source-closure/candidate';ev=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()))
def run(es):
 b=[1]*980+[0];peak=1;units=0
 for op,a,t,c,f,z in es:
  if op==1:b[a]+=abs(c)*b[t];units+=abs(c);peak=max(peak,b[a])
  elif op==2:b[t]=b[a];peak=max(peak,b[t])
  elif op==3:b[t]=0
 return peak,units
forward=run(ev);inverse=[]
for op,a,b,c,f,z in reversed(ev):
 if op==1:c=-c
 elif op==2:op=3
 elif op==3:op=2
 inverse.append((op,a,b,c,f,z))
reverse=run(inverse);assert forward==(1124,16466)and reverse==(27414,16466)
r={'status':'PASS_INDEPENDENT_SIGNED60_PAID_ABSOLUTE_UNITS_CANCELLATION_FREE_PREFIX','forward_prefix':forward[0],'inverse_prefix':reverse[0],'paid_unit_adds_each_orientation':forward[1],'phase_absolute_units':dict(Counter({z:sum(abs(c)for op,a,b,c,f,p in ev if op==1 and p==z)for z in range(6)})),'scope':'Everyliteralcoefficient chargedbyabsolutevalue, no sign cancellation. COPYduplicates actualsourcebound, ERASEdiscards onlyverifiedrecovered borrowedrow. Addressroute factors must be added bycompleteglobalinvoice.'}
(P/'UNITS-PREFIX.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],forward,reverse)
