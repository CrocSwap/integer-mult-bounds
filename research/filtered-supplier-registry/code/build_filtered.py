"""Frozen support-saturated response construction; no candidate search."""
import argparse,copy,gzip,hashlib,json,subprocess,sys
from fractions import Fraction as Q
from pathlib import Path

def main():
 if not __debug__:raise SystemExit('Assertions must remain enabled.')
 ap=argparse.ArgumentParser();ap.add_argument('--work',type=Path,required=True);a=ap.parse_args()
 root=Path(__file__).resolve().parents[1];up=root/'vendor/pr531';a.work=a.work.resolve();a.work.mkdir(parents=True,exist_ok=False)
 spec=json.loads((root/'inputs/FILTERED-CONSTRUCTION.json').read_text())
 subprocess.run([sys.executable,'-B',str(up/'code/construct_504.py'),str(up/'inputs/hamming'),str(a.work/'raw')],check=True)
 sys.path.insert(0,str(up/'vendor/gk'));import gk_common as common,gk_word as g
 raw=json.load(gzip.open(a.work/'raw/FULL-WORD.json.gz'));common.V=g.V=len(raw['ports']);common.DATA=g.DATA=64*g.V
 digest=lambda w:hashlib.sha256(json.dumps({k:v for k,v in w.items()if k!='report'},sort_keys=True,separators=(',',':')).encode()).hexdigest()
 assert digest(raw)==spec['raw_semantic_sha256'],'raw source geometry changed'
 w=g.build(raw,spec['selection'],check=True)
 for e in w['A']+w['B']:
  if not g.V<=e[1]<2*g.V:
   assert e[0]!='add' or not g.V<=e[2]<2*g.V
 for m in spec['promotions']:
  e=w[m['section']][m['index']];assert e[-1]==m['old_frame'];assert set(g.span(g.basis(e[-1])))<=set(g.span(g.basis(m['new_frame'])));e[-1]=m['new_frame']
 H=g.profile(w);assert dict(H)=={int(k):v for k,v in spec['profile'].items()}
 for section in ('A','B','cut','cleanup','precondition'):
  for e in w.get(section,[]):
   if e[0]=='add':assert e[1]!=e[2];q=Q(e[3],e[4])
   else:q=Q(e[2],e[3]);assert q and abs(q.numerator)&(abs(q.numerator)-1)==0
   assert q.denominator&(q.denominator-1)==0
 assert digest(w)==spec['result_semantic_sha256'],'changed frozen program'
 w['report']['local_profile']={str(k):v for k,v in sorted(H.items())};w['report']['local_rank_mass']=sum(k*v for k,v in H.items());w['report']['status']='EXACT_FROZEN_FILTERED_CONSTRUCTION'
 for k in ('global_profile','live','complex_coarse_float','gain_percent_float'):w['report'].pop(k,None)
 (a.work/'FULL-WORD.json.gz').write_bytes(g.dump(w));(a.work/'SELECTION.json').write_text(json.dumps(spec['selection'],indent=2)+'\n')
 (a.work/'CONSTRUCTION.json').write_text(json.dumps(dict(status='PASS_FROZEN_RATIONAL_FRAME_DYADIC_REBUILD',semantic_sha256=digest(w),profile=dict(H),ordered_widths=g.widths_of(w)),indent=2)+'\n')
 print(a.work/'FULL-WORD.json.gz')
if __name__=='__main__':main()
