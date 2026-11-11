from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import support
support.require_assertions()
"""Correct the supplementary source chronology scope using actual descent frames."""
from pathlib import Path
from collections import Counter
import sys,json,hashlib
P=support.FRAME;A=support.HERE/"admission";sys.path.insert(0,str(A))
support.verify_admission()
from weighted_source_data import read,verify,HEAD
from admission_config import OVER,OVER_SHA
from check_transport import rr,null,included
if not __debug__:raise RuntimeError('Assertions must be enabled')
verify();assert hashlib.sha256(OVER.read_bytes()).hexdigest()==OVER_SHA
w=json.loads(OVER.read_text());g=read('graph.json');F={int(k):v for k,v in read('frames.json')['frames'].items()};D=read('descent-selection.json')['entries'];K=read('kchron.json')['entries'];lookup={(e['scalar'][0],e['scalar'][1]):e for e in D};assert len(lookup)==480
ann=lambda f:F[f]['a']if'a'in F[f]else null(F[f]['b'])
H=Counter();members=Counter();receipts=[]
for e in K:
 a,b=e['carrier'],e['passive'];d=lookup[a,b];B=d['new_basis'];A18=null(B)
 assert d['scalar']==[a,b,1,20]and d['new_dimension']==18 and len(rr(B)[0])==18 and len(A18)==2
 for q in(a,b):
  start=w['source_frame'][q];chi=[int(j in g['labels'][q])for j in range(20)];assert F[start]['dim']==1 and all(sum(x*y for x,y in zip(chi,row))==0 for row in ann(start))
  assert included(A18,ann(start))and all(sum(row[j]for j in g['labels'][q])==0 for row in A18)
  frames=[('source',start,1),('descent_basis',d['record'],18)]
  if q==a:
   end=e['deliver_frame'];assert F[end]['dim']==18 and included(ann(end),A18);frames.append(('delivery',end,18))
  frames.append(('full',w['full_frame'],20));assert F[w['full_frame']]['dim']==20 and not ann(w['full_frame'])
  for x,y in zip(frames,frames[1:]):
   if y[2]>x[2]:H[y[2]-x[2]]+=1
  members[q]+=1;receipts.append(dict(source=q,partner_source=b if q==a else a,chain=frames,retimed_basis_sha256=hashlib.sha256(json.dumps(B,separators=(',',':')).encode()).hexdigest()))
assert members==Counter({q:1 for q in range(960)})and H=={17:960,2:960}
out=dict(status='PASS_CORRECTED_ALL960_FINAL_DESCENDED_SOURCE_CHAINS',head=HEAD,candidate_sha256=OVER_SHA,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),previous_admission_manifest_sha256=hashlib.sha256((support.ADM/'MANIFEST.json').read_bytes()).hexdigest(),previous_supplementary_receipt_sha256=hashlib.sha256((support.ADM/'source-target-geometry-result.json').read_bytes()).hexdigest(),correction='The previous supplementary checker used original rank2 partner mix frames for source setups. Its source-chain statement is limited to original/pre-descent source chains and must not be described as final post-descent chronology. All core matching, kernel, alias, target, scalar/COPY, norm, and reorder-transport receipts remain unchanged. This receipt independently verifies every actual rank18 descended source setup and all960 final source chains.',source_columns=960,retimed_setups=480,all_actual_descent_frames_rank18=True,all_source_lines_and_integer_setup_spans_contained=True,source_paid_histogram={str(k):v for k,v in sorted(H.items())},source_rank_mass=sum(k*v for k,v in H.items()),receipts=receipts,scope='Exact post-descent source geometry correction. Final target chains in the prior supplementary audit are unaffected by descent. Source setup scalar operands/order and all final source endpoints are unchanged. Global compiler, prime, and all-size conditions are not asserted.',input_manifest_sha256=hashlib.sha256((support.INPUT_MANIFEST).read_bytes()).hexdigest())
(P/'SOURCE-GEOMETRY-CORRECTION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items()if k!='receipts'},indent=2))
