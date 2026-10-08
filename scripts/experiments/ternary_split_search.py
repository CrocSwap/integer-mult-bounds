#!/usr/bin/env python3
"""Search exact cancellation-free local templates; never update certificates.

Each state chooses its own split and may transpose a rectangular transform.
The exported plan can be screened with ternary_target_fingerprint.cpp, then
checked with ternary_target_exact.cpp and ternary_target_dual.cpp.
"""
from functools import lru_cache
from itertools import combinations
from math import comb
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import intersection_circuit as baseline
from intersection_circuit import Circuit, feasible
import ternary_target_fingerprint as exporter

# Greedy whole-DAG selection, independently checked with the exact support and
# frame checkers: 9,910,929 additions, 10,009,587 roles, no delayed frame nodes.
# These are template substitutions in a fixed 14+14 top partition.
H28_SELECTED_STATES = (
    (14, 1, 2, 0), (14, 1, 3, 0), (14, 2, 1, 0),
    (14, 2, 3, 0), (14, 2, 3, 1), (14, 2, 4, 1),
    (14, 2, 4, 2), (14, 2, 5, 2), (14, 3, 4, 1),
    (14, 3, 4, 2), (14, 3, 5, 2), (14, 4, 5, 2),
)


def transpose(c):
    """Reverse a cancellation-free 0/1 circuit, summing original fanouts."""
    result = Circuit(c.n, c.l, c.k, c.r)
    users = [[] for _ in c.args]
    for i, node in enumerate(c.outputs, 1):
        users[node].append(i)
    values = {}
    for node in reversed(c.active):
        value = result.total(users[node])
        values[node] = value
        for parent in c.args[node] or ():
            users[parent].append(value)
    return result.finish([values[i] for i in range(1, len(c.inputs)+1)])


def exact_outputs(c):
    """Check every coefficient, independently of the recursive decomposition."""
    for target, node in zip(c.targets, c.outputs):
        expected = sum(1 << i for i, source in enumerate(c.inputs)
                       if len(set(source) & set(target)) == c.r)
        if c.support[node] != expected:
            raise AssertionError((c.n, c.k, c.l, c.r, target))
    return True


class Search:
    def __init__(self, splits='all', transpose_enabled=True, orders=('cost',)):
        if baseline.MODE != 'half':
            baseline.MODE = 'half'
            baseline.build.cache_clear()
        self.splits = splits
        self.transpose_enabled = transpose_enabled
        self.orders = orders
        self.choices = {}
        self.trials = 0

    @lru_cache(None)
    def build(self, n, k, l, r):
        assert feasible(n, k, l, r)
        # Complement permutations shrink dense subset degrees before searching.
        if 2*k > n:
            c = Circuit(n, k, l, r)
            other = self.build(n, n-k, l, l-r)
            all_points = set(range(n))
            inputs = [c.variables[tuple(sorted(all_points-set(t)))] for t in other.inputs]
            return c.finish(c.apply(other, inputs))
        if 2*l > n:
            c = Circuit(n, k, l, r)
            other = self.build(n, k, n-l, k-r)
            out = c.apply(other, list(range(1, len(c.inputs)+1)))
            mapped = {tuple(sorted(set(range(n))-set(t))): node
                      for t, node in zip(other.targets, out)}
            return c.finish([mapped[t] for t in c.targets])
        if self.transpose_enabled and k > l:
            return transpose(self.build(n, l, k, r))
        key = n, k, l, r
        best = baseline.build(*key)
        choice = dict(kind='inherited-half', additions=best.additions)
        row = comb(l, r)*comb(n-l, k-r)
        if row == 1 or l == 0 or k == 0 or n <= 4:
            self.choices[key] = choice
            return best
        splits = range(1, n//2+1) if self.splits == 'all' else [n//2]
        orientations = [(k, l)]
        if self.transpose_enabled and k != l:
            orientations.append((l, k))
        for kin, lout in orientations:
            # Retain the asymmetric vector primitive before transposition.
            primitive = baseline.build(n, kin, lout, r)
            if kin != k:
                primitive = transpose(primitive)
            if primitive.additions < best.additions:
                best = primitive
                choice = dict(kind='transpose-inherited', additions=best.additions)
            for nl in splits:
                for order in self.orders:
                    candidate = self.split(n, kin, lout, r, nl, order)
                    if kin != k:
                        candidate = transpose(candidate)
                    self.trials += 1
                    if candidate.additions < best.additions:
                        best = candidate
                        choice = dict(kind='split', split=nl, transpose=kin != k,
                                      order=order, additions=best.additions)
        self.choices[key] = choice
        return best

    def split(self, n, k, l, r, nl, order='cost'):
        c = Circuit(n, k, l, r)
        nr = n-nl
        pieces = {t: [] for t in c.targets}
        for b in range(max(0, l-nr), min(l, nl)+1):
            tl = list(combinations(range(nl), b))
            tr = list(combinations(range(nr), l-b))
            for a in range(max(0, k-nr), min(k, nl)+1):
                il = list(combinations(range(nl), a))
                ir = list(combinations(range(nr), k-a))
                for u in range(r+1):
                    if not feasible(nl, a, b, u) or not feasible(nr, k-a, l-b, r-u):
                        continue
                    left = self.build(nl, a, b, u)
                    right = self.build(nr, k-a, l-b, r-u)
                    mat = [[c.variables[s+tuple(nl+x for x in t)] for t in ir] for s in il]
                    lc = len(ir)*left.additions+len(tl)*right.additions
                    rc = len(tr)*left.additions+len(il)*right.additions
                    first = (lc <= rc) if order == 'cost' else order == 'left'
                    if first:
                        temp = list(zip(*[c.apply(left, list(col)) for col in zip(*mat)]))
                        out = [c.apply(right, list(row)) for row in temp]
                    else:
                        temp = [c.apply(right, row) for row in mat]
                        out = list(zip(*[c.apply(left, list(col)) for col in zip(*temp)]))
                    for i, s in enumerate(tl):
                        for j, t in enumerate(tr):
                            pieces[s+tuple(nl+x for x in t)].append(out[i][j])
        return c.finish([c.total(pieces[t]) for t in c.targets])

    def export(self, h, path, selected=None):
        old = exporter.build
        try:
            if selected is None:
                exporter.build = self.build
            else:
                selected = set(map(tuple, selected))
                exporter.build = lambda *key: (self.build(*key) if key in selected
                                                else baseline.build(*key))
            return exporter.export(h, Path(path))
        finally:
            exporter.build = old

    def global_search(self, h, workdir, binary):
        """Greedy template substitution using whole-DAG fingerprint counts.

        Local gate minima can destroy sharing between tensor cases. Every
        accepted choice must instead lower the retained full-producer count.
        These are discovery counts only; independent exact checking is required.
        """
        workdir = Path(workdir)
        workdir.mkdir(parents=True, exist_ok=True)
        seen = {}
        original = exporter.build
        def record(*key):
            seen[key] = self.build(*key)
            return seen[key]
        try:
            exporter.build = record
            exporter.export(h, workdir/'all-optimized.bin')
        finally:
            exporter.build = original
        changes = sorted([key for key, c in seen.items()
                          if c.additions < baseline.build(*key).additions],
                         key=lambda key: seen[key].additions-baseline.build(*key).additions)
        selected = set()
        trials = []
        def screen(keys, tag):
            def choose(*key):
                return seen[key] if key in keys else baseline.build(*key)
            try:
                exporter.build = choose
                path = workdir/f'{tag}.bin'
                exporter.export(h, path)
            finally:
                exporter.build = original
            run = subprocess.run([str(binary), str(path)], check=True, capture_output=True, text=True)
            result = json.loads(run.stdout)
            return result['retained_additions_if_no_collision']
        best = screen(selected, 'baseline')
        print(json.dumps(dict(stage='baseline', additions=best)), flush=True)
        for i, key in enumerate(changes):
            count = screen(selected | {key}, f'trial-{i:02d}')
            accepted = count < best
            row = dict(state=key, additions=count, change=count-best, accepted=accepted)
            trials.append(row)
            print(json.dumps(row), flush=True)
            if accepted:
                selected.add(key)
                best = count
        screen(selected, 'selected')
        return dict(status='FINGERPRINT SCREEN; NOT EXACT CERTIFICATE', h=h,
                    additions=best, selected_states=sorted(selected), trials=trials)

    def report(self):
        return dict(trials=self.trials, cached_states=self.build.cache_info().currsize,
                    changed_states=[dict(state=key, **choice)
                                    for key, choice in sorted(self.choices.items())
                                    if choice['kind'] != 'inherited-half'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--h', type=int, default=28)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--selection', type=Path,
                        help='Previous report containing global_search.selected_states')
    parser.add_argument('--selected-h28', action='store_true',
                        help='Reproduce the retained 9,910,929-addition candidate')
    parser.add_argument('--splits', choices=('all', 'half'), default='all')
    parser.add_argument('--no-transpose', action='store_true')
    parser.add_argument('--orders', nargs='+', choices=('cost', 'left', 'right'), default=['cost'])
    parser.add_argument('--global-workdir', type=Path)
    parser.add_argument('--fingerprint-binary', type=Path,
                        default=Path('/private/tmp/ternary-target-fingerprint'))
    args = parser.parse_args()
    if args.selected_h28 and (args.h != 28 or args.selection):
        parser.error('--selected-h28 requires h=28 and no --selection')
    started = time.monotonic()
    search = Search(args.splits, not args.no_transpose, tuple(args.orders))
    selection = (json.loads(args.selection.read_text())['global_search']['selected_states']
                 if args.selection else None)
    if args.selected_h28:
        selection = H28_SELECTED_STATES
    result = dict(plan=search.export(args.h, args.plan, selection), search=search.report(),
                  elapsed_seconds=time.monotonic()-started)
    if args.global_workdir:
        result['global_search'] = search.global_search(args.h, args.global_workdir, args.fingerprint_binary)
    result['elapsed_seconds'] = time.monotonic()-started
    if args.report:
        args.report.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print(json.dumps(result, sort_keys=True), flush=True)
