"""Authenticate and materialize the exact minimal PR3605 source closure."""
from pathlib import Path
import gzip,hashlib,io,json,tarfile
P=Path(__file__).resolve().parent
HEAD='3efbb5de06a49ffeea6684482f2d3fe48cdca3fb'
def need(v,s):
 if not v:raise ValueError(s)
def sha(b):return hashlib.sha256(b).hexdigest()
def extract(out):
 out=Path(out);need(not out.exists(),'fresh predecessor directory')
 m=json.loads((P/'vendor/PR3605-MANIFEST.json').read_bytes());archive=(P/'vendor/PR3605-SOURCES.tar.gz').read_bytes()
 need(m['head']==HEAD and sha(archive)==m['archive_sha256'],'immutable PR3605 source archive')
 raw=gzip.decompress(archive);need(sha(raw)==m['tar_payload_sha256'],'exact source archive payload')
 with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as t:
  members=t.getmembers();need(len(members)==len(m['files']) and {x.name for x in members}==set(m['files']),'complete unique source closure')
  for x in members:
   need(x.isfile() and not x.name.startswith('/') and '..' not in Path(x.name).parts,'regular safe source path')
   b=t.extractfile(x).read();row=m['files'][x.name]
   need(row['source_head']==HEAD and row['source_path']==x.name and len(b)==row['bytes'] and sha(b)==row['sha256'] and hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()==row['git_blob'],'exact predecessor Git blob '+x.name)
  out.mkdir(parents=True);t.extractall(out,filter='data')
 return out/'research/staged-644-660-conditional-release',out/'research/staged-644-660-width-reduction'
