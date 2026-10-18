#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Read-only finite replay: words, corrections, cleanup, hosting and exact moment.
No assertion-optimized execution; full native/outer release is separate.
"""
import copy,gzip,hashlib,json
from pathlib import Path
from fractions import Fraction as F
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import composition as C
import independent_local as L
import independent_owners as I
import exact_moment as M
HERE=Path(__file__).resolve().parent
PROFILE={1:1593072,2:430236,3:204396,4:79920,5:22532,8:5328,32:1,48:26558}
LOW=F('0.001717141586348426338109')
def need(ok,msg):
 if not ok:raise ValueError(msg)
def rd(name):
 p=HERE/'inputs'/name;b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def run():
 need(__debug__,'run without -O: inherited independent local checker uses assertions')
 pins=json.loads((HERE/'INPUT-PINS.json').read_text())
 for path,digest in pins.items():need(hashlib.sha256((HERE/path).read_bytes()).hexdigest()==digest,'input digest '+path)
 claim=json.loads((HERE/'CLAIM.json').read_text())
 need({int(k):v for k,v in claim['profile'].items()}==PROFILE,'claim profile')
 need(F(claim['complex_lower'])==LOW and F(claim['complex_upper'])==LOW+F(1,10**24),'claim bracket')
 need(F(claim['kappa'])==LOW-F(1,10**46)-F(1,10**70),'claim outer endpoint')
 for name in ('PR2733','PR2745'):
  previous=json.loads((HERE/'evidence'/f'{name}-CLAIM.json').read_text())
  need(F(claim['kappa'])>F(previous['kappa']),'strict improvement over '+name)
 words={}
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=rd('WORD-'+tag+'.json.gz');words[pid]=w
  L.check_frames(w);L.check_cleanup(w);L.algebra(w)
  need(set(int(t)+112 for t in w['target_levels']).isdisjoint(g[1] for g in w['cut']),'lifted targets avoid every cut read')
  for label in ['drop_anticipatory','reverse_anticipatory','reverse_recovery']:
   bad=copy.deepcopy(w)
   if label=='drop_anticipatory':bad['initial_corrections'].pop()
   elif label=='reverse_anticipatory':bad['initial_corrections'][0]['coefficient']=str(-F(bad['initial_corrections'][0]['coefficient']))
   else:
    j=next(i for i,g in enumerate(bad['B']) if g[:5]==['add',49,33,-1,1]);bad['B'][j][3]=1
   try:L.algebra(bad)
   except AssertionError:pass
   else:raise ValueError('accepted mutation '+label)
 order,fill,providers=rd('ORDER.json'),rd('FILL.json.gz'),rd('PROVIDERS.json')
 dispatch={(s,r):p for s,r,p in rd('DISPATCH.json.gz')}
 need(order==rd('SOURCE-ORDER.json'),'source order')
 constructed,_,_=C.transform(rd('SOURCE-PROVIDERS.json'),providers,rd('SOURCE-FILL.json.gz'),order,dispatch,words)
 need(constructed==fill,'complete deterministic fill')
 owner=I.check(rd('PLAN.json.gz'),rd('GLOBAL-TEMPLATE.json.gz'),order,fill,providers,dispatch,PROFILE)
 bad=copy.deepcopy(fill);bad['rows'][0][5]=999
 try:I.check(rd('PLAN.json.gz'),rd('GLOBAL-TEMPLATE.json.gz'),order,bad,providers,dispatch,PROFILE)
 except (ValueError,RuntimeError):pass
 else:raise ValueError('accepted out-of-bin placement')
 _,a=M.moment_bounds(PROFILE,LOW);b,_=M.moment_bounds(PROFILE,LOW+F(1,10**24));need(a<66304<b,'exact adjacent root bracket')
 baseline=dict(PROFILE);baseline[1]+=2664;baseline[7]=2664;baseline[8]-=2664
 x,_=M.moment_bounds(baseline,LOW);need(x>66304,'PR2733 rejects candidate endpoint')
 return {'status':'PASS_JOINT_TWELVE_FINITE_REPLAY','roles':owner['roles'],'local_mutations_rejected':6,'owner_mutations_rejected':1,'complex_lower':str(LOW),'complex_upper':str(LOW+F(1,10**24)),'scope':'Independent local symbolic identity, actual frame bill, cleanup, exact hosting and moment only. Native/strict supplier/outer release is separate.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
