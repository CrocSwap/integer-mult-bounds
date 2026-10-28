#!/usr/bin/env python3
"""Full T360 replay with explicit, authenticated optional fresh-native reuse.

Adapted from PR3624 replay.py; exact upstream retained in PR3624-SOURCE.tar.gz.
Sources and native words are unchanged; only order/allocation/profile differ.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse,gzip,hashlib,json,os,subprocess,sys
from check_inputs import authenticate
from dependency import source
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def need(x,m):
 if not x:raise ValueError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def fill_binding(literal,admission):
 left,right=read(literal),read(admission)
 need(left==right,'complete literal/admission semantic equality')
 return {'literal_sha256':sha(literal),'admission_sha256':sha(admission),'literal_payload_sha256':hashlib.sha256(gzip.decompress(literal.read_bytes())).hexdigest(),'semantic_equality':True,'rows':len(left['rows'])}
def prepared_check(prepared):
 old=prepared/'predecessor';new=prepared/'changed'
 # Explicit prepared-source reuse must preserve every original materializer input.
 for name,row in read(ROOT/'research/t8-rank7-two-swaps/MATERIALIZE.json')['entries'].items():
  need(sha(old/name)==row['sha256'],'retained materializer file '+name)
 for name,digest in {'prepare_extension_native.py':'a2900b3a296f1273f75c6883bc4fe89a206368112efac774f381ab8d0fc79744','admit_extension.py':'86e6098e764198fef99d58494baaa3a44de0def3fbe7cea26d83c4942bf12d29'}.items():
  need(sha(new/name)==digest,'derived driver binding '+name)
 return True
def main():
 need(__debug__,'enabled assertions required by retained scientific engines');authenticate()
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);ap.add_argument('--prepared',type=Path);ap.add_argument('--native',type=Path);ap.add_argument('--allocation',type=Path);a=ap.parse_args()
 need(not a.work.exists(),'fresh replay output');work=a.work.resolve();work.mkdir();dep=source();stages=[]
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONINTMAXSTRDIGITS='0')
 for key in ['PYTHONPATH','PYTHONOPTIMIZE','WITNESS_SPEC','WITNESS_RECORD','WITNESS_DISCOVER']:env.pop(key,None)
 def run(name,cmd):
  with(work/(name+'.log')).open('w')as out:r=subprocess.run(cmd,env=env,stdout=out,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
  stages.append({'name':name,'command':cmd,'exit_code':r.returncode,'log_sha256':sha(work/(name+'.log'))});(work/'STAGES.json').write_text(json.dumps(stages,indent=2)+'\n');need(r.returncode==0,'failed '+name+'; inspect '+str(work/(name+'.log')));print('PASS',name,flush=True)
 prepared=a.prepared.resolve()if a.prepared else work/'prepared'
 if a.prepared is None:run('source-materialization',[sys.executable,'-B',str(dep/'replay.py'),'--t8-package',str(ROOT/'research/t8-rank7-two-swaps'),'--main-files',str(ROOT),'--work',str(prepared),'--materialize-only'])
 old=prepared/'predecessor';new=prepared/'changed'
 prepared_check(prepared)
 need(sha(new/'source/MANIFEST.json')=='318ede57c79d10323fb1918f7be4d451d1fcdac01c6456fe9851d51d05d59453','unchanged staged native source manifest')
 need(sha(old/'adapters/extension_blocknorm.py')=='6e6b8683cc87a84e5410c399b1128eb68694f852a3927cb124067f503ed7d7c7','original stock checker')
 allocation=a.allocation.resolve()if a.allocation else work/'allocation'
 if a.allocation is None:run('literal-construction',[sys.executable,'-B',str(P/'literal_build.py'),'--out',str(allocation),'--owner-check'])
 expected=read(P/'LITERAL-EXPECTED.json')
 for name,h in expected['literal_files'].items():need(sha(allocation/name)==h,'candidate literal input '+name)
 need(hashlib.sha256(gzip.decompress((allocation/'FILL.json.gz').read_bytes())).hexdigest()==expected['payload_sha256'],'literal semantic payload')
 native=a.native.resolve()if a.native else new/'native'
 if a.native is None:run('fresh-native',[sys.executable,'-B',str(new/'prepare_extension_native.py'),'--source',str(new/'source'),'--retained-cache',str(old/'native-cache'),'--retained-receipt',str(old/'NATIVE-RECEIPT.json'),'--out',str(native),'--jobs','1'])
 # Full admission independently authenticates source/cache/receipt and both words.
 native_receipt=read(native/'NATIVE-RECEIPT.json')
 run('independent-native-frame-owners',[sys.executable,'-B',str(P/'audit_entry.py'),str(allocation),str(native/'native-cache'),str(work/'INDEPENDENT-OWNERS.json')])
 fill=read(allocation/'FILL.json.gz');need(len(fill['rows'])==1321920,'complete candidate rows');fill['dispatch_overrides']=[]
 converted=work/'FILL-legacy.json.gz';converted.write_bytes(gzip.compress(json.dumps(fill,separators=(',',':')).encode(),mtime=0));need(read(converted)['rows']==read(allocation/'FILL.json.gz')['rows'],'legacy semantic conversion')
 (work/'FILL-BINDING.json').write_text(json.dumps(fill_binding(allocation/'FILL.json.gz',converted),indent=2)+'\n')
 cmd=[sys.executable,'-B',str(new/'admit_extension.py')]
 for key,val in {'source':new/'source','fill':converted,'order':allocation/'ORDER.json','dispatch':allocation/'DISPATCH.json','native-cache':native/'native-cache','native-receipt':native/'NATIVE-RECEIPT.json','work':work/'admission','replica-helper-dir':old/'helpers','reconstructor':old/'helpers/reconstruct_replica.py','comparison-claim':old/'PR2969-CLAIM.json','blocknorm-checker':old/'adapters/extension_blocknorm.py'}.items():cmd+=['--'+key,str(val)]
 cmd+=['--source-profile','staged3605','--comparison-profile','pr2969','--jobs','1'];run('full-admission',cmd)
 result=read(work/'admission/RESULT.json');need(result['status']=='PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE','complete release status')
 exp=read(P/'PRICE-EXPECTED.json');need(result['replicas']==360 and result['actual_expected_helpers']==408,'actual geometry');need(result['profile']==exp['profile'],'complete release profile')
 endpoint=Q(exp['root_interval'][0])-Q(1,10**46)-Q(1,10**70);need(Q(result['kappa'])==endpoint,'exact candidate endpoint');need(endpoint>Q(exp['comparator_root_interval'][1]),'strict improvement over latest pinned comparator')
 run('exact-price',[sys.executable,'-B',str(P/'price_check.py')])
 out={'status':'PASS_T360_JOIN_SWAP_COMPLETE_CONDITIONAL_RELEASE','kappa':str(endpoint),'kappa_decimal':result['kappa_decimal'],'comparator_pr':3624,'comparator_head':exp['comparator_head'],'replicas':360,'roles':1321920,'physical':323069,'profile':result['profile'],'fresh_native_reused':a.native is not None,'prepared_source_reused':a.prepared is not None,'native_receipt_sha256':sha(native/'NATIVE-RECEIPT.json'),'release_receipt_sha256':sha(work/'admission/release/RELEASE-RECEIPT.json'),'stages':stages,'scope':result['scope']}
 (work/'RESULT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],out['kappa_decimal'],flush=True)
if __name__=='__main__':main()
