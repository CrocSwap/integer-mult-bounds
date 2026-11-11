"""Portable pinned inert input and generated-output contract. Standard library only."""
from pathlib import Path
from functools import lru_cache
import os,json,hashlib,gzip
HERE=Path(__file__).resolve().parent
INPUTS=Path(os.environ.get('P10_INPUTS',str(HERE/'local-inputs'))).resolve()
SOURCE=INPUTS
OUTPUT=Path(os.environ.get('P10_OUTPUT',str(HERE/'output'))).resolve()
HEAD='e983fea0896b2a1d7355983674db7e9bb33a9e32'
def out(*parts):
 p=OUTPUT.joinpath(*parts);p.parent.mkdir(parents=True,exist_ok=True);return p
@lru_cache(None)
def pins():
 p=json.loads((HERE/'inputs.json').read_text());assert p['head']==HEAD;return p
@lru_cache(None)
def read_bytes(name):
 row=next(r for r in pins()['files']if r['path']==name);raw=(INPUTS/row['local']).read_bytes()
 assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],name
 return raw
def read(name):
 raw=read_bytes(name)
 return json.loads(gzip.decompress(raw)if name.endswith('.gz')else raw)
def verify_inputs():
 if not __debug__:raise RuntimeError('Run without -O; assertions are required.')
 return {r['path']:dict(bytes=len(read_bytes(r['path'])),git_blob=r['git_blob'],sha256=r['sha256'],url=r['url'])for r in pins()['files']}
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def materialize_word():
 base=read('bitword/selected/bit/word_p10.json.gz');delta=json.loads((HERE/'witnesses/weighted892-delta.json').read_text())
 assert delta['source_head']==HEAD
 pairs=set(map(tuple,base['pairs']));remove=set(map(tuple,delta['remove']));add=set(map(tuple,delta['add']))
 assert len(remove)==71 and len(add)==73 and remove<=pairs and not(add&pairs)
 base['pairs']=[list(x)for x in sorted((pairs-remove)|add)];base['reads'].update(delta['reads_add'])
 assert len(base['pairs'])==892 and len({p[0]for p in base['pairs']})==len({p[1]for p in base['pairs']})==892
 raw=json.dumps(base,sort_keys=True,separators=(',',':')).encode()+b'\n'
 assert hashlib.sha256(raw).hexdigest()==delta['candidate_word_sha256']
 path=out('matching','word_weighted892.json');path.write_bytes(raw);return path
