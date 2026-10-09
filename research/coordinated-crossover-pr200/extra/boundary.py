"""Independent21-source paths, reflected ledgers, paid deltas and exact primes.
Prepared with substantial OpenAI Codex assistance; Apache-2.0.
Whole scalar word and complete assembly are checked separately.
"""
from pathlib import Path
from collections import Counter,defaultdict
import importlib.util,json,hashlib,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sp=importlib.util.spec_from_file_location('source492_boundary_setup',D/'setup.py');setup=importlib.util.module_from_spec(sp);sp.loader.exec_module(setup)
m=setup.m;W=m.W;C=m.C;selected=setup.extra
compact=lambda H:{str(k):v for k,v in sorted(H.items())if v}
oldsel=sum((json.loads((P/f'{side}/selection.json').read_text())for side in('borrow','gaugeb','newg')),[])
assert len(oldsel)==471 and len(selected)==21 and len(m.borrow)==492
usedroles={r['role']for r in oldsel};usedsource={r[k]for r in oldsel for k in('source','partner')};assert len(usedsource)==942
recipient={d:b for b,d in W.pairs};roots=defaultdict(list)
for j,r in enumerate(W.w['rootroles']):roots[r].append(W.w['root_frame'][j])
touched={s for i in W.phase1 for s in W.ops[i][:2]};positions={i:j for j,i in enumerate(W.phase1+W.rest)}
# Rebuild actual positive adjoint directly from literal retimed operations.
adj=[{}for _ in range(W.R)]
for root,role in zip(W.g['roots'],W.w['rootroles']):
 for t in root['targets']:adj[role][t]=adj[role].get(t,0)+1
for i in reversed(W.phase1+W.rest):
 if i in m.omitted:continue
 a,b,_=W.ops[i]
 for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
assert adj==m.adj

def histogram(chain,start):
 H=Counter();prev=None;d=start
 for f in chain:
  assert C.nondeg(f)and(prev is None or C.sub(prev,f));n=C.dimf[f];assert n>=d
  if n>d:H[n-d]+=1
  prev=f;d=n
 return H

def determinant(A):
 A=[list(r)for r in A];n=len(A)
 if not n:return 1
 den=1;sign=1
 for k in range(n-1):
  i=next((j for j in range(k,n)if A[j][k]),None)
  if i is None:return 0
  if i!=k:A[k],A[i]=A[i],A[k];sign=-sign
  pivot=A[k][k]
  for i in range(k+1,n):
   for j in range(k+1,n):
    x=A[i][j]*pivot-A[i][k]*A[k][j];assert x%den==0;A[i][j]=x//den
   A[i][k]=0
  den=pivot
 return sign*A[-1][-1]

def prime_record(B,dual=False):
 sums=list(map(sum,B));scale=9-W.h if dual else 9;sign=1 if dual else -1
 gram=[[scale*W.module.dot(x,y)+sign*sums[i]*sums[j]for j,y in enumerate(B)]for i,x in enumerate(B)]
 det=determinant(gram);assert det;rest=abs(det);powers={}
 for p in(2,3,5,7,11,13,17,19,23,29,31):
  exponent=0
  while rest%p==0:rest//=p;exponent+=1
  powers[str(p)]=exponent
 assert 0<rest<2**80
 check=rest
 for p,e in powers.items():check*=int(p)**e
 assert check==abs(det)
 return dict(dimension=len(B),cleared_determinant=det,small_prime_powers=powers,remaining_factor=rest)
rows=[];delta=Counter();newroles=set();newsource=set();frames=set()
for r in selected:
 role,s,p=r['role'],r['source'],r['partner'];e=m.kpair[s];M=e['mix_frame'];G=W.register(r.get('split_gauge_basis',r['gauge_basis']));frames.add(G)
 assert role not in usedroles|newroles|touched|m.removed|set(W.source.values())|set(W.donor)
 assert not({s,p}&(usedsource|newsource));newsource.update((s,p));newroles.add(role)
 assert p==e['carrier']and C.dimf[M]==2 and C.dimf[G]in(2,4)and C.sub(M,G)
 assert adj[role]==m.adj[role]and sorted(adj[role])==r['targets'];ops=W.role_ops[role]
 assert ops and ops[0]==r['first_operation']and C.sub(G,W.opframe[ops[0]])
 aux=[W.opframe[i]for i in ops]+roots[role]
 if role in recipient:
  rec=recipient[role];assert positions[ops[-1]]<positions[W.role_ops[rec][0]]
  aux+=[W.gauge[rec]['frame']]+[W.opframe[i]for i in W.role_ops[rec]]+roots[rec]
 aux.append(W.w['full_frame']);chain=[W.w['source_frame'][s],M,G]+aux
 oldaux=histogram(aux,0);oldsource=histogram(e['passive_chain'][1:],1);newhist=histogram(chain[1:],1)
 reflection=Counter()
 for a,b in zip(reversed(chain),list(reversed(chain))[1:]):
  assert all(W.module.dot(x,y)==0 for x in C.A[a]for y in C.B[b]);d=len(C.A[b])-len(C.A[a]);assert d>=0
  if d:reflection[d]+=1
 assert reflection==newhist
 rowdelta=Counter(newhist);rowdelta.subtract(oldaux);rowdelta.subtract(oldsource);assert sum(k*v for k,v in rowdelta.items())==-24
 delta.update(rowdelta);rows.append(dict(role=role,source=s,partner=p,alias_recipient=recipient.get(role),source_gauge=C.dimf[G],source_path=chain,old_aux_histogram=compact(oldaux),old_source_histogram=compact(oldsource),complete_source_histogram=compact(newhist),source_delta=compact(rowdelta),reflected_equal=True))
assert len(newroles)==21 and len(newsource)==42 and sum(k*v for k,v in delta.items())==-504
primes=[dict(frame=f,basis=C.B[f],annihilator=C.A[f],primal=prime_record(C.B[f]),dual=prime_record(C.A[f],True))for f in sorted(frames)]
result=dict(status='PASS_SOURCE492_INDEPENDENT_SOURCE_AUX_PATHS_BOTH_REFLECTIONS_AND_PRIMES',selected=21,source_local_delta=compact(delta),local_rank_delta=-504,shared_rank_delta=-1512,W_delta=-21,deficit_delta=0,endpoint_rows=rows,source_gauge_prime_witnesses=primes,maximum_prime_residual=max(r[k]['remaining_factor']for r in primes for k in('primal','dual')),all_source_paths_reflected=True,scope='Independent complete changed source/auxiliary paths and exact paid histograms; target ledger, literal scalar word and assembly separately checked.',input_pins={str(p.relative_to(P)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(D/'selection.json',D/'setup.py',Path(__file__),P/'newg/replay.py')})
(D/'boundary.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS21 source/auxiliary paths, reflected ledgers,42 primal/dual prime witnesses',compact(delta),flush=True)
