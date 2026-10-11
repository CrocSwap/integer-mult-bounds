"""Six exact native416/418 leaves for the additional entrance propagation step.
The restored directory is an explicitly limited source closure, not a full package.
"""
from pathlib import Path
import base64,hashlib,importlib.util,json,sys,zlib
if not __debug__:raise RuntimeError('Source restoration requires assertions enabled')
sys.dont_write_bytecode=True
INDEX_SHA256='cc88d819779e5d7203720638441f65cc7b30be30e9948d1218cbe6654c463d9e'
BASE_SHA256='98af6306151f9d77719cf22626abce811c407de13a966e465f53cbd2309baf0c'
sha=lambda b:hashlib.sha256(b).hexdigest()
basepath=Path(__file__).resolve().with_name('prefix_source.py');assert sha(basepath.read_bytes())==BASE_SHA256
spec=importlib.util.spec_from_file_location('_prefix_transport',basepath);T=importlib.util.module_from_spec(spec);spec.loader.exec_module(T)
MAX_ARCHIVE=200000;MAX_COMPRESSED=100000;MAX_CARRIER=150000
NAMES={'construct.py','common.py','local_admit.py','ORIGINAL892.json','SELECTION.json','PATTERNS.json'}
def metadata(package):
 p=Path(package)/'propagation-native.json';assert p.is_file()and not p.is_symlink();raw=p.read_bytes();assert sha(raw)==INDEX_SHA256
 m=T.load(raw);assert m['version']=='six-leaf-propagation-v1'and len(m['files'])==6
 assert {e['path']for e in m['files']}==NAMES and m['carrier']['name']=='propagation-sources.b64';return m
def unpack(raw,m):
 assert type(raw)is bytes and 0<len(raw)<=MAX_ARCHIVE and len(raw)==m['carrier']['archive_bytes']and sha(raw)==m['carrier']['archive_sha256']
 records=T.load(raw);assert type(records)is list and len(records)==6;expected={e['path']:e for e in m['files']};out={}
 for r in records:
  assert type(r)is dict and set(r)=={'path','data'};name=T.safe(r['path']);assert name in NAMES and name not in out
  assert type(r['data'])is str and len(r['data'])<=MAX_ARCHIVE;b=base64.b64decode(r['data'],validate=True);assert base64.b64encode(b).decode()==r['data'];e=expected[name]
  assert len(b)==e['bytes']and sha(b)==e['sha256']
  assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['git_blob'];out[name]=b
 assert set(out)==NAMES;return out
def decode(package,m=None):
 m=metadata(package)if m is None else m;c=m['carrier']
 for k,limit in [('archive_bytes',MAX_ARCHIVE),('compressed_bytes',MAX_COMPRESSED),('bytes',MAX_CARRIER)]:assert type(c[k])is int and 0<c[k]<=limit
 p=Path(package)/c['name'];assert p.is_file()and not p.is_symlink();b=p.read_bytes();assert len(b)==c['bytes']and sha(b)==c['sha256']and len(b)<=MAX_CARRIER
 assert b.endswith(b'\n')and not b.endswith(b'\n\n')and b'\r'not in b
 lines=b[:-1].split(b'\n');assert all(len(s)==76 for s in lines[:-1])and 1<=len(lines[-1])<=76
 enc=b''.join(lines);comp=base64.b64decode(enc,validate=True);assert base64.b64encode(comp)==enc and len(comp)==c['compressed_bytes']
 dz=zlib.decompressobj();raw=dz.decompress(comp,c['archive_bytes']+1);assert len(raw)==c['archive_bytes']and dz.eof and not dz.unused_data and not dz.unconsumed_tail
 return unpack(raw,m)
def check(package,restored):
 m=metadata(package);expected={e['path']:e['sha256']for e in m['files']};assert T.inventory(restored)==expected
 return dict(status='PASS_SIX_EXACT_NATIVE_PROPAGATION_LEAVES',source_index_sha256=INDEX_SHA256,source_sha256=expected,scope=m['scope'])
def restore(package,fresh_out):
 package=Path(package).resolve();out=Path(fresh_out).absolute();assert not out.exists()and not out.is_symlink()and not out.resolve().is_relative_to(package)
 for p in[out]+list(out.parents):assert not p.is_symlink()
 m=metadata(package);leaves=decode(package,m);out.mkdir(parents=True)
 for name,b in leaves.items():(out/name).write_bytes(b)
 check(package,out);return out
if __name__=='__main__':
 assert len(sys.argv)==3,'PACKAGE FRESH_OUT';out=restore(*sys.argv[1:]);print(json.dumps(check(sys.argv[1],out),sort_keys=True))
