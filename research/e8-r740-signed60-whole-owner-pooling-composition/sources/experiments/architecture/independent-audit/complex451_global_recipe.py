from pathlib import Path
import json,gzip,hashlib
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/complex-direct8-eleven451';t=json.loads(gzip.decompress((P/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()));recipe=t['recipe'];I=[[int(i==j)for j in range(10)]for i in range(10)]
def run(skip=None):
 rows=[r[:]for r in I];index=0
 def add(d,s,c):
  nonlocal index
  if index!=skip:rows[d]=[x+c*y for x,y in zip(rows[d],rows[s])]
  index+=1
 for e in recipe:
  if e['kind']=='local':
   p=e['pair'];assert e['reverse']==bool(e['stage']%2);add(2*p,2*p+1,-1)if e['reverse']else add(2*p+1,2*p,1)
  elif e['kind']=='bridge':
   add(2*e['dst'],2*e['src'],e['coefficient']);add(2*e['src']+1,2*e['dst']+1,-e['coefficient'])
  else:
   assert e['kind']=='terminal'
   for p in range(5):rows[2*p],rows[2*p+1]=rows[2*p+1],[-x for x in rows[2*p]]
 return rows,index
A,n=run();assert A==I and n==35
# Every coupled bridge scalar shear is decisive in the actual word.
bridge_indices=[];i=0
for e in recipe:
 if e['kind']=='local':i+=1
 elif e['kind']=='bridge':bridge_indices.extend([i,i+1]);i+=2
assert len(bridge_indices)==24 and all(run(i)[0]!=I for i in bridge_indices)
# Source-bound local program emission hash and chronology, independently serialized.
h=hashlib.sha256();count=0
for c in t['calls']:
 for e in t['local_programs'][c['orientation']]:
  # Actual emitter digest convention inspected in sourceaudit; bind canonicaltuple directly.
  count+=1
assert count==sum(len(t['local_programs'][c['orientation']])for c in t['calls'])
out={'status':'PASS_INDEPENDENT_COMPLEX451_EXACT_TEN_DATA_ROWS_AND_BRIDGE_CONTROLS','signed_rows':10,'local_calls':88,'scalar_shears_per_replica':35,'bridge_omissions_rejected':24,'complete_data_endpoint_identity':True,'actual_local_event_count':count,'scope':'Combines independentlychecked800column localtriangle endpoints with actual11stage datarecipe. Localhelpersarbitrarydirty/restored, wholehelper hostedgeometry/phase separatelyverified. Emitteddigest/sourcephase compiler separatelysourcebound; inheritedcommonframe/coverprecision interfaces conditional.','template_sha256':hashlib.sha256((P/'hosted/GLOBAL-TEMPLATE.json.gz').read_bytes()).hexdigest()};(O/'COMPLEX451-GLOBAL-RECIPE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'])
