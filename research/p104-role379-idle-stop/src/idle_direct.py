#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Contract one silent public stop and check its literal and physical substitution."""

import argparse
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
import gzip
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import runpy
import sys


PRICE_PINS = {
    'compare_recursive_invoices.py': '3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6',
    'evaluate_recursive_power.py': '52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad',
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def read_pinned(path, pin):
    data = path.read_bytes()
    require(digest(data) == pin, f'input hash mismatch for {path.name}')
    return data


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('ascii')


def span(frame):
    values = {0}
    for vector in frame:
        require(type(vector) is int and 0 < vector < 512 and vector not in values,
                'dependent or invalid frame vector')
        values |= {entry ^ vector for entry in values}
    return frozenset(values)


def operands(event):
    return event[1:3] if event[0] in ('ADD', 'COPY') else event[1:2]


def inspect(word, spans):
    """Check the entire typed tape without evaluating or changing any scalar."""
    public = word['public']
    charts = list(word['initial']) + [None] * word['owned_fields']
    require(len(word['initial']) == len(word['final']) == public,
            'wrong public interface size')
    paid, operations, clears, protected, labels = Counter(), Counter(), [], [], set()
    active = peak = 0
    for clock, event in enumerate(word['program']):
        op, addr = event[:2]
        fields = operands(event)
        require(all(type(r) is int and 0 <= r < len(charts) for r in fields),
                f'clock {clock}: operand range')
        owned = addr >= public
        if any(r >= public for r in fields):
            protected.append(event)
        operations[op] += 1
        if op == 'MOVE':
            source, target, flag = event[2:]
            require(flag is owned and charts[addr] == source and source is not None,
                    f'clock {clock}: MOVE source chart or ownership')
            require(spans[source] < spans[target] or (owned and spans[target] < spans[source]),
                    f'clock {clock}: MOVE must have the required strict nesting')
            charts[addr] = target
            paid[abs(len(word['frames'][target]) - len(word['frames'][source]))] += 1
        elif op == 'INIT':
            require(owned and charts[addr] is None and 0 <= event[2] < len(spans),
                    f'clock {clock}: INIT requires a dead owned field and a chart')
            charts[addr] = event[2]
            labels.add(addr)
            active += 1
            peak = max(peak, active)
        elif op == 'CLEAR':
            require(owned and charts[addr] is not None and charts[addr] == event[2],
                    f'clock {clock}: CLEAR requires a live owned field in its chart')
            charts[addr] = None
            active -= 1
            clears.append(clock)
        else:
            require(op in ('ADD', 'COPY', 'SCALE') and len(set(fields)) == len(fields),
                    f'clock {clock}: scalar operation or repeated operand')
            require(all(charts[r] is not None and charts[r] == event[-1] for r in fields),
                    f'clock {clock}: scalar operands must share the declared chart')
            require(Fraction(event[-2]) != 0, f'clock {clock}: scalar coefficient cannot vanish')
    require(active == 0 and charts[public:] == [None] * word['owned_fields'],
            'every owned field must end dead')
    require(charts[:public] == word['final'], 'wrong public end charts')
    live = set(word['live'])
    mains = live | {r + 112 for r in live} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    dims = [len(frame) for frame in word['frames']]
    targets = Counter(dims[b] - dims[a] for r, (a, b) in enumerate(zip(word['initial'], word['final']))
                      if r not in mains)
    require(all(rank > 0 for rank in targets), 'productive helper ranks must be positive')
    return {'paid': paid, 'targets': targets, 'operations': operations, 'clears': clears,
            'protected': protected, 'labels': sorted(labels), 'peak': peak, 'mains': mains}


def construct(word, role, first, second, spans):
    tape = word['program']
    require(0 <= role < word['public'] and 0 <= first < second < len(tape),
            'role or MOVE clocks outside the source tape')
    enter, leave = tape[first], tape[second]
    require(enter[:2] == leave[:2] == ['MOVE', role] and enter[-1] is leave[-1] is False,
            'two public MOVE anchors must name the fixed role')
    source, middle, target = enter[2], enter[3], leave[3]
    require(leave[2] == middle and spans[source] < spans[middle] < spans[target],
            'anchors do not form a strictly nested path')
    touched = [clock for clock in range(first + 1, second) if role in operands(tape[clock])]
    require(not touched, f'role observed in open MOVE interval at {touched[:4]}')
    direct = ['MOVE', role, source, target, False]
    edited = tape[:first] + tape[first + 1:second] + [direct] + tape[second + 1:]
    return dict(word, program=edited), direct, (source, middle, target)


def scalar_transcript(word):
    return [event for event in word['program'] if event[0] != 'MOVE']


def prove_scalar_order(before, after):
    original = scalar_transcript(before)
    require(original == scalar_transcript(after), 'normalized non-MOVE sequence differs')
    return {'events': len(original), 'sha256': digest(canonical(original)),
            'invariant': 'Identical INIT, ADD, COPY, SCALE and CLEAR instructions in order imply '
                         'identical normalized symbolic rows after each scalar operation on arbitrary inputs.'}


def remap_certificates(certs, before, after, removed):
    indexed = certs['clear_event_index']
    require(set(indexed) == {str(clock) for clock in before['clears']},
            'source CLEAR certificate clocks do not cover the exact tape')
    shifted = {str(clock - (clock > removed)): indexed[str(clock)] for clock in before['clears']}
    require(set(shifted) == {str(clock) for clock in after['clears']},
            'candidate CLEAR certificate clocks do not cover the exact tape')
    return dict(certs, clear_event_index=shifted)


def must_reject(check, expected):
    try:
        check()
    except ValueError as error:
        require(expected in str(error), f'wrong rejecting control: {error}')
        return str(error)
    raise ValueError(f'negative control accepted: {expected}')


def structural_controls(word, candidate, role, first, second, spans):
    source_program, new_program = word['program'], candidate['program']
    observer = ['SCALE', role, '-1', source_program[first][3]]
    observed = dict(word, program=source_program[:second] + [observer] + source_program[second:])
    inspect(observed, spans)
    replacement = second - 1
    direct = new_program[replacement]
    wrong = new_program[:replacement] + [direct[:2] + source_program[first][3:4] + direct[3:]] + new_program[replacement + 1:]
    omitted = new_program[:replacement] + new_program[replacement + 1:]
    nearby = next(i for i in range(replacement + 1, len(new_program))
                  if new_program[i][0] in ('ADD', 'SCALE') and role in operands(new_program[i]))
    mutation = new_program[nearby][:]
    mutation[-2] = str(-Fraction(mutation[-2]))
    changed_scalar = dict(candidate, program=new_program[:nearby] + [mutation] + new_program[nearby + 1:])
    inspect(changed_scalar, spans)
    return {
        'legal_intervening_scale': must_reject(
            lambda: construct(observed, role, first, second + 1, spans), 'role observed in open MOVE interval'),
        'wrong_direct_source': must_reject(lambda: inspect(dict(candidate, program=wrong), spans), 'MOVE source chart'),
        'missing_direct_move': must_reject(lambda: inspect(dict(candidate, program=omitted), spans), 'operands must share'),
        'legal_changed_scalar': must_reject(lambda: prove_scalar_order(word, changed_scalar), 'normalized non-MOVE sequence differs'),
    }


def verify_phase(source_check, frames, path):
    # Pinned predecessor module reads a mode at import time.
    original_argv = sys.argv
    try:
        sys.argv = [str(source_check)]
        tools = runpy.run_path(str(source_check))
    finally:
        sys.argv = original_argv
    first, middle, last = path
    dagger, tableau, column = (tools[name] for name in ('dagger', 'tableau', 'column'))
    lower, frame, recipe_circuit = (tools[name] for name in ('lower', 'frame_op', 'recipe_circuit'))
    checked = []
    circuits = []
    for a, b in ((first, middle), (middle, last), (first, last)):
        rank = tools['pair_columns'](frames, a, b)
        recipe = lower(frame(frames[a]).dag().then(frame(frames[b])))
        circuits.append(recipe_circuit(recipe))
        checked.append({'pair': [a, b], 'rank': rank, 'forward_columns': 512,
                        'adjoint_columns': 512, 'wrong_phase_rejected': True,
                        'recipe_sha256': digest(canonical(recipe))})
    via, direct = circuits[0] + circuits[1], circuits[2]
    require(tableau(via) == tableau(direct) and tableau(dagger(via)) == tableau(dagger(direct)),
            'composed signed Pauli action differs')
    wrong_phase = direct + (('phase', 1),)
    require(tableau(wrong_phase) == tableau(via) and column(wrong_phase) != column(via)
            and column(dagger(wrong_phase)) != column(dagger(via)), 'wrong-phase control did not reject')
    for name, a, b in (('forward', via, direct), ('adjoint', dagger(via), dagger(direct))):
        for index in range(512):
            require(column(a, index) == column(b, index), f'{name} composed column {index} differs')
    return {'checked_pairs': checked, 'composed_path': list(path), 'forward_columns': 512,
            'adjoint_columns': 512, 'signed_pauli_equal': True, 'absolute_phase_equal': True,
            'wrong_phase_same_pauli': True, 'wrong_phase_rejected_forward_and_adjoint': True}


def delta(new, old):
    return {str(rank): new[rank] - old[rank] for rank in sorted(new.keys() | old.keys()) if new[rank] != old[rank]}


def compare_price(pricing_dir, old, before, after, calls, source_upper):
    for filename, pin in PRICE_PINS.items():
        read_pinned(pricing_dir / filename, pin)
    compare = runpy.run_path(str(pricing_dir / 'compare_recursive_invoices.py'))['compare_invoices']
    evaluate = runpy.run_path(str(pricing_dir / 'evaluate_recursive_power.py'))['evaluate']
    residuals = {}
    new = dict(old)
    for side in ('paid', 'targets'):
        full = Counter({int(rank): count for rank, count in old[side].items()})
        residual = {rank: full[rank] - calls * before[side][rank] for rank in full.keys() | before[side].keys()}
        require(all(count >= 0 for count in residual.values()), f'declared caller residual below zero for {side}')
        residuals[side] = {str(rank): count for rank, count in sorted(residual.items()) if count}
        new[side] = {str(rank): residual.get(rank, 0) + calls * after[side][rank]
                     for rank in sorted(residual.keys() | after[side].keys())
                     if residual.get(rank, 0) + calls * after[side][rank]}
    comparison = compare(old, new)
    require(comparison['classification'] == 'uniformly_better' and not comparison['delta_targets'],
            'candidate must improve the fixed-target declared invoice')
    require(not any(comparison['rank_mass']['delta'].values()), 'paid and target rank masses changed')
    zero = dict(old, paid={}, targets={})
    scale = 10**13
    base_upper = Fraction(source_upper)
    lo = base_upper * scale
    require(lo.denominator == 1 and 0 < base_upper < 1 - Fraction(1, 10000), 'invalid source upper on the price grid')
    lo = lo.numerator
    hi = lo + scale // 10000

    def point(invoice, bound):
        return evaluate(zero, invoice, 1 - Fraction(bound, scale), bits=256)

    base_probe, separation_probe = point(old, lo), point(new, lo)
    require(base_probe['classification'] == 'new_cost_higher', 'declared source upper must have negative moment')
    require(separation_probe['classification'] == 'new_cost_lower', 'candidate does not separate from source upper')
    high_probe = point(new, hi)
    require(high_probe['classification'] == 'new_cost_higher', 'candidate higher endpoint is outside bounded search')
    low_probe = separation_probe
    while hi - lo > 1:
        mid = (lo + hi) // 2
        probe = point(new, mid)
        side = probe['classification']
        if side == 'new_cost_lower':
            lo, low_probe = mid, probe
        else:
            require(side == 'new_cost_higher', 'directed price point unresolved')
            hi, high_probe = mid, probe

    def as_decimal(tick):
        return f'{tick // scale}.{tick % scale:013d}'

    report = {'comparison': comparison, 'source_upper': source_upper, 'bracket': [as_decimal(lo), as_decimal(hi)],
              'source_at_source_upper': base_probe, 'candidate_at_source_upper': separation_probe,
              'candidate_at_lower': low_probe, 'candidate_at_upper': high_probe,
              'native_calls': calls, 'declared_fixed_caller_residual': residuals,
              'scope': 'Literal native counts plus unchanged residual inferred from the pinned declared invoice.'}
    return new, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('word', 'invoice', 'certificates', 'source-check', 'pricing-dir', 'out'):
        parser.add_argument('--' + name, type=Path, required=True)
    for name in ('word-sha', 'word-gzip-sha', 'invoice-sha', 'certificates-sha', 'source-check-sha', 'source-head', 'base-upper'):
        parser.add_argument('--' + name, required=True)
    for name in ('source-pr', 'role', 'clears'):
        parser.add_argument('--' + name, type=int, required=True)
    parser.add_argument('--calls', type=int, default=17)
    parser.add_argument('--anchors', type=int, nargs=2, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'use a fresh output directory')
    started = datetime.now(timezone.utc).isoformat()
    raw = gzip.decompress(read_pinned(args.word, args.word_gzip_sha))
    require(digest(raw) == args.word_sha, 'decoded source word hash mismatch')
    source = json.loads(raw)
    old_invoice = json.loads(read_pinned(args.invoice, args.invoice_sha))
    certs = json.loads(read_pinned(args.certificates, args.certificates_sha))
    read_pinned(args.source_check, args.source_check_sha)
    spans = [span(frame) for frame in source['frames']]
    first, second = args.anchors
    candidate, direct, path = construct(source, args.role, first, second, spans)
    before, after = inspect(source, spans), inspect(candidate, spans)
    require(args.role not in before['mains'], 'scope requires a nonmain role')
    require(len(before['clears']) == len(after['clears']) == args.clears, 'wrong CLEAR denominator')
    require(all(before[key] == after[key] for key in ('protected', 'peak', 'labels', 'targets')),
            'owned operations, bank inventory, peak or target ranks differ')
    require(len(source['program']) == len(candidate['program']) + 1, 'MOVE count must fall exactly one')
    normalized = prove_scalar_order(source, candidate)
    candidate_certs = remap_certificates(certs, before, after, first)
    controls = structural_controls(source, candidate, args.role, first, second, spans)
    physical = verify_phase(args.source_check, source['frames'], path)
    new_invoice, price = compare_price(args.pricing_dir, old_invoice, before, after, args.calls, args.base_upper)
    native_delta = delta(after['paid'], before['paid'])
    require(sum(native_delta.values()) == -1 and sum(int(rank) * n for rank, n in native_delta.items()) == 0,
            'native paid substitution must drop one MOVE and preserve rank mass')

    payload = canonical(candidate)
    compressed = BytesIO()
    with gzip.GzipFile(filename='', mode='wb', fileobj=compressed, compresslevel=9, mtime=0) as archive:
        archive.write(payload)
    archive = compressed.getvalue()
    edits = {'source_pr': args.source_pr, 'source_head': args.source_head, 'source_word_sha256': args.word_sha,
             'base_events': len(source['program']), 'delete': [[clock, source['program'][clock]] for clock in args.anchors],
             'insert_before': [[second, [direct]]], 'append': []}
    kept_neighbors = {side: next(([clock, source['program'][clock]] for clock in clocks
                                  if args.role in operands(source['program'][clock])), None)
                      for side, clocks in (('before', range(first - 1, -1, -1)),
                                           ('after', range(second + 1, len(source['program']))))}
    result = {
        'status': 'PASS_SILENT_PUBLIC_MOVE_SUBSTITUTION', 'started_at': started,
        'finished_at': datetime.now(timezone.utc).isoformat(), 'role': args.role,
        'source': {'pr': args.source_pr, 'head': args.source_head, 'word_sha256': args.word_sha,
                   'gzip_sha256': args.word_gzip_sha, 'events': len(source['program']),
                   'invoice_sha256': args.invoice_sha, 'certificates_sha256': args.certificates_sha,
                   'physical_checker_sha256': args.source_check_sha, 'price_checker_sha256': PRICE_PINS},
        'candidate': {'word_sha256': digest(payload), 'gzip_sha256': digest(archive), 'events': len(candidate['program'])},
        'cut': {'anchors': args.anchors, 'frames': list(path), 'dimensions': [len(source['frames'][c]) for c in path],
                'intervening_role_mentions': 0, 'neighbors': kept_neighbors,
                'CLEARs_in_open_interval': sum(first < clock < second for clock in before['clears'])},
        'scalar_order': normalized, 'protected_events': len(before['protected']),
        'ordered_clears': args.clears, 'owned_peak': before['peak'], 'owned_labels': len(before['labels']),
        'CLEAR_certificates': 'same coefficients keyed by retained CLEAR clocks',
        'paid_native_before': dict(before['paid']), 'paid_native_after': dict(after['paid']),
        'paid_native_delta': native_delta, 'declared_signed_paid_delta': price['comparison']['delta_paid'],
        'signed_price_bracket_on_declared_residual': price['bracket'],
        'physical': physical, 'controls': controls,
    }
    args.out.mkdir(parents=True)
    (args.out / 'WORD.json.gz').write_bytes(archive)
    for filename, data in (('EDITS.json', edits), ('CLEAR-CERTIFICATES.json', candidate_certs), ('INVOICE.json', new_invoice),
                           ('PRICE.json', price), ('RESULT.json', result)):
        (args.out / filename).write_bytes(canonical(data) + b'\n')
    print(json.dumps({'status': result['status'], 'candidate': result['candidate'], 'native_delta': native_delta,
                      'price_bracket_on_declared_residual': price['bracket']}, sort_keys=True))


if __name__ == '__main__':
    main()
