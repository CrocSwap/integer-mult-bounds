"""Re-derive a concave-descent frame selection (Rohan Arun's #287 rule, re-implemented): local descent of
sum_r n_r r ln(m/r), m = 5h over the parity-fused ADD word; each move reassigns one ADD gate to a frame already on one of
its operands' chains, keeping nested chains, fixed endpoints, exact integer operand source spans and nondegeneracy.
usage: descent_search.py PKG OUT.json [--compare FROZEN.json]"""
import sys, importlib.util, json, time, math, hashlib
from collections import Counter, defaultdict
from pathlib import Path
root = Path(sys.argv[1]).resolve(); sys.path.insert(0, str(root)); outp = Path(sys.argv[2])
def load(name, p):
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); sys.modules[name] = m; spec.loader.exec_module(m); return m
t0 = time.time()
context = load('portable527_prepare', root / 'prepare.py').prepare()
phys = load('portable527_physical', root / 'code/physical527.py')
producer = phys.run(dict(context), context['SOURCE_TEXT'], output_dir=None)
pr = load('portable527_parity', root / 'parity_transform.py').run(producer, output_dir=None)
print('parity done %.0fs' % (time.time() - t0), flush=True)
W, C = pr['W'], pr['C']; v = W.v; old = pr['records']; initial = pr['initial_state']; n = len(initial); ZERO, FULL = pr['ZERO'], pr['FULL']
final = {i: FULL for i in initial}
for t in range(v): final[v + t] = W.register(W.module.kernel([C.cov[t]], W.h)[0])
M = 5 * W.h; LN = [0.0] + [d * math.log(M / d) for d in range(1, M + 1)]
def cost(x, y): return LN[C.dimf[y] - C.dimf[x]]
# chains: per register list of frames (needs); gate -> [(reg, pos)]
chain = {i: [] for i in initial}; gate_slots = {}; gates = []
copy = None; in_copy = set()
N = len(old) // 6
for k in range(N):
    op, a, b, c, f, z = old[6*k:6*k+6]
    if op == 1:
        slots = [(a, len(chain[a]))]; chain[a].append(f)
        if b != n: slots.append((b, len(chain[b]))); chain[b].append(f)
        gate_slots[k] = slots; gates.append(k)
        if copy is not None and (a == copy[0] or b == copy[0]): in_copy.add(k)
        if b == n: in_copy.add(k)
    elif op == 2: copy = (a, b, c); chain[a].append(c)
    elif op == 3: copy = None
gate_frame = {k: old[6*k+4] for k in gates}
def prevf(reg, pos): return chain[reg][pos-1] if pos > 0 else initial[reg]
def nextf(reg, pos): return chain[reg][pos+1] if pos + 1 < len(chain[reg]) else final[reg]
def total():
    H = Counter()
    for i in initial:
        bef = initial[i]
        for f in chain[i] + [final[i]]:
            d = C.dimf[f] - C.dimf[bef]
            if d: H[d] += 1
            bef = f
    return H
H0 = total(); L0 = sum(LN[d] * c for d, c in H0.items())
print('base chain histogram mass', sum(d*c for d, c in H0.items()), 'calls', sum(H0.values()), 'L %.1f' % L0, flush=True)
nd_cache = {}
def nondeg(g):
    if g not in nd_cache: nd_cache[g] = C.nondeg(g)
    return nd_cache[g]
chi = C.chi
def contains_span(g, srcs):
    A = C.A[g]
    return all(all(W.module.dot(x, chi[s]) == 0 for x in A) for s in srcs)
selected = {}
for it in range(4):
    columns = [{i: 1} if i < v else {} for i in range(n)]; center = None; moved = 0; gain = 0.0
    for k in range(N):
        op, a, b, c, f, z = old[6*k:6*k+6]
        if op == 0: continue
        if op == 2: center = a; continue
        if op == 3: center = None; continue
        source = center if b == n else b; ca = columns[a]
        for s, x in columns[source].items():
            y = ca.get(s, 0) + c * x
            if y: ca[s] = y
            else: del ca[s]
        if k in in_copy: continue
        slots = gate_slots[k]; cur = gate_frame[k]
        cand = set()
        for reg, pos in slots:
            cand.update(chain[reg]); cand.add(initial[reg]); cand.add(final[reg])
        cand.discard(cur)
        base = sum(cost(prevf(r, p), cur) + cost(cur, nextf(r, p)) for r, p in slots)
        best = None
        for g in cand:
            if not all(C.sub(prevf(r, p), g) and C.sub(g, nextf(r, p)) for r, p in slots): continue
            d = sum(cost(prevf(r, p), g) + cost(g, nextf(r, p)) for r, p in slots) - base
            if d < -1e-9 and (best is None or d < best[0]): best = (d, g)
        if best is None: continue
        # verify span + nondegeneracy for candidates in improving order
        opts = sorted(((sum(cost(prevf(r, p), g) + cost(g, nextf(r, p)) for r, p in slots) - base, g) for g in cand
                       if all(C.sub(prevf(r, p), g) and C.sub(g, nextf(r, p)) for r, p in slots)), key=lambda t: (t[0], t[1]))
        need = set()
        if not (v <= a < 2*v): need.update(ca)
        if not (v <= b < 2*v) and b != n: need.update(columns[b])
        for d, g in opts:
            if d >= -1e-9: break
            if nondeg(g) and contains_span(g, need):
                for r, p in slots: chain[r][p] = g
                gate_frame[k] = g; moved += 1; gain += d
                if g == old[6*k+4]: selected.pop(k, None)
                else: selected[k] = g
                break
    print('pass', it, 'moved', moved, 'gain %.2f' % gain, 'selected', len(selected), '%.0fs' % (time.time() - t0), flush=True)
    if not moved: break
H1 = total(); L1 = sum(LN[d] * c for d, c in H1.items())
delta = Counter(H1); delta.subtract(H0); delta = {d: c for d, c in sorted(delta.items()) if c}
print('delta', delta, 'removed calls', sum(H0.values()) - sum(H1.values()), 'L %.1f -> %.1f' % (L0, L1), flush=True)
def sha_basis(B): return hashlib.sha256(json.dumps(B, separators=(',', ':')).encode()).hexdigest()
entries = []
for k in sorted(selected):
    op, a, b, c, f, z = old[6*k:6*k+6]; g = selected[k]
    entries.append(dict(record=k, scalar=[a, b, c, z], old_dimension=C.dimf[f], old_basis_sha256=sha_basis(C.B[f]),
                        new_basis=[list(map(int, row)) for row in C.B[g]], new_dimension=C.dimf[g]))
copies = Counter({W.h - 2: W.h})
sel = dict(status='FROZEN_CONCAVE_DESCENT_FRAME_SELECTION', input_raw_sha256=hashlib.sha256(old.tobytes()).hexdigest(),
           input_scalar_sha256=pr['physical']['scalar_projection_sha256'], source_record_count=N, selected_gate_count=len(entries),
           expected_local_histogram_delta={str(d): c for d, c in delta.items()}, expected_rank_mass=sum(d*c for d, c in (H1 + copies).items()),
           expected_removed_calls=sum(H0.values()) - sum(H1.values()), expected_scalar_additions=pr['physical']['weighted_scalar_events'],
           provenance="Re-derived on this word by gen5/descent_search.py (re-implementation of #287's stated rule): greedy local descent of sum r*ln(m/r), m = 5h over the parity-fused ADD word, each move reassigning one ADD gate to a frame already on one of its operands' chains; nested chains, fixed endpoints, exact integer operand source spans and nondegeneracy enforced. Rule by Rohan Arun (#287); re-derivation prepared with Anthropic Claude assistance.",
           entries=entries)
outp.write_text(json.dumps(sel, indent=1) + '\n')
if len(sys.argv) > 4 and sys.argv[3] == '--compare':
    fz = json.loads(Path(sys.argv[4]).read_text()); fr = {e['record']: e for e in fz['entries']}
    mine = {e['record']: e for e in entries}
    print('frozen', len(fr), 'mine', len(mine), 'common records', len(set(fr) & set(mine)), 'same new basis', sum(fr[r]['new_basis'] == mine[r]['new_basis'] for r in set(fr) & set(mine)))
    print('frozen delta', fz['expected_local_histogram_delta'], 'removed', fz['expected_removed_calls'])
