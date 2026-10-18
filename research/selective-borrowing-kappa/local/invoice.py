"""Fresh conservative finite invoice from actual local words and owner table.

Retains the existing m=73 chart compiler and finite cover/row conventions, but
recounts the new program, all scratch and exact fine-grid magnitude/depth guards.
The separate optional rounding envelope is not an inherited child premise.
"""
import argparse
import gzip
import hashlib
import json
import sys
from collections import Counter,defaultdict
from fractions import Fraction as Q
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from precision import calculate,expanded

def need(condition,label):
    if not condition:raise ValueError(label)

def scalar_count(trace):
    counts=Counter();real=work=0;macros=0
    for event in expanded(trace['events']):
        kind=event[0];counts[kind]+=1
        if kind=='add':
            q=Q(event[3]);a,b=abs(q.numerator),q.denominator
            need(a>0 and b&(b-1)==0,'dyadic ADD coefficient')
            count=3+(a.bit_length()-1)+a.bit_count()+(b.bit_length()-1)
            work+=count;macros+=1;real+=2*count
        elif kind=='scale':
            q=Q(event[2]);a,b=abs(q.numerator),q.denominator
            need(a>0 and a&(a-1)==0 and b&(b-1)==0,'dyadic unit SCALE')
            count=abs(a.bit_length()-b.bit_length())+int(q<0)
            macros+=1;real+=2*count
        elif kind in ('copy','clear','zero_buffer'):
            macros+=1;real+=2
    # Explicit post-call exact clears make the private-zero return literal even
    # for approximate recursive children. They preserve the ideal word endpoint.
    postlude_clears=len(trace['zero_buffers'])+1
    real+=2*postlude_clears;macros+=postlude_clears
    return dict(expanded_event_counts=dict(counts),scalar_macros=macros,
                real_component_primitives=real,coefficient_work_primitives=work,
                extra_exact_private_postlude_clears=postlude_clears,
                conservative_macro_envelope=sum(counts.values())+postlude_clears)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--variant',type=Path,required=True)
    parser.add_argument('--owners',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();words={};local={};bindings={}
    for orientation in ('forward','backward'):
        p=args.variant/(orientation+'.json');words[orientation]=json.loads(p.read_bytes())
        local[orientation]=scalar_count(words[orientation]);local[orientation]['precision']=calculate(words[orientation])
        bindings[orientation+'_word_sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
    raw=args.owners.read_bytes();owners=json.loads(gzip.decompress(raw) if args.owners.suffix=='.gz' else raw)
    groups=defaultdict(list)
    for row in owners:groups[row['stage'],row['replica']].append(row)
    helpers=len(words['forward']['helper_widths']);expected_helpers=set(map(int,words['forward']['helper_widths']))
    need(helpers==436,'selected fixed 44-alias variant')
    need(set(groups)=={(stage,replica) for stage in range(9) for replica in range(8)},'all actual stage/replica calls')
    for rows in groups.values():
        need(len(rows)==helpers and {r['helper'] for r in rows}==expected_helpers,'actual new physical helper roles')
    calls=len(groups);replicas=8;bridges=9*replicas;m=73;v=112
    # Eight original private centre reserves safely cover the one COPY buffer;
    # retain all 492 old local-helper reserves and add all 75 cleanup buffers.
    live=896*replicas;retained_helper_reserve=492
    cleanup_buffers=max(len(w['zero_buffers']) for w in words.values())
    need(cleanup_buffers==75,'actual simultaneous FULL cleanup reserve')
    centres,coefficient_work=8,2
    physical=live+retained_helper_reserve+cleanup_buffers+centres+coefficient_work
    n=2*v+helpers+cleanup_buffers+1+coefficient_work
    compiler=64*(m+1)**3
    children=sum(words['forward']['local_profile'].values())
    need(words['forward']['local_profile']==words['backward']['local_profile'],'same true paid profile')
    macro_bound=max(x['conservative_macro_envelope'] for x in local.values())
    adapters=16*(macro_bound+children+n+centres)+64*m
    primitive=max(x['real_component_primitives'] for x in local.values())+adapters*compiler
    local_guard=max(x['precision']['local_sufficient_guard_bits'] for x in local.values())
    block_count=calls+bridges
    summation_bits=(block_count-1).bit_length()
    input_sup_to_l2_bits=(m+1)//2
    coordinate_defect_to_l2_bits=(m+1)//2
    optional_rounding_guard=local_guard+2*block_count+summation_bits+3+input_sup_to_l2_bits+coordinate_defect_to_l2_bits
    ideal_local_bits=max(x['precision']['P_binary_upper'] for x in local.values())
    global_guard=ideal_local_bits+block_count+input_sup_to_l2_bits
    payload=512
    # Endpoint-normalized data calls and bridge shears have stream-Hilbert
    # operator norm <=2; helpers are content-independent unitary residuals.
    # Thus P<=2^B, K<=B*2^B for B completed blocks. Applying the same feedback
    # argument to the local guard gives the following deliberately coarse bill.
    wrapper_count=2*helpers+2*v
    wrapper_factors=calls*wrapper_count*2*(m-1)
    bridge_additions=2*v*bridges
    shifts=4*v*replicas;moves=2*shifts
    outside_items=(6*calls*n+m*live+bridge_additions+shifts+moves+live+physical+wrapper_factors)
    outside=8*outside_items+64*m
    orientation_counts=Counter('forward' if stage%2==0 else 'backward' for stage,replica in groups)
    scalar=sum(orientation_counts[o]*local[o]['real_component_primitives'] for o in local)
    pervertex=scalar+bridge_additions+shifts+moves+live+(calls*adapters+outside)*compiler+64*physical
    half=m//2;group=2**(half*half)
    for j in range(1,half+1):group*=2**(2*j)-1
    stock=group*physical;logical=group*pervertex+64
    router=compiler*(logical+1)*(stock+1)**2
    # Source-independent mass overcharge: actual admitted profiles have positive
    # deficit and therefore no more than m*live total paid rank.
    streamed_mass=group*m*live
    G,E,C0=2**30000,2**100000,2**210000
    literal=2*G*stock**2+8*streamed_mass+4*stock+4+32*m
    total_mass=streamed_mass+E
    row=2*stock.bit_length()+9909+252+2*payload
    checks=dict(local_primitive_bound=primitive<2**48,logical=logical<2**6050,
                router=router<G,literal=literal<E,mass=total_mass<2**100001,
                precision=32*m*total_mass*total_mass<C0,tape=2*total_mass+18<C0,
                row=row<20161,global_payload=global_guard<payload)
    need(all(checks.values()),('finite reserve failure',checks))
    output=dict(status='PASS_FRESH_CONSERVATIVE_FINITE_INVOICE_UNDER_RETAINED_INTERFACES',
        local=local,actual_roles=len(owners),actual_calls=calls,orientation_counts=dict(orientation_counts),
        helper_count=helpers,private_cleanup_buffers=cleanup_buffers,owned_private_fields=cleanup_buffers+1,
        physical_stock_identity=dict(live=live,retained_local_helper_reserve=retained_helper_reserve,
                                    cleanup_buffers=cleanup_buffers,private_centres=centres,coefficient_work=coefficient_work),
        physical_families=physical,n_including_owned_private_and_coefficient_work=n,
        compiler=compiler,local_adapters=adapters,local_primitive_bound=primitive,
        global_precision_guard_coefficient=global_guard,charged_payload_coefficient=payload,
        precision_units='Payload512 is a per-lambda magnitude coefficient, not a fixed bit count. Exact recursive children return Gaussian dyadics without intermediate rounding. Common denominator/magnitude excess is charged separately by C0*d.',
        exact_magnitude_guard=dict(ideal_local_bits=ideal_local_bits,completed_blocks=block_count,
             initial_sup_to_hilbert_per_lambda=input_sup_to_l2_bits,
             sufficient_inequality=f'{ideal_local_bits+block_count} + {input_sup_to_l2_bits}*lambda <= {global_guard}*lambda < {payload}*lambda for integer lambda>=1'),
        exact_fine_grid_contract=dict(completed_child='C_r tensor powers are exact, with Gaussian dyadic denominators 2^(r*f) and coordinate row-sum at most 2^(r*f). No intermediate child rounding.',
             active_depth_recurrence='A(e)<=A(rmax*floor(e/73))+s*floor(e/73)+E; for rmax<=72 and B=s+E>=8, A(e)<=2*B*e.',
             outer_common_excess='(2*B+18)*d < 32*73*B^2*d; use Delta=ceil(C0*d) with C0=2^210000.',
             literal_scope='Fresh literal charge includes every dyadic Horner primitive, private clear, monomial wrapper and route; native monomials introduce only unit Gaussian phases.'),
        optional_rounding_robustness=dict(global_guard_coefficient=optional_rounding_guard,
             scope='Separate sufficient feedback implication only, conditional on the explicit local Hilbert-defect contracts in precision receipts. It is not the inherited exact child contract and is not needed for the exact finite invoice.'),
        wrapper_elementary_factors=wrapper_factors,actual_recounted_real_primitives=scalar,
        conservative_outside_items=outside_items,conservative_pervertex=pervertex,
        finite=dict(group_bits=group.bit_length(),physical_stock_bits=stock.bit_length(),
                    logical_bits=logical.bit_length(),router_bits=router.bit_length(),literal_bits=literal.bit_length(),
                    physical_row_coefficient=row,retained_row_coefficient=20161,
                    required_C0_bits=(32*m*total_mass*total_mass).bit_length(),C0_exponent=210000),
        strict_checks=checks,source_bindings=bindings,
        owner_table_sha256=hashlib.sha256(raw).hexdigest(),
        inherited_conventions='m=73 cover order, chart compiler64*(m+1)^3, elementary route/family-selection bound, row9909+252, G=2^30000, E=2^100000, C0=2^210000',
        scope='Fresh source-bound finite upper charges. All-size compiler, exact Gaussian-dyadic completed-child interface with active-depth common exponent, tape/route realization and analytic transfer remain inherited premises. Owner capacity/chronology/axes admission and exact moment/outer assembly are separate checked artifacts.')
    args.out.write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(output['status'],'physical',physical,'guard',global_guard,'row',row,'primitive_bits',primitive.bit_length())

if __name__=='__main__':main()
