#!/usr/bin/env python3
"""Read only, exact-blob acquisition of the three named public contributions."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,urllib.request
H=Path(__file__).resolve().parent
OUT=H.parent/'public_constructions'
HEADS={6398:'dee2663ba0918be86993fd9d63c8d64b020f4c83',6399:'a928a7aa5ab5b21b7cf841d6d960ab2e7efd1041',6401:'0645ec2c14669558861e8e9a1281b59643dce4ed'}

def get(item):
    number,entry=item
    name=entry['filename'];rel=Path(name)
    if rel.is_absolute() or '..'in rel.parts or rel.parts[0]!='research':raise ValueError(name)
    path=OUT/rel;path.parent.mkdir(parents=True,exist_ok=True)
    url=entry['raw_url']
    data=urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'research-readonly'}),timeout=60).read()
    blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    if blob!=entry['sha']:raise ValueError(('blob mismatch',name,blob,entry['sha']))
    path.write_bytes(data)
    return dict(pr=number,head=HEADS[number],path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob=blob,url=url)

def main():
    todo=[]
    for number in HEADS:
        rows=json.loads((H/'public_refresh'/f'PR{number}-FILES.json').read_text())
        if len(rows)>=100:raise ValueError('Pagination requires another manifest page')
        todo.extend((number,row)for row in rows)
    with ThreadPoolExecutor(max_workers=8)as pool:
        records=list(pool.map(get,todo))
    result=dict(status='PASS_EXACT_PUBLIC_BLOBS',heads=HEADS,files=records,read_only_acquisition=True)
    (OUT/'ACQUISITION.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(status=result['status'],files=len(records),bytes=sum(r['bytes']for r in records),heads=HEADS),indent=2))

if __name__=='__main__':main()
