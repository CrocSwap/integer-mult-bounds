#!/usr/bin/env python3
"""Exact later-capture parity bound. Produced by Nick Petalas. Apache-2.0."""

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = 'research/g20-conjugation-admission/WORD.json.gz'
FRAMES = 'research/g20-conjugation-admission/prior/prior/prior/source/vendor/g20/inputs/FRAMES.json'
HELPERS = (297, 465, 591)
CUTS = (6292, 6296, 6622)
MAX_EQUATIONS = 17


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticated_inputs():
    sources = json.loads((HERE / 'SOURCES.json').read_text())
    live = {r['path']: r for r in sources['files'] if r['usage'] == 'input'}
    need(set(live) == {WORD, FRAMES}, 'live input inventory')
    payloads = {}
    for name in (WORD, FRAMES):
        data = (ROOT / name).read_bytes()
        need(sha256(data).hexdigest() == live[name]['sha256'], 'source hash: ' + name)
        payloads[name] = data
    return payloads


def check_contract(word, frames):
    need(len(word['records']) == 14794 and len(word['start']) == 685, 'word shape')
    need(len(word['final']) == 685 and len(word['owned']) == 48, 'boundary shape')
    need(not set(HELPERS).intersection(word['owned']), 'retained helpers')
    targets = []
    for helper, cut in zip(HELPERS, CUTS, strict=True):
        event = word['records'][cut]
        need(event[0] == 'ADD' and event[2] == helper, 'capture boundary')
        start = frames[str(word['start'][helper])]['dim']
        final = frames[str(word['final'][helper])]['dim']
        targets.append(abs(start - final))
    need(targets == [8, 4, 8], 'target ranks')
    reads = [i for i, e in enumerate(word['records']) if e[0] == 'ADD' and e[2] == HELPERS[0]]
    need(min(reads) == CUTS[0], 'unread leading interval')
    return targets


def parity_equations(word):
    width = len(word['start'])
    base_mask = (1 << width) - 1
    zeros = set(word['owned']) | set(HELPERS)
    rows = [0 if i in zeros else 1 << i for i in range(width)]
    inject = {cut: j for j, cut in enumerate(CUTS)}
    groups, always, impossible = defaultdict(list), [], []
    for index, event in enumerate(word['records']):
        if index in inject:
            j = inject[index]
            rows[HELPERS[j]] = 1 << (width + j)
        op, dest = event[:2]
        if op == 'ERASE':
            rows[dest] = 0
        elif op == 'ADD':
            # Maximal free clearing before the first read of helper 297.
            if dest != HELPERS[0] or index >= CUTS[0]:
                rows[dest] ^= rows[event[2]]
        elif op == 'Q':
            dep, label = rows[dest] >> width, rows[dest] & base_mask
            query = (index, event[4])
            if dep:
                groups[dep, label].append(query)
            elif label:
                impossible.append(query)
            else:
                always.append(query)
        else:
            need(op in ('INIT', 'ZERO_Q'), 'operation alphabet')
    need(len(groups) == MAX_EQUATIONS, 'equation count')
    need(always == [(6291, 1)] and len(impossible) == 2828, 'query partition')
    need(all(len(q) == 1 for q in groups.values()), 'one query per equation')
    equations = [(d, v, tuple(groups[d, v])) for d, v in sorted(groups)]
    return equations, always, impossible


def echelon(pairs):
    basis = {}
    for dep, label in pairs:
        for pivot in range(2, -1, -1):
            if dep & (1 << pivot):
                if pivot not in basis:
                    basis[pivot] = (dep, label)
                    break
                mask, value = basis[pivot]
                dep, label = dep ^ mask, label ^ value
        else:
            if label:
                return None
    return basis


def implied(basis, dep, label):
    for pivot in range(2, -1, -1):
        if dep & (1 << pivot) and pivot in basis:
            mask, value = basis[pivot]
            dep, label = dep ^ mask, label ^ value
    return dep == 0 and label == 0


def histogram(queries):
    counts = Counter(rank for _, rank in queries)
    return tuple(counts[rank] for rank in range(1, 7))


def raw_rank(profile):
    return sum(rank * count for rank, count in enumerate(profile, 1))


def basis_oracle(equations, always):
    need(len(equations) <= MAX_EQUATIONS, 'bounded equation domain')
    pairs = [(d, v) for d, v, _ in equations]
    profiles, closures = set(), set()
    best, witness, attempts = -1, None, 0
    for size in range(4):
        for chosen in combinations(pairs, size):
            attempts += 1
            basis = echelon(chosen)
            if basis is None:
                continue
            kept = tuple(i for i, (d, v) in enumerate(pairs) if implied(basis, d, v))
            queries = list(always)
            for i in kept:
                queries.extend(equations[i][2])
            profile = histogram(queries)
            profiles.add(profile)
            closures.add(kept)
            if raw_rank(profile) > best:
                best, witness = raw_rank(profile), chosen
    need(witness is not None, 'nonempty basis enumeration')
    return best, witness, sorted(profiles), len(closures), attempts


def subset_oracle(equations, always):
    """Separate finite oracle: exhaust subsets and build their complete row spans."""
    need(len(equations) <= MAX_EQUATIONS, 'bounded subset domain')
    best, consistent = 0, 0
    free_rank = sum(rank for _, rank in always)
    for selected in range(1 << len(equations)):
        span, cost, valid = {0: 0}, free_rank, True
        for i, (dep, label, queries) in enumerate(equations):
            if not selected & (1 << i):
                continue
            cost += sum(rank for _, rank in queries)
            if dep in span:
                if span[dep] != label:
                    valid = False
                    break
            else:
                additions = {key ^ dep: value ^ label for key, value in span.items()}
                span.update(additions)
                need(len(span) <= 8, 'three-variable span capacity')
        if valid:
            consistent += 1
            best = max(best, cost)
    return best, consistent


def solve_witness(pairs):
    basis = echelon(pairs)
    need(basis is not None and len(basis) == 3, 'full-rank attaining relaxation')
    values = [0, 0, 0]
    for pivot in range(3):
        dep, label = basis[pivot]
        for j in range(pivot):
            if dep & (1 << j):
                label ^= values[j]
        values[pivot] = label
    return values


def check_rank_bound(equations, always):
    result = basis_oracle(equations, always)
    need(result[0] == 13, 'raw paid-rank bound')
    return result


def expect_rejection(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError('control accepted: ' + message)


def controls(word, frames, equations, always):
    zero_labels = [(d, 0, q) for d, _, q in equations]
    expect_rejection(lambda: check_rank_bound(zero_labels, always), 'erased consistency labels')
    independent = defaultdict(int)
    for dep, _, queries in equations:
        independent[dep] = max(independent[dep], sum(k for _, k in queries))
    need(sum(independent.values()) + 1 == 20, 'separate-class false positive')
    expect_rejection(lambda: need(sum(independent.values()) + 1 <= 13, 'raw bound'),
                     'separately chosen payloads')
    damaged = json.loads(json.dumps(word))
    damaged['records'][CUTS[2]][2] = 590
    expect_rejection(lambda: check_contract(damaged, frames), 'wrong reinjection source')
    altered = json.loads(json.dumps(frames))
    altered[str(word['final'][465])]['dim'] = 6
    expect_rejection(lambda: check_contract(word, altered), 'missing target debit')
    impossible = [(1, 0, ()), (1, 1, ())]
    need(echelon([(d, v) for d, v, _ in impossible]) is None, 'inconsistent fixture')
    need(subset_oracle(impossible, [])[1] == 3, 'subset inconsistency fixture')
    return 5


def compute():
    payloads = authenticated_inputs()
    word = json.loads(gzip.decompress(payloads[WORD]))
    frames = json.loads(payloads[FRAMES])['frames']
    targets = check_contract(word, frames)
    equations, always, impossible = parity_equations(word)
    best, witness, profiles, closures, attempts = check_rank_bound(equations, always)
    subset_best, consistent = subset_oracle(equations, always)
    need(subset_best == best, 'two exact finite oracles')
    values = solve_witness(witness)
    attained = list(always)
    for dep, label, queries in equations:
        actual = 0
        for j in range(3):
            if dep & (1 << j):
                actual ^= values[j]
        if actual == label:
            attained.extend(queries)
    need(sum(rank for _, rank in attained) == 13, 'sharp parity relaxation')
    need(8**99 * 5**100 > 39**100, '8^(99/100) > 39/5')
    need(4**99 * 10**100 > 39**100, '4^(99/100) > 39/10')
    rejection_count = controls(word, frames, equations, always)
    return {
        'claim_type': 'scoped proof with exact finite parity certificate',
        'input_sha256': {name: sha256(data).hexdigest() for name, data in payloads.items()},
        'verifier_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
        'helpers': list(HELPERS), 'injection_cuts': list(CUTS), 'target_ranks': targets,
        'equations': [{'dependence': d, 'label_hex': hex(v), 'queries': list(q)}
                      for d, v, q in equations],
        'free_queries': always, 'unremovable_constant_queries': len(impossible),
        'basis_candidates': attempts, 'distinct_closures': closures,
        'profiles': profiles, 'subset_candidates': 1 << len(equations),
        'consistent_subsets': consistent, 'maximum_removed_rank': best,
        'attaining_parity_payloads_hex': [hex(value) for value in values],
        'attaining_parity_queries': sorted(attained),
        'saving_interval': ['0', '1/100'], 'strict_loss_lower_bound': '13/2',
        'rejection_controls': rejection_count, 'new_kappa': False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', type=Path)
    args = parser.parse_args()
    result = compute()
    encoded = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.write_result:
        with args.write_result.open('x') as output:
            output.write(encoded)
    else:
        need(json.loads((HERE / 'RESULT.json').read_text()) == json.loads(encoded), 'result receipt')
    print('PASS_G20_LATER_TRIPLE_PARITY_FLOOR max_rank=13 target_rank=20 loss>13/2 '
          'equations=17 subsets=131072 controls=5 no_new_kappa')


if __name__ == '__main__':
    main()
