"""Restore complete pinned public Hamming/compressed-E8 source packages.

The carrier preserves native bytes, original provenance, notices and licenses.
Restoration is distinct from which complete native entry points are replayed.
OpenAI Codex assistance; Apache-2.0.
"""
from pathlib import Path,PurePosixPath
from hashlib import sha256,sha1
import base64,json,lzma,struct
if not __debug__:raise RuntimeError('Source restoration requires assertions enabled')
MAGIC=b'HAMMINGNATIVE1\n'
INDEX_SHA='853c5ec9a4200ad2337c3d0fcb5d29f424e2fd9209ef9c5629389a354002d955'
FILES_SHA='cfc17bd13097534fdb4ef022c6c772fd091f019ffc495ecea32f545ff0bd9384'
FILE_COUNT=384
PART_COUNT=17
COMMITS=('db4f46579b95bec6e2a0c59e3e1ee2b6584dbab3', 'e11ccea1d092beb1b01b4ee4ce49da478234254c', 'dd11cf8069554f0333afde398f12a56c3a7c29dd', 'b7fe9cdf2da009c947ff6b334c562bc190b30373', 'd0a620fcc99ba012468d61d01f5bb14007076d50')
MAX_ARCHIVE=12_000_000
sha=lambda x:sha256(x).hexdigest()
def unique(pairs):
 out={}
 for k,v in pairs:assert k not in out,'duplicate JSON key';out[k]=v
 return out
def read(raw):return json.loads(raw,object_pairs_hook=unique)
def safe(name):
 assert isinstance(name,str)and name and '\\'not in name and ':'not in name and '\x00'not in name
 p=PurePosixPath(name);assert not p.is_absolute()and str(p)==name and all(x not in ('','.','..')for x in p.parts);return name
def archive(raw,meta):
 assert len(raw)==meta['archive_bytes']<=MAX_ARCHIVE and sha(raw)==meta['archive_sha256']and raw.startswith(MAGIC)
 pos=len(MAGIC);assert len(raw)>=pos+8;size=struct.unpack('<Q',raw[pos:pos+8])[0];pos+=8;assert 0<size<=150_000 and pos+size<=len(raw)
 header=raw[pos:pos+size];pos+=size;index=read(header);assert set(index)=={'files','blobs'}and json.dumps(index,sort_keys=True,separators=(',',':')).encode()==header
 expected=meta['files'];assert len(expected)==meta['file_count']==FILE_COUNT and sha(json.dumps(expected,sort_keys=True,separators=(',',':')).encode())==FILES_SHA
 assert len(index['files'])==FILE_COUNT and set(index['files'])==set(expected)
 for name,key in index['files'].items():safe(name);assert key==expected[name]['sha256']
 blobs={};last='';assert len(index['blobs'])==meta['unique_blobs']<=FILE_COUNT
 for ent in index['blobs']:
  assert set(ent)=={'sha256','size'};key,n=ent['sha256'],ent['size'];assert isinstance(key,str)and len(key)==64 and key>last
  assert isinstance(n,int)and not isinstance(n,bool)and 0<=n<=MAX_ARCHIVE and pos+n<=len(raw)
  data=raw[pos:pos+n];pos+=n;assert sha(data)==key;blobs[key]=data;last=key
 assert pos==len(raw)and set(blobs)==set(index['files'].values())
 files={name:blobs[key]for name,key in index['files'].items()};assert sum(map(len,files.values()))==meta['native_bytes']<=20_000_000
 for name,data in files.items():
  pin=expected[name];assert len(data)==pin['bytes']and sha(data)==pin['sha256'];assert sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==pin['git_blob'];assert pin['source_commit']in COMMITS;safe(pin['source_path'])
 assert tuple(s['commit']for s in meta['sources'])==COMMITS and len(meta['sources'])==5
 for source in meta['sources']:
  prefix=safe(source['path']);mn=prefix+'/'+source['manifest'];assert sha(files[mn])==source['manifest_sha256'];sub={n[len(prefix)+1:]:sha(b)for n,b in files.items()if n.startswith(prefix+'/')and n!=mn};assert len(sub)+1==source['file_count']
  if source['manifest'].endswith('.sha256'):
   rows=[z.split(None,1)for z in files[mn].decode().splitlines()];m={r.strip().removeprefix('./'):h for h,r in rows};assert len(m)==len(rows)
  else:o=read(files[mn]);m=o.get('files',o)
  assert set(sub)-set(m)==set(source['manifest_extras'])and all(sub[n]==h for n,h in m.items())
 return files
def decode(package,meta):
 package=Path(package);n=meta['archive_bytes'];assert isinstance(n,int)and not isinstance(n,bool)and 0<n<=MAX_ARCHIVE
 assert len(meta['carrier_parts'])==PART_COUNT;parts=[]
 for i,p in enumerate(meta['carrier_parts'],1):
  assert p['name']=='native-sources-%02d.b64'%i;data=(package/p['name']).read_bytes();assert len(data)==p['bytes']<=266000 and sha(data)==p['sha256'];assert data.endswith(b'\n')and b'\r'not in data
  lines=data[:-1].split(b'\n');assert lines and all(len(x)==76 for x in lines[:-1])and 1<=len(lines[-1])<=76;text=b''.join(lines);assert len(text)==p['base64_characters'];parts.append(text)
 text=b''.join(parts);packed=base64.b64decode(text,validate=True);assert base64.b64encode(packed)==text and len(packed)==meta['compressed_bytes']<=4_000_000 and sha(packed)==meta['compressed_sha256']
 d=lzma.LZMADecompressor(format=lzma.FORMAT_XZ,memlimit=64*1024*1024);raw=d.decompress(packed,max_length=n+1);assert d.eof and not d.unused_data,'truncated/concatenated stream';return archive(raw,meta)
def metadata(package):
 raw=(Path(package)/'native-source-index.json').read_bytes();assert sha(raw)==INDEX_SHA;return read(raw)
def check(package,output):
 meta=metadata(package);output=Path(output).resolve();assert output.is_dir()and not any(p.is_symlink()for p in output.rglob('*'))
 actual={p.relative_to(output).as_posix():sha(p.read_bytes())for p in output.rglob('*')if p.is_file()};assert len(actual)==FILE_COUNT and actual=={p:x['sha256']for p,x in meta['files'].items()}
 return dict(status='PASS_EXACT_COMPLETE_NATIVE_SOURCE_INVENTORY',files=FILE_COUNT,index_sha256=INDEX_SHA)
def restore(package,output):
 package,output=Path(package).resolve(),Path(output).resolve();assert package.is_dir()and not output.exists()and not output.is_relative_to(package)
 meta=metadata(package);files=decode(package,meta);output.mkdir(parents=True)
 for name,data in sorted(files.items()):p=output/safe(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
 check(package,output);return {s['key']:output/s['path']for s in meta['sources']}
if __name__=='__main__':
 import sys
 assert len(sys.argv)==3
 print(json.dumps({k:str(v)for k,v in restore(*sys.argv[1:]).items()},sort_keys=True))
