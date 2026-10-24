#!/usr/bin/env python3
"""The fragmentation of the #4610 word is rigid under free scalar reordering.

Standard library only; about 2-4 minutes.  Reads Cao Yifan's final PR4610 word
(research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz) and its ARITHMETIC.json,
both pinned by SHA256 in SOURCES.json.

Model (the retained frame contract of #4610 / #5226, with the chronological order freed):
  * every persistent field f occupies a nested chain of frames S_f = F_0 < ... < F_k = T_f
    (binary subspaces); a climb F_i < F_{i+1} is a paid job of rank dim F_{i+1} - dim F_i and the
    fragmentation loss of the field is Lambda_f(t) = sum_j rank_j^t - R_f^t (#5226, Theorem B);
  * a two-field scalar contact (ADD/COPY) happens at ONE common frame that both chains contain,
    inside the interval  S_d + S_s  <=  F  <=  T_d & T_s;
  * a scalar contact with the owned centre buffer C0 needs the field at the frame the centre walk
    uses: the eight centre reads (COPY C0 <- source) may move to any frame of the source's chain of
    dimension >= 1 (the transport C0 -> frame 0 then costs that dimension), the 176 deliveries
    (target += C0 at frame 0) are fixed;
  * scalar operations, warps, centre transports and adapters keep their value dependencies
    (write/read and write/write conflicts; ADDs into one destination commute), the three
    interpreter-visible phase markers (zero_frame_precondition, full_frame_cleanup, done) are
    barriers, every native warp is anchored between its two frames, and along each field the
    contacts occur in non-decreasing chain order (no descents).
A "level" of a field is an intermediate frame of its chain that hosts at least one contact.
Dropping a level means re-routing all its contacts to other frames of the chain (possibly adding
a frame to a partner's chain) and merging the two adjacent climbs into one; every such re-routing
is enumerated and tested for feasibility by an exact acyclicity check of the operation/level graph.

Result: no level of any field can be dropped.  Controls show the test is live.
Usage: python3 -I -B verify.py [--write]
"""
import argparse, collections, gzip, hashlib, itertools, json, math, sys, time
from pathlib import Path
from decimal import Decimal as D, getcontext

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
W3 = ROOT / 'research' / 'kappa-round3-warp-20261022'
getcontext().prec = 40


def require(ok, message):
    if not ok:
        raise SystemExit('FAIL: ' + message)


def pinned_inputs():
    rows = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))['files']
    for row in rows:
        if row['usage'] == 'input':
            data = (ROOT / row['path']).read_bytes()
            require(hashlib.sha256(data).hexdigest() == row['sha256'], 'input drift: ' + row['path'])


# ----------------------------------------------------------------------------------------------
# word model
# ----------------------------------------------------------------------------------------------
class Word:
    def __init__(self, word, arithmetic, centre_free=True, pin_centre=True, barriers=True):
        c = word['canonical']; self.c = c
        self.frames = list(c['frames']); self.nf = len(c['start']); self.S = list(c['start']); self.T = list(c['final'])
        self.H = {int(k): n for k, n in arithmetic['local_helpers'].items()}
        self.N = {int(k): n for k, n in arithmetic['local_paid'].items()}
        self.nm = self.nf - sum(self.H.values())
        self.spans = [self.span_of(fr) for fr in self.frames]
        self.span_id = {sp: i for i, sp in enumerate(self.spans)}
        prog = word['programs']['forward']; self.prog = prog
        S, T, nf = self.S, self.T, self.nf
        # pass 1: visit sequences, pinned (revisiting) fields, warp frames
        cur = list(S); chain0 = [[S[f]] for f in range(nf)]; pinned = set(); warp_frames = collections.defaultdict(set)
        for e in prog:
            if e[0] == 'climb':
                f = e[2]
                require(cur[f] == e[3] and self.spans[e[3]] < self.spans[e[4]] and e[5] == self.dim(e[4]) - self.dim(e[3]), 'nested climb with its paid rank')
                if e[4] in chain0[f]: pinned.add(f)
                chain0[f].append(e[4]); cur[f] = e[4]
            elif e[0] == 'warp':
                f = e[1][1]
                if e[4] != e[3]:
                    if e[4] in chain0[f]: pinned.add(f)
                    warp_frames[f].update((cur[f], e[4])); chain0[f].append(e[4])
                cur[f] = e[4]
        self.chain0, self.pinned, self.warp_frames = chain0, pinned, warp_frames
        # pass 2: ops (DAG nodes), contacts with level keys
        ops = []; contacts = []; warp_ops = []; barrier_ops = []
        cur = list(S); visit = [0] * nf
        key_of = lambda f: ('v', visit[f]) if f in pinned else cur[f]
        for e in prog:
            kind = e[0]
            if kind == 'climb':
                f = e[2]; cur[f] = e[4]; visit[f] += 1
            elif kind == 'warp':
                f = e[1][1]; j = len(ops); ops.append((False, {('L', f)}, set()))
                if e[4] != e[3]:
                    warp_ops.append((j, f, visit[f], cur[f], e[4])); cur[f] = e[4]; visit[f] += 1
            elif kind == 'phase':
                if barriers and e[1] in ('zero_frame_precondition', 'full_frame_cleanup', 'done'): barrier_ops.append(len(ops))
                ops.append((False, set(), set()))
            elif kind == 'center': ops.append((False, {('L', e[2])}, set()))
            elif kind == 'adapter': ops.append((False, {('L', e[2]), ('L', e[3])}, set()))
            elif kind == 'scalar':
                op = e[1]; k = op[0]; roles = [tuple(r) for r in op[1:] if isinstance(r, list)]
                W, Rd = ({roles[0]}, {roles[1]}) if k in ('add', 'copy') else ({roles[0]}, set())
                j = len(ops); ops.append((k == 'add', W, Rd))
                L = [r[1] for r in roles if r[0] == 'L']
                if k in ('add', 'copy') and len(L) == 2:
                    d, s = L; F = e[2]
                    require(cur[d] == F and cur[s] == F, 'contact frame mismatch in the word')
                    lo = self.join(S[d], S[s]); hi = self.meet(T[d], T[s])
                    if not self.sub(lo, F): lo = F           # 135 contacts of the word sit below S_d+S_s (warped fields)
                    contacts.append(dict(d=d, s=s, op=j, lo=lo, hi=hi, F=F, kd=key_of(d), ks=key_of(s),
                                         pin=(d in pinned or s in pinned), kind='LL'))
                elif k in ('add', 'copy') and len(L) == 1 and pin_centre:
                    f = L[0]; F = e[2]
                    if k == 'copy' and centre_free:
                        contacts.append(dict(d=f, s=f, op=j, lo=S[f], hi=T[f], F=F, kd=key_of(f), ks=key_of(f), pin=f in pinned, kind='Cread'))
                    else:
                        contacts.append(dict(d=f, s=f, op=j, lo=F, hi=F, F=F, kd=key_of(f), ks=key_of(f), pin=True, kind='Cdeliver' if k == 'add' else 'Cread'))
            else:
                raise SystemExit('FAIL: unknown event ' + kind)
        self.ops, self.contacts, self.warp_ops = ops, contacts, warp_ops
        n = len(ops); self.n = n
        pred = [set() for _ in range(n)]
        last_write = {}; readers = collections.defaultdict(list); adds = collections.defaultdict(list)
        for j, (is_add, W, Rd) in enumerate(ops):
            for r in Rd:
                if r in last_write: pred[j].add(last_write[r])
                pred[j].update(adds.get(r, []))
            for r in W:
                if r in last_write: pred[j].add(last_write[r])
                pred[j].update(readers.get(r, []))
                if is_add: adds[r].append(j)
                else:
                    pred[j].update(adds.get(r, [])); last_write[r] = j; readers[r] = []; adds[r] = []
            for r in Rd: readers[r].append(j)
            pred[j].discard(j)
        bi = 0
        for j in range(n):
            if bi < len(barrier_ops) and j == barrier_ops[bi]:
                if bi > 0: pred[j].update(range(barrier_ops[bi - 1] + 1, j))
                bi += 1
            elif bi > 0: pred[j].add(barrier_ops[bi - 1])
        self.pred = pred
        self.succ = [[] for _ in range(n)]
        for j in range(n):
            for k in pred[j]: self.succ[k].append(j)
        # chains and level sets
        self.chain = []; self.frame_of = {}
        for f in range(nf):
            if f in pinned:
                keys = [('v', i) for i in range(len(chain0[f]))]
                for i, fr in enumerate(chain0[f]): self.frame_of[(f, ('v', i))] = fr
            else:
                keys = []
                for fr in chain0[f]:
                    if fr not in keys: keys.append(fr)
                    self.frame_of[(f, fr)] = fr
            self.chain.append(keys)
        self.cset = [set(ch) for ch in self.chain]
        self.at = collections.defaultdict(set)
        for k, e in enumerate(contacts): self.at[(e['d'], e['kd'])].add(k); self.at[(e['s'], e['ks'])].add(k)

    # frames ---------------------------------------------------------------------------------
    @staticmethod
    def span_of(vs):
        s = {0}
        for v in vs: s |= {x ^ v for x in s}
        return frozenset(s)
    def fid(self, sp):
        if sp not in self.span_id: self.span_id[sp] = len(self.spans); self.spans.append(sp)
        return self.span_id[sp]
    def dim(self, i): return len(self.spans[i]).bit_length() - 1
    def sub(self, a, b): return self.spans[a] <= self.spans[b]
    def join(self, a, b): return a if a == b else self.fid(self.span_of(list(self.spans[a] | self.spans[b])))
    def meet(self, a, b): return self.fid(self.spans[a] & self.spans[b])
    def fdim(self, f, key): return self.dim(self.frame_of[(f, key)])

    # fragmentation ------------------------------------------------------------------------------
    def lam(self, t):
        tot = 0.0
        for f in range(self.nf):
            ds = [self.fdim(f, k) for k in self.chain[f]]
            tot += sum(pw(ds[i + 1] - ds[i], t) for i in range(len(ds) - 1)) - pw(ds[-1] - ds[0], t)
        return tot
    def climb_profile(self):
        prof = collections.Counter()
        for f in range(self.nf):
            ds = [self.fdim(f, k) for k in self.chain[f]]
            for i in range(len(ds) - 1):
                if ds[i + 1] > ds[i]: prof[ds[i + 1] - ds[i]] += 1
        return prof


def pw(x, t): return 0.0 if x <= 0 else math.exp(t * math.log(x))


# ----------------------------------------------------------------------------------------------
# dynamic graph with a Pearce-Kelly topological order
# ----------------------------------------------------------------------------------------------
class DynGraph:
    def __init__(self):
        self.out = []; self.inn = []; self.ord = []
    def node(self, ord_):
        # a strict total order: ties between level nodes that share an operation are broken by the node id
        self.out.append(set()); self.inn.append(set()); self.ord.append((ord_, len(self.out) - 1)); return len(self.out) - 1
    def add_edge(self, u, v):
        """False (graph unchanged) if the edge would close a cycle."""
        if v in self.out[u]: return True
        ord_ = self.ord
        if ord_[u] < ord_[v]: self.out[u].add(v); self.inn[v].add(u); return True
        lb, ub = ord_[v], ord_[u]
        Rf = []; seen = {v}; st = [v]
        while st:
            x = st.pop(); Rf.append(x)
            for y in self.out[x]:
                if y == u: return False
                if y not in seen and ord_[y] <= ub: seen.add(y); st.append(y)
        Rb = []; seenb = {u}; st = [u]
        while st:
            x = st.pop(); Rb.append(x)
            for y in self.inn[x]:
                if y not in seenb and ord_[y] >= lb: seenb.add(y); st.append(y)
        Rb.sort(key=lambda x: ord_[x]); Rf.sort(key=lambda x: ord_[x])
        pos = sorted(ord_[x] for x in Rb + Rf)
        for x, p in zip(Rb + Rf, pos): ord_[x] = p
        self.out[u].add(v); self.inn[v].add(u); return True
    def del_edge(self, u, v): self.out[u].discard(v); self.inn[v].discard(u)


class LevelGraph:
    """ops + level nodes; built in the word's own order (no reordering needed), then edited transactionally."""
    def __init__(self, w):
        self.w = w; n = w.n; G = DynGraph(); self.G = G
        for j in range(n): G.node(2 * j)
        for j in range(n):
            for k in w.pred[j]: require(G.add_edge(k, j), 'dependency DAG is acyclic')
        self.lv = {}
        for f in range(w.nf):
            for key in w.chain[f]:
                ks = w.at.get((f, key))
                if not ks: continue
                idx = [w.contacts[k]['op'] for k in ks]
                ent = G.node(2 * min(idx) - 1); ex = G.node(2 * max(idx) + 1); self.lv[(f, key)] = (ent, ex)
        self.edges = set()
        for f in range(w.nf): self.edges |= self.level_edges(f)
        for u, v in sorted(self.edges): require(G.add_edge(u, v), 'initial level graph is acyclic')

    def level_edges(self, f):
        w = self.w; E = set(); lv = self.lv
        act = [k for k in w.chain[f] if (f, k) in lv and w.at.get((f, k))]   # empty levels are pass-through
        for key in act:
            ent, ex = lv[(f, key)]
            for k in w.at[(f, key)]:
                o = w.contacts[k]['op']; E.add((ent, o)); E.add((o, ex))
        for a, b in zip(act, act[1:]): E.add((lv[(f, a)][1], lv[(f, b)][0]))
        for (j, g, va, A, B) in w.warp_ops:
            if g != f: continue
            ch = w.chain[f]
            if f in w.pinned:
                for key in ch:
                    if (f, key) not in lv: continue
                    if key[1] <= va: E.add((lv[(f, key)][1], j))
                    else: E.add((j, lv[(f, key)][0]))
            else:
                pa, pb = ch.index(A), ch.index(B)
                for i, key in enumerate(ch):
                    if (f, key) not in lv: continue
                    if i <= pa: E.add((lv[(f, key)][1], j))
                    elif i >= pb: E.add((j, lv[(f, key)][0]))
        return E

    def try_state(self, touched):
        """apply the level structure of the touched fields (current chains/at); True iff acyclic; always rolls back."""
        w, G, lv = self.w, self.G, self.lv
        created = []
        for f in touched:
            for key in w.chain[f]:
                if w.at.get((f, key)) and (f, key) not in lv:
                    idx = [w.contacts[k]['op'] for k in w.at[(f, key)]]
                    ent = G.node(2 * min(idx) - 1); ex = G.node(2 * max(idx) + 1); lv[(f, key)] = (ent, ex); created.append((f, key))
        old = set(); new = set()
        for f in touched:
            old |= self.field_edges[f]
            new |= self.level_edges(f)
        for u, v in old - new: G.del_edge(u, v)
        added = []; ok = True
        for u, v in sorted(new - old):
            if not G.add_edge(u, v): ok = False; break
            added.append((u, v))
        for u, v in added: G.del_edge(u, v)
        for u, v in old - new: require(G.add_edge(u, v), 'rollback of a previously acyclic edge')
        for fk in created: lv.pop(fk)
        return ok

    def index_owners(self):
        self.field_edges = [self.level_edges(f) for f in range(self.w.nf)]


# ----------------------------------------------------------------------------------------------
# exhaustive single-level drop test
# ----------------------------------------------------------------------------------------------
def options_for(w, k, f, F):
    """frames of f's chain (other than F) where contact k could happen; each option is (X, partner_insert)."""
    e = w.contacts[k]
    if e['pin'] and e['kind'] != 'Cread': return []
    opts = [X for X in w.chain[f] if X != F and w.sub(e['lo'], X) and w.sub(X, e['hi'])]
    if e['kind'] == 'Cread': return [(X, None) for X in opts if w.dim(X) >= 1]
    g = e['s'] if e['d'] == f else e['d']
    out = []
    for X in opts:
        if X in w.cset[g]: out.append((X, None))
        elif g not in w.pinned and all(w.sub(x, X) or w.sub(X, x) for x in w.chain[g]) and w.sub(w.S[g], X) and w.sub(X, w.T[g]):
            out.append((X, g))
    return out


def drop_test(w, LG, cap=100000, t=1 - 0.0030217759):
    """for every droppable level enumerate all re-routings; returns counters and the list of feasible drops with
    their exact bill change (field climbs + partner insertions + centre transport ranks) at exponent t."""
    res = collections.Counter(); feasible = []; capped = []
    def lam_f(f):
        ds = [w.fdim(f, k) for k in w.chain[f]]
        return sum(pw(ds[i + 1] - ds[i], t) for i in range(len(ds) - 1)) - pw(ds[-1] - ds[0], t)
    def centre(): return sum(pw(w.dim(w.contacts[k]['F']), t) for k in range(len(w.contacts)) if w.contacts[k]['kind'] == 'Cread')
    for f in range(w.nf):
        if f in w.pinned: continue
        for F in list(w.chain[f]):
            if F in (w.S[f], w.T[f]) or F in w.warp_frames[f]: continue
            ks = sorted(w.at.get((f, F), []))
            if not ks: res['empty_level'] += 1; continue
            res['levels'] += 1
            if res['levels'] % 500 == 0: print(f'    ... {res["levels"]} levels enumerated', flush=True)
            opts = [options_for(w, k, f, F) for k in ks]
            if any(not o for o in opts): res['no_plan'] += 1; continue
            # necessary condition: if op a must precede op b (value dependency), the frame of a along f cannot lie
            # above the frame of b (frames of one field never decrease in time)
            kops = {w.contacts[k]['op']: i for i, k in enumerate(ks)}
            before_pairs = []
            for i, k in enumerate(ks):
                src = w.contacts[k]['op']; seen = {src}; st = [src]
                while st:
                    u = st.pop()
                    for v in w.succ[u]:
                        if v not in seen:
                            seen.add(v); st.append(v)
                            if v in kops: before_pairs.append((i, kops[v]))
            posf = {X: p for p, X in enumerate(w.chain[f])}
            def consistent(combo):
                return all(posf[combo[a][0]] <= posf[combo[b][0]] for a, b in before_pairs)
            total = 1
            for o in opts: total *= len(o)
            combos = (c for c in itertools.product(*opts) if consistent(c))
            if total > cap: capped.append((f, F, total)); res['pruned_levels'] += 1
            res['plans'] += total
            found = None
            for combo in itertools.islice(combos, cap):
                partners = {g for (X, g) in combo if g is not None}
                before = lam_f(f) + sum(lam_f(g) for g in partners) + centre()
                # apply: insert partner frames, move contacts, remove level
                inserted = []; moved = []
                for k, (X, g) in zip(ks, combo):
                    e = w.contacts[k]
                    if g is not None and X not in w.cset[g]:
                        pos = len(w.chain[g])
                        for i, x in enumerate(w.chain[g]):
                            if w.dim(x) > w.dim(X): pos = i; break
                        w.chain[g].insert(pos, X); w.cset[g].add(X); w.frame_of[(g, X)] = X; inserted.append((g, X))
                    w.at[(e['d'], e['kd'])].discard(k); w.at[(e['s'], e['ks'])].discard(k)
                    moved.append((k, e['F'], e['kd'], e['ks']))
                    e['F'] = X; e['kd'] = X; e['ks'] = X; w.at[(e['d'], X)].add(k); w.at[(e['s'], X)].add(k)
                posF = w.chain[f].index(F); w.chain[f].remove(F); w.cset[f].discard(F)
                touched = {f} | {e['d'] for k in ks for e in [w.contacts[k]]} | {e['s'] for k in ks for e in [w.contacts[k]]}
                ok = LG.try_state(touched)
                after = lam_f(f) + sum(lam_f(g) for g in partners) + centre()
                # rollback state
                w.chain[f].insert(posF, F); w.cset[f].add(F)
                for k, F0, kd, ks_ in moved:
                    e = w.contacts[k]; w.at[(e['d'], e['kd'])].discard(k); w.at[(e['s'], e['ks'])].discard(k)
                    e['F'], e['kd'], e['ks'] = F0, kd, ks_; w.at[(e['d'], kd)].add(k); w.at[(e['s'], ks_)].add(k)
                for g, X in inserted: w.chain[g].remove(X); w.cset[g].discard(X); w.frame_of.pop((g, X), None)
                if ok and (found is None or after - before < found): found = after - before
            if found is not None:
                res['feasible'] += 1; feasible.append((f, F, round(found, 6)))
                if found < -1e-9: res['improving'] += 1
            else: res['cycle'] += 1
    return res, feasible, capped


# ----------------------------------------------------------------------------------------------
# kap-family ceilings (what Lambda would buy)
# ----------------------------------------------------------------------------------------------
def kap_ceiling(H, Nloc, ports=112, block=8, pmax=40):
    def momD(P, t): return sum(D(n) * (D(0) if r == 0 else (t * D(r).ln()).exp()) for r, n in P.items())
    def mom(P, t): return sum(n * pw(r, t) for r, n in P.items())
    def inv(p, a):
        T = collections.Counter({r: (p + 2) * n for r, n in H.items()}); P = collections.Counter({r: (p + 2) * n for r, n in Nloc.items()})
        P[1] += ports * (p - 1); T[1 + block * (p + 2)] += 2 * ports
        for L in (a, p - 1 - a):
            for j in range(1, L + 1): T[1 + block * (j + 1)] += 2 * ports; P[block * (j + 1)] += 2 * ports
        return T, P
    def root(T, P, exact):
        lo, hi = (D('1e-7'), D('0.2')) if exact else (1e-7, 0.2)
        f = (lambda c: momD(T, 1 - c) - momD(P, 1 - c)) if exact else (lambda c: mom(T, 1 - c) - mom(P, 1 - c))
        if f(lo) <= 0: return lo * 0
        if f(hi) > 0: return hi
        for _ in range(100 if exact else 50):
            m = (lo + hi) / 2
            if f(m) > 0: lo = m
            else: hi = m
        return lo
    best = max((root(*inv(p, a), False), p, a) for p in range(2, pmax + 1) for a in range(0, (p - 1) // 2 + 1))
    T, P = inv(best[1], best[2])
    return root(T, P, True), best[1], best[2], root(*inv(16, 7), True)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--write', action='store_true'); args = ap.parse_args()
    t_start = time.time(); pinned_inputs()
    word = json.loads(gzip.decompress((W3 / 'ACTUAL-WORD.json.gz').read_bytes()))
    arith = json.loads((W3 / 'ARITHMETIC.json').read_text(encoding='utf-8'))
    t0 = 1 - 0.0030217759
    w = Word(word, arith)
    out = {}
    # [1] word census
    prof = w.climb_profile(); prof_c = collections.Counter(prof); prof_c[8] += 8
    require(dict(prof_c) == w.N, 'climb profile + 8 centre jobs equals ARITHMETIC local_paid')
    lam0 = w.lam(t0)
    print(f'[1] word: {w.nf} fields ({w.nm} mains, {w.nf - w.nm} helpers), {len(w.prog)} events, {w.n} ops, '
          f'{sum(1 for e in w.contacts if e["kind"] == "LL")} two-field contacts, {sum(1 for e in w.contacts if e["kind"] != "LL")} centre contacts; '
          f'climb profile {dict(sorted(prof.items()))}; Lambda(t0) = {lam0:.4f}')
    require(abs(lam0 - 23.8626369) < 2e-6, 'Lambda of the word at its own root (#5226: 23.8626)')
    out['lambda_word'] = round(lam0, 7); out['climb_profile'] = {str(k): v for k, v in sorted(prof.items())}
    dims = collections.Counter(w.dim(e['F']) for e in w.contacts if e['kind'] == 'LL')
    out['contacts_by_dimension'] = {str(k): v for k, v in sorted(dims.items())}
    levels_total = sum(1 for f in range(w.nf) for F in w.chain[f][1:-1] if w.at.get((f, F)))
    # [2] dependency slack
    n = w.n; asap = [0] * n
    for j in range(n): asap[j] = 1 + max((asap[k] for k in w.pred[j]), default=-1)
    out['dag'] = {'ops': n, 'edges': sum(len(p) for p in w.pred), 'critical_path': max(asap) + 1}
    print(f'[2] dependency DAG: {n} ops, {out["dag"]["edges"]} edges, critical path {out["dag"]["critical_path"]} (order is loose)')
    # [3] one-field-at-a-time relaxations
    forced_end = forced_exact = 0; lv_cnt = 0
    chainset = [set(ch) for ch in w.chain]
    for f in range(w.nf):
        ch = w.chain[f]
        for i in range(1, len(ch) - 1):
            ks = [k for k in w.at.get((f, ch[i]), []) if w.contacts[k]['kind'] == 'LL']
            if not ks: continue
            lv_cnt += 1
            fr = lambda key: w.frame_of[(f, key)]
            nxt, prv = fr(ch[i + 1]), fr(ch[i - 1])
            def partner(k): e = w.contacts[k]; return e['s'] if e['d'] == f else e['d']
            if not all(w.sub(nxt, w.T[partner(k)]) or (w.sub(w.S[partner(k)], prv) and w.sub(prv, w.T[partner(k)])) for k in ks): forced_end += 1
            if not all(ch[i + 1] in chainset[partner(k)] or ch[i - 1] in chainset[partner(k)] for k in ks): forced_exact += 1
    out['levels_with_two_field_contacts'] = lv_cnt
    out['forced_by_partner_endpoints'] = forced_end; out['forced_by_partner_chains'] = forced_exact
    print(f'[3] levels with two-field contacts {lv_cnt}: forced by partner endpoints alone {forced_end}; forced by the partners\' exact chains {forced_exact}')
    # [4] exhaustive drop test, exact rules
    t1 = time.time(); LG = LevelGraph(w); LG.index_owners()
    res, feasible, capped = drop_test(w, LG)
    print(f'[4] exact rules: levels {res["levels"]}, re-routings enumerated {res["plans"]}, no re-routing {res["no_plan"]}, '
          f'all re-routings cyclic {res["cycle"]}, feasible drops {res["feasible"]} (bill-improving {res["improving"]}), capped levels {len(capped)} ({time.time() - t1:.0f}s)')
    for f, F, delta in feasible: print(f'    feasible drop: field {f} ({"main" if f < w.nm else "helper"}) frame {F} dim {w.dim(F)}: best bill change {delta:+.4f} (the centre read moves to the full frame)')
    require(res['improving'] == 0, 'no level of the #4610 word can be dropped at a gain under the exact rules')
    require(not capped or all(any(w.contacts[k]['kind'] == 'Cread' for k in w.at[(f, F)]) for f, F, _ in capped), 'only centre-read levels exceed the enumeration cap (their consistent re-routings are all enumerated)')
    require(all(any(w.contacts[k]['kind'] == 'Cread' for k in w.at[(f, F)]) for f, F, _ in feasible), 'every feasible drop is a centre-read level')
    out['exact'] = dict(res); out['exact']['feasible_drops'] = feasible
    # [5] control: centre contacts ignored -> drops appear (the test is live)
    t1 = time.time(); w2 = Word(word, arith, pin_centre=False); LG2 = LevelGraph(w2); LG2.index_owners()
    res2, feas2, capped2 = drop_test(w2, LG2)
    print(f'[5] control, centre contacts ignored: feasible drops {res2["feasible"]} (improving {res2["improving"]}) of {res2["levels"]} levels (no re-routing {res2["no_plan"]}, cyclic {res2["cycle"]}, capped {len(capped2)}) ({time.time() - t1:.0f}s)')
    require(res2['improving'] >= 5, 'the drop test finds improving drops when the centre interface is ignored')
    out['control_no_centre'] = dict(res2); out['control_no_centre']['first_drops'] = feas2[:10]
    # [6] what Lambda would buy: kap-family ceilings
    H = w.H; Nc = collections.Counter(w.N)
    mains = collections.Counter(); helps = collections.Counter(); cur = list(w.S); jobs = collections.defaultdict(list)
    for e in w.prog:
        if e[0] == 'climb': jobs[e[2]].append(e[5])
    for f in range(w.nf):
        for r in jobs[f]: (mains if f < w.nm else helps)[r] += 1
    centre = collections.Counter({8: 8})
    table = {}
    for name, N_ in (('word', mains + helps + centre), ('mains_one_climb', collections.Counter({8: w.nm}) + helps + centre),
                     ('helpers_one_climb', mains + collections.Counter(H) + centre), ('lambda_zero', collections.Counter({8: w.nm}) + collections.Counter(H) + centre)):
        k, p, a, k16 = kap_ceiling(H, N_)
        table[name] = {'kappa_best': f'{k:.10f}', 'p': p, 'a': a, 'kappa_p16a7': f'{k16:.10f}'}
        print(f'[6] {name:18s}: kappa {k:.10f} at p={p} a={a}; at p16 a7 {k16:.10f}')
    require(D('0.0030217758') < D(table['word']['kappa_p16a7']) < D('0.0030217760'), 'kap formula reproduces kappa(#4610)')
    require(D(table['lambda_zero']['kappa_best']) > D('0.0081'), 'Lambda = 0 ceiling of the kap family above 0.0081')
    out['kap_family'] = table
    # result file
    path = HERE / 'RESULT.json'
    if args.write:
        path.write_text(json.dumps(out, indent=1, sort_keys=True) + '\n', encoding='utf-8'); print('wrote', path)
    else:
        stored = json.loads(path.read_text(encoding='utf-8'))
        require(stored == json.loads(json.dumps(out, sort_keys=True)), 'stored RESULT.json equals the rebuilt result')
    print(f'PASS_FRAGMENTATION_REORDER_RIGIDITY ({time.time() - t_start:.0f}s)')


if __name__ == '__main__':
    main()
