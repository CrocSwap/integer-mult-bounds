#!/usr/bin/env python3
"""Partial direct compiler, nested integer batches and exact size controls.

The near-root direct exponent theorem remains open. No floating-point result
is used by this verifier. zxv with OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
import gzip
from pathlib import Path

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def source(path):
    env = {'__file__': str(path), '__name__': 'pinned_or_local_library'}
    exec(compile(path.read_bytes(), str(path), 'exec'), env)
    return env


FLOW = source(HERE/'flow.py')
Flow = FLOW['Flow']


def authenticate():
    result = {}
    prefix = Path('research/direct-mixed-flow/vendor')
    for row in json.loads((HERE/'VENDOR.json').read_text())['files']:
        raw = (HERE/'vendor'/Path(row['path']).relative_to(prefix)).read_bytes()
        digest = sha256(raw).hexdigest()
        need(digest == row['sha256'], 'changed source: '+row['path'])
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == row['git_blob'], 'changed Git source blob')
        result[row['path']] = digest
    return result


def bigint_record(n):
    return {'bits': n.bit_length(),
            'unsigned_big_endian_sha256': sha256(n.to_bytes((n.bit_length()+7)//8, 'big')).hexdigest()}


def ratio_interval(n, d):
    scale = 10**18
    low = n*scale//d
    return {'lower': str(Q(low, scale)), 'upper': str(Q(low+1, scale))}


def compile_counts(targets, paid, maximum, force_unit_replication=False):
    m, W, calls = max(targets), sum(targets.values()), sum(paid.values())
    surplus = sum(k*v for k, v in targets.items())-sum(k*v for k, v in paid.items())
    need(surplus > 0, 'positive raw rank-one surplus')
    widths = [1]*(maximum+1)
    leaves = list(range(maximum+1))
    units = [0]*(maximum+1)
    columns = [0]*(maximum+1)
    slots = [0]*(maximum+1)
    largest_sources = 1
    for n in range(m, maximum+1):
        f = Flow(targets, paid, n).merged()
        a = 1 if force_unit_replication else widths[n-1]
        widths[n] = a*f['source_count']
        leaves[n] = 0
        units[n] = a*f['units']
        columns[n] = a*f['column_mass']
        slots[n] = a*(f['source_count']+sum(f['exits'].values())+(W+calls)*f['units'])
        for histogram, complement in [(f['sources'], True), (f['exits'], False)]:
            for rank, count in histogram.items():
                e = n-rank if complement else rank
                need(0 <= e < n, 'all recursive ranks strictly decrease')
                need(a % widths[e] == 0, 'whole integer subprogram batches')
                copies = count*(a//widths[e])
                for records in (leaves, units, columns, slots):
                    records[n] += copies*records[e]
        need(widths[n] % widths[n-1] == 0, 'nested divisibility')
        need(widths[n]*n-leaves[n] == surplus*columns[n], 'whole-word rank-one identity')
        need(units[n] <= columns[n] <= widths[n]*n//surplus, 'owned-unit upper bound')
        need(slots[n] <= 2*(W+calls)*units[n], 'all compiler routing slots counted')
        largest_sources = max(largest_sources, f['source_count'])
    f = Flow(targets, paid, maximum).merged()
    Cmax = W*(W+calls+1)**(f['height']+1)
    need(largest_sources <= Cmax and widths[maximum] <= Cmax**maximum,
         'single-exponential width envelope')
    n = maximum
    return {'n': n, 'productive_width': bigint_record(widths[n]),
            'paid_rank_one_leaves': bigint_record(leaves[n]),
            'raw_instances': bigint_record(units[n]),
            'column_mass': bigint_record(columns[n]),
            'routing_slots': bigint_record(slots[n]),
            'leaves_per_array': ratio_interval(leaves[n], widths[n]),
            'width_exponent_envelope': Cmax.bit_length()*n,
            'source_count_upper': Cmax, 'rank_one_surplus': surplus,
            'paid_above_99_percent_linear': leaves[n] > 99*widths[n]*n//100,
            'nested_batch_checks': maximum-m+1}, (widths, leaves, units, columns, slots)


def finite_flows():
    rules = [
        ('separated-control', {3:2, 4:1}, {1:4, 2:2}, [1,1,1,1,2,2]),
        ('strict-overlap', {2:1, 5:1}, {1:2, 4:1}, [1,1,4]),
        ('source-open-equality', {2:4, 3:1}, {1:6, 2:2}, [1]*6+[2]*2),
    ]
    old = source(HERE/'vendor/tree_flow.py')
    rows = []
    for label, targets, paid, word in rules:
        for n in (20, 40, 80):
            f = Flow(targets, paid, n)
            merged, literal = f.merged(), f.literal(word)
            need(merged['sources'] == literal['sources'] and merged['exits'] == literal['exits'],
                 'literal and merged whole-job flow agree')
            if label == 'separated-control':
                predecessor, _ = old['lockstep_literal'](targets, word, n)
                need(merged['source_count'] == predecessor['src'] and
                     merged['exits'] == predecessor['exits'], 'unchanged separated predecessor')
                need(not merged['boundary_exits'], 'separated case has no premature exits')
            rows.append({'rule': label, 'targets': targets, 'paid': paid,
                         'flow': merged, 'literal_classes': literal['classes']})
    strict = Flow({2:1, 5:1}, {1:2, 4:1}, 20).merged()
    mass = lambda h: sum(k*v for k, v in h.items())
    without_boundary = strict['exits']-strict['boundary_exits']
    need(strict['boundary_exits'] and
         mass(strict['sources'])-mass(without_boundary) >
         strict['rank_one_surplus']*strict['column_mass'], 'omitted boundary exits undercharge')
    return rows


def inherited_rank_size_bound():
    old = json.loads((HERE/'vendor/higher-moment-RESULT.json').read_text())
    p7 = json.loads((HERE/'vendor/p7-RESULT.json').read_text())['strictification']
    T = {int(k): v for k, v in p7['targets'].items()}
    P = {int(k): v for k, v in p7['paid'].items()}
    v = old['strictification']['tensor_power']
    H = old['uniform_rank']['H']
    need((v, H) == (150, 349300000000), 'unchanged sufficient ambient rank')
    W = sum(T.values())**v
    paid_mass_upper = sum(k*n for k, n in P.items())**v+W*15**v
    need(W < 2**1950, 'productive field exponent envelope')
    need(paid_mass_upper < 2**2701 and W+paid_mass_upper+1 < 2**2702,
         'every padded/split paid call counted by its positive rank mass')
    D = 1950+2702*(H+1)
    need(sum(k*n for k, n in T.items())-sum(k*n for k, n in P.items()) == 608,
         'underlying raw p7 rank-one surplus')
    native_bytes = gzip.decompress((HERE/'vendor/THREE-base-FULL-IDENTITY-NATIVE.json.gz').read_bytes())
    native = json.loads(native_bytes)
    factor_bytes = (HERE/'vendor/P7-FACTOR.json').read_bytes()
    factor = json.loads(factor_bytes)
    need(sha256(factor_bytes).hexdigest() == p7['native_inventory']['factor_receipt_sha256'],
         'actual p7 factor receipt')
    need(set(native) == {'forward', 'backward'} and
         all(len(w) == 22633 for w in native.values()), 'actual raw native record counts')
    # Macro description allowance: 15 exact local words, both serialized
    # orientations as an overcount, literal controller, source scalar
    # allowance, every productive/paid/contact/helper/idle slot, with 32
    # records per extra routing/ownership slot and literal payload bits.
    ni = p7['native_inventory']
    slots = (ni['productive_fields']+ni['paid_calls']+ni['contacts']+
             ni['fresh_helper_fields']+ni['main_fields']+sum(ni['whole_idle_profile'].values()))
    raw_allowance = (15*8*len(native_bytes)+8*len(factor_bytes)+
                     32*(ni['scalar_allowance']+slots+15*max(map(len,native.values()))))
    need(raw_allowance < 2**40, 'complete raw macro/serialized-input allowance')
    W0, P0 = sum(T.values()), sum(P.values())
    Uproduct = sum(W0**(v-1-i)*P0**i for i in range(v))
    need(Uproduct < 2**2392, 'chronological product raw-instance count')
    strict_surplus = (sum(k*n for k,n in T.items())**v-
                      sum(k*n for k,n in P.items())**v)
    need(strict_surplus > 0 and strict_surplus % 608 == 0
         and strict_surplus//608 >= Uproduct, 'expanded product raw-column identity')
    product_allowance = (2**40+32*v*(W0+P0+1))*Uproduct+32*v*P0**v
    completed_allowance = product_allowance+32*(paid_mass_upper+W+P0**v)
    # Include each dense binary chart/quadratic phase descriptor and role
    # indices in the fixed completed-unit allowance, not just opcodes.
    ambient = 121**v
    serialized_unit_upper = completed_allowance*64*ambient**2
    need(serialized_unit_upper < 2**5000, 'fixed completed-unit description allowance')
    need(2**5000+32*(W+paid_mass_upper)+1 < 2**5001, 'compiled record coefficient')
    need(2*D*(H+1) > 7*H+30049, 'explicit closure exponent absorption')
    return {'kappa': old['kappa'], 'H': H, 'N': '2^'+str(H), 'D': D,
            'width_bound': 'B_N < 2^(D * 2^H)',
            'paid_leaf_bound': 'P_N < B_N * 2^H',
            'raw_p7_instance_bound': 'U_raw <= (B_N * 2^H - P_N)/608',
            'owned_p7_center_bound': 'one per raw instance; <= B_N * 2^H / 608',
            'routing_macro_record_bound':
                'R <= (A + 32*(W+P) + 1) * B_N * N; A < 2^5000',
            'raw_native_record_counts': {k:len(w) for k,w in native.items()},
            'raw_macro_and_payload_allowance': raw_allowance,
            'raw_macro_allowance_upper': '2^40',
            'completed_unit_description_upper': '2^5000',
            'compiled_record_upper': 'R < 2^(D*2^H + H + 5001)',
            'source_precision_E_upper': 'E < 2^(3*D*2^H + 3*H + 15021)',
            'source_C0_upper': 'C0 < 2^(8*D*2^H)',
            'routing_slot_bound': 'slots <= 2*(W+P)*V, V completed-unit instances',
            'physical_scope': 'Encoded whole-job adapter/move records. Their permitted physical implementation and tariffs remain inherited, separately priced premises.',
            'winning_uniform_word_materialized': False}


def verify():
    inputs = authenticate()
    flows = finite_flows()
    toy = []
    for T, P in [({2:1, 5:1}, {1:2, 4:1}), ({2:4, 3:1}, {1:6, 2:2})]:
        row, _ = compile_counts(T, P, 100)
        toy.append(row)
    p7 = json.loads((HERE/'vendor/p7-RESULT.json').read_text())['strictification']
    T, P = ({int(k): v for k, v in p7[key].items()} for key in ('targets', 'paid'))
    direct, counts = compile_counts(T, P, 1000)
    B, paid = counts[0][1000], counts[1][1000]
    need(paid > 990*B, 'exact direct rank-1000 saving is below target')
    kappa = Q('0.00268647')
    # ln(2)>2/3 by its first atanh term. 1000>2^9 implies ln(1000)>6.
    # exp(x)>1+x then gives 1000^kappa > 1+6*kappa > 100/99.
    need(1000 > 2**9 and 1+6*kappa > Q(100,99), 'exact target comparison')
    direct['target_failure'] = {'kappa': str(kappa),
                                'proved': 'L(1000) > 990 > 1000^(1-kappa)',
                                'scope': 'This particular finite rank fails; no asymptotic impossibility claim.'}
    rejected = []
    try:
        compile_counts({2:1, 5:1}, {1:2, 4:1}, 10, force_unit_replication=True)
    except ValueError as e:
        need(str(e) == 'whole integer subprogram batches', 'correct missing-batch rejection')
        rejected.append(str(e))
    else:
        raise ValueError('unit-replication mutant accepted')
    try:
        Flow({2:1, 5:1}, {1:1, 5:1}, 20)
    except ValueError as e:
        need(str(e) == 'finite direct-flow rank contract', 'nondecreasing exit rejected')
        rejected.append(str(e))
    else:
        raise ValueError('nondecreasing-exit mutant accepted')
    return {'schema': 'partial-direct-mixed-flow-and-finite-size/1',
            'status': 'PASS_PARTIAL_DIRECT_FLOW_AND_SIZE_BOUNDS',
            'direct_exponent_theorem_established': False,
            'finite_flows': flows, 'exact_toy_compilations': toy,
            'exact_p7_direct_compilation': direct,
            'existing_supplier_size_bounds': inherited_rank_size_bound(),
            'rejected_mutations': rejected, 'source_sha256': inputs,
            'new_code_sha256': {f: sha256((HERE/f).read_bytes()).hexdigest()
                                for f in ('flow.py', 'verify.py')},
            'scope': 'New finite matching/scheduling and batching/size bounds. The direct near-root exponent is open. Existing conditional endpoint and native/physical hypotheses remain inherited; no new kappa.'}


def normalize(x):
    if isinstance(x, dict):
        return {str(k): normalize(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [normalize(v) for v in x]
    return x


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = normalize(verify())
    if args.out:
        need(not args.out.exists(), 'new output path required')
        args.out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == result, 'changed saved receipt')
    print(json.dumps({'status': result['status'], 'direct_exponent_theorem': False,
                      'p7_width_bits_at_1000': result['exact_p7_direct_compilation']['productive_width']['bits'],
                      'target_failure': result['exact_p7_direct_compilation']['target_failure']['proved']}))


if __name__ == '__main__':
    main()
