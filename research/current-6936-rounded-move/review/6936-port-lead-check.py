"""Independent source/lifetime audit of the proposed #6936 occurrence port.

Uses binary pivot elimination, not the package's explicit span enumeration.
Finite source and binding evidence only; no numerical whole-MOVE execution.
Prepared for @CubeJerry with OpenAI assistance.
"""
import argparse
from collections import Counter
from dataclasses import replace
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import sys

p = argparse.ArgumentParser()
p.add_argument('package')
p.add_argument('--output', required=True)
args = p.parse_args()
root = Path(args.package).resolve()
raw = (root / 'data/word.json.gz').read_bytes()
assert hashlib.sha256(raw).hexdigest() == '273e81f176f001684b1fa3eb857992bf58b54748004fcfe806b83adb48d2cc00'
w = json.loads(gzip.decompress(raw))

def gf2rank(rows):
    pivots = {}
    for v in rows:
        assert type(v) is int and 0 <= v < 512
        while v:
            j = v.bit_length() - 1
            if j in pivots:
                v ^= pivots[j]
            else:
                pivots[j] = v
                break
    return len(pivots)

frames = w['frames']
for f in frames:
    assert gf2rank(f) == len(f) and all(x > 0 for x in f)
pub, owned = w['public'], w['owned_fields']
assert type(pub) is type(owned) is int and pub > 0 and owned > 0
current = list(w['initial']) + [None] * owned
assert len(current) == pub + owned
assert all(type(i) is int and 0 <= i < len(frames) for i in w['initial'] + w['final'])
live, lifetimes, pairs, moves = {}, [], set(), {}
hist = Counter()
peak = rises = scalar_count = 0
for pc, e in enumerate(w['program']):
    op, r = e[:2]
    assert type(r) is int and 0 <= r < len(current)
    if op == 'INIT':
        assert len(e) == 3 and r >= pub and current[r] is None and r not in live
        assert type(e[2]) is int and 0 <= e[2] < len(frames)
        current[r] = e[2]
        live[r] = pc
        peak = max(peak, len(live))
    elif op == 'CLEAR':
        assert len(e) == 3 and r in live and current[r] == e[2]
        lifetimes.append((r, live.pop(r), pc))
        current[r] = None
    elif op == 'MOVE':
        assert len(e) == 5
        a, b, private = e[2:]
        assert type(a) is type(b) is int and type(private) is bool
        assert 0 <= a < len(frames) and 0 <= b < len(frames)
        assert current[r] == a and private == (r in live)
        assert r < pub or r in live
        da, db = len(frames[a]), len(frames[b])
        assert da != db and gf2rank(frames[a] + frames[b]) == max(da, db)
        assert private or da < db
        rank = abs(da - db)
        assert 1 <= rank <= 8
        hist[rank] += 1
        rises += int(private and da < db)
        pairs.add((a, b))
        moves[pc] = (tuple(e), rank, r)
        current[r] = b
    else:
        assert op in ('ADD', 'COPY', 'SCALE')
        assert len(e) == (4 if op == 'SCALE' else 5)
        assert current[r] is not None and current[r] == e[-1]
        assert type(e[-1]) is int and type(e[-2]) is str
        Fraction(e[-2])
        if op != 'SCALE':
            s = e[2]
            assert type(s) is int and 0 <= s < len(current) and s != r
            assert current[s] == current[r]
        scalar_count += 1
assert not live and current[:pub] == w['final']
assert all(v is None for v in current[pub:])
assert (len(w['program']), len(frames), len(moves), len(pairs), len(lifetimes), peak, rises) == (71144,1095,6323,2961,54,43,23)
receipt = json.loads((root / 'CATALOG-RESULT.json').read_text())
assert receipt['source']['lifetime_sha256'] == hashlib.sha256(json.dumps(sorted(lifetimes)).encode()).hexdigest()
assert {int(k): v for k, v in receipt['source']['rank_occurrences'].items()} == dict(hist)
assert {(r[0], r[1]) for r in receipt['certificates']} == pairs
for a, b, rank, *_ in receipt['certificates']:
    assert rank == abs(len(frames[a]) - len(frames[b]))

sys.path.insert(0, str(root))
import port_sources
state = port_sources.activate()
base = port_sources.base()
catalog = state.catalog
cls = port_sources.provider_class()
assert state.direct.S.catalog is catalog and base.direct.S.catalog is base.catalog
assert catalog is not base.catalog
assert sys.modules[cls.__module__].S.catalog is catalog
entries = catalog.catalog()[1]
assert set(entries) == set(moves)
for pc, (raw_e, rank, owner) in moves.items():
    left, child, right = entries[pc]
    token = ('proposal-6936', catalog.WORD_SHA, pc, raw_e)
    assert child.token == token and child.rank == rank and child.fields == (owner,)
    assert left.token == ('move-in',) + token and right.token == ('move-out',) + token
    assert left.fields == right.fields == child.fields
    assert left.op == right.op == 'SERVICE' and child.op == 'PAID'
event = next(t[1] for t in entries.values() if t[1].rank == 1)
bad = [replace(event, rank=True), replace(event, fields=(True,)),
       replace(event, token=('local', event.token[2], event.token[3])),
       replace(event, token=('proposal-6936', '0'*64, event.token[2], event.token[3])),
       replace(event, token=('proposal-6936', catalog.WORD_SHA, True, event.token[3]))]
for event_bad in bad:
    try:
        catalog.bind_paid(event_bad)
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError('typed negative control accepted')
out = dict(status='pass',method='independent GF(2) pivot/lifetime/source scan and exported module binding inspection',
           source_events=len(w['program']),frames=len(frames),moves=len(moves),pairs=len(pairs),
           owned_lifetimes=len(lifetimes),peak_owned=peak,owned_rises=rises,
           scalar_events=scalar_count,rank_histogram=dict(hist),typed_negative_controls=len(bad),
           unchanged_selected_catalogue=True,numerical_whole_MOVE=False,
           scientific_sha256={name: hashlib.sha256((root/name).read_bytes()).hexdigest()
             for name in ('PROOF.md','source_catalog.py','port_sources.py','rounded_move.py')},
           limitations=['Not an independent replay of every Pauli/column certificate.',
                        'No numerical whole MOVE, caller/header exporter, erasure semantics or new kappa.'])
Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,sort_keys=True))
