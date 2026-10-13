"""Direct selected-XOR via diagonal phases: exact identity and cost screen.

Douglas Colkitt, with OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(ROOT/'research/kappa-nine'))
from target_budget import encode


def require(condition,message):
    if not condition:raise AssertionError(message)


def walsh(values,bits):
    """Unnormalized W along physical binary address positions; integer pairs."""
    out=list(values)
    for bit in bits:
        step=1<<bit
        for start in range(0,len(out),2*step):
            for j in range(start,start+step):
                a,b=out[j],out[j+step]
                out[j]=(a[0]+b[0],a[1]+b[1])
                out[j+step]=(a[0]-b[0],a[1]-b[1])
    return out


def phase(values,pairs):
    return [((-a,-b) if sum(((i>>x)&1)*((i>>y)&1) for x,y in pairs)%2 else (a,b))
            for i,(a,b) in enumerate(values)]


def divide(values,power):
    divisor=1<<power
    require(all(a%divisor==b%divisor==0 for a,b in values),'exact final Gaussian-integer division')
    return [(a//divisor,b//divisor) for a,b in values]


def direct_selected_xor(values,pairs):
    """2^-f W_target D_source,target W_target, with no address swaps."""
    targets=[y for _,y in pairs]
    return divide(walsh(phase(walsh(values,targets),pairs),targets),len(pairs))


def address_selected_xor(values,pairs):
    out=[None]*len(values)
    for i,value in enumerate(values):
        target=i
        for x,y in pairs:target ^= ((i>>x)&1)<<y
        require(out[target] is None,'address bijection')
        out[target]=value
    return out


def twice_c(values,mask):
    """2 C_v = (1+i)I + (1-i)X_v, on Gaussian integer pairs."""
    out=[]
    for i,(ar,ai) in enumerate(values):
        br,bi=values[i^mask]
        out.append((ar+br-ai+bi,ai+bi+ar-br))
    return out


def fused_direction(values,bits):
    """A genuine local Hadamard cancellation; still too many child widths.

    For pivot p and J=bits minus {p}: C_v=H_J D C_p D H_J,
    D=(-1)^(x_p sum_{j in J}x_j). Test numerator 2*C_v exactly.
    """
    p,*others=bits
    pairs=[(p,j) for j in others]
    stage=walsh(values,others)
    stage=phase(stage,pairs)
    stage=twice_c(stage,1<<p)
    stage=phase(stage,pairs)
    return divide(walsh(stage,others),len(others))


def operator_checks():
    trials=[]
    # Extra physical positions are untouched gaps, prefix/suffix, and dirty fields.
    for width,pairs in [(5,[(4,1)]),(9,[(7,1),(8,3)]),(12,[(8,1),(10,3),(11,5)]),
                        (9,[(1,7),(3,8)])]:
        values=[((i*37)%101-50,(i*i+3*i)%97-48) for i in range(1<<width)]
        got=direct_selected_xor(values,pairs)
        want=address_selected_xor(values,pairs)
        require(got==want,'direct selected-XOR exact arbitrary payload control')
        trials.append(dict(address_bits=width,pairs=pairs,records=len(values),equal=True))
    for width,bits in [(4,[0,2]),(6,[0,2,5]),(10,[0,1,2,3,4,5,6,7,8])]:
        values=[(i%11-5,i%7-3) for i in range(1<<width)]
        require(fused_direction(values,bits)==twice_c(values,sum(1<<b for b in bits)), 'fused directional identity')
        trials.append(dict(address_bits=width,directional_bits=bits,records=len(values),equal=True))
    return trials


def budget():
    path=ROOT/'certificates/copied-centers-network.json'
    cert=json.loads(path.read_text());c=cert['complex']['counts']
    pinned=json.loads((ROOT/'research/kappa-nine/baseline/certificate.json').read_text())['finite_bridge']['complex']
    m,W,N,L,s=(c[k] for k in ('m','W','N','L','total_rank'))
    require((m,W,s)==(pinned['m'],pinned['W'],pinned['s']),'same pinned complex network')
    rows={int(t):n for t,n in c['child_multiplicities'].items()}
    require(sum(t*n for t,n in rows.items())==s,'existing mass')
    deficit=W*m-s
    require(deficit==N-L==5778864,'copied-center deficit')
    # In the literal standard tensor coordinates, endpoint u=triple tensor triple
    # has support weight nine. Retain every other old call and grant free setup.
    weight=9
    additions={'one_extra_unit_child_per_endpoint':N,
        'coordinate_mobility_lower_bound':(weight-1)*N,
        'fused_hadamard_schedule':2*(weight-1)*N,
        'unfused_row_addition_schedule':4*(weight-1)*N}
    screens={name:dict(added_rank_mass=added,linear_exponent_moment=Q(s+added,W*m),
        exceeds_linear_budget=s+added>W*m,ratio_to_available_slack=Q(added,deficit))
        for name,added in additions.items()}
    require(all(x['exceeds_linear_budget'] for x in screens.values()),'all specified substitutions fail at exponent one')
    return dict(m=m,W=W,N=N,L=L,s=s,rank_slack=deficit,endpoint_support_weight=weight,
        extra_unit_child_allowance_per_endpoint=Q(deficit,N),
        row_addition_allowance_if_two_unit_children_each=Q(deficit,2),
        screens=screens,
        scope='Local standard-coordinate endpoint replacement on each complete original role/copy stream; other old calls retained. Does not cover a paid global basis change with cross-residual reuse, new volume splitting, or a redesigned whole network.')


def audit():
    source_paths=['upstream/build/sections/02-streams.tex','upstream/build/sections/05-layers.tex',
        'notes/compact-control-movement.tex','notes/compact-control-layout.tex',
        'notes/copied-centers-complex.tex','docs/research/coded-carry-audit.md',
        'certificates/copied-centers-network.json','research/kappa-nine/baseline/certificate.json',
        'research/direct-selected-xor/audit.py']
    return dict(status='EXACT OPERATOR SPECIALIZATION; NO FASTER TAPE ALGORITHM CERTIFIED',
        operator_trials=operator_checks(),budget=budget(),
        identities=['selected XOR = 2^(-f) W_target D W_target',
                    'C_v = H_J D C_p D H_J, J=support(v) minus pivot'],
        independent_basis_test_command="python3 -m unittest discover -s research/direct-selected-xor -p 'test_*.py' -v",
        new_exponent_claimed=False,finite_construction_selected=False,
        source_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths})


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);args=parser.parse_args()
    result=audit()
    if args.output:args.output.write_text(json.dumps(encode(result),indent=2,sort_keys=True)+'\n')
    print('PASS exact selected-XOR and fused directional phase identities')
    print('Extra unit-child allowance per endpoint:',result['budget']['extra_unit_child_allowance_per_endpoint'])
    for name,row in result['budget']['screens'].items():
        print(name,'mass / capacity =',float(row['linear_exponent_moment']))
    print('No improved time bound or kappa; literal local substitution fails.')
