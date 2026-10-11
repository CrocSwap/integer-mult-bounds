"""Whole-residual complex hosting with paid adapters and one helper per host/call.
Schedule/phase lineage PR451, hosting PR442, kernel PR449.
Chafreaky with OpenAI Codex assistance; Apache-2.0.
Usage: emit.py PARENT451_COMPLEX LOCAL_SPLIT_CENTRES OUT
"""
import copy,gzip,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];M,H,K,L,T,V,R=89,9,5,11,8,120,560;W=9600
ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())
blob=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def build(parent,local,out):
 out.mkdir(exist_ok=True,parents=True);old=ld(parent/'GLOBAL-TEMPLATE.json.gz');ph=ld(parent/'DATA-PHASES.json');c=ld(local/'CANONICAL-WORD.json.gz');review=ld(local/'LOCAL-REVIEW.json');ad=ld(local/'RESIDUAL-ADAPTERS.json');programs=ld(local/'ADAPTED-PROGRAMS.json.gz')
 assert review['status']=='PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION'
 assert (old['m'],old['h'],old['stages'],old['replicas'])==(M,H,L,T)
 assert ph['ports']==V and [p['q'] for p in ph['recipes']]==c['ports']
 (out/'DATA-PHASES.json').write_bytes((parent/'DATA-PHASES.json').read_bytes())
 schedule=copy.deepcopy(old['execution_schedule']);idle={e['idx']:e for e in schedule if e['kind']=='idle'}
 wins={int(i):(p,r,set(st)) for i,(p,r,st) in old['hosting']['windows'].items()}
 widths={h:H-len(c['frames'][c['start'][2*V+h]]) for h in range(R)}
 pool={(s,w):[h for h in range(R) if widths[h]==w] for s in range(L) for w in set(widths.values())}
 selected=ld(ROOT/'data/hosting.json')['selected'];counts=Counter();slots=[];rem={};helpers={}
 for e in selected:
  i=e['idle'];pair,rank,allowed=wins[i];pat=e['pattern'];assert len(pat)==len({s for s,w in pat})
  for _ in range(e['copies']):
   cp=counts[i];counts[i]+=1;assert cp<240;off=0
   for s,w in pat:
    assert s in allowed and off+w<=rank;h=pool[s,w].pop();slots.append([i,cp,off,w,s,h]);helpers[s,h]=(i,cp,off,w);off+=w
   rem[i,cp]=rank-off
 assert len(slots)==L*R and all(n==240 for n in counts.values()) and all(not xs for xs in pool.values())
 # U_q followed by exterior coordinate vectors is the parent's exact idle basis.
 bases=[]
 for q in c['ports']:
  z=next(i for i in range(H) if not(q>>i&1));a=q^(1<<z);order=list(range(H));order[0],order[z]=order[z],order[0]
  bases.append([(1<<i)^(a if a>>i&1 else 0) for i in order]+[1<<i for i in range(H,M)])
 routes={}
 for s,h in helpers:
  i,cp,off,w=helpers[s,h];side,port=divmod(cp,V);phase=ph['recipes'][port]['idle_children'][idle[i]['phase_children'][side]]
  wanted=phase['orthogonal_axes'][off:off+w];axis=[bases[port].index(x) for x in wanted]
  axis+= [j for j in range(M) if j not in axis][:H-w]
  assert len(axis)==H and len(set(axis))==H
  routes[s,h]=axis
 calls=[];paid=Counter();digest=hashlib.sha256();events=0
 for s in range(L):
  p=max(0,(s-1)//2);ori='backward' if s%2 else 'forward'
  for rep in range(T):
   own=[[rep*1200+(2*p+j//V)*V+j%V,[1,s,j%V]] for j in range(240)]
   for h in range(R):
    i,cp,off,w=helpers[s,h];pair=wins[i][0];side,port=divmod(cp,V)
    own.append([rep*1200+(2*pair+side)*V+port,[4,i,off,w,c['start'][240+h],routes[s,h]]])
   assert len({f for f,r in own})==800,'every helper must have a distinct physical family within a call'
   call=dict(stage=s,replica=rep,pair=p,orientation=ori,owners=own,local_program_sha256=hashlib.sha256(blob(programs[ori])).hexdigest());calls.append(call)
   for rank,num in review['checks'][ori]['paid_profile'].items():paid[int(rank)]+=num
   for e in programs[ori]:
    z=copy.deepcopy(e);tag=z[0]
    if tag in ('adapter','climb'):z[2]=own[z[2]]
    elif tag=='residual_adapter':
     f=z[3];z[2]=own[z[2]];z.append(ad['recipes'][str(f)][z[1]])
    elif tag=='center':z[1]=[W+z[1],['private_center',z[1]]]
    elif tag=='scalar':
     z[1]=[own[x[1]] if isinstance(x,list) and x[0]=='L' else [W+x[1],['private_center',x[1]]] if isinstance(x,list) and x[0]=='C' else x for x in z[1]]
    else:assert tag=='phase'
    digest.update(blob([s,rep,z])+b'\n');events+=1
 remainder=[]
 for i,e in idle.items():
  for side,ch in enumerate(e['phase_children']):
   for port in range(V):
    rank=rem.get((i,side*V+port),e['rank']);phase=ph['recipes'][port]['idle_children'][ch]
    if rank:paid[rank]+=T
    remainder.append(dict(idle=i,side=side,port=port,phase_child=ch,rank=rank,hosted=e['rank']-rank,replicas=T,translation_after=phase['translation_after']))
 assert M*W-sum(r*n for r,n in paid.items())==3264
 t=copy.deepcopy(old);t.update(version='complex-eleven-adapted-kernel-v1',local_programs=programs,calls=calls,idle_children=remainder,
  hosting=dict(windows=old['hosting']['windows'],slots=slots,max_helpers_per_physical_family_per_call=1),
  residual_adapters=ad,exact_local_clifford_recipe_sha256=sha(local/'CLIFFORD-RECIPES.json'),
  source_template_sha256=hashlib.sha256(blob(old)).hexdigest(),source_canonical_word_sha256=hashlib.sha256(blob(c)).hexdigest(),
  residual_route_semantics=dict(chart='sigma columns are the recorded first-nine indices in U_q plus exterior axes, then unused basis indices in increasing order',owner='g=d*sigma^-1 in O(89,2)',pre='P_d (R^-1 tensor I) P_d^-1 before the entire local invocation',post='P_d (L^-1 tensor I) P_d^-1 after full-frame cleanup',net='P_g C_selected_pending_axes P_g^-1; identity on all spectator axes',helper_entry='no entrance gate; the borrowed value has the declared initial label interpretation',monomial_compiler_groups_per_wrapper=8))
 t['route_semantics']['helper']='whole residual made coordinate by explicit paid two-sided monomials; at most one helper per physical family per invocation'
 encoded=blob(t);(out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(encoded,mtime=0))
 result=dict(status='PASS_COMPLEX_ADAPTED_KERNEL_TEMPLATE',template_sha256=hashlib.sha256(encoded).hexdigest(),m=M,live=W,physical=10178,stages=L,replicas=T,hosted_residuals=L*T*R,bank_assignments=0,profile=dict(sorted(paid.items())),rank_mass=sum(r*n for r,n in paid.items()),deficit=3264,maxchild=max(paid),local_invocations=len(calls),local_events=events,emitted_program_sha256=digest.hexdigest(),source_local_checks=review['checks'],source_canonical_word_sha256=hashlib.sha256(blob(c)).hexdigest(),source_local_phase_sha256=sha(local/'CLIFFORD-RECIPES.json'),data_phase_sha256=sha(out/'DATA-PHASES.json'),private_centers=16,residual_adapter_sha256=sha(local/'RESIDUAL-ADAPTERS.json'),wrapper_events=158*L*T,charged_wrapper_groups=2*R*8*L*T,max_helpers_per_physical_family_per_call=1)
 (out/'GLOBAL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':build(*map(Path,sys.argv[1:]))
