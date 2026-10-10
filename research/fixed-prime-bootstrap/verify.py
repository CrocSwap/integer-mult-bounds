#!/usr/bin/env python3
"""Fixed-prime paid moment and seven finite levels on immutable PR237/234.

Copyright 2026 Gabriele Nespoli. Apache-2.0. Developed with OpenAI Codex.
No floating-point decisions; no parent mutation; no saved execution receipt input.
"""
import argparse,importlib.util,json,subprocess,sys,tempfile
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
HERE=Path(__file__).resolve().parent
DEPTH=7;GRID=10**24;COARSE_GRID=10**27;PRIME=2**127-1
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

def require(ok,message):
    if not ok:raise ValueError(message)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def serial(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):serial(v)for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [serial(v)for v in x]
    return x
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
def inventory(root,manifest):
    require(not any(p.is_symlink()for p in root.rglob('*')),'Package symlink')
    actual={p.relative_to(root).as_posix():digest(p)for p in root.rglob('*')if p.is_file()and p!=root/manifest}
    require(actual==json.loads((root/manifest).read_text())['files'],'Source drift: '+str(root))
    return actual
def point(x,grid=GRID):
    z=x*grid;return Q((z.numerator-1)//z.denominator,grid)

def prime_certificate():
    require(all(127%d for d in range(2,12)),'Composite Mersenne exponent')
    values=[4]
    for _ in range(125):values.append((values[-1]**2-2)%PRIME)
    require(values[-1]==0 and PRIME>2**80 and PRIME%2==1,'Ineligible prime')
    return dict(q=PRIME,p=127,iterations=125,residues=values,
        criterion='Lucas-Lehmer sufficiency, independently kernel-checked in Prime.lean',
        fixed_before_all_widths=True)

def validate_step(j,predecessor,c,old,a):
    require(1<=j<=DEPTH and predecessor==j-1,'Cyclic completed supplier')
    require(a==(1-c)*c+c*old and old<a<c<1-a,'Unpaid finite toll or unattained coarse leaf')
    gaps=dict(atom=c-a,borrowing=1-a-c,remainder=1-a-c*(1-old),stock=1-c)
    require(min(gaps.values())>0,'Nonpositive cutoff gap')
    return gaps

def arithmetic(parent,fresh,banks_root):
    unbanked=json.loads((fresh/'certificate.json').read_text())
    bank_package=banks_root/'research/five-stage-banks'
    sys.path.insert(0,str(bank_package))
    packing=load('retained_completed_banks',bank_package/'packing5.py')
    bank_math=load('retained_banked_arithmetic',bank_package/'arithmetic5.py')
    physical=packing.build(parent.parents[1],16643)
    computed=bank_math.build(parent.parents[1],unbanked,physical)
    old=json.loads((bank_package/'certificate.json').read_text())
    require(serial(computed)==old['arithmetic']and serial(physical)==old['physical'],'Fresh bank certificate mismatch')
    old=old['arithmetic']
    finite=json.loads((fresh/'finite.json').read_text())
    primes=json.loads((fresh/'primes.json').read_text())
    public=load('retained_five_stage_moment',parent/'code/five_stage_bit_cost_20261009.py')
    independent=load('independent_atanh_moment',HERE/'base_two_moment.py')
    outer=load('retained_outer47',parent/'code/paired_cube_assembly.py')
    cutoffs=load('retained_finite_cutoff',parent/'finite_check.py')
    prime=prime_certificate();m=120;W=261659
    H={int(r):n for r,n in old['bit_profile']['histogram'].items()}
    E=sum(H.values());mass=sum(r*n for r,n in H.items())
    require((E,mass,max(H))==(5916300,31346280,50)and m*W-mass==52800,'Changed banked profile')
    require(physical['distinct_charts']==231 and max(physical['max_num'],physical['max_den'])<2**80,'Ineligible bank charts')
    require(physical['conservative_selector_calls']==12227329044<2**40,'Unpaid bank selectors')
    require(all(0<r<m and n>0 for r,n in H.items()),'Nonmonotone moment')
    require(primes['prime_factors']==[2,3,5,7]and primes['all_remaining_factors_below_2_power_80'],'Unverified excluded primes')
    require(finite['primitive_contract']['eligible_prime']=='any fixed odd prime q>2^80','Prime-specific primitive contract')
    require(finite['primitive_contract']['initialization_and_table_scans_charged'],'Unpaid prime-dependent tables')
    proof=(parent/'proof/three-stage-cover-bit.tex').read_text()
    require('bad fraction at most $2m^3/q<10^{-16}$'in proof,'Detached rare-density bound')
    rho=Q(2*m**3,PRIME)
    require(0<rho<Q(1,10**16),'Fallback omitted or no density improvement')
    fallback=[(1,32*m*m*E)]
    def paid(a,density=rho):
        lo,hi=public.moment(H,m,W,a,False)
        l,u=public.logarithm(Q(m));e,f=public.exponential(a*l,a*u)
        bill=density*Q(32*m*E,W)
        return public.floor(lo+bill*e),public.ceil(hi+bill*f)
    def separate(a):
        lo,hi=independent.moment(m,W,list(H.items()),a)
        fl,fu=independent.moment(m,W,fallback,a)
        return lo+rho*fl,hi+rho*fu
    c0=Q(old['bit_coarse_saving']);lo=int(c0*COARSE_GRID);hi=lo+COARSE_GRID//10**8
    require(paid(Q(lo,COARSE_GRID))[1]<1<paid(Q(hi,COARSE_GRID))[0],'Coarse bracket')
    while hi-lo>1:
        mid=(lo+hi)//2;l,u=paid(Q(mid,COARSE_GRID))
        if u<1:lo=mid
        elif l>1:hi=mid
        else:raise ValueError('Inconclusive rational moment enclosure')
    c=Q(lo,COARSE_GRID);excluded=Q(hi,COARSE_GRID)
    pa,pe,ia,ie=paid(c),paid(excluded),separate(c),separate(excluded)
    require(pa[1]<1<pe[0]and ia[1]<1<ie[0],'Independent paid moment bracket')
    require(paid(c,Q(1,10**16))[0]>1,'Improvement does not depend on the certified smaller density')
    base=Q(384599,10**10);b=Q(747454944651775,10**18)
    require(Q(old['ordinary_chain'][0])==base,'Changed completed base supplier')
    require(public.moment({int(r):n for r,n in unbanked['complex_profile']['histogram'].items()},110,14692,b,False)[1]<1,'Complex moment')
    bridge=unbanked['finite_bridge'];bridge['rows']['degree_gap']=Q(bridge['rows']['degree_gap'])
    eta=Q(1,10**12);beta=Q(1,10**9)
    def assemble(a,grid=GRID):
        require(a<(1-beta)*b,'Complex cap became active')
        z=a*(1-2*eta);bound=(1-eta)*z/(1+z);k=point(bound,grid)
        result=outer.assembly(a,b,bridge,k,eta=eta,beta=beta)
        require(len(result['strict_constraints'])==47 and len(result['margins'])==7,'Incomplete outer assembly')
        require(all(v>0 for v in result['strict_constraints'].values())and all(v>k for v in result['margins'].values()),'Non-strict outer inequalities')
        try:outer.assembly(a,b,bridge,k+Q(1,grid),eta=eta,beta=beta)
        except AssertionError:pass
        else:raise ValueError('Adjacent kappa point admitted')
        return dict(kappa=k,bound=bound,assembly=result)
    chain=[base];steps=[]
    for j in range(1,DEPTH+1):
        old_a=chain[-1];a=(1-c)*c+c*old_a;gaps=validate_step(j,j-1,c,old_a,a)
        require(a==c-c**j*(c-base),'Recurrence mismatch')
        delta=min(gaps.values());L=cutoffs.cutoff_log2(delta,1)
        require(L*delta**2>=36 and L*delta>=8,'Cutoff arithmetic')
        steps.append(dict(level=j,ordinary_predecessor=j-1,saving=a,gaps=gaps,
            minimum_gap=delta,cutoff_log2_at_C_equals_1=L))
        chain.append(a)
    result=assemble(chain[-1]);previous=assemble(Q(old['ordinary_chain'][-1]))
    require(assemble(Q(old['ordinary_chain'][-1]),10**18)['kappa']==Q(old['kappa']),'Published comparator')
    require(result['kappa']>previous['bound'],'No genuine improvement over unrounded parent')
    sixth=assemble(chain[6]);third=assemble(chain[3])
    require(result['kappa']>sixth['kappa'],'Seventh level does not improve reported grid')
    require(result['kappa']==assemble(c)['kappa']==assemble(excluded)['kappa'],'Not at this paid family grid cap')
    delta1=1-Q(mass,m*W)-rho*Q(32*m*E,W)
    require(delta1>0 and 1-pa[1]>0,'Recurrence contraction gap')
    require(finite['paid_inventory']['fallback_children']==32*m*m,'Fallback count changed')
    base_coefficient=finite['q_power_bound']['coefficient']
    require(base_coefficient==1568901757016837,'Changed base q-power bill')
    # Pay twelve copies of every original charge plus an intentionally excessive
    # per-selector wrapper/high-affine/stock/matrix-preparation bill for new banks.
    d=m*m;N=2*m;K=physical['conservative_selector_calls']
    per_selector=16*(d+1)**2+(W+12*24)+128*N**3+(8*m*m+8)+1
    # Also overcharge every original routing family against the entire enlarged
    # bank role set, instead of relying on a per-copy stock accounting shortcut.
    enlarged_role_charge=12*208670*(W+12*24)
    coefficient=12*base_coefficient+enlarged_role_charge+K*per_selector
    require(coefficient<2**80<PRIME,'Invalid banked q-power overcharge')
    controls=[]
    for name,j,pred,a in [('cyclic supplier',DEPTH,DEPTH,chain[-1]),('unattained coarse ordinary leaf',DEPTH,DEPTH-1,c)]:
        try:validate_step(j,pred,c,chain[-2],a)
        except ValueError:controls.append(name)
        else:raise ValueError('Invalid supplier admitted')
    # An omitted or larger rare density may not be substituted into the published certificate.
    corrupted=prime['residues'][:];corrupted[37]+=1
    require(any(corrupted[i+1]!=(corrupted[i]**2-2)%PRIME for i in range(125)),'Corrupt prime residue accepted')
    controls.extend(['corrupt Lucas-Lehmer residue','old-density paid moment at new coarse point','adjacent coarse and kappa grid points'])
    return serial(dict(schema='fixed-prime-bootstrap/1',scope='Conditional on the unchanged PR234 all-size and symbolic interfaces',
        prime=prime,rare_density=rho,depth=DEPTH,coarse_grid=COARSE_GRID,kappa_grid=GRID,
        banked_profile=old['bit_profile'],bank_physical=physical,
        coarse=c,excluded_coarse=excluded,public_accepted=pa,public_excluded=pe,
        independent_accepted=ia,independent_excluded=ie,fallback_histogram=fallback,
        delta_linear=delta1,delta_tau_lower=1-pa[1],ordinary_chain=chain,steps=steps,
        eta=eta,beta=beta,complex_saving=b,kappa=result['kappa'],kappa_decimal=public.decimal(result['kappa']),
        parent_published_kappa=Q(old['kappa']),parent_matched_kappa=previous['kappa'],parent_unrounded_bound=previous['bound'],
        gain=result['kappa']-Q(old['kappa']),matched_gain=result['kappa']-previous['kappa'],
        refined_three_level_kappa=third['kappa'],six_level_kappa=sixth['kappa'],seventh_level_gain=result['kappa']-sixth['kappa'],
        assembly=result['assembly'],minimum_margin=result['bound'],paid_family_grid_cap_attained=True,
        primitive_contract=finite['primitive_contract'],original_per_copy_paid_inventory=finite['paid_inventory'],
        bank_extra_selector_calls=K,banked_physical_stock_role_upper=W+12*24,
        q_power_bound=dict(coefficient=coefficient,low_matrix_power=14400,strict_upper='q^14401',
            original_copies=12,original_coefficient=base_coefficient,
            enlarged_role_charge=enlarged_role_charge,per_selector_coefficient=per_selector,
            toll='C_primitive(q,source,j)*(1+B(q))*(n+w^(1-a_previous))'),
        cutoff=finite['finite_cutoff'],row_reserve=finite['row_reserve'],controls=controls))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--parent-root',type=Path,required=True)
    p.add_argument('--banks-root',type=Path,required=True)
    p.add_argument('--write',action='store_true');args=p.parse_args()
    require(not sys.flags.optimize,'Run without -O')
    own=None if args.write else inventory(HERE,'SOURCE.json')
    prerequisite=json.loads((HERE/'prerequisite.json').read_text());root=args.parent_root.resolve()
    require(subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()==prerequisite['commit'],'Wrong parent commit')
    parent=root/'research/five-stage-source-bound-v8'
    require(digest(parent/'MANIFEST.json')==prerequisite['manifest_sha256'],'Parent manifest drift')
    before=inventory(parent,'MANIFEST.json')
    banks_root=args.banks_root.resolve();banks_package=banks_root/'research/five-stage-banks'
    require(subprocess.check_output(['git','-C',str(banks_root),'rev-parse','HEAD'],text=True).strip()==prerequisite['banks_commit'],'Wrong bank commit')
    def bank_inventory():
        actual={p.relative_to(banks_package).as_posix():digest(p)for p in banks_package.rglob('*')if p.is_file()}
        require(actual==prerequisite['banks_files'],'Bank source drift');return actual
    banks_before=bank_inventory()
    with tempfile.TemporaryDirectory(prefix='fixed-prime-')as tmp:
        fresh=Path(tmp)/'fresh'
        print('Replaying all six immutable parent stages.',flush=True)
        subprocess.run([sys.executable,'-B',str(parent/'verify.py'),'--output',str(fresh)],check=True)
        result=arithmetic(parent,fresh,banks_root)
    require(inventory(parent,'MANIFEST.json')==before,'Parent mutation')
    require(bank_inventory()==banks_before,'Bank source mutation')
    result['prerequisite']=prerequisite
    if args.write:(HERE/'certificate.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:
        require(result==json.loads((HERE/'certificate.json').read_text()),'Certificate mismatch')
        require(inventory(HERE,'SOURCE.json')==own,'Own source changed')
    print('PASS kappa='+result['kappa']+' = '+result['kappa_decimal'],flush=True)
if __name__=='__main__':main()
