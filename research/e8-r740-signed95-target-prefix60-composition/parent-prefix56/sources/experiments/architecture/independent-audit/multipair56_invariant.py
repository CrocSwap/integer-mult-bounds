from pathlib import Path
from collections import Counter
from fractions import Fraction as Q
import json,struct,copy,hashlib,runpy
O=Path(__file__).resolve().parent;R=O.parents[2];P=R/'experiments/architecture/target-prefix-multipair-complete';S=R/'experiments/stage-search/pr445-signed95-eleven/signed';rd=lambda p:json.loads(p.read_text());ps=rd(P/'PAIR-SELECTION.json')['pairs'];w=rd(P/'word.json');b=rd(S/'word.json');F=rd(P/'records/frames.json')['frames'];rec={e['receiver']for e in ps};don={e['donor']for e in ps};assert len(ps)==len(rec)==56 and not rec&don
def sub(a,c):return all(sum(Q(x)*Q(y)for x,y in zip(u,v))==0 for u in F[str(a)]['B']for v in F[str(c)]['A'])
new=copy.deepcopy(b);negative=0
for e in ps:
 u,d,g=e['receiver'],e['donor'],e['frame'];cu=Counter();cd=Counter()
 for f,a,ss in b['B']:
  if sub(f,g):
   if a==u:cu.update(ss)
   if a==d:cd.update(ss)
 assert cu==cd==Counter(dict(e['helper_coefficients']))
 sc=Counter(b['scatter'][u-120]);sc.subtract(b['scatter'][d-120]);sc={k:v for k,v in sc.items()if v};assert sc=={int(k):v for k,v in e['scatter_new'].items()};assert set(sc.values())<={-1,1};negative+=sum(v<0 for v in sc.values())
 new['D'].append([0,u,[d]]);new['scatter'][u-120]=sorted(sc);B=[];mix=0;cut=max(i for i,(f,a,ss)in enumerate(new['B'])if a==d and f==g)
 for i,(f,a,ss)in enumerate(new['B']):
  if a==u and sub(f,g):continue
  B.append([f,a,ss])
  if i==cut:B.append([g,u,[d]]);mix+=1
 assert mix==1;new['B']=B
assert new==w
for d in don:
 assert [x for x in b['B']if x[1]==d]==[x for x in w['B']if x[1]==d]
 assert b['scatter'][d-120]==w['scatter'][d-120]
 assert [x for x in b['D']if x[1]==d]==[x for x in w['D']if x[1]==d]
# Independent actual signed matrices must preserve the complete old integer decoder, not only parity.
v=runpy.run_path(str(O/'multipair56_word.py'));A,_,_=v['replay'](v['E']);old=list(struct.iter_unpack('<6i',(S/'signed-records.bin').read_bytes()));B,_,_=v['replay'](old);assert A==B
out={'status':'PASS_INDEPENDENT_56_SHARED_DONOR_SIGNED_FORMAL_INVARIANT','receiver_count':56,'distinct_donors':len(don),'receiver_donor_sets_disjoint':True,'negative_scatter_deliveries':negative,'exact_reconstructed_word_matches':True,'donor_D_scatter_B_unchanged':True,'all_exact_integer_decoder_and_dirt_columns_equal95':True,'formal_argument':'Each unchangeddonor mayfeed multipledistinctreceivers; receiver transforms do notwrite anydonor. MinusZEROprecondition, minusdonorscatter, omittedexactintegerprefix and plusdonor atG cancel donorinput/D0/scatter, replacingomittedprefix. Gates on distinctreceivers commute evenwithshareddonor. Chronology inserts eachmix afterdonorG and beforehigherdonordeliveries. Literal signedinverse undoes allshears, nofreezero/donor assumed.','candidate_sha256':hashlib.sha256((P/'global/CANDIDATE.json').read_bytes()).hexdigest(),'scope':'Exact signedlocal invariant, notMILPoptimality or unconditionalallsize weightedcompiler.'};(O/'MULTIPAIR56-INVARIANT.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status'],len(don),negative)
