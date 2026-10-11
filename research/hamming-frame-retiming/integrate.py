"""Emit both local programs, integrate the fixed nine-stage geometry, and bill.

The expanded scalar interface is justified in PROOF.txt. This script does not
claim a Lean proof or discharge the inherited all-size/analytic interfaces.
"""
import copy,gzip,hashlib,importlib.util,json,math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

OUT=Path('work/complex-network/hamming');cp=OUT/'CANONICAL-WORD.json.gz'
c=json.load(gzip.open(cp));audit=json.loads((OUT/'SCALAR-FRAME-AUDIT.json').read_text())
phase=json.loads((OUT/'CLIFFORD-REVIEW.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert phase['canonical_word_sha256']==audit['canonical_word_sha256']==sha(cp)
assert phase['all_child_equalities_include_global_phase']
frames=c['frames'];v,R,h=c['v'],c['R'],c['h'];n=2*v+R
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def basis(vs):
    b={}
    for x in vs:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def dual(e):
    e=list(e)
    if e[0]=='add':e[1],e[2]=e[2],e[1];e[3]*=-1
    else:e[2],e[3]=e[3],e[2]
    return e
def scalar(e,back):
    e=dual(e) if back else list(e)
    if e[0]=='add':return ['add',['L',e[1]],['L',e[2]],e[3],e[4]]
    return ['scale',['L',e[1]],e[2],e[3]]
def primitive_bound(e):
    if e[0] in ('clear','copy'):return 1
    q=Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])
    a,b=abs(q.numerator),q.denominator
    assert b&(b-1)==0
    if e[0]=='scale':
        assert a&(a-1)==0
        return abs(a.bit_length()-b.bit_length())+int(q<0)
    # Exact binary Horner multiplication on a cleared private stream, repeated
    # halving, signed accumulation into the target, then clear the private stream.
    return 3+(a.bit_length()-1)+a.bit_count()+(b.bit_length()-1)

def emit(back):
    out=[];cur=c['start'].copy()
    def event(e):out.append(e)
    def scal(e,f):event(['scalar',e,f])
    event(['phase','zero_frame_precondition'])
    for e in c['precondition']+c['compensation']:
        regs=[e[1]]+([e[2]] if e[0]=='add' else [])
        assert all(c['start'][r]==0 for r in regs)
        scal(scalar(e,back),0)
    event(['phase','entry_adapters'])
    for r,f in enumerate(c['start']):event(['adapter','old_to_new',r,f])
    def climb(r,f,part):
        old=cur[r]
        if old==f:return
        assert basis(frames[old]+frames[f])==tuple(frames[f])
        rank=len(frames[f])-len(frames[old]);assert rank>0
        event(['climb',part,r,old,f,rank]);cur[r]=f
    for part in ('A','centers','B','final'):
        event(['phase',part])
        if part in ('A','B'):
            for e in c[part]:
                regs=[e[1]]+([e[2]] if e[0]=='add' else [])
                for r in regs:climb(r,e[-1],part)
                scal(scalar(e,back),e[-1])
        elif part=='centers':
            assert all(cur[r]==0 for r in range(v,2*v))
            for k,r in enumerate(c['centers']):
                assert cur[r]==1
                C=['C',k];scal(['clear',C],0 if back else 1)
                terms=[e for e in c['cut'] if e[2]==r]
                if back:
                    for e in terms:scal(['add',C,['L',e[1]],e[3],e[4]],0)
                else:scal(['copy',C,['L',r]],1)
                event(['center',k,0 if back else 1,1 if back else 0,h])
                if back:scal(['add',['L',r],C,-1,1],1)
                else:
                    for e in terms:scal(['add',['L',e[1]],C,e[3],e[4]],0)
                scal(['clear',C],1 if back else 0)
        else:
            for r,f in enumerate(c['final']):climb(r,f,part)
    event(['phase','exit_adapters'])
    for r,f in enumerate(c['final']):event(['adapter','new_to_old',r,f])
    event(['phase','full_frame_cleanup'])
    for e in c['cleanup']:
        regs=[e[1]]+([e[2]] if e[0]=='add' else [])
        assert all(c['final'][r]==1 for r in regs)
        scal(scalar(e,back),1)
    event(['phase','done'])
    return out

def check_local(events,back):
    # Literal scalar replay of the emitted stream, including center lifetimes.
    state={('L',r):{r:Q(1)} for r in range(n)};live=[];paid=Counter();prims=0;macros=0
    for e in events:
        if e[0]=='climb':assert not live;paid[e[5]]+=1
        elif e[0]=='center':assert live==[e[1]];paid[e[4]]+=1
        elif e[0]=='scalar':
            op=e[1];tag=op[0];t=tuple(op[1]);macros+=1;prims+=2*primitive_bound(op)
            if tag=='clear':
                state[t]={}
                if t[0]=='C' and t[1] in live:live.remove(t[1])
            elif tag=='copy':state[t]=dict(state.get(tuple(op[2]),{}));live.append(t[1])
            elif tag=='scale':state[t]={j:Q(op[2],op[3])*x for j,x in state[t].items()}
            else:
                s=tuple(op[2]);q=Q(op[3],op[4]);row=state.setdefault(t,{})
                if t[0]=='C' and t[1] not in live:live.append(t[1])
                for j,x in list(state.get(s,{}).items()):
                    z=row.get(j,Q(0))+q*x
                    if z:row[j]=z
                    else:row.pop(j,None)
    assert not live and all(not row for r,row in state.items() if r[0]=='C')
    for r in range(n):
        expected={r:Q(1)}
        if back and r<v:expected[v+r]=Q(-1)
        elif not back and v<=r<2*v:expected[r-v]=Q(1)
        assert state['L',r]==expected,('emitted column mismatch',back,r)
    assert dict(paid)=={int(r):z for r,z in c['local_profile'].items()}
    return {'sha256':digest(events),'events':len(events),'scalar_macros':macros,
            'real_component_primitive_bound':prims,'paid_profile':dict(sorted(paid.items())),
            'all_columns':n,'private_centers_cleared':True,'private_coefficient_stream_cleared_after_each_macro':True}

programs={};checks={}
for name,back in [('forward',False),('backward',True)]:
    programs[name]=emit(back);checks[name]=check_local(programs[name],back)
    print('PASS emitted',name,checks[name]['events'],'events',flush=True)

old=Path('work/complex-nine-native');template=json.load(gzip.open(old/'GLOBAL-TEMPLATE.json.gz'))
data_phase=json.loads((old/'DATA-PHASES.json').read_text())
assert template['exact_data_phase_recipe_sha256']==sha(old/'DATA-PHASES.json')
assert data_phase['status']=='PASS_EXACT_Z4_DATA_ROUTE_IDLE_AND_TERMINAL_PHASES'
m,T,L,k=73,8,9,4;W=2*v*k*T+L*R;physical=W+R+h+2
template['version']='hamming-mutable-basis-nine-v1';template['live']=W;template['physical']=physical
template['local_programs']=programs;paid=Counter();assignments=set();event_count=0;scalar_primitives=0
for call in template['calls']:
    stage,rep,pair=call['stage'],call['replica'],call['pair'];ori=call['orientation']
    owners=[[rep*2*k*v+(2*pair+r//v)*v+r%v,[1,stage,r%v]] for r in range(2*v)]
    for r in range(R):
        z=rep*R+r;bank,slot=divmod(z,T);owners.append([2*v*k*T+stage*R+bank,[2,slot]])
        assignments.add((stage,rep,r,bank,slot))
    assert len(owners)==n and len({(f,tuple(route)) for f,route in owners})==n
    assert all(f<W for f,route in owners)
    call['owners']=owners;call['local_program_sha256']=checks[ori]['sha256']
    for r,z in checks[ori]['paid_profile'].items():paid[r]+=z
    event_count+=checks[ori]['events'];scalar_primitives+=checks[ori]['real_component_primitive_bound']
assert len(assignments)==L*T*R and len(template['calls'])==72
for item in template['idle_children']:paid[item['rank']]+=item['replicas']
paid[1]+=L*R
assert dict(paid)=={int(r):z for r,z in json.load(gzip.open(OUT/'FULL-WORD.json.gz'))['report']['global_profile'].items()}
mass=sum(r*z for r,z in paid.items());assert m*W-mass==2496
template['bank_padding']['families']=list(range(7680,W))
template['cover_final_correction']['families']=[0,W]
template['cover_final_correction']['charged_calls_per_cover']=W
for e in template['execution_schedule']:
    if e['kind']=='bank_padding_cover_sweep':e['families']=[7680,W]
    elif e['kind']=='translate_every_live_family':e.update(template['cover_final_correction'])
template['private_namespace']={'centers':[W,W+h],'reserved_tableau':[W+h,W+h+R],
                               'coefficient':[physical-2,physical]}
template['exact_local_clifford_recipe_sha256']=sha(OUT/'CLIFFORD-RECIPES.json')
template['expanded_scalar_interface']='See PROOF.txt: mutable source basis, frame-zero output preconditioner, explicit dirty compensator, and full-frame inverse source/helper cleanup.'
blob=json.dumps(template,sort_keys=True,separators=(',',':')).encode()
(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))

# Fresh finite overcharge, with the changed stock, scalar counts, coefficient
# lowering, and private work reserve. No unchanged local invoice is assumed.
compiler=64*(m+1)**3;macros=max(z['scalar_macros'] for z in checks.values());children=sum(checks['forward']['paid_profile'].values())
adapters=16*(macros+children+n+h)+64*m
local_bound=max(z['real_component_primitive_bound'] for z in checks.values())+adapters*compiler
bridges=[e for e in template['recipe'] if e['kind']=='bridge'];bridge_adds=2*v*T*len(bridges)
terminal_shifts=k*v*T;terminal_moves=2*k*v*T
nonlocal_items=4*v*T*L+2*v*T*L+2*L*T*R+sum(e['replicas'] for e in template['idle_children'])+L*R+bridge_adds+terminal_shifts+terminal_moves+W+physical
outside=8*nonlocal_items+64*m
pervertex=scalar_primitives+bridge_adds+terminal_shifts+terminal_moves+W+(72*adapters+outside)*compiler+64*physical
r=m//2;group=2**(r*r)*math.prod(2**(2*i)-1 for i in range(1,r+1));stock=group*physical
smass=group*mass;logical=group*pervertex+64;router=compiler*(logical+1)*(stock+1)**2
GG,EE,C0=1<<30000,1<<100000,1<<210000;BB=smass+EE
literal=2*GG*stock**2+8*smass+4*stock+4+32*m
maxchild=max(paid);depth=2;assert m**depth>2*maxchild**depth
assert local_bound<1<<48 and logical<1<<6050 and router<GG and literal<EE and BB<1<<100001
assert 32*m*BB*BB<C0 and 2*BB+18<C0
row=depth*stock.bit_length()+9909+252;assert row<20161

def load(name):
    sp=importlib.util.spec_from_file_location('hamming_integrate_'+name,Path('work/pr361/code/engines')/(name+'.py'))
    mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);return mod
Outer=load('outer');b=Q(audit['prospective_complex_b']);bit=Q(1057833103534317,10**18)
eta=Q(1,10**12);beta=Q(1,10**9);grid=Q(1,10**18)
s=Q(int(((1-beta)*min(b,bit)-grid)*10**18),10**18);assert s<bit and s<(1-beta)*b
chain=[Q(384599,10**10)];cutoffs=[]
for _ in range(3):
    a=chain[-1];z=(1-s)*s+s*a;gap=min(s-z,1-z-s,1-z-s*(1-a),1-s)
    assert a<z<s<1-z and gap>0
    bound=max(math.ceil(36/gap**2),math.ceil(2*(4+512)/gap))
    assert bound*gap**2>=36 and bound*gap>=2*(4+512)
    cutoffs.append(str(bound));chain.append(z)
bridge={'semantic':{'C0':{'base':2,'exponent':210000},'strict_literal_gap':1},
        'rows':{'degree_gap':Q(10**6)-Q(51*20161,25)}}
q=chain[-1]*(1-2*eta);ticks=(1-eta)*q/(1+q)/grid;kap=Q((ticks.numerator-1)//ticks.denominator,10**18)
assembly=Outer.assembly(chain[-1],b,bridge,kap,eta=eta,beta=beta)
try:Outer.assembly(chain[-1],b,bridge,kap+grid,eta=eta,beta=beta)
except AssertionError:pass
else:raise AssertionError('next kappa grid accepted')
result={'status':'PASS_NEW_STRUCTURAL_PROGRAM_AND_FINITE_ASSEMBLY_PENDING_REPLAY',
        'canonical_word_sha256':sha(cp),'scalar_audit_sha256':sha(OUT/'SCALAR-FRAME-AUDIT.json'),
        'exact_phase_receipt_sha256':sha(OUT/'CLIFFORD-REVIEW.json'),'global_template_sha256':hashlib.sha256(blob).hexdigest(),
        'local_program_checks':checks,'R':R,'m':m,'live':W,'physical':physical,
        'bank_assignments':len(assignments),'rank_mass':mass,'deficit':2496,
        'global_profile':dict(sorted(paid.items())),'emitted_local_events_all_calls':event_count,
        'finite_invoice':{'local_primitive_bound':local_bound,'local_adapters':adapters,
                          'pervertex':pervertex,'physical_stock_bits':stock.bit_length(),
                          'router_bits':router.bit_length(),'literal_bits':literal.bit_length(),
                          'physical_row_coefficient':row,'retained_row_coefficient':20161,
                          'compiler':compiler,'G_exponent':30000,'E_exponent':100000,'C0_exponent':210000,
                          'required_C0_bits':(32*m*BB*BB).bit_length(),'halving_degree':depth,
                          'halving_integer_inequality':[m**depth,2*maxchild**depth]},
        'complex_b':str(b),'bit_c':str(bit),'prospective_kappa':str(kap),'kappa_float':float(kap),
        'log2_kappa':math.log2(float(kap)),
        'kappa_gain_percent':float(100*(kap/Q(998390813251625,10**18)-1)),
        'strict_outer_constraints':{name:str(z) for name,z in assembly['strict_constraints'].items()},
        'next_kappa_grid_rejected':True,'bootstrap_cutoffs_log2':cutoffs,
        'scope':'New finite scalar interface with a written conjugation proof, conditional on inherited all-size compiler, precision/tape and analytic transfer. Independent emitted-program replay and fresh package replay still required before final promotion.'}
(OUT/'INTEGRATION.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS prospective kappa',float(kap),'gain',result['kappa_gain_percent'],'percent',flush=True)
