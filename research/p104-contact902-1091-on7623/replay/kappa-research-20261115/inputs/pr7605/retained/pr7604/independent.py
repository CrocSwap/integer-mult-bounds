#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Independent rational audit of #7546 -> #7601 -> #7603 -> helper-315 lift.

Hao Yan (@FanPUYen), with substantial OpenAI Codex assistance.

No predecessor checker or builder is imported.  The endpoint test propagates
linear functionals BACKWARDS, including one functional for the contents erased
at each CLEAR.  A separate forward pass checks event legality, coefficient
growth, lifecycle data, and the native invoice.  All public inputs are formal
indeterminates; no sampled input or floating-point calculation is used.

This checks a finite exact word and the invoice substitution.  It does not
replace the retained caller/all-width/precision/outer proof obligations.
"""
import argparse
import collections
import copy
import gzip
import hashlib
import json
import math
import time
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
RETAINED = HERE / 'retained/token-settled/data'
BASE_SHA = '6e03624b173b90356e96f845d05fc93153846b863734dc8163ab6c44c602cd32'
TOKEN_SHA = 'be97530506ab633c2a76a173a51d13f58b581ee7249338821e6e4994e3104675'
TWO_CHART_SHA = 'b3b991e9fc8d9eb684d2ee80ca477a04ad72106d6eee3f41f7b2284800c25d22'
TWO_CHART = HERE / 'retained/two-contractions'
CALLS = 17


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_word(path, digest=None):
    raw = path.read_bytes()
    if digest is not None:
        require(hashlib.sha256(raw).hexdigest() == digest, str(path) + ': frozen SHA256')
    return json.loads(gzip.decompress(raw))


def axpy(destination, source, scalar):
    """Sparse exact destination += scalar * source, with canonical zeros."""
    for index, value in source.items():
        result = destination.get(index, 0) + scalar * value
        if result:
            destination[index] = result
        else:
            destination.pop(index, None)


def reverse_outputs(word):
    """All endpoint rows AND every pre-CLEAR row via reverse linear algebra.

    For x_d <- x_d + q*x_s, adjoint[s] += q*adjoint[d].
    At CLEAR, discard dependence through its zero result and introduce a new
    output functional measuring its old value.  At INIT, discard dependence
    through the zero initial value.  MOVE is identity in normalized coordinates.
    """
    public = word['public']
    total = public + word['owned_fields']
    erased = [(e[1], e[2]) for e in word['program'] if e[0] == 'CLEAR']
    adjoints = [{r: Fraction(1)} for r in range(total)]
    erasure = len(erased)
    for event in reversed(word['program']):
        op, destination = event[:2]
        if op in ('ADD', 'COPY'):
            axpy(adjoints[event[2]], adjoints[destination], Fraction(event[3]))
        elif op == 'SCALE':
            scalar = Fraction(event[2])
            adjoints[destination] = {k: scalar * v for k, v in adjoints[destination].items()}
        elif op == 'INIT':
            adjoints[destination] = {}
        elif op == 'CLEAR':
            erasure -= 1
            adjoints[destination] = {total + erasure: Fraction(1)}
        else:
            require(op == 'MOVE', 'reverse: unknown opcode ' + str(op))
    require(erasure == 0, 'reverse: clear count')
    require(all(not row for row in adjoints[public:]), 'reverse: no uninitialized owned input')
    outputs = [{} for _ in range(total + len(erased))]
    for input_index, column in enumerate(adjoints[:public]):
        for output_index, value in column.items():
            outputs[output_index][input_index] = value
    return outputs[:total], erased, outputs[total:]


def frame_spans(frames):
    result = []
    for basis in frames:
        points = {0}
        for vector in basis:
            require(type(vector) is int and 0 < vector < 512 and vector not in points,
                    'independent frame basis over F2^9')
            points |= {p ^ vector for p in points}
        result.append(frozenset(points))
    return result


def forward_audit(word):
    """Independent legality/precision/lifecycle and native invoice census."""
    public = word['public']
    total = public + word['owned_fields']
    spans = frame_spans(word['frames'])
    dimensions = [len(basis) for basis in word['frames']]
    chart = list(word['initial']) + [None] * word['owned_fields']
    require(len(chart) == total and len(word['final']) == public, 'header register lengths')
    rows = [{r: Fraction(1)} if r < public else {} for r in range(total)]
    active = {}
    peak = 0
    owned_moves, lifetimes, erased = [], [], []
    chains = collections.defaultdict(list)
    paid, operations = collections.Counter(), collections.Counter()
    grid = dict(max_den_exp=0, odd_den=1, max_num_bits=0)

    def note(value):
        denominator = value.denominator
        exponent = (denominator & -denominator).bit_length() - 1
        grid['max_den_exp'] = max(grid['max_den_exp'], exponent)
        grid['odd_den'] = math.lcm(grid['odd_den'], denominator >> exponent)
        grid['max_num_bits'] = max(grid['max_num_bits'], abs(value.numerator).bit_length())

    def frame(index):
        require(type(index) is int and 0 <= index < len(spans), 'valid frame index')

    def live(register):
        require(type(register) is int and 0 <= register < total, 'valid register index')
        require(register < public or register in active, 'operand must be live')

    for index, event in enumerate(word['program']):
        require(isinstance(event, list) and len(event) >= 2, 'event syntax')
        op, destination = event[:2]
        require(type(destination) is int and 0 <= destination < total, 'destination index')
        operations[op] += 1
        if op == 'INIT':
            require(len(event) == 3 and destination >= public and destination not in active,
                    'INIT requires dead owned field')
            frame(event[2])
            active[destination] = event[2]
            chart[destination], rows[destination] = event[2], {}
            peak = max(peak, len(active))
        elif op == 'CLEAR':
            require(len(event) == 3 and destination in active, 'CLEAR requires live owned field')
            require(chart[destination] == event[2], 'CLEAR chart')
            erased.append((destination, event[2], rows[destination].copy()))
            lifetimes.append((destination, active.pop(destination), event[2]))
            chart[destination], rows[destination] = None, {}
        elif op == 'MOVE':
            require(len(event) == 5, 'MOVE arity')
            live(destination)
            source_frame, target_frame, owned = event[2:]
            frame(source_frame)
            frame(target_frame)
            require(type(owned) is bool and owned == (destination >= public), 'MOVE ownership flag')
            require(chart[destination] == source_frame, 'MOVE current chart at event ' + str(index))
            if owned:
                require(spans[source_frame] < spans[target_frame] or spans[target_frame] < spans[source_frame],
                        'owned MOVE must be strictly nested')
                owned_moves.append((destination, source_frame, target_frame))
            else:
                require(spans[source_frame] < spans[target_frame], 'public MOVE must strictly ascend')
            chart[destination] = target_frame
            chains[destination].append((source_frame, target_frame))
            paid[abs(dimensions[target_frame] - dimensions[source_frame])] += 1
        elif op == 'SCALE':
            require(len(event) == 4, 'SCALE arity')
            live(destination)
            scalar = Fraction(event[2])
            require(scalar != 0 and chart[destination] == event[3], 'SCALE coefficient/chart')
            rows[destination] = {k: scalar * v for k, v in rows[destination].items()}
            for value in rows[destination].values():
                note(value)
        elif op in ('ADD', 'COPY'):
            require(len(event) == 5, 'ADD/COPY arity')
            source, scalar, event_frame = event[2], Fraction(event[3]), event[4]
            live(destination)
            live(source)
            require(destination != source and scalar != 0, 'ADD/COPY operands/coefficient')
            require(chart[destination] == chart[source] == event_frame,
                    'ADD/COPY common chart at event ' + str(index))
            require(op != 'COPY' or not rows[destination], 'COPY needs zero destination')
            for column, value in rows[source].items():
                new = rows[destination].get(column, 0) + scalar * value
                if new:
                    rows[destination][column] = new
                    note(new)
                else:
                    rows[destination].pop(column, None)
        else:
            raise ValueError('unknown opcode ' + str(op))
    require(not active, 'no owned lifetimes remain open')
    require(chart[:public] == word['final'], 'public endpoint charts')
    require(all(x is None for x in chart[public:]), 'owned endpoint charts')
    mains = set(word['live']) | {r + 112 for r in word['live']}
    mains |= set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    require(all(rows[r] == {r: 1} for r in range(public) if r not in mains), 'helper identity rows')
    require(all(not row for row in rows[public:]), 'owned endpoint zero rows')
    helpers = collections.Counter(dimensions[word['final'][r]] - dimensions[word['initial'][r]]
                                  for r in range(public) if r not in mains)
    rises = collections.Counter(dimensions[b] - dimensions[a]
                                for _, a, b in owned_moves if dimensions[b] > dimensions[a])
    return dict(rows=rows, chart=chart, chains=dict(chains), grid=grid, owned_moves=owned_moves,
                lifetimes=lifetimes, peak=peak, erased=erased, paid=paid, helpers=helpers,
                rises=rises, operations=operations, mains=mains)


def matrix_digest(rows):
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps([[k, str(v)] for k, v in sorted(row.items())],
                                 separators=(',', ':')).encode())
        digest.update(b'\n')
    return digest.hexdigest()


def audit_word(word, name):
    started = time.monotonic()
    forward = forward_audit(word)
    endpoint_rows, erased_labels, erased_rows = reverse_outputs(word)
    require(endpoint_rows == forward['rows'], name + ': forward/reverse endpoints disagree')
    require(erased_labels == [(r, f) for r, f, _ in forward['erased']], name + ': erasure labels')
    require(erased_rows == [row for _, _, row in forward['erased']], name + ': forward/reverse erased rows')
    print(name + ': exact forward/reverse audit passed in %.2fs' % (time.monotonic() - started), flush=True)
    return forward


def compare(base_word, base, candidate_word, candidate, changed, changed_helpers=()):
    require({k: v for k, v in base_word.items() if k != 'program'} ==
            {k: v for k, v in candidate_word.items() if k != 'program'}, 'identical word header')
    for key in ('rows', 'chart', 'grid', 'owned_moves', 'lifetimes', 'peak', 'erased', 'helpers', 'rises'):
        require(base[key] == candidate[key], 'preserved ' + key)
    changes = sorted(r for r in set(base['chains']) | set(candidate['chains'])
                     if base['chains'].get(r) != candidate['chains'].get(r))
    require(changes == changed, 'exact changed MOVE chain set: ' + str(changes))
    for register in changed:
        if register in changed_helpers:
            require(register == 315 and register not in candidate['mains'], 'only the named helper315 may change')
            require(base['rows'][register] == candidate['rows'][register] == {register: 1},
                    'changed helper315 preserves its independent identity output')
            require(base['helpers'] == candidate['helpers'], 'helper target histogram retained')
        else:
            require(register in candidate['mains'], 'other changed register is main')
        old, new = base['chains'][register], candidate['chains'][register]
        require(old[0][0] == new[0][0] and old[-1][1] == new[-1][1], 'chain endpoints')


def histogram(invoice, key):
    return collections.Counter({int(rank): count for rank, count in invoice[key].items()})


def invoice_audit(audits):
    paths = [RETAINED / 'invoice-7546.json', RETAINED / 'invoice-new.json',
             HERE / 'data/invoice-7603.json', HERE / 'data/invoice-new.json']
    invoices = [json.loads(path.read_bytes()) for path in paths]
    receipt = json.loads((TWO_CHART / 'receipt.json').read_bytes())
    require(invoices[2]['paid'] == receipt['complete_invoice']['P'] and
            invoices[2]['targets'] == receipt['complete_invoice']['T'],
            'PR7603 source invoice derives exactly from retained receipt P/T')
    require(receipt['complete_invoice']['S'] == 1424 and
            receipt['complete_invoice']['empty_root_credits'] == 0,
            'PR7603 retained surplus and no empty-root credits')
    wrapper = None
    for result, invoice in zip(audits, invoices):
        require(invoice['schema'] == invoices[0]['schema'] and invoice['contract'] == invoices[0]['contract'],
                'full invoice contract unchanged')
        require(invoice['targets'] == invoices[0]['targets'], 'full target histogram unchanged')
        paid = histogram(invoice, 'paid')
        residual = {rank: paid[rank] - CALLS * result['paid'][rank]
                    for rank in set(paid) | set(result['paid'])}
        require(all(value >= 0 for value in residual.values()), 'nonnegative paid caller wrapper')
        residual = {rank: value for rank, value in residual.items() if value}
        if wrapper is None:
            wrapper = residual
        require(residual == wrapper, 'same fixed caller paid wrapper in all four full invoices')
    before, after = audits[2]['paid'], audits[3]['paid']
    delta = {r: after[r] - before[r] for r in set(before) | set(after) if after[r] != before[r]}
    require(delta == {1: -2, 2: 1}, 'independently counted native paid delta')
    paid, target = histogram(invoices[-1], 'paid'), histogram(invoices[-1], 'targets')
    require(sum(paid.values()) == 110383 and sum(target.values()) == 22461, 'full invoice position counts')
    surplus = sum(r * n for r, n in target.items()) - sum(r * n for r, n in paid.items())
    require(surplus == 1424, 'full invoice rank surplus')
    return dict(native_paid_delta=delta, complete_paid_delta={r: CALLS * n for r, n in delta.items()},
                paid_positions=sum(paid.values()), target_positions=sum(target.values()), rank_surplus=surplus,
                fixed_wrapper_paid_positions=sum(wrapper.values()))


def controls(candidate, audited):
    results = []
    corrupt = copy.deepcopy(candidate)
    direct = [i for i, e in enumerate(corrupt['program']) if e == ['MOVE', 315, 729, 808, False]]
    require(len(direct) == 1, 'unique direct lift')
    corrupt['program'][direct[0]][3] = 789
    try:
        forward_audit(corrupt)
    except ValueError as error:
        require('chart' in str(error), 'wrong-chart control rejected for the expected reason')
        results.append('wrong helper315 direct destination rejected at subsequent chart event')
    else:
        raise ValueError('wrong direct destination accepted')

    corrupt = copy.deepcopy(candidate)
    correction = [i for i, e in enumerate(corrupt['program']) if e == ['ADD', 166, 990, '1/2', 907]]
    require(len(correction) == 1, 'unique inherited main-166 correction')
    corrupt['program'][correction[0]][3] = '3/2'
    endpoints, _, erased = reverse_outputs(corrupt)
    require(endpoints != audited['rows'] or erased != [row for _, _, row in audited['erased']],
            'wrong inherited correction must alter exact arbitrary-input behavior')
    results.append('legal-chart wrong inherited correction rejected by exact output/erasure comparison')

    corrupt = copy.deepcopy(candidate)
    require(corrupt['program'][0] == ['ADD', 134, 146, '-1/2', 3], 'first retained premix event')
    corrupt['program'][0][3] = '-3/2'
    endpoints, _, erased = reverse_outputs(corrupt)
    require(endpoints != audited['rows'] or erased != [row for _, _, row in audited['erased']],
            'wrong inherited premix must alter exact arbitrary-input behavior')
    results.append('legal-chart wrong inherited premix rejected by exact output/erasure comparison')

    # Equal final rows alone are insufficient: CLEAR can hide a bad owned row.
    fixture = dict(public=1, owned_fields=1, program=[['INIT', 1, 0],
                   ['ADD', 1, 0, '1', 0], ['CLEAR', 1, 0]])
    changed = copy.deepcopy(fixture)
    changed['program'][1][3] = '2'
    first, labels, erased_first = reverse_outputs(fixture)
    second, labels_second, erased_second = reverse_outputs(changed)
    require(first == second and labels == labels_second and erased_first != erased_second,
            'owned erasure control must catch behavior hidden from endpoints')
    require(erased_first == [{0: Fraction(1)}] and erased_second == [{0: Fraction(2)}],
            'owned erasure control expected symbolic contents')
    results.append('nonzero owned erasure change detected despite identical final rows')
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='write audit report to this JSON path')
    args = parser.parse_args()
    words = [load_word(RETAINED / 'base-7546-word.json.gz', BASE_SHA),
             load_word(RETAINED / 'word.json.gz', TOKEN_SHA),
             load_word(TWO_CHART / 'word.json.gz', TWO_CHART_SHA), load_word(HERE / 'data/word.json.gz')]
    audits = [audit_word(word, name) for word, name in zip(words, ['PR7546', 'PR7601', 'PR7603', 'helper315'])]
    compare(words[0], audits[0], words[1], audits[1], [100, 134])
    compare(words[1], audits[1], words[2], audits[2], [134, 166])
    compare(words[2], audits[2], words[3], audits[3], [315], changed_helpers=(315,))
    compare(words[0], audits[0], words[3], audits[3], [100, 134, 166, 315], changed_helpers=(315,))
    operation_deltas = []
    for baseline, expected in [(audits[0], {'ADD': 152, 'MOVE': -5}),
                               (audits[1], {'ADD': -2, 'MOVE': -3}), (audits[2], {'MOVE': -1})]:
        old, new = baseline['operations'], audits[3]['operations']
        delta = {op: new[op] - old[op] for op in set(old) | set(new) if new[op] != old[op]}
        require(delta == expected, 'exact ordinary/native opcode count delta')
        operation_deltas.append(delta)
    report = dict(status='PASS_INDEPENDENT_RATIONAL_AUDIT', method='forward legality plus reverse exact output functionals',
                  all_public_inputs='independent rational indeterminates', events=[len(w['program']) for w in words],
                  public_inputs=words[3]['public'], owned_fields=words[3]['owned_fields'],
                  endpoint_rows=len(audits[3]['rows']), owned_clear_rows=len(audits[3]['erased']),
                  endpoint_sha256=matrix_digest(audits[3]['rows']),
                  erased_sha256=matrix_digest([row for _, _, row in audits[3]['erased']]),
                  grid=audits[3]['grid'], owned_peak=audits[3]['peak'],
                  operation_deltas_from_7546_7601_7603=operation_deltas,
                  changed_chains_from_7546=[100, 134, 166, 315], changed_chains_from_7603=[315],
                  helper315_identity_and_target_preserved=True,
                  invoice=invoice_audit(audits), controls=controls(words[3], audits[3]),
                  limitations=['Normalized rational word semantics; physical/all-width and precision proofs are separate.',
                               'Complete invoice checks fixed caller substitution at 17 calls; caller semantics are separately replayed.'])
    text = json.dumps(report, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text, encoding='utf-8')
    print(text, end='')


if __name__ == '__main__':
    main()
