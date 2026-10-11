"""Reconstruct PR402 from fresh PR401 and independently compare all raw columns."""
from pathlib import Path
from collections import Counter
import copy,hashlib,json,sys
assert __debug__
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
def main():
 base=json.loads(Path(sys.argv[1]).read_text());out=Path(sys.argv[2]);assert not out.exists();out.mkdir(parents=True)
 sys.path.insert(0,str(ROOT/'vendor402'));from redesign import build,from_json
 design=from_json(json.loads((ROOT/'vendor402/designs.json').read_text()));c=build(base,design);v=base['v'];n=2*v+base['R']
 # Independent straight-line rational interpreter, separately written here.
 from fractions import Fraction as Q
 def operator(word):
  rows=[{i:Q(1)} for i in range(n)]
  def add(t,source,q):
   for k,a in list(source.items()):
    value=rows[t].get(k,Q(0))+q*a
    if value:rows[t][k]=value
    else:rows[t].pop(k,None)
  for section in ['A','B']:
   if section=='B':
    totals={k:dict(rows[r]) for k,r,f in word['ret']}
    for t,terms in enumerate(word['scat']['table']):
     for k,a,b in terms:add(v+t,totals[k],Q(a,b))
   for kind,frame,reg,terms,*unused in word[section]:
    assert kind in ('in','out')
    if kind=='in':
     for source,a,b in terms:add(reg,dict(rows[source]),Q(a,b))
    else:
     source=dict(rows[reg])
     for target,a,b in terms:add(target,source,Q(a,b))
  return rows,totals
 expected=operator(base);assert operator(c)==expected
 for k in ['A','frames','start','ext','final','ret','scat','h','v','R','cst','ports']:assert c[k]==base[k],k
 def hist(word):
  h=Counter()
  for block in word['blocks'].values():h.update({int(k):v for k,v in block.items()})
  return h
 delta=hist(c);delta.subtract(hist(base));assert {k:v for k,v in delta.items() if v}=={2:2,3:-2,5:-2,6:2}
 controls=[]
 bad=copy.deepcopy(c);j=next(j for j,g in enumerate(bad['B']) if g[0]=='in' and g[1]==0 and g[2]==177 and g[3][0][0]==180);bad['B'].pop(j)
 assert operator(bad)!=expected;controls.append('omitted_target_setup')
 wrong=copy.deepcopy(design);pos,f,s,q=wrong[220][-1];wrong[220][-1]=(pos,f,s,-q);assert operator(build(base,wrong))!=expected;controls.append('flipped_delivery')
 raw=json.dumps(c,sort_keys=True,separators=(',',':')).encode();(out/'candidate.json').write_bytes(raw)
 result=dict(status='PASS_RESYNTHESIS_FULL_RAW_OPERATOR_ALL_DIRTY_COLUMNS',columns=n,retained_totals_equal=True,unchanged_helpers_and_gauges=True,delta={str(k):v for k,v in delta.items() if v},candidate_sha256=hashlib.sha256(raw).hexdigest(),controls_rejected=controls)
 (out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
