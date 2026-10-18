#!/usr/bin/env python3
"""Derive zero-padding-free width100/T300 banks from actual initial and final frames."""
import sys
if not __debug__:raise SystemExit('assertions required')
sys.dont_write_bytecode=True
from pathlib import Path
from collections import Counter
import argparse,json,importlib.util

def run(base,candidate,output,source_root=None):
 from source_tiling import tile
 base=Path(base);candidate=Path(candidate);read=lambda p:json.loads(p.read_text())
 st=read(base/'249-states.json');ini=read(candidate/'COHORT249-INITIAL.json');fin=read(candidate/'COHORT249-FINAL.json');fs=read(base/'frames.json')['frames'];nf=read(candidate/'COHORT249-FRAMES.json');assert not set(fs)&set(nf);fs.update(nf);d=lambda f:fs[str(f)]['dim']
 census=Counter();saved=0;changed=0;original=0
 for i in range(2*st['v'],st['n']):
  k=str(i);r=d(fin[k])-d(ini[k]);oldr=d(st['final'][k])-d(st['initial'][k]);assert 0<=r<=oldr
  census[r]+=1;saved+=oldr-r;original+=oldr;changed+=(ini[k]!=st['initial'][k] or fin[k]!=st['final'][k])
 deleted=census.pop(0,0);assert original>0
 patterns=tile({r:300*n for r,n in census.items()},100)
 result=dict(physical_replicas=300,original_residual=original,census=dict(census),deleted=deleted,entrance_rank=saved,changed_helpers=changed,patterns=[dict(widths=w,count=n)for w,n in patterns],note='entrance_rank is total initial/final endpoint residual saving')
 Path(output).write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print('PASS exact tiling',sum(n for w,n in patterns),'banks',dict(census),flush=True)
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('base');ap.add_argument('candidate');ap.add_argument('output');ap.add_argument('--source-root');a=ap.parse_args();run(a.base,a.candidate,a.output,a.source_root)
