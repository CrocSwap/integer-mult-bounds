"""Exact independent-stage QUERY rank and paid-mask obstruction."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys

PINS = {
    'EFREE-CALLER.json.gz': '757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b',
    'check.py': '460ed9a77d66264b00c31d0a7f8dab1db9aab21ec4cc0eaf0452bd4be4ef585e',
    'retained/inputs/independent_interval.py': '9293f567aa4afd9b4e618f1cddd3cf66eea51c5e194e3c578e7a8f4db6e04a57',
}
KAPPA = Fraction('.0040075385047236')


def checked(package, relpath):
    raw = (package/relpath).read_bytes()
    assert sha256(raw).hexdigest() == PINS[relpath]
    return raw


def load(package, relpath):
    checked(package,relpath)
    path = package/relpath
    spec = spec_from_file_location(path.stem,path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def dot(a,b):
    return (a & b).bit_count() % 2


def rank(rows):
    pivots = {}
    for row in rows:
        while row and row.bit_length()-1 in pivots:
            row ^= pivots[row.bit_length()-1]
        if row:
            pivots[row.bit_length()-1] = row
    return len(pivots)


def outer_sum(terms, n, mask):
    result = [0]*n
    for u,v in terms:
        while u:
            bit = u & -u
            result[bit.bit_length()-1] ^= v & mask
            u ^= bit
    return result


def audit(events, diagonal, dimension):
    n = len(diagonal)
    mask = (1<<n)-1
    prefix = [1<<i for i in range(dimension)]
    inverse = prefix[:]
    stages = defaultdict(list)
    local_terms = defaultdict(list)
    q = []
    for i,(op,*args) in enumerate(events):
        if op == 'SWAP':
            a,b = args
            prefix[a],prefix[b] = prefix[b],prefix[a]
            inverse[a],inverse[b] = inverse[b],inverse[a]
            continue
        if op == 'IDLE_ONE':
            a,serving = args
            assert len(serving) == len(set(serving))
            for s in serving:
                stages[s].append([(inverse[a],prefix[a])])
            continue
        if op == 'LOCAL':
            s,src,dst = args
            stages[s].append([(inverse[src],prefix[src]),(inverse[dst],prefix[dst])])
            local_terms[s].append((i,inverse[dst],prefix[src]))
        else:
            assert op in ('QUERY','ADD')
            dst,src = args
        assert src != dst
        if op != 'ADD':
            q.append((inverse[dst],prefix[src]))
        prefix[dst] ^= prefix[src]
        inverse[src] ^= inverse[dst]
    assert all(dot(v,u)==(i==j) for i,v in enumerate(prefix) for j,u in enumerate(inverse))
    target = [1<<i if i<n else 0 for i in range(dimension)]
    assert [v & mask for v in prefix] == target
    assert all(d['q']==1 for d in diagonal)
    q_delta = rank([a^b for a,b in zip(outer_sum(q,dimension,mask),target,strict=True)])
    gram = [(1<<i)^sum(dot(v & mask,u2)<<j for j,(u2,_) in enumerate(q))
            for i,(_,v) in enumerate(q)]
    stage_data, failures = [],[]
    for s in range(1,19):
        expected = [1<<i if i<n and s in diagonal[i]['stages'] else 0 for i in range(dimension)]
        terms = [t for p in stages[s] for t in p]
        observed = outer_sum(terms,dimension,mask)
        if observed != expected:
            failures.append([s,rank([a^b for a,b in zip(observed,expected,strict=True)])])
            continue
        assert rank(expected) == len(terms)
        assert all(u & ~mask == 0 for u,_ in terms)
        for first,second in combinations(stages[s],2):
            assert all(dot(u,v2)==dot(u2,v)==0 for u,v in first for u2,v2 in second)
        pair = local_terms[s]
        assert len(pair)==2
        assert all(dot(u,v)==0 for _,u,_ in pair for _,_,v in pair)
        stage_data.append(dict(stage=s,rank=rank(expected),body_incidence=len(terms),
                               local_events=[x[0] for x in pair],local_defect_minor_rank=2))
    return dict(dimension=dimension,q_terms=len(q),q_target_delta_rank=q_delta,
                compressed_q_defect_rank=rank(gram),stage_controls=stage_data,stage_failures=failures)


def subtract(a,b):
    return a[0]-b[1],a[1]-b[0]


def price(events, interval):
    original = Counter(7*len(e[2]) for e in events if e[0]=='IDLE_ONE')
    demands = Counter(s for e in events if e[0]=='IDLE_ONE' for s in e[2])
    assert original == {7*i:4 for i in range(1,9)}
    base = interval.moment(original,1-KAPPA)
    profiles = []
    for s in range(1,19):
        needed = demands.copy()
        needed[s] += 1
        packed = [7*sum(c>=j for c in needed.values()) for j in range(1,max(needed.values())+1)]
        delta = subtract(interval.moment(Counter(packed),1-KAPPA),base)
        assert delta[0] > 4
        profiles.append(dict(stage=s,nested_ranks=packed,added_paid_per_port=interval.bounds_text(delta)))
    return dict(original_idle_histogram=original,minimum_extra_incidence_profiles=profiles,
                maximum_query_rebate_per_port=4)


def run(package):
    caller = json.loads(gzip.decompress(checked(package,'EFREE-CALLER.json.gz')))
    forward = load(package,'check.py')
    interval = load(package,'retained/inputs/independent_interval.py')
    events,diagonal = caller['events'],caller['diagonal']
    assert (caller['roles'],caller['ports'],caller['stages']) == (38,111,18)
    base = audit(events,diagonal,38)
    assert base['q_terms']==40 and base['q_target_delta_rank']==0 and base['compressed_q_defect_rank']==2
    assert len(base['stage_controls'])==18 and not base['stage_failures']
    literal = forward.forward(caller)
    assert literal == 38**2

    mutated = [e[:] for e in events]
    query = next(i for i,e in enumerate(events) if e[0]=='QUERY')
    mutated[query][0] = 'ADD'
    q_control = audit(mutated,diagonal,38)
    assert q_control['q_target_delta_rank']==1 and not q_control['stage_failures']

    mutated = [e[:] for e in events]
    idle = next(e for e in mutated if e[0]=='IDLE_ONE')
    omitted = idle[2][0]
    idle[2] = idle[2][1:]
    body_control = audit(mutated,diagonal,38)
    assert body_control['q_target_delta_rank']==0 and body_control['stage_failures']==[[omitted,1]]

    local = next(i for i,e in enumerate(events) if e[0]=='LOCAL')
    _,s,a,b = events[local]
    padded = [*events[:local],['SWAP',a,38],['LOCAL',s,38,b],['SWAP',a,38],*events[local+1:]]
    _,d,c = events[query]
    padded[query+2:query+3] = [['SWAP',d,39],['QUERY',39,c],['SWAP',d,39]]
    h = audit(padded,diagonal,40)
    assert h['q_target_delta_rank']==0 and h['compressed_q_defect_rank']==2 and not h['stage_failures']
    return dict(status='EXACT_BIT_STAGE_QUERY_AND_MASK_PRICE',dependencies=PINS,target=str(KAPPA),
                exact_original_polynomial_coefficients=literal,baseline=base,
                query_phase_control_rank=q_control['q_target_delta_rank'],
                body_incidence_control=body_control['stage_failures'],
                helper_padding_control=dict(dimension=40,stage_checks=len(h['stage_controls']),q_defect_rank=2),
                price=price(events,interval))


if __name__ == '__main__':
    if not __debug__ or sys.implementation.name != 'cpython' or sys.version_info[:2] != (3,12):
        raise RuntimeError('Use CPython 3.12 with assertions enabled')
    package = Path(__file__).resolve().parent
    source = Path(sys.argv[1]) if len(sys.argv) == 2 else package.parent / 'paired-query-only-bit'
    receipt = json.dumps(run(source), indent=2, sort_keys=True) + '\n'
    if receipt.encode() != (package / 'RECEIPT.json').read_bytes():
        raise ValueError('exact stage/query receipt mismatch')
    print('PASS_BIT_LOCAL_QUERY_RANK_BOUND')
