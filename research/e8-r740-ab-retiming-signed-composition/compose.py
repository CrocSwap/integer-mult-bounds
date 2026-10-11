"""Source-bound refined composition of PR433 split-centre and PR436 signed R740 plus75 exact integer kernel suppliers.

OpenAI Codex assistance; Apache-2.0. Keeps the finite Hamming construction,
source-preserving R740 bit supplier and all their stated all-size/analytic obligations.
Uses fresh PR433 full-phase replay and a separately validated signed lift.
"""
import argparse, hashlib, importlib.util, json, math
from fractions import Fraction as Q
from pathlib import Path

if not __debug__: raise SystemExit('Assertions required')
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rd=lambda p:json.loads(Path(p).read_text())
def enc(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):enc(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [enc(v) for v in x]
    return x
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--complex',type=Path,required=True);ap.add_argument('--bit',type=Path,required=True);ap.add_argument('--engines',type=Path,required=True);ap.add_argument('--native-bit',type=Path,required=True);a=ap.parse_args()
    a.complex=a.complex.resolve();a.bit=a.bit.resolve();a.engines=a.engines.resolve();a.native_bit=a.native_bit.resolve()
    cx=a.complex/'split-centres';bit=a.native_bit/'bit426-source-centres/global'
    paths=[a.complex/'RESULT.json',cx/'INTEGRATION.json',cx/'SCALAR-FRAME-AUDIT.json',a.complex.parent/'PRIMITIVE-REVIEW.json',bit/'GLOBAL.json',bit/'GEOMETRY.json',a.bit/'RESULT.json',a.bit/'GLOBAL-BOUND.json']
    inputs={str(p.relative_to(P)) if p.is_relative_to(P) else str(p):sha(p) for p in paths}
    full,ci,ca,primitive,bg,geo,signed,bc=map(rd,paths)
    assert bc['status']=='PASS_KERNEL75_R740_T64_SIGNED_COMPLETE_PREFIX_AND_COMPENSATED_FINITE_INVOICE'
    for rel,digest in bc['source_inputs'].items():assert sha(P/'evidence'/rel)==digest
    assert sha(bit/'GLOBAL.json')==bc['source_inputs'][str((bit/'GLOBAL.json').relative_to(P/'evidence'))]
    assert sha(bit/'GEOMETRY.json')==bc['source_inputs'][str((bit/'GEOMETRY.json').relative_to(P/'evidence'))]
    native_bit=rd(a.native_bit/'RESULT.json')
    assert signed['integer_kernel']['pivots']==75 and signed['integer_kernel']['all_positive_start_responses_zero_over_Z']
    assert signed['integer_kernel']['sidecar_convention']=='K_p=sum(c_d K_d); entrance=-c_d, cleanup=+c_d'
    assert full['status']=='PASS_CONDITIONAL_SPLIT_CENTRE_ASSEMBLY' and full['phase_mode']=='full replay'
    assert full['manifest_sha256']=='3129eb4321f706542470f8443f66a6b4351a12a9ceec85e7f76aa19db1e1e32f'
    assert bg['R']==740 and bg['m']==64 and bg['replicas']==64 and bg['live']==113829
    assert primitive['status']=='PASS_INDEPENDENT_LITERAL_PRIMITIVES_ALL800_COLUMNS_AND_ACTUAL_PAYMENT'
    for ori in ('forward','backward'):
        pr=primitive['orientations'][ori];native=ci['local_program_checks'][ori]
        assert pr['all_live_endpoints_exact'] and pr['private_work_zero'] and pr['omitted_actual_first_halve_rejected']
        assert pr['columns']==native['all_columns']==800
        assert pr['real_component_primitives']==native['real_component_primitive_bound']
    assert signed['status']=='PASS_EXACT_SIGNED_DEFINING_DECODER_AND_LITERAL_PARITY_PROJECTION'
    assert signed['exported_F2_record_sha256']==bg['source_records_sha256']
    assert signed['literal_parity_record_equality'] and signed['arbitrary_helper_dirt_restored_exactly']
    assert signed['compensation']==dict(weighted_additions=8906,odd_additions=8506,even_additions=400,unit_additions=9780,maximum_coefficient=5)
    engines=a.engines
    moment,other,outer=[load('refine_'+n,engines/(n+'.py')) for n in ['moment','base_two_moment','outer']]
    for n in ['moment','base_two_moment','outer']:inputs[str(engines/(n+'.py'))]=sha(engines/(n+'.py'))
    def certify(profile,m,W):
        H={int(r):n for r,n in profile.items()};root=moment.certify(H,m,W,True)
        z=Q(root['lower']);grid=Q(1,10**24)
        iv=moment.moment(H,m,W,z,True);nxt=moment.moment(H,m,W,z+grid,True)
        def second(x):
            lo,hi=other.moment(m,W,list(H.items()),x)
            a,b=other.moment(m,W,[(1,32*m*m*sum(H.values()))],x)
            return lo+a/10**16,hi+b/10**16
        iv2=second(z);nxt2=second(z+grid)
        assert iv[1]<1<nxt[0] and iv2[1]<1<nxt2[0]
        return H,z,dict(lower=z,upper=z+grid,first=iv,second=iv2,next_first=nxt,next_second=nxt2)
    HC,b,cm=certify(ci['global_profile'],73,12720)
    HB,c,bm=certify(bg['profile'],64,113829)
    assert b>Q(full['complex_lower']) and c==Q(bc['bit_coarse'])
    assert sum(r*n for r,n in HC.items())==ci['rank_mass']==73*12720-2496
    assert sum(r*n for r,n in HB.items())==bg['rank_mass']==64*113829-19968
    assert 73**2>2*max(HC)**2 and 64**2>2*max(HB)**2
    # Recompute the native strong-bit bill from freshly emitted records/routes.
    m,T,L,R,V,K=64,64,9,740,120,4;W=bg['live'];physical=bg['physical'];E=sum(HB.values());d=m*m;N=2*m
    cf=signed['forward']['max_prefix_row_l1'];cb=signed['literal_signed_inverse']['max_prefix_row_l1']
    assert (cf,cb)==(804,26806)
    prefix=cf**5*cb**4*2**18
    assert prefix>int(bg['global_prefix_bound']) and prefix.bit_length()==126 and prefix<2**128
    assert bg['local_additions']==15314
    extra=signed['compensation']['unit_additions']-signed['compensation']['odd_additions'];assert extra==1274
    unit=L*T*(bg['local_additions']+extra)+bg['bridge_additions']
    assert 576*extra==733824
    J=8*T*L*(2*V+R)+8*(2*K*V*T)+2*bg['bank_assignments']+2*bg['copy_erase_episodes']
    high=16*(d+1)**2;good=8*m*m+8;compiler=128*N**3
    selectors=2*L*T*((W-1)+R*m*(geo['max_route_factors']+(m-1)+m))
    coefficient=unit+J*high+J*physical+E*(good+compiler)+16*m**3+bg['copy_erase_episodes']+selectors+prefix+1
    composed=(coefficient+1)**2*(E+1)**2
    assert coefficient.bit_length()==126 and composed.bit_length()==293
    assert coefficient==int(bc['finite']['signed_coefficient']) and composed==int(bc['finite']['signed_two_level_coefficient'])
    assert prefix==int(bc['finite']['signed_prefix']) and unit==bc['finite']['signed_unit_additions']
    assert coefficient<2**128 and composed<2**512
    assert 2*(m*m+1)+9909+252==18355<20161
    assert ci['finite_invoice']['physical_row_coefficient']==15445<20161
    eta=beta=Q(1,10**30);grid=Q(1,10**27);cap=(1-beta)*b
    lim=min(c,cap);selected=Q(((lim-grid)*10**27).numerator//((lim-grid)*10**27).denominator,10**27)
    assert 0<selected<c<cap and 0<lim-selected<=2*grid
    sm=moment.moment(HB,m,W,selected,True);assert sm[1]<1
    _,u=other.moment(m,W,list(HB.items()),selected);_,bad=other.moment(m,W,[(1,32*m*m*E)],selected);assert u+bad/10**16<1
    chain=[Q(384599,10**10)];cuts=[]
    for i in range(8):
        old=chain[-1];new=(1-selected)*selected+selected*old
        gaps=dict(atom=selected-new,borrowing=1-new-selected,remainder=1-new-selected*(1-old),stock=1-selected)
        gap=min(gaps.values());assert old<new<selected<1-new and gap>0
        cutoff=max(1,math.ceil(36/gap**2),math.ceil(2*(4+(composed-1).bit_length())/gap))
        assert cutoff*gap**2>=36 and cutoff*gap>=2*(4+(composed-1).bit_length())
        cuts.append(dict(stage=i+1,gaps=gaps,minimum_gap=gap,cutoff_log2=cutoff,charged_coefficient=composed));chain.append(new)
    bridge=dict(semantic=dict(C0=dict(base=2,exponent=210000),strict_literal_gap=1),rows=dict(degree_gap=Q(10**6)-Q(51*20161,25)))
    q=chain[-1]*(1-2*eta);ticks=(1-eta)*q/(1+q)/grid;k=Q((ticks.numerator-1)//ticks.denominator,10**27)
    assembly=outer.assembly(chain[-1],b,bridge,k,eta=eta,beta=beta)
    assert len(assembly['strict_constraints'])==47 and min(assembly['strict_constraints'].values())>0
    try:outer.assembly(chain[-1],b,bridge,k+grid,eta=eta,beta=beta)
    except AssertionError:pass
    else:raise AssertionError('Adjacent grid admitted')
    try:outer.assembly(cap,b,bridge,k,eta=eta,beta=beta)
    except AssertionError as err:assert 'leaf_saving_above_bit' in str(err)
    else:raise AssertionError('Complex leaf cap admitted')
    p=assembly['parameters'];e,cc,r,bb=[p[n] for n in ['epsilon','c','alpha_squared_power','beta']]
    ka,km,kb,ks=[math.ceil(1/x) for x in [r,e*cc,1-e,e*bb]]
    C0=2**210000;largest=73
    outercuts=dict(guard=math.ceil(Q((2*C0).bit_length())/(1-e)),normalization=math.ceil(7/(1-e-r)),alpha=16*ka*ka+1,compact=64*km*km+1,geometry=math.ceil(3/(1-e*(1+cc))),phase_cell=math.ceil(9/(e-(1-r)/2)),period=128*kb*kb+1,stopped_leaf=ks*(4*largest).bit_length(),log_p=25,reservoir=14)
    common=max(outercuts.values());assert common==14*10**30 and common>=max(2*ka,2*km,2*kb,25)
    checkpoints=[]
    for j in range(6):
        z=common*2**j
        powers=dict(alpha=(z//ka,8*(z+ka)+64),compact=(z//km,32*(z+km)+192),period=(z//kb,16*(z+kb)+56),rows=(z//kb,4*10**6*(z+kb+8)),leaf=(z//ks,4*largest))
        assert all(lhs>=rhs.bit_length() for lhs,rhs in powers.values())
        checkpoints.append(dict(log2_input=z,powers=powers))
    assert k>Q(native_bit['kappa'])>Q(full['kappa'])
    result=dict(status='PASS_SOURCE_BOUND_SPLIT433_SIGNED_R740_KERNEL75_T64_REFINED_COMPOSITION',source_head='6d9244518175caf9e0089f92486959bc2c317273',bit_source_head='da8ca2025472553ac9b36f4400138ed48a6a0e3b',input_sha256=inputs,script_sha256=sha(__file__),complex_b=b,bit_c=c,kappa=k,kappa_decimal=format(float(k),'.20f'),improvement_over_native=k-Q(native_bit['kappa']),improvement_over_split433_native=k-Q(full['kappa']),complex_moment=cm,bit_moment=bm,eta=eta,beta=beta,selected_saving=selected,selected_bit_moment=sm,selected_second_moment_upper=u+bad/10**16,bootstrap_chain=chain,finite_cutoffs=cuts,finite=dict(bit_coefficient=coefficient,bit_composed_coefficient=composed,charged_bits=512,prefix=prefix,prefix_bits=126,bit_row=18355,complex_row=15445,retained_row=20161),assembly=assembly,adjacent_grid_rejected=True,complex_leaf_cap_rejected=True,outer_cutoffs=dict(components=outercuts,common=common,power_checkpoints=checkpoints,all_interval_argument='For [Z,Z+k), bound RHS at Z+k and LHS at floor(Z/k). Successive intervals double LHS and positive affine RHS grows at most linearly; 2^j >= j+1 proves persistence.'),scope='Conditional exact composition of the PR433 split-centre complex template and a PR436 signed R740 source-preserving bit supplier with75 exact integer kernel relations. The positive-entrance dirty responses vanish over Z and the mixed rank residual slots are freshly admitted. Independent interface review and release packaging are separate gates. Inherited all-size weighted compilers, common prime/chart/precision/tape interfaces, analytic transfer, and a stage-specific C_full dominating counted primitive/wrapper/row/previous constants remain explicit. These cutoffs are not universal machine cutoffs or practical runtime estimates.')
    assert inputs=={key:sha(P/key if not Path(key).is_absolute() else Path(key)) for key in inputs}
    (P/'derived/REFINED-ASSEMBLY.json').write_text(json.dumps(enc(result),sort_keys=True,indent=2)+'\n')
    print(result['status'],str(k),float(k),flush=True)

if __name__=='__main__':main()
