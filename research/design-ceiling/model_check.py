#!/usr/bin/env python3
"""Check the lemmas of PROOF.md on a certified word (Python stdlib only; sanity, not part of the proof).

PROOF.md argues about every word on #144's paired-cube design through an abstraction: frame chains of physical
registers, units of a source, registers at a target's hyperplane. This script rebuilds that abstraction for one real
certified word, with the repository's own producer, and checks that

  1. the abstraction is the word's ledger: the children it lists are the certified child histogram, exactly;
  2. Lemma E: every source role enters at frame 0 and steps to its own line;
  3. Lemma D: every target of col(S) is reached through the exit of a unit of S (or at the line), and every source
     has two big units, or enough small units and line targets;
  4. Lemma T: every target has a register at its hyperplane, and two of them unless y_T has an intermediate stop;
  5. every unit, every source and every target pays at least the floor that the charging argument assigns to it,
     and the certified cost is above the design floor C(p) of ceiling.py.

Usage:  python3 research/design-ceiling/model_check.py [--tree PATH]
  --tree  a checkout of this repository (default: the tree containing this script, whose scripts regenerate #144's
          word at p = 12).  A tree with scripts/paired_cube_physical.py is read with its frame layer, reuse pairs
          and, if present, research/terminal-sinks.
"""
import argparse
import importlib
import json
import math
import sys
import tempfile
import time
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')

HERE = Path(__file__).resolve().parent
T0 = time.time()


def log(*a):
    print('[%4.0fs]' % (time.time() - T0), *a, flush=True)


def load(tree):
    sys.path.insert(0, str(tree / 'scripts'))
    cert = lambda name: json.loads((tree / 'certificates' / name).read_text())
    if (tree / 'scripts/paired_cube_physical.py').exists():
        PCP = importlib.import_module('paired_cube_physical')
        g, witness, word, record = PCP.regenerated_word()
        pairs = [(int(a), int(b)) for a, b, _ in json.loads((PCP.REF / 'pairs.json').read_text())['pairs']]
        moved = {int(i): tuple(F) for i, F in json.loads((PCP.REF / 'frames.json').read_text())['frames']}
        sink_file = tree / 'research/terminal-sinks/sinks.json'
        sinks = {int(s): int(p) for s, p in json.loads(sink_file.read_text())['sinks']} if sink_file.exists() else {}
        profile = cert('paired-cube-sinks-input.json' if sinks else 'paired-cube-physical-input.json')
        return g, witness, word, record, pairs, moved, sinks, profile
    producer = importlib.import_module('paired_cube_producer')
    record = cert('paired-cube-complex-input.json')
    with tempfile.TemporaryDirectory(prefix='design-ceiling-') as d:
        producer.regenerate(record, Path(d))
        g, witness, word = (json.loads((Path(d) / n).read_text()) for n in ('graph.json', 'frames.json', 'selection.json'))
    return g, witness, word, record, [], {}, {}, record


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path, default=HERE.parents[1])
    tree = ap.parse_args().tree.resolve()
    g, witness, word, record, pairs, moved, sinks, profile = load(tree)
    from paired_cube.frames import basis, perp, contained
    h, v, R = g['h'], g['v'], record['R']
    m, p = 3 * h, h // 2
    inputs = g['inputs']
    full = perp((), h)
    f = lambda r: r * math.log(m / r) if r > 0 else 0.0
    args = [None] + [None if a is None else (a[0] + 1, a[1] + 1) for a in g['args']]
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    ops = [tuple(o) for o in word['ops']]
    span = [()] * len(args)
    for x in range(1, len(args)):
        span[x] = (inputs[x - 1],) if args[x] is None else basis(span[args[x][0]] + span[args[x][1]])
    frame = [basis(moved[i]) if i in moved else perp(tuple(witness['annihilators'][x]), h) for i, (_, _, x) in enumerate(ops)]
    source_of = {s: int(x) - 1 for x, s in word['sources'].items()}
    gauge = {z['role']: perp(tuple(z['annihilator']), h) for z in word['selected']}
    gauge_targets = {z['role']: z['targets'] for z in word['selected']}
    root_frame, root_targets, star_dims = {}, {}, []
    for r, s in zip(roots, word['rootroles']):
        if r['kind'] == 'center':
            root_frame[s] = span[r['node']]
            star_dims.append(len(root_frame[s]))
        else:
            root_frame[s] = perp(basis(inputs[t] for t in r['targets']), h)
            root_targets[s] = list(r['targets'])
    role_ops = defaultdict(list)
    for i, (a, b, _) in enumerate(ops):
        role_ops[a].append(i)
        role_ops[b].append(i)
    donors = {a for a, _ in pairs}
    recipient_of = dict(pairs)
    is_recipient = {b for _, b in pairs}

    # ---- physical auxiliary registers: one ascending chain of frames per stage (PROOF.md, section 2.3)
    slots, children = {}, Counter()
    for s in range(R):
        if s in is_recipient or s in sinks:
            continue
        chain, merged = [()], 0
        for k, u in enumerate([s] + ([recipient_of[s]] if s in donors else [])):
            if k == 0 and u in source_of:
                chain.append((inputs[source_of[u]],))            # injection at the source line
            elif k == 0 and u in gauge:
                chain, merged = [gauge[u]], len(gauge[u])        # entrance gauge: one merged child of width 3 dim
            elif k > 0:
                chain.append(gauge[u])                           # hand-off into the recipient's gauge
            chain.extend(frame[i] for i in role_ops[u])
            if u in root_frame:
                chain.append(root_frame[u])
        chain.append(full)
        stops = [chain[0]]
        for F in chain[1:]:
            assert contained(stops[-1], F), 'a register chain does not ascend'
            if len(F) > len(stops[-1]):
                stops.append(F)
        steps = [len(b) - len(a) for a, b in zip(stops, stops[1:])]
        for r in steps:
            children[r] += 3
        if merged:
            children[3 * merged] += 1
        slots[s] = dict(stops=stops, cost=(f(3 * merged) if merged else 0.0) + 3 * sum(f(r) for r in steps))
    # ---- target registers: the frames at which the auxiliary word uses y_T
    y_stops = [set() for _ in range(v)]
    sink_groups = []
    for s, targets in gauge_targets.items():
        for t in targets:
            y_stops[t].add(gauge[s])
    for s, targets in root_targets.items():
        if s in sinks:
            pivot, U = sinks[s], root_frame[s]
            for i in role_ops[s]:
                assert ops[i][0] == s, 'a sink is written only as a destination'
                y_stops[pivot].add(frame[i])
            others = [t for t in targets if t != pivot]
            for t in others:
                y_stops[t].add(U)
                y_stops[pivot].add(U)
            sink_groups.append((pivot, U, others))
        else:
            for t in targets:
                y_stops[t].add(root_frame[s])
    line = [(q,) for q in inputs]
    hyper = [perp((q,), h) for q in inputs]
    y_cost = []
    for t in range(v):
        st = sorted(y_stops[t], key=len)
        assert all(contained(a, b) for a, b in zip(st, st[1:])) and all(contained(F, hyper[t]) for F in st)
        dims = sorted({0, h - 1} | {len(F) for F in st})
        steps = [b - a for a, b in zip(dims, dims[1:])]
        for r in steps:
            children[r] += 3
        y_cost.append(3 * sum(f(r) for r in steps))
    for r in (1, 2, h - 4):                                      # source registers: the K itinerary
        children[r] += 3 * v
    children[2] += 2 * v                                         # endpoint children
    for r in star_dims:
        children[r] += 3                                         # star copies
    certified = {int(r): n for r, n in profile['child_histogram'].items() if n}
    assert dict(children) == certified, 'the abstraction differs from the certified child histogram'
    C = sum(n * f(r) for r, n in certified.items())
    log('%s at p = %d: %d physical auxiliary registers, %d reuse pairs, %d sinks' % (
        'frame-layer word' if moved or pairs else 'gauged word', p, len(slots), len(pairs), len(sinks)))
    log('1. the abstraction lists exactly the certified children (C = %.0f)' % C)

    # ---- Lemma E
    for s, t in source_of.items():
        stops = slots[s]['stops']
        assert stops[0] == () and stops[1] == line[t], 'a source role does not step from 0 to its own line'
    log('2. Lemma E: every source role enters at frame 0 and steps to its own line')

    # ---- units, T-registers, Lemma D
    line_index = {line[t]: t for t in range(v)}
    hyper_index = {hyper[t]: t for t in range(v)}
    units, t_registers = defaultdict(list), defaultdict(list)
    for s, d in slots.items():
        for k, F in enumerate(d['stops']):
            if len(F) == 1 and F in line_index:
                units[line_index[F]].append((s, d['stops'][k + 1]))
            if len(F) == h - 1 and F in hyper_index:
                t_registers[hyper_index[F]].append(s)
    labels = [frozenset(l) for l in g['labels']]
    cube = [frozenset(c // 2 for c in l) for l in labels]
    mu, ncol = 4 * (p - 3), 12 * (p - 3) + 12 * comb(p - 3, 2) + 8 * comb(p - 3, 3)
    orthogonal = lambda F, q: all((x & q).bit_count() % 2 == 0 for x in F)
    U2 = f(3) + 3 * f(1) + 3 * f(h - 2)
    idle = f(3) + 3 * f(h - 1)
    eps, delta = f(1) + f(h - 3) - f(h - 2), f(1) + f(h - 2) - f(h - 1)
    rho = U2 / mu
    tau = min(6 * eps, 3 * delta + 3 * eps - rho)
    at_hyperplane = {s for regs in t_registers.values() for s in regs}
    kinds, unit_costs, payers = Counter(), [], defaultdict(set)
    for S in range(v):
        col = [T for T in range(v) if cube[T] != cube[S] and len(labels[T] & labels[S]) in (0, 2)]
        assert len(col) == ncol
        at_line = {T for T in col if line[S] in y_stops[T]}                       # L(S): line targets
        for pivot, U, others in sink_groups:                                       # L(S): pivot targets
            if line[S] in y_stops[pivot] and contained(line[S], U):
                at_line.update(T for T in others if T in col)
        for T in at_line:
            payers[T].add(S)
        big = [F for _, F in units[S] if 2 <= len(F) <= h - 2]
        small = [F for _, F in units[S] if len(F) == h - 1]
        kinds.update(big=len(big), small=len(small), idle=len(units[S]) - len(big) - len(small))
        reached = set(at_line)
        for F in big + small:
            reached.update(T for T in col if orthogonal(F, inputs[T]))
        assert reached >= set(col), 'a target of col(S) is not reached through a unit exit'
        assert len(big) >= 2 or (len(big) == 1 and len(at_line) + len(small) >= mu) or \
            (not big and len(at_line) + len(small) >= ncol), 'Lemma D'
        total = 0.0
        for s, F in units[S]:
            floor = idle if len(F) == h else U2 + (3 * eps if s in at_hyperplane and len(F) < h - 1 else 0.0)
            assert slots[s]['cost'] >= floor - 1e-9, 'a unit costs less than its floor'
            total += slots[s]['cost']
        assert total >= 2 * U2 + 3 * math.log(3) - 1e-9, 'a source pays less than two units'
        unit_costs.append(total)
    log('3. Lemma D: %d units (%s); every target of col(S) is reached through a unit exit; unit cost per source '
        'min %.1f, mean %.1f, floor %.1f' % (sum(kinds.values()), ', '.join('%d %s' % (n, k) for k, n in sorted(kinds.items())),
                                              min(unit_costs), sum(unit_costs) / v, 2 * U2 + 3 * math.log(3)))

    # ---- Lemma T and the target side of the charging argument
    plain = 0
    for T in range(v):
        between = [F for F in y_stops[T] if F and F != hyper[T]]
        n = len(t_registers[T])
        assert n >= 1 and (n >= 2 or between), 'Lemma T'
        plain += not between
        assert len(payers[T]) <= 2
        received = y_cost[T] - 3 * f(h - 1) + 3 * eps * min(n, 2) - rho * len(payers[T])
        assert received >= tau - 1e-9, 'a target collects less than tau'
    spread = Counter(len(t_registers[T]) for T in range(v))
    log('4. Lemma T: registers at a target hyperplane per target: %s; %d targets without an intermediate stop' % (
        dict(sorted(spread.items())), plain))

    # ---- the design floor of ceiling.py at this p (floats; ceiling.py has the exact version)
    D = 2 * v - 3 * record['loss']
    floor = v * (3 * (f(1) + f(2) + f(h - 4)) + 3 * f(h - 1) + 2 * f(2) + 2 * U2 + tau) \
        + (v - v // ncol) * (3 * f(1) - f(3)) + 3 * h * f(h - 2)
    assert D == profile['deficit_per_vertex'] and C >= floor
    log('5. certified cost %.0f >= design floor %.0f (%.1f%% of it); D/C = %.4e, D/floor = %.4e' % (
        C, floor, 100 * floor / C, D / C, D / floor))
    log('PASS the lemmas hold on this word')


if __name__ == '__main__':
    main()
