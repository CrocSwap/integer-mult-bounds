"""Restore four exact PR411 leaves over a verified native PR410 runtime.

The overlay is explicitly derived. The retained native410 manifest is provenance,
not a claim that its old inventory validates the changed runtime. No source code
is executed by this transport module. Original files/licenses remain intact.
"""
from pathlib import Path,PurePosixPath
import base64,hashlib,json,os,sys,zlib
if not __debug__:raise RuntimeError('Source restoration requires assertions enabled')
sys.dont_write_bytecode=True
INDEX_SHA256='176f4281f1a3c8e87919be1480e3830520c16999b9ee2a8de4b74231c393535f'
MAX_ARCHIVE=200000;MAX_COMPRESSED=100000;MAX_CARRIER=150000
sha=lambda b:hashlib.sha256(b).hexdigest()
def unique(pairs):
 d={}
 for key,value in pairs:
  assert key not in d,'Duplicate JSON key';d[key]=value
 return d
def load(raw):return json.loads(raw,object_pairs_hook=unique)
def safe(name):
 assert type(name)is str and name and '\\'not in name and '\x00'not in name
 p=PurePosixPath(name);assert not p.is_absolute()and str(p)==name and all(x not in ('','.','..')for x in p.parts)
 assert ':'not in name;return name
def inventory(root):
 root=Path(root);assert root.is_dir()and not root.is_symlink()
 result={}
 for p in sorted(root.rglob('*')):
  assert not p.is_symlink(),'No source symlinks'
  if p.is_file():result[safe(p.relative_to(root).as_posix())]=sha(p.read_bytes())
  else:assert p.is_dir(),'Unsupported filesystem item'
 return result
def metadata(package):
 package=Path(package);p=package/'prefix-native.json';assert p.is_file()and not p.is_symlink();raw=p.read_bytes();assert sha(raw)==INDEX_SHA256,'Changed source index'
 m=load(raw);assert m['version']=='pr411-four-leaf-overlay-v1'
 assert m['parent']['file_count']==193 and len(m['parent_inventory'])==193 and len(m['derived_inventory'])==194
 assert len(m['overlay_files'])==4 and m['carrier']['name']=='prefix-sources.b64'
 for n in list(m['parent_inventory'])+list(m['derived_inventory']):safe(n)
 return m
def unpack(raw,m):
 assert type(raw)is bytes and 0<len(raw)<=MAX_ARCHIVE and len(raw)==m['carrier']['archive_bytes']
 assert sha(raw)==m['carrier']['archive_sha256'],'Changed native archive'
 data=load(raw);assert type(data)is list and len(data)==4
 expected={e['path']:e for e in m['overlay_files']};assert len(expected)==4
 out={}
 for item in data:
  assert type(item)is dict and set(item)=={'path','data'};name=safe(item['path']);assert name in expected and name not in out
  assert type(item['data'])is str and len(item['data'])<=MAX_ARCHIVE
  b=base64.b64decode(item['data'],validate=True);assert base64.b64encode(b).decode()==item['data'],'Noncanonical source base64'
  e=expected[name];assert len(b)==e['bytes']and sha(b)==e['sha256'],'Changed native source bytes'
  assert hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==e['git_blob'],'Changed native Git blob'
  out[name]=b
 assert set(out)==set(expected);return out
def decode(package,m=None):
 package=Path(package);m=metadata(package)if m is None else m;c=m['carrier']
 for key,limit in [('archive_bytes',MAX_ARCHIVE),('compressed_bytes',MAX_COMPRESSED),('bytes',MAX_CARRIER)]:
  assert type(c[key])is int and 0<c[key]<=limit,'Invalid allocation bound'
 p=package/c['name'];assert p.is_file()and not p.is_symlink();raw=p.read_bytes()
 assert len(raw)==c['bytes']and len(raw)<=MAX_CARRIER and sha(raw)==c['sha256'],'Changed carrier'
 assert raw.endswith(b'\n')and not raw.endswith(b'\n\n')and b'\r'not in raw
 lines=raw[:-1].split(b'\n');assert lines and all(len(s)==76 for s in lines[:-1])and 1<=len(lines[-1])<=76
 enc=b''.join(lines);compressed=base64.b64decode(enc,validate=True);assert base64.b64encode(compressed)==enc
 assert len(compressed)==c['compressed_bytes']and len(compressed)<=MAX_COMPRESSED
 dz=zlib.decompressobj();plain=dz.decompress(compressed,c['archive_bytes']+1)
 assert len(plain)==c['archive_bytes']and dz.eof and not dz.unused_data and not dz.unconsumed_tail,'Truncated, oversized or trailing compressed data'
 return unpack(plain,m)
def parent_check(parent,m):
 parent=Path(parent);inv=inventory(parent);assert inv==m['parent_inventory'],'Parent410 inventory changed'
 assert sha((parent/'MANIFEST.json').read_bytes())==m['parent']['manifest_sha256']
 manifest=load((parent/'MANIFEST.json').read_bytes())['files'];assert len(manifest)==192 and manifest=={k:v for k,v in inv.items()if k!='MANIFEST.json'}
 return inv
def check(package,derived,parent410=None):
 m=metadata(package);assert inventory(derived)==m['derived_inventory'],'Derived runtime inventory changed'
 if parent410 is not None:parent_check(parent410,m)
 assert sha((Path(derived)/'MANIFEST.json').read_bytes())==m['parent']['manifest_sha256']
 return dict(status='PASS_EXACT_PR411_FOUR_LEAF_DERIVED_RUNTIME',source_index_sha256=INDEX_SHA256,parent_file_count=193,derived_file_count=194,parent_manifest_sha256=m['parent']['manifest_sha256'],upstream_commit=m['upstream']['commit'],upstream_manifest_sha256=m['upstream']['manifest_sha256'],native_overlay_sha256={e['path']:e['sha256']for e in m['overlay_files']},derived_inventory_sha256=sha(json.dumps(m['derived_inventory'],sort_keys=True,separators=(',',':')).encode()),scope=m['derived_scope'])
def restore(package,fresh_out,parent410):
 package=Path(package).resolve();parent410=Path(parent410).resolve();out=Path(fresh_out).absolute()
 assert not out.exists()and not out.is_symlink(),'Fresh output is required'
 resolved=out.resolve();assert not resolved.is_relative_to(package)and not resolved.is_relative_to(parent410),'Output must be outside source packages'
 # No writes occur until every parent byte and all four native leaves validate.
 m=metadata(package);before=parent_check(parent410,m);leaves=decode(package,m)
 for p in [out]+list(out.parents):assert not p.is_symlink(),'No output path symlinks'
 out.mkdir(parents=True)
 for name in sorted(before):
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((parent410/name).read_bytes())
 for name,b in leaves.items():
  p=out/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
 assert parent_check(parent410,m)==before;check(package,out,parent410);return out
if __name__=='__main__':
 assert len(sys.argv)==4,'PACKAGE FRESH_OUT PARENT410'
 out=restore(*sys.argv[1:]);print(json.dumps(check(sys.argv[1],out,sys.argv[3]),sort_keys=True))
