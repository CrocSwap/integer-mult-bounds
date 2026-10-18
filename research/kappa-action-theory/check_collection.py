"""Read-only structural/integrity check. This is not a mathematical proof checker."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parent
def need(ok,message):
 if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 rows=json.loads((ROOT/'THEOREMS.json').read_bytes())
 need(len(rows)==400,'expected exactly 400 theorem records')
 ids={r['id']for r in rows};need(len(ids)==400,'duplicate IDs')
 expected={f'{p}{i:03d}'for p in 'NPTA'for i in range(1,101)}
 need(ids==expected,'wrong ID set')
 table={r['id']:r for r in rows};active=set();done=set()
 def visit(ident):
  if ident in done:return
  need(ident not in active,'cyclic dependency '+ident);active.add(ident)
  for dep in table[ident]['dependencies']:
   need(dep in ids,'missing dependency '+dep);visit(dep)
  active.remove(ident);done.add(ident)
 volumes={}
 for r in rows:
  for key in ['title','statement','proof','action','frontier_target','proof_status','novelty']:
   need(bool(r.get(key)),f"missing {key}: {r['id']}")
  need(r['proof_status']=='informal_proved','nonproved entry '+r['id'])
  need(len(r['proof'].split())>=25,'empty/placeholder proof '+r['id'])
  need(hashlib.sha256(r['proof'].encode()).hexdigest()==r['proof_sha256'],'proof hash '+r['id'])
  need('\\n'not in r['proof'],'literal newline escape '+r['id'])
  if r['volume']not in volumes:volumes[r['volume']]=(ROOT/r['volume']).read_text(encoding='utf-8')
  s=volumes[r['volume']]
  need(s.count(f'<a id="{r["anchor"]}"></a>')==1,'bad anchor '+r['id'])
  need(r['statement']in s and r['proof']in s,'proof/statement text mismatch '+r['id'])
  visit(r['id'])
 for prefix,rel in zip('NPTA',['volumes/01-native.md','volumes/02-physical.md','volumes/03-tensor.md','volumes/04-analytic.md']):
  s=volumes[rel]
  headings=re.findall(r'^### ('+prefix+r'\d{3})[ .-]',s,re.M)
  need(headings==[f'{prefix}{i:03d}'for i in range(1,101)],'volume heading sequence '+rel)
  need(len(re.findall(r'^\*\*Proof\.\*\*',s,re.M))==100,'proof count '+rel)
  need(len(re.findall(r'^\*\*(?:Statement|Theorem)\.\*\*',s,re.M))==100,'statement count '+rel)
 for name in ['ANALYTIC-self-review.md','NATIVE-self-review.md','PHYSICAL-self-review.md','TENSOR-self-review.md','TENSOR-reviews-ANALYTIC.md','PHYSICAL-reviews-NATIVE.md','ROOT-reviews-PHYSICAL.md','NATIVE-reviews-TENSOR.md']:
  need((ROOT/'reviews'/name).is_file(),'missing review '+name)
 # Public text should retain Unicode and ordinary prose spacing; exact identifiers are permitted.
 for p in ROOT.rglob('*'):
  if p.is_file():
   need(p.suffix.lower()not in ['.lean','.olean','.zip','.rar','.exe','.dll','.log'],'unexpected artifact '+p.name)
   need(p.stat().st_size<25*1024*1024,'oversize '+p.name)
   if p.suffix.lower()in ['.md','.json','.txt','.py']or p.name=='NOTICE':
    s=p.read_text(encoding='utf-8');need('\ufffd'not in s,'replacement character '+p.name)
    need(('C:/'+'Users/')not in s and ('C:'+'\\Users\\')not in s,'personal host path '+p.name)
 # File hashes protect prose bytes, not mathematical truth.
 if '--structure-only'not in sys.argv:
  manifest=json.loads((ROOT/'MANIFEST.json').read_bytes())
  actual={p.relative_to(ROOT).as_posix()for p in ROOT.rglob('*')if p.is_file()and p.name!='MANIFEST.json'}
  need(actual=={r['path']for r in manifest['files']},'manifest file-set mismatch')
  for r in manifest['files']:
   p=ROOT/r['path'];need(p.stat().st_size==r['bytes']and digest(p)==r['sha256'],'manifest hash '+r['path'])
 print('PASS_COLLECTION_STRUCTURE theorems=400 volumes=4 proofs=400 dependency_graph=acyclic reviews=8')
 if '--structure-only'not in sys.argv:print('PASS_SEALED_FILE_HASHES mathematical_verification=not_claimed')
if __name__=='__main__':
 try:check()
 except (ValueError,KeyError,OSError,json.JSONDecodeError)as e:
  print('FAIL_COLLECTION',str(e));sys.exit(1)
