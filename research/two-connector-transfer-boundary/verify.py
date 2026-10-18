#!/usr/bin/env python3
"""Exact paid two-connector boundary audit; woklerx / OpenAI Codex, Apache-2.0."""
import hashlib
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def need(value, message):
    if not value:
        raise ValueError(message)

def pair_words(n):
    """Pair least unassigned endpoint; canonical labels by opening position."""
    def rec(slots, label):
        if None not in slots:
            yield tuple(slots)
            return
        i = slots.index(None)
        for j in range(i + 1, len(slots)):
            if slots[j] is None:
                nxt = list(slots)
                nxt[i] = nxt[j] = label
                yield from rec(nxt, label + 1)
    yield from rec([None] * (2 * n), 0)

def states(word):
    z = [1, 2]
    history = [tuple(z)]
    for op in word:
        if op[0] == 'C':
            z[0] ^= z[1]
        else:
            _, source, port = op
            z[port] ^= 1 << (source + 2)
        history.append(tuple(z))
    return history

def coverage(history):
    groups = {1: set(), 2: set(), 3: set()}
    for state in history:
        for row in state:
            groups[row & 3].add(row >> 2)
    return {a ^ b for group in groups.values() for a in group for b in group}

def oracle(history):
    """Independent literal pairs across all ports/times; dirt must vanish."""
    rows = list(itertools.chain.from_iterable(history))
    return {(a ^ b) >> 2 for a in rows for b in rows if not ((a ^ b) & 3)}

def source_word(labels, regs, first, second):
    it = iter(labels)
    return [('C',) if pos in (first, second) else
            ('B', j, (regs >> j) & 1)
            for pos in range(len(labels) + 2)
            for j in ([0] if pos in (first, second) else [next(it)])]

def census(n):
    total = restored = 0
    histogram = {}
    max_mixed = 0
    for labels in pair_words(n):
        for regs in range(1 << n):
            for first, second in itertools.combinations(range(2 * n + 2), 2):
                total += 1
                h = states(source_word(labels, regs, first, second))
                if h[-1] != (1, 2):
                    continue
                restored += 1
                masks = coverage(h)
                histogram[len(masks)] = histogram.get(len(masks), 0) + 1
                opposite = ((1 << n) - 1) ^ regs
                mixed = sum(bool(m & regs) and bool(m & opposite) for m in masks)
                max_mixed = max(max_mixed, mixed)
                need(mixed == 0, 'paired readout mixed two source-port groups')
    return {'sources': n, 'candidates': total, 'restored': restored,
            'max_mixed_masks': max_mixed, 'coverage_histogram': histogram}

def run():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for entry in pins['files']:
        if entry['usage'] == 'input':
            need(hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest()
                 == entry['sha256'], 'source pin mismatch')
    # A four-transfer witness shows the mixed-support lower bound is sharp.
    witness = [('C',), ('B', 1, 1), ('C',), ('B', 0, 0),
               ('B', 0, 0), ('C',), ('B', 1, 1), ('C',)]
    history = states(witness)
    need(history[-1] == (1, 2), 'four-transfer endpoint')
    need(3 in coverage(history), 'four-transfer mixed-mask witness')
    need(coverage(history) == oracle(history), 'independent witness oracle')
    # Place the two readouts at entry and after the first B0. Check all 32
    # arbitrary scalar x0,x1,z0,z1,y inputs, forward and inverse.
    def replay(bits, ops):
        x0, x1, z0, z1, y = bits
        xs, zs = [x0, x1], [z0, z1]
        for op in ops:
            if op[0] == 'A': y ^= zs[op[1]]
            elif op[0] == 'C': zs[0] ^= zs[1]
            else: zs[op[2]] ^= xs[op[1]]
        return tuple(xs + zs + [y])
    full = [('A', 0)] + witness[:4] + [('A', 0)] + witness[4:]
    for bits in itertools.product(range(2), repeat=5):
        out = replay(bits, full)
        expected = bits[:4] + (bits[4] ^ bits[0] ^ bits[1],)
        need(out == expected, 'dirty scalar map')
        need(replay(out, reversed(full)) == bits, 'inverse map')
    controls = {}
    for name, mutant in [('omit-final-transfer', full[:-1]),
                          ('wrong-readout-port', [('A', 1)] + full[1:]),
                          ('missing-source-restore', full[:6] + full[7:])]:
        failures = sum(replay(bits, mutant) != bits[:4] + (bits[4] ^ bits[0] ^ bits[1],)
                       for bits in itertools.product(range(2), repeat=5))
        need(failures > 0, name + ' not detected')
        controls[name] = failures
    # Dirt equality is essential: mixing readouts from different ports may
    # manufacture apparent mixed masks but leaves independent dirty columns.
    dirty_bad = states([('B', 0, 0), ('B', 1, 1)])[-1]
    need(((dirty_bad[0] ^ dirty_bad[1]) >> 2) == 3
         and ((dirty_bad[0] ^ dirty_bad[1]) & 3) == 3, 'dirty-frame control')
    reports = [census(n) for n in range(1, 6)]
    need(reports[-1]['candidates'] == 1995840, 'complete five-source domain')
    need(max(reports[-1]['coverage_histogram']) == 31, 'five-source obstruction')
    # The old single-root census is checked separately, independent of C.
    counts = {}
    for labels in pair_words(5):
        prefix, vertices = 0, {0}
        for j in labels: prefix ^= 1 << j; vertices.add(prefix)
        size = len({a ^ b for a in vertices for b in vertices})
        counts[size] = counts.get(size, 0) + 1
    need(sum(counts.values()) == 945 and max(counts) == 31, 'old control')
    return {'status': 'PASS_TWO_CONNECTOR_TRANSFER_BOUNDARY', 'censuses': reports,
            'old_control': counts, 'four_transfer_witness': witness,
            'dirty_scalar_cases': 32, 'failure_controls': controls,
            'claim': 'at least four one-way transfers at minimum B/A incidence; no new kappa'}

if __name__ == '__main__':
    result = run()
    expected = HERE / 'EXPECTED.json'
    if expected.exists():
        need(json.loads(expected.read_text()) == json.loads(json.dumps(result)), 'receipt mismatch')
    print(json.dumps(result, indent=2, sort_keys=True))
