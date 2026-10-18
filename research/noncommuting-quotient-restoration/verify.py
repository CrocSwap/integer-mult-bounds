#!/usr/bin/env python3
"""Replay the exact scoped certificate and semantic failure controls.

Standard library only; works with -I -O. Apache-2.0.
"""
import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import model as m
import oracle as o

PINNED_NOTES = {
    'references/PR1287-README.md': ('8606df05eca3c65032361c74ee3dbc2630b0cdc4', 'fc56e55e76a4d41d9da442ee1af63b4032eb41267a80500814f81027cc0fd087'),
    'references/PR1227-README.md': ('f39574ae9b2e3cceb01e29cf48e134f409ec1b0f', '1a038312c647b33cb697cd78bd5b2f74f5fbb8d87ec39894176c0f6ce90f5026')}


def source_bindings(directory=HERE):
    entries = json.loads((directory / 'PREDECESSORS.json').read_text(encoding='utf-8'))
    m.require(len(entries) == len(PINNED_NOTES), 'source inventory changed')
    found = set()
    for pin in entries:
        name = pin['local_path']
        m.require(name in PINNED_NOTES and name not in found, 'unknown/duplicate source')
        path = (directory / name).resolve()
        m.require(path.is_relative_to(directory.resolve()) and not (directory / name).is_symlink(), 'source path escape')
        data = path.read_bytes()
        head, digest = PINNED_NOTES[name]
        m.require(pin['commit'] == head and pin['sha256'] == digest, 'source provenance changed')
        m.require(len(data) == pin['bytes'] and hashlib.sha256(data).hexdigest() == digest, 'source bytes changed')
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        m.require(blob == pin['git_blob'], 'source Git blob mismatch')
        found.add(name)
    return len(found)


def source_matrix(width, dense):
    n = 6 * width
    matrix = o.identity(n)
    if dense:
        for i in range(n):
            matrix[i][(i + 1) % n] = -1 if i % 3 == 0 else 1
    return matrix


def group_checks():
    m.require(m.READER == o.R, 'reader order drift')
    m.require(m.pull(m.A) == o.PA and m.pull(m.B) == o.PB, 'regular action binding')
    m.require(set(m.pull(g) for g in m.GROUP) == set(o.group()), 'group closure disagreement')
    m.require(m.compose(m.A, m.B) != m.compose(m.B, m.A), 'generators commute')
    p = m.IDENTITY
    matrices = {}
    for g in m.GROUP:
        word = m.permutation_word(g, 0, 1)
        matrix = o.columns(word, 6)
        expected = [[int(j == m.pull(g)[i]) for j in range(6)] for i in range(6)]
        m.require(matrix == expected, 'literal group permutation failure')
        m.require(m.invoice(word) == o.access_invoice(word), 'permutation invoice failure')
        matrices[g] = matrix
    for g in m.GROUP:
        for h in m.GROUP:
            m.require(o.multiply(m.pull(g), m.pull(h)) == m.pull(m.compose(g, h)), 'group law failure')
            m.require(m.character(m.compose(g, h)) == m.character(g) * m.character(h), 'character not multiplicative')
    for g in m.CHILDREN:
        p = m.compose(g, p)
    m.require(p == m.IDENTITY, 'six-child relation not closed')
    admitted = []
    for reader in product((-1, 0, 1), repeat=6):
        good = True
        for g in (m.A, m.B):
            matrix = matrices[g]
            row = tuple(sum(reader[i] * matrix[i][j] for i in range(6)) for j in range(6))
            good &= row == tuple(-v for v in reader)
        if good:
            admitted.append(list(reader))
    m.require(admitted == sorted([list(m.READER), list(-v for v in m.READER), [0] * 6]), 'admission census failure')
    return {'states':6, 'group_laws':36, 'noncommuting_generators':True, 'reader_candidates':729, 'admitted_readers':admitted,
            'reader':list(m.READER), 'regular_A':list(o.PA), 'regular_B':list(o.PB)}


CASES = [((), ()), ((2,), ()), ((1,), ()), ((), (2,)), (tuple(range(1,7)), ())]
PRICES = [(1,1), (3,1), (1,3)]


def boundary_checks():
    total, results = o.boundary_census(CASES, PRICES)
    m.require(total == 6 ** 6, 'incomplete boundary census')
    for case, record in zip(CASES, results):
        record['plans'] = []
        for price, minimum in zip(PRICES, record['minima']):
            cost, corrections = m.plan(*case, *price)
            m.require(cost == minimum, 'planner/census disagreement')
            word, cuts = m.batch(corrections=corrections)
            actual = o.columns(word, 13)
            m.require(actual == o.expected_batch(1), 'planned word incorrect')
            for i in case[0]:
                prefix = o.columns(word[:cuts[i-1]], 13)
                expected = o.expected_batch(1, i)
                m.require(prefix[12] == expected[12], 'output checkpoint incorrect')
            for i in case[1]:
                prefix = o.columns(word[:cuts[i-1]], 13)
                expected = o.expected_batch(1, i)
                m.require(prefix == expected, 'workspace checkpoint incorrect')
            fixed_child = 6 * (6 * price[0] + 9 * price[0] + 3 * price[1])
            bill = m.invoice(word)
            m.require(bill['ADD'] * price[0] + bill['NEG'] * price[1] == fixed_child + minimum, 'planned paid bill mismatch')
            record['plans'].append([list(h) for h in corrections])
    m.require([r['minima'][0] for r in results] == [6,6,28,30,72], 'unit checkpoint minima changed')
    return {'normalized_endpoint_correct_schedules':total,'prices_ADD_NEG':[list(p) for p in PRICES],'cases':results}


def word_checks():
    records = []
    columns = 0
    for width in (1,2,3):
        for dense in (False, True):
            matrix = source_matrix(width, dense)
            for eager in (False, True):
                word = m.echo(width, eager, matrix)
                actual, signed_peak, majorant = m.replay(word, 13 * width)
                expected = o.expected_echo(width, matrix)
                m.require(actual == expected, 'full dirty-state echo mismatch')
                m.require(o.columns(word, 13 * width) == expected, 'independent column mismatch')
                backward = m.invert_word(word)
                m.require(o.columns(backward, 13 * width) == o.expected_echo(width, matrix, -1), 'literal inverse mismatch')
                incoming = [Fraction((-1)**i * (i + 2), i + 1) for i in range(13 * width)]
                result = [sum(row[j] * incoming[j] for j in range(13 * width)) for row in expected]
                m.require(o.run(word, incoming) == result and o.run(backward, result) == incoming, 'rational dirty probe failed')
                bill = m.invoice(word)
                m.require(bill == o.access_invoice(word), 'access invoice mismatch')
                records.append({'L':width,'source':'banded_noncommuting' if dense else 'identity', 'eager':eager,
                                'invoice':bill, 'signed_peak_row_norm':signed_peak,
                                'cancellation_free_peak':str(majorant), 'working_bits_for_entry_bound_7':1+(7*signed_peak).bit_length()})
                columns += 2 * 13 * width
    # First two-child dirty-input pilot, before relying on the six-call relation.
    pilot, _ = m.batch(children=(m.A,m.A))
    m.require(o.columns(pilot,13) == o.expected_batch(1,2), 'two-child pilot failed')
    transport, cuts = m.batch()
    p = o.ONE
    for i, g in enumerate((o.PA,o.PB)*3,1):
        p = o.multiply(g,p)
        prefix = o.columns(transport[:cuts[i-1]],13)
        m.require(prefix == o.expected_batch(1,i,p), 'typed prefix contract failed')
    kernel_prefix = o.columns(transport[:cuts[1]],13)
    m.require(kernel_prefix[12] == o.expected_batch(1,2)[12] and kernel_prefix[6:12] != o.identity(13)[6:12], 'kernel checkpoint not separated')
    return {'root_cases':len(records),'forward_inverse_basis_columns':columns,'rational_probes':len(records),'two_child_pilot':True,
            'typed_prefixes':6,'kernel_output_checkpoint':2,'records':records,
            'primary_transport_word':[list(op) for op in m.echo()], 'primary_eager_word':[list(op) for op in m.echo(eager=True)]}


def failure_controls():
    passed = []
    def reject_map(name, word, expected):
        m.require(o.columns(word,13) != expected, 'failure control survived: '+name)
        passed.append(name)
    e, cuts = m.batch()
    missing = list(e)
    del missing[next(i for i,op in enumerate(missing) if op == ('NEG',12))]
    reject_map('missing_paid_output_negation',missing,o.expected_batch(1))
    # Deliberately assemble the illegal contract outside the admitted compiler.
    wrong_reader = (m.reader_word(1,(1,0,0,0,0,0)) + m.permutation_word(m.A,6,1) + [('NEG',12)]) * 2
    wrong_expected = o.identity(13)
    wrong_expected[12][6] = 2
    reject_map('reader_admission_removed',wrong_reader,wrong_expected)
    wrong_order, _ = m.batch(children=(m.B,m.A,m.A,m.B,m.A,m.B))
    reject_map('noncommuting_child_order',wrong_order,o.expected_batch(1))
    identity_f = m.source_word(1)
    reject_map('missing_source_restoration',m.invert_word(e)+identity_f+e,o.expected_echo(1,o.identity(6)))
    reject_map('omitted_batch_inverse',identity_f+e+m.invert_word(identity_f),o.expected_echo(1,o.identity(6)))
    # Literal inverse direction matters: a forward E cannot replace E^-1.
    reject_map('forward_batch_used_as_inverse',e+identity_f+e+m.invert_word(identity_f),o.expected_echo(1,o.identity(6)))
    prefix2 = o.columns(e[:cuts[1]],13)
    m.require(prefix2[6:12] != o.expected_batch(1,2)[6:12], 'workspace observer control survived')
    passed.append('workspace_observer_at_kernel_cut')
    prefix1 = o.columns(e[:cuts[0]],13)
    m.require(prefix1[12] != o.expected_batch(1,1)[12], 'odd output observer control survived')
    passed.append('output_observer_at_odd_cut')
    bad_permutation = m.permutation_word(m.A,0,1)[1:]
    m.require(o.columns(bad_permutation,6) != [[int(j==m.pull(m.A)[i]) for j in range(6)] for i in range(6)], 'permutation corruption survived')
    passed.append('incomplete_workspace_permutation')
    for name, word in [('aliased_source',[('ADD',0,0,1)]),('wrong_sign',[('ADD',0,1,0)]),('unreserved_port',[('NEG',13)])]:
        try:
            m.validate_word(word,13)
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('invalid word survived: '+name)
    return passed


def derive():
    return {'schema_version':1, 'status':'PASS_NONCOMMUTING_QUOTIENT_RESTORATION', 'scope':'Exact characteristic-zero fixed-child group boundary; no new kappa.',
            'source_notes':source_bindings(), 'group':group_checks(), 'boundary':boundary_checks(),
            'word':word_checks(), 'failure_controls':failure_controls()}


def verify_certificate(directory=HERE):
    result = derive()
    expected = json.loads((directory/'CERTIFICATE.json').read_text(encoding='utf-8'))
    m.require(expected == result, 'certificate changed or does not match exact replay')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-certificate', action='store_true')
    args = parser.parse_args()
    result = derive() if args.write_certificate else verify_certificate()
    if args.write_certificate:
        (HERE/'CERTIFICATE.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('PASS_NONCOMMUTING_QUOTIENT_RESTORATION instructions=372->240 boundary=72->6 kernel_output_cut=2 workspace_cut_cost=30 schedules=46656 controls='+str(len(result['failure_controls']))+' no_new_kappa')


if __name__ == '__main__':
    main()
