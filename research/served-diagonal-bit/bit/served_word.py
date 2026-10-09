"""Formal admission of the served physical bit word.

Fork of PR200's bit/word.py and bit/base_word.py (Chafik Boukhalfa, Apache-2.0; built on eumemic's PR168 v4
exact integer backend) with one new operation kind. A served operation ops[i] = [a, -1-d, n] adds the passive
source data register x_d into the auxiliary register a at frame op_frame[i]; that partner pair's XOR
x_c += x_d runs right after the injections ('early'), so its passive chain is line -> mix -> op_frame[i] -> full.
Everything else is PR200's check, unchanged: phase-one closure, register contents, gauges, compensated pairs,
physical chains, target chronology, partner chains, the paid ledger and the complete F2 and integer columns.
"""
from collections import Counter, defaultdict
from pathlib import Path
import gzip, importlib.util, json, sys


def need(ok, msg):
    if not ok:
        raise ValueError(msg)


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def read(p):
    raw = p.read_bytes()
    return json.loads(gzip.decompress(raw) if p.suffix == '.gz' else raw)


class Candidate:
    def __init__(self, pr200_package, served_dir):
        pr200_package, served_dir = Path(pr200_package), Path(served_dir)
        SOURCE = pr200_package / 'references/pr168-v4'
        self.module = backend = module('exact_integer_backend', SOURCE / 'research/paired-cube-bit/check_paired_cube_bit.py')
        C = backend.Checker.__new__(backend.Checker); self.C = C; C.mut = None
        B = pr200_package / 'selected/bit'
        self.input_paths = [B / 'graph_p12.json', served_dir / 'profile_p12.json', served_dir / 'word_p12.json.gz',
                            B / 'frames_p12.json.gz', served_dir / 'kchron_p12.json']
        C.g, C.prof, C.w, C.fr, C.k = map(read, self.input_paths)
        C.h = C.g['h']; C.v = C.g['v']; C.frames()
        self.h, self.v, self.R = C.h, C.v, C.prof['R']; self.w, self.g, self.k = C.w, C.g, C.k
        self.ops = self.w['ops']; self.nf = {int(n): f for n, f in self.w['node_frame'].items()}
        self.served = {i: (d, f) for i, d, f in self.w['served']}
        need(all(self.ops[i][1] == -1 - d for i, (d, f) in self.served.items()), 'served operations carry the passive marker')
        need(all(b >= 0 for i, (a, b, n) in enumerate(self.ops) if i not in self.served), 'only served operations read data registers')
        need(all(self.w['op_frame'][i] == f for i, (d, f) in self.served.items()), 'served frame is the operation frame')
        self.source = {int(n): s for n, s in self.w['sources'].items()}; self.gauge = {z['role']: z for z in self.w['gauges']}
        need(len(self.gauge) == len(self.w['gauges']), 'unique gauge roles')
        self.original_opframe = tuple(self.nf[n] for a, b, n in self.ops); self.opframe = self.w['op_frame'][:]
        need(len(self.opframe) == len(self.ops), 'complete operation frame vector')
        self.changed_frames = [i for i, (a, b) in enumerate(zip(self.original_opframe, self.opframe)) if a != b]
        self.phase1 = sorted(self.w['phase1']); phase = set(self.phase1)
        self.rest = [i for i in range(len(self.ops)) if i not in phase]; order = self.phase1 + self.rest
        self.position = {i: p for p, i in enumerate(order)}; pos = {i: p for p, i in enumerate(self.rest)}
        self.order = [z['role'] for z in reversed(self.w['gauges'])]
        self.role_ops = defaultdict(list)
        for i in order:
            for s in self.ops[i][:2]:
                if s >= 0:
                    self.role_ops[s].append(i)
        need(all(xs == sorted(xs) for xs in self.role_ops.values()), 'execution order preserves every role chronology')
        need(all(s in self.role_ops or s in set(self.w['rootroles']) for s in range(self.R)), 'every role is used')
        self.first = {s: pos.get(xs[0], -1) for s, xs in self.role_ops.items()}
        self.last = {s: pos.get(xs[-1], -1) for s, xs in self.role_ops.items()}
        self.endframe = {s: self.opframe[xs[-1]] for s, xs in self.role_ops.items()}
        self.rootroles = set(self.w['rootroles']); self.rootkind = {s: r['kind'] for s, r in zip(self.w['rootroles'], self.g['roots'])}
        need(len(self.rootroles) == len(self.w['rootroles']), 'unique root roles')
        reads = {int(s): p for s, p in self.w['reads'].items()}
        need(set(reads) <= set(self.gauge), 'only gauges have explicit reads')
        self.readtime = {s: reads.get(s, len(self.phase1)) - len(self.phase1) for s in self.order}
        need(all(0 <= self.readtime[s] <= self.first[s] for s in self.order), 'all gauge reads after centre phase and before first use')
        self.pairs = [[b, a] for a, b in self.w['pairs']]; self.donor = dict(self.pairs)
        need(len(self.donor) == len(self.pairs) == len(set(self.donor.values())), 'one-to-one aliases')
        need(not set(self.donor) & set(self.donor.values()), 'disjoint donor recipient sets')
        for b, d in self.pairs:
            need(d not in self.gauge and d not in self.rootroles and b in self.gauge, 'ungauged non-root donor and gauged recipient')
            need(self.last[d] < self.readtime[b], 'donor dead before recipient read')
        self.phys = {s: self.donor.get(s, s) for s in range(self.R)}
        need(len(set(self.phys.values())) == self.R - len(self.pairs), 'physical slot count')
        need(all(self.phys[a] != self.phys[b] for i, (a, b, n) in enumerate(self.ops) if i not in self.served), 'distinct physical gate ports')
        C.chains = self.base_chains

    # ---------------------------------------------------------------- PR200 base_word.py, served-aware
    def exact_frames(self):
        C = self.C
        C.decoder(); C.geometry()
        for i in self.changed_frames:
            f = self.opframe[i]; x = self.ops[i][2]; bits = C.sup[x]
            need(C.nondeg(f), 'replacement operation frame nondegenerate')
            while bits:
                low = bits & -bits; s = low.bit_length() - 1; bits -= low
                need(C.in_frame(C.chi[s], f), 'value span in replacement operation frame')
        for b, d in self.pairs:
            need(C.sub(self.endframe[d], self.gauge[b]['frame']), 'exact Q donor-to-birth containment')
            need(C.nondeg(self.endframe[d]) and C.nondeg(self.gauge[b]['frame']), 'handoff endpoints nondegenerate')
        for i, (d, f) in self.served.items():
            need(C.nondeg(f) and C.in_frame(C.chi[d], f), 'served passive line inside the served frame')

    def register(self, rows):
        C = self.C
        B, _ = self.module.reduce_rows(rows, self.h)
        B = tuple(sorted(map(tuple, B), key=lambda r: next(i for i, x in enumerate(r) if x)))
        if not hasattr(self, 'frame_ids'):
            self.frame_ids = {}
        if B in self.frame_ids:
            return self.frame_ids[B]
        f = max(C.B) + 1; A, _ = self.module.kernel(B, C.h)
        C.B[f], C.A[f], C.dimf[f] = B, A, len(B); self.frame_ids[B] = f
        return f

    def base_chains(self):
        """Phase/gauge/source contracts; the served passive chains carry their extra stop."""
        C, w, h, v = self.C, self.w, self.h, self.v
        order = self.phase1 + self.rest
        roleprev = {}; pred = []
        for i, (a, b, n) in enumerate(self.ops):
            pa = roleprev.get(a, -1); pb = roleprev.get(b, -1) if b >= 0 else -1
            pred.append((pa, pb)); roleprev[a] = i
            if b >= 0:
                roleprev[b] = i
        pending = [roleprev[s] for s in self.rootroles if self.rootkind[s] == 'center' and s in roleprev]; closure = set()
        while pending:
            i = pending.pop()
            if i not in closure:
                closure.add(i); pending.extend(j for j in pred[i] if j >= 0)
        need(closure == set(self.phase1), 'phase one is exactly centre closure')
        content = [0] * self.R
        for n, s in self.source.items():
            content[s] = 1 << n
        for i in order:
            a, b, n = self.ops[i]; args = self.g['args'][n]
            if i in self.served:
                d = self.served[i][0]
                need(content[a] and args is not None and {content[a], 1 << d} == {C.sup[t] for t in args}, 'served addition operands')
                content[a] |= 1 << d
                continue
            if content[a]:
                need(args is not None and {content[a], content[b]} == {C.sup[t] for t in args}, 'actual addition operands')
            else:
                need(content[b] == C.sup[n], 'actual copied node value')
            content[a] |= content[b]
        co = [set() for _ in range(self.R)]
        for r, s in zip(self.g['roots'], w['rootroles']):
            co[s].update(r['targets'])
        for i in reversed(order):
            a, b, n = self.ops[i]
            if b >= 0:
                co[b].update(co[a])
        touched = {s for i in self.phase1 for s in self.ops[i][:2] if s >= 0}
        for s, z in self.gauge.items():
            need(s not in self.source.values() and s not in touched, 'gauge untouched in phase one and source injection')
            need(set(z['targets']) == co[s] and C.dimf[z['frame']] == z['dim'] > 0, 'gauge dimension and complete response support')
        served_by_passive = {d: f for i, (d, f) in self.served.items()}
        need(len(served_by_passive) == len(self.served), 'one served operation per passive source')
        src = Counter(); members = Counter(); labels = list(map(set, self.g['labels']))
        for e in self.k['entries']:
            c, d, f, cap = e['carrier'], e['passive'], e['mix_frame'], e['deliver_frame']
            need(len(labels[c] & labels[d]) == 1, 'orthogonal partner pair')
            need(C.dimf[f] == 2 and C.in_frame(C.chi[c], f) and C.in_frame(C.chi[d], f), 'partner mix span')
            need(C.sub(f, cap) and all(self.module.dot(C.cov[t], u) == 0 for t in e['receivers'] for u in C.B[cap]), 'partner mix delivery cap')
            need(e['carrier_chain'] == [w['source_frame'][c], f, cap, w['full_frame']], 'exact carrier chain')
            if d in served_by_passive:
                need(e.get('early') is True, 'served pair mixes right after injection')
                need(e['passive_chain'] == [w['source_frame'][d], f, served_by_passive[d], w['full_frame']], 'served passive chain')
            else:
                need(not e.get('early'), 'unserved pair keeps its delivery-time mix')
                need(e['passive_chain'] == [w['source_frame'][d], f, w['full_frame']], 'exact passive chain')
            root = self.g['roots'][e['deliver_after_root']]
            need(root['kind'] == 'side' and sorted(e['receivers']) == sorted(root['targets']), 'partner delivery at own receiver root')
            for chain in (e['carrier_chain'], e['passive_chain']):
                for a, b in zip(chain, chain[1:]):
                    need(C.sub(a, b), 'nested source chronology'); src[C.dimf[b] - C.dimf[a]] += 1
            members[c] += 1; members[d] += 1
        need(all(members[s] == 1 for s in range(v)), 'every source in one partner pair')
        need(set(served_by_passive) <= {e['passive'] for e in self.k['entries']}, 'served sources are passive partners')
        return Counter(), Counter(), src, self.R

    def row(self):
        C, h, v = self.C, self.h, self.v
        _, baseline_Y, src, _ = C.chains()
        seq = defaultdict(list)
        for i, (a, b, x) in enumerate(self.ops):
            seq[a].append(self.opframe[i])
            if b >= 0:
                seq[b].append(self.opframe[i])
        for j, s in enumerate(self.w['rootroles']):
            seq[s].append(self.w['root_frame'][j])
        start = {b: self.w['source_frame'][x] for x, b in self.source.items()}
        start.update({b: z['frame'] for b, z in self.gauge.items()})
        recipient = {d: b for b, d in self.pairs}
        H = Counter()
        for s in range(self.R):
            if s in self.donor:
                continue
            chain = list(seq[s])
            if s in recipient:
                b = recipient[s]; chain += [self.gauge[b]['frame']] + seq[b]
            chain.append(self.w['full_frame'])
            prev = start.get(s); dp = 0 if prev is None else C.dimf[prev]
            if s in self.source.values():
                H[1] += 1
            for f in chain:
                need(prev is None or C.sub(prev, f), 'physical role chain nested')
                d = C.dimf[f]
                if d > dp:
                    H[d - dp] += 1
                prev, dp = f, d
        for j, r in enumerate(self.g['roots']):
            if r['kind'] == 'center':
                H[C.dimf[self.w['root_frame'][j]]] += 1
        Y = Counter(); current = [None] * v

        def readt(t, f):
            old = current[t]; d = 0 if old is None else C.dimf[old]
            need(old is None or C.sub(old, f), 'actual target frame chronology')
            if C.dimf[f] > d:
                Y[C.dimf[f] - d] += 1
            current[t] = f
        for b in sorted(self.order, key=lambda b: self.readtime[b]):
            for t in self.gauge[b]['targets']:
                readt(t, self.gauge[b]['frame'])
        deliveries = defaultdict(list)
        for e in self.k['entries']:
            deliveries[e['deliver_after_root']].append(e)
        for j, r in enumerate(self.g['roots']):
            if r['kind'] != 'center':
                for t in r['targets']:
                    readt(t, self.w['root_frame'][j])
            for e in deliveries[j]:
                for t in e['receivers']:
                    readt(t, e['deliver_frame'])
        for t, f in enumerate(current):
            need(f is not None and all(self.module.dot(C.cov[t], b) == 0 for b in C.B[f]), 'final target cap')
            gap = h - 1 - C.dimf[f]
            if gap:
                Y[gap] += 1
        need(sum(r * n for r, n in Y.items()) == v * (h - 1), 'target rank mass')
        hist = Counter()
        for part in (H, Y, src):
            for r, n in part.items():
                if r and n:
                    hist[r] += 3 * n
        for b, z in self.gauge.items():
            if b not in self.donor:
                hist[3 * z['dim']] += 1
        hist[2] += 2 * v
        hist = {r: n for r, n in sorted(hist.items()) if n}
        need(all(0 < r < 3 * h and n > 0 for r, n in hist.items()), 'positive proper child bins')
        R = self.R - len(self.pairs); W = 2 * v + R; mass = sum(r * n for r, n in hist.items()); m = 3 * h
        need(W * m - mass == C.prof['deficit_per_vertex'], 'reuse preserves telescoping deficit')
        return dict(h=h, v=v, R=R, virtual_R=self.R, reused_registers=len(self.pairs), W_per_vertex=W, m=m,
                    loss=C.prof['loss'], rank_per_vertex=mass, deficit_per_vertex=W * m - mass,
                    child_histogram=hist, maxchild=max(hist), selected_roles=len(self.gauge) - len(self.pairs),
                    selected_rank_histogram=dict(Counter(z['dim'] for b, z in self.gauge.items() if b not in self.donor)),
                    changed_operation_frames=len(self.changed_frames), served_operations=len(self.served),
                    frames_not_contained_in_original=sum(not C.sub(self.opframe[i], self.original_opframe[i]) for i in self.changed_frames),
                    physical_target_histogram=dict(Y), physical_internal_histogram=dict(H),
                    source_data_histogram=dict(src), foreign_producer_replays=0)

    def adjoint(self):
        """Dirty-register responses; a data register is not a dirty auxiliary, so served operations add none."""
        adj = [dict() for _ in range(self.R)]
        for r, s in zip(self.g['roots'], self.w['rootroles']):
            for t in r['targets']:
                adj[s][t] = adj[s].get(t, 0) + 1
        for a, b, _ in reversed(self.ops):
            if b < 0:
                continue
            for t, c in adj[a].items():
                adj[b][t] = adj[b].get(t, 0) + c
        return adj

    def formal(self, ring, tamper=None):
        """All source, target and dirty-register columns; no random sampling."""
        v, phys = self.v, self.phys
        regs = sorted(set(phys.values())); index = {r: 2 * v + j for j, r in enumerate(regs)}
        if ring == 2:
            unit = lambda i: 1 << i

            def accum(dst, val, c):
                return dst ^ val if c & 1 else dst
        else:
            unit = lambda i: {i: 1}

            def accum(dst, val, c):
                out = dict(dst)
                for i, z in val.items():
                    k = out.get(i, 0) + c * z
                    if k:
                        out[i] = k
                    else:
                        out.pop(i, None)
                return out
        x = [unit(s) for s in range(v)]; y = [unit(v + t) for t in range(v)]
        a = {r: unit(index[r]) for r in regs}
        adj = self.adjoint()
        at = defaultdict(list)
        for b in self.order:
            at[self.readtime[b]].append(b)
        done = []
        stale_used = False

        def read(b):
            nonlocal stale_used
            if tamper == 'omit_compensation' and b == self.order[0]:
                return
            value = a[phys[b]]
            if tamper == 'stale' and b in self.donor and not stale_used:
                value = unit(index[phys[b]]); stale_used = True
            for t, c in adj[b].items():
                y[t] = accum(y[t], value, -c)

        def op(i, sign):
            b, d, _ = self.ops[i]
            if i in self.served:
                p = self.served[i][0]
                if tamper == 'served_from_carrier':
                    p = next(e['carrier'] for e in self.k['entries'] if e['passive'] == p)
                a[phys[b]] = accum(a[phys[b]], x[p], sign)
            else:
                a[phys[b]] = accum(a[phys[b]], a[phys[d]], sign)
        for b in range(self.R):
            if b not in self.gauge:
                read(b)
        for s, b in self.source.items():
            a[phys[b]] = accum(a[phys[b]], x[s], 1)
        for e in self.k['entries']:
            if e.get('early') and tamper != 'late_served_mix':
                x[e['carrier']] = accum(x[e['carrier']], x[e['passive']], 1)
        for i in self.phase1:
            op(i, 1); done.append(i)
        for r, b in zip(self.g['roots'], self.w['rootroles']):
            if r['kind'] == 'center':
                for t in r['targets']:
                    y[t] = accum(y[t], a[phys[b]], 1)
        for j, i in enumerate(self.rest):
            for b in at[j]:
                read(b)
            op(i, 1); done.append(i)
        for b in at[len(self.rest)]:
            read(b)
        deliveries = defaultdict(list)
        for e in self.k['entries']:
            deliveries[e['deliver_after_root']].append(e)
        broken = False
        for j, (r, b) in enumerate(zip(self.g['roots'], self.w['rootroles'])):
            if r['kind'] != 'center':
                for t in r['targets']:
                    y[t] = accum(y[t], a[phys[b]], 1)
            for e in deliveries[j]:
                c, d = e['carrier'], e['passive']
                if not e.get('early') or tamper == 'late_served_mix':
                    x[c] = accum(x[c], x[d], 1)
                for t in e['receivers']:
                    if tamper == 'missing_partner' and not broken:
                        broken = True; continue
                    y[t] = accum(y[t], x[c], 1)
        for e in self.k['entries']:
            x[e['carrier']] = accum(x[e['carrier']], x[e['passive']], -1)
        for i in reversed(done):
            op(i, -1)
        for s, b in self.source.items():
            a[phys[b]] = accum(a[phys[b]], x[s], -1)
        need(all(a[r] == unit(index[r]) for r in regs), 'all dirty register columns restored')
        need(all(x[s] == unit(s) for s in range(v)), 'all source columns restored')
        if ring == 2:
            want = [accum(unit(v + t), unit(t), 1) for t in range(v)]
        else:
            support = [{s: 1} for s in range(v)]
            for aa, bb in self.g['args'][v:]:
                support.append(accum(support[aa], support[bb], 1))
            want = [unit(v + t) for t in range(v)]
            for r in self.g['roots']:
                for t in r['targets']:
                    want[t] = accum(want[t], support[r['node']], 1)
            for e in self.k['entries']:
                for t in e['receivers']:
                    want[t] = accum(want[t], unit(e['carrier']), 1)
                    want[t] = accum(want[t], unit(e['passive']), 1)
        need(y == want, 'all target columns equal defining decoder')
        return dict(ring=str(ring), formal_variables=2 * v + len(regs),
                    target_contract='F2 identity' if ring == 2 else 'integer defining decoder',
                    identity=ring == 2, defining_decoder=True, all_dirty_and_source_columns_restored=True,
                    served_operations=len(self.served))
