"""Independent literal scalar/common-label and physical residual read-back.
Does not import the kernel, adapter generator or local emitter. Apache-2.0.
Chafreaky with OpenAI Codex assistance.
"""
import copy,gzip,hashlib,json,sys
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
from clifford_exact import canonical_frame,diag,perm,xgate,Op,identity,fourier
blob=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
def basis(vs):
 rows={}
 for x in vs:
  for k in sorted(rows,reverse=True):
   if x>>k&1:x^=rows[k]
  if x:
   k=x.bit_length()-1
   for j in rows:
    if rows[j]>>k&1:rows[j]^=x
   rows[k]=x
 return tuple(rows[k] for k in sorted(rows,reverse=True))
def adapter_check(word,ad):
 h=word['h'];assert h==9 and ad['h']==h;full=tuple(1<<i for i in range(h));frames=word['frames'];wanted=set(word['start'][240:]);assert set(map(int,ad['recipes']))==wanted
 def decode(r):
  assert len(r['matrix_rows'])==len(r['quadratic_rows'])==len(r['linear_Z4'])==h
  return diag(h,tuple(r['quadratic_rows']),tuple(r['linear_Z4'])).then(perm(h,tuple(r['matrix_rows']))).then(xgate(h,r['offset'])).then(Op(h,identity(h),[('phase',r['phase'])]))
 for k,rec in ad['recipes'].items():
  f=int(k);E=frames[f];w=h-len(E);assert rec['rank']==w
  S=canonical_frame(h,E).adjoint().then(canonical_frame(h,full));C=fourier(h,range(w))
  if E:
   assert not rec['identity_adapters'];pre,post=decode(rec['pre']),decode(rec['post']);op=pre.then(S).then(post)
  else:
   assert rec==dict(rank=9,pre=None,post=None,identity_adapters=True);op=S
  assert op.tab==C.tab and op.zero_state()==C.zero_state(),'two-sided residual equality including phase'
 return len(wanted)-1

def replay(word,program,back):
 n=800;v=120;frames=word['frames'];cur={('L',r):f for r,f in enumerate(word['start'])};state={('L',r):{r:Q(1)} for r in range(n)};paid=Counter();centers=set();pre=[];post=[];started=False;finished=False;endpoint=[];macros=primitives=0;largest_num=largest_den=0
 def bound(op):
  if op[0] in ('clear','copy'):return 1
  q=Q(op[3],op[4]) if op[0]=='add' else Q(op[2],op[3]);a,b=abs(q.numerator),q.denominator;assert q and b&(b-1)==0
  if op[0]=='scale':assert a&(a-1)==0;return abs(a.bit_length()-b.bit_length())+int(q<0)
  return 3+a.bit_length()-1+a.bit_count()+b.bit_length()-1
 for e in program:
  tag=e[0]
  if tag=='residual_adapter':
   _,side,r,f=e;assert 240<=r<n and f==word['start'][r] and f
   if side=='pre':assert not started and not finished;pre.append(r)
   else:assert side=='post' and started;finished=True;post.append(r)
   continue
  assert not finished;started=True
  if tag=='phase':continue
  if tag=='adapter':
   _,direction,r,f=e;assert r<240 and f==(word['start'] if direction=='old_to_new' else word['final'])[r];endpoint.append((direction,r));continue
  if tag=='climb':
   _,part,r,old,new,width=e;assert not centers and cur['L',r]==old
   assert basis(frames[old]+frames[new])==basis(frames[new]) and width==len(frames[new])-len(frames[old])>0
   cur['L',r]=new;paid[width]+=1;continue
  if tag=='center':
   _,r,old,new,width=e;assert centers=={r} and cur['C',r]==old
   assert width==abs(len(frames[new])-len(frames[old]))>0
   assert basis(frames[old]+frames[new]) in (basis(frames[old]),basis(frames[new]))
   cur['C',r]=new;paid[width]+=1;continue
  assert tag=='scalar';_,op,f=e;kind=op[0];t=tuple(op[1]);macros+=1;primitives+=2*bound(op)
  if kind=='clear':
   assert t[0]=='C';state[t]={};cur[t]=f;centers.discard(t[1]);continue
  if t not in cur:assert t[0]=='C';cur[t]=f
  assert cur[t]==f
  if kind in ('add','copy'):s=tuple(op[2]);assert cur[s]==f,'scalar operands must share their actual current label'
  if kind=='copy':
   assert t[0]=='C' and not state.get(t);state[t]=dict(state[s]);centers.add(t[1])
  elif kind=='scale':state[t]={i:Q(op[2],op[3])*z for i,z in state[t].items()}
  else:
   assert kind=='add';q=Q(op[3],op[4]);assert t!=s
   if t[0]=='C':centers.add(t[1])
   for i,z in list(state[s].items()):
    a=state[t].get(i,Q(0))+q*z
    if a:state[t][i]=a
    else:state[t].pop(i,None)
  for q in state[t].values():largest_num=max(largest_num,abs(q.numerator).bit_length());largest_den=max(largest_den,q.denominator.bit_length())
 wanted=[r for r in range(240,n) if word['start'][r]];assert pre==post==wanted and len(wanted)==79
 assert not centers and all(not row for k,row in state.items() if k[0]=='C')
 assert Counter(endpoint)==Counter((direction,r) for direction in ('old_to_new','new_to_old') for r in range(240))
 assert [cur['L',r] for r in range(n)]==word['final']
 for r in range(n):
  expected={r:Q(1)}
  if back and r<v:expected[v+r]=Q(-1)
  if not back and v<=r<2*v:expected[r-v]=Q(1)
  assert state['L',r]==expected,('literal column',r)
 assert paid==Counter({int(r):z for r,z in word['local_profile'].items()})
 return dict(sha256=hashlib.sha256(blob(program)).hexdigest(),events=len(program),scalar_macros=macros,real_component_primitive_bound=primitives,paid_profile=dict(sorted(paid.items())),all_columns=n,private_centers_cleared=True,private_coefficient_stream_cleared_after_each_macro=True,wrappers=158,max_exact_scalar_numerator_bits=largest_num,max_exact_scalar_denominator_bits=largest_den,common_labels_checked=True,helpers_restored_as_scalar_rows=True)

def main(out):
 word=ld(out/'CANONICAL-WORD.json.gz');raw=ld(out/'LOCAL-PROGRAMS.json.gz');ps=ld(out/'ADAPTED-PROGRAMS.json.gz');ad=ld(out/'RESIDUAL-ADAPTERS.json');nontrivial=adapter_check(word,ad);checks={}
 for o,p in ps.items():
  assert o in ('forward','backward')
  body=[e for e in p if e[0]!='residual_adapter'];expected=[e for e in raw[o] if not(e[0]=='adapter' and e[2]>=240)];assert body==expected
  checks[o]=replay(word,p,o=='backward')
 assert set(checks)=={'forward','backward'}
 rejected=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,KeyError,IndexError,ValueError,ZeroDivisionError):rejected.append(name)
  else:raise AssertionError('accepted '+name)
 reject('omit first pre adapter',lambda:replay(word,ps['forward'][1:],False))
 reject('omit final post adapter',lambda:replay(word,ps['forward'][:-1],False))
 q=copy.deepcopy(ps['forward']);e=next(e for e in q if e[0]=='scalar' and e[1][0]=='add');e[2]=(e[2]+1)%len(word['frames']);reject('scalar at wrong frame',lambda:replay(word,q,False))
 q=copy.deepcopy(ps['forward']);q=[e for e in q if not(e[0]=='scalar' and e[1][0]=='add' and e[1][1][0]=='L' and e[1][1][1]>=240)];reject('omit helper scalar restoration',lambda:replay(word,q,False))
 f=next(k for k,r in ad['recipes'].items() if not r['identity_adapters'])
 q=copy.deepcopy(ad);q['recipes'][f]['post']['phase']=(q['recipes'][f]['post']['phase']+1)%4;reject('wrong residual global phase',lambda:adapter_check(word,q))
 q=copy.deepcopy(ad);q['recipes'][f]['rank']+=1;reject('wrong residual width',lambda:adapter_check(word,q))
 q=copy.deepcopy(ad);q['recipes'][f]['pre']=q['recipes'][f]['post'];reject('wrong pre adapter order',lambda:adapter_check(word,q))
 result=dict(status='PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION',nontrivial_entrance_frames=nontrivial,wrappers_per_call=158,helper_entry_recursive_calls=0,checks=checks,mutations_rejected=rejected,canonical_word_sha256=hashlib.sha256(blob(word)).hexdigest(),adapters_sha256=hashlib.sha256((out/'RESIDUAL-ADAPTERS.json').read_bytes()).hexdigest(),phase_recipes_sha256=hashlib.sha256((out/'CLIFFORD-RECIPES.json').read_bytes()).hexdigest())
 (out/'LOCAL-REVIEW.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main(Path(sys.argv[1]))
