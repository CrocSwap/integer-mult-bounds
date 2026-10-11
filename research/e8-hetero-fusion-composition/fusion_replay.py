"""Source-bound PR394 free-sink/padding fusion on heterogeneous R781.
Usage: python -B fusion_replay.py PR390_TREE PR394_LEAVES ORDINARY_COMPLEX HETERO SIGNED BASELINE BIT_PARENT OUT

PR390_TREE may be a generated source view; only pinned source leaves are used.
PR394_LEAVES needs code/emit.py, data/sinks-e8clean.json, PROOF.md.
Full upstream/parent inventories belong to the caller. No network or search.
Prepared with OpenAI Codex assistance; Apache-2.0, inherited notices apply.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
from types import SimpleNamespace
import argparse,ast,copy,gzip,hashlib,importlib.util,io,json,math,sys
assert __debug__ and sys.version_info>=(3,12)
sys.dont_write_bytecode=True
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
unzip=lambda p:json.loads(gzip.decompress(Path(p).read_bytes()))
def write(p,x):Path(p).write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def gz(raw):
 from transport import deterministic_gzip
 return deterministic_gzip(raw)

def labeller(bindings):
 def label(p):
  for name,base in bindings:
   if p.is_relative_to(base):return name+'/'+p.relative_to(base).as_posix()
  raise AssertionError('unbound source '+str(p))
 return label

FUNCTION_PROVENANCE={'upstream_commit': 'be2a06b597b2ba76c7a226ab4cca4c6d04e918eb', 'functions': {'rehist': {'path': 'research/e8-clean-padding/code/cxkernel.py', 'source_sha256': '8fc2a43e70fa8c1ce3f3025c9568b562accc5cf25b2ed53d7c0a1cbf954a0599', 'function_sha256': '106bd52db2dea43428f03bdf35206b6c1cc00718659445a3e3ab8612c5000c12'}, 'insert': {'path': 'research/e8-clean-padding/code/word.py', 'source_sha256': '63c02f96767435dd44f721148a483960bc4a966ef23de0f42a9f1614232a0f2c', 'function_sha256': 'fe0390d1a307907594e418570c29411c47700629a11368bffefd1ad5eb19765a'}}}

def rehist(c):
    """recompute block histograms and N exactly as gx.check1 counts them (climbs per class, COPY ranks)"""
    v, R = c['v'], c['R']; n = 2 * v + R; dim = [len(f) for f in c['frames']]
    cls = lambda r: 'x' if r < v else 'y' if r < 2 * v else 's'
    cur = list(c['start']); H = {'x': Counter(), 'y': Counter(), 's': Counter(), 'c': Counter()}
    def climb(r, f):
        if cur[r] != f: H[cls(r)][dim[f] - dim[cur[r]]] += 1; cur[r] = f
    for ph in ('A', 'B'):
        if ph == 'B':
            for k, s_, f in c['ret']: H['c'][dim[f]] += 1
        for g in c[ph]:
            regs = [g[2]] + ([t for t, _, _ in g[3]] + list(g[4]) if g[0] == 'out' else [x for x, _, _ in g[3]] if g[0] == 'in' else [])
            for r in regs: climb(r, g[1])
    for r in range(n): climb(r, c['final'][r])
    c['blocks'] = {k: {str(r): x for r, x in sorted(w.items())} for k, w in H.items()}
    c['N'] = sum(r * x for w in H.values() for r, x in w.items())
    return c

def insert(c, sinks):
    """sinks: dicts with sink_helper, cut_group (insert after this original gate), frame, uncompute=[[donor, a, b]]
    meaning sink += (a/b)*donor.  Several gates at one cut keep list order."""
    c = copy.deepcopy(c); nA = len(c['A']); by = {}
    for s in sinks: by.setdefault(s['cut_group'], []).append(s)
    A, B = [], []
    for i, g in enumerate(c['A'] + c['B']):
        (A if i < nA else B).append(g)
        for s in by.get(i, []):
            (A if i < nA else B).append(['in', s['frame'], s.get('target', s['sink_helper']), [list(x) for x in s['uncompute']]])
    c['A'], c['B'] = A, B
    return rehist(c)

def reconstruct(PR390,SOURCE,BASE,CX,HERE):
 assert not HERE.exists();HERE.mkdir();(HERE/'code').mkdir()
 label=labeller([('hetero',BASE),('pr394',SOURCE),('source390',PR390),('candidate',HERE)])
 gxroot=CX/'work/native358/vendor/complex-reserve/upstream/pr352/code/complex/inputs/complex/sources'
 assert sha(gxroot/'tools__gx__gx.py')=='6f3dc8bb639933227a8dae181ec4a542e85c7276be9c9e330f49518e7b630b95'
 assert sha(gxroot/'tools__gx__gxcore.py')=='eb972c06fe8c322db2d9a8d9a7d05596e8f40c4ca8e5f42eb6df3c7361b5d517'
 gx=load('fusion_reference_gx',gxroot/'tools__gx__gx.py');gxcore=load('fusion_reference_gxcore',gxroot/'tools__gx__gxcore.py')
 word=SimpleNamespace(insert=insert)
 raw=(SOURCE/'code/emit.py').read_bytes();text=raw.decode();assert text.count('V,R=120,783; N=2*V+R')==1
 adapted=text.replace('V,R=120,783; N=2*V+R','V,R=120,781; N=2*V+R').encode();(HERE/'code/emit.py').write_bytes(adapted)
 spec=importlib.util.spec_from_file_location('adapted_emit',HERE/'code/emit.py');E=importlib.util.module_from_spec(spec);spec.loader.exec_module(E)
 assert sha(BASE/'candidate.json')=='468460de3bb2ebf6c89b3156fdd332623596f7f6ae74324362862324cf71a98c'
 c=read(BASE/'candidate.json');old=json.loads(gzip.decompress((PR390/'data/prefix18.json.gz').read_bytes()))
 assert hashlib.sha256(gzip.decompress((PR390/'data/prefix18.json.gz').read_bytes())).hexdigest()=='ba159f566568627d8459960500b9c285e9c9d69368f1b60fa27ae83f0a84c39a'
 selected=read(SOURCE/'data/sinks-e8clean.json');mapped=[];provenance=[]
 def role(r):
  if r==706:return 268
  if r==708:return 323
  return r-int(r>706)-int(r>708)
 def gate(g):
  out=copy.deepcopy(g);out[2]=role(g[2]);out[3]=[[role(r),a,b]for r,a,b in g[3]]
  if len(out)>4:out[4]=[role(r)for r in out[4]]
  return out
 groups=c['A']+c['B'];oldgroups=old['A']+old['B']
 for entry in selected:
  sourcecut=entry['cut_group'];reference=gate(oldgroups[sourcecut]);hits=[i for i,g in enumerate(groups)if g==reference]
  assert len(hits)==1,(sourcecut,hits)
  item=copy.deepcopy(entry);item['cut_group']=hits[0];item['sink_helper']=role(item['sink_helper'])
  if 'target'in item:item['target']=role(item['target'])
  item['uncompute']=[[role(r),a,b]for r,a,b in item['uncompute']]
  mapped.append(item);provenance.append(dict(source_cut=sourcecut,new_cut=hits[0],matched_group=reference))
 hetero=read(BASE/'sink-audit.json')['accepted'];endpoints={a['sink_helper']:a['frame']for a in hetero};fused={a['sink_helper']for a in mapped}
 assert fused=={301,324,387}
 wbase=word.insert(c,hetero);wnew=word.insert(c,hetero+mapped)
 def hist(w):
  H=Counter()
  for block in w['blocks'].values():H.update({int(k):v for k,v in block.items()})
  return H
 assert hist(wbase)==hist(wnew)
 for name,w in [('base',wbase),('new',wnew)]:
  gx.check1(copy.deepcopy(w),scalar=True,stats={})
  assert gxcore.mirror(gxcore.normal(copy.deepcopy(w)))['hist']==dict(hist(w))
  print('PASS gx/gxcore',name,flush=True)
 pre=E.prewhite(wnew,set(endpoints)|fused);pbase=E.prewhite(wbase,set(endpoints))
 oldpre=read(BASE/'prewhite.json')
 for got,key in zip(pbase,['pre_target_dirty_cancellation_gates','pre_helper_inverse_gates','post_full_helper_clean_repair_gates']):
  assert got==[(t,s,Q(a,b))for t,s,a,b in oldpre[key]],key
 checks={};programs={}
 for orientation in ['forward','backward']:
  program=list(E.emit(wnew,orientation,endpoints,fused,pre));check=E.validate(program,wnew,orientation,endpoints,fused)
  checks[orientation]=check;programs[orientation]=program;print('PASS exact1021 dirty columns + final-use fusion',orientation,flush=True)
 assert checks['forward']['paid_hist']==checks['backward']['paid_hist']
 bank=read(BASE/'full/HETEROBANKS.json');assignment={(x['replica'],x['helper']):x for x in bank['assignments']};routes=[[int(x,2)for x in rows]for rows in bank['route_recipes']]
 fused_banks=[]
 for rep in range(32):
  for h in fused:
   a=assignment[rep,h];assert a['rank']==9 and a['bank']>=8
   route=routes[a['orthogonal_route_id']]
   image=sum(((r>>72)&1)<<i for i,r in enumerate(route));assert image==1<<72
   fused_banks.append(a['bank'])
 assert len(fused_banks)==len(set(fused_banks))==96
 H=Counter({int(k):v for k,v in read(BASE/'full/hetero/RESULT.json')['profile'].items()})
 delta={1:-864,2:-864,3:864};H.update(delta);assert all(n>=0 for n in H.values())
 Hactual=Counter({r:288*n for r,n in checks['forward']['paid_hist'].items()})
 for r in [16,8,32,8,48,8,48,32,16]:Hactual[r]+=7680
 Hactual[1]+=9*(3115-96)
 assert H==Hactual and 73*58827-sum(r*n for r,n in H.items())==9984
 moment=load('fusion_screen_moment',CX/'work/pr361/code/engines/moment.py');base_two_moment=load('fusion_screen_second',CX/'work/pr361/code/engines/base_two_moment.py')
 result=moment.certify(H,73,58827,True);b=Q(int(Q(result['lower'])*10**18),10**18);fb=32*73**2*sum(H.values())
 bounds=[]
 for q in [b,b+Q(1,10**18)]:
  p=moment.moment(H,73,58827,q,True);lo,hi=base_two_moment.moment(73,58827,list(H.items()),q);fl,fh=base_two_moment.moment(73,58827,[(1,fb)],q)
  bounds.append(dict(saving=str(q),moment=list(map(str,p)),independent=list(map(str,[lo+Q(1,10**16)*fl,hi+Q(1,10**16)*fh]))))
 assert Q(bounds[0]['moment'][1])<1<Q(bounds[1]['moment'][0])and Q(bounds[0]['independent'][1])<1<Q(bounds[1]['independent'][0])
 raw=json.dumps(wnew,sort_keys=True,indent=2).encode()+b'\n';(HERE/'candidate.json').write_bytes(raw);(HERE/'candidate.json.gz').write_bytes(gz(raw))
 write(HERE/'selection.json',mapped)
 def encode(x):
  if isinstance(x,Q):return [x.numerator,x.denominator]
  if isinstance(x,(tuple,list)):return [encode(a)for a in x]
  if isinstance(x,dict):return {str(k):encode(v)for k,v in x.items()}
  return x
 write(HERE/'programs.json',encode(programs));write(HERE/'prewhite.json',encode(pre))
 write(HERE/'SCREEN.json',dict(status='PASS_SOURCE_BOUND_SCALAR_AND_LABEL_FUSION_SCREEN_ONLY',source_pr394='be2a06b597b2ba76c7a226ab4cca4c6d04e918eb',
  source_sha256={label(p):sha(p)for p in [SOURCE/'code/emit.py',SOURCE/'data/sinks-e8clean.json',BASE/'candidate.json',BASE/'prewhite.json',BASE/'full/HETEROBANKS.json']},
  derived_emitter_sha256=sha(HERE/'code/emit.py'),candidate_sha256=sha(HERE/'candidate.json'),selection=mapped,cut_provenance=provenance,
  exact_live_columns=1021,both_orientations=checks,new_scalar_gates=9,prewhite_counts=list(map(len,pre)),fused_banks=sorted(fused_banks),
  profile_delta=delta,profile=H,live=58827,m=73,deficit=9984,complex_b=str(b),bounds=bounds,
  scope='Exploratory scalar/lifetime/bank-slot and two-engine arithmetic screen only. Missing fresh tensor-padding Clifford recipe/global owner-template and finite invoice admission. No final kappa claim.'))
 print('SCREEN b',b,float(b),flush=True)

def admit(PR390,PR394,ORDINARY,BASE,SIGNED,BASELINE,BIT_PARENT,HERE,OUT):
 assert not OUT.exists();OUT.mkdir()
 CX=PR390/'public/381/source/research/e8-nine-stage-kappa/complex377'
 ORD=ORDINARY/'work/complex-nine-native'
 label=labeller([('candidate',HERE),('hetero',BASE),('ordinary',ORDINARY),('pr394',PR394),('source390',PR390)])
 bound=[HERE/'candidate.json',HERE/'SCREEN.json',HERE/'selection.json',HERE/'code/emit.py',BASE/'COMPOSITION-RECEIPT.json',BASE/'full/hetero/HETEROGENEOUS-TEMPLATE.json.gz',BASE/'full/hetero/GLOBAL-HETEROGENEOUS-TEMPLATE.json.gz',BASE/'full/hetero/BANK-ENDPOINT-PHASE.json',BASE/'full/HETEROBANKS.json',BASE/'full/BANK-REVIEW.json',CX/'work/odd-stages/clifford_exact.py',PR390/'code/complex-hetero-compose.py',PR394/'PROOF.md']
 pins={label(p):sha(p)for p in bound}
 c=read(HERE/'candidate.json');assert sha(HERE/'candidate.json')=='199b967e9cd8c1ea6b661eb355552bc3d6d255d998d1c2d51f238b42edd71cc3'
 screen=read(HERE/'SCREEN.json');oldc=read(BASE/'candidate.json');assert c['frames']==oldc['frames']
 E=load('fusion_emitter',HERE/'code/emit.py');hetero={355:206,403:221};fused={301,324,387}
 pre=E.prewhite(c,set(hetero)|fused);assert list(map(len,pre))==[1660,1557,7768]
 source=(PR390/'code/complex-hetero-compose.py').read_text();tree=ast.parse(source)
 selected=['lower_scalar','primitive_bound','check_lowered_coefficient'];fragments=[]
 for node in tree.body:
  if isinstance(node,ast.FunctionDef)and node.name in selected:fragments.append(ast.get_source_segment(source,node))
 assert len(fragments)==3;scope={'Q':Q};exec('\n\n'.join(fragments),scope)
 lower,checkcoeff=scope['lower_scalar'],scope['check_lowered_coefficient'];local={};checks={};paid={};primitives={};macros={};fused_events={}
 def update(reg,t,s,q):
  dest=reg.setdefault(t,{})
  for k,v in list(reg.get(s,{}).items()):
   z=dest.get(k,Q(0))+q*v
   if z:dest[k]=z
   else:dest.pop(k,None)
 for ori in ['forward','backward']:
  events=list(E.emit(c,ori,hetero,fused,pre));checks[ori]=E.validate(events,c,ori,hetero,fused)
  reg={('L',i):{i:Q(1)}for i in range(1021)};nprimitive=0;converted=[];nmacro=0
  for e in events:
   if e[0]!='scalar':converted.append(e);continue
   p,op,f=e[1:]
   if op[0]=='add':op=op[:3]+(op[3].numerator,op[3].denominator);checkcoeff(op[3],op[4])
   converted.append(('scalar',p,op,f));nmacro+=1
   for item in lower(op):
    tag,t=item[:2];nprimitive+=1
    if tag=='clear':reg[t]={}
    elif tag=='copy':reg[t]=dict(reg[item[2]])
    elif tag=='accumulate':update(reg,t,item[2],Q(item[3]))
    else:
     q={'double':Q(2),'halve':Q(1,2),'divide3':Q(1,3)}[tag];reg[t]={k:q*v for k,v in reg[t].items()}
  expected={('L',i):{i:Q(1)}for i in range(1021)}
  for i in range(120):expected['L',120+i if ori=='forward'else i][i if ori=='forward'else 120+i]=Q(1 if ori=='forward'else-1)
  assert all(reg[r]==v for r,v in expected.items())and all(not v for r,v in reg.items()if r[0]!='L')
  local[ori]=converted;paid[ori]=Counter(checks[ori]['paid_hist']);primitives[ori]=2*nprimitive;macros[ori]=nmacro
  fused_events[ori]=[e for e in events if e[0]=='climb_pad72']
  assert {(e[1],e[2],e[3],e[4],e[5])for e in fused_events[ori]}=={(301,731,1,2,3),(324,744,1,2,3),(387,759,1,2,3)}
  print('PASS fully lowered scalar stream',ori,nmacro,2*nprimitive,flush=True)
 assert paid['forward']==paid['backward']
 mutation_checks=[]
 for ori in ['forward','backward']:
  original=list(E.emit(c,ori,hetero,fused,pre))
  for name in ['cleanup_on_fused_sink','padded_climb_before_last_use','drop_uncompute_add','flip_precancellation','padding_not_paid']:
   events=list(original)
   if name=='cleanup_on_fused_sink':
    i=next(i for i,e in enumerate(events)if e[0]=='scalar'and e[1]=='cleanup');e=events[i];op=e[2]
    events[i]=(e[0],e[1],(op[0],('L',301)if ori=='forward'else op[1],op[2]if ori=='forward'else('L',301),op[3]),e[3])
   elif name=='padded_climb_before_last_use':
    i=next(i for i,e in enumerate(events)if e[0]=='climb_pad72');e=events.pop(i)
    k=max(k for k,x in enumerate(events)if x[0]=='scalar'and x[1]=='main'and('L',e[1])in x[2][1:3]);events.insert(k,e)
   elif name=='drop_uncompute_add':
    i=next(i for i,e in enumerate(events)if e[0]=='scalar'and e[1]=='main'and e[2][0]=='add'and e[2][1 if ori=='forward'else 2]==('L',301)and e[2][2 if ori=='forward'else 1]==('L',276));events.pop(i)
   elif name=='flip_precancellation':
    i=next(i for i,e in enumerate(events)if e[0]=='scalar'and e[1]=='old_response');e=events[i];op=e[2];events[i]=(e[0],e[1],op[:3]+(-op[3],),e[3])
   else:
    i=next(i for i,e in enumerate(events)if e[0]=='climb_pad72');e=events[i];events[i]=e[:5]+(e[4],)
   try:E.validate(events,c,ori,hetero,fused)
   except(AssertionError,KeyError)as error:mutation_checks.append(dict(orientation=ori,name=name,rejected=str(error)))
   else:raise AssertionError('control accepted '+ori+' '+name)
 sys.path.insert(0,str(CX/'work/odd-stages'));import clifford_exact as C
 def lift(op):
  result=C.ident(10)
  for e in op.circuit:
   tag=e[0]
   if tag=='P':part=C.perm(10,tuple(e[1])+(1<<9,))
   elif tag=='D':part=C.diag(10,tuple(e[1])+(0,),tuple(e[2])+(0,))
   elif tag=='C':part=C.cgate(10,e[1],e[2])
   elif tag=='X':part=C.xgate(10,e[1])
   elif tag=='phase':part=C.Op(10,C.identity(10),[e])
   else:raise AssertionError(e)
   result=result.then(part)
  return result
 fused_recipes=[]
 for r,f in [(301,731),(324,744),(387,759)]:
  edge=C.canonical_frame(9,c['frames'][f]).adjoint().then(C.canonical_frame(9,c['frames'][1]))
  original,compiled=C.lower_child(edge);assert original['rank']==2
  tensor=lift(edge).then(C.cgate(10,1<<9));recipe,fcompiled=C.lower_child(tensor)
  assert recipe['rank']==3 and tensor.tab==fcompiled.tab and tensor.zero_state()==fcompiled.zero_state()
  same=lift(compiled).then(C.cgate(10,1<<9));assert same.tab==tensor.tab and same.zero_state()==tensor.zero_state()
  # The actual new->old FULL adapter is a scalar identity on the local factor,
  # and all remaining local adapters act on the first nine axes only.
  commute=lift(C.canonical_frame(9,c['frames'][1])).then(C.cgate(10,1<<9))
  reverse=C.cgate(10,1<<9).then(lift(C.canonical_frame(9,c['frames'][1])))
  assert commute.tab==reverse.tab and commute.zero_state()==reverse.zero_state()
  assert tensor.tab!=lift(edge).tab,'omitted padding must change actual operator'
  occupancy=[]
  for occ in [0,1]:
   oldabs=lift(C.canonical_frame(9,c['frames'][f]));newabs=lift(C.canonical_frame(9,c['frames'][1]))
   if occ:oldabs=oldabs.then(C.cgate(10,1<<9));newabs=newabs.then(C.cgate(10,1<<9))
   newabs=newabs.then(C.cgate(10,1<<9));relative=oldabs.adjoint().then(newabs)
   assert relative.tab==tensor.tab and relative.zero_state()==tensor.zero_state()
   occupancy.append(dict(old_exterior_C72_exponent=occ,new_exterior_C72_exponent=occ+1,exact_relative_tensor_child=True))
  squared=C.cgate(10,1<<9).then(C.cgate(10,1<<9));translation=C.xgate(10,1<<9)
  assert squared.tab==translation.tab and squared.zero_state()==translation.zero_state()
  assert squared.tab!=C.cgate(10,1<<9).tab,'stage8 endpoint must not use set union'
  fused_recipes.append(dict(helper=r,old=f,new=1,local_rank=2,paid_rank=3,padding_axis_local=9,padding_axis_global=72,base_recipe=original,fused_recipe=recipe,exact_tableau_and_gaussian_phase=True,
   exterior_occupancy_cases=occupancy,C72_squared_is_X72=True,endpoint_flag='retain one additional C72 factor through the local rankzero new_to_old adapter; never reduce frame bookkeeping by subspace union'))
  print('PASS exact tensor-padding child',r,flush=True)
 write(OUT/'FUSION-PHASES.json',dict(status='PASS_THREE_EXACT_RANK_THREE_TENSOR_PADDING_CHILDREN',recipes=fused_recipes,
  scope='Literal nine local axes plus one exterior axis; identified with global axis72 through checked owner routes. Mixed-window compiler admission remains explicit.'))
 oldlocal=unzip(BASE/'full/hetero/HETEROGENEOUS-TEMPLATE.json.gz');ordinary=read(ORD/'CLIFFORD-RECIPES.json')
 phases={(a['old'],a['new']):a for a in ordinary['children']+oldlocal['new_phase_recipes']};used=set()
 for ori,events in local.items():
  for e in events:
   if e[0]=='climb':old,new,rank=e[3:6]
   elif e[0]=='center':old,new,rank=e[2:5]
   elif e[0]=='climb_pad72':old,new,rank=e[2:5]
   else:continue
   assert (old,new)in phases and phases[old,new]['rank']==rank;used.add((old,new))
 endpoints=read(BASE/'full/hetero/BANK-ENDPOINT-PHASE.json')
 for ep in endpoints['endpoints']:
  rows=ep['orthogonal_rows'];routed=C.perm(9,rows).adjoint().then(C.fourier(9,range(1,9))).then(C.perm(9,rows))
  rel=C.canonical_frame(9,c['frames'][ep['frame']]).adjoint().then(routed);got,compiled=C.lower_child(rel)
  assert json.loads(json.dumps(got))==ep['canonical_to_orthogonal_coordinate_adapter']and got['rank']==0
 global0=unzip(BASE/'full/hetero/GLOBAL-HETEROGENEOUS-TEMPLATE.json.gz');bank=read(BASE/'full/HETEROBANKS.json')
 assert global0['banks']==bank['assignments'];assignment={(a['replica'],a['helper']):a for a in bank['assignments']}
 routes=[[int(x,2)for x in A]for A in bank['route_recipes']]
 def transpose(A):return [sum(((row>>i)&1)<<j for j,row in enumerate(A))for i in range(73)]
 assert global0['bank_placement_matrices']==routes and global0['bank_owner_right_factors']==[transpose(A)for A in routes]
 removed=set();fusions=[];hist=Counter()
 for call in global0['calls']:
  s,rep,p=call['stage'],call['replica'],call['pair'];assert len(call['owners'])==1021;hist.update(paid[call['orientation']])
  for h in range(240,1021):
   a=assignment[rep,h];assert call['owners'][h]==[30720+s*3123+a['bank'],['helper',a['orthogonal_route_id']]]
   assert 0<=call['owners'][h][0]<58827
  for h in sorted(fused):
   a=assignment[rep,h];assert a['rank']==9 and a['bank']>=8
   A=routes[a['orthogonal_route_id']];image=sum(((row>>72)&1)<<i for i,row in enumerate(A));assert image==1<<72
   key=(s,a['bank']);assert key not in removed;removed.add(key)
   fusions.append(dict(stage=s,replica=rep,helper=h,bank=a['bank'],bank_family=30720+s*3123+a['bank'],route=a['orthogonal_route_id'],axis=72,paid_rank=3,endpoint_extra_C72_flag=1))
 assert len(removed)==len(fusions)==864
 padding=[p for p in global0['bank_padding']if(p['stage'],p['bank'])not in removed];assert len(padding)==27171
 assert {(p['stage'],p['bank'])for p in padding}.isdisjoint(removed)
 assert {(p['stage'],p['bank'])for p in global0['bank_padding']}=={(p['stage'],p['bank'])for p in padding}|removed
 for idle in unzip(ORD/'GLOBAL-TEMPLATE.json.gz')['idle_children']:hist[idle['rank']]+=32
 hist[1]+=len(padding);assert hist==Counter({int(k):v for k,v in screen['profile'].items()})
 assert sum(hist.values())==1235907 and sum(k*v for k,v in hist.items())==4284387
 assert 73*58827-sum(k*v for k,v in hist.items())==9984
 template=copy.deepcopy(global0);template['local']['local_programs']=local;template['local']['fused_child_recipes']=fused_recipes
 template['bank_padding']=padding;template['fused_padding']=fusions
 template['terminal_data_rule']='Unchanged exact nine-stage signed data/exchange and cover correction. Padding for864 unique(stage,bank) owners is moved into certified rank3 final children; remaining27171 rank1 padding children precede cover correction.'
 for ori,events in template['local']['local_programs'].items():
  converted=[]
  for e in events:
   if e[:2]==('adapter','canonical_to_bank_residual'):
    ep=next(a for a in endpoints['endpoints']if a['frame']==e[3]);e=('rankzero_endpoint_adapter',e[2],e[3],ep['canonical_to_orthogonal_coordinate_adapter'])
   elif e[:2]==('adapter','new_to_old')and e[2]in fused:
    e=('flagged_new_to_old',e[2],e[3],72,1)
   converted.append(e)
   if e[0]=='climb_pad72':converted.append(('endpoint_padding_flag',e[1],72,1))
  assert len([e for e in converted if e[0]=='endpoint_padding_flag'])==3
  assert {e[1]for e in converted if e[0]=='flagged_new_to_old'}==fused
  template['local']['local_programs'][ori]=converted
 template['local'].pop('local_scalar_programs',None);template['local'].pop('lowered_scalar_programs',None)
 template['scope']='Source-template composition with exact finite scalar, phase and owner evidence. PR394 mixed local/exterior compiler and complete arbitrary-correlated-bank chronological substitution remain conditional; not a separately emitted global scalar IR.'
 raw=json.dumps(template,sort_keys=True,separators=(',',':')).encode();(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gz(raw))
 compiler=64*74**3;lc=sum(paid['forward'].values());adapters=16*(max(macros.values())+lc+1021+9)+64*73
 local_bound=max(primitives.values())+adapters*compiler;live,physical=58827,59618
 bridge_adds=18*120*32;terminal_shifts=4*120*32;terminal_moves=8*120*32;cover=live
 nonlocal_items=4*120*32*9+2*120*32*9+2*9*32*781+2160*32+9*3123+bridge_adds+terminal_shifts+terminal_moves+cover+physical+2*9*32
 # Charge eight extra global compiler groups for each tensor-padding fusion,
 # even though it replaces the existing rank2 child rather than adding a child.
 outside=8*(nonlocal_items+864)+64*73
 pervertex=160*primitives['forward']+128*primitives['backward']+bridge_adds+terminal_shifts+terminal_moves+cover+(288*adapters+outside)*compiler+64*physical
 group=2**1296*math.prod(2**(2*i)-1 for i in range(1,37));stock=group*physical;s=group*4284387;logical=group*pervertex+64
 router=compiler*(logical+1)*(stock+1)**2;Ebudget=1<<100000;B=s+Ebudget;literal=2*(1<<30000)*stock**2+8*s+4*stock+4+32*73
 assert local_bound<1<<48 and logical<1<<6050 and router<1<<30000 and literal<Ebudget and 32*73*B*B<1<<210000
 assert 73**2>2*48**2 and 2*stock.bit_length()+9909+252==15449<20161
 invoice=dict(local_primitive_bound=local_bound,pervertex=pervertex,physical_stock_bits=stock.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),required_C0_bits=(32*73*B*B).bit_length(),physical_row_coefficient=15449,halving_degree=2,induction_gap_multiple_B=49,
  fusion_extra_compiler_groups=8*864,macros=macros,real_component_primitives=primitives)
 eng=CX/'work/pr361/code/engines';M=load('fusion_moment',eng/'moment.py');BM=load('fusion_other',eng/'base_two_moment.py')
 b=Q(screen['complex_b']);assert b==Q(501407775311651,5*10**17);fb=32*73**2*sum(hist.values());bounds=[]
 for q in [b,b+Q(1,10**18)]:
  a=M.moment(hist,73,live,q,True);lo,hi=BM.moment(73,live,list(hist.items()),q);fl,fh=BM.moment(73,live,[(1,fb)],q)
  bounds.append(dict(saving=str(q),original=list(map(str,a)),independent=list(map(str,[lo+Q(1,10**16)*fl,hi+Q(1,10**16)*fh]))))
 assert Q(bounds[0]['original'][1])<1<Q(bounds[1]['original'][0])and Q(bounds[0]['independent'][1])<1<Q(bounds[1]['independent'][0])
 supplier=dict(status='PASS_FRESH_NINE_STAGE_COMPLEX_INTERFACE',b=str(b),m=73,W=live,histogram=hist,bounds=bounds,template_sha256=hashlib.sha256(raw).hexdigest(),finite_invoice=invoice,semantic_C1=1,
  scope=template['scope'],source_hashes=pins)
 write(OUT/'COMPLEX-SUPPLIER.json',supplier)
 assembly=load('fusion_assembly',BASELINE/'assembly.py').run(BIT_PARENT,read(SIGNED/'composition/baseline/replay/unsplit-bit/kappa-input.json'),read(SIGNED/'validation/FINITE.json'),supplier)
 write(OUT/'ASSEMBLY.json',assembly)
 assert pins=={label(p):sha(p)for p in bound}
 receipt=dict(status='PASS_FINITE_CONDITIONAL_PR394_PADDING_FUSION_ON_R781_HETEROGENEOUS_COMPLEX',source_pr394='be2a06b597b2ba76c7a226ab4cca4c6d04e918eb',source_hashes=pins,
  candidate_sha256=sha(HERE/'candidate.json'),kappa=assembly['kappa'],complex_b=str(b),binding=assembly['binding'],local_scalar_macros=macros,local_real_component_primitives=primitives,exact_live_columns=1021,
  complete_existing_phase_edges=len(used),fresh_tensor_rank3_children=3,fusions=864,unfused_padding=27171,profile=hist,rank_mass=4284387,live=live,physical=physical,finite_invoice=invoice,mutation_controls=mutation_checks,
  output_sha256={name:sha(OUT/name)for name in ['GLOBAL-TEMPLATE.json.gz','FUSION-PHASES.json','COMPLEX-SUPPLIER.json','ASSEMBLY.json']},scope=template['scope']+' Independent review and a portable complete default still required before publication.')
 write(OUT/'RECEIPT.json',receipt);print(receipt['status'],receipt['kappa'],flush=True)

def main():
 p=argparse.ArgumentParser(description=__doc__)
 for name in ['source390','source394','ordinary','hetero','signed','baseline','bit_parent','output']:p.add_argument(name,type=Path)
 a=p.parse_args();PR390,PR394,ORDINARY,BASE,SIGNED,BASELINE,BIT_PARENT,OUT=[getattr(a,name).resolve()for name in ['source390','source394','ordinary','hetero','signed','baseline','bit_parent','output']]
 assert not OUT.exists()
 for x in [PR390,PR394,ORDINARY,BASE,SIGNED,BASELINE,BIT_PARENT]:assert x.is_dir()and not OUT.is_relative_to(x)
 for x in [OUT,PR390,PR394,ORDINARY,BASE,SIGNED,BASELINE,BIT_PARENT,Path(sys.executable).resolve()]:assert not any(c.isspace()for c in str(x))
 pin_sources={
  PR394/'code/emit.py':'574c91ed87c32282209dd9986afb6c50284666ad64659cf94f97b4f93b1bab00',
  PR394/'data/sinks-e8clean.json':'c4398318f38abc0f180ab07d9a54e8683c7b4749100e5c31d97e9dbf9dcf4df1',
  PR394/'PROOF.md':'cf334ab21d6d5b21eeda8ad1531afb271a39c3213845473027d044a4307f8d1e',
  PR390/'code/complex-hetero-compose.py':'f8320faafc3e08b829d85a583cc34bec6e0578368ae4411200724a79a6899b30',
  BASELINE/'assembly.py':'fe545811e9e858c9ca616d64f3348b797319a51f1dfa8097588ab117bf78e82c'}
 assert all(sha(path)==want for path,want in pin_sources.items())
 assert read(BASE/'COMPOSITION-RECEIPT.json')['status']=='PASS_BOUND_HETEROGENEOUS_COMPLEX_AND_VERIFIED_SIGNED_SEVEN_STAGE_BIT_RESEARCH_COMPOSITION'
 assert read(ORDINARY/'VERIFICATION.json')['status']=='PASS_SOURCE_BOUND_PR390_PREFIX_TWO_ALIAS_TWO_FRAMES_ORDINARY_NINE_STAGE'
 assert read(SIGNED/'RECEIPT.json')['status']=='PASS_FULL_FRESH_COMPOSITION_AND_SIGNED_BIT_SUPPLEMENT'
 OUT.mkdir(parents=True);CX=PR390/'public/381/source/research/e8-nine-stage-kappa/complex377'
 reconstruct(PR390,PR394,BASE,CX,OUT/'candidate')
 assert sha(OUT/'candidate/candidate.json')=='199b967e9cd8c1ea6b661eb355552bc3d6d255d998d1c2d51f238b42edd71cc3'
 admit(PR390,PR394,ORDINARY,BASE,SIGNED,BASELINE,BIT_PARENT,OUT/'candidate',OUT/'admission')
 assert all(sha(path)==want for path,want in pin_sources.items())
 result=read(OUT/'admission/RECEIPT.json')
 assert result['kappa']=='50090545902704112039161/50000000000000000000000000'
 result.update(portable_replay_sha256=sha(Path(__file__)),function_provenance=FUNCTION_PROVENANCE,full_clean_extension_replay=True,
  parent_bindings={name:sha(path)for name,path in [('heterogeneous',BASE/'COMPOSITION-RECEIPT.json'),('ordinary',ORDINARY/'VERIFICATION.json'),('signed',SIGNED/'RECEIPT.json')]},
  admission_receipt_sha256=sha(OUT/'admission/RECEIPT.json'))
 write(OUT/'RECEIPT.json',result)
if __name__=='__main__':main()
