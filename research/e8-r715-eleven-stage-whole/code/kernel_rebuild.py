"""Shared-donor kernel for a new bit word (PR #417/#443 kernel, PR #443's replica_kernel with 32 replicas, unchanged), with a
deterministic selection search, plus PR #436's retiming before and after.  Entry = pivot p, entrance E (a coordinate
subspace spanned by frame lines inside p's first frame, so that #443's residual isometries are coordinate permutations),
donors D with resp(p) = XOR resp(D) over F2 (found by elimination among eligible helpers).  Every result is checked by
PR #443's exact replay (legality, F2 on all columns, source spans) and its interface check.
usage: kernel_rebuild.py REPO_RESEARCH_DIR WORD_IN OUT_WORD OUT_SELECTION OUT_ISOMETRIES
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code (search and isometry emission); the kernel,
replay and retiming code are the cited upstream modules, unchanged.  Apache-2.0."""
import os, sys, json, copy
os.environ['E8COORD'] = 'ham'
R, src, out, out_sel, out_iso = sys.argv[1:6]
P443 = os.path.join(R, 'e8-r740-replica32')
sys.path[:0] = [P443 + '/code', P443 + '/parent436/code/bit/producer', P443 + '/parent436/code/reuse']
from e8core import load_word, save_word, replay, Lat, to_masks
from stages import content_sha, occurrences
from replica_kernel import kernel
from iface386 import check
import retime as RT
w = load_word(src)
prim = copy.deepcopy(w)
for ph in ('D', 'A', 'B', 'C'): prim[ph] = [[f, d, [s]] for f, d, ss in w[ph] for s in ss]
ret, mv1 = RT.retime(prim, sweeps=6, M=64)
L = Lat(ret['lines']); masks = to_masks(ret, L); v = ret['v']; n = 2 * v + ret['R']
occ = occurrences(ret, masks)
gm = {(ph, k): masks[g[0]] for ph in ('D', 'A', 'B', 'C') for k, g in enumerate(ret[ph])}
first = {h: next(x if kind == 'p' else gm[x] for kind, x in occ[h][1:] if (x if kind == 'p' else gm[x]) != 0) for h in range(2 * v, n)}
resp = {h: 0 for h in range(2 * v, n)}
for f, t, ss in ret['D']:
    for s in ss: resp[s] ^= 1 << (t - v)
retset = set(ret['ret']); H = [h for h in range(2 * v, n) if h not in retset]
dim = lambda m: L.dim(m) if m else 0
FRAMEL = [i for i in range(v) if sum(1 for x in ret['lines'][i] if x) == 1]; assert len(FRAMEL) == 8
piv, donor_at, sel = {}, {}, []
def solve(p, E):
    elig = sorted((h for h in H if h != p and h not in piv and (E & ~first[h]) == 0 and donor_at.get(h, E) == E),
                  key=lambda h: (0 if donor_at.get(h) == E else 1, h))
    basis = []
    for h in elig:
        y, cm = resp[h], {h}
        for bv, bs in basis:
            if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm = cm ^ bs
        if y: basis.append((y, cm)); basis.sort(key=lambda z: -z[0])
    y, cm = resp[p], set()
    for bv, bs in basis:
        if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm = cm ^ bs
    return sorted(cm) if y == 0 else None
for p in sorted(H, key=lambda h: (-dim(first[h]), h)):
    if p in piv or p in donor_at: continue
    fl = [i for i in FRAMEL if first[p] >> i & 1]
    if not fl: continue
    Efull = L.close(sum(1 << i for i in fl))
    for E in [Efull] + ([1 << i for i in fl] if len(fl) > 1 else []):
        D = solve(p, E)
        if D is None or p in D: continue
        piv[p] = E
        for d in D: donor_at[d] = E
        sel.append([[i for i in range(v) if E >> i & 1], p, D]); break
tot = sum(len(e[0]) for e in sel)
if (8 * ret['R'] - tot) % 2:
    sel.pop(max(i for i, e in enumerate(sel) if len(e[0]) == 1))
kw, ent, rank, don = kernel(ret, sel, 32)
kw, mv2 = RT.retime(kw, sweeps=6, M=64)
a = replay(kw, span_mode='z'); assert not a['viol'], a['viol'][:5]
itf = check(kw, 192); assert itf['prefix_ok']
Lk = Lat(kw['lines']); mk = to_masks(kw, Lk)
iso = []
for f in sorted(set(kw['start'][2 * v:])):
    m = mk[f]; eb = [i for i in FRAMEL if m >> i & 1]; rb = [i for i in FRAMEL if not m >> i & 1]
    assert (Lk.close(sum(1 << i for i in eb)) == m) if eb else m == 0, ('entrance not a coordinate subspace', f)
    mat = [list(kw['lines'][i]) for i in eb + rb]; red = [[x // 2 for x in r] for r in mat]; ops = []
    for i in range(8):
        j = next(j for j in range(i, 8) if red[j][i] != 0)
        if j != i: red[i], red[j] = red[j], red[i]; ops.append(['swap', i, j, None])
    iso.append(dict(frame=f, entrance_rank=len(eb), denominator=2, entrance_basis=eb, residual_basis=rb, orthogonal_rows_numerator=mat, gaussian_reduction=ops))
save_word(kw, out)
json.dump(dict(input_sha256=content_sha(w), retimed_sha256=content_sha(ret), output_sha256=content_sha(kw), entries=sel), open(out_sel, 'w'))
json.dump(iso, open(out_iso, 'w'))
print(json.dumps(dict(status='PASS_KERNEL_REBUILD', pre_retime_moves=mv1, post_retime_moves=mv2, entries=ent, entrance_rank=rank,
                      donor_slots=don, replicas=32, output_sha256=content_sha(kw), interface_prefix_ok=itf['prefix_ok'])))
