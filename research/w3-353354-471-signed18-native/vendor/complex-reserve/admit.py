"""Independent E8 dirty scalar words and corrected odd-dimensional cover invoice.
OpenAI Codex-assisted; no Lean build, unconditional theorem, or combined kappa claim.
"""
import sys
sys.dont_write_bytecode=True
assert __debug__
sys.set_int_max_str_digits(0)
from pathlib import Path
from fractions import Fraction as Q
from math import prod
import os,importlib.util,gzip,json,hashlib,time
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--source',required=True,type=Path);ap.add_argument('--output',required=True,type=Path);args=ap.parse_args();ROOT=args.source.resolve();C=ROOT/'code/complex';OUT=args.output.resolve();assert not OUT.exists() and not OUT.is_relative_to(ROOT);OUT.mkdir(parents=True)
os.environ['CX_PINS']=str(C/'pins-e8.json')
for k in ['CX_SOURCE_PINS','CX_RECORD']:os.environ.pop(k,None)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
G=load('independent_e8_guard',C/'portable_complex.py');raw=G.run(C,progress=lambda s:print(s,flush=True));(OUT/'UPSTREAM-GUARD.json').write_text(json.dumps(raw,sort_keys=True,indent=2)+'\n')
pins=json.loads((C/'inputs/complex/source-pins.json').read_text());cert=json.loads(gzip.decompress((C/pins['certificate']['path']).read_bytes()));S=G.module(C,'complex_scalars');A=S.flat(cert['A']);B=S.flat(cert['B']);v,R,h=cert['v'],cert['R'],cert['h'];n=2*v+R
# Live columns are arbitrary independent input scalars; only private work is initially zero.
# Set all abstract recursive frame transforms to identity to isolate both literal dirty scalar maps.
scalars={};start=time.monotonic()
for orientation in ['forward','backward']:
 reg={('L',i):{i:Q(1)}for i in range(n)};steps=0
 for phase,e in S.inv_schedule(orientation,A,B,cert):
  tag=e[0]
  if tag=='recursive_center':continue
  t=e[1]
  if tag=='clear':reg[t]={}
  elif tag=='copy':reg[t]=dict(reg.get(e[2],{}))
  elif tag=='add':
   src=dict(reg.get(e[2],{}));q=Q(e[3],e[4]);target=reg.setdefault(t,{})
   for j,c in src.items():
    z=target.get(j,Q(0))+q*c
    if z:target[j]=z
    else:target.pop(j,None)
  else:raise AssertionError(tag)
  steps+=1
 expected={('L',i):{i:Q(1)}for i in range(n)}
 for t in range(v):
  if orientation=='forward':expected[('L',v+t)][t]=Q(1)
  else:expected[('L',t)][v+t]=Q(-1)
 assert all(reg[r]==e for r,e in expected.items()),orientation+' actual live scalar map'
 assert all(not z for r,z in reg.items()if r[0]!='L'),orientation+' dirty work cleanup'
 scalars[orientation]=dict(status='PASS_FULL_ACTUAL_DIRTY_SCALAR_WORD',independent_live_columns=n,source_columns=v,target_columns=v,helper_columns=R,scalar_macros=steps,all_live_rows_correct=True,all_private_work_restored_zero=True,expected_map='Y += X; X and dirty S restored'if orientation=='forward'else 'X -= Y; Y and dirty S restored',recursive_scope='All recursive frame operators specialized to identity; validates literal dirty scalar map and both projection schedules, while upstream splice separately checks exact frame incidence and child ranks.')
 print('PASS actual dirty scalar word',orientation,steps,flush=True)
guard_module=load('e8_parity_correct_finite_guard',Path(__file__).with_name('finite_guard.py'));correct=guard_module.finite_guard(raw,cert)
rowphysical=correct['physical_row_overcharge_coefficient']
rec=dict(status='PASS_E8_INDEPENDENT_DIRTY_SCALARS_AND_CORRECTED_FINITE_GUARD',upstream_head='04b4c3c478b5bd8797d2663d89d8db4dfd0ad9f2',upstream_manifest_sha256=sha(ROOT/'MANIFEST.sha256'),guard_receipt_sha256=sha(OUT/'UPSTREAM-GUARD.json'),certificate_sha256=pins['certificate']['uncompressed_sha256'],scalar_words=scalars,finite_guard=correct,upstream_finding='The upstream m=45 guard uses the even-dimension orthogonal order and undercounts the cover by (2^44-1)/2. Correcting it preserves every retained strict finite guard and changes no coarse saving.',seconds=time.monotonic()-start,scope='Independent audit of supplier words and finite charges only; no Lean build or complete multiplication theorem proof.')
(OUT/'INDEPENDENT-AUDIT.json').write_text(json.dumps(rec,sort_keys=True,indent=2)+'\n');print('PASS corrected complete invoice',correct['group_bits'],rowphysical,flush=True)
