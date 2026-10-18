"""Apply the frozen joint frame refit to the pinned PR1195 fusion word; native replay validates it."""
import argparse,gzip,json
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--recipe',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();w=json.loads(gzip.decompress(a.base.read_bytes()));rc=json.loads(a.recipe.read_text())
for k,v in rc.items():assert w[k]==v['old'],k;w[k]=v['new']
a.out.write_bytes(gzip.compress(json.dumps(w,sort_keys=True,separators=(',',':')).encode(),mtime=0));print('REBUILT_MIXED_FUSION_WORD')
