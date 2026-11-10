"""One-time capsule creation from the independently completed source-bound run."""
from pathlib import Path
import argparse,json,hashlib,sys
sys.set_int_max_str_digits(500000)
P=Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--native-source',type=Path,required=True)
ap.add_argument('--native-work',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args()
source=a.native_source.resolve();run=a.native_work.resolve()
b=json.loads((P/'frontier_fusion/NATIVE-ADMISSION-BINDING.json').read_text())
def normalized(x):
 if isinstance(x,dict):return {k:normalized(v)for k,v in x.items()if k not in {'seconds','log_sha256'}}
 if isinstance(x,list):
  y=[normalized(v)for v in x]
  return sorted(y,key=lambda v:v['name']) if y and all(isinstance(v,dict)and'name'in v and'exit_code'in v for v in y) else y
 if isinstance(x,str):return x.replace(str(run),'{native-work}').replace(str(source),'{native-source}')
 return x
out={'schema':'phase-fusion-native-receipt-capsule/1','scope':'Canonical semantic hashes of the completed native JSON receipts. Elapsed seconds, stage-log digests, and the two root directory prefixes are normalized; concurrent named stage records are sorted. Actual current stage-log hashes are checked separately. Log byte hashes identify the historical run but are not compared across fresh runs.','source_commit':b['source_head'],'source_manifest_sha256':b['source_manifest_sha256'],'receipts':[]}
for rel,raw in b['receipt_sha256'].items():
 if rel.startswith('target002_upstream/full-1661-verification/'):
  kind='native_work';r=rel.removeprefix('target002_upstream/full-1661-verification/');f=run/r
 else:
  prefix='target002_upstream/pr1661/research/gmx-t74-p566-ep400/'
  assert rel.startswith(prefix);kind='native_source';r=rel.removeprefix(prefix);f=source/r
 blob=f.read_bytes();assert hashlib.sha256(blob).hexdigest()==raw
 row={'root':kind,'path':r,'historical_sha256':raw}
 if f.suffix=='.json':row['semantic_sha256']=hashlib.sha256(json.dumps(normalized(json.loads(blob)),sort_keys=True,separators=(',',':')).encode()).hexdigest()
 out['receipts'].append(row)
a.output.write_text(json.dumps(out,indent=2)+'\n')
print(len(out['receipts']),'receipts',sum('semantic_sha256'in r for r in out['receipts']),'canonical JSON hashes')
