"""Independent frozen-word review, not importing candidate checker/native_core.
Apache-2.0; substantial OpenAI Codex assistance; source credit in REVIEW.md.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
from collections import Counter
import json,gzip,sys,types
HERE=Path(__file__).resolve().parent
def load_own(name):
 env={'__file__':str(HERE/(name+'.py')),'__name__':'independent_'+name}
 exec(compile((HERE/(name+'.py')).read_bytes(),str(HERE/(name+'.py')),'exec'),env)
 return types.SimpleNamespace(**env)
def need(v,m):
 if not v:raise ValueError(m)
def read(path):return json.loads(gzip.decompress(path.read_bytes()))
def main():
 for n,h in json.loads((HERE/'CANDIDATE-HASHES.json').read_text()).items():need(sha256((HERE/'candidate-inputs'/n).read_bytes()).hexdigest()==h,'Candidate freeze '+n)
 derive=load_own('derive');engine=load_own('replay_independent')
 for row in json.loads((HERE/'SOURCES.json').read_text())['files']:need(sha256((HERE/row['path']).read_bytes()).hexdigest()==row['sha256'],'Pinned upstream '+row['path'])
 coded=read(HERE/'inputs/CODED-WORDS.json.gz');forward=read(HERE/'inputs/INVOLUTIVE-WORD.json.gz');w=read(HERE/'candidate-inputs/RAWDUAL-WORD.json.gz')
 c=coded['canonical'];F=[[Q(x) for x in row] for row in forward['F']]
 need(w['canonical']==c,'Entire canonical boundary unchanged')
 need(w['target_F']==forward['F'],'Frozen source-restored F unchanged')
 need(w['selected_ports']==list(derive.S),'Selected sources unchanged')
 n=len(coded['programs']['backward']);need(w['program'][:n]==coded['programs']['backward'],'Literal4929 backward prefix unchanged')
 need(w['program'][n:]==w['repair_suffix'],'Literal suffix declared exactly')
 # Independently reconstruct only the audited correction, from source R.
 R=[[Q(x) for x in row] for row in json.loads((HERE/'inputs/R.json').read_text())]
 K=[[R[k][i]/4 for k in range(8)] for i in range(112)]
 P=[K[j] if j in derive.S else [Q(0)]*8 for j in range(112)]
 D=[[12*x for x in row] for row in derive.mm(P,R)]
 expected_suffix=[]
 for j in derive.S:
  f=c['final'][112+j]
  expected_suffix.extend([['scalar',['clear',['C',0]],f],['scalar',['copy',['C',0],['L',112+j]],f],['center',0,f,1,1]])
  for i,v in enumerate(D[j]):
   if v:expected_suffix.append(['scalar',['add',['L',i],['C',0],(-v).numerator,(-v).denominator],1])
  expected_suffix.append(['scalar',['clear',['C',0]],0])
 need(w['repair_suffix']==expected_suffix,'Actual coefficient/sign/owners/suffix chronology')
 old,op,om,oe=engine.replay(c,coded['programs']['backward'])
 A=[[Q(i==j)-v for j,v in enumerate(row)] for i,row in enumerate(derive.mm(K,R))]
 need(old[:632]==engine.expected(A,True),'Independent all632 coded backward rows')
 fr,fp,fm,fe=engine.replay(forward['canonical'],forward['program'])
 need(fr[:632]==engine.expected(F,False),'Independent all6324935 forward rows')
 rows,paid,mx,ev=engine.replay(c,w['program'])
 target=engine.expected(F,True)
 need(rows[:632]==target,'Independent all632 physical-normalized rawdual rows')
 need(paid==fp==Counter({1:2209,2:412,3:510,4:127,5:40}),'Complete paid source+suffix bill')
 need(all(rows[i]=={(i,()):Q(1)} for i in range(112,632)),'Every Y/helper original owner retained')
 ce=types.ModuleType('independent_candidate_ce');sys.modules[ce.__name__]=ce
 exec(compile((HERE/'inputs/clifford_exact.py').read_bytes(),'pinned_ce','exec'),ce.__dict__)
 barT=derive.conjugate(ce.canonical_frame(9,c['frames'][1]),ce)
 need(len(w['native_lifts'])==8,'Exactly8 actual native maps')
 phase_columns=0
 for j,rec in zip(derive.S,w['native_lifts']):
  fi=c['final'][112+j]
  need((rec['port'],rec['source_owner'],rec['from'],rec['to'],rec['rank'])==(j,112+j,fi,1,1),'Literal native boundary identity')
  need(rec['lowering']['rank']==1 and rec['actual_raw_dual_conjugation'] is True,'Native rank/actualbar binding')
  barV=derive.conjugate(ce.canonical_frame(9,c['frames'][fi]),ce)
  for k in range(512):
   need(derive.sparse(barV.circuit+rec['literal_circuit'],k)==derive.sparse(barT.circuit,k),'Actual frozen lift including phase')
   phase_columns+=1
 controls={}
 def rejected(name,word,error=None):
  try:r,_,_,_=engine.replay(c,word)
  except ValueError as e:
   if error:need(error in str(e),name+' intended rejection')
   controls[name]=True
  else:
   need(r[:632]!=target,name+' must change endpoint');controls[name]=True
 bad=json.loads(json.dumps(w['program']));idx=next(i for i in range(n,len(bad)) if bad[i][0]=='scalar' and bad[i][1][0]=='add');bad[idx][1][3]*=-1;rejected('scatter_sign',bad)
 bad=w['program'][:n]+[e for e in w['repair_suffix'] if e[0]!='center'];rejected('omit_lifts',bad,'Scalar source chart')
 rejected('erase_all_repairs',w['program'][:n])
 bad=json.loads(json.dumps(w['program']));idx=next(i for i in range(n,len(bad)) if bad[i][0]=='scalar' and bad[i][1][0]=='copy');bad[idx][1][1]=['L',112];rejected('borrowed_copy',bad,'Borrowed overwrite')
 bad=json.loads(json.dumps(w['program']));idx=next(i for i in range(n,len(bad)) if bad[i][0]=='scalar' and bad[i][1][0]=='clear');bad[idx][1][1]=['L',224];rejected('borrowed_clear',bad,'Borrowed erasure')
 need(target!=engine.expected([list(x) for x in zip(*F)],True),'F transpose distinction')
 controls['wrong_transpose']=True
 # Frozen actual circuit corruption, separate from symbolic chart replay.
 rec=w['native_lifts'][0];badcirc=rec['literal_circuit']+[['phase',1]];fi=rec['from'];barV=derive.conjugate(ce.canonical_frame(9,c['frames'][fi]),ce)
 need(derive.sparse(barV.circuit+badcirc,0)!=derive.sparse(barT.circuit,0),'Globalphase-only semantic corruption')
 controls['global_phase_only']=True
 coeff=Counter(Q(e[1][3],e[1][4]) for e in expected_suffix if e[0]=='scalar' and e[1][0]=='add')
 result={'status':'PASS_INDEPENDENT_FROZEN_RAWDUAL_ONE_REPAIR','all632_backward_rows':True,'all632_source_forward_rows':True,'all632_coded_backward_rows':True,'target_source_restored':True,'source_mutating_variant':False,'literal4929_backward_prefix_unchanged':True,'owned_C0_final_zero':not rows[632],'all112Y_and408helpers_retained':True,'paid':dict(paid),'source_prefix_l1':str(om),'new_prefix_l1':str(mx),'forward_prefix_l1':str(fm),'suffix_events':len(expected_suffix),'scatter_counts':{str(v):count for v,count in sorted(coeff.items())},'actual_frozen_phase_columns':phase_columns,'semantic_controls':controls,'replay_inherited_phase_scope':'Independent normalized free-word event interpreter. Complete inherited source physical warp semantics remain source premises; all4096NEWlift columns independentlychecked as Gaussian integers.','candidate_checker_imported':False,'new_kappa':None}
 print(json.dumps(result,indent=2))
 if '--emit' in sys.argv:(HERE/'REVIEW.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
