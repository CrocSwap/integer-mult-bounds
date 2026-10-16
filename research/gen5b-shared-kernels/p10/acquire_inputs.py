"""Download only immutable inert data/text, verify size/Git blob/SHA256; execute none."""
from pathlib import Path
import argparse,json,hashlib,urllib.request
from support import HERE,pins

def check(raw,row):
 assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
 assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],row['path']
def acquire(destination):
 root=Path(destination).resolve()
 for row in pins()['files']:
  path=root/row['local']
  if path.exists():check(path.read_bytes(),row);continue
  request=urllib.request.Request(row['url'],headers={'User-Agent':'p10-independent-verifier'})
  with urllib.request.urlopen(request,timeout=60)as response:raw=response.read()
  check(raw,row);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 return len(pins()['files'])
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 parser=argparse.ArgumentParser();parser.add_argument('--dest',type=Path,default=HERE/'local-inputs');args=parser.parse_args()
 print('Verified',acquire(args.dest),'immutable inert inputs at',args.dest.resolve())
