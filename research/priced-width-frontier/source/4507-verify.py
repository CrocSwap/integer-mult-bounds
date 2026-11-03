#!/usr/bin/env python3
"""Source-bound exact checks for the chronological batch-width lemma.

Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
The written argument, not these finite checks, supplies the all-rank lemma.
"""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import prod
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from batches import (check_batches, compile_widths, direct_flow, multiplier,
                     require, requirements)

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def integer_record(value):
    return {'bits': value.bit_length(), 'unsigned_big_endian_sha256':
            digest(value.to_bytes(max(1, (value.bit_length()+7)//8), 'big'))}


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def source_check(root=HERE):
    rows = json.loads((root/'VENDOR.json').read_text(encoding='utf-8'))
    for row in rows:
        content = (root/row['path']).read_bytes()
        require(digest(content) == row['sha256'], 'vendored source SHA256')
        blob = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
        require(blob == row['git_blob'], 'vendored Git blob')
    return {row['path']: row['sha256'] for row in rows}


def literal_flow(targets, paid_word, n):
    """Enumerate ordered target words and each chronological paid position.

    This checker uses neither Pascal coefficients nor merged path counts.
    It is bounded to small fixtures, and returns repeated cut batches literally.
    """
    m, kmin = max(targets), min(targets)
    cap, G, power = n//m, 0, 1
    while power*kmin <= cap:
        G += 1
        power *= kmin
    alphabet = [k for k, count in targets.items() for _ in range(count)]
    source, exits, cuts = Counter(), Counter(), []
    unit_count = columns = 0

    def visit(path, rho):
        nonlocal unit_count, columns
        level = G-len(path)
        supplies = Counter(prod(word) for word in product(alphabet, repeat=level)
                           if prod(word)*rho <= cap)
        unit_count += sum(supplies.values())
        columns += sum(rho*c*q for c, q in supplies.items())
        demands = Counter()
        for c, q in supplies.items():
            for k in alphabet:
                demands[c*k] += q
        return supplies, demands

    def run(path, rho, incoming):
        supplies, demands = visit(path, rho)
        for c, q in demands.items():
            require(incoming[c] <= q, 'literal incoming slots')
            source[rho*c] += q-incoming[c]
        for position, r in enumerate(paid_word):
            rr = rho*r
            if len(path) == G:
                waiting = Counter({rr*c: q for c, q in supplies.items()})
            else:
                child_units = Counter(prod(word) for word in product(alphabet, repeat=G-len(path)-1)
                                      if prod(word)*rr <= cap)
                child_demands = Counter()
                for c, q in child_units.items():
                    for k in alphabet:
                        child_demands[c*k] += q
                passed = Counter({c: min(q, child_demands[c]) for c, q in supplies.items()})
                waiting = Counter({rr*c: q-passed[c] for c, q in supplies.items()})
            for rank, count in waiting.items():
                if count:
                    exits[rank] += count
                    cuts.append((len(path), rho, r, rank, count))
            if len(path) < G and rr <= cap:
                run(path+(position,), rr, passed)
    run((), 1, Counter())
    return +source, +exits, Counter(cuts), unit_count, columns


def expect_failure(function, message):
    try:
        function()
    except ValueError as exc:
        require(message in str(exc), 'expected rejection reason: '+message)
        return
    raise ValueError('control was accepted: '+message)


def main_result():
    pins = source_check()
    reference = json.loads((HERE/'vendor/direct-flow-RESULT.json').read_text(encoding='utf-8'))
    native = json.loads((HERE/'vendor/p7-RESULT.json').read_text(encoding='utf-8'))['strictification']['native_inventory']
    parse = lambda h: {int(k): v for k, v in h.items()}
    t7, p7 = parse(native['targets']), parse(native['paid'])
    require(sum(t7.values()) == 7688 and sum(p7.values()) == 55998, 'p7 source census')

    # Match all nine frozen #4436 receipts, not a predecessor evaluator.
    for row in reference['finite_flows']:
        expected = row['flow']
        flow = direct_flow(parse(row['targets']), parse(row['paid']), expected['n'])
        for key in ('sources', 'exits', 'boundary_exits'):
            require(flow[key] == parse(expected[key]), 'frozen '+key)
        for key in ('height', 'units', 'column_mass', 'matched_jobs'):
            require(flow[key] == expected[key], 'frozen '+key)

    literal_count = 0
    for targets, word, ranks in [({2:1,5:1}, [1,4,1], range(5,46)),
                                 ({2:2,3:1}, [2,1,2], range(3,29)),
                                 ({2:1,4:1,8:1}, [1,3,1], range(8,41)),
                                 ({2:4,3:1}, [1]*6+[2]*2, [12])]:
        for n in ranks:
            flow = direct_flow(targets, Counter(word), n)
            ss, ee, cc, uu, qq = literal_flow(targets, word, n)
            compressed = Counter()
            for cut in flow['cuts']:
                compressed[tuple(cut[k] for k in ('depth','rho','paid_rank','rank','count'))] += cut['copies']
            require((flow['sources'], flow['exits'], compressed, flow['units'], flow['column_mass'])
                    == (ss, ee, cc, uu, qq), 'literal chronological cuts')
            literal_count += 1

    # Independently brute-force the least positive integer for two constraints.
    brute_count = 0
    for b1, b2, q1, q2 in product(range(1,9), range(1,9), range(1,7), range(1,7)):
        brute = next(a for a in range(1,b1*b2+1) if a*q1 % b1 == 0 and a*q2 % b2 == 0)
        require(multiplier([b1,b2], [(0,q1),(1,q2)]) == brute, 'exhaustive multiplier minimum')
        brute_count += 1

    outputs = []
    cases = [('strict-overlap', {2:1,5:1}, {1:2,4:1}, 100, reference['exact_toy_compilations'][0]),
             ('source-open-equality', {2:4,3:1}, {1:6,2:2}, 100, reference['exact_toy_compilations'][1]),
             ('raw-p7', t7, p7, 1000, reference['exact_p7_direct_compilation'])]
    compiled = {}
    for name, targets, paid, maximum, expected in cases:
        result = compile_widths(targets, paid, maximum)
        compiled[name] = result
        require(integer_record(result['nested_widths'][-1]) == expected['productive_width'],
                'frozen nested width')
        require(integer_record(result['nested_leaves'][-1]) == expected['paid_rank_one_leaves'],
                'frozen nested leaf count')
        # Check the aggregate rational recurrence separately at every rank.
        rational = [Fraction(n) for n in range(max(targets))]
        for n in range(max(targets), maximum+1):
            f = direct_flow(targets, paid, n)
            cost = (sum(q*rational[n-s] for s,q in f['sources'].items())
                    +sum(q*rational[e] for e,q in f['exits'].items())) / sum(f['sources'].values())
            require(cost == Fraction(result['leaves'][n],result['widths'][n]), 'rational leaf recurrence')
            rational.append(cost)
        outputs.append({'rule': name, 'maximum': maximum, **result['counters'],
                        'width': integer_record(result['widths'][-1]),
                        'nested_width': integer_record(result['nested_widths'][-1]),
                        'leaves': integer_record(result['leaves'][-1]),
                        'width_reduction_factor': integer_record(result['nested_widths'][-1]//result['widths'][-1]),
                        'all_rank_receipt_sha256': digest(canonical(result['rows'])),
                        'normalized_leaf_cost_unchanged': True,
                        'new_width_divides_nested_at_every_rank': True,
                        'first_pooled_failure': result['first_pooled_failure']})

    fail = compiled['source-open-equality']['first_pooled_failure']
    require(fail['n'] == 12 and fail['pooled_multiplier'] == 175
            and fail['chronological_multiplier'] == fail['child_width'] == 700,
            'actual chronology counterexample')
    toy_flow = direct_flow({2:4,3:1}, {1:6,2:2}, 12)
    widths = compiled['source-open-equality']['widths'][:12]
    pooled_rows = requirements(toy_flow,12,pooled_exits=True)
    check_batches(widths, pooled_rows, 175)  # positive: the tempting relaxation passes
    controls = []
    def reject(name, function, message):
        expect_failure(function,message); controls.append(name)
    reject('pooled exit multiplier at actual cut', lambda: check_batches(widths,requirements(toy_flow,12),175), 'whole chronological batch')
    reject('drop a factor from least multiplier', lambda: check_batches(widths,requirements(toy_flow,12),350), 'whole chronological batch')
    reject('zero replication', lambda: check_batches(widths,requirements(toy_flow,12),0), 'positive replication')
    reject('zero supplier width', lambda: multiplier([0],[(0,1)]), 'positive supplier width')
    reject('zero job count', lambda: multiplier([1],[(0,0)]), 'positive batch count')
    reject('negative job count', lambda: multiplier([1],[(0,-1)]), 'positive batch count')
    reject('boolean job count', lambda: multiplier([1],[(0,True)]), 'positive batch count')
    reject('future rank', lambda: multiplier([1],[(1,1)]), 'smaller rank')
    reject('paid rank equal to ambient', lambda: direct_flow({2:1,5:1},{5:1},10), 'strict rank contract')
    reject('noninteger target multiplicity', lambda: direct_flow({2:1.0,5:1},{1:1},10), 'positive integer histogram')
    f = direct_flow({2:1,5:1},{1:2,4:1},20)
    trimmed = f['exits']-f['boundary_exits']
    reject('delete premature exits', lambda: require(sum(s*q for s,q in f['sources'].items())-sum(e*q for e,q in trimmed.items()) == f['column_mass'], 'rank-one conservation'), 'rank-one conservation')
    multiplied = [(c['rank'],c['count']*c['copies']) for c in toy_flow['cuts']]
    bad_a = multiplier(widths,[(12-s,q) for s,q in toy_flow['sources'].items()]+multiplied)
    reject('merge repeated parent paths and paid positions', lambda: check_batches(widths,requirements(toy_flow,12),bad_a), 'whole chronological batch')
    return {'schema': 'chronological-batch-width/v1', 'claim_type': 'conditional batching lemma and exact finite accounting',
            'no_new_kappa': True, 'source_sha256': pins,
            'frozen_flows_matched': 9, 'independent_literal_cut_fixtures': literal_count,
            'brute_force_minimality_cases': brute_count, 'compilations': outputs,
            'chronology_counterexample': {**fail, 'widths_through_12': compiled['source-open-equality']['widths'][:13],
                                          'aggregate_exits': dict(toy_flow['exits']),
                                          'aggregate_sources': dict(toy_flow['sources']),
                                          'repeated_cut_multiplier': bad_a},
            'rejected_controls': controls}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', action='store_true', help='authoring only: replace RESULT.json')
    args=ap.parse_args()
    # JSON object keys are strings after serialization (the small witness
    # contains rank-indexed dictionaries). Compare the same representation.
    result=json.loads(canonical(main_result()))
    target=HERE/'RESULT.json'
    if args.write:
        target.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:
        require(result == json.loads(target.read_text(encoding='utf-8')), 'committed result matches fresh replay')
    print('PASS_CHRONOLOGICAL_BATCH_WIDTH cuts='+str(result['independent_literal_cut_fixtures'])
          +' controls='+str(len(result['rejected_controls'])))


if __name__ == '__main__':
    main()
