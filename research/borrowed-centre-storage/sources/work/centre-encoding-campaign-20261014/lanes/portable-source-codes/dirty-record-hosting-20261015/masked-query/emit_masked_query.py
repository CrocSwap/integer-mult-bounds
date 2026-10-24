#!/usr/bin/env python3
"""Emit a unit target code that exports a masked current query."""

import argparse
from fractions import Fraction as Q
import gzip
from hashlib import sha256
import importlib.util
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parents[2]
PRIOR = LANES / 'paired-package-review/upstream-followthrough-20261015/current-query-encoder'
INTERPRETER = PRIOR.parent / 'full-exit-readers-review/check_review.py'
PINS = {
    PRIOR / 'emit_current_query.py': 'd2c45cd05f8ad0e27573226a012e183c5b0ecec4b49655beeb1f9fdd13fb3184',
    INTERPRETER: 'e59b1fe12a62e8de01eae9dd25b415524f8e43c56806f1e05a8d1d7d00b70168',
    PRIOR / 'UNIT-QUERY-PROGRAM.json.gz': '75e3e04f79d319f0024d9139d1dceaeeb2fb8e741f6e31a6079000c219c4eaa2',
    PRIOR / 'UNIT-QUERY.md': '6f53e12ba5144c8eb9df5de7eb3e19e7e0c7c1e1119db3e8116a2e643662f3a7',
    LANES / 'coherent-port/current-query-review-20261015/UNIT-REVIEW.json':
        '58620b41e6b6aef4250bea4c4b4e66ab4c8fd03cd8bdd1f438a61377f297e756',
}
PAYLOAD_PIN = '9cb744034b11ef515a9c429264199a03f02fd9c4cb408e6455021ce9c0802a9c'
T_PORTS = (21, 37, 47, 76, 81, 87, 92, 110)
SECTION_PORTS = (1, 6, 22, 28, 33, 49, 58, 109)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    for path, digest in PINS.items():
        if sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Pinned source '+str(path))
    spec = importlib.util.spec_from_file_location('retained_query', PRIOR / 'emit_current_query.py')
    base = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(base)
    m = base.m
    raw = gzip.decompress((PRIOR / 'UNIT-QUERY-PROGRAM.json.gz').read_bytes())
    m.need(sha256(raw).hexdigest() == PAYLOAD_PIN, 'Unit-query payload pin')
    old = json.loads(raw)
    # The retained query proof pins R through the unchanged current-query packet.
    current_raw = gzip.decompress((PRIOR / 'CURRENT-QUERY-PROGRAM.json.gz').read_bytes())
    m.need(sha256(current_raw).hexdigest() == old['base_payload_sha256'], 'Inherited exact R source')
    current = json.loads(current_raw)
    R = [{int(p): Q(v) for p, v in row.items()} for row in current['R']]
    J = [{int(p): Q(v) for p, v in row.items()} for row in current['J']]
    A = tuple(old['selected_A'])
    V = A+T_PORTS
    U = tuple(p for p in range(112) if p not in V)
    m.need(len(set(V)) == 16 and set(SECTION_PORTS) <= set(U), 'Disjoint mask and section')
    I = [{p: Q(1)} for p in range(112)]
    I8 = [{k: Q(1)} for k in range(8)]
    zero8 = [{} for _ in range(8)]
    P = [{k: row.get(p, 0)/4 for k, row in enumerate(R) if row.get(p, 0)}
         if p in SECTION_PORTS else {} for p in range(112)]
    kept = [{p: v for p, v in row.items() if p in U} for row in R]
    masked = [{p: v for p, v in row.items() if p in V} for row in R]
    m.need(base.multiply(kept, P) == I8, 'Actual retained-port dyadic section')
    m.need(base.multiply(masked, P) == zero8, 'Mask and section supports are disjoint')
    T = [{int(p): Q(v) for p, v in row.items()} for row in old['T']]
    Tinv = [{int(p): Q(v) for p, v in row.items()} for row in old['inverse_T']]
    LA = [{p: v for p, v in row.items() if p in A} for row in R]
    PA = [{k: row.get(p, 0)/4 for k, row in enumerate(R) if row.get(p, 0)}
          if p in A else {} for p in range(112)]
    delta = base.multiply(P, masked)
    B, Binv = [[dict(row) for row in I] for _ in range(2)]
    for p, row in enumerate(delta):
        m.add(B[p], row, -1)
        m.add(Binv[p], row)
    TB = base.multiply(T, B)
    TBinv = base.multiply(Binv, Tinv)
    m.need(base.multiply(B, Binv) == base.multiply(Binv, B) == I, 'Both mask inverse orders')
    m.need(base.multiply(TB, TBinv) == base.multiply(TBinv, TB) == I, 'Both target inverse orders')
    m.need(base.multiply(R, B) == kept, 'Exact masked query')
    m.need(base.multiply(LA, T) == R and base.multiply(LA, TB) == kept, 'Retained unit and masked target queries')
    m.need(all(v.denominator & (v.denominator-1) == 0
               for matrix in (B, Binv, TB, TBinv) for row in matrix for v in row.values()), 'Dyadic maps and inverses')

    mask_prefix = [['scalar', ['add', ['L', 112+p], ['L', 112+q], -v.numerator, v.denominator], 0]
                   for p, row in enumerate(delta) for q, v in sorted(row.items())]
    m.need(len(mask_prefix) == 64 and all(abs(v) == Q(1, 2) for row in delta for v in row.values()), '64 half additions')
    m.need(all(e[1][1][1]-112 in SECTION_PORTS and e[1][2][1]-112 in V and e[2] == 0
               for e in mask_prefix), 'Every new gate has legal I-frame disjoint supports')
    query_delta = [dict(row) for row in kept]
    for k, row in enumerate(base.multiply(LA, J)):
        m.add(query_delta[k], row, -1)
    correction = base.multiply(PA, query_delta)
    H = [dict(row) for row in J]
    for p, row in enumerate(correction):
        m.add(H[p], row)
    m.need(base.multiply(LA, H) == kept, 'Exact masked source query')
    m.need(all(not row or p in A for p, row in enumerate(correction)), 'Correction only on selected FULL rows')
    core, native = old['retained_core'], old['native_normalizations']
    suffix = [['scalar', ['add', ['L', 112+p], ['L', q], v.numerator, v.denominator], 1]
              for p, row in enumerate(correction) for q, v in sorted(row.items())]
    program = mask_prefix+old['prefix']+core+native+suffix
    expected = [{p: Q(1)} for p in range(712)]
    for p in range(112):
        expected[112+p] = dict(H[p])
        m.add(expected[112+p], {112+q: v for q, v in TB[p].items()})
    expected[704:] = [{} for _ in range(8)]
    output = m.replay(program)
    m.need(output == expected, 'All 712 input columns of the complete word')
    m.need(all(output[h] == {h: Q(1)} for h in range(224, 704)), 'All 480 arbitrary helpers restore')
    m.need(not any(k >= 224 for row in output[:224] for k in row), 'No helper or private data coefficient')
    prefix_map = m.replay(mask_prefix+old['prefix'])
    m.need(prefix_map[112:224] == [{112+q: v for q, v in row.items()} for row in TB], 'Literal target order T B')
    actual_query = base.multiply(LA, output[112:224])
    query_expected = [dict(row) for row in kept]
    for k, row in enumerate(kept):
        m.add(query_expected[k], {112+p: v for p, v in row.items()})
    m.need(actual_query == query_expected, 'Selected FULL query on every input')
    # This inverse is an exact content map. It is not a mixed-frame circuit.
    recovered_y = base.multiply(TBinv, output[112:224])
    for p, row in enumerate(base.multiply(TBinv, H)):
        m.add(recovered_y[p], row, -1)
    m.need(recovered_y == [{112+p: Q(1)} for p in range(112)], 'All original target information is retained')
    m.need(len(native) == 8 and all(e[0] == 'intrinsic_line' and e[3] == 1 for e in native), 'Unchanged eight positive query lines')
    m.need(core == old['retained_core'] and native == old['native_normalizations'], 'Every retained native event is unchanged')
    m.need(all(e[2] == 1 and e[1][1][1]-112 in A and e[1][2][1] < 112 for e in suffix), 'Every new source correction uses FULL fields')
    price = lambda events: sum(m.cost(e) for e in events if e[0] == 'scalar')
    costs = {'mask_prefix': price(mask_prefix), 'retained_unit_prefix': price(old['prefix']),
             'retained_core': price(core), 'selected_masked_source_correction': price(suffix),
             'complete_scalar': price(program), 'native_mass': 5530,
             'added_rank_one_children': 8, 'added_native_wrappers': 16,
             'new_fields': 0, 'new_mask_private_use': 0}
    m.need(costs['mask_prefix'] == 640 and costs['complete_scalar'] == 213466, 'Exact scalar bill')
    controls = {
        'mask_omitted': m.replay(old['prefix']+core+native+suffix) != expected,
        'mask_sign_reversed': m.replay([['scalar', [*e[1][:3], -e[1][3], e[1][4]], 0] for e in mask_prefix]+old['prefix']+core+native+suffix) != expected,
        'mask_after_T': m.replay(old['prefix']+mask_prefix+core+native+suffix) != expected,
        'unmasked_source_suffix': m.replay(mask_prefix+old['program']) != expected,
        'incomplete_section': base.multiply(kept, [{} if p == SECTION_PORTS[0] else row for p, row in enumerate(P)]) != I8,
    }
    m.need(all(controls.values()), 'Each mask-specific negative control fails')
    packet = {'schema': 'masked-current-query-unit-v1', 'source_payload_sha256': PAYLOAD_PIN,
              'source_pins': {str(path.relative_to(LANES)): digest for path, digest in PINS.items()},
              'R': base.serial(R), 'selected_A': list(A), 'masked_ports': list(V), 'kept_ports': list(U),
              'section_ports': list(SECTION_PORTS), 'section': base.serial(P),
              'B': base.serial(B), 'inverse_B': base.serial(Binv), 'T': old['T'],
              'source_response': base.serial(H), 'source_query': base.serial(kept),
              'target_code': base.serial(TB), 'inverse_target_code': base.serial(TBinv),
              'mask_prefix': mask_prefix, 'retained_unit_prefix': old['prefix'], 'retained_core': core,
              'native_normalizations': native, 'suffix': suffix, 'program': program,
              'physical_input': old['physical_input'], 'physical_output': old['physical_output'],
              'output_frames': old['output_frames']}
    encoded = m.encode(packet)
    receipt = {'status': 'PASS_MASKED_CURRENT_SUM_QUERY_UNIT_712_COLUMNS',
               'payload_sha256': sha256(encoded).hexdigest(), 'source_payload_sha256': PAYLOAD_PIN,
               'all_input_columns': 712, 'restored_arbitrary_helpers': 480, 'cleared_owned_fields': 8,
               'program_events': len(program), 'mask_events': len(mask_prefix), 'costs': costs,
               'query': 'L_A Y_out = R_U(X_U+Y_U)', 'target_inverse': 'Y = (T B)^-1(Y_out - H X_out)',
               'controls': controls,
               'scope': 'Exact local native word. Target inverse is algebraic only; changed-code consumer, child hosting, streams and precision remain open.'}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/'MASKED-QUERY-PROGRAM.json.gz').write_bytes(gzip.compress(encoded, mtime=0))
    (args.out/'MASKED-QUERY.json').write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    print(receipt['status'])
    print(json.dumps(costs, sort_keys=True))


if __name__ == '__main__':
    main()
