"""Download immutable inert source blobs; verify byte length, Git blob and SHA256."""
from pathlib import Path
import argparse, urllib.request
import support

def acquire(destination):
 root=Path(destination).resolve();support.require_assertions()
 for row in support.pins()['files']:
  path=root/row['local']
  if path.exists():support.check_bytes(path.read_bytes(),row);continue
  request=urllib.request.Request(row['url'],headers={'User-Agent':'independent-p10-updated1047-verifier'})
  with urllib.request.urlopen(request,timeout=60)as response:raw=response.read()
  support.check_bytes(raw,row);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 return len(support.pins()['files'])
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--dest',type=Path,default=support.INPUTS);a=p.parse_args()
 print('Verified',acquire(a.dest),'immutable inert inputs at',a.dest.resolve())
