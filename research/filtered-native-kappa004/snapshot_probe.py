#!/usr/bin/env python3
"""Search already-paid backward snapshots for the following thin query.

The formal free-group replay retains all 632 arbitrary input columns.  Ordinary
native-warp recodings are allowed when they carry the snapshot frame to the
requested hyperplane. This is a bounded search, not a complete module algorithm.
Apache-2.0. Substantial OpenAI Codex assistance; predecessor notices retained.
"""
from collections import defaultdict
from fractions import Fraction as Q
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import argparse
import gzip
import importlib.util
import json
import sys
import time

HERE = Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    sys.modules[name] = m
    s.loader.exec_module(m)
    return m


def reduced(word):
    out = []
    for x in word:
        if out and out[-1] == -x:
            out.pop()
        else:
            out.append(x)
    return tuple(out)


def recode(row, word):
    out = defaultdict(Q)
    for (i, w), v in row.items():
        out[i, reduced(word+w)] += v
    return {k: v for k, v in out.items() if v}


class Span:
    def __init__(self):
        self.basis = {}
        self.columns = []

    def insert(self, row, desc):
        v = dict(row)
        rep = {len(self.columns): Q(1)}
        while v:
            p = min(v)
            if p not in self.basis:
                a = v[p]
                self.basis[p] = ({k: x/a for k, x in v.items()},
                                 {k: x/a for k, x in rep.items()})
                self.columns.append((row, desc))
                return True
            b, r = self.basis[p]
            a = v[p]
            for target, source in ((v, b), (rep, r)):
                for k, x in source.items():
                    z = target.get(k, Q(0))-a*x
                    if z:
                        target[k] = z
                    else:
                        target.pop(k, None)
        return False

    def solve(self, row):
        v, rep = dict(row), defaultdict(Q)
        while v and min(v) in self.basis:
            p = min(v)
            b, r = self.basis[p]
            a = v[p]
            for k, x in b.items():
                z = v.get(k, Q(0))-a*x
                if z:
                    v[k] = z
                else:
                    v.pop(k, None)
            for k, x in r.items():
                rep[k] += a*x
        if not v:
            check = defaultdict(Q)
            for k, x in rep.items():
                for t, a in self.columns[k][0].items():
                    check[t] += x*a
            need({k: x for k, x in check.items() if x} == row, 'Exact recovered row')
        return v, {k: x for k, x in rep.items() if x}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--packet', type=Path, required=True)
    ap.add_argument('--ports', type=int, default=112)
    ap.add_argument('--output', type=Path, default=HERE/'evidence/snapshot-probe.json')
    args = ap.parse_args()
    start = time.monotonic()
    root = args.packet
    source = root/'research/native_contact/SCALED-GLOBAL-CANCEL-WORD.json.gz'
    core_path = root/'upstream/research/involutory-producer-raw-dual/inputs/core/native_core.py'
    w = json.loads(gzip.decompress(source.read_bytes()))
    c = w['canonical']
    core = load('snapshot_native_core', core_path)
    rows = [core.identity(i) for i in range(632)]+[{}]
    frames = c['start'][:]+[None]
    snapshots = []
    seen = set()

    def save(i, at):
        f = frames[i]
        if f is None or len(c['frames'][f]) != 8 or not rows[i]:
            return
        key = f, tuple(sorted(rows[i].items()))
        if key not in seen:
            seen.add(key)
            snapshots.append((dict(rows[i]), f, i, at))

    for i in range(632):
        save(i, -1)
    paid = defaultdict(int)
    for pos, e in enumerate(w['programs']['backward']):
        typ = e[0]
        if typ == 'scalar':
            a, f = e[1:]
            d = a[1][1]+632*(a[1][0] == 'C')
            if a[0] == 'clear':
                need(d == 632, 'Only owned erasure')
                rows[d], frames[d] = {}, f
            elif a[0] in ('copy', 'add'):
                s = a[2][1]+632*(a[2][0] == 'C')
                need(frames[s] == frames[d] == f, 'Scalar frame')
                if a[0] == 'copy':
                    rows[d] = dict(rows[s])
                else:
                    core.add(rows[d], rows[s], Q(a[3], a[4]))
            else:
                need(a[0] == 'scale', 'Known scalar')
                rows[d] = {k: v*Q(a[2], a[3]) for k, v in rows[d].items() if a[2]*v}
        elif typ == 'warp':
            d = e[1][1]+632*(e[1][0] == 'C')
            need(frames[d] == e[3], 'Warp entrance')
            rows[d] = core.warp(rows[d], e[2], True)
            frames[d] = e[4]
            save(d, pos)
        elif typ in ('climb', 'center'):
            d, old, new, rank = e[2:] if typ == 'climb' else (632+e[1], *e[2:])
            need(frames[d] == old, 'Paid entrance')
            frames[d] = new
            paid[rank] += 1
            save(d, pos)
        else:
            need(typ in ('phase', 'adapter', 'residual_adapter'), 'Known event')
    need(rows[:632] == [core.expected(i, True) for i in range(632)], 'All independent originals')
    need(not rows[632] and frames[:632] == c['final'], 'Native return')
    print('snapshots', len(snapshots), flush=True)
    # The phase-bearing K_G must be used here. A binary incidence test on
    # G alone is insufficient for the physical Clifford transport.
    sys.path.insert(0, str(root/'research/retained_state_next'))
    kg = load('thin_snapshot_kg', root/'research/retained_state_next/consumer_kg_module.py')
    ce = load('thin_snapshot_ce', kg.CLIFFORD)
    review = load('thin_snapshot_review', root/'research/retained_state_next/review_kg_full_frame_kernel.py')
    group = kg.PhaseGroup(ce, c, True)

    @lru_cache(None)
    def operator(word):
        out = ce.ident(9)
        for op in reversed(word):
            label = (1 if op > 0 else -1)*(abs(op) % 1000000)
            out = out.then(group.ops[group.letters[label]])
        return out

    @lru_cache(None)
    def frame(f):
        return review.conjugate(ce, ce.canonical_frame(9, c['frames'][f]))

    @lru_cache(None)
    def free_transport(old, new, word):
        op = frame(old).adjoint().then(operator(word)).then(frame(new))
        return ce.rank([x for x, z, p in op.tab[9:]]) == 0

    results = []
    for port in range(args.ports):
        target_f = c['final'][112+port]
        span = Span()
        attempted = 0
        for row, f, owner, at in snapshots:
            words = {tuple(-x for x in reversed(word)) for (origin, word) in row
                     if origin in (port, port+112)}
            for word in sorted(words):
                if not free_transport(f, target_f, word):
                    continue
                attempted += 1
                v = recode(row, word)
                span.insert(v, {'snapshot_owner': owner, 'after_event': at,
                                'snapshot_frame': f, 'left_native_word': word})
        goal = core.expected(port, True)
        residual, recipe = span.solve(goal)
        # No logical X should be silently dropped by a Y-only control.
        control = core.identity(port+112)
        control_residual, _ = span.solve(control)
        r = {'port': port, 'ordinary_recoded_candidate_rows': attempted,
             'independent_rows': len(span.basis), 'recovered': not residual,
             'residual_terms': len(residual), 'native_Y_exit_control': not control_residual}
        if not residual:
            r['recipe'] = [{'coefficient': str(a), **span.columns[k][1]} for k, a in recipe.items()]
        results.append(r)
        print('PORT', port, r, 'seconds', round(time.monotonic()-start, 2), flush=True)
    out = {'status': 'BOUNDED_NATIVE_WARP_RECODED_THIN_QUERY_SCREEN',
           'source_sha256': sha256(source.read_bytes()).hexdigest(),
           'core_sha256': sha256(core_path.read_bytes()).hexdigest(),
           'native_paid': dict(sorted(paid.items())), 'arbitrary_originals': 632,
           'snapshots': len(snapshots), 'results': results,
           'scope': 'Backward native word, rank-eight snapshot arrivals; align one target input term by an inverse existing native word. Exact free-group rows. Negative results do not exclude additional group relations or arbitrary ordinary recodings.',
           'physical_binding': 'Every candidate transport is tested with the actual conjugate K_G and raw-dual canonical-frame tableaus; its B block has rank zero. A positive recipe would still need literal absolute-phase normalizers and caller wrapper checks.',
           'new_kappa': False, 'elapsed_seconds': time.monotonic()-start}
    args.output.write_text(json.dumps(out, indent=2)+'\n')


if __name__ == '__main__':
    main()
