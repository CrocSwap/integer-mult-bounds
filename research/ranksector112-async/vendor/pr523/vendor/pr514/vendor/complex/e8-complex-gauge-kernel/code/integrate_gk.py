# GK: modified copy of PR #433's complex_integrate.py (icekylinx with Codex assistance; PR #425) by DreamingOfClouds with Claude Opus 5.5
# (Anthropic), via Claude Code.  Every change is marked "GK:".  On a word without start_extra / target_levels the behaviour
# and every written file equal PR #433's (regression anchor in verify.py).
import sys as _sys, os as _os; _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
# Adapted from PR425 for heterogeneous centres by icekylinx, with Codex assistance.
import copy,gzip,hashlib,importlib.util,json,math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
OUT=Path('split-centres');cp=OUT/'CANONICAL-WORD.json.gz'
c=json.load(gzip.open(cp));audit=json.loads((OUT/'SCALAR-FRAME-AUDIT.json').read_text())
phase=json.loads((OUT/'CLIFFORD-REVIEW.json').read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert phase['canonical_word_sha256']==audit['canonical_word_sha256']==sha(cp)
assert phase['all_child_equalities_include_global_phase']
programs=json.load(gzip.open(OUT/'LOCAL-PROGRAMS.json.gz'));checks=json.loads((OUT/'LOCAL-CHECKS.json').read_text())
frames=c['frames'];v,R,h=c['v'],c['R'],c['h'];n=2*v+R;private_centres=len(c['centers'])
for z in checks.values():z['paid_profile']={int(r):n for r,n in z['paid_profile'].items()}
old=Path('work/complex-nine-native');template=json.load(gzip.open(old/'GLOBAL-TEMPLATE.json.gz'))
data_phase=json.loads((old/'DATA-PHASES.json').read_text())
assert template['exact_data_phase_recipe_sha256']==sha(old/'DATA-PHASES.json')
assert data_phase['status']=='PASS_EXACT_Z4_DATA_ROUTE_IDLE_AND_TERMINAL_PHASES'
m,T,L,k=73,8,9,4
# GK: residual widths 9 - dim(start frame); banks tile per width class (all 9: PR #433's eight residuals + one pad)
from gk_common import tile,route
widths=[h-len(frames[c['start'][2*v+i]]) for i in range(R)]
assign,nb,pads=tile([(rep,i,widths[i]) for rep in range(T) for i in range(R)]);entering0=any(w_<h for w_ in widths)
W=2*v*k*T+L*nb;physical=W+R+private_centres+2
template['version']='hamming-mutable-basis-nine-v1';template['live']=W;template['physical']=physical
template['local_programs']=programs;paid=Counter();assignments=set();event_count=0;scalar_primitives=0
for call in template['calls']:
    stage,rep,pair=call['stage'],call['replica'],call['pair'];ori=call['orientation']
    owners=[[rep*2*k*v+(2*pair+r//v)*v+r%v,[1,stage,r%v]] for r in range(2*v)]
    for r in range(R):
        bank,off_,w_,pure_,sp_=assign[rep,r];owners.append([2*v*k*T+stage*nb+bank,route(off_,w_,pure_,sp_)])   # GK: [2,slot] in pure width-9 banks, [2,offset,width,spectators] for entering helpers
        assignments.add((stage,rep,r,bank,off_))
    assert len(owners)==n and len({(f,json.dumps(route)) for f,route in owners})==n
    assert all(f<W for f,route in owners)   # GK: every owner lies in the live stock (none in the private namespace)
    fam=Counter(f for f,route in owners)   # GK: an entering helper is the only owner of its bank family in the invocation (PR #458's rule, banks included); the data families are the 240 distinct active ones
    assert all(fam[f]==1 for f,route in owners[:2*v]) and all(fam[owners[2*v+r][0]]==1 for r in range(R) if widths[r]<h),('entering helper shares its bank family',stage,rep)
    call['owners']=owners;call['local_program_sha256']=checks[ori]['sha256']
    for r,z in checks[ori]['paid_profile'].items():paid[r]+=z
    event_count+=checks[ori]['events'];scalar_primitives+=checks[ori]['real_component_primitive_bound']
assert len(assignments)==L*T*R and len(template['calls'])==72
for item in template['idle_children']:paid[item['rank']]+=item['replicas']
for r_,z_ in pads.items():paid[r_]+=z_*L   # GK: bank pads (rank 1 each at width 9 and 8)
assert dict(paid)=={int(r):z for r,z in json.load(gzip.open(OUT/'FULL-WORD.json.gz'))['report']['global_profile'].items()}
mass=sum(r*z for r,z in paid.items());assert m*W-mass==2496
if entering0:template['route_semantics']['helper']+='; entering helpers: paid wrappers R_E^-1 before and L_E^-1 after the invocation; an entering helper is the only owner of its bank family in the invocation, route [2, offset, width, spectator cells] with the spectators the first cells of the bank beyond every residual cell'   # GK
template['bank_padding']['families']=list(range(7680,W))
template['cover_final_correction']['families']=[0,W]
template['cover_final_correction']['charged_calls_per_cover']=W
for e in template['execution_schedule']:
    if e['kind']=='bank_padding_cover_sweep':e['families']=[7680,W]
    elif e['kind']=='translate_every_live_family':e.update(template['cover_final_correction'])
template['private_namespace']={'centers':[W,W+private_centres],'reserved_tableau':[W+private_centres,W+private_centres+R],
                               'coefficient':[physical-2,physical]}
template['exact_local_clifford_recipe_sha256']=sha(OUT/'CLIFFORD-RECIPES.json')
if (OUT/'RESIDUAL-ADAPTERS.json').exists():template['residual_adapter_sha256']=sha(OUT/'RESIDUAL-ADAPTERS.json')   # GK: paid wrappers of entering helpers (Lemma A)
template['expanded_scalar_interface']='See PROOF.txt: mutable source basis, frame-zero output preconditioner, explicit dirty compensator, and full-frame inverse source/helper cleanup.'
blob=json.dumps(template,sort_keys=True,separators=(',',':')).encode()
(OUT/'GLOBAL-TEMPLATE.json.gz').write_bytes(gzip.compress(blob,mtime=0))

# Fresh finite overcharge, with the changed stock, scalar counts, coefficient
# lowering, and private work reserve. No unchanged local invoice is assumed.
compiler=64*(m+1)**3;macros=max(z['scalar_macros'] for z in checks.values());children=sum(checks['forward']['paid_profile'].values())
adapters=16*(macros+children+n+private_centres)+64*m
local_bound=max(z['real_component_primitive_bound'] for z in checks.values())+adapters*compiler
bridges=[e for e in template['recipe'] if e['kind']=='bridge'];bridge_adds=2*v*T*len(bridges)
terminal_shifts=k*v*T;terminal_moves=2*k*v*T
entering=sum(1 for w_ in widths if w_<h)   # GK: entrance adapters (Lemma A): a monomial on 9 bits is at most 81+45+9=135 elementary factors (matrix, quadratic form, translation); charge 144 at entry and at exit of every entering helper in every invocation
nonlocal_items=4*v*T*L+2*v*T*L+2*L*T*R+sum(e['replicas'] for e in template['idle_children'])+L*nb+bridge_adds+terminal_shifts+terminal_moves+W+physical+2*L*T*entering*144
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
Outer=load('outer');b=Q(audit['prospective_complex_b']);bit=Q(json.loads(Path('BIT-PRICE.json').read_text())['lower'])
eta=Q(1,10**12);beta=Q(1,10**9);grid=Q(1,10**18)
s=Q(int(((1-beta)*min(b,bit)-grid)*10**18),10**18);assert s<bit
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
