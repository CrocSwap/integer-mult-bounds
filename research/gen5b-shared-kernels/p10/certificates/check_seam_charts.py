"""New exact rank-projector charts for the 73 changed weighted892 alias seams.
Only our authored rational routines execute; pinned upstream sources are inert.
"""
from pathlib import Path
import sys,gzip,json,hashlib
from fractions import Fraction as Q
from collections import Counter
CODE=Path(__file__).resolve().parent
sys.path.insert(0,str(CODE.parent))
import support
ROOT=support.out('certificates','placeholder').parent
CLOSURE=support.OUTPUT/'closure'
sys.path.insert(0,str(CODE.parent/'closure'))
import chart_rational as rat
from chart_construction import gram
from source_contract import SOURCE,HEAD,verify_inputs
PARAM=support.OUTPUT/'matching'
WORD_SHA='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def basis(frame):return frame.get('b')or rat.nullspace(frame['a'])
def ann(frame):return frame.get('a')or rat.nullspace(frame['b'])
def chart(D,E):
 BD=basis(D);AE=ann(E)
 assert len(BD)==D['dim'] and len(AE)==20-E['dim']
 assert all(sum(a*b for a,b in zip(x,y))==0 for x in AE for y in BD)
 # E intersect D-perp is precisely the image of P_E-P_D.
 gd=[[9*x-sum(row)for x in row]for row in BD]
 residual=rat.nullspace(AE+gd)
 outside=[rat.primitive([11*x-sum(a)for x in a])for a in AE]
 rank=E['dim']-D['dim'];assert len(residual)==rank>=0
 assert all(gram(a,b)==0 for a in residual for b in BD+outside)
 assert all(gram(a,b)==0 for a in BD for b in outside)
 columns=residual+BD+outside
 assert len(columns)==20 and len(rat.rref(columns)[1])==20
 B=[list(row)for row in zip(*columns)];f=rat.factor(B)
 assert f['count']<=400 and max(f['max_numerator'],f['max_denominator'])<2**80
 # Reconstruct inverse from the exact elimination program and check both products.
 inv=[[Q(i==j)for j in range(20)]for i in range(20)]
 for op,i,j,q in f['factors']:
  if op=='swap':inv[i],inv[j]=inv[j],inv[i]
  elif op=='scale':inv[i]=[x*q for x in inv[i]]
  else:inv[i]=[x+q*y for x,y in zip(inv[i],inv[j])]
 for L,R in ((B,inv),(inv,B)):
  assert all(sum(L[i][k]*R[k][j]for k in range(20))==int(i==j)for i in range(20)for j in range(20))
 return dict(rank=rank,donor_dimension=D['dim'],recipient_dimension=E['dim'],basis_columns=columns,inverse=inv,**f)
def run():
 verify_inputs();word=PARAM/'word_weighted892.json';seams_path=PARAM/'scalar_and_seams892.json'
 assert sha(word)==WORD_SHA
 s=json.loads(seams_path.read_text());assert s['candidate_word_sha256']==WORD_SHA and s['changed_pairs']==73
 frames_path=SOURCE/'bitword/selected/bit/frames_p10.json.gz'
 frames={int(k):v for k,v in json.loads(gzip.decompress(frames_path.read_bytes()))['frames'].items()}
 programs=[];ids={};uses=[]
 for row in s['seams']:
  key=(row['donor_end_frame'],row['recipient_gauge_frame'])
  if key not in ids:
   ids[key]=len(programs);programs.append(dict(program_id=len(programs),donor_end_frame=key[0],recipient_gauge_frame=key[1],**chart(frames[key[0]],frames[key[1]])))
  p=programs[ids[key]];assert p['rank']==row['transition_rank']
  uses.append(dict(donor=row['donor'],recipient=row['recipient'],stream=row['physical_stream'],read_order=row['read_order'],rank=p['rank'],program_id=ids[key]))
 report=dict(status='PASS_EXACT_CHANGED_ALIAS_SEAM_CHARTS',source_head=HEAD,candidate_word_sha256=WORD_SHA,frames_sha256=sha(frames_path),seam_receipt_sha256=sha(seams_path),
  dimension=20,metric='9I-J',exterior_formula='11*a-sum(a)',changed_seams=len(uses),distinct_programs=len(programs),positive_rank_seams=sum(x['rank']>0 for x in uses),rank_census=dict(Counter(x['rank']for x in uses)),
  max_chart_factors=max(x['count']for x in programs),max_numerator=max(x['max_numerator']for x in programs),max_denominator=max(x['max_denominator']for x in programs),retained_chart_bound=400,retained_normalizer_bound=599,
  exact_inverse_replayed=True,role_uses=uses,factor_programs=programs,scope='Exact new interior projector charts only. No all-characteristics claim: retained prime selection and compiler interfaces are inherited. Physical kernel/target/reorder chronology and finite billing are bound separately.')
 out=ROOT/'weighted892-seam-charts.json';out.write_text(json.dumps(rat.serial(report),separators=(',',':'))+'\n')
 print(json.dumps({k:v for k,v in report.items()if k not in('role_uses','factor_programs')},indent=2));return report
if __name__=='__main__':
 if not __debug__:raise RuntimeError('Assertions required')
 run()
