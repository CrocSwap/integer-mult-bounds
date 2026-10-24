#!/usr/bin/env python3
"""Emit the unit target code with an unscaled current sum query."""

import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('prior', HERE / 'emit_current_query.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
m = base.m


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    producer_pin = 'd2c45cd05f8ad0e27573226a012e183c5b0ecec4b49655beeb1f9fdd13fb3184'
    m.read_pin(HERE / 'emit_current_query.py', producer_pin)
    raw = gzip.decompress(m.read_pin(HERE / 'CURRENT-QUERY-PROGRAM.json.gz', 'b4d5cba37c696d1c31f530b3aa4f01535718972227f8b63d626125f35046d09e'))
    m.need(sha256(raw).hexdigest() == '75d7f083af8d5687b971aa0c012e201b922f5473a4080869b581b9ba8c195fea', 'Prior literal payload')
    old = json.loads(raw)
    A, U = tuple(old['selected_A']), tuple(old['other_Y'])
    R = [{int(p): Q(v) for p, v in row.items()} for row in old['R']]
    J = [{int(p): Q(v) for p, v in row.items()} for row in old['J']]
    I = [{p: Q(1)} for p in range(112)]
    K = [{k: R[k].get(p, 0) / 4 for k in range(8) if R[k].get(p, 0)} for p in range(112)]
    KA = [row if p in A else {} for p, row in enumerate(K)]
    KU = [row if p in U else {} for p, row in enumerate(K)]
    LA = [{p: v for p, v in row.items() if p in A} for row in R]
    RU = [{p: v for p, v in row.items() if p in U} for row in R]
    plus, minus, iplus, iminus = [[dict(row) for row in I] for _ in range(4)]
    for p, row in enumerate(base.multiply(KA, RU)):
        m.add(plus[p], row)
        m.add(iplus[p], row, -1)
    for p, row in enumerate(base.multiply(KU, LA)):
        m.add(minus[p], row, -1)
        m.add(iminus[p], row)
    T = base.multiply(minus, plus)
    Tinv = base.multiply(iplus, iminus)
    m.need(base.multiply(T, Tinv) == base.multiply(Tinv, T) == I, 'Both unit inverse orders')
    m.need(base.multiply(LA, T) == R, 'Unscaled full query')
    m.need(all(T[p] == J[p] for p in U), 'Unchanged nonspecial rows')
    m.need(all(q.denominator & (q.denominator - 1) == 0 for rows in (T, Tinv) for row in rows for q in row.values()), 'Dyadic unit and inverse')
    S = [dict(row) for row in T]
    for p in range(112):
        m.add(S[p], J[p], -1)
    m.need(sum(map(len, S)) == 424 and all(abs(q) == 1 for row in S for q in row.values()), '424 signed unit corrections')
    m.need({p for p, row in enumerate(S) if row} == set(A), 'Only eight target rows')

    def event(gate, frame):
        return ['scalar', gate, frame]

    prefix, blocks = [], []
    for query, scatter, sign in ((RU, KA, 1), (LA, KU, -1)):
        part = []
        for k, row in enumerate(query):
            part.append(event(['clear', ['C', 0]], 0))
            part.extend(event(['add', ['C', 0], ['L', 112 + p], v.numerator, v.denominator], 0)
                        for p, v in sorted(row.items()))
            part.append(event(['scale', ['C', 0], 1, 4], 0))
            part.extend(event(['add', ['L', 112 + p], ['C', 0], int(sign * 4 * col[k]), 1], 0)
                        for p, col in enumerate(scatter) if k in col)
            part.append(event(['clear', ['C', 0]], 0))
        blocks.append(part)
        prefix.extend(part)
    suffix = [event(['add', ['L', 112 + p], ['L', q], int(v), 1], 1)
              for p, row in enumerate(S) for q, v in sorted(row.items())]
    core, native = old['retained_core'], old['native_normalizations']
    program = prefix + core + native + suffix
    output = m.replay(program)
    expected = [{p: Q(1)} for p in range(712)]
    for p, row in enumerate(T):
        expected[112 + p] = dict(row)
        m.add(expected[112 + p], {112 + q: v for q, v in row.items()})
    expected[704:] = [{} for _ in range(8)]
    m.need(output == expected, 'Every original data, helper and private input column')
    m.need(m.replay(prefix)[112:224] == [{112 + p: v for p, v in row.items()} for row in T], 'Exact literal unit prefix')
    m.need(all(output[h] == {h: Q(1)} for h in range(224, 704)), 'All arbitrary helpers restore')
    m.need(not any(k >= 224 for row in output[:224] for k in row), 'No helper or private input leakage')
    m.need(all(e[2] == 0 for e in prefix), 'Every new prefix gate is at I')
    m.need(all(e[2] == 1 and e[1][1][1] - 112 in A and e[1][2][1] < 112 for e in suffix), 'Every suffix gate uses completed X and selected FULL Y')
    m.need(core == old['retained_core'] and native == old['native_normalizations'], 'No new kernel or native phase premise')
    price = lambda events: sum(m.cost(e) for e in events if e[0] == 'scalar')
    costs = dict(first_shear=price(blocks[0]), second_shear=price(blocks[1]),
                 retained_core=price(core), selected_FULL_correction=price(suffix),
                 complete_scalar=price(program), native_mass=5530,
                 added_rank_one_children=8, added_native_wrappers=16)
    m.need(costs == dict(first_shear=3648, second_shear=3648, retained_core=202138,
                        selected_FULL_correction=3392, complete_scalar=212826, native_mass=5530,
                        added_rank_one_children=8, added_native_wrappers=16), 'Exact complete local invoice')
    controls = dict(reversed_prefix=m.replay(blocks[1] + blocks[0] + core + native + suffix) != expected,
                    omitted_suffix=m.replay(prefix + core + native) != expected,
                    omitted_second_shear=m.replay(blocks[0] + core + native + suffix) != expected,
                    missing_private_clear=any(704 in row for row in m.replay(prefix[1:] + core + native + suffix)[:224]))
    m.need(all(controls.values()), 'Each concrete mutation fails')
    payload = dict(schema='unit-current-query-v1', selected_A=list(A), other_Y=list(U),
                   base_payload_sha256=sha256(raw).hexdigest(), inherited_source_pins=old['source_pins'],
                   T=base.serial(T), inverse_T=base.serial(Tinv), S=base.serial(S),
                   prefix=prefix, retained_core=core, native_normalizations=native, suffix=suffix,
                   program=program, physical_input=old['physical_input'], physical_output=old['physical_output'],
                   output_frames=old['output_frames'])
    encoded = m.encode(payload)
    receipt = dict(status='PASS_UNIT_CURRENT_SUM_QUERY_712_COLUMNS', payload_sha256=sha256(encoded).hexdigest(),
                   prior_producer_sha256=producer_pin, prior_payload_sha256=sha256(raw).hexdigest(),
                   all_input_columns=712, restored_arbitrary_helper_rows=480, owned_private_rows_cleared=8,
                   new_selected_query='L_A Y_out = R(X+Y)', unit_inverse='(I-K_A R_U)(I+K_U L_A)',
                   odd_divisions=0, costs=costs, controls=controls,
                   inherited_native_check='The eight positive lines, mixed output frames and old native word are byte-identical to the PJ variant.',
                   open=['Whole-cover owner and phase review of the new mixed interface',
                         'Mixed-frame bridge consumption', 'Old-stage query capture and code retirement',
                         'Recursive hosting, finite precision and the complete supplier invoice'])
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'UNIT-QUERY-PROGRAM.json.gz').write_bytes(gzip.compress(encoded, mtime=0))
    (args.out / 'UNIT-QUERY.json').write_text(json.dumps(receipt, sort_keys=True, indent=2) + '\n')
    print(receipt['status'])
    print(json.dumps(costs, sort_keys=True))


if __name__ == '__main__':
    main()
