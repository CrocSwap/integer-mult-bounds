#!/usr/bin/env python3
"""JCR search v4: same model as v3 (joint frame chains + contact frames, free scalar order within value
dependencies, warp frames fixed, 12 revisiting fields pinned), but with an INCREMENTAL acyclicity check
(Pearce-Kelly dynamic topological order) instead of a full graph rebuild per move, and a systematic sweep
phase before annealing.

Graph nodes: the 18,149 ops (static DAG edges) plus dynamic level nodes entry/exit per (field, level) that
currently hosts contacts.  Edges: entry(f,L) -> op -> exit(f,L) for every contact op at that level, and
exit(f,L_i) -> entry(f,L_{i+1}) along each chain; warp ops anchored between their two frames.
A move = a set of edge deletions followed by edge insertions; an insertion that closes a cycle rejects the move
and everything is rolled back.

Usage: py -3.12 jcr_search4.py [minutes=60] [seed=1]
"""
import json, gzip, collections, os, time, sys, math, random
W3 = 'D:/Math/imb-docking/research/kappa-round3-warp-20261022/'
HERE = os.path.dirname(os.path.abspath(__file__)); LOG = open(os.path.join(HERE, 'progress.log'), 'a')
def log(*a):
    s = time.strftime('%H:%M:%S ') + ' '.join(str(x) for x in a); print(s, flush=True); LOG.write(s + '\n'); LOG.flush()
MINUTES = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 1
random.seed(SEED)
t = 1 - 0.0030217759
def pw(x): return 0.0 if x <= 0 else math.exp(t * math.log(x))

# ---------------- word ----------------
w = json.loads(gzip.decompress(open(W3 + 'ACTUAL-WORD.json.gz', 'rb').read()))
c = w['canonical']; frames = c['frames']; nf = len(c['start']); S = list(c['start']); T = list(c['final']); nm = 224
prog = w['programs']['forward']
def span_of(vs):
    s = {0}
    for v in vs: s |= {x ^ v for x in s}
    return frozenset(s)
spans = [span_of(fr) for fr in frames]; span_id = {sp: i for i, sp in enumerate(spans)}
def fid(sp):
    if sp not in span_id: span_id[sp] = len(spans); spans.append(sp)
    return span_id[sp]
def dim(i): return len(spans[i]).bit_length() - 1
def sub(a, b): return spans[a] <= spans[b]
def join(a, b): return a if a == b else fid(span_of(list(spans[a] | spans[b])))
def meet(a, b): return fid(spans[a] & spans[b])

cur = list(S); chain0 = [[S[f]] for f in range(nf)]; pinned_f = set(); warp_frames = collections.defaultdict(set)
for e in prog:
    if e[0] == 'climb':
        f = e[2]
        if e[4] in chain0[f]: pinned_f.add(f)
        chain0[f].append(e[4]); cur[f] = e[4]
    elif e[0] == 'warp':
        f = e[1][1]
        if e[4] != e[3]:
            if e[4] in chain0[f]: pinned_f.add(f)
            warp_frames[f].add(cur[f]); warp_frames[f].add(e[4]); chain0[f].append(e[4])
        cur[f] = e[4]
ops = []; contacts = []; warp_ops = []; barriers = []; block_ops = []   # phase markers are barriers
cur = list(S); visit = [0] * nf
def key_of(f): return ('v', visit[f]) if f in pinned_f else cur[f]
for e in prog:
    if e[0] == 'climb': f = e[2]; cur[f] = e[4]; visit[f] += 1
    elif e[0] == 'warp':
        f = e[1][1]; j = len(ops); ops.append((False, {('L', f)}, set()))
        if e[4] != e[3]: warp_ops.append((j, f, visit[f], cur[f], e[4])); cur[f] = e[4]; visit[f] += 1
    elif e[0] == 'phase':
        if e[1] in ('zero_frame_precondition', 'full_frame_cleanup', 'done') and not os.environ.get('JCR_NOBARRIER'): barriers.append(len(ops))
        ops.append((False, set(), set()))
    elif e[0] == 'center': ops.append((False, {('L', e[2])}, set()))
    elif e[0] == 'adapter': ops.append((False, {('L', e[2]), ('L', e[3])}, set()))
    elif e[0] == 'scalar':
        op = e[1]; kind = op[0]; roles = [tuple(r) for r in op[1:] if isinstance(r, list)]
        W, Rd = ({roles[0]}, {roles[1]}) if kind in ('add', 'copy') else ({roles[0]}, set())
        j = len(ops); ops.append((kind == 'add', W, Rd))
        if kind in ('add', 'copy') and roles[0][0] == 'L' and roles[1][0] == 'L':
            d, s = roles[0][1], roles[1][1]; F = e[2]
            lo = join(S[d], S[s]); hi = meet(T[d], T[s])
            if not sub(lo, F): lo = F
            contacts.append({'d': d, 's': s, 'op': j, 'lo': lo, 'hi': hi, 'F': F, 'kd': key_of(d), 'ks': key_of(s),
                             'pin': (d in pinned_f or s in pinned_f)})
        elif kind in ('add', 'copy') and sum(r[0] == 'L' for r in roles) == 1 and not os.environ.get('JCR_NOC'):
            f = next(r[1] for r in roles if r[0] == 'L'); F = e[2]      # contact with the owned C0 buffer: pinned
            contacts.append({'d': f, 's': f, 'op': j, 'lo': F, 'hi': F, 'F': F, 'kd': key_of(f), 'ks': key_of(f), 'pin': True, 'C': True})
        # 'scale' ops commute with climbs: they stay in the DAG only and take the field's current frame when emitted
n = len(ops)
pred = [set() for _ in range(n)]
# barrier edges: every op depends on the last phase marker before it, and the next marker depends on every op
bi = 0
for j in range(n):
    if bi < len(barriers) and j == barriers[bi]:
        if bi > 0:
            for k in range(barriers[bi - 1] + 1, j): pred[j].add(k)
        bi += 1
    elif bi > 0: pred[j].add(barriers[bi - 1])
last_write = {}; readers = collections.defaultdict(list); adds = collections.defaultdict(list)
for j, (is_add, W, Rd) in enumerate(ops):
    for r in Rd:
        if r in last_write: pred[j].add(last_write[r])
        pred[j].update(adds.get(r, []))
    for r in W:
        if r in last_write: pred[j].add(last_write[r])
        pred[j].update(readers.get(r, []))
        if is_add: adds[r].append(j)
        else: pred[j].update(adds.get(r, [])); last_write[r] = j; readers[r] = []; adds[r] = []
    for r in Rd: readers[r].append(j)
    pred[j].discard(j)
log(f'JCR v4: fields {nf} (pinned {len(pinned_f)}), contacts {len(contacts)}, ops {n}, dag edges {sum(len(p) for p in pred)}, frames {len(spans)}')

# ---------------- dynamic graph with Pearce-Kelly order ----------------
class DynGraph:
    def __init__(self, nstatic, pred):
        self.out = [set() for _ in range(nstatic)]; self.inn = [set() for _ in range(nstatic)]
        for j in range(nstatic):
            for k in pred[j]: self.out[k].add(j); self.inn[j].add(k)
        self.ord = list(range(nstatic))          # node -> position
        self.free = []
    def new_node(self):
        if self.free: u = self.free.pop(); self.out[u] = set(); self.inn[u] = set(); return u
        u = len(self.out); self.out.append(set()); self.inn.append(set()); self.ord.append(self.ord and max(self.ord) + 1 or 0)
        return u
    def del_node(self, u):
        assert not self.out[u] and not self.inn[u]; self.free.append(u)
    def del_edge(self, u, v): self.out[u].discard(v); self.inn[v].discard(u)
    def add_edge(self, u, v):
        """returns False (and leaves the graph unchanged) if the edge would close a cycle."""
        if v in self.out[u]: return True
        ord = self.ord
        if ord[u] < ord[v]: self.out[u].add(v); self.inn[v].add(u); return True
        lb, ub = ord[v], ord[u]
        # forward from v within (.., ub]
        Rf = []; seen = {v}; st = [v]
        while st:
            x = st.pop(); Rf.append(x)
            for y in self.out[x]:
                if y == u: return False
                if y not in seen and ord[y] <= ub: seen.add(y); st.append(y)
        Rb = []; seenb = {u}; st = [u]
        while st:
            x = st.pop(); Rb.append(x)
            for y in self.inn[x]:
                if y not in seenb and ord[y] >= lb: seenb.add(y); st.append(y)
        # reorder: nodes of Rb then Rf take the sorted positions of Rb ∪ Rf
        Rb.sort(key=lambda x: ord[x]); Rf.sort(key=lambda x: ord[x])
        pos = sorted(ord[x] for x in Rb + Rf)
        for x, p in zip(Rb + Rf, pos): ord[x] = p
        self.out[u].add(v); self.inn[v].add(u); return True

G = DynGraph(n, pred)

# ---------------- state ----------------
chain = []; frame_of = {}
for f in range(nf):
    if f in pinned_f:
        keys = [('v', i) for i in range(len(chain0[f]))]
        for i, fr in enumerate(chain0[f]): frame_of[(f, ('v', i))] = fr
    else:
        keys = []
        for fr in chain0[f]:
            if fr not in keys: keys.append(fr)
            frame_of[(f, fr)] = fr
    chain.append(keys)
cset = [set(ch) for ch in chain]
at = collections.defaultdict(set)
for k, e in enumerate(contacts): at[(e['d'], e['kd'])].add(k); at[(e['s'], e['ks'])].add(k)
lvnode = {}                                  # (f, key) -> (entry, exit) for levels with contacts
def fdim(f, key): return dim(frame_of[(f, key)])
def lam_field(f):
    ds = [fdim(f, k) for k in chain[f]]
    return sum(pw(ds[i+1] - ds[i]) for i in range(len(ds) - 1)) - pw(ds[-1] - ds[0])
LAM = [lam_field(f) for f in range(nf)]
def total(): return sum(LAM)

# build initial level graph in word order (cannot fail)
def active_levels(f): return [k for k in chain[f] if (f, k) in lvnode]
for f in range(nf):
    for key in chain[f]:
        if at.get((f, key)):
            ent, ex = G.new_node(), G.new_node(); lvnode[(f, key)] = (ent, ex)
            for k in at[(f, key)]:
                o = contacts[k]['op']; assert G.add_edge(ent, o) and G.add_edge(o, ex)
    al = active_levels(f)
    for a, b in zip(al, al[1:]): assert G.add_edge(lvnode[(f, a)][1], lvnode[(f, b)][0])
def warp_anchor_edges(j, f, va, A, B):
    """edges (u, v) anchoring warp op j for the current chain of f."""
    out = []; ch = chain[f]
    if f in pinned_f:
        for key in ch:
            if (f, key) not in lvnode: continue
            if key[1] <= va: out.append((lvnode[(f, key)][1], j))
            else: out.append((j, lvnode[(f, key)][0]))
    else:
        pa, pb = ch.index(A), ch.index(B)
        for i, key in enumerate(ch):
            if (f, key) not in lvnode: continue
            if i <= pa: out.append((lvnode[(f, key)][1], j))
            elif i >= pb: out.append((j, lvnode[(f, key)][0]))
    return out
for wo in warp_ops:
    for u, v in warp_anchor_edges(*wo): assert G.add_edge(u, v)
warps_of = collections.defaultdict(list)
for wo in warp_ops: warps_of[wo[1]].append(wo)
log(f'initial Lambda = {total():.4f}; dynamic graph built, nodes {len(G.out)}')

# ---------------- transactional edits ----------------
class Txn:
    """collects structural changes; graph edges are re-derived for touched fields and applied with rollback."""
    def __init__(self): self.touched = set(); self.undo = []; self.added = []; self.removed = []
    def set_contact(self, k, Fnew):
        e = contacts[k]; self.undo.append(('c', k, e['F'], e['kd'], e['ks']))
        at[(e['d'], e['kd'])].discard(k); at[(e['s'], e['ks'])].discard(k)
        e['F'] = Fnew; e['kd'] = Fnew; e['ks'] = Fnew
        at[(e['d'], Fnew)].add(k); at[(e['s'], Fnew)].add(k); self.touched.update((e['d'], e['s']))
    def insert_frame(self, f, F):
        pos = len(chain[f])
        for i, x in enumerate(chain[f]):
            if dim(x) > dim(F): pos = i; break
        chain[f].insert(pos, F); cset[f].add(F); frame_of[(f, F)] = F; LAM[f] = lam_field(f)
        self.undo.append(('i', f, F)); self.touched.add(f)
    def remove_frame(self, f, F):
        chain[f].remove(F); cset[f].discard(F); at.pop((f, F), None); frame_of.pop((f, F), None); LAM[f] = lam_field(f)
        self.undo.append(('r', f, F)); self.touched.add(f)
    def rollback_state(self):
        while self.undo:
            kind, *a = self.undo.pop()
            if kind == 'c':
                k, F, kd, ks = a; e = contacts[k]
                at[(e['d'], e['kd'])].discard(k); at[(e['s'], e['ks'])].discard(k)
                e['F'], e['kd'], e['ks'] = F, kd, ks; at[(e['d'], kd)].add(k); at[(e['s'], ks)].add(k)
            elif kind == 'i':
                f, F = a; chain[f].remove(F); cset[f].discard(F); frame_of.pop((f, F), None); LAM[f] = lam_field(f)
            else:
                f, F = a; pos = len(chain[f])
                for i, x in enumerate(chain[f]):
                    if dim(x) > dim(F): pos = i; break
                chain[f].insert(pos, F); cset[f].add(F); frame_of[(f, F)] = F; LAM[f] = lam_field(f)

def level_edges(f):
    """all graph edges owned by field f's level structure (contact edges, chain edges, warp anchors)."""
    E = set()
    al = active_levels(f)
    for key in al:
        ent, ex = lvnode[(f, key)]
        for k in at[(f, key)]:
            o = contacts[k]['op']; E.add((ent, o)); E.add((o, ex))
    for a, b in zip(al, al[1:]): E.add((lvnode[(f, a)][1], lvnode[(f, b)][0]))
    for wo in warps_of.get(f, []): E.update(warp_anchor_edges(*wo))
    return E

def commit_graph(txn):
    """re-derive the level graph of touched fields; return True if acyclic (edges applied), else rollback edges."""
    old = {}
    for f in txn.touched: old[f] = level_edges_snapshot[f]
    # create/delete level nodes according to current `at`
    newnodes = []; delnodes = []
    for f in txn.touched:
        for key in chain[f]:
            has = bool(at.get((f, key)))
            if has and (f, key) not in lvnode: lvnode[(f, key)] = (G.new_node(), G.new_node()); newnodes.append((f, key))
        for (ff, key) in [x for x in lvnode if x[0] == f]:
            if key not in chain[f] or not at.get((f, key)): delnodes.append((f, key))
    new = {}
    for f in txn.touched: new[f] = level_edges(f)
    oldE = set().union(*old.values()) if old else set(); newE = set().union(*new.values()) if new else set()
    for u, v in oldE - newE: G.del_edge(u, v)
    added = []
    ok = True
    for u, v in newE - oldE:
        if not G.add_edge(u, v): ok = False; break
        added.append((u, v))
    if not ok:
        for u, v in added: G.del_edge(u, v)
        for u, v in oldE - newE: assert G.add_edge(u, v)
        for fk in newnodes: ent, ex = lvnode.pop(fk); G.del_node(ent); G.del_node(ex)
        return False
    for fk in delnodes:
        ent, ex = lvnode.pop(fk); G.del_node(ent); G.del_node(ex)
    for f in txn.touched: level_edges_snapshot[f] = new[f]
    return True
level_edges_snapshot = [level_edges(f) for f in range(nf)]

def apply(txn):
    """finish a transaction: graph check; on failure roll back state too."""
    if commit_graph(txn): return True
    txn.rollback_state()
    # level nodes for fields whose `at` was restored may need re-creation on the next commit; keep lvnode consistent:
    for f in txn.touched:
        for key in chain[f]:
            if at.get((f, key)) and (f, key) not in lvnode:
                lvnode[(f, key)] = (G.new_node(), G.new_node())
                for k in at[(f, key)]:
                    o = contacts[k]['op']; assert G.add_edge(lvnode[(f, key)][0], o) and G.add_edge(o, lvnode[(f, key)][1])
        level_edges_snapshot[f] = level_edges(f)
    return False

def nested_ok(f, F):
    return f not in pinned_f and all(sub(x, F) or sub(F, x) for x in chain[f]) and sub(S[f], F) and sub(F, T[f])
def removable(f, F): return f not in pinned_f and F != S[f] and F != T[f] and F not in warp_frames[f]

def drop_level(f, F, txn):
    if not removable(f, F): return False
    plan = []
    for k in list(at.get((f, F), [])):
        e = contacts[k]
        if e['pin']: return False
        g = e['s'] if e['d'] == f else e['d']
        opts = [X for X in chain[f] if X != F and sub(e['lo'], X) and sub(X, e['hi'])]
        if e.get('U'):
            if not opts: return False
            plan.append((k, random.choice(opts), None)); continue
        common = [X for X in opts if X in cset[g]]
        if common: plan.append((k, random.choice(common), None)); continue
        ins = [X for X in opts if nested_ok(g, X)]
        if not ins: return False
        plan.append((k, random.choice(ins), g))
    for k, X, g in plan:
        if g is not None and X not in cset[g]: txn.insert_frame(g, X)
        txn.set_contact(k, X)
    txn.remove_frame(f, F); return True
def reroute(k, txn):
    e = contacts[k]
    if e['pin']: return False
    d, s = e['d'], e['s']
    opts = [X for X in chain[d] if X in cset[s] and X != e['F'] and sub(e['lo'], X) and sub(X, e['hi'])]
    if e.get('U') and opts: txn.set_contact(k, random.choice(opts)); return True
    if not opts: return False
    txn.set_contact(k, random.choice(opts)); return True
def new_frame(k, txn):
    e = contacts[k]
    if e['pin'] or e.get('U'): return False
    d, s = e['d'], e['s']
    cand = [X for X in random.sample(range(len(spans)), 40) if X != e['F'] and sub(e['lo'], X) and sub(X, e['hi'])
            and (X in cset[d] or nested_ok(d, X)) and (X in cset[s] or nested_ok(s, X))]
    if not cand: return False
    X = random.choice(cand)
    if X not in cset[d]: txn.insert_frame(d, X)
    if X not in cset[s]: txn.insert_frame(s, X)
    txn.set_contact(k, X); return True
def drop_empty(txn):
    for f in list(txn.touched):
        for F in list(chain[f]):
            if removable(f, F) and not at.get((f, F)): txn.remove_frame(f, F)

free_fields = [f for f in range(nf) if f not in pinned_f]; free_contacts = [k for k, e in enumerate(contacts) if not e['pin']]
best = total(); cur_val = best
def save(tag):
    prof = collections.Counter()
    for f in range(nf):
        ds = [fdim(f, k) for k in chain[f]]
        for i in range(len(ds) - 1):
            if ds[i+1] > ds[i]: prof[ds[i+1] - ds[i]] += 1
    # topological order of all graph nodes (Kahn on the dynamic graph), ops only
    indeg = {u: len(G.inn[u]) for u in range(len(G.out)) if u < n or (G.out[u] or G.inn[u])}
    ready = sorted([u for u, dg in indeg.items() if dg == 0], key=lambda u: G.ord[u]); order = []
    import heapq
    heap = [(G.ord[u], u) for u in ready]; heapq.heapify(heap)
    while heap:
        _, u = heapq.heappop(heap); order.append(u)
        for v_ in G.out[u]:
            indeg[v_] -= 1
            if indeg[v_] == 0: heapq.heappush(heap, (G.ord[v_], v_))
    assert len(order) == len(indeg), 'cyclic at save'
    json.dump({'best': best, 'profile': dict(prof), 'chains': [[str(k) for k in ch] for ch in chain],
               'chain_frames': [[frame_of[(f, k)] for k in ch] for f, ch in enumerate(chain)],
               'contact_frames': [e['F'] for e in contacts], 'contact_ops': [e['op'] for e in contacts],
               'op_order': [u for u in order if u < n], 'extra_frames': [sorted(spans[i]) for i in range(len(frames), len(spans))], 'tag': tag},
              open(os.path.join(HERE, f'jcr4_state_seed{SEED}.json'), 'w'))
    return prof

# ---------------- phase 1: systematic sweep (greedy, downhill only) ----------------
start = time.time(); deadline = start + MINUTES * 60
sweep = 0; gained = 0
while time.time() < deadline and sweep < 3:
    sweep += 1; improved = 0; f_plan = f_cost = f_cycle = 0
    order = list(free_fields); random.shuffle(order)
    for f in order:
        for F in list(chain[f]):
            if not removable(f, F) or F not in chain[f]: continue
            txn = Txn(); before = total()
            if not drop_level(f, F, txn): txn.rollback_state(); f_plan += 1; continue
            drop_empty(txn)
            if total() > before + 1e-12: txn.rollback_state(); f_cost += 1; continue
            if apply(txn): improved += 1; cur_val = total()
            else: f_cycle += 1
    gained += improved
    log(f'sweep {sweep}: {improved} levels dropped, Lambda {total():.4f}; failed: no plan {f_plan}, cost {f_cost}, cycle {f_cycle}')
    if improved == 0: break
best = total(); save('sweep')

# ---------------- phase 2: annealing ----------------
Temp = 0.02; it = acc = rej = 0; last_ck = time.time()
log(f'annealing until {MINUTES} min, seed {SEED}')
while time.time() < deadline:
    it += 1
    txn = Txn(); before = cur_val
    r = random.random()
    if r < 0.5:
        f = random.choice(free_fields); inner = [F for F in chain[f] if removable(f, F)]
        if not inner: continue
        ok = drop_level(f, random.choice(inner), txn)
    elif r < 0.8: ok = reroute(random.choice(free_contacts), txn)
    else: ok = new_frame(random.choice(free_contacts), txn)
    if not ok: txn.rollback_state(); continue
    drop_empty(txn)
    after = total(); delta = after - before
    if delta <= 0 or random.random() < math.exp(-delta / Temp):
        if apply(txn): cur_val = after; acc += 1
        else: rej += 1
    else: txn.rollback_state()
    if cur_val < best - 1e-12: best = cur_val; save('anneal')
    Temp = max(0.002, Temp * 0.99998)
    if time.time() - last_ck > 180:
        last_ck = time.time()
        log(f'it {it} acc {acc} cyc-rejected {rej} T {Temp:.4f} cur {cur_val:.4f} best {best:.4f}')
prof = save('final')
hist = collections.Counter(sum(1 for i in range(len(ch) - 1) if fdim(f, ch[i+1]) > fdim(f, ch[i])) for f, ch in enumerate(chain))
log(f'FINAL best Lambda = {best:.4f} (word 23.8626); climbs/field hist {dict(sorted(hist.items()))}; climb profile {dict(sorted(prof.items()))}')
log('done jcr_search4')
