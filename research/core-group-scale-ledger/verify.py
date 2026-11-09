"""Bounded exact controls for the source-specific scale/precision lemma."""
import argparse
from fractions import Fraction as Q
from itertools import product
import json
from pathlib import Path
from ledger import need, power2, ceil_log2, scale_policy, diagonal_gate, common_budget, hole_schedule, trunc_grid
from sources import authenticate, bridge, hole_geometry, source_sites, REFERENCE, OUTER, GAUSSIAN, BRIDGE


def min_terms(gap, u, bound):
    if gap == 1:
        return 1
    def good(j):
        return (1-gap)**j/(power2(u)*gap) <= bound
    hi=1
    while not good(hi): hi*=2
    lo=0
    while hi-lo>1:
        mid=(hi+lo)//2
        if good(mid): hi=mid
        else: lo=mid
    return hi


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--emit',action='store_true');cli=parser.parse_args()
    raw=authenticate();retained=bridge(raw);sites=source_sites(raw)
    Geometry,ast_hash=hole_geometry(raw);controls=[]
    def reject(name,action):
        try: action()
        except ValueError: controls.append(name)
        else: raise ValueError('adverse case accepted: '+name)

    hole_entries=0;hole_fixtures=[]
    for s,e in ((7,1),(13,3),(29,3)):
        ref=Geometry({},s,e,1,1,1,8)
        selected={j+(2*e*j+s)//(2*s) for j in range(s)}
        holes=[k for k in range(s+e) if k not in selected]
        need(holes==[k for k in range(s+e) if ref.source_at.get(k) is None],'literal hole coordinates')
        for r,c in product(range(s+e),repeat=2):
            if r in holes or c in holes:
                entry=ref._narrow(r,c)
                need(entry.kind=='hole-identity' and entry.value==Q(r==c),'original identity-hole branch')
                hole_entries+=1
        hole_fixtures.append({'source':s,'excess':e,'holes':holes})

    scale_cases=0
    for count in range(1,5):
        for us in product(range(3),repeat=count):
            for rs in product(range(2),repeat=count):
                ks=tuple(u+r for u,r in zip(us,rs))
                for gamma,policy in product((0,sum(ks)+2),('spend_existing','add_new')):
                    plan=scale_policy(us,ks,gamma,policy)
                    endpoint=power2(plan['restoration_bits']);target=power2(gamma)
                    for u,r,k in zip(us,plan['remaining_bits'],ks):
                        endpoint/=(1 << u)*(1 << r);target/=1 << k
                    need(endpoint==target,'complete policy endpoint');scale_cases+=1

    # Independent single integer quotient, rather than staged Fraction rounding.
    grid_cases=0
    for us,rs in product(product(range(4),repeat=2),product(range(3),repeat=2)):
        ks=tuple(u+r for u,r in zip(us,rs));gamma=sum(ks)
        for policy in ('spend_existing','add_new'):
            total_drop=sum(ks)+(sum(us) if policy=='add_new' else 0)
            restore=gamma+(sum(us) if policy=='add_new' else 0)
            for q,v in product(range(2,total_drop+4),range(-7,8)):
                got,_=hole_schedule(Q(v,4),us,ks,gamma,policy,q)
                num=abs(v)*(1 << (q-2))//(1 << total_drop)
                expect=Q((-1 if v<0 else 1)*num*(1 << restore),1 << q)
                need(got==expect,'independent signed-grid oracle');grid_cases+=1
    vanished,trace15=hole_schedule(1,(8,8),(8,8),16,'spend_existing',15)
    survived,_=hole_schedule(1,(8,8),(8,8),16,'spend_existing',16)
    need(vanished==0 and survived==1 and trace15[0][0]==Q(1,256),'cumulative pre-extraction loss')
    controls.append('individual_group_grid_does_not_fund_total')
    # Apply actual selected addresses to complete natural-coordinate fields.
    ref=Geometry({},15,1,1,1,1,8);selected=tuple(ref.selected)
    hole=next(k for k in range(16) if ref.source_at.get(k) is None)
    exact_field=[Q(int(r==hole and c==hole)) for r,c in product(range(16),repeat=2)]
    erased_field=[value*vanished for value in exact_field]
    extracted_exact=[exact_field[16*r+c] for r,c in product(selected,repeat=2)]
    extracted_erased=[erased_field[16*r+c] for r,c in product(selected,repeat=2)]
    need(exact_field!=erased_field and extracted_exact==extracted_erased
         and all(value==0 for value in extracted_exact),'hole control stops before actual extraction')
    controls.append('hole_witness_cannot_claim_extracted_output_failure')
    us,ks,gamma=(2,3),(7,8),15
    correct,_=hole_schedule(1,us,ks,gamma,'spend_existing',32)
    omitted=power2(gamma-sum(ks)-sum(us));doubled=correct*power2(sum(us))
    need(correct==1 and omitted==Q(1,32) and doubled==32,'two scale-policy failures')
    controls+=['extra_normalizers_without_restoration','existing_normalizers_restored_twice']
    reject('overspend_existing_scale',lambda:scale_policy((4,),(3,),0,'spend_existing'))
    reject('underfunded_remaining_diagonal',lambda:diagonal_gate((2,),(3,),(2,)))
    reject('unknown_normalization_policy',lambda:scale_policy((1,),(2,),0,'unnamed'))

    budget_cases=source_calls=zero_tails=max_bits=max_terms=max_grid=0
    for count,radius,tau,gamma,profile in product((1,2,3,5),(1,3,16),(1,8,32),(0,3,40),range(3)):
        z=tau+gamma+ceil_log2(count)+1;eta=power2(-z);specs=[]
        for j in range(count):
            size=1+j%3;group=[]
            for i in range(size):
                u=(profile+i)%3;gap=power2(-u);band=0 if u==0 else 1+i%2
                terms=min_terms(gap,u,eta/(8*radius*size))
                group.append((u,gap,band,terms));max_terms=max(max_terms,terms)
            specs.append(group)
        boundary=max((j-1)*b for group in specs for u,d,b,j in group)+1
        local=ceil_log2(4*boundary+1)
        groups=tuple(tuple(retained.Axis(local+1,b,j,d,u) for u,d,b,j in group) for group in specs)
        n=sum(a.coordinate_bits for group in groups for a in group)+2
        plan=common_budget(groups,radius,tau,gamma);total=Q()
        for group,t in zip(groups,plan['core_targets']):
            spectators=n-sum(a.coordinate_bits for a in group)
            actual=retained.allocation(group,local,boundary,spectators,2*radius,plan['grid_bits'],t)
            need(actual['field_bits']==n,'complete spectator volume')
            need(actual['complete_error_bound']<=eta,'actual bridge exceeds allocation')
            need((2*radius)**2*(1 << n)<=1 << (2*actual['source_radius_bits']),'global Euclidean radius')
            total+=actual['complete_error_bound']+eta
            source_calls+=1;zero_tails+=int(all(a.tail==0 for a in group))
        need(total*power2(gamma)<=power2(-tau),'complete restored budget')
        need(plan['bridge_radius']==2*radius and plan['wrapper_radius']==3*radius,'actual radii')
        need(power2(1-plan['grid_bits'])<=eta/4,'remaining-wrapper rounding')
        budget_cases+=1;max_bits=max(max_bits,n);max_grid=max(max_grid,plan['grid_bits'])
    reject('underfunded_complete_tail',lambda:common_budget(((retained.Axis(8,1,1,Q(1,2),1),),),1,32,10))
    integer_gap=common_budget(((retained.Axis(8,0,1,1,0),),),1,4,0)
    rational_gap=common_budget(((retained.Axis(8,0,1,Q(1),0),),),1,4,0)
    need(integer_gap==rational_gap and all(type(x) is Q for x in integer_gap['row_costs']),
         'integer unit gap must not introduce floating division')

    # State-dependent defects exercise the actual-state induction without
    # assuming linearity of rounded stages. Exact suffix products are separate.
    recurrence_cases=0
    for count,radius,tau,pattern in product(range(1,9),(1,3),(1,4),range(4)):
        eta=power2(-tau-ceil_log2(count)-2);x=y=Q(radius)
        common_q=ceil_log2(1/eta)+3*count+2
        bound=Q();weights=[];increments=[];radius_sum=Q()
        for j in range(count):
            b=Q(1,2) if (j+pattern)%2 else Q(1)
            c=(Q(1),Q(1,2),Q(1,4))[(j+pattern)%3]
            returned=b*x+(eta if x.numerator%3 else -eta)
            x=c*returned+(-eta if returned.numerator%2 else eta);y=c*b*y
            need(all((1 << common_q)%value.denominator==0 for value in (x,y,returned)),
                 'all nonlinear trajectory states share one funded grid')
            increment=c*eta+eta;weights.append(c*b);increments.append(increment)
            bound=c*b*bound+increment;radius_sum+=increment
            need(abs(x-y)<=bound and abs(x)<=radius+radius_sum,'nonlinear actual trajectory')
            need(abs(returned)<=3*radius,'actual wrapper domain')
        independent=Q()
        for i,inc in enumerate(increments):
            term=inc
            for later in weights[i+1:]:term*=later
            independent+=term
        need(bound==independent and bound<=2*count*eta<=power2(-tau),'independent weighted suffix')
        recurrence_cases+=1
    adverse_return=integer_gap['bridge_radius']+Q(1,4)
    need(adverse_return>integer_gap['bridge_radius'] and adverse_return<=integer_gap['wrapper_radius'],
         'wrapper actual-radius control')
    controls.append('wrapper_must_admit_the_returned_state')
    h=Q(1,256);component=3*h/4;lost=2*(component-trunc_grid(component,8))
    need(lost>h and lost<2*h,'both final components round')
    controls.append('missing_wrapper_final_component_rounding')
    need((2**2)*(1 << 20)>2**2,'local radius omits complete volume')
    controls.append('omitted_global_field_volume')

    family_cases=0
    for p in range(2,258):
        l=ceil_log2(p);u=ceil_log2(16*p*p);v=2*l+8;k=100*l
        need(u<=2*l+4 and k-u-v>=96*l-12>0,'dyadic source polynomial budget')
        need(diagonal_gate((u,),(k,),(v,))[0]<=1,'remaining source contraction');family_cases+=1
    for path in (REFERENCE,OUTER,GAUSSIAN,BRIDGE,'retained/bridge/PROOF.md','retained/bridge/NOTICE.md'):
        reject('source_corruption:'+path,lambda path=path:authenticate({path:raw[path]+b'\n# mutation\n'}))
    for action in (lambda:common_budget((),1,1,0),lambda:scale_policy((True,),(2,),0,'spend_existing'),
                   lambda:common_budget(((retained.Axis(8,0,1,Q(1),0),),),0,1,0)):
        reject('invalid_exact_domain',action)
    receipt={'status':'PASS_CORE_GROUP_SCALE_LEDGER','source_sites':sites,'source_hole_ast_sha256':ast_hash,
             'hole_fixtures':hole_fixtures,'literal_hole_entries':hole_entries,'exact_scale_cases':scale_cases,
             'signed_grid_cases':grid_cases,'budget_families':budget_cases,'retained_bridge_allocations':source_calls,
             'zero_tail_groups':zero_tails,'max_field_bits':max_bits,'max_source_terms':max_terms,'max_grid_bits':max_grid,
             'integer_and_rational_unit_gap_agree':True,
             'nonlinear_recurrence_cases':recurrence_cases,'finite_polynomial_budget_cases':family_cases,
             'hole_control':{'q15_return':str(vanished),'q16_return':str(survived),'first_q15_bridge_value':str(trace15[0][0]),
                             'after_extraction_both':'0','extracted_coordinates':len(extracted_exact),
                             'scope':'pre-extraction only; no final-output lower bound'},
             'negative_controls':controls,'no_new_kappa':True,
             'scope':'Source/allocation arithmetic and literal hole branch only; diagonal/native payload execution remain premises.'}
    expected=Path(__file__).with_name('RESULTS.json')
    if not cli.emit:
        need(expected.is_file(),'missing frozen receipt')
        need(receipt==json.loads(expected.read_text()),'frozen scientific receipt changed')
    print(json.dumps(receipt,sort_keys=True));print('PASS_CORE_GROUP_SCALE_LEDGER')


if __name__=='__main__':main()
