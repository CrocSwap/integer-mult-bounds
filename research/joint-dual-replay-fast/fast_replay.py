#!/usr/bin/env python3
"""Opt-in adapter: faster joint-dual serialized-word replay with identical checks.

The historical verifier `scripts/experiments/binary_frame_replay.py`, its
transitions stage `binary_frame_profile_prepare.py` and the frozen pin record
`research/joint-dual/SOURCE.json` are untouched; this adapter is additive.

Measured bottleneck (CPython 3.12, Windows): in `replay` on the pinned word
`certificates/joint-dual-word-23.json.gz`, the per-output full-triple scans

    expected = sum(1 << i for i, t in enumerate(triples)
                   if common in t and not (set(t) & (set(triple) - {common})))
    tt = [i for i, t in enumerate(triples) if common in t]

cost 0.84 s of a 2.045 s call (cProfile: 1,020,119 generator iterations at
that line; 5,336 outputs x 1,771 triples). The adapter replaces the scans with
containment masks over the same triple enumeration:

    expected(common, triple) = center_mask[common]
                               & ~pair_mask[common][x] for each x in set(triple)-{common}

which is exactly the literal condition `common in t and not (set(t) & ...)`:
bit i of `center_mask[c]` is `c in triples[i]`, bit i of `pair_mask[c][x]` is
`{c, x} <= triples[i]`. The tables are rebuilt on every call from the word's
own `h`, so there is no persistent cache and no invalidation state.

Every assertion, both full-basis orientations and the complete receipt are
retained. `check_word` and the whole transitions stage are the frozen
historical implementations, imported unchanged. The package's verify.py
cross-checks the mask identity against a literal scan on every output of both
pinned words and against the complete `tests/test_joint_reclaim.py` mutation
matrix, using the historical module as oracle.

Prepared by Aaron Wang, with help from opencode. Apache-2.0.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')

from collections import Counter
import gzip
import importlib.util
from itertools import combinations
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENTS = ROOT / 'scripts' / 'experiments'


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The frozen historical implementations, loaded by exact path under private
# names so this adapter works even when its own shim shadows the historical
# module name (see shim/binary_frame_replay.py).
historical_replay = _load('_jd_historical_frame_replay', EXPERIMENTS / 'binary_frame_replay.py')
check_word = historical_replay.check_word  # retained unchanged (incl. PR64 scatter control)

_historical_prepare = None


def prepare(path, destination):
    """The frozen historical transitions stage, delegated unchanged."""
    global _historical_prepare
    if _historical_prepare is None:
        # Lazy: the historical module imports `binary_frame_replay` by name,
        # which a preloaded shim may occupy; load only at call time.
        if 'binary_frame_replay' not in sys.modules:
            sys.path.insert(0, str(EXPERIMENTS))
        _historical_prepare = _load('_jd_historical_frame_profile_prepare',
                                    EXPERIMENTS / 'binary_frame_profile_prepare.py')
    return _historical_prepare.prepare(path, destination)


def tables(h):
    """Containment masks, destination lists and triple lookup over combinations(range(h), 3)."""
    triples = list(combinations(range(h), 3))
    center = [0] * h
    pair = [[0] * h for _ in range(h)]
    for i, t in enumerate(triples):
        bit = 1 << i
        for c in t:
            center[c] |= bit
            for x in t:
                pair[c][x] |= bit
    destinations = [[i for i, t in enumerate(triples) if c in t] for c in range(h)]
    return triples, center, pair, destinations, {t: i for i, t in enumerate(triples)}


def expected_mask(center, pair, common, triple):
    """The literal per-output scan as O(1) bitmask algebra (see module docstring)."""
    mask = center[common]
    for x in set(triple) - {common}:
        mask &= ~pair[common][x]
    return mask


def replay(path):
    """Identical contract, checks and receipt to binary_frame_replay.replay."""
    raw = Path(path).read_bytes()
    raw = gzip.decompress(raw) if str(path).endswith('.gz') else raw
    d = json.loads(raw)
    check_word(d)
    h, v, R = d['h'], d['v'], d['R']
    F = d['frames']
    triples, center, pair, destinations, lookup = tables(h)
    assert len(triples) == v
    ranks = [1 if c == u else u.bit_count() - c.bit_count() for c, u in F]
    for c, u in F:
        assert c and not c & ~u and (c.bit_count() in (1, 2) or c == u and c.bit_count() == 3)
    # First-match semantics of the historical F.index([mask, mask]) scan.
    frame_index = {}
    for index, frame in enumerate(F):
        frame_index.setdefault(tuple(frame), index)
    physical = [None] * R
    symbols = [0] * R
    hist = Counter()
    sources = {int(i): s for i, s in d['sources'].items()}
    assert len(sources) == v and len(set(sources.values())) == v

    def incidence(s, g):
        old = physical[s]
        if old is not None:
            c, u = F[old]
            cc, uu = F[g]
            assert not cc & ~c and not u & ~uu
            hist[ranks[g] - ranks[old]] += 1
        else:
            hist[ranks[g]] += 1
        physical[s] = g

    for i, s in sources.items():
        mask = sum(1 << j for j in triples[i])
        key = (mask, mask)
        if key not in frame_index:
            raise ValueError(str([mask, mask]) + ' is not in list')
        g = frame_index[key]
        incidence(s, g)
        symbols[s] = 1 << i
    for a, b, g in d['ops']:
        assert a != b
        incidence(a, g)
        incidence(b, g)
        symbols[a] ^= symbols[b]
    scatter = [0] * v
    out = set()
    for s, g, common, triple in d['outputs']:
        assert s not in out
        out.add(s)
        incidence(s, g)
        c, u = F[g]
        expected = expected_mask(center, pair, common, triple)
        assert symbols[s] == expected
        if len(triple) == 1:
            assert c == 1 << common and u == (1 << h) - 1
            r = ranks[g]
            hist[r] += 1
            hist[h - r] += 1
            tt = destinations[common]
        else:
            assert c == 1 << common and u == ((1 << h) - 1) ^ sum(1 << j for j in triple if j != common)
            hist[h - 1 - ranks[g]] += 1
            hist[1] += 1
            key = tuple(triple)
            if key not in lookup:
                raise ValueError(str(list(key)) + ' is not in list')
            tt = [lookup[key]]
        for i in tt:
            scatter[i] ^= symbols[s]
    for s, g in enumerate(physical):
        assert g is not None
        if s not in out:
            hist[h - ranks[g]] += 1
    assert scatter == [1 << i for i in range(v)]
    assert sum(t * n for t, n in hist.items()) == h * R + h * (h - 1)
    initial = [1 << i for i in range(2 * v + R)]
    M = [(2 * v + a, 2 * v + b) for a, b, g in d['ops']]
    V = [(2 * v + s, i) for i, s in sources.items()]
    J = [tuple(x) for x in d['scatter']]
    word = M + J + M[::-1] + V + M + J + M[::-1] + V
    for dual in (False, True):
        x = initial.copy()
        for a, b in reversed(word) if dual else word:
            if dual:
                a, b = b, a
            x[a] ^= x[b]
        assert x[2 * v:] == initial[2 * v:]
        if dual:
            assert x[:v] == [initial[i] ^ initial[v + i] for i in range(v)] and x[v:2 * v] == initial[v:2 * v]
        else:
            assert x[v:2 * v] == [initial[i] ^ initial[v + i] for i in range(v)] and x[:v] == initial[:v]
    return dict(status='independent serialized word, exact frames, full input and dirty basis both orientations PASS',
                h=h, roles=R, output_roles=len(out), elementary_xors=len(M), word_length=len(word),
                full_basis_vectors=2 * v + R, rank_mass=sum(t * n for t, n in hist.items()),
                histogram=dict(hist))


if __name__ == '__main__':
    print(json.dumps(replay(sys.argv[1]), indent=2))
