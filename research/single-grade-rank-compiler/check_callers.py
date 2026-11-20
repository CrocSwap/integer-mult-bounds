"""Check the two retained callers against ordinary BIT prices supplied by the compiler."""

from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd, prod
from pathlib import Path
import sys
from types import ModuleType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from check_funding import applications, sources


PINS = {
    'selected_result': 'd9ba709fa5dcefffe3f3abdcf34600ce188224703cfd743e6db8b58ba4816cb7',
    'selected_caller': '3828d53e80ea97e8b866320f081af20b6b93bfebd58b95b56b85a7afe151af5e',
    'selected_gate': '60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5',
    'pending_result': '2a3946fc2fdcbf2b52f6fd4d67bcfb8920b5ef871a556bd939501f384fc82203',
    'pending_gate': '3796b2e5a27f3caa142d16364154788e60d0099f1e24a8dcd028e4fbd35a84ca',
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def pinned(path, role):
    data = path.read_bytes()
    if data.startswith(b'\x1f\x8b'):
        data = gzip.decompress(data)
    need(sha256(data).hexdigest() == PINS[role], f'wrong {role} source bytes')
    return data


def gate_at(path, role, invoice, receipt, price):
    gate = ModuleType(role)
    gate.__file__ = str(path)
    exec(compile(pinned(path, role), str(path), 'exec'), gate.__dict__)
    # The continued source's driver installs the independently certified BIT cap.
    if role == 'pending_gate':
        gate.BIT_PIN = str(price)
    result = gate.gate(invoice, receipt['claim'], receipt['tested'], *receipt['raw_bracket'], bit_pin=price)
    need(Fraction(result['BIT_margin']) == price - Fraction(receipt['tested']) > 0, 'BIT service price')
    need(result['outer'] == receipt['outer'], 'outer predicate or minimum margin')
    need((result['outer']['strict_count'], result['outer']['functional_count']) == (54, 4), 'outer count')
    print(role, 'claim', result['claim'], 'strict=54 functional=4 minimum=' + result['outer']['minimum_margin'])


def copies(histogram, count):
    return Counter({int(rank): count * n for rank, n in histogram.items()})


def compare(paid, targets, stored):
    invoice = {'P': {str(r): n for r, n in paid.items()}, 'T': {str(r): n for r, n in targets.items()}}
    need(invoice['P'] == stored['P'] and invoice['T'] == stored['T'], 'complete paid and productive grades')
    return invoice


def selected_invoice(call, result):
    ports = {kind: len(table['ports']) for kind, table in call['types'].items()}
    targets, paid = Counter(), Counter()
    calls = 0
    for event in call['events']:
        if event[0] == 'J':
            calls += 1
        elif event[1] == 'QUERY':
            paid[1] += ports[event[0]]
        elif event[1] == 'IDLE_ONE':
            paid[8 * len(event[3])] += ports[event[0]]
    for kind, table in call['types'].items():
        for direction in table['diagonal']:
            targets[(direction[0] % 2) + 8 * sum(direction[2:])] += ports[kind]
    native = result['native']
    targets.update(copies(native['helpers'], calls))
    paid.update(copies(native['paid'], calls))
    need((calls, call['ambient_rank'], sum(targets.values()), sum(paid.values())) == (18, 153, 23392, 117612), 'selected owners')
    return compare(paid, targets, result['invoice'])


def pending_invoice(result):
    ref = result['caller_census']
    native, app = result['native'], result['application']
    bindings = ref['finite_binding']
    need(result['caller_proof']['readback']['event_stream_sha256'] == result['caller'], 'pending caller identity')
    need((ref['calls'], bindings['ambient'], bindings['native_main_bindings']) == (48, 137, 19200), 'pending bindings')
    targets = copies(native['positive_helper_ranks'], ref['calls']) + copies(ref['fixed_root_targets'], 1)
    paid = copies(native['paid_native_ranks'], ref['calls']) + copies(ref['fixed_caller_paid'], 1)
    need((sum(targets.values()), sum(paid.values())) == (52512, 283248), 'pending owner counts')
    ordinary = app['ordinary']
    need(32 * sum(ordinary['raw_scalar_incidence_allowance_before_factor_32'].values()) == ordinary['scalar_services'] == 1315129344,
         'expanded scalar invoice')
    need((ordinary['odd_conversions'], ordinary['ordinary_elementary_record_upper']) == (143424, 151931146752), 'ordinary costs')
    return compare(paid, targets, {'P': app['invoice']['paid'], 'T': app['invoice']['targets']})


def ceil_log2(value):
    value = Fraction(value)
    bits = max(0, value.numerator.bit_length() - value.denominator.bit_length())
    return bits + (2**bits < value)


def contexts(selected, pending):
    old = selected['precision']['common_grid']
    unit, call = old['word'], old['caller']
    height = max(call['denominator_height'], call['pre_joint_height'] + unit['dyadic_height'])
    mass = max(ceil_log2(call['maximum_mass']), ceil_log2(call['pre_joint_mass']) + ceil_log2(unit['maximum_scaled_mass']))
    need((height, mass, unit['odd_scale_lcm']) == (178, 161, 1125), 'selected odd-grid bounds')
    first = 2 * max(height, mass)
    need(first == old['context_c'], 'selected context')

    unit = pending['native']
    variants = pending['caller_proof']['template_bounds'].values()
    caller_odd = pending['caller_census']['odd_scale']
    height = max(max(t['height'], t['entrance_height'] + unit['path_grid_height']) for t in variants)
    local_mass = unit['path_grid_odd'] * Fraction(unit['positive_path_mass_bound_unscaled'])
    mass = caller_odd * max(max(Fraction(t['mass']), Fraction(t['entrance_mass']) * local_mass) for t in variants)
    signed = pending['application']['common_root']
    need((signed['exact_grid'], signed['signed_width'], signed['temporary_width'])
         == ('2^(-p-D)', 'W=p+h+2D+3', 'W+26'), 'installed pending grid and temporary')
    need((height, ceil_log2(mass), str(mass)) == (140, 428, signed['context_mass_bound']), 'pending raw context')
    factors = pending['conversion']['odd_factors']
    need(prod(factors) == unit['path_grid_odd'] and max(factors) < 2**24, 'local exact divisions')
    need(unit['path_grid_odd'] * 2**unit['path_grid_height'] == unit['minimum_product_grid'], 'local product grid')
    coarse = unit['path_only_grid']
    common = coarse
    sparse_witness = None
    for row in unit['product_gcd_witnesses']:
        need(row['previous_gcd'] == common, 'product gcd chain')
        common = gcd(common, row['scaled_product'])
        need(row['gcd'] == common, 'product gcd witness')
        if (row['row'], row['donor'], row['input_owner']) == (34008, 48, 332):
            sparse_witness = Fraction(row['scaled_product'], coarse)
    need(coarse // common == unit['minimum_product_grid'] and sparse_witness is not None,
         'actual pre-add product grid')
    need((sparse_witness * unit['minimum_snapshot_grid']).denominator == 47
         and (sparse_witness * unit['minimum_product_grid']).denominator == 1,
         'a stored-row-only grid loses the pre-add cut')
    second = 2 * max(height, ceil_log2(mass))
    need(second == signed['context_c'], 'pending context')
    return first, second


def depth_guard(context, row):
    # One data dependency traverses at most v raw words at each inner level.
    h, v = row['H'], row['v']
    levels = row['depth_at_most']
    need(h == v * levels, 'source-specific nested rank bound')
    unfinished = 2 * v * (levels + 1)
    bits = (context * unfinished).bit_length()
    need(bits < h, 'c L < 2^H for the new program')
    return bits


def check_nested_return():
    # Parent coefficients use a quarter grid. Its owned auxiliary is zero only at the endpoints.
    parent = (2, 3)
    owned = tuple(x + y for x, y in zip((0, 0), parent))
    need(owned is not parent, 'private owner has distinct backing')
    def child(row):
        scaled = tuple(3 * x for x in row)
        transformed = scaled[::-1]  # A completed Clifford permutes the two amplitudes.
        need(all(v % 3 == 0 for v in transformed), 'local odd conversion')
        return tuple(v // 3 for v in transformed)
    public = child(parent)
    retired = tuple(x - y for x, y in zip(child(owned), public))
    need(public == (3, 2) and retired == (0, 0), 'completed child and public source')
    need(any(v % 4 for v in public) and any(v % 3 for v in parent), 'parent grid and separate scale are necessary')
    need(any(x - y for x, y in zip(child((0, 0)), public)), 'clearing a live parent auxiliary must change this return')


def main():
    sources()
    rows = applications()
    source = ROOT / 'research/shared-wire-split-composition'
    selected = json.loads(pinned(source / 'FULL-RESULT.json', 'selected_result'))
    pending = json.loads(pinned(HERE / 'retained/pending-application.json.gz', 'pending_result'))
    physical = json.loads(pinned(source / 'data/caller.json', 'selected_caller'))
    gate_at(source / 'interval_gate.py', 'selected_gate', selected_invoice(physical, selected),
            selected['gate'], Fraction(rows['selected_BIT']['ordinary']))
    gate_at(HERE / 'retained/supplier_gate.py', 'pending_gate', pending_invoice(pending),
            pending['application']['compiler'], Fraction(rows['pending_BIT']['ordinary']))
    selected_c, pending_c = contexts(selected, pending)
    selected_bits = depth_guard(selected_c, rows['selected_complex'])
    pending_bits = depth_guard(pending_c, rows['pending_complex'])
    check_nested_return()
    print(f'PASS_OUTER_CALLERS applications=2 strict=54 functional=4 contexts=356,856 '
          f'new_depth_bits={selected_bits},{pending_bits}')


if __name__ == '__main__':
    main()
