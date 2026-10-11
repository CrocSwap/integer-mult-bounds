"""Exact incremental sigma transport; parent transport remains untouched."""
from pathlib import Path
import json,gzip,hashlib,os
P=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((P/'INCREMENTAL-TRANSPORT.json').read_text())
assert __debug__
for dest,z in m.items():
 comp=P/z['transport_path'];assert sha(comp)==z['compressed_sha256'];raw=P/dest;raw.parent.mkdir(parents=True,exist_ok=True)
 if not raw.exists():
  tmp=raw.with_name(raw.name+'.materializing');assert not tmp.exists();h=hashlib.sha256();n=0
  try:
   with gzip.open(comp,'rb')as src,tmp.open('xb')as out:
    for b in iter(lambda:src.read(1048576),b''):n+=len(b);assert n<=z['raw_bytes'];h.update(b);out.write(b)
   assert n==z['raw_bytes']and h.hexdigest()==z['raw_sha256'];os.replace(tmp,raw)
  finally:
   if tmp.exists():tmp.unlink()
 assert raw.stat().st_size==z['raw_bytes']and sha(raw)==z['raw_sha256']
print('PASS_EXACT_INCREMENTAL_FROZEN_SIGMA_MATERIALIZED')
