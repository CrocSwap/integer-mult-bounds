#!/usr/bin/env python3
"""Recompute numerical comparisons and changed-frame claims from frozen data."""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import argparse,gzip,json,sys
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from paired_cube.frames import perp

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--write',action='store_true');args=ap.parse_args()
 if sys.flags.optimize:raise ValueError('Assertions must be enabled')
 source=json.loads((HERE/'SOURCE.json').read_text())
 seed=HERE/'seed/pr195-frames.json'
 assert sha256(seed.read_bytes()).hexdigest()==source['predecessor_frames_sha256']
 cert=json.loads((HERE/'certificate.json').read_text());k=Q(cert['kappa']);prior=Q(source['predecessor_kappa']);base=Q(cert['baseline_kappa'])
 assert k>prior and Q(cert['previous_kappa'])==prior
 def load(n):return json.loads(gzip.decompress((HERE/'candidate'/(n+'.json.gz')).read_bytes()))
 g,fw,w=map(load,['graph','frames','word'])
 defaults={i:list(perp(fw['annihilators'][n],g['h'])) for i,(_,_,n) in enumerate(w['ops'])}
 old=defaults|dict(json.loads(seed.read_text())['frames']);new=defaults|dict(load('physical-frames'))
 expected=[dict(operation=i,before=old[i],after=new[i]) for i in new if old[i]!=new[i]]
 assert json.loads((HERE/'changes.json').read_text())==expected
 assert json.loads((HERE/'frames.json').read_text())['physical_frames']==load('physical-frames')
 summary=dict(kappa=str(k),complex_saving=cert['complex_moment']['accepted']['saving'],predecessor_kappa=str(prior),baseline_kappa=str(base),absolute_gain_over_predecessor=str(k-prior),relative_gain_over_predecessor=str(k/prior-1),relative_gain_over_PR186=str(k/base-1),changed_frames_from_PR195=len(expected),maxchild=cert['profile']['maxchild'])
 path=HERE/'summary.json'
 if args.write:path.write_text(json.dumps(summary,indent=2)+'\n')
 else:
  assert json.loads(path.read_text())==summary
  from decimal import Decimal,localcontext
  with localcontext() as ctx:
   ctx.prec=60;decimal=str(Decimal(k.numerator)/Decimal(k.denominator))
  assert decimal in (HERE/'README.md').read_text(),'README must state exact kappa'
 print('PASS report, seed provenance hash and',len(expected),'exact frame changes; kappa='+str(k))
if __name__=='__main__':main()
