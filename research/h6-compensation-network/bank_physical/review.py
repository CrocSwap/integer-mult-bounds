#!/usr/bin/env python3
"""Independent integral-bank, bounded physical-child and amplification audit."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib, importlib.util, json, sys
import numpy as np
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'research/niemeier-lattices/code'))
import e8_cubed as geo, e8_sections as sections
spec=importlib.util.spec_from_file_location('clifford17',ROOT/'research/split-centres-global/vendor/clifford_exact.py')
ce=importlib.util.module_from_spec(spec);sys.modules[spec.name]=ce;spec.loader.exec_module(ce)
H=17;R=480337920;R3=3363840;N=30960;CENTERS=816;DELTA=15872
parity=np.array([i.bit_count()&1 for i in range(1<<H)],dtype=np.int64)
xs=np.arange(1<<H,dtype=np.int64);pcache={};dcache={}
def need(c,m):
 if not c:raise ValueError(m)
def vec(op,basis=0):
 re=np.zeros(1<<H,np.int64);im=re.copy();re[basis]=1;den=0
 for e in op.circuit:
  if e[0]=='P':
   G=tuple(e[1]);idx=pcache.get(G)
   if idx is None:
    idx=sum(parity[xs&r]<<i for i,r in enumerate(G));pcache[G]=idx
   nr=np.empty_like(re);ni=np.empty_like(im);nr[idx]=re;ni[idx]=im;re,im=nr,ni
  elif e[0]=='X':re,im=re[xs^e[1]],im[xs^e[1]]
  elif e[0] in ('D','phase'):
   if e[0]=='phase':q=np.full(1<<H,e[1]%4,np.int64)
   else:
    key=(tuple(e[1]),tuple(e[2]));q=dcache.get(key)
    if q is None:
     q=sum(int(a)*((xs>>i)&1) for i,a in enumerate(e[2]))
     for i in range(H):
      for j in range(i+1,H):
       if e[1][i]>>j&1:q+=2*((xs>>i)&1)*((xs>>j)&1)
     q%=4;dcache[key]=q
   re,im=np.choose(q,[re,-im,-re,im]),np.choose(q,[im,re,-im,-re])
  elif e[0]=='C':
   j=xs^e[1];s=e[2]
   re,im=re-s*im+re[j]+s*im[j],im+s*re+im[j]-s*re[j];den+=1
   while den and not np.any((re|im)&1):re//=2;im//=2;den-=1
  else:raise ValueError(e)
  need(max(int(abs(re).max()),int(abs(im).max()))<2**60,'exact integer vector guard')
 return re,im,den
# Accelerate the inherited exact compiler's global-phase checks, preserving its semantics.
def zs(self,basis=0):
 a,b,d=vec(self,basis);return list(zip(a.tolist(),b.tolist())),d
ce.Op.zero_state=zs
roots,_,P,profiles=geo.construct_shell();P=P[(profiles&4)==0,:16].astype(np.int64)
_,packed,_=geo.binary_labels(roots,P)
E,w,den=sections.evaluate_operator_centers(P);need(den==8192,'factor denominator')
absE=np.abs(E.astype(np.int64));weighted=absE*np.abs(w)[None,:]
gcol=absE.sum(0);grow=absE.sum(1);scol=weighted.sum(0);srow=weighted.sum(1)
need(int(np.count_nonzero(E))==6440208,'full factor incidence census')
# Per-phase triangle bounds use distinct arbitrary initial rows with unit l1.
a=F(5*DELTA,16);forward={
 'comp_prefix':1+a,'K_prefix':1+a+F(int(srow.max()),den),
 'comp_gather':F(2),'K_centers_gather':F(1+int(gcol.max())),
 'K_private_scatter':1+a+F(int((weighted@(1+gcol)).max()),den),
 'comp_scatter':1+3*a+F(int((weighted@(1+gcol)).max()),den),
 'comp_cleanup':F(3)}
dual_source=1+DELTA+a
dual_K=dual_source+F(int((absE@(den+scol)).max()),den)
dual={'comp_prefix_helper':F(21,16),'K_prefix_center':1+F(int(scol.max()),den),
 'comp_gather_source':dual_source,'K_gather_source':dual_K,
 'K_private':F(int(scol.max()),den),'K_center_before_cancellation':1+F(2*int(scol.max()),den),
 'K_undo_source':dual_K+F(int(grow.max())),
 'comp_scatter_helper':F(13,8),'comp_cleanup_source':dual_K+F(int(grow.max()))+DELTA}
B=max(list(forward.values())+list(dual.values()))
# Cleared Horner temporary <=16 times current source, since max |numerator| is16.
B_horner=16*B
# Component max norm of a rank-r C child is <=(sqrt2)^r; each logical register
# has current representative rank<=17. The initial source inverse has rank1.
# Their combined infinity norm is<=2^((17+1)/2)=512; other entrances are0.
# Monomial adapters preserve component absolute values.
physical=512*B_horner
# Prefix row bounds control range, not arbitrary injected-error propagation.
# Use a fresh crude Lipschitz budget below; no predecessor precision constant.
kres=json.loads((HERE.parent/'k_encoder/RESULT.json').read_text())
primitive_comp=24*R+6*R3
def weighted_cost(q):
 q=F(q);a=abs(q.numerator);b=q.denominator
 need(a>0 and b&(b-1)==0,'nonzero dyadic primitive')
 return 3+a.bit_length()-1+a.bit_count()+b.bit_length()-1
gather_cost=scatter_cost=0
for c in range(816):
 vals,counts=np.unique(E[:,c],return_counts=True)
 for value,count in zip(vals,counts):
  if value:
   gather_cost+=int(count)*weighted_cost(F(int(value)))
   scatter_cost+=int(count)*weighted_cost(F(int(value*w[c]),8192))
need(2*(gather_cost+scatter_cost)+3*816==kres['K_forward_primitive_bound'],'fresh full K forward primitive count')
need(2*(gather_cost+scatter_cost)+6*816==kres['K_dual_primitive_bound'],'fresh full K dual primitive count')
real_primitive=2*(primitive_comp+max(kres['K_forward_primitive_bound'],kres['K_dual_primitive_bound']))
transitions=3*R+2*N+2*CENTERS
rank_mass=17*R+32*N+34*CENTERS
# Generic child lowering has two explicit monomial adapters. Each can use
# <=154 unit phases and one affine movement per coordinate. Use172 combined
# semantic actions conservatively; a complex unit phase
# can be realized with<=2 real component sign/movement operations.
adapter_real_bound=2*transitions*172*(1<<H)*2
whole_real_bound=real_primitive*(1<<H)+adapter_real_bound
# Integral slot assignment: role i of replica j owns bank i, pure slot j.
banks=[]
for L in (3,5,7):
 m=16*L+1;q,pad=divmod(m,H);T=q
 group=[]
 for name,count,path in [('compensation',R,[1,15,1]),('K_centers',816,[17])]:
  need(T*count%q==0,'integral distinct role banks')
  group.append(dict(name=name,roles_per_invocation=count,path=path,replicas=T,
    physical_banks_per_stage=count,slots_per_bank=q,pad_rank=pad,
    ordinary_rank_mass_per_stage=T*count*17,pad_rank_mass_per_stage=count*pad,
    complete_rank_mass_per_stage=count*m,
    owner_formula='bank=(stage,group,role); pure_slot=replica in [0,q)',
    exterior='separate pad C_pad on exterior axes; no spectator hosting'))
 stock=T*(L-1)*N+L*(R+816)
 mass=(16*L+1)*stock-T*((L-1)*N-L*816*17)
 banks.append(dict(L=L,m=m,replication=T,q=q,pad=pad,groups=group,
  replicated_stock=stock,replicated_complete_rank_mass=mass,
  phase_safety='All q replica invocations use disjoint pure slots. Groups and stage banks are disjoint; private streams have fresh cleared lifetimes. Pad executes on exterior after local episode.'))
# Actual nested helper edges, including both coefficient classes.
witness=[];selected=[]
for t in range(50):
 ts=(P@P[t])//4
 for v in (1,3):
  found=np.flatnonzero(ts==v)
  if len(found) and not any(x[2]==v for x in selected):selected.append((int(found[0]),t,v))
 if len(selected)==2:break
Fop=ce.fourier(H)
for s,t,pair in selected:
 ps,pt=int(packed[s]),int(packed[t]);need((ps&pt).bit_count()%2==0,'actual binary nesting')
 source=ce.cgate(H,ps);target=ce.cgate(H,pt,-1).then(Fop)
 ops=[ce.ident(H),source,target,Fop];steps=[];compiled=ce.ident(H)
 for i in range(3):
  transition=ops[i].adjoint().then(ops[i+1])
  recipe,lowered=ce.lower_child(transition)
  need(recipe['rank']==[1,15,1][i],'actual child rank')
  need(lowered.tab==transition.tab,'full signed Pauli tableau identity')
  # global phase checked on complete 2^17 basis-zero state by inherited compiler.
  compiled=compiled.then(lowered)
  steps.append(dict(rank=recipe['rank'],left=recipe['left'],right=recipe['right'],
                    literal_clifford_factors=len(lowered.circuit)))
 need(compiled.tab==Fop.tab,'ordinary helper residual signed tableau')
 av=vec(compiled);bv=vec(Fop)
 need(av[2]==bv[2] and np.array_equal(av[0],bv[0]) and np.array_equal(av[1],bv[1]),'ordinary C17 global phase')
 witness.append(dict(source_port=s,target_port=t,pairing=pair,source_address=ps,target_address=pt,
  child_ranks=[1,15,1],recipes=steps,signed_tableau_generators_checked=34,
  complete_basis_zero_state_coordinates_checked=1<<17,
  ordinary_residual='EXACT_C17_INCLUDING_GLOBAL_PHASE'))
# Integrate the proven local universal recipe family without materializing tape.
universal_path=HERE.parent/'physical_compiler/UNIVERSAL-RESULT.json'
universal=json.loads(universal_path.read_text())
need(universal['status']=='PASS_UNIVERSAL_H6_AFFINE_TRANSITION_FAMILY','universal local recipe family')
need(universal['adapter_bound']['affine_moves_per_positive_rank_transition']==2,'universal2move bound')
need(universal['adapter_bound']['unit_phase_factors']==0,'no universal phase factors')
horner_path=HERE.parent/'COEFFICIENTS.json'
horner=json.loads(horner_path.read_text())
need(horner['status']=='PASS_ALL_DYADIC_COEFFICIENT_STREAMS','all coefficient Horner streams')
bucket_path=HERE.parent/'routes/BUCKETED-SCHEMA.json'
bucket=json.loads(bucket_path.read_text());bucket_count=bucket['helper_count']
need(bucket_count==227312640,'full bucket role count')
# Weighted edge adds are retained; only two unit adds become once per lane.
bucket_comp=2*(8*(R-R3)+11*R3)+8*bucket_count
need(bucket_comp==9524090880,'fresh bucket scalar primitive count')
sharp=[]
for name,count,comp in [('edge',R,primitive_comp),('bucket',bucket_count,bucket_comp)]:
 tr=3*count+2*N+2*CENTERS
 raw=comp+max(kres['K_forward_primitive_bound'],kres['K_dual_primitive_bound'])
 coordinate_arithmetic=raw*(1<<H)
 moves=2*tr*(1<<H)
 local_rank=17*count+32*N+34*CENTERS
 all_real=2*(coordinate_arithmetic+moves)
 sharp.append(dict(word=name,ordinary_compensation_roles=count,local_transition_count=tr,
  local_child_rank_mass=local_rank,affine_movement_passes_per_transition_at_most=2,
  scalar_unit_phase_factors=0,complex_coordinate_arithmetic=coordinate_arithmetic,
  complex_coordinate_movements=moves,combined_semantic_complex_coordinate_actions=coordinate_arithmetic+moves,
  combined_real_component_actions=all_real,scalar_primitives_before_coordinate_expansion_and_real_doubling=raw,
  conservative_scalar_error_propagation=f'{all_real}*2^({all_real}+{local_rank}-b)',
  norm_coverage='Logical range bound here is audited for edge word. This movement/arithmetic/error ledger also covers bucket word; no bucket prefix range bound is inferred.',
  scope='Local universal recipe-family arithmetic plus movement ledger; max2 affine passes, no unit-phase factors. Semantic per-coordinate actions, not machine/tape instructions. Pad/controller/stage repetitions and approximate-child errors remain outside.'))
paths=['notes/general-clifford-frames.tex','research/split-centres-global/vendor/clifford_exact.py',
 'research/h6-compensation-network/k_encoder/network.py','research/h6-compensation-network/construction/network.py',
 'research/h6-compensation-network/contract/THEOREM.md','research/niemeier-lattices/code/e8_sections.py',
 'research/h6-independent-audit/walsh/results.json',
 'research/h6-compensation-network/physical_compiler/universal.py',
 'research/h6-compensation-network/physical_compiler/UNIVERSAL-THEOREM.md',
 'research/h6-compensation-network/physical_compiler/UNIVERSAL-RESULT.json',
 'research/h6-compensation-network/physical_compiler/UNIVERSAL-RECIPES.json',
 'research/h6-compensation-network/coefficient_horner.py','research/h6-compensation-network/COEFFICIENTS.json',
 'research/h6-compensation-network/routes/BUCKETED-SCHEMA.json']
result=dict(status='PASS_INTEGRAL_BANK_AND_BOUNDED_PHYSICAL_ROW_BOUNDS',
 no_new_kappa=True,bank_layout=banks,physical_helper_witnesses=witness,
 factor_incidence_statistics=dict(nonzeros=6440208,max_gather_row=int(grow.max()),
  max_gather_column=int(gcol.max()),max_scatter_row=str(F(int(srow.max()),den)),
  max_scatter_column=str(F(int(scol.max()),den))),
 amplification=dict(norm='row l1 on arbitrary independent initial scalar columns',
  forward_phases={k:str(v) for k,v in forward.items()},dual_phases={k:str(v) for k,v in dual.items()},
  logical_bound=str(B),cleared_horner_bound=str(B_horner),component_physical_bound=str(physical),
  input_norm_convention='Unit maximum complex magnitude per initial logical coordinate. Physical conversion includes initial source C_p inverse infinity norm sqrt2 and current frame norm at most2^(17/2), total512. Other initial frames are zero. Real/imag component inputs individually bounded1 require an additional sqrt2 if interpreted as complex magnitudes.',
  physical_operator_norm_factor=512,real_component_multiplier_for_operation_counts=2,
  primitive_roundoff_error_bound=f'{whole_real_bound}*2^({whole_real_bound}+{rank_mass}-b)',
  sufficient_binary_precision_for_error_epsilon=f'b >= {whole_real_bound}+{rank_mass}+ceil(log2({whole_real_bound}/epsilon))',
  roundoff_derivation='Each real scalar primitive has max component amplification<=2; each rank-r child has infinity norm<=2^r. Summing arbitrary scalar errors<=2^-b over all real operations gives P*2^(P+total_child_rank-b). This is an impractical finite conservative bound, conditional on exact child actions. Prefix B does not bound suffix error propagation.',
  maximum_exact_coefficient_halvings=10,
  caveat='Conservative local phase bounds. No all-size precision/grid/child-error transfer is certified.'),
 scalar_primitive_bound=dict(compensation=primitive_comp,K_forward=kres['K_forward_primitive_bound'],
  K_dual=kres['K_dual_primitive_bound'],real_components=real_primitive,
  convention='Cleared Horner temporary, repeated doubling/halving, signed accumulation, erase. Includes copy/clear convention. No implicit coefficient adapter is free.'),
 sharp_universal_movement_ledger=sharp,
 local_compiler_families=dict(universal_coverage=universal['coverage'],
  coefficient_coverage=horner['scope'],status='LOCAL_ENDPOINT_TRANSITION_AND_COEFFICIENT_FAMILIES_CLOSED'),
 adapter_bound=dict(ledger='GENERIC172_ACTION_CONSERVATIVE_LEDGER_RETAINED',two_monomials_per_transition=True,h=17,
  monomial_recipe_fields=['binary17x17 address permutation','translation17','quadratic136 off-diagonal plus17 linear phases','global phase'],
  maximum_scalar_unit_phase_actions_per_adapter_per_coordinate=154,
  conservative_combined_phase_and_movement_actions_per_adapter_per_coordinate=172,
  maximum_address_movements_per_adapter_per_coordinate=1,
  local_transition_count=transitions,local_child_rank_mass=rank_mass,
  two_adapters_per_transition_real_component_operation_bound=adapter_real_bound,
  whole_scalar_plus_adapter_real_component_operation_bound=whole_real_bound,
  bound_scope='Semantic recipe bound: at most136 quadratic,17 linear and1 global unit phases plus1 affine address movement per coordinate.172 combined actions is a conservative upper bound before2 real-component operations per complex action. This is not a raw machine-instruction bound; implementation of permutation movement/tape remains within the inherited cost model. Universal local transition family now provides the separately reported sharper2-affine-pass/no-phase ledger; integrated tape/bank compiler remains open.'),
 source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
 remaining_gate='Local all-endpoint/transition operator recipe family and every used coefficient Horner stream are supplied by universal.py and coefficient_horner.py. Remaining: integrated physical bank/controller/pad and immutable tape/compiler realization, common-grid precision with accumulated approximate-child errors, full bit supplier and all-size analytic/outer transfer. The finite semantic movement ledger is not a machine-instruction/tape bound.',
 limits='No full3.38-billion-event replay, no full physical bank allocation materialization, no favorable nominal invoice, no supplier admission.')
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(result['status']);print('logical row bound',B,'Horner',B_horner,'physical',physical);print('physical witnesses',len(witness))
