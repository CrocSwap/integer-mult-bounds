"""Independent full owner/window/route/phase/program audit of paid adapters.
Does not import the emitter or hosting solver. Parent phase checks are unchanged.
Chafreaky with OpenAI Codex assistance; Apache-2.0.
"""
import copy,gzip,hashlib,importlib.util,json,sys
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];M,H,K,L,T,V,R,W=89,9,5,11,8,120,560,9600
sp=importlib.util.spec_from_file_location('unchanged_phase_audit',ROOT.parent/'r740-hosted-rank149/code/complex_audit.py');PA=importlib.util.module_from_spec(sp);sp.loader.exec_module(PA)
from local_audit import adapter_check
blob=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ld=lambda p:json.loads(gzip.decompress(p.read_bytes())) if p.suffix=='.gz' else json.loads(p.read_text())

def validate(t,parent,word,programs,ad,ph):
 assert (t['m'],t['h'],t['stages'],t['replicas'],t['live'],t['physical'])==(M,H,L,T,W,10178)
 unchanged=['cover','recipe','execution_schedule','bank_padding','private_namespace','cover_final_correction','terminal_translations','exact_data_phase_recipe_sha256']
 for k in unchanged:assert t[k]==parent[k],('changed parent field',k)
 assert t['source_template_sha256']==hashlib.sha256(blob(parent)).hexdigest()
 assert t['local_programs']==programs and t['residual_adapters']==ad
 assert t['residual_route_semantics']==dict(chart='sigma columns are the recorded first-nine indices in U_q plus exterior axes, then unused basis indices in increasing order',owner='g=d*sigma^-1 in O(89,2)',pre='P_d (R^-1 tensor I) P_d^-1 before the entire local invocation',post='P_d (L^-1 tensor I) P_d^-1 after full-frame cleanup',net='P_g C_selected_pending_axes P_g^-1; identity on all spectator axes',helper_entry='no entrance gate; the borrowed value has the declared initial label interpretation',monomial_compiler_groups_per_wrapper=8)
 idle={};wins={};last={};locals_=[]
 for position,e in enumerate(t['execution_schedule']):
  k=e['kind']
  if k=='local':locals_.append((position,e['stage'],e['pair']));last[e['pair']]=position
  elif k=='bridge':last[e['dst']]=last[e['src']]=position
  elif k=='idle':
   i,p=e['idx'],e['pair'];assert i==len(idle);idle[i]=e;wins[i]={s for pos,s,pair in locals_ if last.get(p,-1)<pos<position and pair!=p}
 wanted_windows={str(i):[e['pair'],e['rank'],sorted(wins[i])] for i,e in idle.items() if e['rank'] and wins[i]}
 assert t['hosting']['windows']==wanted_windows and t['hosting']['max_helpers_per_physical_family_per_call']==1
 occupied=defaultdict(set);helper={};per_call=set()
 for i,cp,off,width,s,h in t['hosting']['slots']:
  assert i in idle and s in wins[i] and 0<=cp<240 and 0<=h<R
  f=word['start'][240+h];assert width==H-len(word['frames'][f]) and 0<=off and off+width<=idle[i]['rank']
  cells=set(range(off,off+width));assert not cells&occupied[i,cp];occupied[i,cp]|=cells
  assert (s,h) not in helper;helper[s,h]=(i,cp,off,width)
  host=(s,idle[i]['pair'],cp);assert host not in per_call,'two helpers on one physical host in the same call';per_call.add(host)
 assert set(helper)=={(s,h) for s in range(L) for h in range(R)}
 bases=[]
 for q in word['ports']:
  pivot=next(j for j in range(H) if not (q>>j)&1);a=q^(1<<pivot)
  order=[pivot if j==0 else 0 if j==pivot else j for j in range(H)]
  basis=[(1<<j)^(a if (a>>j)&1 else 0) for j in order]+[1<<j for j in range(H,M)]
  assert basis[0]==q and all((u&v).bit_count()%2==int(i==j) for i,u in enumerate(basis) for j,v in enumerate(basis));bases.append(basis)
 profile=Counter();events=wrappers=0;digest=hashlib.sha256();routes=0
 assert len(t['calls'])==L*T
 for index,call in enumerate(t['calls']):
  s,rep=divmod(index,T);pair=max(0,(s-1)//2);ori='backward' if s%2 else 'forward'
  assert (call['stage'],call['replica'],call['pair'],call['orientation'])==(s,rep,pair,ori)
  assert call['local_program_sha256']==hashlib.sha256(blob(programs[ori])).hexdigest()
  own=call['owners'];assert len(own)==800 and len(set(f for f,route in own))==800
  for j,(family,route) in enumerate(own):
   if j<240:assert (family,route)==(rep*1200+(2*pair+j//120)*120+j%120,[1,s,j%120]);continue
   h=j-240;i,cp,off,w=helper[s,h];p=idle[i]['pair'];side,port=divmod(cp,120);f=word['start'][j]
   assert family==rep*1200+(2*p+side)*120+port and p!=pair
   assert route[:5]==[4,i,off,w,f] and len(route)==6
   axis=route[5];assert len(axis)==H and len(set(axis))==H and all(0<=k<M for k in axis)
   ch=idle[i]['phase_children'][side];pending=ph['recipes'][port]['idle_children'][ch]['orthogonal_axes']
   assert [bases[port][k] for k in axis[:w]]==pending[off:off+w]
   # The extra coordinates are spectators, and the exact residual adapter is
   # identity on them after the call. Deterministic completion fixes routing.
   complement=[k for k in range(M) if k not in axis[:w]]
   assert axis[w:]==complement[:H-w]
   permutation=axis+[k for k in range(M) if k not in axis]
   assert sorted(permutation)==list(range(M))
   assert ad['recipes'][str(f)]['rank']==w
   routes+=1
  def operand(x):
   if not isinstance(x,list):return x
   assert len(x)==2 and x[0] in ('L','C')
   return own[x[1]] if x[0]=='L' else [W+x[1],['private_center',x[1]]]
  for event in programs[ori]:
   z=copy.deepcopy(event);tag=z[0]
   if tag in ('climb','adapter'):
    if tag=='climb':profile[z[5]]+=1
    z[2]=own[z[2]]
   elif tag=='residual_adapter':
    side,r,f=z[1:];assert f==word['start'][r] and f and 240<=r<800
    z[2]=own[r];z.append(ad['recipes'][str(f)][side]);wrappers+=1
   elif tag=='center':profile[z[4]]+=1;z[1]=[W+z[1],['private_center',z[1]]]
   elif tag=='scalar':z[1]=[operand(x) for x in z[1]]
   else:assert tag=='phase'
   digest.update(blob([s,rep,z])+b'\n');events+=1
 remainder=[]
 for i,e in idle.items():
  for side,ch in enumerate(e['phase_children']):
   for port in range(V):
    rank=e['rank']-len(occupied[i,side*V+port]);phase=ph['recipes'][port]['idle_children'][ch];assert phase['rank']==e['rank']
    remainder.append(dict(idle=i,side=side,port=port,phase_child=ch,rank=rank,hosted=e['rank']-rank,replicas=T,translation_after=phase['translation_after']))
    if rank:profile[rank]+=T
 assert t['idle_children']==remainder and M*W-sum(r*n for r,n in profile.items())==3264
 assert wrappers==158*L*T and routes==R*L*T
 return profile,digest.hexdigest(),events,routes,wrappers

def main(parent_dir,local,out):
 parent=ld(parent_dir/'GLOBAL-TEMPLATE.json.gz');t=ld(out/'GLOBAL-TEMPLATE.json.gz');ph=ld(out/'DATA-PHASES.json');word=ld(local/'CANONICAL-WORD.json.gz');programs=ld(local/'ADAPTED-PROGRAMS.json.gz');ad=ld(local/'RESIDUAL-ADAPTERS.json');g=ld(out/'GLOBAL.json')
 assert ld(local/'LOCAL-REVIEW.json')['status']=='PASS_INDEPENDENT_COMPLEX_KERNEL_LOCAL_REALIZATION'
 assert (parent_dir/'DATA-PHASES.json').read_bytes()==(out/'DATA-PHASES.json').read_bytes()
 pc=PA.phases(ph,word['ports']);bc=PA.bridge_controls(t['recipe']);ac=adapter_check(word,ad)
 profile,digest,events,routes,wrappers=validate(t,parent,word,programs,ad,ph)
 assert g['template_sha256']==hashlib.sha256(blob(t)).hexdigest() and g['profile']=={str(k):v for k,v in sorted(profile.items())}
 assert g['emitted_program_sha256']==digest and g['local_events']==events and g['wrapper_events']==wrappers
 assert g['charged_wrapper_groups']==2*R*8*L*T and g['max_helpers_per_physical_family_per_call']==1
 assert g['source_canonical_word_sha256']==t['source_canonical_word_sha256']==hashlib.sha256(blob(word)).hexdigest()
 assert g['source_local_phase_sha256']==t['exact_local_clifford_recipe_sha256']==sha(local/'CLIFFORD-RECIPES.json')
 assert g['residual_adapter_sha256']==sha(local/'RESIDUAL-ADAPTERS.json')
 assert t['exact_data_phase_recipe_sha256']==g['data_phase_sha256']==sha(out/'DATA-PHASES.json')
 assert (g['live'],g['physical'],g['hosted_residuals'],g['bank_assignments'],g['deficit'],g['maxchild'])==(9600,10178,49280,0,3264,64)
 rejected=[]
 def reject(name,fn):
  q=copy.deepcopy(t);fn(q)
  try:validate(q,parent,word,programs,ad,ph)
  except (AssertionError,KeyError,IndexError,TypeError,ValueError):rejected.append(name)
  else:raise AssertionError('accepted '+name)
 reject('omit a call',lambda q:q['calls'].pop())
 reject('alias physical helper family',lambda q:q['calls'][0]['owners'][241].__setitem__(0,q['calls'][0]['owners'][240][0]))
 reject('cross replica helper',lambda q:q['calls'][0]['owners'][240].__setitem__(0,q['calls'][0]['owners'][240][0]+1200))
 reject('wrong residual width',lambda q:q['hosting']['slots'][0].__setitem__(3,7))
 reject('negative slot offset',lambda q:q['hosting']['slots'][0].__setitem__(2,-1))
 reject('wrong hosting stage',lambda q:q['hosting']['slots'][0].__setitem__(4,10))
 reject('duplicate helper slot',lambda q:q['hosting']['slots'].append(q['hosting']['slots'][0]))
 reject('missing helper slot',lambda q:q['hosting']['slots'].pop())
 reject('omit paid residual pre adapter',lambda q:q['local_programs']['forward'].pop(0))
 reject('omit post adapter after cleanup',lambda q:q['local_programs']['forward'].pop())
 reject('wrong local orientation',lambda q:q['calls'][0].__setitem__('orientation','backward'))
 reject('omit terminal translations',lambda q:q['execution_schedule'].pop(next(i for i,e in enumerate(q['execution_schedule']) if e['kind']=='terminal_Y_translations')))
 reject('omit cover correction',lambda q:q['execution_schedule'].pop())
 reject('undercharge cover correction',lambda q:q['cover_final_correction'].__setitem__('charged_calls_per_cover',0))
 reject('omit idle remainder',lambda q:q['idle_children'].pop())
 reject('understate physical reserve',lambda q:q.__setitem__('physical',q['physical']-1))
 reject('claim a recursive helper entrance',lambda q:q['residual_route_semantics'].__setitem__('helper_entry','uncharged T_E'))
 reject('wrong route target axis',lambda q:q['calls'][0]['owners'][240][1][5].__setitem__(0,q['calls'][0]['owners'][240][1][5][1]))
 r=next(j for j in range(240,800) if word['start'][j])
 reject('spectator aliases selected axis',lambda q:q['calls'][0]['owners'][r][1][5].__setitem__(8,q['calls'][0]['owners'][r][1][5][0]))
 reject('omit residual phase',lambda q:q['residual_adapters']['recipes'][str(word['start'][r])]['post'].__setitem__('phase',99))
 reject('undercharge wrappers',lambda q:q['residual_route_semantics'].__setitem__('monomial_compiler_groups_per_wrapper',0))
 # Produce a geometrically legal two-helper packing which violates only the
 # new within-call ownership restriction before owner tables are considered.
 def combine(q):
  slots=q['hosting']['slots'];by=defaultdict(list);cap={e['idx']:e['rank'] for e in q['execution_schedule'] if e['kind']=='idle'}
  for z in slots:by[z[0],z[1]].append(z)
  for a in slots:
   i,cp,off,w,s,h=a;end=max(z[2]+z[3] for z in by[i,cp])
   for b in slots:
    if b[0]==i and b[4]==s and b[1]!=cp and end+b[3]<=cap[i]:b[1]=cp;b[2]=end;return
  raise RuntimeError('could not build within-call alias control')
 reject('disjoint slots but two helpers per host in one call',combine)
 for name,fn in [('wrong stage phase',lambda q:q['recipes'][0]['stage_alignment'][10].__setitem__('exit_X',0)),('omit idle phase correction',lambda q:q['recipes'][0]['idle_children'][0].__setitem__('translation_after',0)),('omit terminal phase',lambda q:q['recipes'][0].__setitem__('terminal_Y_translation',0))]:
  q=copy.deepcopy(ph);fn(q)
  try:PA.phases(q,word['ports'])
  except AssertionError:rejected.append(name)
  else:raise AssertionError('accepted '+name)
 result=dict(status='PASS_INDEPENDENT_ADAPTED_KERNEL_GLOBAL_AUDIT',template_sha256=g['template_sha256'],emitted_program_sha256=digest,local_events=events,profile={str(r):n for r,n in sorted(profile.items())},live=W,physical=10178,hosted_residuals=49280,bank_assignments=0,rank_mass=sum(r*n for r,n in profile.items()),deficit=3264,maxchild=max(profile),exact_phase_equalities=pc,exact_orthogonal_data_routes=1320,exact_residual_route_instances=routes,nontrivial_adapter_frames=ac,wrapper_events=wrappers,charged_wrapper_groups=g['charged_wrapper_groups'],max_helpers_per_physical_family_per_call=1,omitted_bridge_shears_rejected=bc,mutations_rejected=rejected,scope='Finite exact operator/ownership template with distinct borrowed families per call. Complete cover enumeration and all-size compilation remain inherited contracts.')
 (out/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main(*map(Path,sys.argv[1:]))
