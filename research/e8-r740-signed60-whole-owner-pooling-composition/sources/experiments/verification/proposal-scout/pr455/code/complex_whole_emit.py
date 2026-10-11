"""Eleven-stage dimension89 complex supplier with every rank9 helper hosted.
Adapted from Zhihao Chen PR377, icekylinx PR433 and DaysSky PR442.
Integration: chafreaky with OpenAI Codex assistance. Apache-2.0.
"""
import gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path
HERE=Path(__file__).resolve().parent
import hosting_core_bounded as HC
V,R,K,L,T,M,H=120,560,5,11,8,89,9
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
canonical=lambda x:json.dumps(x,sort_keys=True,separators=(',',':')).encode()

def recipe():
 es=[dict(kind='local',stage=0,pair=0,reverse=False)]
 for j in range(K):
  es.append(dict(kind='local',stage=2*j+1,pair=j,reverse=True))
  if j<K-1:es.append(dict(kind='bridge',dst=j,src=j+1,coefficient=1))
  es.append(dict(kind='local',stage=2*j+2,pair=j,reverse=False))
  if j<K-1:es.append(dict(kind='bridge',dst=j,src=j+1,coefficient=-1))
 for j in reversed(range(K-1)):es.append(dict(kind='bridge',dst=j+1,src=j,coefficient=1))
 es.append(dict(kind='terminal'));return es

def build(src,out,selection):
 old=dict(local_programs=json.loads(gzip.decompress((src/'LOCAL-PROGRAMS.json.gz').read_bytes())),cover_final_correction=dict(formula='delta_i=(weight(row_i(g))-1)/2 mod 2'))
 local=read(src/'LOCAL-CHECKS.json');ind=read(src/'SCALAR-FRAME-AUDIT.json');phase=read(out/'DATA-PHASES.json')
 assert ind['live_columns_each_orientation']==800 and ind['all_target_rows_correct'] and ind['all_live_source_and_helper_rows_restored']
 assert phase['m']==M and phase['ports']==V and phase['terminal_omission_controls_rejected']==V
 assert phase['cover_correction']['mandatory'] and all(local[o]['all_columns']==800 for o in local)
 c=json.loads(gzip.decompress((src/'CANONICAL-WORD.json.gz').read_bytes()))
 assert c['h']==H and c['v']==V and c['R']==R
 for o,es in old['local_programs'].items():assert hashlib.sha256(canonical(es)).hexdigest()==local[o]['sha256']
 es=recipe();schedule=[];levels=[-1]*K;idx=0
 def idle(pair,to,phase_indices):
  nonlocal idx
  lo=levels[pair];rr=8*(to-lo);levels[pair]=to
  schedule.append(dict(kind='idle',pair=pair,idx=idx,rank=rr,source_level=lo,target_level=to,phase_children=phase_indices));idx+=1
 for e in es:
  schedule.append(dict(e))
  if e['kind']=='local':
   s,p=e['stage'],e['pair'];assert levels[p]==s-1;levels[p]=s
   if 0<s<2*K-1:
    j=(s+1)//2 if s%2 else s//2;b=4*(j-1)+(0 if s%2 else 1)
    idle(j,s,[b,b+2])
   elif s==2*K:
    for j in range(K):idle(j,s,[4*(K-1)+2*j,4*(K-1)+2*j+1])
 assert levels==[L-1]*K
 win={i:w for i,w in HC.windows(schedule).items() if w[1] and w[2]}
 ys,zs,val=HC.load_selection(selection,'bit')
 slots,rem=HC.expand(win,ys,zs,{s:[(r*R+h,H) for r in range(T) for h in range(R)] for s in range(L)},T*2*V)
 hosted={(s,h//R,h%R):(i,cp,off,w) for i,cp,off,w,s,h in slots};assert len(hosted)==len(slots)==L*T*R
 W=2*K*V*T;centers=len(c['centers']);physical=W+R+centers+2
 calls=[];paid=Counter();digest=hashlib.sha256();nevents=0
 for e in es:
  if e['kind']!='local':continue
  s,p=e['stage'],e['pair'];ori='backward' if e['reverse'] else 'forward'
  for rep in range(T):
   owners=[[rep*(2*K*V)+(2*p+j//V)*V+j%V,[1,s,j%V]] for j in range(2*V)]
   for h in range(R):
    i,cp,off,w=hosted[s,rep,h];host_rep,within=divmod(cp,2*V);side,port=divmod(within,V)
    owners.append([host_rep*(2*K*V)+(2*win[i][0]+side)*V+port,[3,i,off,w]])
   assert len(set((f,tuple(r)) for f,r in owners))==800
   call=dict(stage=s,replica=rep,pair=p,orientation=ori,owners=owners,local_program_sha256=local[ori]['sha256']);calls.append(call)
   for r,n in local[ori]['paid_profile'].items():paid[int(r)]+=n
   for z in old['local_programs'][ori]:
    tag=z[0]
    if tag=='phase':row=z
    elif tag=='adapter':row=[tag,z[1],owners[z[2]],*z[3:]]
    elif tag=='climb':row=[tag,z[1],owners[z[2]],*z[3:]]
    elif tag=='center':row=[tag,[W+z[1],['private_center',z[1]]],*z[2:]]
    else:
     assert tag=='scalar';macro=[]
     for x in z[1]:
      if isinstance(x,list) and len(x)==2 and x[0] in ('L','C'):
       macro.append(owners[x[1]] if x[0]=='L' else [W+x[1],['private_center',x[1]]])
      else:macro.append(x)
     row=[tag,macro,z[2]]
    digest.update(canonical([s,rep,row])+b'\n');nevents+=1
 idle_children=[]
 for e in schedule:
  if e['kind']!='idle':continue
  i=e['idx']
  for side,ch in enumerate(e['phase_children']):
   for port in range(V):
    ph=phase['recipes'][port]['idle_children'][ch];assert ph['rank']==e['rank']
    for rep in range(T):
     cp=rep*2*V+side*V+port;rr=rem[i,cp] if i in win else e['rank']
     if rr:paid[rr]+=1
     idle_children.append(dict(idle=i,side=side,port=port,replica=rep,phase_child=ch,rank=rr,hosted=e['rank']-rr,replicas=1,translation_after=ph['translation_after']))
 assert M*W-sum(r*n for r,n in paid.items())==(2*K*V-72*L)*T==3264
 correction=dict(kind='translate_every_live_family',formula=old['cover_final_correction']['formula'],families=[0,W],charged_calls_per_cover=W,must_follow_data_signed_exchange=True)
 schedule.insert(len(schedule)-1,dict(kind='terminal_Y_translations',pairs=list(range(K)),vector='port q transported by cover matrix'))
 schedule.append(dict(correction))
 template=dict(version='complex-eleven-whole-cross-replica-v1',m=M,h=H,stages=L,replicas=T,live=W,physical=physical,
  cover='all matrices in O(89,2), in lexicographic row order',recipe=es,execution_schedule=schedule,
  local_programs=old['local_programs'],calls=calls,idle_children=idle_children,bank_padding=None,
  exact_data_phase_recipe_sha256=sha(out/'DATA-PHASES.json'),exact_local_clifford_recipe_sha256=sha(src/'CLIFFORD-RECIPES.json'),
  private_namespace=dict(centers=[W,W+centers],tableau=[W+centers,W+centers+R],coefficient=[physical-2,physical]),
  cover_final_correction=correction,terminal_translations=dict(pairs=list(range(K)),vector='port q transported by cover matrix'),
  hosting=dict(windows={str(i):[w[0],w[1],sorted(w[2])] for i,w in win.items()},slots=[list(z) for z in slots]),
  route_semantics=dict(data='right factor rho(q,stage), exact orthogonal involution in DATA-PHASES proof',helper='coordinate permutation followed by pending idle basis U_q; maps whole rank9 residual onto its assigned interval',work='private disjoint family, cleared after every invocation'),
  source_local_programs_sha256=sha(src/'LOCAL-PROGRAMS.json.gz'),selection_sha256=sha(selection),source_binding='Inherited PR451 local primitive/phase interfaces; whole helper moves only, no split residual')
 blob=canonical(template);(out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))
 result=dict(status='PASS_COMPLEX_ELEVEN_WHOLE_POOLED_TEMPLATE',template_sha256=hashlib.sha256(blob).hexdigest(),m=M,live=W,physical=physical,
  stages=L,replicas=T,hosted_residuals=L*T*R,bank_assignments=0,profile=dict(sorted(paid.items())),rank_mass=sum(r*n for r,n in paid.items()),deficit=3264,
  maxchild=max(paid),local_invocations=len(calls),local_events=nevents,emitted_program_sha256=digest.hexdigest(),
  source_local_checks=local,source_canonical_word_sha256=sha(src/'CANONICAL-WORD.json.gz'),source_local_phase_sha256=sha(src/'CLIFFORD-RECIPES.json'),
  data_phase_sha256=sha(out/'DATA-PHASES.json'),private_centers=centers)
 (out/'GLOBAL.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':build(*map(Path,sys.argv[1:]))
