#!/usr/bin/env python3
"""Rigorous ceiling on the bit saving, and hence on kappa, for every operation-frame layout of #200's physical bit
word (Python stdlib only; no -O).  The method is DaysSky's #192 (research/kappa-ceiling), carried from #168's complex
word to the bit word that #200, #205, #206 and #207 share.

For a shared-core bit profile with children n_r (0 < r < m), W roles per vertex, deficit D = W m - sum r n_r and
cost C = sum n_r r ln(m/r):

  1. every coarse saving a certified by the paid moment test satisfies a < D / C  (e^x >= 1 + x);
  2. the balanced assembly accepts kappa only below a (1 - 2 eta)(1 - eta) / (1 + a (1 - 2 eta)) < a / (1 + a)
     (#183, romainhedouin), and the finite ordinary-leaf bootstrap of #185/#197/#207 stays below the coarse saving
     it starts from (a_j = (1 - c) c + c a_(j-1) < c);
  3. a chain of frame steps of total rank t costs at least f(t) = t ln(m/t) (f is subadditive);
  4. for the fixed word (DAG, operations and their order, sources, gauges, reuse pairs, partner chronology and terminal
     sinks), every admissible choice of operation frames has C >= C_floor, where C_floor propagates frame bounds
     jointly through both registers of every operation, minimises each physical slot's chain exactly by dynamic
     programming over frame dimensions, and couples the two registers of each operation by Lagrangian prices.

Hence coarse < D / C_floor and kappa < G(D / C_floor) for every frame layout of the word.  Two ledgers are priced:
#200's own (gauged first occupants pay 3 dim sigma) and the completed-entrance-bank ledger of #205/#206/#207 (those
children removed, nothing else changed), so the ceiling also covers the banked rows built on this word.

All costs are exact integers in units of 2^-64 with every logarithm replaced by a rational lower bound, so the printed
ceilings are true upper bounds, rounded up.  By default the script rebuilds the eight pinned files of #200 it reads
(the frozen physical bit word, frames, partner chronology, graph, profile, sinks, certificate and the retained
PR168-v4 exact integer checker) in a temporary directory from baseline-pr200.tar.gz after checking every sha256
against SOURCE.json (commit a1175449).  Nothing outside the temporary directory is read or written.

Usage:  python3 research/bit-frame-ceiling-200/ceiling.py [--check] [--tree PATH] [--rounds N] [--overrides FILE]
  --check      compare the results with expected.json
  --tree       run on a checkout of #200 (its root or research/paired-cube-diagonal-bit-168) instead of the archive
  --overrides  also test another layout of the same word, given as #207's frames/opframe-bases.json ([op, rows]...)
"""
import argparse
import hashlib
import importlib.util
import io
import json
import math
import sys
import tarfile
import tempfile
import time
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

if sys.flags.optimize:
    raise SystemExit('Assertions must remain enabled: run without -O')
sys.set_int_max_str_digits(0)
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
PKG = 'research/paired-cube-diagonal-bit-168'
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


def cost_table(m):
    """f(r) = r ln(m/r), as integers rounded down in units of 2^-SCALE, for 0 <= r < m."""
    out = [0] * m
    for r in range(1, m):
        val = r * log_lower(Q(m, r))
        out[r] = (val.numerator << SCALE) // val.denominator
    return out


def G(a):
    """Every acceptance region used by the retained assemblies lies below a/(1+a) (#183: q(1-eta)/(1+q) with
    q = a(1-2 eta), increasing in a and decreasing in eta; the limit eta -> 0 is the weakest bound)."""
    return a / (1 + a)


def ceil7(x):
    return -((-x.numerator * 10**7) // x.denominator)          # round up on the 10^-7 grid


# ---------------------------------------------------------------------------------------------- the pinned files
def rebuild(dest):
    """Write the pinned #200 files into dest after checking the archive and every file against SOURCE.json."""
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


def read(p):
    import gzip
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


def load(tree):
    """The retained exact integer checker on #200's frozen bit word, with its geometry (frames, decoder supports,
    coordinate rows, target covectors) prepared, plus the sinks and the certified bit record."""
    pkg = tree if (tree / 'selected/bit').exists() else tree / PKG
    path = pkg / 'references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py'
    spec = importlib.util.spec_from_file_location('check_paired_cube_bit', path)
    backend = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(backend)
    C = backend.Checker.__new__(backend.Checker)
    C.mut = None
    B = pkg / 'selected/bit'
    C.g, C.prof, C.w, C.fr, C.k = (read(B / n) for n in ('graph_p12.json', 'profile_p12.json', 'word_p12.json.gz',
                                                           'frames_p12.json.gz', 'kchron_p12.json'))
    C.h, C.v = C.g['h'], C.g['v']
    C.frames()
    C.decoder()
    C.geometry()
    sinks = json.loads((B / 'sinks.json').read_text())
    cert = json.loads((pkg / 'certificate.json').read_text())
    return dict(C=C, backend=backend, sinks=sinks, cert=cert['bit'], kappa=cert.get('kappa'), pkg=pkg)


# ---------------------------------------------------------------------------------------------- the word's chains
class Word:
    """Mirrors the role, partner and target chains of the retained physical checker (PR168 v4
    scripts/paired_cube_bit_physical.py), and derives the joint frame bounds of #192, Lemma 4a."""

    def __init__(self, T):
        C, backend = T['C'], T['backend']
        self.C, self.mod = C, backend
        w, h = C.w, C.h
        self.w, self.h, self.m, self.v = w, h, 3 * h, C.v
        self.ops = [tuple(o) for o in w['ops']]
        self.opf = list(w['op_frame'])
        assert len(self.opf) == len(self.ops)
        self.ids = {tuple(B): f for f, B in C.B.items()}
        phase = set(w['phase1'])
        self.order = sorted(phase) + [i for i in range(len(self.ops)) if i not in phase]
        self.position = {i: p for p, i in enumerate(self.order)}
        self.cut = len(phase)
        self.sources = {int(x): s for x, s in w['sources'].items()}
        self.R = 1 + max(max(max(a, b) for a, b, _ in self.ops), max(w['rootroles']), max(self.sources.values()))
        self.start = {s: w['source_frame'][x] for x, s in self.sources.items()}
        self.gauge = {z['role']: z for z in w['gauges']}
        for s, z in self.gauge.items():
            assert s not in self.start
            self.start[s] = z['frame']
        self.rootframe = {s: w['root_frame'][j] for j, s in enumerate(w['rootroles'])}
        self.full = w['full_frame']
        self.zero = self.register([])
        self.role_ops = defaultdict(list)
        for i in self.order:
            for s in self.ops[i][:2]:
                self.role_ops[s].append(i)
        self.pairs = [(int(a), int(b)) for a, b in w.get('pairs', [])]
        self.recipient_of = {a: b for a, b in self.pairs}
        self.donor_of = {b: a for a, b in self.pairs}
        reads = {int(s): t for s, t in w.get('reads', {}).items()}
        self.when = {}
        for k, z in enumerate(reversed(w['gauges'])):
            self.when[z['role']] = (reads.get(z['role'], self.cut), k)
        self.sinkroles = {w['rootroles'][e['root']] for e in T['sinks']}
        assert len(self.sinkroles) == len(T['sinks'])
        assert not self.sinkroles & (set(self.donor_of) | set(self.recipient_of) | set(self.gauge) | set(self.sources.values()))

    # exact linear algebra over the h coordinates, through the retained checker
    def register(self, rows):
        C, mod = self.C, self.mod
        B, _ = mod.reduce_rows(rows, self.h)
        B = tuple(sorted(map(tuple, B), key=lambda r: next(i for i, x in enumerate(r) if x)))
        if B in self.ids:
            return self.ids[B]
        f = max(C.B) + 1
        A, _ = mod.kernel(B, self.h)
        C.B[f], C.A[f], C.dimf[f] = B, A, len(B)
        self.ids[B] = f
        return f

    def join(self, *fs):
        return self.register([row for f in fs for row in self.C.B[f]])

    def meet(self, *fs):
        rows, _ = self.mod.kernel([row for f in fs for row in self.C.A[f]], self.h)
        return self.register(rows)

    def dim(self, f):
        return self.C.dimf[f]

    def sub(self, f, g):
        return self.C.sub(f, g)

    def span(self, x):
        bits, rows = self.C.sup[x], []
        while bits:
            b = bits & -bits
            bits -= b
            rows.append(self.C.chi[b.bit_length() - 1])
        return self.register(rows)

    def bounds(self):
        """Lemma 4a: L_i = span(x_i) + previous frames of both registers; U_i = next frames of both registers.
        Sink registers take part: every admitted layout is first admitted as a complete pre-sink layout, and the
        terminal record then substitutes fixed children (see run)."""
        live = lambda r: True
        cur = {s: self.start.get(s, self.zero) for s in range(self.R)}
        lo = [None] * len(self.ops)
        for i in self.order:
            a, b, x = self.ops[i]
            F = self.span(x)
            for r in (a, b):
                if live(r):
                    F = self.join(F, cur[r])
            lo[i] = F
            for r in (a, b):
                if live(r):
                    cur[r] = F
        cur = {s: self.rootframe.get(s, self.gauge[self.recipient_of[s]]['frame'] if s in self.recipient_of else self.full)
               for s in range(self.R)}
        hi = [None] * len(self.ops)
        for i in reversed(self.order):
            a, b, x = self.ops[i]
            U = cur[a] if live(a) else self.full
            if live(b):
                U = self.meet(U, cur[b])
            hi[i] = U
            for r in (a, b):
                if live(r):
                    cur[r] = U
        for i in range(len(self.ops)):
            assert self.sub(lo[i], hi[i]), 'joint bounds infeasible at op %d' % i
        self.lo, self.hi = lo, hi
        return lo, hi

    def inside(self, opf):
        return all(self.sub(self.lo[i], opf[i]) and self.sub(opf[i], self.hi[i]) for i in range(len(self.ops)))

    def slots(self):
        """Physical slots with their events (lo, hi, tag): a recipient continues its donor's slot through the exact
        step into its gauge; a root is read at its root frame; the chain ends at the full space."""
        live = lambda r: True
        out = []
        for s in range(self.R):
            if s in self.donor_of:
                continue
            events = []
            lives = [s] + ([self.recipient_of[s]] if s in self.recipient_of else [])
            for k, u in enumerate(lives):
                if k > 0:
                    g = self.gauge[u]['frame']
                    events.append((g, g, None))
                for i in self.role_ops[u]:
                    a, b, _ = self.ops[i]
                    tag = (i, 1 if a == u else -1) if live(a) and live(b) else None
                    events.append((self.lo[i], self.hi[i], tag))
                if u in self.rootframe:
                    events.append((self.rootframe[u], self.rootframe[u], None))
            if not events and s not in self.start:
                continue
            out.append((s, self.start.get(s, self.zero), events, s in self.sinkroles))
        return out

    def chain_dims(self, s, opf):
        """The actual frame dimensions along slot s under layout opf (the checker's chain(s), spliced at a pair)."""
        seq = [self.start.get(s)]
        lives = [s] + ([self.recipient_of[s]] if s in self.recipient_of else [])
        for k, u in enumerate(lives):
            if k > 0:
                seq.append(self.gauge[u]['frame'])
            seq += [opf[i] for i in self.role_ops[u]]
            if u in self.rootframe:
                seq.append(self.rootframe[u])
        seq.append(self.full)
        d0, steps = (0 if seq[0] is None else self.dim(seq[0])), []
        for f in seq[1:]:
            d = self.dim(f)
            assert d >= d0
            if d > d0:
                steps.append(d - d0)
            d0 = d
        return steps

    def fixed_children(self):
        """The children that no layout changes: source injections, copied centres, partner (source data) chains,
        target chains (gauge reads, side caps, partner deliveries), gauged first occupants and the 2v data children."""
        C, w, h, v = self.C, self.w, self.h, self.v
        dim = self.dim
        injections = sum(1 for s in self.sources.values() if s not in self.gauge)
        centres = [dim(w['root_frame'][j]) for j, r in enumerate(C.g['roots']) if r['kind'] == 'center']
        source = Counter()
        for e in C.k['entries']:
            c, d = e['carrier'], e['passive']
            for ch in ((w['source_frame'][c], e['mix_frame'], e['deliver_frame'], self.full),
                       (w['source_frame'][d], e['mix_frame'], self.full)):
                for f1, f2 in zip(ch, ch[1:]):
                    assert self.sub(f1, f2)
                    source[dim(f2) - dim(f1)] += 1
        events = defaultdict(list)
        for s in sorted(self.when, key=self.when.get):
            for t in self.gauge[s]['targets']:
                events[t].append(self.gauge[s]['frame'])
        deliveries = defaultdict(list)
        for e in C.k['entries']:
            deliveries[e['deliver_after_root']].append(e)
        for j, r in enumerate(C.g['roots']):
            if r['kind'] == 'side':
                for t in r['targets']:
                    events[t].append(w['root_frame'][j])
                for e in deliveries.get(j, ()):
                    for t in e['receivers']:
                        events[t].append(e['deliver_frame'])
        target = Counter()
        for t in range(v):
            prev, d0 = None, 0
            for f in events[t]:
                assert prev is None or self.sub(prev, f)
                if dim(f) > d0:
                    target[dim(f) - d0] += 1
                prev, d0 = f, dim(f)
            assert d0 <= h - 1
            if d0 < h - 1:
                target[h - 1 - d0] += 1
        tails = Counter(dim(z['frame']) for s, z in self.gauge.items() if s not in self.donor_of)
        return dict(injections=injections, centres=centres, source=source, target=target, tails=tails)


# ---------------------------------------------------------------------------------------------- the slot floor
def slot_bounds(W, start, events):
    n = len(events)
    lo, acc = [0] * n, start
    for i, ev in enumerate(events):
        acc = W.join(acc, ev[0])
        lo[i] = W.dim(acc)
    hi, acc = [0] * n, W.full
    for i in reversed(range(n)):
        acc = W.meet(acc, events[i][1])
        hi[i] = W.dim(acc)
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


# ---------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--tree', type=Path, default=None)
    ap.add_argument('--check', action='store_true')
    ap.add_argument('--rounds', type=int, default=1200, help='Lagrangian rounds (default 1200)')
    ap.add_argument('--overrides', type=Path, default=None, help='another layout of the word ([op, rows] list)')
    a = ap.parse_args()
    if a.tree is not None:
        return run(a, a.tree.resolve())
    with tempfile.TemporaryDirectory(prefix='bit-frame-ceiling-pr200-') as d:
        commit = rebuild(Path(d))
        log('rebuilt the pinned files of #200 (commit %s) from baseline-pr200.tar.gz; hashes match SOURCE.json' % commit[:7])
        return run(a, Path(d).resolve())


def run(a, tree):
    T = load(tree)
    W = Word(T)
    h, v, m = W.h, W.v, W.m
    cert = T['cert']
    pre, post = cert['overridden_profile'], cert['profile']
    loss = pre['loss']
    D = 2 * v - 3 * loss
    assert pre['deficit_per_vertex'] == post['deficit_per_vertex'] == D and pre['m'] == post['m'] == m
    F = cost_table(m)
    unit = Q(1, 1 << SCALE)
    out = dict(package=PKG, h=h, v=v, loss=loss, D=D, m=m, operations=len(W.ops), roles=W.R, reuse_pairs=len(W.pairs),
               sinks=len(W.sinkroles))
    log('#200 bit word: h %d, v %d, centre loss %d, deficit D = 2v - 3 loss = %d, %d operations, %d roles, %d reuse pairs, %d sinks'
        % (h, v, loss, D, len(W.ops), W.R, len(W.pairs), len(W.sinkroles)))

    # fact 1, numerically: D/C of the certified profile against its certified coarse saving
    f = lambda r: r * math.log(m / r)
    Hpost = {int(r): n for r, n in post['child_histogram'].items() if n}
    C_post = math.fsum(n * f(r) for r, n in Hpost.items())
    coarse = Q(cert['coarse']['coarse_saving'])
    log('fact 1: certified coarse saving %.7e < D/C = %.7e (gap %.3f%%)' % (float(coarse), D / C_post, 100 * (1 - float(coarse) / (D / C_post))))
    assert coarse < Q(D) / Q(C_post)

    # the slot model: with #200's own frames it reproduces the certified ledger child for child
    W.bounds()
    assert W.inside(W.opf), 'the certified layout lies outside the joint bounds'
    slots = W.slots()
    fixed = W.fixed_children()
    local, prepared, actual_total = Counter(), [], 0
    for s, start, ev, is_sink in slots:
        steps = W.chain_dims(s, W.opf)
        local.update(steps)
        lo, hi = slot_bounds(W, start, ev)
        tags = [e[2] for e in ev]
        own, _ = slot_dp(W.dim(start), lo, hi, tags, h, F, {})
        assert own <= sum(F[r] for r in steps), 'floor above the actual chain of slot %d' % s
        if is_sink:
            assert steps[-1] == h - W.dim(W.rootframe[s]), 'sink chain ends with the root-to-full step'
        prepared.append((W.dim(start), lo, hi, tags))
        actual_total += sum(F[r] for r in steps)
    # the terminal record: per sink and stage, the sink's last step (root frame to full space, width h - dim root,
    # present in every layout) and one target child (the pivot's cap read, width fixed by the gauges and roots)
    # disappear; the sink's other steps are copied to the pivot and stay charged (research/paired-cube-diagonal-bit-168
    # bit/terminal.py; #207 audits the same -102/-102 substitution on its layout)
    delta = Counter({int(r): n for r, n in cert['terminal']['child_delta'].items()})
    sink_steps = Counter({r: -n // 3 for r, n in delta.items()})
    assert all(-n == 3 * sink_steps[r] for r, n in delta.items()) and sum(sink_steps.values()) == 2 * len(W.sinkroles)
    last = Counter(h - W.dim(W.rootframe[s]) for s in W.sinkroles)
    assert sink_steps[next(iter(last))] >= last[next(iter(last))] and len(last) == 1
    other = [r for r in sink_steps if r != next(iter(last))] or [next(iter(last))]
    pre_t = {int(r): n for r, n in pre['physical_target_histogram'].items()}
    post_t = {int(r): n for r, n in post['physical_target_histogram'].items()}
    assert all(pre_t.get(r, 0) - post_t.get(r, 0) >= sink_steps[r] - last.get(r, 0) for r in other), 'removed target children'
    local[1] += fixed['injections']
    for r in fixed['centres']:
        local[r] += 1
    children = Counter()
    for part in (local, fixed['source'], fixed['target']):
        for r, n in part.items():
            if r and n:
                children[r] += 3 * n
    for d, n in fixed['tails'].items():
        children[3 * d] += n
    children[2] += 2 * v
    assert dict(children) == {int(r): n for r, n in pre['child_histogram'].items() if n}, 'slot model differs from the certified pre-sink ledger'
    assert 2 * v + W.R - len(W.pairs) == pre['W_per_vertex'] and sum(r * n for r, n in children.items()) == pre['rank_per_vertex']
    less = Counter(children)
    for r, n in sink_steps.items():
        less[r] -= 3 * n
    assert +less == Counter(Hpost), 'the certified sink record is not one [r] and one [h - r] per sink and stage'
    assert dict(Counter({int(r): n for r, n in cert['terminal']['child_delta'].items()})) == {r: -3 * n for r, n in sink_steps.items()}
    log('self-test: #200\'s layout lies inside every derived frame bound; its slot chains reproduce the certified '
        'pre-sink ledger exactly (W %d, rank %d); the terminal record substitutes [%s] per sink and stage; every slot floor is below its actual chain'
        % (pre['W_per_vertex'], pre['rank_per_vertex'], ', '.join('%d' % r for r in sorted(sink_steps))))

    # fact 4: Lagrangian coupling; each round's total is a valid floor (price terms cancel on any common-frame layout)
    price, best, step, independent = {}, None, (3 << SCALE) // 10, None
    for k in range(a.rounds + 1):
        total, grad = 0, defaultdict(int)
        for d0, lo, hi, tags in prepared:
            c, dims = slot_dp(d0, lo, hi, tags, h, F, price)
            total += c
            for tg, d in zip(tags, dims):
                if tg is not None:
                    grad[tg[0]] += tg[1] * d
        assert total <= actual_total, 'Lagrangian floor above the certified layout'
        if best is None or total > best:
            best = total
        if k == 0:
            independent = total
        for i, g in grad.items():
            if g:
                price[i] = price.get(i, 0) + step * g
        step = step * 995 // 1000
    sink_cost = 3 * sum(F[r] * n for r, n in sink_steps.items())      # fixed in every layout (see the terminal record above)
    fixed_cost = 3 * (fixed['injections'] * F[1] + sum(F[r] for r in fixed['centres'])
                      + sum(F[r] * n for r, n in fixed['source'].items() if r)
                      + sum(F[r] * n for r, n in fixed['target'].items() if r)) + 2 * v * F[2]
    tails_cost = sum(F[3 * d] * n for d, n in fixed['tails'].items())
    results = {}
    for name, extra in (('own', tails_cost), ('banked', 0)):
        C_floor = (3 * best + fixed_cost + extra - sink_cost) * unit
        C_ind = (3 * independent + fixed_cost + extra - sink_cost) * unit
        C_act = (3 * actual_total + fixed_cost + extra - sink_cost) * unit
        results[name] = dict(C_floor=float(C_floor), C_certified_layout=float(C_act),
                             coarse_ceiling='%d/10^7' % ceil7(Q(D) / C_floor), coarse_ceiling_uncoupled='%d/10^7' % ceil7(Q(D) / C_ind),
                             kappa_ceiling='%d/10^7' % ceil7(G(Q(D) / C_floor)))
    out.update(results=results, rounds=a.rounds, certified_coarse=str(coarse),
               certified_kappa=str(T['kappa']) if T['kappa'] is not None else None)
    Hpre = {int(r): n for r, n in pre['child_histogram'].items() if n}
    Hbank = dict(Hpost)
    for d, n in fixed['tails'].items():
        Hbank[3 * d] -= n
    Hbank = {r: n for r, n in Hbank.items() if n}
    log('fact 4, #200\'s own ledger:    certified C = %.0f, floor C >= %.0f;  coarse < %s = %.7e  (certified %.7e is %.1f%% of it);  kappa < %s'
        % (C_post, results['own']['C_floor'], results['own']['coarse_ceiling'], ceil7(Q(D) / Q(results['own']['C_floor'])) / 1e7,
           float(coarse), 100 * float(coarse) / (ceil7(Q(D) / Q(results['own']['C_floor'])) / 1e7), results['own']['kappa_ceiling']))
    C_bank = math.fsum(n * f(r) for r, n in Hbank.items())
    log('fact 4, banked ledger (#205/#206/#207 accounting on this word): D/C of #200\'s layout = %.7e;  floor C >= %.0f;  coarse < %s;  kappa < %s'
        % (D / C_bank, results['banked']['C_floor'], results['banked']['coarse_ceiling'], results['banked']['kappa_ceiling']))
    log('without coupling the two registers of an operation: coarse < %s (own), %s (banked)'
        % (results['own']['coarse_ceiling_uncoupled'], results['banked']['coarse_ceiling_uncoupled']))

    if a.overrides is not None:        # another layout of the same word, e.g. #207's 302 changed frames
        opf = list(W.opf)
        changes = json.loads(a.overrides.read_text())
        for i, rows in changes:
            opf[i] = W.register([tuple(int(z) for z in r) for r in rows])
        assert W.inside(opf), 'the override layout lies outside the joint bounds'
        total_over, loc = 0, Counter()
        for s, start, ev, is_sink in slots:
            steps = W.chain_dims(s, opf)
            loc.update(steps)
            total_over += sum(F[r] for r in steps)
            if is_sink:
                assert steps[-1] == h - W.dim(W.rootframe[s])
        assert best <= total_over, 'floor above the override layout'
        Hov = Counter()
        loc[1] += fixed['injections']
        for r in fixed['centres']:
            loc[r] += 1
        for part in (loc, fixed['source'], fixed['target']):
            for r, n in part.items():
                if r and n:
                    Hov[r] += 3 * n
        Hov[2] += 2 * v
        for r, n in sink_steps.items():
            Hov[r] -= 3 * n
        C_ov = math.fsum(n * f(r) for r, n in Hov.items() if n)
        out['overrides'] = dict(file=str(a.overrides), changed=len(changes), inside_bounds=True,
                                banked_DC=D / C_ov, own_DC=D / (C_ov + math.fsum(n * f(3 * d) for d, n in fixed['tails'].items())))
        log('override layout %s: %d changed frames, inside every bound, above the floor; banked D/C = %.7e (%.1f%% of the banked ceiling)'
            % (a.overrides.name, len(changes), D / C_ov, 100 * (D / C_ov) / (ceil7(Q(D) / Q(results['banked']['C_floor'])) / 1e7)))

    if a.check:
        expected = json.loads((HERE / 'expected.json').read_text())
        keys = ('h', 'v', 'loss', 'D', 'm', 'operations', 'roles', 'reuse_pairs', 'sinks', 'rounds', 'certified_coarse')
        got = {k: out[k] for k in keys}
        got['results'] = {n: {k: r[k] for k in ('coarse_ceiling', 'coarse_ceiling_uncoupled', 'kappa_ceiling')} for n, r in results.items()}
        exp = {k: expected[k] for k in keys}
        exp['results'] = {n: {k: r[k] for k in ('coarse_ceiling', 'coarse_ceiling_uncoupled', 'kappa_ceiling')} for n, r in expected['results'].items()}
        assert got == exp, 'results differ from expected.json'
        log('PASS results equal expected.json')
    print(json.dumps(out, indent=1, sort_keys=True))


if __name__ == '__main__':
    main()
