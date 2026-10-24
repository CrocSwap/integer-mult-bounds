"""New symbolic entrance-normalization checks. No zero-entrance guard relaxed."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import gzip,json,hashlib,sys,os
P=Path('pr378-donor-screen');c=json.load(gzip.open(P/'signed25-donor-candidate.json.gz'));old=json.load(gzip.open(P/'best-candidate.json.gz'));v,R=c['v'],c['R'];n=2*v+R;ext=dict(c['ext']);root=Path('pr378-complex-screen/candidate-guard').resolve();os.environ['CX_PINS']=str(root/'pins-e8.json');sys.path.insert(0,str(root/'code'));import complex_scalars as S
# Freeze the non-Y-reading response/cleanup circuit of the same donor word,
# not of the original no-donor word. Main permits only Y-to-Y extra reads.
A0=S.flat(old['A']);B0=S.flat(old['B']);K=list(S.old_positive(A0,B0,old))
def main_flat(gs):
 out=[]
 for g in gs:
  for r,a,b in g[3]:
   t,s=(r,g[2]) if g[0]=='out' else (g[2],r)
   assert t!=s and not (s>=2*v and t<v)
   assert not (v<=s<2*v) or v<=t<2*v
   out.append((t,s,Q(a,b)))
 return out
A=main_flat(c['A']);B=main_flat(c['B'])
helper=lambda xs:[e for e in xs if e[0]<v or e[0]>=2*v]
assert helper(A+B)==helper(A0+B0)
# Rational scalar propagation with distinct formal entrance operators for
# gauged initial columns. Each key (column, chart) represents coefficient
# times that column under chart I or C_q^-1. Distinct charts never cancel.
def initial(symbolic):return {('L',i):{(i,'Cq_inverse' if symbolic and i in ext else 'I'):Q(1)} for i in range(n)}
def apply(reg,e):
 op=e[0]
 if op=='recursive_center':return
 t=e[1]
 if op=='clear':reg[t]={}
 elif op=='copy':reg[t]=dict(reg.get(e[2],{}))
 elif op=='add':
  source=dict(reg.get(e[2],{}));q=Q(e[3],e[4]);target=reg.setdefault(t,{})
  for k,a in source.items():
   z=target.get(k,0)+q*a
   if z:target[k]=z
   else:target.pop(k,None)
 else:raise AssertionError(op)
# Old response on physical helper values, i.e. the I chart.
pre=initial(False)
for e in S.old_word('forward',K):apply(pre,e)
# Main and source/helper cleanup are in normalized canonical coordinates.
# Only gauge columns differ; targets keep their old-response correction.
reg=initial(True)
for i in range(v,2*v):reg[('L',i)]=dict(pre[('L',i)])
main=list(S.main_scalar('forward',A,B,c));cleanup=list(S.cleanup('forward',A0+B0))
for e in main+cleanup:apply(reg,e)
expected=initial(True)
for t in range(v):expected[('L',v+t)][(t,'I')]=Q(1)
assert all(reg[k]==row for k,row in expected.items())
assert all(not row for k,row in reg.items() if k[0]!='L')
# This comparison is in normalized endpoint charts: F*Cq^-1 residuals
# on gauged helpers, F on the rest. Port charts are unchanged from baseline.
# Actual inverse-adjoint scalar projection: both chronological orientations.
words={};bills={}
for ori in ['forward','backward']:
 seq=[(p,e) for p,es in [('old_response',S.old_word(ori,K)),('main',S.main_scalar(ori,A,B,c)),('cleanup',S.cleanup(ori,A0+B0))] for e in es]
 S.lifecycle(seq,c);bill=S.bill(seq);bills[ori]=bill;g=initial(False)
 for p,e in seq:apply(g,e)
 want=initial(False)
 for t in range(v):
  if ori=='forward':want[('L',v+t)][(t,'I')]=Q(1)
  else:want[('L',t)][(v+t,'I')]=Q(-1)
 assert all(g[k]==row for k,row in want.items()) and all(not row for k,row in g.items() if k[0]!='L')
 words[ori]=seq
# Control: omit each donor term, retain the frozen old response. Symbolic
# chart mismatch must then leak into target rows, despite same-frame gates.
controls=[]
headlen=len(c['A'])-len(json.load(gzip.open(P/'signed25.json.gz'))['A'])
for gi in range(headlen):
 for ti in range(len(c['A'][gi][3])):
  bad=json.loads(json.dumps(c));bad['A'][gi][3].pop(ti);badA=main_flat(bad['A']);g=initial(True)
  for i in range(v,2*v):g[('L',i)]=dict(pre[('L',i)])
  for e in list(S.main_scalar('forward',badA,B,bad))+cleanup:apply(g,e)
  assert any(g[('L',i)]!=expected[('L',i)] for i in range(v,2*v));controls.append([gi,ti])
raw=json.dumps(words,sort_keys=True,separators=(',',':')).encode();(P/'signed25-gauge-scalar-words.json.gz').write_bytes(gzip.compress(raw,mtime=0))
result=dict(status='PASS_SYMBOLIC_DISTINCT_ENTRANCE_CHART_DIRTY_LIFT_AND_BOTH_SCALAR_ORIENTATIONS',candidate_sha256=hashlib.sha256((P/'signed25-donor-candidate.json.gz').read_bytes()).hexdigest(),live_columns=n,gauged_columns=len(ext),symbolic_endpoint='unchanged data shear; helper F*Cq^-1 on nine gauge inputs, F elsewhere',frozen_response_source_sha256=hashlib.sha256((P/'best-candidate.json.gz').read_bytes()).hexdigest(),helper_cleanup_subword_equal=True,independent_operator_tokens=['I','Cq_inverse'],donor_omission_symbolic_controls=len(controls),scalar_words_sha256=hashlib.sha256(raw).hexdigest(),bills=bills,scope='Exact local normalization algebra with distinct entrance operator tokens, plus literal rational schedules both orientations. Conditional on exact common-frame chart interpretation. Does not alone prove arbitrary correlated global banks/cover routing/ambient phases, full physical emission, finite invoice or final kappa.')
(P/'signed25-gauge-lift-audit.json').write_text(json.dumps(result,indent=2));print(result['status'],len(controls),{o:bills[o]['totals']['real_component_primitive_steps'] for o in bills})
