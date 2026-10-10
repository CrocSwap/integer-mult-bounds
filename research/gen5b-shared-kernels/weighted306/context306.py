"""Portable immutable inputs; only our authored sibling modules are imported."""
from pathlib import Path
import hashlib,json,os,sys
HERE=Path(__file__).resolve().parent;BASE=HERE.parent/'weighted305'
sys.path.insert(0,str(BASE))
import source_data as oldsource
INPUTS=Path(os.environ.get('PR306_INPUTS',HERE/'inputs')).resolve()
OUTPUT=Path(os.environ.get('PR306_OUTPUTS',HERE/'generated')).resolve()
HEAD='0314371983b8837f01723f5af2c70217f75b01cc'
def pins():
 p=json.loads((HERE/'inputs.json').read_text());assert p['head']==HEAD;return p

def read_bytes(name):
 row=next(r for r in pins()['files']if r['path']==name);raw=(INPUTS/row['local']).read_bytes()
 assert len(raw)==row['bytes']
 assert hashlib.sha256(raw).hexdigest()==row['sha256']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
 return raw

def read_new(name):return json.loads(read_bytes(name))

def verify_new():
 if not __debug__:raise RuntimeError('Assertions required')
 for row in pins()['files']:read_bytes(row['path'])
 return len(pins()['files'])

def verify_dependencies():
 p=json.loads((HERE/'DEPENDENCIES.json').read_text())
 for name,row in p['files'].items():
  raw=(HERE.parent/name).read_bytes();assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],name
 return len(p['files'])

def verify_package():
 p=json.loads((HERE/'MANIFEST.json').read_text())
 assert p['source_head']==HEAD
 for name,row in p['files'].items():
  raw=(HERE/name).read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['sha256'],name
 return len(p['files'])
