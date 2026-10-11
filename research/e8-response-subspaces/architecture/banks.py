from pathlib import Path
from collections import Counter,defaultdict,deque
import sys,json,gzip,hashlib,math,copy
sys.dont_write_bytecode=True
CP,PAT,PHASE,LOCAL,LOCALRESULT,PRIOR,GEO,OUT=[Path(a).resolve() for a in sys.argv[1:9]];assert not OUT.exists();OUT.mkdir(parents=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());ungzip=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()));write=lambda name,o:(OUT/name).write_text(json.dumps(o,indent=2))
sys.path.insert(0,str(GEO));from clifford_exact import transpose,mv
c=read(CP);patterns=read(PAT);phase=read(PHASE);local=ungzip(LOCAL);lr=read(LOCALRESULT);prior=ungzip(PRIOR);ext=dict(c['ext']);h,v,R=c['h'],c['v'],c['R'];n=2*v+R;m,T,L=73,8,9
DATA=Path(sys.argv[9]).resolve() if len(sys.argv)>9 else PRIOR.with_name('DATA-PHASES.json');assert sha(DATA)==prior['exact_data_phase_recipe_sha256']
assert sha(CP)==phase['candidate_sha256']==local['candidate_sha256']==lr['candidate_sha256'];assert lr['all_new_phase_equalities_include_Gaussian_global_phase'] and lr['gauged_K_columns_zero'];assert lr['raw_operator_equals_same_entrance_nonY_baseline']
assert hashlib.sha256(gzip.decompress(LOCAL.read_bytes())).hexdigest()==lr['local_programs_uncompressed_sha256'];assert prior['m']==m and len(prior['calls'])==72;phaseby={p['frame']:p for p in phase['frames']}
queues=defaultdict(deque)
for rep in range(T):
 for r in range(2*v,n):queues[h-len(c['frames'][ext[r]]) if r in ext else h].append((rep,r))
expected=Counter({r:len(q) for r,q in queues.items()});assign=[];bank=0;padding=[]
for pattern in patterns:
 for _ in range(pattern['count']):
  offset=0
  for key,num in sorted(((k,num) for k,num in pattern.items() if k.startswith('r')),key=lambda x:-int(x[0][1:])):
   rank=int(key[1:])
   for slot in range(num):
    assert queues[rank];rep,helper=queues[rank].popleft();axes=list(range(offset,offset+rank));offset+=rank;assert offset<=m
    cols=axes+[a for a in range(m) if a not in axes];A=transpose(tuple(1<<a for a in cols),m);Ai=transpose(A,m)
    assert all(mv(A,1<<i)==1<<axes[i] for i in range(rank));assign.append(dict(replica=rep,helper=helper,bank=bank,rank=rank,residual_axes=axes,map_local_to_bank_rows=A,owner_right_factor_rows=Ai))
  if offset<m:assert m-offset<=48;padding.append(dict(bank=bank,axes=list(range(offset,m)),rank=m-offset))
  bank+=1
assert all(not q for q in queues.values());lookup={(x['replica'],x['helper']):x for x in assign};assert len(lookup)==T*R
# Explicit unitary adapters surround the COMPLETE dirty invocation in BOTH orientations.
# Chronological inverse-adjoint keeps each unitary address operator U unchanged.
programs={};bills=local['bills'];localhist=Counter({int(k):num for k,num in local['local_profile'].items()})
for ori in ['forward','backward']:
 raw=local['local_programs'][ori];assert raw[0]==['phase','old_response'] and raw[-1]==['phase','done'];pre=[];post=[]
 for r,f in sorted(ext.items()):
  p=phaseby[f];assert p['basis']==c['frames'][f] and p['residual_rank']==h-len(c['frames'][f]);assert p['pre_adapter']['rank']==p['post_adapter']['rank']==0
  chart=local['entry_charts'][str(f)];assert chart['basis']==c['frames'][f] and chart['entry_adapter_rank']==0
  pre.append(['bank_adapter','right_inverse_before_old_response',r,f,p['pre_adapter']]);post.append(['bank_adapter','left_inverse_after_cleanup',r,f,p['post_adapter']])
 programs[ori]=[['phase','bank_pre_adapters']]+pre+raw[:-1]+[['phase','bank_post_adapters']]+post+[['phase','done']]
 hh=Counter()
 for ev in programs[ori]:
  if ev[0]=='climb':hh[ev[5]]+=1
  elif ev[0]=='center':hh[ev[4]]+=1
 assert hh==localhist
calls=[];H=Counter();primitives=0
for old in prior['calls']:
 call=copy.deepcopy(old);s,r=call['stage'],call['replica'];call['owners']=call['owners'][:2*v]+[[7680+s*bank+lookup[r,helper]['bank'],['explicit_inverse_route',r,helper]] for helper in range(2*v,n)];assert len({json.dumps(o) for o in call['owners']})==n;assert len({(lookup[r,helper]['bank'],tuple(lookup[r,helper]['owner_right_factor_rows'])) for helper in range(2*v,n)})==R
 call['local_program_sha256']=hashlib.sha256(json.dumps(programs[call['orientation']],sort_keys=True,separators=(',',':')).encode()).hexdigest();calls.append(call);H.update(localhist);primitives+=bills[call['orientation']]['totals']['real_component_primitive_steps']
for ch in prior['idle_children']:H[ch['rank']]+=ch['replicas']
for p in padding:H[p['rank']]+=L
live=7680+L*bank;physical=live+R+h+1;mass=sum(r*num for r,num in H.items());assert m*live-mass==2496 and max(H)<=48
compiler=64*(m+1)**3;macros=max(bills[o]['totals']['scalar_macros'] for o in bills);lc=sum(localhist.values());adapters=16*(macros+lc+n+h)+64*m+8*len(ext);localbound=max(bills[o]['totals']['real_component_primitive_steps'] for o in bills)+adapters*compiler
bridges=sum(e['kind']=='bridge' for e in prior['recipe']);pairs=len({e['pair'] for e in prior['recipe'] if e['kind']=='local'});bridge_adds=2*v*T*bridges;terminal_shifts=pairs*v*T;terminal_moves=7680
nonlocal_items=6*v*T*L+2*L*T*R+len(prior['idle_children'])*T+L*len(padding)+bridge_adds+terminal_shifts+terminal_moves+live+physical+4*len(calls)*len(ext)
outside=8*nonlocal_items+64*m;pervertex=primitives+bridge_adds+terminal_shifts+terminal_moves+live+(len(calls)*adapters+outside)*compiler+64*physical
rr=m//2;group=2**(rr*rr)*math.prod(2**(2*i)-1 for i in range(1,rr+1));stock=group*physical;smass=group*mass;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2;G,E,C0=1<<30000,1<<100000,1<<210000;bb=smass+E;literal=2*G*stock**2+8*smass+4*stock+4+32*m;row=2*stock.bit_length()+9909+252
assert localbound<1<<48 and logical<1<<6050 and router<G and literal<E and 32*m*bb*bb<C0 and m*m>2*max(H)**2 and row<20161
invoice=dict(local_bound=localbound,real_primitives_all_calls=primitives,adapter_groups=adapters,outside_groups=outside,explicit_bank_boundary_adapters=2*len(calls)*len(ext),pervertex=pervertex,live=live,physical=physical,group_bits=group.bit_length(),physical_stock_bits=stock.bit_length(),logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),row=row,retained_row=20161,compiler=compiler,G_exponent=30000,E_exponent=100000,C0_exponent=210000,halving_degree=2,induction_gap_multiple_B=2*(m-max(H))-1)
routeblob=json.dumps(assign,separators=(',',':')).encode();(OUT/'ROUTES.json.gz').write_bytes(gzip.compress(routeblob,mtime=0));schedule=[copy.deepcopy(e) for e in prior['execution_schedule'] if e['kind'] not in ('bank_padding_cover_sweep','translate_every_live_family')];pad=[dict(family=7680+s*bank+p['bank'],axes=p['axes'],rank=p['rank']) for s in range(L) for p in padding];correction=dict(kind='translate_every_live_family',families=[0,live],formula=prior['cover_final_correction']['formula']);schedule+=[dict(kind='heterogeneous_bank_padding_cover_sweep',padding=pad),correction]
ir=dict(version='arbitrary-entrance-two-sided-banks-v1',candidate_sha256=sha(CP),m=m,live=live,physical=physical,banks_per_stage=bank,local_programs=programs,entry_charts=local['entry_charts'],calls=calls,recipe=prior['recipe'],execution_schedule=schedule,idle_children=prior['idle_children'],bank_padding=pad,cover_final_correction=correction,route_table_sha256=hashlib.sha256(routeblob).hexdigest(),residual_phase_sha256=sha(PHASE),local_admission_sha256=sha(LOCALRESULT),private_namespace=dict(centers=[live,live+h],tableau=[live+h,live+h+R],coefficient=[physical-1,physical]),scope='Finite changed dirty-word/adapters/routing/template/invoice. Exact local scalar and Gaussian checks source-bound; inherited all-size window lift, arbitrary correlated bank semantics, recursive compiler, fixed tapes, common grid, restored rows and analytic interfaces remain conditional.')
ir['cover']=prior['cover'];ir['loop_order']=prior['loop_order'];ir['route_semantics']=dict(prior['route_semantics']);ir['route_semantics']['helper']='physical cover owner g=d*A^-1 using explicit owner_right_factor_rows; local-to-bank map A is an orthogonal coordinate permutation';ir['adapter_policy']='Retain source-bound exact data phase and endpoint adapters; explicit helper pre R0^-1 before entire old_response, post L^-1 after complete cleanup; count all rankzero compilations';ir['exact_data_phase_recipe_sha256']=sha(DATA)
blob=json.dumps(ir,sort_keys=True,separators=(',',':')).encode();(OUT/'TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0));result=dict(status='PASS_NEW_ARBITRARY_ENTRANCE_TWO_SIDED_BANK_TEMPLATE_FINITE_INVOICE',candidate_sha256=sha(CP),template_sha256=hashlib.sha256(blob).hexdigest(),route_table_sha256=hashlib.sha256(routeblob).hexdigest(),m=m,live=live,physical=physical,banks_per_stage=bank,residual_ranks=dict(expected),padding_per_stage=dict(Counter(p['rank'] for p in padding)),rank_mass=mass,deficit=m*live-mass,profile=dict(sorted(H.items())),local_profile=dict(sorted(localhist.items())),invoice=invoice,source_hashes={str(p):sha(p) for p in [CP,PAT,PHASE,LOCAL,LOCALRESULT,PRIOR,DATA,GEO/'clifford_exact.py',Path(__file__)]},scope=ir['scope']);write('ADMISSION.json',result)
assert all(sha(p)==digest for p,digest in result['source_hashes'].items());print('PASS FRESH PORTABLE BANK EMISSION + INVOICE',bank,live,physical,invoice)
