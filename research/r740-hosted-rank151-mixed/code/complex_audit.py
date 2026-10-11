"""Independent complex eleven-stage phase, owner, scalar and emitted stream audit.
No emitter, hosting expander or phase generator is imported.
Chafreaky with OpenAI Codex; mathematical/source lineage PR377/433/442. Apache-2.0.
"""
import copy,gzip,hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
M,H,K,L,T,V,R=89,9,5,11,8,120,560
W=2*K*V*T
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
blob=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()

def polynomial(terms):
 linear=[0]*M;quadratic=[0]*M
 for vector,sign in terms:
  assert 0<=vector<1<<M and sign in (-1,1)
  for i in range(M):
   if vector>>i&1:linear[i]=(linear[i]+sign)%4;quadratic[i]^=vector
 return linear,quadratic

def phases(ph,ports):
 assert ph['m']==M and ph['ports']==V and len(ph['recipes'])==V
 assert ph['terminal_omission_controls_rejected']==V and ph['cover_correction']['mandatory']
 checked=0
 for port,q in enumerate(ports):
  rec=ph['recipes'][port];assert rec['port']==port and rec['q']==q and q.bit_count()%2==1 and q.bit_count()!=H
  zero=next(i for i in range(H) if not q>>i&1);reflect=q^(1<<zero)
  order=[zero]+[i for i in range(H) if i!=zero]
  # Parent basis orders the remaining axes by swapping axis zero and 'zero'.
  order=list(range(H));order[0],order[zero]=order[zero],order[0]
  basis=[(1<<i)^(reflect if (reflect>>i)&1 else 0) for i in order]+[1<<i for i in range(H,M)]
  assert basis[0]==q and all((a&b).bit_count()%2==int(i==j) for i,a in enumerate(basis) for j,b in enumerate(basis))
  def desired(level,side):
   if level<0:return [(q,1)] if side==0 else []
   return [(1<<i,1) for i in range(H+8*level)]+([] if side==0 else [(q,-1)])
  def route(vector,level):
   if level==0:return vector
   off=H+8*(level-1);answer=0
   for i in range(H):
    if vector>>i&1:
     answer^=(q if q>>i&1 else 0)
     for j in range(8):
      if basis[j+1]>>i&1:answer^=1<<(off+j)
   for j in range(8):
    if vector>>(off+j)&1:answer^=basis[j+1]
   mask=((1<<H)-1)|(((1<<8)-1)<<off)
   answer^=vector&~mask;return answer
  assert len(rec['stage_alignment'])==L
  for s,alignment in enumerate(rec['stage_alignment']):
   columns=[route(1<<i,s) for i in range(M)]
   assert all(route(columns[i],s)==1<<i for i in range(M))
   assert all((a&b).bit_count()%2==int(i==j) for i,a in enumerate(columns) for j,b in enumerate(columns))
   for name,local,level,side,entry in [
    ('entry_X',[(q,1)],s-1,0,True),('entry_Y',[],s-1,1,True),
    ('exit_X',[(1<<i,1) for i in range(H)],s,0,False),
    ('exit_Y',[(1<<i,1) for i in range(H)]+[(q,-1)],s,1,False)]:
    terms=local+[(1<<i,1) for i in range(H,H+8*s)]
    actual=[(route(v,s),sgn) for v,sgn in terms];canonical=desired(level,side)
    a,b=(canonical,actual) if entry else (actual,canonical)
    la,qa=polynomial(a);lb,qb=polynomial(b);shift=alignment[name]
    assert 0<=shift<1<<M and qa==qb
    assert all((la[i]+2*((shift>>i)&1))%4==lb[i] for i in range(M));checked+=1
  expected=[]
  for j in range(1,K):
   for side in range(2):expected.extend([(-1,2*j-1,side),(2*j-1,2*j,side)])
  for j in range(K):
   for side in range(2):expected.append((2*j+2,L-1,side))
  assert len(rec['idle_children'])==len(expected)
  for child,(a,b,side) in zip(rec['idle_children'],expected):
   axes=child['orthogonal_axes'];assert child['rank']==len(axes)==8*(b-a)
   assert all(v in basis for v in axes) and len(set(axes))==len(axes)
   la,qa=polynomial([(v,1) for v in axes]);lb,qb=polynomial([(v,-sgn) for v,sgn in desired(a,side)]+desired(b,side))
   shift=child['translation_after'];assert 0<=shift<1<<M and qa==qb
   assert all((la[i]+2*((shift>>i)&1))%4==lb[i] for i in range(M));checked+=1
  la,qa=polynomial([(q,-1)]+desired(L-1,1));lb,qb=polynomial([(1<<i,1) for i in range(M)])
  assert rec['terminal_Y_translation']==q and qa==qb and la!=lb
  assert all((la[i]+2*((q>>i)&1))%4==lb[i] for i in range(M));checked+=1
 return checked

def validate(t,old,ph):
 assert (t['m'],t['h'],t['stages'],t['replicas'],t['live'],t['physical'])==(M,H,L,T,W,10178)
 assert t['local_programs']==old['local_programs'] and t['source_template_sha256']==hashlib.sha256(blob(old)).hexdigest()
 assert t['cover']=='all matrices in O(89,2), in lexicographic row order'
 assert t['bank_padding'] is None and t['private_namespace']==dict(centers=[W,W+16],tableau=[W+16,W+576],coefficient=[W+576,W+578])
 rows=[[int(i==j) for j in range(2*K)] for i in range(2*K)];levels=[-1]*K;last={};locals_=[];idle={};wins={};bridges=0;terminal=False;translated=False;corrected=False
 def add(d,s,c):rows[d]=[x+c*y for x,y in zip(rows[d],rows[s])]
 for position,e in enumerate(t['execution_schedule']):
  assert not corrected;kind=e['kind']
  if kind=='local':
   s,p,rev=e['stage'],e['pair'],e['reverse'];assert not terminal and s==len(locals_) and p==max(0,(s-1)//2) and rev==bool(s%2)
   assert levels[p]==s-1;levels[p]=s;locals_.append((position,s,p));last[p]=position
   add(2*p,2*p+1,-1) if rev else add(2*p+1,2*p,1)
  elif kind=='bridge':
   a,b,c=e['dst'],e['src'],e['coefficient'];assert 0<=a<K and 0<=b<K and a!=b and c in (-1,1) and levels[a]==levels[b] and not terminal
   add(2*a,2*b,c);add(2*b+1,2*a+1,-c);last[a]=last[b]=position;bridges+=1
  elif kind=='idle':
   i,p,lo,hi=e['idx'],e['pair'],e['source_level'],e['target_level'];assert i==len(idle) and levels[p]==lo and lo<=hi<L and e['rank']==8*(hi-lo)
   levels[p]=hi;idle[i]=e;wins[i]={s for pos,s,pp in locals_ if last.get(p,-1)<pos<position and pp!=p}
   expected=[4*(i//2)+i%2,4*(i//2)+2+i%2] if i<8 else [16+2*(i-8),17+2*(i-8)]
   assert e['phase_children']==expected
  elif kind=='terminal_Y_translations':
   assert levels==[L-1]*K and not terminal and not translated and e==dict(kind=kind,**t['terminal_translations']);translated=True
  elif kind=='terminal':
   assert translated and not terminal
   for j in range(K):rows[2*j],rows[2*j+1]=rows[2*j+1],[-x for x in rows[2*j]]
   terminal=True
  else:
   assert kind=='translate_every_live_family' and terminal and e==t['cover_final_correction'];corrected=True
 assert corrected and rows==[[int(i==j) for j in range(2*K)] for i in range(2*K)] and len(locals_)==L and bridges==12
 assert [e for e in t['execution_schedule'] if e['kind'] in ('local','bridge','terminal')]==t['recipe']
 assert t['terminal_translations']==dict(pairs=list(range(K)),vector='port q transported by cover matrix')
 assert t['cover_final_correction']==dict(kind='translate_every_live_family',formula=old['cover_final_correction']['formula'],families=[0,W],charged_calls_per_cover=W,must_follow_data_signed_exchange=True)
 assert t['hosting']['windows']=={str(i):[e['pair'],e['rank'],sorted(wins[i])] for i,e in idle.items() if e['rank'] and wins[i]}
 occupation=defaultdict(set);helpers={}
 for i,cp,off,width,s,h in t['hosting']['slots']:
  assert i in wins and s in wins[i] and 0<=cp<240 and 0<=h<R and width==9 and 0<=off and off+9<=idle[i]['rank']
  cells=set(range(off,off+9));assert not cells&occupation[i,cp];occupation[i,cp]|=cells
  assert (s,h) not in helpers;helpers[s,h]=(i,cp,off)
 assert set(helpers)=={(s,h) for s in range(L) for h in range(R)}
 profile=Counter();events=0;digest=hashlib.sha256()
 assert len(t['calls'])==L*T
 for idx,call in enumerate(t['calls']):
  s,rep=divmod(idx,T);p=max(0,(s-1)//2);ori='backward' if s%2 else 'forward'
  assert (call['stage'],call['replica'],call['pair'],call['orientation'])==(s,rep,p,ori)
  assert call['local_program_sha256']==hashlib.sha256(blob(t['local_programs'][ori])).hexdigest()
  own=call['owners'];assert len(own)==800 and len(set((f,tuple(r)) for f,r in own))==800
  for j,(family,route) in enumerate(own):
   if j<240:assert (family,route)==(rep*1200+(2*p+j//120)*120+j%120,[1,s,j%120])
   else:
    i,cp,off=helpers[s,j-240];pair=idle[i]['pair'];assert pair!=p
    assert (family,route)==(rep*1200+(2*pair+cp//120)*120+cp%120,[3,i,off,9])
  def operand(x):
   if not isinstance(x,list):return x
   assert len(x)==2 and x[0] in ('L','C')
   return own[x[1]] if x[0]=='L' else [W+x[1],['private_center',x[1]]]
  for event in t['local_programs'][ori]:
   z=copy.deepcopy(event);tag=z[0]
   if tag in ('climb','adapter'):
    if tag=='climb':profile[z[5]]+=1
    z[2]=own[z[2]]
   elif tag=='center':profile[z[4]]+=1;z[1]=[W+z[1],['private_center',z[1]]]
   elif tag=='scalar':z[1]=[operand(x) for x in z[1]]
   else:assert tag=='phase'
   digest.update(blob([s,rep,z])+b'\n');events+=1
 expected=[]
 for i,e in idle.items():
  for side,ch in enumerate(e['phase_children']):
   for port in range(V):
    rank=e['rank']-len(occupation[i,side*V+port]);pp=ph['recipes'][port]['idle_children'][ch]
    assert pp['rank']==e['rank']
    expected.append(dict(idle=i,side=side,port=port,phase_child=ch,rank=rank,hosted=e['rank']-rank,replicas=T,translation_after=pp['translation_after']))
    if rank:profile[rank]+=T
 assert t['idle_children']==expected
 assert M*W-sum(r*n for r,n in profile.items())==3264
 return profile,digest.hexdigest(),events

def bridge_controls(recipe):
 def matrix(skip):
  rows=[[int(i==j) for j in range(10)] for i in range(10)];count=0
  def add(d,s,c):rows[d]=[x+c*y for x,y in zip(rows[d],rows[s])]
  for e in recipe:
   if e['kind']=='local':
    p=e['pair'];add(2*p,2*p+1,-1) if e['reverse'] else add(2*p+1,2*p,1)
   elif e['kind']=='bridge':
    a,b,c=e['dst'],e['src'],e['coefficient']
    for d,s,sign in [(2*a,2*b,c),(2*b+1,2*a+1,-c)]:
     if count!=skip:add(d,s,sign)
     count+=1
   else:
    for j in range(5):rows[2*j],rows[2*j+1]=rows[2*j+1],[-x for x in rows[2*j]]
  assert count==24;return rows
 ident=[[int(i==j) for j in range(10)] for i in range(10)]
 assert matrix(-1)==ident
 for skip in range(24):assert matrix(skip)!=ident
 return list(range(24))

def main(parent,out):
 src=parent/'parent444/upstream442/parent/changed/split-centres'
 old=json.loads(gzip.decompress((src/'GLOBAL-TEMPLATE.json.gz').read_bytes()));t=json.loads(gzip.decompress((out/'GLOBAL-TEMPLATE.json.gz').read_bytes()))
 ph=read(out/'DATA-PHASES.json');word=json.loads(gzip.decompress((src/'CANONICAL-WORD.json.gz').read_bytes()));g=read(out/'GLOBAL.json')
 assert g['source_canonical_word_sha256']==sha(src/'CANONICAL-WORD.json.gz')
 pc=phases(ph,word['ports']);profile,digest,events=validate(t,old,ph);bc=bridge_controls(t['recipe'])
 assert t['exact_data_phase_recipe_sha256']==sha(out/'DATA-PHASES.json')==g['data_phase_sha256']
 assert t['exact_local_clifford_recipe_sha256']==sha(src/'CLIFFORD-RECIPES.json')==g['source_local_phase_sha256']
 assert hashlib.sha256(blob(t)).hexdigest()==g['template_sha256'] and profile==Counter({int(r):n for r,n in g['profile'].items()})
 assert digest==g['emitted_program_sha256'] and events==g['local_events']
 assert (g['live'],g['physical'],g['hosted_residuals'],g['bank_assignments'],g['deficit'],g['maxchild'])==(9600,10178,49280,0,3264,64)
 rejected=[]
 def reject(name,fn):
  q=copy.deepcopy(t);fn(q)
  try:validate(q,old,ph)
  except (AssertionError,KeyError,IndexError,TypeError):rejected.append(name)
  else:raise AssertionError('accepted '+name)
 reject('omitted call',lambda q:q['calls'].pop())
 reject('aliased helper',lambda q:q['calls'][0]['owners'].__setitem__(241,q['calls'][0]['owners'][240]))
 reject('cross replica helper',lambda q:q['calls'][0]['owners'][240].__setitem__(0,q['calls'][0]['owners'][240][0]+1200))
 reject('wrong residual width',lambda q:q['hosting']['slots'][0].__setitem__(3,8))
 reject('negative slot offset',lambda q:q['hosting']['slots'][0].__setitem__(2,-1))
 reject('wrong hosting stage',lambda q:q['hosting']['slots'][0].__setitem__(4,10))
 reject('duplicate helper slot',lambda q:q['hosting']['slots'].append(q['hosting']['slots'][0]))
 reject('missing helper slot',lambda q:q['hosting']['slots'].pop())
 reject('omit local scalar instruction',lambda q:q['local_programs']['forward'].pop())
 reject('wrong local orientation',lambda q:q['calls'][0].__setitem__('orientation','backward'))
 reject('omit terminal translations',lambda q:q['execution_schedule'].pop(next(i for i,e in enumerate(q['execution_schedule']) if e['kind']=='terminal_Y_translations')))
 reject('omit cover correction',lambda q:q['execution_schedule'].pop())
 reject('undercharge cover correction',lambda q:q['cover_final_correction'].__setitem__('charged_calls_per_cover',0))
 reject('omit idle remainder',lambda q:q['idle_children'].pop())
 reject('understate physical reserve',lambda q:q.__setitem__('physical',q['physical']-1))
 reject('wrong idle rank',lambda q:next(e for e in q['execution_schedule'] if e['kind']=='idle').__setitem__('rank',1))
 for name,fn in [('wrong stage phase',lambda q:q['recipes'][0]['stage_alignment'][10].__setitem__('exit_X',0)),('omit idle phase correction',lambda q:q['recipes'][0]['idle_children'][0].__setitem__('translation_after',0)),('omit terminal phase',lambda q:q['recipes'][0].__setitem__('terminal_Y_translation',0))]:
  q=copy.deepcopy(ph);fn(q)
  try:phases(q,word['ports'])
  except AssertionError:rejected.append(name)
  else:raise AssertionError('accepted '+name)
 result=dict(status='PASS_INDEPENDENT_COMPLEX_ELEVEN_AUDIT',template_sha256=g['template_sha256'],emitted_program_sha256=digest,
  local_events=events,profile={str(r):n for r,n in sorted(profile.items())},live=W,physical=10178,hosted_residuals=49280,bank_assignments=0,
  rank_mass=sum(r*n for r,n in profile.items()),deficit=3264,maxchild=max(profile),exact_phase_equalities=pc,exact_orthogonal_routes=1320,omitted_bridge_shears_rejected=bc,mutations_rejected=rejected,
  scalar_composition='Ten exact integer data rows plus the freshly checked 800-column local theorem, independently lifted over all 120 ports and 6160 separate stage helpers before hosting.')
 (out/'AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main(*map(Path,sys.argv[1:]))
