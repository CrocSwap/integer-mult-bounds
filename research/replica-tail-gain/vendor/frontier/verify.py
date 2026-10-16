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
PROFILE={1: 1603728, 2: 431568, 3: 185082, 4: 85248, 5: 27194, 8: 5328, 32: 1, 48: 26558}
LOW=F('0.001717794984118634663827')
PROFILE2751={1:1593072,2:430236,3:204396,4:79920,5:22532,8:5328,32:1,48:26558}
LOW2751=F('0.001717141586348426338109')
ALIASES=[(606,550),(635,551),(637,552),(638,553),(639,562)]   # retired5
NEW7=[(667,401),(669,403)]   # retired7: retired-lender aliases enabled by moving the hostees of warps 30/31 onto 564/565
import importlib.util as _iu
_s=_iu.spec_from_file_location('word_patch_pr2679',Path(__file__).resolve().parent/'vendor/word_patch_pr2679.py');WP=_iu.module_from_spec(_s);_s.loader.exec_module(WP)
def refit_apply(w0,p):
 w=copy.deepcopy(w0)
 for sec,i,fr in p['frames']:
  need(w[sec][i][:-1]==w0[sec][i][:-1],'refit changes a gate');w[sec][i][-1]=fr
 w['report']['local_profile']=p['local_profile'];return w
def compact(fill,old_words,new_words,old_prov,new_prov,order,dispatch):
 live=lambda w:[r for r in range(224,704) if r not in set(w['removed'])]
 L0=live(old_words['gauge44']);L1=live(new_words['gauge44']);need(L0==live(old_words['extra']) and L1==live(new_words['extra']),'live helper sets')
 gone=set(L0)-set(L1);need(set(L1)<=set(L0) and sorted(gone)==sorted([h for h,_ in ALIASES]+[h for h,_ in NEW7]),'removed helpers')
 i1={r:i for i,r in enumerate(L1)};bins={}
 for pid in ('gauge44','extra'):need([old_prov[pid]['widths'][L0.index(r)] for r in L1]==new_prov[pid]['widths'],'renumbered widths')
 for t,h,o,c,p,off in fill['rows']:
  if L0[h] in gone:continue
  bins.setdefault((o,c,p),[]).append([t,i1[L0[h]],o,c,p,off])
 rows=[]
 for key,rs in bins.items():
  rs.sort(key=lambda x:x[5]);pos=0
  for x in rs:x[5]=pos;pos+=new_prov[dispatch[tuple(order[x[0]])]]['widths'][x[1]];rows.append(x)
 rows.sort(key=lambda x:(x[0],x[1]));return dict(fill,rows=rows)
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
 for name in ('PR2733','PR2745','PR2751','PR2766','PR2767'):
  previous=json.loads((HERE/'evidence'/(f'{name}-OUTER-CLAIM.json' if name=='PR2767' else f'{name}-CLAIM.json')).read_text())
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
 # retired5: PR2751's own construction (its words, providers and fill) is reproduced first ...
 words51={'gauge44':rd('WORD2751-base.json.gz'),'extra':rd('WORD2751-extra.json.gz')};prov51=rd('PROVIDERS2751.json');fill51=rd('FILL2751.json.gz')
 constructed,_,_=C.transform(rd('SOURCE-PROVIDERS.json'),prov51,rd('SOURCE-FILL.json.gz'),order,dispatch,words51)
 need(constructed==fill51,'complete deterministic PR2751 fill')
 # ... then the declared stages turn its words into the candidate words exactly ...
 for tag,pid in [('base','gauge44'),('extra','extra')]:
  w=refit_apply(words51[pid],rd('refit5_43'+tag+'.json'));w=WP.apply_lowfour(w,rd('alias5_43'+tag+'.json'));w=refit_apply(w,rd('refit5c_43'+tag+'.json'))
  w=refit_apply(w,rd('refit7_43'+tag+'.json'));w=WP.apply_lowfour(w,rd('hostmove2_43'+tag+'.json'));w=WP.apply_lowfour(w,rd('alias7_43'+tag+'.json'));w=refit_apply(w,rd('refit7c_43'+tag+'.json'))   # retired7
  need(w==words[pid],'declared stages reproduce the candidate word '+tag)
 d2=dict(dispatch)
 for s,r,p in fill['dispatch_overrides']:d2[s,r]=p
 # ... and the candidate fill is PR2751's fill with the seven removed helpers' roles dropped, renumbered and re-tiled as bin prefixes
 need(compact(fill51,words51,words,prov51,providers,order,d2)==fill,'complete deterministic candidate fill')
 owner=I.check(rd('PLAN.json.gz'),rd('GLOBAL-TEMPLATE.json.gz'),order,fill,providers,dispatch,PROFILE)
 bad=copy.deepcopy(fill);bad['rows'][0][5]=999
 try:I.check(rd('PLAN.json.gz'),rd('GLOBAL-TEMPLATE.json.gz'),order,bad,providers,dispatch,PROFILE)
 except (ValueError,RuntimeError):pass
 else:raise ValueError('accepted out-of-bin placement')
 _,a=M.moment_bounds(PROFILE,LOW);b,_=M.moment_bounds(PROFILE,LOW+F(1,10**24));need(a<66304<b,'exact adjacent root bracket')
 x,_=M.moment_bounds(PROFILE2751,LOW);need(x>66304,'PR2751 rejects candidate endpoint')
 return {'status':'PASS_JOINT_TWELVE_RETIRED7_FINITE_REPLAY','roles':owner['roles'],'local_mutations_rejected':6,'owner_mutations_rejected':1,'complex_lower':str(LOW),'complex_upper':str(LOW+F(1,10**24)),'scope':'Independent local symbolic identity, actual frame bill, cleanup, exact hosting and moment only. Native/strict supplier/outer release is separate.'}
if __name__=='__main__':print(json.dumps(run(),indent=2))
