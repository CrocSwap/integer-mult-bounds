"""Exact R781 signed-prefix, heterogeneous-bank, and padding-fusion composition.
Rohan Arun with OpenAI Codex assistance. Conditional finite construction.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import copy,gzip,hashlib,importlib.util,json,math,sys,time
assert __debug__
sys.dont_write_bytecode=True;sys.set_int_max_str_digits(0)
ROOT=Path(__file__).resolve().parent;SOURCE=ROOT.parent/'e8-r781-signed-source';BOOT=ROOT.parent/'e8-prefix-bootstrap';FUSION=ROOT.parent/'e8-signed-padding'
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
F=mod('inherited_fusion',FUSION/'fusion.py');E,W,S,C=F.E,F.W,F.S,F.C
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):
 raw=Path(p).read_bytes();return json.loads(gzip.decompress(raw) if raw[:2]==b'\x1f\x8b' else raw)
def blob(x):return json.dumps(F.encode(x),sort_keys=True,separators=(',',':')).encode()
def digest(x):return hashlib.sha256(blob(x)).hexdigest()
def tr(A):return [sum(((row>>i)&1)<<j for j,row in enumerate(A)) for i in range(len(A))]
def mv(A,x):return sum(((a&x).bit_count()%2)<<i for i,a in enumerate(A))
def perm(src,off,m):
 p=[None]*m;used=set(range(off,off+len(src)))
 for j,i in enumerate(src):p[i]=off+j
 rest=iter(i for i in range(m) if i not in used)
 for i in range(m):
  if p[i] is None:p[i]=next(rest)
 return tr([1<<x for x in p])
def build(cp,phasepath,out):
 start=time.monotonic();cp=Path(cp);phasepath=Path(phasepath);out=Path(out);assert not out.exists();out.mkdir(parents=True)
 c=read(cp);phase=read(phasepath);spec=read(ROOT/'SELECTION.json');H={e['sink_helper']:e['frame'] for e in spec['hetero']};Z={e['sink_helper'] for e in spec['free']};assert not set(H)&Z
 E.V=c['v'];E.R=c['R'];E.N=2*E.V+E.R;v,h,R=c['v'],c['h'],c['R'];m=phase['m'];assert m==8*h+1 and phase['status']=='PASS_EXACT_Z4_DATA_ROUTE_IDLE_AND_TERMINAL_PHASES'
 word=W.insert(c,spec['hetero']+spec['free']);pw=E.prewhite(word,set(H)|Z);programs={};checks={};counts={};controls=[]
 def reject(name,fn):
  try:fn()
  except (AssertionError,ValueError,KeyError):controls.append(name)
  else:raise AssertionError('mutation accepted: '+name)
 original=E.replay_main(c,{i:{i:Q(1)} for i in range(E.N)});changed=E.replay_main(word,{i:{i:Q(1)} for i in range(E.N)})
 assert original[:2*v]==changed[:2*v] and c['A']==word['A'] and c['ret']==word['ret'] and c['scat']==word['scat']
 for ori in ['forward','backward']:
  ev=list(E.emit(word,ori,H,Z,pw));check=E.validate(ev,word,ori,H,Z);checks[ori]={k:z for k,z in check.items() if k!='edges'};programs[ori]=ev
  coeffs=set();primitives=0;macros=0
  for e in ev:
   if e[0]!='scalar':continue
   op=e[2];macros+=1
   if op[0]=='add':coeffs.add(op[3]);op=op[:3]+(op[3].numerator,op[3].denominator)
   primitives+=2*len(S.lower_scalar(op))
  for q in coeffs:S.check_lowered_coefficient(q.numerator,q.denominator)
  counts[ori]=dict(scalar_macros=macros,real_component_primitives=primitives,coefficients_checked=len(coeffs))
  j=next(i for i,e in enumerate(ev) if e[0]=='climb_pad72');bad=copy.deepcopy(ev);bad[j]=bad[j][:-1]+(bad[j][-1]-1,);reject(ori+':unpaid_padding',lambda:E.validate(bad,word,ori,H,Z))
  bad=copy.deepcopy(ev);j=next(i for i,e in enumerate(ev) if e[0]=='scalar' and e[1]=='old_response');e=bad[j];bad[j]=e[:2]+(e[2][:3]+(-e[2][3],),e[3]);reject(ori+':wrong_preconditioner',lambda:E.validate(bad,word,ori,H,Z))
  bad=copy.deepcopy(ev);j=next(i for i,e in enumerate(ev) if e[0]=='scalar' and e[1]=='cleanup');bad.insert(j,('scalar','cleanup',E.lift(min(Z),0,Q(1),ori),'old1'));reject(ori+':cleanup_after_fusion',lambda:E.validate(bad,word,ori,H,Z))
 assert checks['forward']['paid_hist']==checks['backward']['paid_hist'];print('PASS both local dirty orientations and coefficient expansion',flush=True)
 # Audit every used ordinary directed edge, copied-centre direction, and mixed child.
 edges=set();mixed={};ops={};recipes=[]
 def canonical(f):
  if f not in ops:ops[f]=C.canonical_frame(h,word['frames'][f])
  return ops[f]
 for ev in programs.values():
  for e in ev:
   if e[0]=='climb':edges.add((e[3],e[4]))
   elif e[0]=='center':edges.add((e[2],e[3]))
   elif e[0]=='climb_pad72':
    if e[2] not in mixed:mixed[e[2]]=F.mixed_recipe(word['frames'],e[2])
    assert mixed[e[2]]['paid_rank']==e[5]
 for i,(a,b) in enumerate(sorted(edges)):
  op=canonical(a).adjoint().then(canonical(b));rec,compiled=C.lower_child(op)
  assert rec['rank']==abs(len(word['frames'][a])-len(word['frames'][b])) and compiled.tab==op.tab and compiled.zero_state()==op.zero_state()
  recipes.append(dict(old=a,new=b,recipe=rec))
  if i%300==0:print('exact edges',i,len(edges),flush=True)
 endpoints={};basis={}
 for helper,fid in H.items():
  frame=word['frames'][fid];assert len(frame)==h-1
  q,=C.nullspace(frame,h);assert q.bit_count()%2==1 and q!=(1<<h)-1
  j=next(i for i in range(h) if not q>>i&1);w=q^(1<<j);cols=[]
  for b in range(h):
   swapped=j if b==0 else 0 if b==j else b;x=1<<swapped
   if (w&x).bit_count()%2:x^=w
   cols.append(x)
  U=tr(cols);P=C.perm(h,U);block=C.ident(h)
  for i in range(1,h):block=block.then(C.cgate(h,1<<i))
  routed=P.adjoint().then(block).then(P);relative=canonical(fid).adjoint().then(routed);rec,compiled=C.lower_child(relative)
  assert rec['rank']==0 and relative.tab==compiled.tab and relative.zero_state()==compiled.zero_state()
  endpoints[fid]=rec;basis[helper]=cols
  for g in word['A']+word['B']:
   if helper in E.gate_regs(g):assert E.nested(word['frames'],g[1],fid)
 for ori,ev in programs.items():
  for i,e in enumerate(ev):
   if e[:2]==('adapter','canonical_to_bank_residual'):ev[i]=('rankzero_endpoint_adapter',e[2],e[3],endpoints[e[3]])
 # Preserve and explicitly verify the data endpoint Gaussian representatives.
 data_endpoints=[];fourier=C.fourier(h)
 for p,q in enumerate(word['ports']):
  for role,old,fid in [('source',C.cgate(h,q),word['start'][p]),('target',C.cgate(h,q).adjoint().then(fourier),word['final'][v+p])]:
   op=old.adjoint().then(canonical(fid));rec,compiled=C.lower_child(op);assert rec['rank']==0 and op.tab==compiled.tab and op.zero_state()==compiled.zero_state();data_endpoints.append(dict(port=p,role=role,frame=fid,recipe=rec))
 print('PASS ordinary, mixed and endpoint Gaussian phases',flush=True)
 # Smallest replica multiple filling mixed banks and all remaining full banks.
 for T in range(1,10000):
  if T*len(H)%8==0 and (T*(R-len(H))-T*len(H)//8)%8==0:break
 full=[(rep,r) for rep in range(T) for r in range(2*v,E.N) if r not in H];small=[(rep,r) for rep in range(T) for r in sorted(H)];special=len(small)//8;bankcount=special+(len(full)-special)//8
 assignments={};routes=[];routeids={}
 def put(role,bank,off,rank):
  rep,helper=role;A=perm(list(range(h)) if rank==h else list(range(1,h)),off,m)
  if rank<h:
   U=basis[helper]+[1<<i for i in range(h,m)];A=[mv(tr(U),row) for row in A]
  inverse=tr(A);assert all(mv(A,mv(inverse,1<<i))==1<<i for i in range(m))
  fr=word['frames'][H[helper]] if helper in H else [1<<i for i in range(h)];mask=sum(1<<i for i in range(off,off+rank));images=[mv(A,x) for x in fr]
  assert all(not x&~mask for x in images) and C.rank(images)==rank
  key=tuple(A)
  if key not in routeids:routeids[key]=len(routes);routes.append(A)
  assignments[role]=dict(replica=rep,helper=helper,bank=bank,offset=off,rank=rank,route=routeids[key])
 for b in range(special):
  put(full[b],b,0,h)
  for j,role in enumerate(small[8*b:8*b+8]):put(role,b,h+(h-1)*j,h-1)
 for i,role in enumerate(full[special:]):b,j=divmod(i,8);put(role,special+b,h*j,h)
 assert len(assignments)==T*R
 occupancy={b:[] for b in range(bankcount)}
 for a in assignments.values():occupancy[a['bank']].extend(range(a['offset'],a['offset']+a['rank']))
 for b,axes in occupancy.items():assert len(axes)==len(set(axes)) and set(axes)==set(range(m-(b>=special)))
 fused=[assignments[rep,r] for rep in range(T) for r in sorted(Z)];assert len({a['bank'] for a in fused})==len(fused) and all(a['bank']>=special for a in fused)
 for a in fused:
  A=routes[a['route']];assert A[m-1]==1<<(m-1) and tr(A)[m-1]==1<<(m-1)
 recipepath=SOURCE/'vendor/cx/work/odd-stages/RECIPE-9.json';recipe=read(recipepath);stages=[e['stage'] for e in recipe if e['kind']=='local'];L=len(stages);assert stages==list(range(L));k=(L-1)//2;datafamilies=2*k*v*T;live=datafamilies+L*bankcount;physical=live+R+h+1
 calls=[];records=[];padding=[];paid=Counter();hashes={o:digest(e) for o,e in programs.items()}
 for e in recipe:
  if e['kind']!='local':continue
  stage,pair=e['stage'],e['pair'];ori='backward' if e['reverse'] else 'forward'
  for rep in range(T):
   owners=[[rep*2*k*v+(2*pair+r//v)*v+r%v,['data',stage,r%v]] for r in range(2*v)]
   for r in range(2*v,E.N):a=assignments[rep,r];owners.append([datafamilies+stage*bankcount+a['bank'],['helper',a['route']]])
   assert len(set((f,tuple(route)) for f,route in owners))==E.N and all(0<=f<live for f,route in owners)
   calls.append(dict(stage=stage,replica=rep,pair=pair,orientation=ori,owners=owners,local_program_sha256=hashes[ori]))
   paid.update(checks[ori]['paid_hist'])
   for r in sorted(Z):
    a=assignments[rep,r];event=next(x for x in programs[ori] if x[0]=='climb_pad72' and x[1]==r);records.append(dict(stage=stage,replica=rep,helper=r,family=owners[r][0],route=a['route'],axis=m-1,phase_recipe=event[2],paid_rank=event[5]))
  used={a['bank'] for a in fused};padding.extend(datafamilies+stage*bankcount+b for b in range(special,bankcount) if b not in used)
 idle=[]
 for p,z in enumerate(phase['recipes']):
  for j,x in enumerate(z['idle_children']):
   if x['rank']:paid[x['rank']]+=T;idle.append(dict(port=p,child=j,rank=x['rank'],replicas=T))
 paid[1]+=len(padding);mass=sum(a*b for a,b in paid.items());deficit=m*live-mass
 for o in programs:assert sum(checks[o]['paid_hist'].values())==sum(checks['forward']['paid_hist'].values())
 bridges=[e for e in recipe if e['kind']=='bridge'];bridgeadds=2*v*T*len(bridges);terminalshifts=k*v*T;terminalmoves=2*k*v*T;compiler=64*(m+1)**3;lc=sum(checks['forward']['paid_hist'].values());macros=max(x['scalar_macros'] for x in counts.values());adapters=16*(macros+lc+E.N+h)+64*m
 localbound=max(x['real_component_primitives'] for x in counts.values())+adapters*compiler;scalar_total=sum(counts[c['orientation']]['real_component_primitives'] for c in calls)
 nonlocalitems=4*v*T*L+2*v*T*L+2*L*T*R+len(idle)*T+L*(bankcount-special)+bridgeadds+terminalshifts+terminalmoves+live+physical+len(H)*L*T
 outside=8*nonlocalitems+64*m+64*len(records);pervertex=scalar_total+bridgeadds+terminalshifts+terminalmoves+live+(len(calls)*adapters+outside)*compiler+64*physical
 d=m//2;group=2**(d*d)*math.prod(2**(2*i)-1 for i in range(1,d+1));stock=group*physical;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2;s=group*mass;B=s+(1<<100000);literal=2*(1<<30000)*stock**2+8*s+4*stock+4+32*m;maxchild=max(paid);row=2*stock.bit_length()+9909+252
 assert localbound<1<<48 and logical<1<<6050 and router<1<<30000 and literal<1<<100000 and B<1<<100001 and 32*m*B*B<1<<210000 and 2*B+18<1<<210000 and m*m>2*maxchild**2 and row<20161
 invoice=dict(local_primitive_bound=localbound,scalar_counts=counts,pervertex=pervertex,extra_fusion_groups=64*len(records),physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),physical_row_coefficient=row,halving_degree=2,induction_gap_multiple_B=2*(m-maxchild)-1)
 template=dict(recipe=recipe,calls=calls,local_programs=programs,bank_placement_matrices=routes,bank_owner_right_factors=[tr(A) for A in routes],banks=list(assignments.values()),standalone_padding_families=padding,fused_padding=records,ordinary_phase_recipes=recipes,mixed_phase_recipes=mixed,endpoint_phase_recipes=endpoints,data_endpoint_phase_recipes=data_endpoints,idle_children=idle,data_phase_recipe=phase,live=live,physical=physical,private_namespace=dict(centres=[live,live+h],tableau=[live+h,live+h+R],coefficient=[physical-1,physical]),cover_correction=dict(families=[0,live],charged_calls=live,formula='delta_i=(weight(row_i(g))-1)/2 mod 2'),execution_schedule=dict(recipe_phases=recipe,local_sweeps='For each local recipe phase run all replicas and cover classes; preserve DATA-PHASES stage alignments, idle children and terminal X_q before signed exchange.',standalone_padding_families=padding,cover_correction_last=True),invoice=invoice)
 expectedpadding=set(padding);expectedrecords=copy.deepcopy(records);allpadding={datafamilies+s*bankcount+b for s in stages for b in range(special,bankcount)}
 def validate(t):
  assert t['bank_owner_right_factors']==[tr(A) for A in t['bank_placement_matrices']]
  assert t['fused_padding']==expectedrecords and len({a['family'] for a in t['fused_padding']})==len(records)
  rest=t['standalone_padding_families'];assert len(rest)==len(set(rest)) and set(rest)==expectedpadding
  assert not set(rest)&{a['family'] for a in t['fused_padding']} and set(rest)|{a['family'] for a in t['fused_padding']}==allpadding
  assert t['execution_schedule']['standalone_padding_families']==rest and t['execution_schedule']['cover_correction_last']
  assert t['cover_correction']['charged_calls']==live
  for call in t['calls']:
   assert call['local_program_sha256']==digest(t['local_programs'][call['orientation']])
   for r in range(2*v,E.N):
    a=assignments[call['replica'],r];assert call['owners'][r]==[datafamilies+call['stage']*bankcount+a['bank'],['helper',a['route']]]
  for o,ev in t['local_programs'].items():
   got=[e for e in ev if e[0]=='rankzero_endpoint_adapter'];assert len(got)==len(H)
   for e in got:assert e[3]==endpoints[e[2]]
 validate(template)
 for name in ['missing_fusion','duplicate_padding','wrong_inverse','wrong_owner','omitted_endpoint','stale_schedule','omit_cover']:
  bad=copy.deepcopy(template)
  if name=='missing_fusion':bad['fused_padding'].pop()
  elif name=='duplicate_padding':bad['standalone_padding_families'].append(records[0]['family'])
  elif name=='wrong_inverse':bad['bank_owner_right_factors'][0][0]^=1
  elif name=='wrong_owner':bad['calls'][0]['owners'][2*v][0]+=1
  elif name=='omitted_endpoint':bad['local_programs']['forward']=[e for e in bad['local_programs']['forward'] if e[0]!='rankzero_endpoint_adapter']
  elif name=='stale_schedule':bad['execution_schedule']['standalone_padding_families']=sorted(allpadding)
  else:bad['cover_correction']['charged_calls']-=1
  reject(name,lambda:validate(bad))
 print('PASS literal bank routes, full template, finite invoice',invoice,flush=True)
 sys.path.insert(0,str(BOOT));from coarse_precision import module as engine;from refine import refine
 M=engine('moment');D=engine('base_two_moment');root=M.certify(paid,m,live,True);lo,hi=Q(root['lower']),Q(root['upper']);fallback=32*m*m*sum(paid.values());a=M.moment(paid,m,live,lo,True);b=M.moment(paid,m,live,hi,True);assert a[1]<1<b[0]
 _,up=D.moment(m,live,list(paid.items()),lo);_,extra=D.moment(m,live,[(1,fallback)],lo);down,_=D.moment(m,live,list(paid.items()),hi);extralo,_=D.moment(m,live,[(1,fallback)],hi);assert up+Q(1,10**16)*extra<1<down+Q(1,10**16)*extralo
 witness=refine(lo,Q('255384852701747/250000000000000000'));kappa=Q(witness['kappa']);assert hi/(1+hi)<kappa+Q(1,10**18)
 result=dict(status='PASS_R781_HETEROFUSION_LOCAL_PHASES_BANKS_GLOBAL_INVOICE_PRICE',kappa=str(kappa),kappa_float=float(kappa),coarse_lower=str(lo),coarse_upper=str(hi),coarse18=str(Q(int(lo*10**18),10**18)),profile=dict(sorted(paid.items())),replicas=T,live=live,physical=physical,m=m,rank_mass=mass,deficit=deficit,banks_per_stage=bankcount,mixed_banks_per_stage=special,padding_calls=len(padding),fused_occurrences=len(records),ordinary_edges=len(edges),local_checks=checks,invoice=invoice,controls_rejected=controls,strict_constraints=47,seconds=time.monotonic()-start,source_hashes={str(p):sha(p) for p in [cp,phasepath,ROOT/'build.py',ROOT/'SELECTION.json',FUSION/'fusion.py',FUSION/'scalar_compiler.py',FUSION/'vendor394/word.py',FUSION/'vendor394/emit.py',recipepath]},scope='Finite conditional construction: inherited arbitrary-dirty invocation, compressed-window, compiler, cover, precision, restoration and analytic interfaces. Full supplier and fresh bit replay are required by verify.py.')
 for name,obj in [('RESULT.json',result),('WITNESS.json',witness)]: (out/name).write_text(json.dumps(obj,indent=2)+'\n')
 template['source_hashes']=result['source_hashes'];raw=blob(template);(out/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(raw,mtime=0));assert read(out/'GLOBAL-TEMPLATE.json.gz')==F.encode(template)
 (out/'WORD.json.gz').write_bytes(gzip.compress(blob(word),mtime=0));print(result['status'],result['kappa'],flush=True);return result
if __name__=='__main__':build(*sys.argv[1:])
