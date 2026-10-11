from pathlib import Path
from collections import Counter
import json,gzip,hashlib
O=Path(__file__).resolve().parent;ROOT=O.parents[2];P=ROOT/'experiments/architecture/whole-owner-pooling-v4/bit60';B=ROOT/'experiments/architecture/pr454-signed-extra-v4/with-prefix60/global/hosted';tf=P/'GLOBAL-TEMPLATE.json.gz';blob=gzip.decompress(tf.read_bytes());T=json.loads(blob);Old=json.loads(gzip.decompress((B/'GLOBAL-TEMPLATE.json.gz').read_bytes()));N=json.load(open(P/'NOMINATION.json'));G=json.load(open(P/'GLOBAL.json'))
assert T['local_programs']==Old['local_programs'] and T['residual_isometries']==Old['residual_isometries'];assert T['source_record_sha256']==Old['source_record_sha256']
slots={(s,h):(i,cp,off,w)for i,cp,off,w,s,h in N['slots']};assert len(slots)==65120
ip={e['idx']:e['pair']for e in T['schedule']if e['kind']=='idle'}
digest=hashlib.sha256();count=0
for c in T['calls']:
 s,rep=c['stage'],c['replica'];owners=c['owners'];oldc=next(z for z in Old['calls']if z['stage']==s and z['replica']==rep);assert owners[:240]==oldc['owners'][:240] and c['local_hash']==oldc['local_hash']
 for h,owner in enumerate(owners[240:]):
  i,cp,off,w=slots[s,rep*740+h];hr,within=divmod(cp,240)
  assert owner==[hr*1200+ip[i]*240+within,['hosted',i,off,w]] and c['helper_owner_replicas'][h]==hr
 for z in T['local_programs'][c['orientation']]:
  if z[0]==0:m=[z[0],owners[z[1]],*z[2:]]
  else:m=[z[0],owners[z[1]],owners[z[2]]if z[2]<980 else[9600,['private',0]],*z[3:]]
  digest.update((json.dumps(m,separators=(',',':'))+'\n').encode());count+=1
assert digest.hexdigest()==G['emitted_program_sha256'] and count==G['emitted_events']
assert hashlib.sha256(blob).hexdigest()==G['template_sha256']
assert T['hosting']['slots']==N['slots']
out={'status':'PASS_INDEPENDENT_WHOLE_POOL_LITERAL_OWNER_TRANSPORT_AND_STREAM','template_sha256':hashlib.sha256(blob).hexdigest(),'emitted_program_sha256':digest.hexdigest(),'emitted_events':count,'complete_calls':88,'helper_owners':65120,'unchanged_local_programs':True,'unchanged_residual_isometries':True,'unchanged_data_owners_and_local_hashes':True,'source_files':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [tf,P/'GLOBAL.json',P/'NOMINATION.json',B/'GLOBAL-TEMPLATE.json.gz']},'scope':'Actual changed wholefamily ownertransport, full mappedinstructionstream/digest, source-program equality. No nativePR455rank147 provider imported. Concreteglobal sigma injection and retainedphysicaldirtyslot/allsizecompiler remain separate gates; no partial invocation splicing or helper payload splitting.'}
(O/'WHOLE-POOL60-BIT-TEMPLATE.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],count)
