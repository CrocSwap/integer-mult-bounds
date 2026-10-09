"""The recycled bit word: #147's reduced PR97 word with dead auxiliary slots handed to later deferred births.

Stdlib only.  A plan is three lists over the slots of Swapnil Jain's round-seven PR97 word (h = 23):

  elim      terminal output slots deleted exactly as in #147 (hpst3r; SovereignSteak's #122 operation);
  retained  first occupants that keep their entrance gauge sigma (as in #144);
  pairs     [recipient B, donor D]: the physical register of D, dead after its last touch at frame U_D, is moved to
            sigma_B and becomes B.  B's inherited deferred read then cancels the value D left behind (jamesyc's #124
            birth-read operation, here on the bit word).

Level slots (retained or recipients) are read at their sigma frames, in the inherited readout order, but each read is
executed as late as the constraints below allow instead of in one block after phase one.  Everything else keeps its
inherited place.  This module derives the timetable, the literal event list, the scalar replay, the frame ledger and
the resulting row; verify.py drives it.
"""
import gzip
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from partial_gauge_bit import frozen_sources  # noqa: E402


def load_schedule():
    record = json.loads((ROOT / 'certificates/paired-cube-bit-input.json').read_text())
    folder, _ = frozen_sources(record)
    spec = importlib.util.spec_from_file_location('pr97_deferred_reuse', folder / 'deferred.py')
    dr = importlib.util.module_from_spec(spec); spec.loader.exec_module(dr)
    W = json.load(gzip.open(folder / 'witness_23.json.gz', 'rt')); D = json.load(gzip.open(folder / 'deferred_23.json.gz', 'rt'))
    return dr, W, D, dr.Schedule(W, D), record, folder


class Word:
    def __init__(self, S, elim, retained, pairs):
        self.S = S; self.h = S.h; self.v = S.v; self.R = S.R
        self.orig_sel = set(S.sel); self.readout = list(S.readout)
        self.elim = set(elim); self.retained = set(retained)
        self.donor_of = {b: d for b, d in pairs}; self.recipient_of = {d: b for b, d in pairs}
        self.level = self.retained | set(self.donor_of)
        ops = self.ops = S.ops
        prev = {}; pred = defaultdict(list); last = {}; first = {}
        for i, op in enumerate(ops):
            for s in S.touch(op):
                if s in prev: pred[i].append(prev[s])
                prev[s] = i; last[s] = i; first.setdefault(s, i)
        anc = set(); stack = [last[s] for s in S.ret]
        while stack:
            i = stack.pop()
            if i in anc: continue
            anc.add(i); stack.extend(pred[i])
        assert not any(set(S.touch(ops[i])) & self.orig_sel for i in anc)
        self.ph1 = [i for i in range(len(ops)) if i in anc and ops[i][0] != 'src']
        self.rest = [i for i in range(len(ops)) if i not in anc and ops[i][0] != 'src']
        self.pos = {i: k for k, i in enumerate(self.rest)}; self.N = len(self.rest)
        self.first_pos = {s: (self.pos[first[s]] if first[s] in self.pos else -1) for s in first}
        self.death = {s: (self.pos[last[s]] if last[s] in self.pos else -1) for s in last}
        self.early_v = sorted(set(S.srcop) - self.orig_sel, key=lambda s: (S.srcop[s], len(S.vstart[s]), s))
        src = Counter()
        for op in ops:
            if op[0] == 'add': src[op[2]] += 1
            elif op[0] == 'fan': src[op[1]] += 1
        self.never_source = {s for s in range(S.R) if src[s] == 0}
        self.adj = S.adjoint()
        self.target_of = {u: S.tid[S.out[u][1]] for u in self.elim}
        self.check_plan()
        self.timetable()

    # ---------------------------------------------------------------------------------------- plan legality
    def check_plan(self):
        S = self.S
        assert all(u in S.out and u in self.orig_sel and u in self.never_source for u in self.elim), 'eliminated slots'
        assert self.retained <= self.orig_sel and set(self.donor_of) <= self.orig_sel, 'level slots are deferred slots'
        assert not (self.retained & set(self.donor_of)), 'a recipient has no entrance gauge'
        assert not (self.level & self.elim) and not (set(self.recipient_of) & self.elim)
        assert len(self.recipient_of) == len(self.donor_of), 'one recipient per donor'
        assert not (set(self.recipient_of) & set(S.out)), 'an output slot is read at the end and never dies'
        assert not (set(self.recipient_of) & set(S.ret)), 'a retained centre is not used as a donor'
        for b, d in self.donor_of.items(): assert b != d

    # ---------------------------------------------------------------------------------------- timetable
    def timetable(self):
        """Latest read position p[B] (the read runs just before rest operation p[B]) and V time tau[s] of every
        deferred V slot, as the greatest solution of
          p[B] <= first operation touching B;            reads keep the inherited readout order;
          a level V slot takes its V gate right after its read (tau = p);
          tau[s] <= first operation touching s;          V gates of one leaf keep the inherited chain order;
          every read on a target precedes the first redirected write into that target.
        """
        S, N = self.S, self.N
        order = [b for b in self.readout if b in self.level]
        p = {b: self.first_pos[b] for b in order}
        late = [s for s in S.late_v]
        tau = {s: self.first_pos[s] for s in late if s not in self.level}
        def get(s): return p[s] if s in p else tau[s]
        def cap(s, value):
            if s in p:
                if value < p[s]: p[s] = value; return True
            elif value < tau[s]: tau[s] = value; return True
            return False
        chains = []
        late_set = set(late)
        for n, us in S.xs:
            ch = [s for s in us if s in late_set]
            if len(ch) > 1: chains.append(ch)
        first_write = {}                               # target -> eliminated slots writing into it
        for u in self.elim: first_write.setdefault(self.target_of[u], []).append(u)
        readers = defaultdict(list)
        for b in order:
            for t in self.adj[b]:
                if t in first_write: readers[t].append(b)
        changed = True
        while changed:
            changed = False
            for a, b in zip(reversed(order[:-1]), reversed(order[1:])):
                changed |= cap(a, p[b])
            for ch in chains:
                for a, b in zip(reversed(ch[:-1]), reversed(ch[1:])):
                    changed |= cap(a, get(b))
            for t, us in first_write.items():
                w = min((tau[u] if u in tau else self.first_pos[u]) for u in us)
                for b in readers[t]: changed |= cap(b, w)
        assert all(0 <= x <= N for x in p.values()) and all(0 <= x <= N for x in tau.values())
        self.order = order; self.p = p; self.tau = tau
        for b, d in self.donor_of.items():
            assert self.death[d] < p[b], ('donor still live at the recipient read', b, d)

    # ---------------------------------------------------------------------------------------- literal events
    def events(self):
        """Forward events of the middle section, in execution order:
        ('read', B) | ('v', s) | ('vred', u) | ('op', i).  Reads and V events with time k run before rest op k."""
        S = self.S
        at = defaultdict(list)
        rank = {b: i for i, b in enumerate(self.readout)}
        lpos = {s: i for i, s in enumerate(S.late_v)}
        for b in self.order:
            at[self.p[b]].append((0, rank[b], 'read', b))
            if b in S.srcop: at[self.p[b]].append((1, lpos[b], 'v', b))
        for s, k in self.tau.items(): at[k].append((1, lpos[s], 'vred' if s in self.elim else 'v', s))
        out = []
        for k in range(self.N + 1):
            out.extend((kind, s) for _, _, kind, s in sorted(at.get(k, ())))
            if k < self.N: out.append(('op', self.rest[k]))
        return out

    def physical(self):
        phys = {}
        for s in range(self.R):
            if s in self.elim: continue
            r = s
            while r in self.donor_of: r = self.donor_of[r]
            phys[s] = r
        return phys

    # ---------------------------------------------------------------------------------------- scalar replay
    def replay(self, ring, rng, outputs, tamper=None):
        """Literal scalar word on physical registers with arbitrary scratch and data.  ring 0: exact integers with the
        exact integer read coefficients; ring 2: the F2 word.  Returns True iff every physical register is restored
        and every target receives exactly its defining sum (over F2 also exactly x_T)."""
        S = self.S; trip, v = S.trip, S.v; ops = self.ops; srcop = S.srcop; elim = self.elim
        mod = (lambda z: z & 1) if ring == 2 else (lambda z: z)
        phys = self.physical()
        x = [rng.randrange(-10**6, 10**6) for _ in range(v)]
        a0 = {r: rng.randrange(-10**6, 10**6) for r in set(phys.values())}
        y0 = [rng.randrange(-10**6, 10**6) for _ in range(v)]
        a = dict(a0); y = list(y0); done = []; count = [0]
        def coefficient(c): return c & 1 if ring == 2 else c
        def read(s):
            value = a[phys[s]]
            if tamper == 'stale' and s in self.donor_of and count[0] == 0:
                count[0] = 1; value = a0[phys[s]]              # reads the register's entrance value, not what D left
            for t, c in self.adj[s].items(): y[t] -= coefficient(c) * value
        def redirected(t, value):
            y[t] += value
        def vgate(s, sign=1): a[phys[s]] += sign * x[srcop[s] - 1]
        def runop(i, sign=1):
            op = ops[i]
            if op[0] == 'add':
                if op[1] in elim:
                    if sign == 1: redirected(self.target_of[op[1]], a[phys[op[2]]])
                    return
                a[phys[op[1]]] += sign * a[phys[op[2]]]
            else:
                for g in op[2]:
                    if g in elim:
                        if sign == 1: redirected(self.target_of[g], a[phys[op[1]]])
                        continue
                    a[phys[g]] += sign * a[phys[op[1]]]
        for s in range(self.R):
            if s not in self.level and s not in elim: read(s)
        for s in self.early_v: vgate(s); done.append(('v', s))
        for i in self.ph1: runop(i); done.append(('op', i))
        for s, c in S.ret.items():
            for t, T in enumerate(trip):
                if c in T: y[t] += a[phys[s]]
        events = self.events()
        if tamper == 'early':                                 # one recycled read executed before its donor's last write
            written = {}
            for j, (kind, s) in enumerate(events):
                if kind == 'v': written[s] = j
                elif kind == 'op':
                    op = ops[s]
                    for g in ([op[1]] if op[0] == 'add' else op[2]): written[g] = j
            b = next(e[1] for e in events if e[0] == 'read' and self.donor_of.get(e[1]) in written)
            j = written[self.donor_of[b]]
            assert events.index(('read', b)) > j
            events = [e for e in events if e != ('read', b)]; events.insert(j, ('read', b))
        for kind, s in events:
            if kind == 'read': read(s)
            elif kind == 'v': vgate(s); done.append(('v', s))
            elif kind == 'vred': redirected(self.target_of[s], x[srcop[s] - 1])
            else: runop(s); done.append(('op', s))
        for s, (c, T) in S.out.items():
            if s not in elim: y[S.tid[T]] += a[phys[s]]
        if tamper == 'vlast':                                 # the inherited inverse order: every V^-1 after L^-1
            done = [e for e in done if e[0] == 'v'] + [e for e in done if e[0] == 'op']
        for kind, s in reversed(done):
            if kind == 'v': vgate(s, -1)
            else: runop(s, -1)
        if any(mod(a[r] - a0[r]) for r in a0): return False
        want = [0] * v
        for (c, T), n in outputs.items():
            A_, B_ = [q for q in T if q != c]
            want[S.tid[T]] += sum(x[i] for i, Sx in enumerate(trip) if c in Sx and A_ not in Sx and B_ not in Sx)
        for c in range(S.h):
            tot = sum(x[i] for i, Sx in enumerate(trip) if c in Sx)
            for t, T in enumerate(trip):
                if c in T: want[t] += tot
        if any(mod(y[t] - y0[t] - want[t]) for t in range(v)): return False
        if ring == 2 and any(mod(y[t] - y0[t] - x[t]) for t in range(v)): return False
        return True

    def complete(self, ring, outputs):
        """The same literal word on formal variables: every data port, target and physical register starts as its
        own variable.  ring 2: bitmasks over the variables; ring 0: sparse integer linear forms.  Deterministic and
        complete: returns True iff every register ends as its own variable and every target ends as its start
        variable plus exactly its defining sum (over F2: plus x_T).  No random vectors are involved."""
        S = self.S; trip, v = S.trip, S.v; ops = self.ops; srcop = S.srcop; elim = self.elim
        phys = self.physical(); regs = sorted(set(phys.values()))
        index = {r: 2 * v + k for k, r in enumerate(regs)}
        want = [dict() for _ in range(v)]
        for (c, T), n in outputs.items():
            A_, B_ = [q for q in T if q != c]
            row = want[S.tid[T]]
            for i, Sx in enumerate(trip):
                if c in Sx and A_ not in Sx and B_ not in Sx: row[i] = row.get(i, 0) + 1
        for c in range(S.h):
            star = [i for i, Sx in enumerate(trip) if c in Sx]
            for t, T in enumerate(trip):
                if c in T:
                    for i in star: want[t][i] = want[t].get(i, 0) + 1
        if ring == 2:
            a = {r: 1 << index[r] for r in regs}; y = [1 << (v + t) for t in range(v)]; x = [1 << i for i in range(v)]
            def into_y(t, value, c):
                if c & 1: y[t] ^= value
            def into_a(r, value, sign): a[r] ^= value
        else:
            a = {r: {index[r]: 1} for r in regs}; y = [{v + t: 1} for t in range(v)]; x = [{i: 1} for i in range(v)]
            def accumulate(dst, value, c):
                for k, z in value.items():
                    z = dst.get(k, 0) + c * z
                    if z: dst[k] = z
                    else: del dst[k]
            def into_y(t, value, c): accumulate(y[t], value, c)
            def into_a(r, value, sign): accumulate(a[r], value, sign)
        done = []
        def read(s):
            value = a[phys[s]]
            for t, c in self.adj[s].items(): into_y(t, value, -c)
        def vgate(s, sign=1): into_a(phys[s], x[srcop[s] - 1], sign)
        def runop(i, sign=1):
            op = ops[i]
            if op[0] == 'add':
                if op[1] in elim:
                    if sign == 1: into_y(self.target_of[op[1]], a[phys[op[2]]], 1)
                    return
                into_a(phys[op[1]], a[phys[op[2]]], sign)
            else:
                for g in op[2]:
                    if g in elim:
                        if sign == 1: into_y(self.target_of[g], a[phys[op[1]]], 1)
                        continue
                    into_a(phys[g], a[phys[op[1]]], sign)
        for s in range(self.R):
            if s not in self.level and s not in elim: read(s)
        for s in self.early_v: vgate(s); done.append(('v', s))
        for i in self.ph1: runop(i); done.append(('op', i))
        for s, c in S.ret.items():
            for t, T in enumerate(trip):
                if c in T: into_y(t, a[phys[s]], 1)
        for kind, s in self.events():
            if kind == 'read': read(s)
            elif kind == 'v': vgate(s); done.append(('v', s))
            elif kind == 'vred': into_y(self.target_of[s], x[srcop[s] - 1], 1)
            else: runop(s); done.append(('op', s))
        for s, (c, T) in S.out.items():
            if s not in elim: into_y(S.tid[T], a[phys[s]], 1)
        for kind, s in reversed(done):
            if kind == 'v': vgate(s, -1)
            else: runop(s, -1)
        if ring == 2:
            if any(a[r] != 1 << index[r] for r in regs): return False
            if any({i for i, c in want[t].items() if c & 1} != {t} for t in range(v)): return False
            return all(y[t] == (1 << (v + t)) ^ (1 << t) for t in range(v))
        if any(a[r] != {index[r]: 1} for r in regs): return False
        for t in range(v):
            expected = dict(want[t]); expected[v + t] = 1
            if y[t] != expected: return False
        return True

    # ---------------------------------------------------------------------------------------- frame ledger
    def ledger(self):
        """Run the forward word on frame keys.  Every scalar gate must find its registers at one common frame key;
        every register only moves forward.  Returns the moves (register kind, old key, new key) in time order, the
        key sequence of every register, and the rank histograms of the actual moves."""
        S = self.S; h, v = S.h, S.v; ops = self.ops; elim = self.elim; phys = self.physical()
        def norm(k): return ('out', 0, tuple(k[2])) if k[0] == 'out' else k
        dim = S.dim
        cur = {}; seq = {}
        for r in set(phys.values()):
            cur['a', r] = ('sigma', r) if r in self.retained else ('0',)
        for n, _ in S.xs: cur['x', n] = ('n', n)
        for t in range(v): cur['y', t] = ('0',)
        for reg, k in cur.items(): seq[reg] = [k]
        hist = {'a': Counter(), 'x': Counter(), 'y': Counter()}
        moves = Counter()
        def move(reg, dst):
            dst = norm(dst); old = cur[reg]
            if old == dst: return
            r = dim(dst) - dim(old)
            assert r >= 0, ('retreat', reg, old, dst)
            moves[reg[0], old, dst] += 1
            if r: hist[reg[0]][r] += 1
            cur[reg] = dst; seq[reg].append(dst)
        def gate(regs, frame):
            for reg in regs: move(reg, frame)
            assert all(cur[reg] == norm(frame) for reg in regs)
        A = lambda s: ('a', phys[s])
        leaf = S.srcop
        def operation(i):
            op = ops[i]
            if op[0] == 'add':
                _, p, o, n = op; frame = ('n', n)
                gate([('y', self.target_of[p]) if p in elim else A(p), A(o)], frame)
            else:
                for g in sorted(op[2], key=lambda s: dim(S.start_key(s))):
                    frame = S.start_key(g)
                    gate([A(op[1]), ('y', self.target_of[g]) if g in elim else A(g)], frame)
        for s in range(self.R):
            if s not in self.level and s not in elim:
                assert cur[A(s)] == ('0',) and s == phys[s], 'zero-prelude read of a first occupant at frame zero'
        for s in self.early_v: gate([A(s), ('x', leaf[s])], ('v', s))
        for i in self.ph1: operation(i)
        centres = 0
        for s, c in S.ret.items():
            move(A(s), ('ret', c))
            assert all(cur['y', t] == ('0',) for t, T in enumerate(S.trip) if c in T)
            centres += 1
        for kind, s in self.events():
            if kind == 'read':
                f = ('sigma', s)
                if s in self.donor_of: move(A(s), f)
                assert cur[A(s)] == f, ('read frame', s)
                for t, c in self.adj[s].items():
                    assert c > 0
                    gate([('y', t)], f)
            elif kind == 'v': gate([A(s), ('x', leaf[s])], ('v', s))
            elif kind == 'vred': gate([('x', leaf[s]), ('y', self.target_of[s])], ('v', s))
            else: operation(s)
        for s, (c, T) in S.out.items():
            if s not in elim: gate([A(s), ('y', S.tid[T])], ('out', 0, T))
        for t, T in enumerate(S.trip): move(('y', t), ('out', 0, T))
        for r in set(phys.values()): move(('a', r), ('F',))
        for n, _ in S.xs: move(('x', n), ('F',))
        return dict(moves=moves, seq=seq, hist=hist, centres=centres, phys=phys)

    # ---------------------------------------------------------------------------------------- inherited nestings
    def inherited(self):
        """Adjacent frame pairs whose nesting the pinned PR97 audits already certify (check_lifted.py D and
        check_frames.py X/Q, relied on by #144): consecutive keys of every original slot chain, of every X chain in
        its original V order, and of every y chain in readout order with positive Z support; plus sigma <= start and
        sigma <= t_T^perp.  Chains are nested sequences, so any ordered pair taken from one chain is nested too."""
        S = self.S
        def norm(k): return ('out', 0, tuple(k[2])) if k[0] == 'out' else k
        keep = S.sel; S.sel = set(self.orig_sel)
        chains = []
        for s in range(S.R): chains.append([norm(k) for k in S.chain_keys(s)])
        S.sel = keep
        for n, us in S.xs: chains.append([('n', n)] + [('v', s) for s in us] + [('F',)])
        byt = defaultdict(list)
        for s in self.readout:
            for t, c in self.adj[s].items():
                if c > 0: byt[t].append(('sigma', s))
        for t, T in enumerate(S.trip): chains.append([('0',)] + byt[t] + [('out', 0, T), ('F',)])
        return chains

    def row(self, led, record):
        """#144's shared-core bit row from the actual ledger moves."""
        S = self.S; h, v = S.h, S.v
        aux, source, target = led['hist']['a'], led['hist']['x'], led['hist']['y']
        assert +source == Counter(r for path in S.xdata() for r in path if r), 'source chains unchanged'
        assert sum(r * n for r, n in target.items()) == v * (h - 1) and led['centres'] == h
        gauges = Counter(S.f[s] for s in self.retained)
        children = Counter()
        for local in (aux, source, target, Counter({h - 1: h})):
            for r, n in local.items():
                if r and n: children[r] += 3 * n
        for r, n in gauges.items(): children[3 * r] += n
        children[2] += 2 * v
        Rn = len(set(led['phys'].values()))
        assert Rn == S.R - len(self.elim) - len(self.donor_of)
        enc = lambda H: {str(r): n for r, n in sorted(H.items()) if n}
        row = dict(record)
        row.update(R=Rn, W_per_vertex=2 * v + Rn, selected_roles=sum(gauges.values()), selected_rank_histogram=enc(gauges),
                   auxiliary_histogram=enc(aux), source_data_histogram=enc(source), target_data_histogram=enc(target),
                   child_histogram=enc(children), rank_per_vertex=sum(r * n for r, n in children.items()),
                   eliminated_roles=len(self.elim), recycled_roles=len(self.donor_of),
                   omitted_roles=len(self.orig_sel) - len(self.elim) - len(self.level))
        row.pop('selection_file', None); row.pop('selection_sha256', None)
        assert row['W_per_vertex'] * row['m'] - row['rank_per_vertex'] == row['deficit_per_vertex'] == 2024
        return row

    def new_moves(self, led):
        """Distinct moves of the ledger that are not an ordered pair of one inherited certified chain."""
        where = defaultdict(dict)
        for ci, chain in enumerate(self.inherited()):
            for i, k in enumerate(chain): where[k].setdefault(ci, i)
        def certified(a, b):
            if a == ('0',) or b == ('F',): return True
            wa, wb = where.get(a), where.get(b)
            if not wa or not wb: return False
            small, big = (wa, wb) if len(wa) <= len(wb) else (wb, wa)
            return any(ci in big and wa[ci] <= wb[ci] for ci in small)
        return sorted((m for m in led['moves'] if not certified(m[1], m[2])), key=str)
