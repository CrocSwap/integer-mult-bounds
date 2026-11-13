"""Bounded source selection only; not another full selected recipe census."""
from pathlib import Path
from hashlib import sha256
import argparse
import atexit
import gzip
import importlib.util
import json
import subprocess
import sys
import tempfile

HERE=Path(__file__).resolve().parent
_cache=tempfile.TemporaryDirectory(prefix='move-source-select-')
atexit.register(_cache.cleanup)
sys.dont_write_bytecode=True;sys.pycache_prefix=str(Path(_cache.name)/'absent')
if not __debug__:raise RuntimeError('canonical compiler selection requires normal mode')
parser=argparse.ArgumentParser();parser.add_argument('repo',type=Path);args=parser.parse_args()
repo=args.repo
raw=subprocess.check_output(['git','show','e54523517d0f03e58352e647c403a5af3e525a57:research/shared-wire-split-composition/data/final.json.gz'],cwd=repo)
if len(raw)!=350722 or sha256(raw).hexdigest()!='2b94953dc14a122e3ef089633f05b58ec689ec5156feb7c784ed3e137dc01883':
    raise ValueError('selected source archive drift')
word=json.loads(gzip.decompress(raw))
path=HERE/'engines/reference/rank2/reference/source/clifford_exact.py'
source=path.read_bytes()
if sha256(source).hexdigest()!='2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962':
    raise ValueError('canonical compiler bytes drift')
spec=importlib.util.spec_from_file_location('bounded_move_selector',path)
c=importlib.util.module_from_spec(spec);sys.modules[spec.name]=c;spec.loader.exec_module(c)
seen=set()
for index,event in enumerate(word['program']):
    if event[0]!='MOVE':continue
    pair=tuple(event[2:4])
    if pair in seen:continue
    seen.add(pair);a,b=pair
    recipe,_=c.lower_child(c.canonical_frame(9,tuple(word['frames'][a])).adjoint().then(
                          c.canonical_frame(9,tuple(word['frames'][b]))))
    factors=(recipe['left'],recipe['right'])
    if any(side['offset'].bit_count()>=2 and side['phase'] for side in factors):
        out={'canonical_main':'e54523517d0f03e58352e647c403a5af3e525a57',
             'event_index':index,'event':event,'frames':{str(j):word['frames'][j] for j in pair},
             'recipe':recipe,'targeted_distinct_pairs_examined':len(seen),
             'source_compressed_sha256':sha256(raw).hexdigest(),
             'canonical_word_sha256':sha256(json.dumps(word,separators=(',',':'),sort_keys=True).encode()).hexdigest()}
        (HERE/'RECIPE.json').write_text(json.dumps(out,indent=2)+'\n')
        print(json.dumps(out,indent=2));break
    if len(seen)>=200:raise ValueError('no scoped candidate in first200 distinct pairs')
else:raise ValueError('no candidate')
