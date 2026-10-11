from pathlib import Path
from collections import Counter
import json,gzip,struct,hashlib
P=Path(__file__).resolve().parent;S=P/'source-closure/candidate';B=P/'source-closure/base95'
f=json.loads((S/'records/frames.json').read_text())['frames'];w=json.loads((B/'word.json').read_text());pairs=json.loads((S/'PAIR-SELECTION.json').read_text())['pairs']
def contained(a,b):return all(sum(x*y for x,y in zip(u,v))==0 for u in f[str(a)]['B']for v in f[str(b)]['A'])
def plus(a,b,c=1):
 for k,v in b.items():
  z=a.get(k,0)+c*v
  if z:a[k]=z
  else:a.pop(k,None)
rows=[{i:1}for i in range(981)];ev=list(struct.iter_unpack('<6i',(B/'signed-records.bin').read_bytes())); deliveries={}
for i,(op,a,b,c,frame,phase)in enumerate(ev):
 if op==1:
  if phase==4 and 120<=a<240:deliveries[i]=(a,b,c,frame,dict(rows[b]))
  plus(rows[a],rows[b],c)
 elif op==2:rows[b]=dict(rows[a])
 elif op==3:assert rows[a]==rows[b];rows[b]={}
receivers={e['receiver']for e in pairs};donors={e['donor']for e in pairs};assert receivers.isdisjoint(donors)
out=[]
for e in pairs:
 u,v,G=e['receiver'],e['donor'],e['frame'];du=[(i,x)for i,x in deliveries.items()if x[0]==v and x[3]==G];assert du;cut=max(i for i,x in du)
 rp={};dp={};ru=[];dv=[]
 for i,(a,b,c,F,row)in deliveries.items():
  if a==u and contained(F,G):plus(rp,row,c);ru.append((i,F,b,c))
  if a==v and i<=cut:plus(dp,row,c);dv.append((i,F,b,c))
 assert rp==dp and rp
 assert all(contained(F,G)for i,F,b,c in dv)
 assert not any(a==v and i>cut and contained(F,G)for i,(a,b,c,F,row)in deliveries.items())
 out.append({'receiver':u,'donor':v,'delivery_frame':G,'donor_last_delivery_cut':cut,'receiver_removed_events':ru,'donor_prefix_events':dv,'equal_actual980_column_prefix':True,'max_receiver_prefix_strictly_smaller_frame':max(f[str(F)]['dim']for i,F,b,c in ru)<f[str(G)]['dim'],'receiver_prefix_strictly_smaller_frame':any(f[str(F)]['dim']<f[str(G)]['dim']for i,F,b,c in ru)})
r={'status':'PASS_INDEPENDENT_ALL60_CHRONOLOGICAL_EXACT_PREFIXES_UNCHANGED_DONORS','pairs':out,'receivers_distinct':len(receivers)==60,'donor_roles':len(donors),'receiver_donor_disjoint':True,'scope':'Actualoriginalsigned95delivery helperVALUES independently propagated through chronologicalADDs; each removedreceiverprefix equalsdonorcompleteprefix atlastGdelivery onall980integercolumns. Shared donors receive no targetprecondition/scatter rewrite because receiver/donor setsdisjoint. Newdelivery commonG andreflectedroute fullarraygate requireseparateaddresscertificate.'}
(P/'PREFIX.json').write_text(json.dumps(r,indent=2)+'\n');print(r['status'],sum(x['receiver_prefix_strictly_smaller_frame']for x in out))
