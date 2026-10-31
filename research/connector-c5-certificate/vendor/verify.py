#!/usr/bin/env python3
"""Standard-library check of the literal words behind this package.

Checks every word recorded in RESULTS below: floor-word shape (each source
exactly c times), depth two in characteristic c (every nonzero binary mask is
q_s + q_t mod c), and the weight identity s + t == |m| (mod c) on every
realizing pair, which is the pruning used by search_sat.py. Rejects controls.
The UNSAT verdicts are local SAT results; this script does not replay them.
"""
import hashlib
import pathlib
import sys
from itertools import product

ROOT = pathlib.Path(__file__).resolve().parents[2]
PIN = ('research/connector-depth-blocks/README.md',
       '0ce59767f249b24d65d7d14b466115858d82c0bbfaaa8eab46b7406f4e975331')

# (k, c) -> literal word found by search_sat.py (positive results and controls).
WORDS = {
    (5, 5): '0123410324314024023142310',           # control: five sources, c = 5 (PR6035)
    (6, 8): '012343532042051425130450511431524015234502413230',  # control: PR6057/PR6061
}
NEW = []  # (k, c) keys whose word is a new result of this package


def fail(msg):
    raise SystemExit('FAIL: ' + msg)


def prefixes(word, k, c):
    if len(word) != k * c or any(word.count(j) != c for j in range(k)):
        raise ValueError('not a floor word')
    q = [0] * k
    out = [tuple(q)]
    for j in word:
        q[j] += 1
        out.append(tuple(q))
    return out


def realizations(word, k, c):
    """mask -> list of boundary pairs (s, t), s <= t <= kc - 1, realizing it."""
    qs = prefixes(word, k, c)[:-1]
    masks = {m: [] for m in product((0, 1), repeat=k) if any(m)}
    for s in range(len(qs)):
        for t in range(s, len(qs)):
            m = tuple((a + b) % c for a, b in zip(qs[s], qs[t]))
            if m in masks:
                masks[m].append((s, t))
    return masks


def check_word(word, k, c):
    real = realizations(word, k, c)
    missing = [m for m, pairs in real.items() if not pairs]
    checks = 0
    for m, pairs in real.items():
        for s, t in pairs:
            if (s + t - sum(m)) % c:
                fail(f'weight identity broken k={k} c={c} m={m} s={s} t={t}')
            checks += 1
    return missing, checks


def main():
    data = (ROOT / PIN[0]).read_bytes()
    if hashlib.sha256(data).hexdigest() != PIN[1]:
        fail('source pin mismatch: ' + PIN[0])
    total = 0
    digest = hashlib.sha256()
    for (k, c), w in sorted(WORDS.items()):
        word = [int(ch) for ch in w]
        missing, checks = check_word(word, k, c)
        if missing:
            fail(f'word for k={k} c={c} misses {len(missing)} masks')
        total += checks
        digest.update(f'{k},{c},{w};'.encode())
    # controls: each must be rejected
    controls = 0
    w = [int(ch) for ch in WORDS[(6, 8)]]
    bad = w[:]; bad[5], bad[6] = bad[6], bad[5]       # adjacent swap of distinct sources
    if bad != w and not check_word(bad, 6, 8)[0]:
        fail('control: swapped c=8 word still has depth two')
    controls += 1
    try:
        prefixes(w[:-1] + [(w[-1] + 1) % 6], 6, 8)
        fail('control: wrong call count accepted')
    except ValueError:
        controls += 1
    # a depth-two word for weights {1,5,6} only, found by search_sat.py --weights 1,5,6 at c = 5
    partial = [int(ch) for ch in '012345012300551533512244443210']
    if len(check_word(partial, 6, 5)[0]) != 32:
        fail('control: partial-weight c=5 word coverage changed')
    controls += 1
    # sorted word: covers every weight-two mask but not depth two
    srt = [j for j in range(6) for _ in range(5)]
    miss = check_word(srt, 6, 5)[0]
    if not miss or any(sum(m) == 2 for m in miss):
        fail('control: sorted c=5 word')
    controls += 1
    print(f'PASS_CONNECTOR_SIX_SOURCE_SMALL_CHAR words={len(WORDS)} new={len(NEW)} '
          f'pair_checks={total} controls={controls} sha256={digest.hexdigest()[:16]}')


if __name__ == '__main__':
    main()
