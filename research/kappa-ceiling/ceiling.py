#!/usr/bin/env python3
"""Rigorous ceilings on kappa for #168's paired-cube complex word (Python stdlib only; no -O).

PROOF.md states and proves the four facts used here.  For a shared-core profile with children n_r (0 < r < m),
W roles per vertex, deficit D = W m - sum r n_r and cost C = sum n_r r ln(m/r):

  1. every saving a certified by the repository's moment test satisfies a < D / C;
  2. kappa < min(certified bit saving, certified complex saving);
  3. a chain of frame steps of total rank t costs at least f(t) = t ln(m/t), and at least f(1) + f(t-1) if it has
     two or more steps;
  4. for a fixed complex word (its DAG, operations, carrier arcs, gauges, reuse pairs and terminal sinks), every
     admissible choice of operation frames has C >= C_floor, where C_floor relaxes the coupling between the two
     registers of an operation and minimises each register's chain exactly by dynamic programming.

Hence kappa < D / C_floor for every frame layout of that word.  The script

  - checks fact 1 numerically against the tree's certified bit and complex profiles (D/C next to the saving);
  - computes C_floor for the tree's complex word with exact integer arithmetic: every logarithm is replaced by a
    rational lower bound (partial sums of the atanh series), scaled down to the grid 2^-64, so the printed ceilings
    are upper bounds, rounded up;
  - prints the weaker design ceilings of PROOF.md (no auxiliary registers; no centre loss; one register per source).

#168's word is not on main, so by default the script rebuilds the 48 files of #168 it reads (scripts, frozen frames,
pairs, sinks, modules and certificates) in a temporary directory, from baseline-pr168.tar.gz.  Before use it checks
the archive's sha256 and every file's sha256 against SOURCE.json, whose hashes are those of commit 4a3c769.  Nothing
outside the temporary directory is read from or written to.

Usage:  python3 research/kappa-ceiling/ceiling.py [--check] [--tree PATH]
  --check  compare the results with expected.json
  --tree   run on a full checkout instead of the archive (for example one of #168).  A tree with
           scripts/paired_cube_physical.py is read with its physical layer and, if present, research/terminal-sinks.
"""
import argparse
import hashlib
import importlib
import io
import tarfile
import json
import math
import sys
import tempfile
import time
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')

HERE = Path(__file__).resolve().parent
SCALE = 64                                     # costs are integers in units of 2^-64, rounded down
T0 = time.time()


def log(*a):
    print('[%4.0fs]' % (time.time() - T0), *a, flush=True)


# ---------------------------------------------------------------------------------------------- rigorous logarithms
def log_lower(x):
    """A rational lower bound on ln x for rational x >= 1: k ln 2 + ln y with y in [1, 2), each from partial sums of
    2 atanh((y-1)/(y+1)), whose terms are all nonnegative.  The truncation error is below 3^-80."""
    assert x >= 1
    def series(y):
        z = (y - 1) / (y + 1)
        return 2 * sum((z ** (2 * j + 1) / (2 * j + 1) for j in range(40)), Q(0))
    k = 0
    while x >= 2:
        x /= 2
        k += 1
    return k * series(Q(2)) + series(x)


def assembly_ceiling(a, balanced, eta=Q(1, 10**8)):
    """The largest kappa the repository's assembly can accept from a supplier saving a (its minimum margin
    epsilon*q), in the closed form of PR #183 (romainhedouin): q = a(1 - 2 eta) and G = q(1 - eta)/(1 + q) for the
    balanced prefix (scripts/paired_cube_assembly.py), G = q(1 - eta)/(1 + q(2 + eta)) for the original prefix
    (scripts/structured_bulk_assembly.py).  G is increasing in a."""
    q = a * (1 - 2 * eta)
    return q * (1 - eta) / (1 + q) if balanced else q * (1 - eta) / (1 + q * (2 + eta))


def cost_table(m):
    """f(r) = r ln(m/r), as integers rounded down in units of 2^-SCALE, for 0 <= r < m."""
    out = [0] * m
    for r in range(1, m):
        val = r * log_lower(Q(m, r))
        out[r] = (val.numerator << SCALE) // val.denominator
    return out


# ---------------------------------------------------------------------------------------------- the tree's word
def load(tree):
    """Regenerate the tree's complex word with the tree's own scripts.  Returns a dict with the graph, witness, word,
    record, reuse pairs, sink roles and the certified complex and bit profiles."""
    sys.path.insert(0, str(tree / 'scripts'))
    cert = lambda name: json.loads((tree / 'certificates' / name).read_text())
    pcn = importlib.import_module('paired_cube_network')
    physical = (tree / 'scripts/paired_cube_physical.py').exists()
    if physical:
        PCP = importlib.import_module('paired_cube_physical')
        g, witness, word, record = PCP.regenerated_word()
        pairs = [(int(a), int(b)) for a, b, _ in json.loads((PCP.REF / 'pairs.json').read_text())['pairs']]
        moved = {int(i): tuple(F) for i, F in json.loads((PCP.REF / 'frames.json').read_text())['frames']}
        base_profile = cert('paired-cube-physical-input.json')
        sink_file = tree / 'research/terminal-sinks/sinks.json'
        sinks = [int(s) for s, _ in json.loads(sink_file.read_text())['sinks']] if sink_file.exists() else []
        sink_root = {}
        for r, s in zip(g['roots'], word['rootroles']):
            if s in sinks:
                from paired_cube.frames import basis, perp
                sink_root[s] = perp(basis(g['inputs'][t] for t in r['targets']), g['h'])
        complex_profile = cert('paired-cube-sinks-input.json' if sinks else 'paired-cube-physical-input.json')
        bit_name = 'paired-cube-bit-physical-input.json'
    else:
        producer = importlib.import_module('paired_cube_producer')
        with tempfile.TemporaryDirectory(prefix='kappa-ceiling-') as d:
            producer.regenerate(cert('paired-cube-complex-input.json'), Path(d))
            g, witness, word = (json.loads((Path(d) / n).read_text()) for n in ('graph.json', 'frames.json', 'selection.json'))
        record = cert('paired-cube-complex-input.json')
        pairs, sinks, complex_profile, moved, base_profile, sink_root = [], [], record, {}, record, {}
        bit_name = 'paired-cube-bit-input.json'
    bit_profile = cert(bit_name) if (tree / 'certificates' / bit_name).exists() else None
    return dict(pcn=pcn, g=g, witness=witness, word=word, record=record, pairs=pairs, sinks=sinks, moved=moved, sink_root=sink_root,
                complex_profile=complex_profile, base_profile=base_profile, bit_profile=bit_profile, physical=physical)


def slot_chains(T):
    """The physical slots of the complex word and, for each, its events in time order: (start subspace, events),
    each event (lo, hi) bounding the frame the slot must occupy at that moment.  Mirrors the role chains of
    scripts/paired_cube/verify.py and scripts/paired_cube_physical.py:
      start = 0, the source line <q_S> for an injected source, or the gauge sigma of a gauged first occupant;
      op of node x: span(x) <= frame <= the full backward intersection of x (any admissible frame lies there);
      side or centre root read, recipient's gauge read: exactly that frame;
      the end of the chain is the full space.
    A recipient continues its donor's slot (the hand-off is the step into its gauge)."""
    from paired_cube.frames import basis, perp
    g, witness, word, record = T['g'], T['witness'], T['word'], T['record']
    h, R = g['h'], record['R']
    inputs = g['inputs']
    args = [None] + [None if a is None else (a[0] + 1, a[1] + 1) for a in g['args']]
    roots = [dict(r, node=r['node'] + 1) for r in g['roots']]
    ann = witness['annihilators']
    ops = [tuple(o) for o in word['ops']]
    span = [()] * len(args)
    for x in range(1, len(args)):
        span[x] = (inputs[x - 1],) if args[x] is None else basis(span[args[x][0]] + span[args[x][1]])
    upper = {x: perp(tuple(ann[x]), h) for _, _, x in ops}
    sources = {int(x): s for x, s in word['sources'].items()}
    source_line = {s: (inputs[x - 1],) for x, s in sources.items()}
    gauge = {z['role']: perp(tuple(z['annihilator']), h) for z in word['selected']}
    rootframe = {}
    for r, s in zip(roots, word['rootroles']):
        rootframe[s] = span[r['node']] if r['kind'] == 'center' else perp(basis(inputs[t] for t in r['targets']), h)
    role_ops = defaultdict(list)
    for i, (a, b, _) in enumerate(ops):
        role_ops[a].append(i)
        role_ops[b].append(i)
    donor_of = {b: a for a, b in T['pairs']}
    recipient_of = {a: b for a, b in T['pairs']}
    sinks = set(T['sinks'])
    assert not sinks & (set(donor_of) | set(recipient_of) | set(gauge) | set(sources.values()))
    # joint bounds: an operation's frame is shared by both of its registers, so it contains everything either
    # register has accumulated (forward pass) and lies in everything either will need later (backward pass)
    join = lambda A, B: basis(A + B)
    meet = lambda A, B: perp(basis(perp(A, h) + perp(B, h)), h)
    full = perp((), h)
    entry = {}
    for s in range(R):
        entry[s] = source_line.get(s, gauge.get(s, ()))
    # a terminal sink is deleted in the certified word: its writes go to a target register instead, so the
    # propagation does not pass through sink registers (dropping constraints only weakens the bounds)
    live = lambda r: r not in sinks
    lo, cur = [None] * len(ops), dict(entry)
    for i, (a, b, x) in enumerate(ops):
        F = span[x]
        for r in (a, b):
            if live(r): F = join(F, cur[r])
        lo[i] = F
        for r in (a, b):
            if live(r): cur[r] = F
    leave = {}
    for s in range(R):
        leave[s] = rootframe.get(s, gauge[recipient_of[s]] if s in recipient_of else full)
    hi, cur = [None] * len(ops), dict(leave)
    for i in reversed(range(len(ops))):
        a, b, x = ops[i]
        U = upper[x]
        for r in (a, b):
            if live(r): U = meet(U, cur[r])
        hi[i] = U
        for r in (a, b):
            if live(r): cur[r] = U
    for i in range(len(ops)):
        assert len(join(lo[i], hi[i])) == len(hi[i]), 'joint bounds infeasible'
        A = T['moved'].get(i, upper[ops[i][2]])       # self-test: the tree's own layout respects every bound
        assert len(join(lo[i], A)) == len(A) and len(join(A, hi[i])) == len(hi[i]), 'tree layout outside the bounds at op %d' % i
    slots, gauged_starts = [], []
    for s in range(R):
        if s in donor_of:
            continue
        start, events = (), []
        lives = [s] + ([recipient_of[s]] if s in recipient_of else [])
        for k, u in enumerate(lives):
            if k == 0 and u in source_line:
                events.append((source_line[u], source_line[u], source_line[u], None))
            elif k == 0 and u in gauge:
                start = gauge[u]
                gauged_starts.append(len(gauge[u]))
            elif k > 0:
                events.append((gauge[u], gauge[u], gauge[u], None))
            for i in role_ops[u]:
                a, b, x = ops[i]
                tag = (i, 1 if a == u else -1) if live(a) and live(b) else None
                events.append((lo[i], hi[i], T['moved'].get(i, upper[x]), tag))
            if u in rootframe:
                events.append((rootframe[u], rootframe[u], rootframe[u], None))
        slots.append((s, start, events, s in sinks))
    centres = [len(rootframe[s]) for r, s in zip(roots, word['rootroles']) if r['kind'] == 'center']
    return slots, gauged_starts, centres


def slot_bounds(start, events, h, basis, perp):
    """Dimension bounds of a slot at each event: the frame contains the join of the lower bounds of events 0..i
    (frames nest upward) and lies in the intersection of the upper bounds of events i..end."""
    n = len(events)
    lo, acc = [0] * n, start
    for i, ev in enumerate(events):
        acc = basis(acc + ev[0])
        lo[i] = len(acc)
    hi, acc = [0] * n, perp((), h)
    for i in reversed(range(n)):
        acc = perp(basis(perp(acc, h) + perp(events[i][1], h)), h)
        hi[i] = len(acc)
    assert all(l <= u for l, u in zip(lo, hi)), 'infeasible slot'
    return lo, hi


def slot_dp(d_start, lo, hi, tags, h, F, price):
    """min over nondecreasing dimensions d_i in [lo_i, hi_i] of  sum f(d_i - d_(i-1)) + f(h - d_last)
    + sum sign * price[op] * d_i  (the Lagrangian term of coupled events).  Exact integers.  Returns (cost, dims)."""
    best, back = {d_start: 0}, []
    for i in range(len(lo)):
        w = 0
        if tags[i] is not None:
            w = tags[i][1] * price.get(tags[i][0], 0)
        nxt, arg = {}, {}
        for d in range(lo[i], hi[i] + 1):
            c, p = None, None
            for d0, c0 in best.items():
                if d0 <= d and (c is None or c0 + F[d - d0] < c):
                    c, p = c0 + F[d - d0], d0
            if c is not None:
                nxt[d], arg[d] = c + w * d, p
        best = nxt
        back.append(arg)
    d = min(best, key=lambda e: best[e] + F[h - e])
    cost = best[d] + F[h - d]
    dims = [0] * len(lo)
    for i in reversed(range(len(lo))):
        dims[i] = d
        d = back[i][d]
    return cost, dims


def rebuild(dest):
    """Write the pinned #168 files into dest after checking the archive and every file against SOURCE.json."""
    src = json.loads((HERE / 'SOURCE.json').read_text())
    data = (HERE / src['archive']).read_bytes()
    if hashlib.sha256(data).hexdigest() != src['archive_sha256']:
        raise SystemExit('baseline archive differs from SOURCE.json')
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
        members = [x for x in archive.getmembers() if x.isfile()]
        if sorted(x.name for x in members) != sorted(src['files']):
            raise SystemExit('baseline archive lists other files than SOURCE.json')
        for x in members:
            part = Path(x.name)
            if part.is_absolute() or '..' in part.parts:
                raise SystemExit('unsafe path in baseline archive: ' + x.name)
            body = archive.extractfile(x).read()
            if hashlib.sha256(body).hexdigest() != src['files'][x.name]:
                raise SystemExit('baseline file differs from SOURCE.json: ' + x.name)
            (dest / part).parent.mkdir(parents=True, exist_ok=True)
            (dest / part).write_bytes(body)
    return src['commit']


# ---------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path, default=None)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--rounds', type=int, default=400, help='Lagrangian rounds (default 400)')
    a = ap.parse_args()
    if a.tree is not None:
        return run(a, a.tree.resolve())
    with tempfile.TemporaryDirectory(prefix='kappa-ceiling-pr168-') as d:
        commit = rebuild(Path(d))
        log('rebuilt the pinned files of #168 (commit %s) from baseline-pr168.tar.gz; hashes match SOURCE.json' % commit[:7])
        return run(a, Path(d).resolve())


def run(a, tree):
    T = load(tree)
    pcn, rec = T['pcn'], T['record']
    from paired_cube.frames import basis, perp
    h, v, ell = rec['h'], rec['v'], rec['loss']
    m, D = 3 * h, 2 * v - 3 * rec['loss']
    F = cost_table(m)
    unit = Q(1, 1 << SCALE)
    balanced = (tree / 'scripts/paired_cube_assembly.py').exists()
    G = lambda a: assembly_ceiling(a, balanced)
    out = dict(tree=str(tree), mode='physical layer' if T['physical'] else 'gauged word', h=h, v=v, loss=ell, D=D,
               assembly='balanced prefix' if balanced else 'original prefix')
    log('tree %s (%s): h %d, v %d, centre loss %d, deficit D = 2v - 3 loss = %d' % (tree, out['mode'], h, v, ell, D))

    # fact 1, numerically: D/C of each certified profile against its certified saving
    f = lambda r: r * math.log(m / r)
    def ratio(p):
        H = {int(r): n for r, n in p['child_histogram'].items()}
        mm = p['m']
        return p['deficit_per_vertex'] / math.fsum(n * r * math.log(mm / r) for r, n in H.items() if r)
    rc = ratio(T['complex_profile'])
    log('fact 1, complex: certified saving %.7e < D/C = %.7e (gap %.3f%%)' % (float(pcn.AC), rc, 100 * (1 - float(pcn.AC) / rc)))
    assert pcn.AC < rc
    if T['bit_profile'] is not None and 'child_histogram' in T['bit_profile']:
        rb = ratio(T['bit_profile'])
        log('fact 1, bit:     certified coarse saving %.7e < D/C = %.7e (gap %.3f%%)' % (
            float(pcn.COARSE), rb, 100 * (1 - float(pcn.COARSE) / rb)))
        assert pcn.COARSE < rb
    assert pcn.KAPPA < G(min(pcn.AC, pcn.COARSE)) < min(pcn.AC, pcn.COARSE)
    log('fact 2 (%s): kappa %s < G(min(complex %s, bit coarse %s)) = %.7e' % (
        out['assembly'], pcn.KAPPA, pcn.AC, pcn.COARSE, float(G(min(pcn.AC, pcn.COARSE)))))

    # fact 4: the frame-layout floor of this word
    slots, gauged_starts, centres = slot_chains(T)
    from collections import Counter
    # self-test 1: with the tree's own frames, the slot chains (sinks included) reproduce the certified ledger of the
    # word before sinks exactly, and no slot's floor exceeds its actual chain
    local, sink_steps, prepared, actual_total = Counter(), Counter(), [], 0
    for s, start, ev, is_sink in slots:
        dims = [len(start)] + [len(e[2]) for e in ev] + [h]
        steps = [b - c for c, b in zip(dims, dims[1:]) if b > c]
        local.update(steps)
        lo, hi = slot_bounds(start, ev, h, basis, perp)
        tags = [e[3] for e in ev]
        own, _ = slot_dp(len(start), lo, hi, tags, h, F, {})
        assert own <= sum(F[r] for r in steps), 'floor above the actual chain of slot %d' % s
        if is_sink:
            sink_steps.update((len(T['sink_root'][s]), h - len(T['sink_root'][s])))
        else:
            prepared.append((len(start), lo, hi, tags))
            actual_total += sum(F[r] for r in steps)
    base = T['base_profile']
    children = Counter()
    for r, n in local.items(): children[r] += 3 * n
    for name in ('source_data_histogram', 'target_data_histogram'):
        for r, n in base[name].items():
            if int(r): children[int(r)] += 3 * n
    for r in centres: children[r] += 3
    for d in gauged_starts: children[3 * d] += 1
    children[2] += 2 * v
    assert dict(children) == {int(r): n for r, n in base['child_histogram'].items() if n}, 'slot model differs from the certified ledger'
    if T['sinks']:   # the certified sink record removes exactly [r] and [h - r] per sink and stage (research/terminal-sinks)
        less = Counter({int(r): n for r, n in base['child_histogram'].items()})
        for r, n in sink_steps.items(): less[r] -= 3 * n
        assert +less == Counter({int(r): n for r, n in T['complex_profile']['child_histogram'].items()}), 'sink record'
    slots = [x for x in slots if not x[3]]
    log('self-test: the tree layout lies inside every derived frame bound; its slot chains reproduce the certified '
        'complex ledger exactly; every slot floor is below its actual chain')
    # Lagrangian coupling: each round's total is a valid floor (the price terms cancel on any common-frame layout);
    # prices move along the disagreement between the two registers of each operation (integer subgradient steps)
    price, best, step, history = {}, None, (6 << SCALE) // 10, []
    for k in range(a.rounds + 1):
        total, grad = 0, defaultdict(int)
        for d0, lo, hi, tags in prepared:
            c, dims = slot_dp(d0, lo, hi, tags, h, F, price)
            total += c
            for tg, d in zip(tags, dims):
                if tg is not None:
                    grad[tg[0]] += tg[1] * d
        assert total <= actual_total, 'Lagrangian floor above the tree layout'
        history.append(total)
        if best is None or total > best:
            best = total
        if k == 0:
            independent = total
        for i, g in grad.items():
            if g:
                price[i] = price.get(i, 0) + step * g
        step = step * 995 // 1000
    two_step = len(slots) * (F[1] + F[h - 1])
    fixed = 3 * 2 * v * F[h - 1] + 2 * v * F[2] + 3 * sum(F[r] for r in centres) + sum(F[3 * d] for d in gauged_starts)
    C_dp, C_ind, C_two = (3 * best + fixed) * unit, (3 * independent + fixed) * unit, (3 * two_step + fixed) * unit
    C_actual = Q(math.fsum(n * f(int(r)) for r, n in T['complex_profile']['child_histogram'].items() if int(r)))
    ceil7 = lambda x: -((-x.numerator * 10**7) // x.denominator)          # round up on the 10^-7 grid
    out.update(physical_slots=len(slots), sinks=len(T['sinks']), reuse_pairs=len(T['pairs']),
               C_certified=float(C_actual), C_floor=float(C_dp),
               ceiling_frames='%d/10^7' % ceil7(G(Q(D) / C_dp)), ceiling_two_step='%d/10^7' % ceil7(G(Q(D) / C_two)),
               ceiling_uncoupled='%d/10^7' % ceil7(G(Q(D) / C_ind)), rounds=a.rounds,
               kappa=str(pcn.KAPPA))
    log('fact 4: %d physical slots (%d reuse pairs, %d sinks); certified C = %.0f; floor C >= %.0f' % (
        len(slots), len(T['pairs']), len(T['sinks']), C_actual, C_dp))
    log('CEILING (any frames for this word):        kappa < %s = %.7e   [kappa %.7e is %.1f%% of it]' % (
        out['ceiling_frames'], ceil7(G(Q(D) / C_dp)) / 1e7, float(pcn.KAPPA), 100 * float(pcn.KAPPA) / (ceil7(G(Q(D) / C_dp)) / 1e7)))
    log('without coupling the two registers of an operation: kappa < %s' % out['ceiling_uncoupled'])
    log('with only two steps per slot:                       kappa < %s' % out['ceiling_two_step'])

    # design ceilings (PROOF.md, section 5): the same h, v and decoder, any word
    data_end_centres = (3 * 2 * v * F[h - 1] + 2 * v * F[2] + 3 * sum(F[r] for r in centres)) * unit
    one_per_source = (3 * v * (F[1] + F[h - 1])) * unit
    design = dict(one_register_per_source='%d/10^7' % ceil7(G(Q(D) / (data_end_centres + one_per_source))),
                  no_auxiliary_registers='%d/10^7' % ceil7(G(Q(D) / data_end_centres)),
                  no_auxiliary_registers_and_no_centre_loss='%d/10^7' % ceil7(G(Q(2 * v) / ((3 * 2 * v * F[h - 1] + 2 * v * F[2]) * unit))))
    out['design'] = design
    log('design ceilings: one register per source %s, no auxiliary registers %s, no centre loss either %s' % (
        design['one_register_per_source'], design['no_auxiliary_registers'], design['no_auxiliary_registers_and_no_centre_loss']))
    if a.check:
        expected = json.loads((HERE / 'expected.json').read_text())
        keys = ('h', 'v', 'loss', 'D', 'physical_slots', 'ceiling_frames', 'ceiling_uncoupled', 'ceiling_two_step', 'design', 'kappa', 'rounds')
        assert {k: out[k] for k in keys} == {k: expected[k] for k in keys}, 'results differ from expected.json'
        log('PASS results equal expected.json')
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
