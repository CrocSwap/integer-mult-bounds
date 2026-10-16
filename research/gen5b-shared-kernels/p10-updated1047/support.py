"""Portable immutable input and authored dependency contract. Never runs upstream code."""
from pathlib import Path
from functools import lru_cache
import gzip, hashlib, importlib.util, json, os, sys
HERE=Path(__file__).resolve().parent
INPUTS=Path(os.environ.get('P10U_INPUTS',str(HERE/'local-inputs'))).resolve()
SOURCE=INPUTS
OUTPUT=Path(os.environ.get('P10U_OUTPUT',str(HERE/'output'))).resolve()
HEAD='1b37957d1520c80b6ea796bf418e52be5109c2d4'
WORD_SHA='41b15c5ccf7d2afd66396f183579a02c66f0f31f5410ceeb2eb271393a84d494'
DEPENDENCIES={
 '../exact_intervals.py':'c261dd44838d4e36c68768a1023ac859677089464ab121cdb46b30c918679333',
 '../assembly_arithmetic.py':'f2f6293c31deb579ebbea19eeaa732c07304ce9c2cacd431685e2dd18d4b0d58',
 '../p10/arithmetic/price_candidate.py':'d9954dd13bb92da8ecbdbf937f438061af2f3afaf65f0fd82cd45d89b1fe4141',
 '../p10/closure/chart_rational.py':'e36c35be0d3aec9adeeca2b8f038cb4757ea2a0b685b40798d4574695bfe7355',
}
def require_assertions():
 if not __debug__:raise RuntimeError('Run without -O; assertions must be enabled.')
def out(*parts):
 p=OUTPUT.joinpath(*parts);p.parent.mkdir(parents=True,exist_ok=True);return p
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def check_bytes(raw,row):
 require_assertions()
 assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],row['path']
@lru_cache(None)
def pins():
 require_assertions();p=json.loads((HERE/'inputs.json').read_text());assert p['head']==HEAD
 assert len({r['path']for r in p['files']})==len(p['files'])
 for r in p['files']:
  for key in ('path','local'):assert not Path(r[key]).is_absolute() and '..'not in Path(r[key]).parts
  assert r['url']==f"https://raw.githubusercontent.com/{p['repository']}/{HEAD}/{p['package']}{r['path']}"
  assert not r['local'].endswith('.py'),'Upstream programs must stay inert text.'
 return p
@lru_cache(None)
def read_bytes(name):
 row=next(r for r in pins()['files']if r['path']==name);raw=(INPUTS/row['local']).read_bytes();check_bytes(raw,row);return raw
def read(name):
 raw=read_bytes(name);return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def verify_inputs():
 require_assertions();return {r['path']:len(read_bytes(r['path']))for r in pins()['files']}
def verify_dependencies():
 require_assertions()
 for path,wanted in DEPENDENCIES.items():assert sha(HERE/path)==wanted,'Authored dependency changed: '+path
 return dict(DEPENDENCIES)
def load_authored(name,path):
 verify_dependencies();assert path in DEPENDENCIES
 spec=importlib.util.spec_from_file_location(name,HERE/path);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def materialize_word():
 require_assertions();base=read('bitword/selected/bit/word_p10.json.gz');d=json.loads((HERE/'witnesses/weighted890-delta.json').read_text())
 assert d['source_head']==HEAD and d['candidate_word_sha256']==WORD_SHA
 pairs=set(map(tuple,base['pairs']));remove=set(map(tuple,d['remove']));add=set(map(tuple,d['add']))
 assert len(remove)==len(add)==63 and remove<=pairs and not add&pairs
 base['pairs']=[list(x)for x in sorted((pairs-remove)|add)];base['reads'].update(d['reads_add'])
 assert len(base['pairs'])==len({a for a,b in base['pairs']})==len({b for a,b in base['pairs']})==890
 raw=json.dumps(base,sort_keys=True,separators=(',',':')).encode()+b'\n';assert hashlib.sha256(raw).hexdigest()==WORD_SHA
 path=out('matching','word_weighted890.json');path.write_bytes(raw);return path
