"""Download the13 immutable PR306 input blobs as inert data, never execute them."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import argparse,hashlib,json,urllib.request
HERE=Path(__file__).resolve().parent

def run(output):
 output=Path(output);pins=json.loads((HERE/'inputs.json').read_text())
 assert pins['head']=='0314371983b8837f01723f5af2c70217f75b01cc'
 def one(row):
  path=output/row['local'];url=row['url']
  assert url.startswith('https://raw.githubusercontent.com/chafreaky/integer-mult-bounds/'+pins['head']+'/')
  raw=path.read_bytes()if path.exists()else urllib.request.urlopen(url,timeout=60).read()
  assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
  assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob']
  if not path.exists():path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  return len(raw)
 with ThreadPoolExecutor(max_workers=4)as pool:sizes=list(pool.map(one,pins['files']))
 return dict(files=len(sizes),bytes=sum(sizes),immutable_head=pins['head'],upstream_code_executed=False)
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
 print(json.dumps(run(p.parse_args().output),indent=2))
