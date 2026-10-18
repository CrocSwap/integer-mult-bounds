"""Fetch the immutable predecessor package, checking every Git blob and manifest.

The predecessor's license and notice are retained with its source. This tool
fetches source only; it makes no mathematical acceptance claim.
"""
import argparse
import hashlib
import json
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

REPOSITORY='jeremykothe2/integer-mult-bounds'
HEAD='614c74a63b0f6d4a24c7740d7ddb90d37861b3c7'
PREFIX='research/gmx-t74-borrow43-refit/'
MANIFEST='557d8d6cfe0768c427e564beed37fbdfe3f65d10367f4c3a3dc36359c89cc62b'


def download(url):
    for attempt in range(4):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'immutable-research-replay'})
            with urllib.request.urlopen(request,timeout=90) as response:
                return response.read()
        except Exception:
            if attempt==3:raise
            time.sleep(attempt+1)


def main():
    if not __debug__:
        raise RuntimeError('Assertions must be enabled for immutable source fetching')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--jobs',type=int,default=8)
    a=ap.parse_args();out=a.out.resolve()
    assert not out.exists(),'Use a new source directory'
    tree=json.loads(download(f'https://api.github.com/repos/{REPOSITORY}/git/trees/{HEAD}?recursive=1'))
    assert not tree.get('truncated')
    entries=[e for e in tree['tree'] if e['type']=='blob' and
             (e['path'].startswith(PREFIX) or e['path'] in ['LICENSE','NOTICE'])]
    out.mkdir(parents=True)

    def fetch(entry):
        relative=Path(entry['path'])
        assert not relative.is_absolute() and '..' not in relative.parts
        data=download(f'https://raw.githubusercontent.com/{REPOSITORY}/{HEAD}/{entry["path"]}')
        blob=hashlib.sha1(('blob '+str(len(data))+'\0').encode()+data).hexdigest()
        assert blob==entry['sha'] and len(data)==entry['size'],entry['path']
        p=out/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        return dict(path=entry['path'],git_blob_sha1=blob,
                    sha256=hashlib.sha256(data).hexdigest(),bytes=len(data))

    with ThreadPoolExecutor(max_workers=max(1,a.jobs)) as pool:
        files=list(pool.map(fetch,entries))
    package=out/PREFIX
    assert hashlib.sha256((package/'MANIFEST.json').read_bytes()).hexdigest()==MANIFEST
    for relative,digest in json.loads((package/'MANIFEST.json').read_bytes()).items():
        assert hashlib.sha256((package/relative).read_bytes()).hexdigest()==digest,relative
    report=dict(status='PASS_IMMUTABLE_SOURCE_FETCH_ONLY',repository=REPOSITORY,
                head=HEAD,package=PREFIX,manifest_sha256=MANIFEST,files=files)
    (out/'FETCH.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS_IMMUTABLE_SOURCE_FETCH_ONLY',len(files),'files',flush=True)


if __name__=='__main__':main()
