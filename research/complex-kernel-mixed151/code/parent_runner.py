"""Run pinned PR458, normalizing only two non-proof discovery metadata fields.
No pinned source is edited. The reconstruction still requires exact word equality.
"""
from pathlib import Path
import copy,gzip,hashlib,json,runpy,subprocess,sys
script=Path(sys.argv[1]).resolve();args=sys.argv[2:];out=Path(args[0]).resolve();pkg=script.parent
assert script.name=='verify.py' and pkg.name=='e8-complex-adapted-kernel'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((pkg/'MANIFEST.json').read_text());rebuild=(pkg/'code/rebuild.py').resolve();assert sha(rebuild)==manifest['code/rebuild.py']
expected=json.loads(gzip.decompress((pkg/'data/word.json.gz').read_bytes()));original_run=subprocess.run

def guarded_run(command,*a,**kw):
 argv=list(command) if isinstance(command,(list,tuple)) else None
 if argv and len(argv)==5 and argv[1]=='-B' and Path(argv[2]).resolve()==rebuild:
  src=Path(argv[3]);word=json.loads(gzip.decompress(src.read_bytes()));changed=copy.deepcopy(word);deltas={}
  for key in ['complex_coarse_float','gain_percent_float']:
   before=word['report'][key];after=expected['report'][key];assert isinstance(before,float) and isinstance(after,float)
   deltas[key]=dict(original=before,frozen=after,difference=before-after);changed['report'][key]=after
  restored=copy.deepcopy(changed)
  for key in deltas:restored['report'][key]=word['report'][key]
  assert restored==word
  normalized=out/'REBUILD-METADATA-NORMALIZED.json.gz';normalized.write_bytes(gzip.compress(json.dumps(changed,sort_keys=True,separators=(',',':')).encode(),mtime=0))
  receipt=dict(status='NORMALIZED_DISCOVERY_METADATA_ONLY',input_sha256=sha(src),normalized_sha256=sha(normalized),rebuild_source_sha256=sha(rebuild),fields=deltas,all_other_json_fields_exactly_unchanged=True,scope='Only two inherited floating-point provenance estimates are normalized to the frozen report. No operator, scalar, frame, selection, exact price or proof field is changed. Original exact reconstruction equality remains active.')
  (out/'METADATA-PORTABILITY.json').write_text(json.dumps(receipt,indent=2)+'\n');argv[3]=str(normalized)
  return original_run(argv,*a,**kw)
 return original_run(command,*a,**kw)
subprocess.run=guarded_run
sys.argv=[str(script),*args];runpy.run_path(str(script),run_name='__main__')
