#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Tekalign (@tekuuu), with substantial OpenAI Codex assistance.
"""Independent target-coefficient transport and four-restoration binding.

Imports no replay, builder, census, target_transport or Gaussian code. This
checks the actual FOUR-CANDIDATE witness, not a full native/outer admission.
"""
from collections import defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE = HERE.parent / 'anticipatory-stage-evidence'
VENDOR = STAGE / 'vendor/pr2339'


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def require(condition, text):
    if not condition:
        raise ValueError(text)


def apply_target_network(vector, gates, targets):
    out = dict(vector)
    for gate in gates:
        t = gate[1]
        if gate[0] == 'add':
            s, coeff = gate[2], Q(gate[3], gate[4])
            require(not (s in targets and t not in targets), 'target influences non-target state')
            if t in targets:
                out[t] = out.get(t, Q(0)) + coeff * out.get(s, Q(0))
        elif t in targets:
            out[t] = out.get(t, Q(0)) * Q(gate[2], gate[3])
        out = {r: q for r, q in out.items() if q}
    return out


def terms_grouped(terms, operator_key):
    groups = defaultdict(dict)
    for term in terms:
        op = term[operator_key]
        if isinstance(op, list):
            require(len(op) == 1, 'unexpected composite operator')
            op = op[0]
        key = (term['source'], op)
        target, value = term['target'], Q(term['coefficient'])
        require(target not in groups[key], 'duplicate correction term')
        groups[key][target] = value
    return dict(groups)


def decode_row(row):
    return {(x['source'], tuple(x['operator_word'])): Q(x['coefficient']) for x in row}


def main():
    receipt = read(STAGE / 'PR2339-SOURCE-RECEIPT.json')
    require(receipt['head'] == 'bf1742aee4d855efb8bbd44a8419eddb33a679e5', 'source commit')
    for entry in receipt['files']:
        if entry['vendor_path'] in {'vendor/pr2339/inputs/gauge44.canonical.json.gz', 'vendor/pr2339/inputs/extra.canonical.json.gz'}:
            require(hashlib.sha256((STAGE / entry['vendor_path']).read_bytes()).hexdigest() == entry['sha256'], 'source hash')
    candidates = read(HERE / 'FOUR-CANDIDATE.json')['cases']
    flags = read(HERE / 'FLAG-FOUR.json')['cases']
    evidence = []
    for case in candidates:
        name, baseline = case['provider'], case['baseline']
        tag = 'base' if name == 'gauge44' else 'extra'
        w = read(VENDOR / 'inputs' / f'{name}.canonical.json.gz')
        original = read(VENDOR / 'witness' / f'witness_80_{tag}.json')
        flag = next(x for x in flags if x['provider'] == name and x['baseline'] == baseline)
        inv = case['witness']
        count = 48 if baseline == 'high48' else 80
        require(len(inv['pairs']) == count + 4, 'pair count')
        require(inv['pairs'][-4:] == flag['pairs'], 'new pair binding')
        require(inv['early_tail_events'] == original['early_tail_events'] +
                [dict(before_B=1109, gate=g) for g in flag['restoration_gates']], 'restoration chronological binding')
        old_used = {p['register'] for p in inv['pairs'][:-4]} | {p['borrow_from'] for p in inv['pairs'][:-4]}
        required_sources = {s for g in flag['restoration_gates'] for s in g[1:3]}
        require(not old_used & required_sources, 'source was previously aliased')
        for record in flag['records']:
            r, partner = record['lender'], record['partner']
            a = decode_row(record['restoration_source_rows'][str(r)])
            b = decode_row(record['restoration_source_rows'][str(partner)])
            repaired = {k: a.get(k, Q(0)) + b.get(k, Q(0))/2 for k in set(a) | set(b)}
            repaired = {k: q for k, q in repaired.items() if q}
            require(repaired == {(r, ()): Q(1)}, 'restoration exact row')
            require(a != repaired, 'omitted restoration control')
            wrong = {k: a.get(k, Q(0)) - b.get(k, Q(0))/2 for k in set(a) | set(b)}
            wrong = {k: q for k, q in wrong.items() if q}
            require(wrong != repaired, 'wrong restoration sign control')
            require(record['restoration_gate'] == ['add', r, partner, 1, 2,
                    next(p['retirement_frame'] for p in flag['pairs'] if p['borrow_from'] == r)], 'restoration frame binding')
        targets = set(range(w['v'], 2*w['v']))
        initial = terms_grouped(flag['abstract_initial_corrections'], 'operator_word')
        actual = terms_grouped(inv['post_wrapper_corrections'], 'operator')
        predicted = {key: apply_target_network(vec, w['precondition'] + w['compensation'], targets)
                     for key, vec in initial.items()}
        require(actual == predicted, 'post-wrapper correction is not P*c0')
        require(set(inv['lifted_target_frames']) == {'135','146','162','220'}, 'lifted target support')
        require(all(w['frames'][fid] == [30] for fid in inv['lifted_target_frames'].values()), 'lifted line30')
        suffix = w['A'] + w['cut'] + w['B']
        require(all(not (e['gate'][0] == 'add' and e['gate'][2] in targets) and e['gate'][1] not in targets
                    for e in inv['early_tail_events']), 'target operation hidden in early tail')
        controls = {'untransported_coefficients_fail': False, 'wrong_post_wrapper_sign_fails': False}
        for key, vec in actual.items():
            require(apply_target_network(vec, suffix, targets) == initial[key], 'target suffix does not cancel residual')
            controls['untransported_coefficients_fail'] |= apply_target_network(initial[key], suffix, targets) != initial[key]
            wrong = dict(vec)
            t = next(iter(wrong))
            wrong[t] *= -1
            controls['wrong_post_wrapper_sign_fails'] |= apply_target_network(wrong, suffix, targets) != initial[key]
        require(all(controls.values()), 'transport negative control')
        evidence.append(dict(provider=name, baseline=baseline, independent_transport=True,
                             restoration_rows_checked=4, source_alias_exclusion=True,
                             chronological_restoration_binding=True, controls=controls))
    out = dict(status='PASS_INDEPENDENT_FOUR_TARGET_TRANSPORT_AND_RESTORATION_BINDING', cases=evidence,
               source_sha256={str(p.relative_to(HERE.parent)): hashlib.sha256(p.read_bytes()).hexdigest()
                              for p in [HERE/'FLAG-FOUR.json', HERE/'FOUR-CANDIDATE.json', Path(__file__).resolve()]},
               scope='Independent rational target transport, source-row identities and actual witness chronology binding. Source-row snapshots are inherited from exact census replay; Gaussian adapters are checked separately. This does not replace native full-word/dual/outer admission.',
               attribution='Tekalign (@tekuuu), with substantial OpenAI Codex assistance. Apache-2.0.')
    (HERE / 'FOUR-CHRONOLOGY-CHECK.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
    print(out['status'])


if __name__ == '__main__':
    main()
