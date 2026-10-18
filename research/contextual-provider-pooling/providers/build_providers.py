"""Rebuild frozen rank-5 promotion providers from the TN27 epoch word."""
import argparse,gzip,hashlib,json,shutil,subprocess,sys
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--input',required=True);ap.add_argument('--gk-dir',required=True);ap.add_argument('--out',required=True);ap.add_argument('--audit',action='store_true');a=ap.parse_args()
here=Path(__file__).resolve().parent
registry=json.loads((here/'VARIANTS.json').read_text())
def digest(path):
 w=json.loads(gzip.decompress(Path(path).read_bytes()))
 return hashlib.sha256(json.dumps(w,sort_keys=True,separators=(',',':')).encode()).hexdigest()
assert digest(a.input)==registry['p0']['word_semantic_sha256'],'wrong epoch source'
out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
for name,item in registry.items():
 dest=out/name
 if name=='p0':
  dest.mkdir();shutil.copyfile(a.input,dest/'FULL-WORD.json.gz')
  (dest/'PROMOTION.json').write_text(json.dumps({'changes':[]})+'\n')
 else:
  subprocess.run([sys.executable,'-B',str(here/'build_promoted_epoch.py'),'--input',a.input,'--gk-dir',a.gk_dir,'--promotion',str(here/'PROMOTION.json'),'--out',str(dest),'--pivots',','.join(map(str,item['pivots']))],check=True)
 assert digest(dest/'FULL-WORD.json.gz')==item['word_semantic_sha256'],('output pin',name)
 if a.audit:
  subprocess.run([sys.executable,'-B',str(here/'audit_promoted_scalar.py'),str(dest/'FULL-WORD.json.gz'),str(dest/'PROMOTION.json'),str(dest/'SCALAR-AUDIT.json')],check=True)
(out/'REGISTRY.json').write_text(json.dumps({'status':'PASS_CANONICAL_SOURCE_AND_VARIANT_PINS','variants':registry,'scalar_replayed':a.audit},indent=2)+'\n')
print('PASS',out)
