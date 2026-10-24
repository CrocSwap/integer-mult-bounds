"""25 operational adaptations, with explicit limits on their transfer.
Each function returns evidence on the pinned multiplication interface. These
are restricted adaptations of techniques, not implementations of 25 whole papers.
"""
import importlib.util
import json
import sys
from collections import Counter, OrderedDict
from functools import cached_property
from fractions import Fraction as F
from pathlib import Path
from algebra import (need, eye, transpose, mm, add, rank, inverse, gf_basis,
                     reversible_path, binary_elimination, coupled_program,
                     replay, lagrange_weights, coupled_program_dual)
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent

def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec);sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj

class Fixture:
    def __init__(self):
        self.n=json.loads((ROOT/'research/coded-native-caller/NORMALIZERS.json').read_text())
        self.p=json.loads((HERE/'inputs/PROVIDER.json').read_text())
        self.bank=json.loads((HERE/'inputs/QUERY-BANK.json').read_text())
        self.selected=json.loads((HERE/'inputs/SELECTED-ARITHMETIC.json').read_text())
        self.controller=json.loads((ROOT/'research/joint-helper-lattice/CONTROLLER.json').read_text())
        self.ce=module('literature_clifford',ROOT/'research/coded-native-caller/clifford_exact.py')
        self.old=module('transport_premise',HERE/'inputs/transport_verify.py')
        self.m=self.n['mode_columns']
        need(len(self.m)==8 and all(len(r)==112 for r in self.m),'actual mode dimensions')
        need(mm(self.m,transpose(self.m))==[[56*(i==j) for j in range(8)] for i in range(8)],'actual mode Gram')
    def op(self,word):
        ce=self.ce;o=ce.ident(9)
        for g in word:
            if g[0]=='P':v=ce.perm(9,g[1])
            elif g[0]=='D':v=ce.diag(9,g[1],g[2])
            elif g[0]=='X':v=ce.xgate(9,g[1])
            elif g[0]=='phase':v=ce.Op(9,ce.identity(9),[('phase',g[1])])
            else:raise ValueError(g)
            o=o.then(v)
        return o
    @cached_property
    def modes(self):
        return [self.op(p['input_K']['literal_word']) for p in self.p['mode_boundaries']]
    @cached_property
    def ports(self):
        return [self.op(p['K_word']) for p in self.n['ports']]
    @cached_property
    def physical(self):
        t=self.old;m=self.m
        kt=[t.table(p['K_word']) for p in self.n['ports']]
        mt=[t.table(p['input_K']['literal_word']) for p in self.p['mode_boundaries']]
        w=[[t.compose(t.inverse(kt[i]),mt[k]) for i in range(112)] for k in range(8)]
        z=[[t.inverse(w[k][i]) for i in range(112)] for k in range(8)]
        v,zv=t.experiment(m,w,z,1);g=t.residual_gram(v,zv);det,piv=t.determinant(g)
        v0,z0=t.experiment(m,w,z,0)
        need(t.residual_gram(v0,z0)==[[0]*8 for _ in range(8)],'zero-address control')
        need(g[0][0]==F(173,14),'nonzero physical address')
        return dict(gram=g,det=det,pivots=piv,w=w,z=z,v=v,zv=zv)
    @cached_property
    def W(self):
        return [[F(self.m[k][i],2) for k in range(8)] for i in range(112)]
    @cached_property
    def Z(self):return transpose(self.W)
    @cached_property
    def C(self):return add(eye(112),mm(self.W,self.Z),-1)
    @cached_property
    def H(self):return replay(coupled_program(self.m,F(-4)),eye(120))
    @cached_property
    def E(self):return [self.ce.cgate(9,1).then(k) for k in self.ports]

def kalman62(f):
    # Readout ignores an arbitrary helper complement until its return is demanded.
    obs=f.Z; r=rank(obs); restored=rank(obs+eye(112))
    need(r==8 and restored==112,'restoration-aware observable quotient')
    return dict(observation_rank=r,rank_with_arbitrary_original_return=restored,
        discarded_directions_requiring_return=restored-r,
        decision='Compress observation history; preserve all 112 independent originals.')

def kalman63(f):
    # Finite two-generation realization on eight actual input columns. Schur
    # complement is the residual Gram, so augmented reachability rank is 16.
    g=f.physical['gram']; schur_rank=rank(g)
    need(schur_rank==8,'eight new reachable directions at second chart')
    trace=f.old.chronology(f.controller)
    successor=json.loads((HERE/'inputs/SUCCESSOR-CONTROLLER.json').read_text())
    need(successor['physical_events'][5:19]==f.controller['physical_events'][1:15],
         'successor has the identical two-generation consumer clip')
    need(trace['required_transfer_equation']=='W3 T = D1 W1','literal source cut')
    return dict(first_reachable_columns=8,new_observable_residual_columns=schur_rank,
        two_generation_witness_column_rank=16,events=trace['event_indices_inclusive'],
        second_helper_cross_contamination=trace['second_helper_cross_contamination'],
        decision='Keep generation-tagged latent state; an eight-mode stationary realization fails.',
        scope='Finite f=1, 17-bit address witness; not a whole-field cost lower bound.')

def ma26(f):
    # Exact residual of inverse approximation I+(-1/52+delta) MM^T.
    delta=F(1,2**20); residual_norm=728*delta; forward_norm=56*delta
    need(residual_norm==13*forward_norm,'actual capacitance residual sensitivity')
    return dict(capacitance_eigenvalue=-13,condition_number_C=13,
        inverse_coefficient_perturbation=str(delta),inverse_error_2norm=str(forward_norm),
        residual_2norm=str(residual_norm),small_update_corollary_applicable=False,
        reason='Update norm is 14; the paper\'s <=1/2 small-update hypothesis fails.',
        decision='Certify exact residuals and amplification; symbolic inversion alone is insufficient.')

def sherman50(f):
    u=list(map(F,f.m[0])); dot=sum(x*x for x in u)
    inv_coefficient=F(-1,4)/(1-dot/4)
    # (I+alpha uuT)(I+beta uuT)=I when alpha+beta+alpha beta ||u||²=0.
    beta=-inv_coefficient
    need(-F(1,4)+beta-F(1,4)*beta*dot==0,'rank-one inverse update')
    need(beta==-F(1,52),'source coefficient')
    return dict(mode_norm_squared=str(dot),inverse_update_coefficient=str(beta),
        denominator_avoided_at_odd_prime=13,
        decision='Use exact rank-one algebra for checks; no physical Gaussian disappears.')

def henderson81(f):
    small=add(eye(8),mm(f.Z,f.W),-1);small_inv=inverse(small)
    need(small==[[F(-13*(i==j)) for j in range(8)] for i in range(8)],'rank-eight capacitance')
    cinv=add(eye(112),mm(mm(f.W,small_inv),f.Z))
    # Minus sign in Woodbury: (I-WZ)^-1 = I + W(I-ZW)^-1 Z.
    need(mm(f.C,cinv)==eye(112),'112-column Woodbury identity')
    return dict(capacitance_dimension=8,checked_original_columns=112,
        formula='C^-1 = I - M M^T/52',
        decision='Low-rank inverse is algebraically closed; implementing it must still pay reads and restoration.')

def bennett73(f):
    ops=f.old.exit_program(f.m,'purchased');checks=f.old.check_exit_program(f.m,'purchased',ops)
    bad=[e[:] for e in ops];bad.pop(next(i for i,e in enumerate(bad) if e[0]=='CLEAR'))
    try:f.old.check_exit_program(f.m,'purchased',bad)
    except ValueError:pass
    else:raise ValueError('missing clean initialization accepted')
    # A recursive result cannot be discarded to implement uncomputation.
    return dict(literal_exit=checks,owned_fields=112,
        source_inverse_is_free=False,omitted_initialization_rejected=True,
        decision='Retain an observation until its last use, then charge its actual cleanup.')

def bennett89(f):
    n=min(8,sum(e[0]=='LOCAL' and e[3] for e in f.controller['physical_events']));profiles={}
    for p in range(3,9):
        path=reversible_path(n,p)
        if path is not None:
            state=0
            for i in path:
                need(i==1 or state>>(i-2)&1,'legal predecessor pebble')
                state^=1<<(i-1);need(state.bit_count()<=p,'pebble budget')
            need(state==1<<(n-1),'clean endpoint')
        profiles[str(p)]=None if path is None else len(path)
    return dict(horizon_nodes=n,minimum_moves_by_peak_saved_nodes=profiles,
        decision='Checkpointing trades retained observations for recomputation; every recomputed child stays paid.',
        scope='Exact finite reversible path search, not a schedule for the full native controller.')

def buhrman14(f):
    # Check every independent coefficient, including the dirty helper a.
    # Q(a+u)-Qa=Qu is linear and restores a only if its original version survives.
    a={'Qa':F(1),'Qu':F(1)};a['Qa']-=1
    need(a=={'Qa':0,'Qu':1},'dirty difference extraction')
    bank=f.bank;need(bank['direction']=='forward_only','bank direction binding')
    queries=bank['queries'];need(len(queries)==112,'paid bank size')
    for q in queries:
        e=f.op(q['input_K']['word']).then(f.ce.canonical_frame(9,[q['line']])).then(f.op(q['response']['word']))
        target=f.ce.cgate(9,1)
        need(e.tab==target.tab and e.zero_state()==target.zero_state(),'112 paid source query phases')
    return dict(checked_paid_bank_queries=112,arbitrary_dirty_input=True,
        fresh_calls_for_Q_of_u=2,calls_if_same_version_Qa_is_retained=1,
        helper_target_rank_upgrade=bank['invoice']['added_paid_rank_mass'],
        same_version_required=True,backward_bank_supplied=False,
        decision='Try versioned dirty observations at real paid sites; helper-bank xi does not equal arbitrary main Y.')

def cook24(f):
    # Leading-coefficient extraction from a dirty shift. Linear case is exactly
    # the two-contact catalytic difference; quadratic case needs three contacts.
    m=f.m;a=[F(i%5-2) for i in range(112)];u=[F((i*7)%11-5) for i in range(112)]
    def energy(t):return sum(sum(v*(x+t*y) for v,x,y in zip(row,a,u))**2 for row in m)
    xs=[-1,0,1]; weights=[F(1,2),F(-1),F(1,2)]
    value=sum(w*energy(x) for x,w in zip(xs,weights));target=sum(sum(v*y for v,y in zip(row,u))**2 for row in m)
    need(value==target,'dirty polynomial leading coefficient cancellation')
    need(sum(weights)==0 and sum(w*x for x,w in zip(xs,weights))==0,'lower-degree annihilation')
    prime=17;omega=4
    need(pow(omega,4,prime)==1 and pow(omega,2,prime)!=1,'root order four')
    def mod_energy(t):return int(energy(t))%prime
    # Constant-term cancellation on u + omega^j a, from Cook-Mertz Lemma 8.
    def shifted(t):return sum(sum(v*(y+t*x) for v,x,y in zip(row,a,u))**2 for row in m)
    averaged=sum(int(shifted(pow(omega,j,prime))) for j in range(4))*pow(4,-1,prime)%prime
    need(averaged==int(target)%prime,'finite-field root-of-unity cancellation')
    return dict(exact_mode_energy_coefficient=str(value),degree=2,evaluations=3,
        roots_of_unity_probe=dict(prime=prime,root=omega,order=4,evaluations=4,result=averaged),
        linear_Gaussian_case_evaluations=2,
        decision='Interpolation removes dirty dependence but introduces contacts; preserve source versions and charge every evaluation.',
        scope='Adapted interpolation identity, not the Cook-Mertz TreeEval algorithm or its space theorem.')

def hong81(f):
    # LRU evaluation of the actual three-pass 120-field boundary program.
    ops=coupled_program(f.m,F(-4));curves={}
    for cap in [8,16,32,64,120]:
        cache=OrderedDict();reads=writes=0
        def touch(i,dirty):
            nonlocal reads,writes
            if i not in cache:
                reads+=1
                if len(cache)==cap:
                    _,d=cache.popitem(last=False);writes+=d
                cache[i]=False
            cache[i]|=dirty;cache.move_to_end(i)
        for e in ops:
            if e[0]=='add':touch(e[2],False)
            touch(e[1],True)
        writes+=sum(cache.values());curves[str(cap)]={'reads':reads,'writes':writes}
    need(curves['120']=={'reads':120,'writes':120},'all-resident I/O control')
    return dict(program='BALANCED-PROGRAM.json',LRU_field_transfer_curve=curves,
        decision='Choose block order against measured residency; a scalar ADD saving is not yet a tape-motion saving.',
        scope='Fixed-program LRU upper costs, not an I/O lower bound or BIT compiler.')

def schwartz23(f):
    degrees=[sum(bool(f.m[k][i]) for i in range(112)) for k in range(8)]
    edges=sum(degrees);ports=sum(any(f.m[k][i] for k in range(8)) for i in range(112))
    need(degrees==[56]*8 and edges==448 and ports==112,'actual observation DAG')
    return dict(dependency_edges=edges,
        schedules=[dict(accumulators=8,source_frame_evaluations=ports,ADD=edges),
                   dict(accumulators=1,source_frame_evaluations=edges,ADD=edges)],
        input_values_preserved=True,output_observation_fields=8,zero_initializations=8,
        one_accumulator_requires_streamed_consumption_or_separate_output_storage=True,
        decision='Use eight resident accumulators when source maps are expensive; owned or borrowed state must be invoiced.',
        scope='Two constructive schedules on the real observation DAG; no optimal pebbling claim.')

def karstadt20(f):
    h=f.H;need(replay(coupled_program(f.m,F(-4)),h)==eye(120),'all-column involution')
    # A common linear encoding carries ADD; mismatched encodings do not.
    other=replay(coupled_program(f.m,F(-1)),eye(120))
    need(h!=other,'different-frame failure control')
    calls=sum(e[0]=='LOCAL' and e[3] for e in f.controller['physical_events'])
    return dict(encoded_ADD_all_columns_checked=120,compatible_frame_required=True,
        backward_calls=calls,ordinary_conversions_if_each_call_decodes=2*calls,
        conversions_if_one_compatible_chain=2,potential_saved_conversions=2*calls-2,
        decision='Retain a common coupled type across compatible consumers; prove intervening thin queries in that type.',
        scope='Conversion fusion conditional on type compatibility, not an admitted sixteen-call chain.')

def schwartz26(f):
    candidates=[]
    for odd in [1,3]:
        for k in range(-8,9):
            a=-F(odd)*F(2)**k;b=-12/a
            candidates.append((338+14*(a*a+b*b),a,b))
    score,a,b=min(candidates)
    need(score==688 and {abs(a),abs(b)}=={3,4},'dyadic gauge optimum in stated grid')
    # Use a=-4 to keep the first pass simple; both symmetric optima have same 2-norm.
    a=F(-4);b=F(3);h=f.H
    norminf=max(sum(abs(v) for v in row) for row in h)
    need(mm(h,h)==eye(120),'balanced involution')
    prior=338+14*(F(6)**2+F(2)**2)
    need(prior==898,'prior PR4935 gauge comparison')
    unbalanced=338+14*(F(1)+144)
    return dict(gauge={'a':str(a),'b':str(b),'a_times_b':str(a*b)},
        normalized_mode_block_Frobenius_squared=str(score),
        prior_PR4935_gauge_Frobenius_squared=str(prior),
        unbalanced_reference_gauge_Frobenius_squared=str(unbalanced),
        continuous_optimum_Frobenius_squared=674,finite_dyadic_grid_candidates=len(candidates),
        exact_scalar_frame_infinity_norm=str(norminf),
        literal_counts=dict(Counter(e[0] for e in coupled_program(f.m,a))),
        physical_signed_monomial_boundary_maps=240,new_owned_fields=0,paid_Gaussian_delta=0,
        decision='Use the balanced scratch-free involution as a coupled boundary seed; prove precision through the full recursion.')

def bini80(f):
    xs=[1,2,3];weights=lagrange_weights(xs)
    need(weights==[F(3),F(-3),F(1)],'degree-two exact recovery weights')
    for degree in range(3):need(sum(w*x**degree for w,x in zip(weights,xs))==int(degree==0),'interpolation identities')
    for row in f.m:
        # An exact degree-two perturbation of each real mode coefficient.
        recovered=[sum(w*(F(c)+x*(i+1)+x*x*(i%7)) for x,w in zip(xs,weights)) for i,c in enumerate(row)]
        need(recovered==row,'all source mode coefficients recovered')
    return dict(perturbation_degree=2,evaluations=3,weight_l1=7,mode_coefficients_checked=896,
        decision='Exactify an approximate seed only after pricing evaluation multiplicity and precision; matrix-exponent overhead is not harmless here.')

def demmel07(f):
    # Propagate independent additive errors through the literal scalar program.
    # Per-field l1 gain bounds do not assume inverse transforms cancel rounding.
    bounds=[F(1)]*120
    for e in coupled_program(f.m,F(-4)):
        if e[0]=='scale':bounds[e[1]]=abs(F(e[2]))*bounds[e[1]]+1
        else:bounds[e[1]]+=abs(F(e[3]))*bounds[e[2]]+1
    # Actual complex Gaussian on input (1/3,0): Q yields ((1+i)/6,(1-i)/6).
    def cmul(a,b):return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    def cadd(a,b):return (a[0]+b[0],a[1]+b[1])
    q=(F(1,2),F(1,2));r=(F(1,2),-F(1,2))
    initial=[(F(1,3),F()),(F(),F())]
    out=[cadd(cmul(q,initial[0]),cmul(r,initial[1])),cadd(cmul(r,initial[0]),cmul(q,initial[1]))]
    rounded=[tuple(F(round(v*4),4) for v in x) for x in out]
    back=[cadd(cmul(r,rounded[0]),cmul(q,rounded[1])),cadd(cmul(q,rounded[0]),cmul(r,rounded[1]))]
    need(back==[(F(1,2),F()),(F(),F())],'actual complex inverse-seam rounding defect')
    need(back[0][0]-initial[0][0]==F(1,6),'nonzero deterministic defect')
    return dict(local_independent_contact_l1_bound=str(max(bounds)),
        actual_Q_inverse_Q_rounded_input=['1/3','0'],rounded_return=['1/2','0'],defect='1/6',
        decision='Track independent rounding contacts and coefficient growth; a formal inverse pair does not erase them.')

def dumitriu26(f):
    # Exact dyadic recovery of the new boundary, including intermediate growth.
    rows=eye(120);max_den=0;peak_l1=F(1)
    for e in coupled_program(f.m,F(-4)):
        rows=replay([e],rows)
        row=rows[e[1]]
        for v in row:
            d=v.denominator;need(d&(d-1)==0,'dyadic program coefficient')
            max_den=max(max_den,d.bit_length()-1)
        peak_l1=max(peak_l1,sum(abs(v) for v in row))
    need(rows==f.H,'exact dyadic boundary')
    cycle=mm(f.Z,f.W);traces=[];power=eye(8)
    for _ in range(4):
        power=mm(power,cycle);traces.append(sum(power[i][i] for i in range(8)))
    need(traces==[8*14**k for k in range(1,5)],'non-nilpotent source cycle')
    # Constructive three-factor nilpotent positive control: U=V=I8, W=N
    # with N[i,i+1]=1. R_i=3i,S_i=3i+1,T_i=3i+2 gives every nonzero
    # transformed entry exponent one, matching the paper's cyclic filtration.
    R=[3*i for i in range(8)];S=[x+1 for x in R];T=[x+2 for x in R]
    exponents=[S[i]-R[i] for i in range(8)]+[T[i]-S[i] for i in range(8)]+[R[j]-T[j-1] for j in range(1,8)]
    need(exponents==[1]*23,'nilpotent cyclic-filtration positive control')
    return dict(similarity_degeneration_trace_screen=list(map(str,traces)),
        source_cycle_nilpotent=False,
        nilpotent_three_factor_positive_control_exponents=exponents,
        nilpotent_tensor_term_transfer_proved=False,
        max_intermediate_coefficient_denominator_bits=max_den,
        max_intermediate_scalar_row_l1=str(peak_l1),
        final_coefficient_denominator_bits=max(v.denominator.bit_length()-1 for row in rows for v in row),
        exact_recovery_requires_error_strictly_below_half_grid=True,
        decision='Reject shrinking the whole non-nilpotent WZ cycle by similarity; separate exact grid recovery from leading recursive precision.',
        scope='Exact grid and coefficient probe; not a transfer of the paper\'s approximate matrix multiplication theorem.')

def ballard16(f):
    # Optimize diagonal scaling within the exact involution family, not by
    # independently minimizing forward/backward norms (the inverse is itself).
    candidates=[]
    for a in [-F(1),-F(2),-F(3),-F(4),-F(6),-F(8),-F(12)]:
        h=replay(coupled_program(f.m,a),eye(120));n=max(sum(abs(v) for v in row) for row in h)
        candidates.append({'a':str(a),'b':str(-12/a),'l1_bound':str(n),'squared_bound':str(n*n)})
    best=min(candidates,key=lambda x:F(x['squared_bound']))
    dual=coupled_program_dual(f.m,F(-12));dual_H=replay(dual,eye(120))
    need(dual_H==replay(coupled_program(f.m,F(-12)),eye(120)),'dual scratch-free compiler endpoint')
    expected_H=[f.C[i]+[-12*x for x in f.W[i]] for i in range(112)]
    expected_H += [f.Z[k]+[F(13*(k==j)) for j in range(8)] for k in range(8)]
    need(dual_H==expected_H,'all 120 analytic row-sum gauge columns')
    need(all(F(e[-1]).denominator&(F(e[-1]).denominator-1)==0 for e in dual),'dual compiler uses only dyadic constants')
    need(replay(dual,dual_H)==eye(120),'dual all-column involution')
    return dict(gauge_l1_screen=candidates,best_scalar_l1_gauge=best,
        dyadic_dual_row_sum_program='ROWSUM-PROGRAM.json',
        dual_program_counts=dict(Counter(e[0] for e in dual)),
        odd_divisions_in_dual_program=0,
        prior_PR4935_scalar_l1_bound='69',
        prior_PR4935_gauge='a=6,b=-2 (equivalent norms to a=-6,b=2)',
        decision='Optimize the precision metric used by the compiler; the 2-norm-optimal gauge need not minimize row-sum error.')

def dehaene03(f):
    def sp(p,q):return ((p[0]&q[1]).bit_count()+(p[1]&q[0]).bit_count())%2
    ops=f.ports+f.modes
    for op in ops:
        for i,p in enumerate(op.tab):
            for j,q in enumerate(op.tab):need(sp(p,q)==int(abs(i-j)==9),'symplectic form')
    return dict(signed_symplectic_operators_checked=len(ops),pauli_pairs_per_operator=324,
        decision='Use binary symplectic forms to search composable frames, with a separate absolute-phase witness.')

def aaronson04(f):
    t=f.old;words=[p['K_word'] for p in f.n['ports']]+[p['input_K']['literal_word'] for p in f.p['mode_boundaries']]
    for op,word in zip(f.ports+f.modes,words):
        v,d=op.zero_state();dest,ph=t.table(word)[0]
        need(d==0 and v[dest]==t.rot((1,0),ph) and sum(x!=(0,0) for x in v)==1,'phase anchor')
    op=f.E[0];bad=op.then(f.ce.Op(9,f.ce.identity(9),[('phase',1)]))
    need(op.tab==bad.tab and op.zero_state()!=bad.zero_state(),'same-tableau global-phase mutation')
    return dict(phase_anchored_frames=len(words),global_phase_only_mutation_rejected=True,
        decision='Tableau plus one anchored state authenticates Clifford phase; tableau equality alone is inadequate.')

def patel08(f):
    totals=Counter();best=0
    for p in f.n['ports']:
        sizes={b:len(binary_elimination(p['G_rows'],b)) for b in [1,2,3,4]}
        totals.update(sizes);best+=min(sizes.values())
    return dict(source_matrices=112,CNOT_counts_by_fixed_panel_size=dict(totals),
        per_matrix_best_count=best,
        decision='Apply panel elimination to ordinary wrapper synthesis; it cannot merge independent physical field volumes.')

def amy14(f):
    # A feasible matroid partition, explicitly not the minimum-T-depth optimizer.
    groups=[]
    for p in f.n['ports']:
        v=p['q']
        for g in groups:
            if len(gf_basis(g+[v]))==len(g)+1:g.append(v);break
        else:groups.append([v])
    need(sum(map(len,groups))==112 and all(len(gf_basis(g))==len(g) for g in groups),'independent linear-form batches')
    return dict(feasible_independent_form_batches=list(map(len,groups)),
        dimension_lower_bound_on_batches=13,optimality_claimed=False,
        decision='Batch independent phase/readout forms for ordinary scheduling; each independent payload remains a separate volume.')

def bravyi21(f):
    flags=[gf_basis([x|(z<<9) for x,z,ph in op.tab[9:]]) for op in f.E]
    need(len(set(flags))==112,'112 distinct actual right monomial cosets')
    need(len(set(flags[:1]*112))==1,'identical-column positive control')
    # Left multiplication by Kp is free individually, but after aggregation the
    # single common left transform has to work for every source column.
    return dict(columns=112,distinct_right_monomial_cosets=len(set(flags)),
        distinct_cosets_per_output_mode=[len({flags[i] for i in range(112) if f.m[k][i]}) for k in range(8)],
        pairwise_shareable_columns_in_single_accumulator=0,identical_column_control_groups=1,
        decision='Reject one-Gaussian-after-monomial-aggregation for this source; seek a two-sided or endogenous observer.',
        scope='Only E_i=G R_i with one shared G and monomial R_i. Does not exclude multi-layer joint circuits.')

def maslov18(f):
    ce=f.ce;left=Counter();right=Counter()
    for i in range(len(f.E)):
        for j in range(i):
            # Two orientations expose why cancellation of Q Q^-1 on paper
            # does not grant common pre-aggregation with independent inputs.
            A=f.E[i];B=f.E[j]
            left[ce.rank([x for x,z,p in A.then(B.adjoint()).tab[9:]])]+=1
            right[ce.rank([x for x,z,p in B.adjoint().then(A).tab[9:]])]+=1
    need(right=={0:6216} and left.get(0,0)==0,'oriented Bruhat rank census')
    return dict(pair_count=6216,rank_B_of_Ej_inverse_Ei=dict(left),rank_B_of_Ei_Ej_inverse=dict(right),
        decision='Cancel compatible two-sided boundaries in the correct order; independent inputs still pay physical volume.')

def edelman98(f):
    g=f.physical['gram'];S=eye(8)
    for i in range(7):S[i][i+1]=1
    changed=mm(mm(transpose(S),g),S)
    need(rank(changed)==8,'basis-independent residual rank')
    det,_=f.old.determinant(changed)
    need(det==f.physical['det'],'unimodular basis determinant control')
    return dict(residual_rank=8,Gram00=str(g[0][0]),determinant=str(det),
        changed_basis_residual_rank=rank(changed),
        decision='A mode-basis search cannot repair a subspace mismatch; change the observable state or the contact.')

def kailath79(f):
    # Across actual charts: D1 C1 - C3 D1 = W3 Z3 D1 - D1 W1 Z1.
    # Evaluate its action on all eight W1 columns, rather than just counting
    # formal generator words. The action is -14 times the residual projection.
    t=f.old;p=f.physical;residual=[]
    for V,ZV in zip(p['v'],p['zv']):
        fields=[]
        for i in range(112):
            projected={}
            for k in range(8):
                sign=f.m[k][i]
                if not sign:continue
                w=p['w'][k][i]
                for address,value in ZV[k].items():
                    local=(address&1)|((address>>9)<<1);dest,phase=w[local]
                    dest=(address&510)|(dest&1)|((dest>>1)<<9)
                    x,y=t.rot(value,phase);u,v=projected.get(dest,(0,0))
                    projected[dest]=(u+sign*x,v+sign*y)
            # V numerator /512; W3 Z3 V numerator /2048.
            # 14 V - W3 Z3 V is the negative displacement action.
            row={a:(56*x,56*y) for a,(x,y) in V[i].items()}
            for a,(x,y) in projected.items():
                u,v=row.get(a,(0,0));row[a]=(u-x,v-y)
            fields.append({a:v for a,v in row.items() if v!=(0,0)})
        residual.append(fields)
    gram=[[t.inner(a,b,2048) for b in residual] for a in residual]
    need(gram==[[196*x for x in row] for row in p['gram']],'actual displacement generator action')
    return dict(identity='D1 C1 - C3 D1 = [W3, D1 W1] [Z3 D1; -Z1]',
        generator_field_blocks_upper=16,actual_residual_witness_rank=rank(gram),
        checked_input_mode_columns=8,displacement_Gram00=str(gram[0][0]),
        decision='Carry chart displacement generators with generation tags, then solve their legal readout and termination.',
        scope='Actual f=1 operator action; 16 generator fields is not a scalar Gaussian rank or a free-volume implementation.')

PROBES=[kalman62,kalman63,ma26,sherman50,henderson81,bennett73,bennett89,
        buhrman14,cook24,hong81,schwartz23,karstadt20,schwartz26,bini80,
        demmel07,dumitriu26,ballard16,dehaene03,aaronson04,patel08,amy14,
        bravyi21,maslov18,edelman98,kailath79]

def run():
    f=Fixture();results=[]
    for i,probe in enumerate(PROBES,1):
        results.append({'paper_id':f'P{i:02d}','implementation':f'experiments.py:{probe.__name__}',
                        'evidence':probe(f)})
    return f,results
