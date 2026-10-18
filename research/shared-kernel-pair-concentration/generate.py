#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Two interleaved PR2857 copies and one width-seven transfer. Codex-assisted."""
import argparse, gzip, hashlib, json
from pathlib import Path

def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def write(p,v):
 b=(json.dumps(v,separators=(',',':'))+'\n').encode();p.write_bytes(gzip.compress(b,mtime=0) if p.suffix=='.gz' else b)
def main():
 p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('out',type=Path);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
 pins={'FILL.json.gz':'82218aaaf08825bd4a3cca676815c7e9c00d06d0da123b1c5ad234c8c91cb501','ORDER.json':'84f030a59dde4fa4635988ef0931ebae66964b3a202df79d38247fbe8a5592dc','DISPATCH.json':'5513481a70c83767b5836b15fb7ff204d2a8f8fca83c6bcaee90a20b3d1ec6c4'}
 for n,h in pins.items():
  if hashlib.sha256((a.source/n).read_bytes()).hexdigest()!=h:raise ValueError('source '+n)
 old=read(a.source/'FILL.json.gz');order=read(a.source/'ORDER.json');dispatch=read(a.source/'DISPATCH.json');rows=[]
 for t,h,r,ch,port,off in old['rows']:
  for k in range(2):rows.append([2*t+k,h,r+37*k,ch,port,off])
 rows.sort(key=lambda r:r[:2]);target=next(r for r in rows if r[0]==658 and r[1]==297)
 if target!=[658,297,35,16,37,0]:raise ValueError('declared source role')
 target[2]=72;target[5]=7
 new=dict(old,rows=rows)
 new['dispatch_overrides']=[[s,r+37*k,pid] for s,r,pid in old['dispatch_overrides'] for k in range(2)]
 write(a.out/'FILL.json.gz',new)
 write(a.out/'ORDER.json',[[s,r+37*k] for s,r in order for k in range(2)])
 write(a.out/'DISPATCH.json',[[s,r+37*k,pid] for s,r,pid in dispatch for k in range(2)])
 write(a.out/'PROVIDERS.json',read(a.source/'PROVIDERS.json'))
 profile={int(r):2*n for r,n in read(a.source/'PROFILE.json').items()};profile[9]-=2;profile[2]+=1;profile[16]=profile.get(16,0)+1;profile={r:n for r,n in sorted(profile.items()) if n}
 write(a.out/'PROFILE.json',profile)
 write(a.out/'CONSTRUCTION.json',{'source_head':'0b2e2537b368a0cade07ce3f71452ea018ebe394','source_sha256':pins,'copies':2,'replica_offset':37,'time_map':'2*t+k','transfer':{'call':658,'helper':297,'width':7,'before':[35,16,37,0],'after':[72,16,37,7]},'profile_delta_from_double':{'2':1,'9':-2,'16':1},'status':'GENERATED_NOT_ADMITTED'})
 print('GENERATED',profile)
if __name__=='__main__':main()
