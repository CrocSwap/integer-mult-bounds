"""Metadata-only written freeze then actual ten-stage parent binding."""
import argparse,ast,hashlib,json,subprocess,sys
from datetime import datetime,timezone
from pathlib import Path
sys.set_int_max_str_digits(100000)
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
HEAD='739c3bb0ad0596f427e0a72a2ebeca23277217a3'
IMPORT=ROOT/'work/tasks/R323-pr290-frontier-source'
BUDGET='work/tasks/R12-latest-replay/windows_budget.py'
RESOURCES={'seconds':120,'cpu':1,'memory_bytes':4*1024**3,'scratch_bytes':20*1024**2,'attempts':1,'cpu_affinity_mask':1024}
NAMES=('raw','bit','physical','global_result','kernel','scalar','primes','banks','complex','math','finite','verification')

def need(ok,why):
 if not ok:raise ValueError(why)

def pin(p):
 b=p.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def safe_path(name):
 need(type(name) is str and not Path(name).is_absolute(),'workspace relative closure path');p=(ROOT/name).resolve();need(p.is_relative_to(ROOT),'closure path containment');return p

def entries(v):
 need(type(v) in (dict,list),'explicit closure entries');out={};rows=v.items() if type(v) is dict else [(r.get('path'),r)for r in v]
 for name,item in rows:
  need(type(item) is dict and type(name) is str and item.get('path',name)==name and name not in out,'unique matching closure path');safe_path(name)
  need(type(item.get('bytes')) is int and item['bytes']>=0 and type(item.get('sha256')) is str and len(item['sha256'])==64,'exact closure pin');out[name]={'bytes':item['bytes'],'sha256':item['sha256']}
 return out

def auth(v):
 for name,wanted in v.items():need(pin(safe_path(name))==wanted,'closure changed: '+name)

def merge(out,v):
 for name,wanted in v.items():need(name not in out or out[name]==wanted,'conflicting closure: '+name);out[name]=wanted

def admission_guard(r):
 need(type(r) is dict and r.get('issuer')=='/root' and r.get('reviewer')=='/root' and r.get('full_finite_proof_admitted') is True and r.get('original_package_head')==HEAD and type(r.get('original_verifier_output_path')) is str,'actual accepted complete PR290 baseline prerequisite')
 for name in ('actual_artifacts','input_closure','source_files'):need(type(r.get(name)) in (dict,list),'actual accepted full parent closure')

def original_auth():
 records=json.loads((IMPORT/'source-import.json').read_bytes());need(records['head']==HEAD and len(records['files'])==136,'complete PR290 Git import')
 out={}
 for r in records['files']:
  p=IMPORT/r['path'];b=p.read_bytes();need(pin(p)=={'bytes':r['bytes'],'sha256':r['sha256']},'raw original SHA');need(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==r['git_blob_sha1'],'raw original Git blob');out[p.relative_to(ROOT).as_posix()]=pin(p)
 return out

def parent_contract(r,original):
 admission_guard(r);need(r.get('source_path') is not None and r.get('source')==pin(safe_path(r['source_path'])),'actual baseline source pin')
 baseline=json.loads(safe_path(r['source_path']).read_bytes());need(entries(r['input_closure'])==baseline['input_closure'] and entries(r['source_files'])==baseline['source_files'],'complete original parent input/source closure')
 auth(entries(r['input_closure']));auth(entries(r['source_files']));actual=entries(r['actual_artifacts']);auth(actual)
 directory=safe_path(r['original_verifier_output_path']);selected={}
 for name in NAMES:
  p=directory/(name+'.json');rel=p.relative_to(ROOT).as_posix();need(actual.get(rel)==pin(p),'mandatory actual selected artifact '+name);json.loads(p.read_bytes());selected[name]={'path':rel,**actual[rel]}
 vr=json.loads((directory/'verification.json').read_bytes());need(vr['fresh_stages']==sorted(['virtual','raw','bit','kernel','scalar','primes','banks','complex','math','finite']) and vr['inputs_unchanged'] is True and vr['status']=='PASS_IMMUTABLE_GEN5_KERNEL_ENTRIES_FIVE_STAGE_BANKED_CONSTRUCTION','complete original ten-stage verifier result')
 # Authenticate exact original copied package through its original source lock,
 # while accommodating the baseline launcher's source-qualified private path.
 need(type(baseline.get('package_files')) is dict and type(baseline.get('git_blobs')) is dict and len(baseline['package_files'])==136,'complete baseline original package map')
 source_import=json.loads((IMPORT/'source-import.json').read_bytes())
 for rec in source_import['files']:
  rel=rec['repository_path'].removeprefix(source_import['prefix']);wanted={'bytes':rec['bytes'],'sha256':rec['sha256']}
  need(baseline['package_files'].get(rel)==wanted and baseline['git_blobs'].get(rel)==rec['git_blob_sha1'],'baseline package matches PR290 raw original')
  copied=safe_path(r['source_path']).parent/'package'/rel;b=copied.read_bytes();need(pin(copied)==wanted and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==rec['git_blob_sha1'],'actual baseline copied original Git closure')
 return baseline,actual,selected

def authenticate_source(s):
 need(s.get('actual_parent_admitted') is True,'actual admitted parent gate');auth(s['input_closure']);auth(s['source_files'])
 need(pin(Path(sys.executable))==s['runtime']['file'] and sys.version==s['runtime']['version'],'runtime identity')
 r=json.loads(safe_path(s['parent_receipt_path']).read_bytes());baseline,actual,selected=parent_contract(r,original_auth())
 need(actual==s['parent_actual_artifacts'],'unchanged admitted artifact inventory')
 for name,value in selected.items():need(s['actual_inputs'][name]==value,'selected artifact equals admitted parent pin')
 need(s['actual_inputs']['parent']=={'path':s['parent_receipt_path'],**pin(safe_path(s['parent_receipt_path']))},'actual parent input pin')

def write(p,d):
 with p.open('x',encoding='utf-8')as f:json.dump(d,f,sort_keys=True,indent=2);f.write('\n')

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--parent-receipt',type=Path);ap.add_argument('--parent-sha256');a=ap.parse_args()
 if a.parent_receipt is None:
  need(a.parent_sha256 is None and not (HERE/'WRITTEN_SOURCE.json').exists(),'unique source-only preparation')
  ledger=ROOT/'outputs/research-framework/task-ledger.json';json.loads(ledger.read_bytes());(HERE/'ledger-context.json').write_bytes(ledger.read_bytes())
  own={}
  for p in sorted(HERE.iterdir()):
   if p.is_file():
    if p.suffix=='.py':compile(ast.parse(p.read_text(encoding='utf-8')),str(p),'exec')
    own[p.relative_to(ROOT).as_posix()]=pin(p)
  inputs=original_auth()
  upstream=json.loads((IMPORT/'SOURCE.json').read_bytes());need(pin(IMPORT/'SOURCE.json')['sha256']=='dae4860b01266da5e5c1d6fdc9655060b3bb68a94bccf362ad8bf1cf2d2d35b1','pinned R323 qualification source')
  for group in ('source_files','input_closure'):auth(upstream[group]);merge(inputs,upstream[group])
  for rel in ('AGENTS.md','outputs/research-framework/AGENTS.md','work/tasks/R323-pr290-frontier-source/SOURCE.json','work/tasks/R323-pr290-frontier-source/REPORT.md','work/tasks/R323-pr290-frontier-source/source-import.json','work/tasks/R312-pr287-arithmetic-refinement-revision/SOURCE.json','outputs/research-framework/evidence/structural-pr287-arithmetic-refinement-terminal-001.json','outputs/research-framework/evidence/structural-pr287-arithmetic-refinement-revision-review-001.json',BUDGET):inputs[rel]=pin(safe_path(rel))
  old=json.loads(safe_path('work/tasks/R312-pr287-arithmetic-refinement-revision/SOURCE.json').read_bytes());auth(old['source_files']);merge(inputs,old['source_files'])
  need(inputs[BUDGET]['sha256']=='5cca39fbac05197c30f22911891984c3627c393d7b4472117e16db046e0a6177','budget helper pin')
  head=subprocess.check_output(['git','-C',str(ROOT/'work/integer-mult-bounds'),'rev-parse','HEAD'],text=True).strip();need(head=='d1d6c070f5a8c684727ee7ec35d930f9ebfa9758','reference read-only head')
  runtime={'path':sys.executable,'version':sys.version,'file':pin(Path(sys.executable))};need(runtime['file']['sha256']=='10d845f50a2af64e3500bb2fcb348b5bc98a75d8ddada63e45ba1da6a1fc79d1','runtime identity')
  s={'schema':'R325-pr290-written-arithmetic-v001','task':'R325','author':'/root/native_module_review','status':'WRITTEN_UNRUN_PENDING_ACTUAL_TEN_STAGE_ADMISSION','source_files':own,'input_closure':inputs,'runtime':runtime,'budget_helper':BUDGET,'resources':RESOURCES,'original_package_head':HEAD,'actual_parent_admitted':False,'actual_inputs':None,'controls_prepared':27,'scientific_execution':False,'scientific_imports':False,'disclosure':'Minimal R312 arithmetic adaptation. Both exact engines, outer47+7 and constant finite8 proof byte unchanged. Original 136 files immutable, original authors/license and AI notices preserved. Future complete parent proof and distinct review/root release required. No new value computed.','created_utc':datetime.now(timezone.utc).isoformat()}
  write(HERE/'WRITTEN_SOURCE.json',s);out=ROOT/'outputs/research-framework/evidence/structural-pr290-eight-level-arithmetic-preparation-001.json';write(out,{'task':'R325','source_path':(HERE/'WRITTEN_SOURCE.json').relative_to(ROOT).as_posix(),'source':pin(HERE/'WRITTEN_SOURCE.json'),'status':s['status'],'controls_prepared':27,'resources':RESOURCES,'scientific_execution':False,'scientific_imports':False,'actual_parent_admitted':False,'scope':'complete source-only arithmetic adaptation, pending original ten-stage operator/bank/kernel parent; no numerical result'});print(json.dumps({'written_source':pin(HERE/'WRITTEN_SOURCE.json'),'receipt':pin(out)}));return
 need(type(a.parent_sha256)is str and pin(a.parent_receipt)['sha256']==a.parent_sha256,'actual parent SHA');s=json.loads((HERE/'WRITTEN_SOURCE.json').read_bytes());auth(s['source_files']);auth(s['input_closure']);r=json.loads(a.parent_receipt.read_bytes());baseline,actual,selected=parent_contract(r,original_auth())
 parent_path=a.parent_receipt.resolve().relative_to(ROOT).as_posix();selected['parent']={'path':parent_path,**pin(a.parent_receipt)};closure=dict(s['input_closure'])
 for v in (entries(r['input_closure']),entries(r['source_files']),actual,{parent_path:pin(a.parent_receipt),(HERE/'WRITTEN_SOURCE.json').relative_to(ROOT).as_posix():pin(HERE/'WRITTEN_SOURCE.json')}):merge(closure,v)
 s.update(actual_parent_admitted=True,actual_inputs=selected,parent_receipt_path=parent_path,parent_actual_artifacts=actual,input_closure=closure,status='SOURCE_BOUND_UNRUN_ROOT_RELEASE_REQUIRED');authenticate_source(s);write(HERE/'SOURCE.json',s);print(json.dumps({'source':pin(HERE/'SOURCE.json')}))

if __name__=='__main__':main()
