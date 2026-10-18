#!/usr/bin/env python3
"""Separate adjoint-cut and dense-controller reconstruction. Apache-2.0.

No import from the primary checker or supplier implementation.
Prepared for BigCactusLabs with substantial OpenAI Codex assistance.
"""
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

PACKAGE = Path(__file__).resolve().parent
REPOSITORY = PACKAGE.parents[1]


def check(ok, message):
    if not ok:
        raise ValueError(message)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def add_term(vector, key, amount):
    value = vector.get(key, Fraction(0)) + amount
    if value:
        vector[key] = value
    else:
        vector.pop(key, None)


def adjoint_cut(program, cut):
    weights = {('C', program[cut][1]): Fraction(1)}
    for event in reversed(program[:cut]):
        if event[0] != 'scalar':
            check(event[0] in ('phase', 'center', 'climb', 'adapter', 'residual_adapter'),
                  'unknown local event')
            continue
        op = event[1]
        dest = tuple(op[1])
        weight = weights.get(dest, Fraction(0))
        if op[0] == 'add':
            add_term(weights, tuple(op[2]), weight * Fraction(op[3], op[4]))
        elif op[0] == 'scale':
            if weight:
                weights[dest] = weight * Fraction(op[2], op[3])
        elif op[0] == 'copy':
            weights.pop(dest, None)
            add_term(weights, tuple(op[2]), weight)
        elif op[0] == 'clear':
            weights.pop(dest, None)
        else:
            raise ValueError('unknown scalar operation')
    check(all(kind == 'L' for kind, index in weights), 'cut depends on initial private state')
    return {index: weight for (kind, index), weight in weights.items() if weight}


def identity():
    return [[int(i == j) for j in range(8)] for i in range(8)]


def multiply(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(8))
             for j in range(8)] for i in range(8)]


def reconstruct(template, programs, bridge_sign=1):
    cuts = {}
    for orient in ('forward', 'backward'):
        locations = {event[1]: i for i, event in enumerate(programs[orient]) if event[0] == 'center'}
        check(sorted(locations) == list(range(8)), 'centre locations differ')
        cuts[orient] = [adjoint_cut(programs[orient], locations[k]) for k in range(8)]
    states = [identity() for _ in range(16)]
    calls = {call['time']: call for call in template['calls']}
    all_rows = []
    for event in template['execution_schedule']:
        kind = event['kind']
        if kind == 'local_cover_sweep':
            call = calls[event['time']]
            orient = call['orientation']
            check(sha(encode(programs[orient])) == call['local_program_sha256'], 'program binding differs')
            for cut in cuts[orient]:
                row = {}
                for local_role, weight in cut.items():
                    physical = call['owners'][local_role][0]
                    rep, remainder = divmod(physical, 896)
                    component, port = divmod(remainder, 112)
                    for initial_component, coefficient in enumerate(states[rep][component]):
                        add_term(row, rep * 896 + initial_component * 112 + port,
                                 weight * coefficient)
                all_rows.append(row)
            transform = identity()
            component = 2 * call['pair']
            if orient == 'forward':
                transform[component + 1][component] = 1
            else:
                transform[component][component + 1] = -1
            rep = call['replica']
            states[rep] = multiply(transform, states[rep])
        elif kind == 'bridge':
            transform = identity()
            dst, src = 2 * event['dst'], 2 * event['src']
            transform[dst][src] = event['coefficient'] * bridge_sign
            transform[src + 1][dst + 1] = -event['coefficient'] * bridge_sign
            rep = event['replica']
            states[rep] = multiply(transform, states[rep])
        elif kind == 'terminal':
            transform = [[0] * 8 for _ in range(8)]
            for pair in range(4):
                transform[2 * pair][2 * pair + 1] = 1
                transform[2 * pair + 1][2 * pair] = -1
            rep = event['replica']
            states[rep] = multiply(transform, states[rep])
        else:
            check(kind in ('idle_cover_sweep', 'terminal_Y_translations',
                           'bank_padding_cover_sweep', 'translate_every_live_family'), 'unknown global event')
    return all_rows, states


def modular_rank(rows):
    # A nonzero 1152-minor mod this prime is a lower bound for rational rank,
    # since every denominator is nonzero mod p. Together with 1152 rows it is exact.
    p = 2147483647
    basis = {}
    for original in reversed(rows):
        row = {}
        for col, q in original.items():
            check(q.denominator % p != 0, 'noninvertible denominator')
            value = q.numerator * pow(q.denominator, -1, p) % p
            if value:
                row[col] = value
        while row:
            pivot = max(row)
            if pivot not in basis:
                inverse = pow(row[pivot], -1, p)
                basis[pivot] = {k: v * inverse % p for k, v in row.items()}
                break
            multiple = row[pivot]
            for k, v in basis[pivot].items():
                value = (row.get(k, 0) - multiple * v) % p
                if value:
                    row[k] = value
                else:
                    row.pop(k, None)
    return len(basis)


def fingerprint(rows):
    return sha(encode([[[i, str(q)] for i, q in sorted(row.items())] for row in rows]))


def main():
    sources = json.loads((PACKAGE / 'SOURCES.json').read_text())
    for item in sources['files']:
        if item['usage'] == 'input':
            check(sha((REPOSITORY / item['path']).read_bytes()) == item['sha256'], 'source hash differs')
    with tarfile.open(REPOSITORY / 'research/community-frontier1094-audit/selected-replay.tar.gz') as archive:
        template_bytes = gzip.decompress(archive.extractfile('candidate/strict/global/hosted/GLOBAL-TEMPLATE.json.gz').read())
        programs = json.loads(gzip.decompress(archive.extractfile('candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz').read()))
    template = json.loads(template_bytes)
    receipt = json.loads((PACKAGE / 'RESULT.json').read_text())
    check(sha(template_bytes) == receipt['template_payload_sha256'], 'template binding differs')
    rows, states = reconstruct(template, programs)
    check(all(state == identity() for state in states), 'dense controller endpoint differs')
    check(fingerprint(rows) == receipt['bridge_rows_sha256'], 'adjoint rows differ from forward rows')
    check(len(rows) == modular_rank(rows) == receipt['bridge_rank_q'] == 1152, 'rank certificate differs')
    # These mutations retain all local calls; they change only the bridge semantics.
    for sign in (0, -1):
        bad_rows, bad_states = reconstruct(template, programs, sign)
        check(fingerprint(bad_rows) != fingerprint(rows), 'bridge mutation did not change cuts')
        if sign == 0:
            check(any(state != identity() for state in bad_states), 'omitted bridges did not change endpoint')
        else:
            # Uniform reversal is conjugation by alternating pair signs.
            # Endpoint identity alone cannot detect this wrong cut computation.
            check(all(state == identity() for state in bad_states), 'sign-conjugate endpoint differs')
            control = receipt['uniform_bridge_sign_reversal']
            check(fingerprint(bad_rows) == control['rows_sha256'], 'sign-control rows differ')
            check(modular_rank(bad_rows) == control['rank_q'] == 1152, 'sign-control rank differs')
            check(sum(a != b for a, b in zip(rows, bad_rows)) == control['changed_centre_rows'],
                  'sign-control changed-row count differs')
            witness = control['first_changed_basis_witness']
            time, stage, replica, centre = witness['cut_time_stage_replica_centre']
            call = next(c for c in template['calls'] if c['time'] == time)
            check((call['stage'], call['replica']) == (stage, replica), 'sign-control cut label differs')
            position = 8 * time + centre
            column = witness['initial_owner_with_value_one']
            check(str(rows[position].get(column, Fraction(0))) == witness['correct_cut_value']
                  and str(bad_rows[position].get(column, Fraction(0)))
                  == witness['reversed_bridge_cut_value'], 'sign-control basis witness differs')
    check(modular_rank(rows[:8] + rows[:8]) == 8, 'dependent-row control failed')
    print('PASS_SELECTED_CENTRE_BRIDGE_ADJOINT rows=1152 rank_mod_2147483647=1152 controls=3')


if __name__ == '__main__':
    main()
