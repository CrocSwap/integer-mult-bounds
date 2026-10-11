"""Kernel-pivot geometry of the R715 bit word: which helpers may become pivots, what the shared-donor kernel can reach, and exact checks.

A kernel pivot p (PR #417/#443 shared-donor kernel) enters at a nonzero frame E (a coordinate subspace of the 8 frame lines inside p's first
frame), its delivery vector resp(p) in F2^120 (the targets it feeds in the D phase) is dropped and re-created by donors D with
resp(p) = XOR resp(D), every donor in the same entrance class.  The paid residual of a helper has width 8 - rank(entrance), so the number
of narrow residuals is the number of pivots.  This module recomputes, from a bit word and the pinned upstream packages only,
  * the candidate carriers (helpers whose first frame contains a frame line), their response vectors and ranks,
  * the exact selection checker (the same conditions PR #443's kernel() asserts, plus the response relation over F2),
  * the proved pivot ceiling |C| - rank(resp(C)) and the per-class tables.
usage: kernel_cap.py REPO_RESEARCH_DIR WORD_IN OUT.json   (analysis); import for the other scripts.
Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.  Apache-2.0."""
import os, sys, json, copy
os.environ['E8COORD'] = 'ham'

def setup(R):
    """put PR #443's modules on the path; returns a namespace of the upstream functions used"""
    P443 = os.path.join(R, 'e8-r740-replica32')
    sys.path[:0] = [P443 + '/code', P443 + '/parent436/code/bit/producer', P443 + '/parent436/code/reuse']
    from e8core import load_word, save_word, replay, Lat, to_masks
    from stages import content_sha, occurrences
    from replica_kernel import kernel
    from iface386 import check
    import retime as RT
    class U: pass
    u = U(); u.load_word, u.save_word, u.replay, u.Lat, u.to_masks = load_word, save_word, replay, Lat, to_masks
    u.content_sha, u.occurrences, u.kernel, u.check, u.RT = content_sha, occurrences, kernel, check, RT
    return u

def primitive_retimed(U, word_path):
    """PR #436's retiming of the word with every gate split to one source (exactly what kernel_rebuild.py starts from)"""
    w = U.load_word(word_path)
    prim = copy.deepcopy(w)
    for ph in ('D', 'A', 'B', 'C'): prim[ph] = [[f, d, [s]] for f, d, ss in w[ph] for s in ss]
    ret, mv = U.RT.retime(prim, sweeps=6, M=64)
    return w, ret, mv

class Geo:
    """first frames, response vectors, helper list of a (pre-kernel, retimed) word"""
    def __init__(self, U, ret):
        self.U, self.ret = U, ret
        v = self.v = ret['v']; n = self.n = 2 * v + ret['R']
        self.L = L = U.Lat(ret['lines']); self.masks = masks = U.to_masks(ret, L)
        occ = U.occurrences(ret, masks)
        gm = {(ph, k): masks[g[0]] for ph in ('D', 'A', 'B', 'C') for k, g in enumerate(ret[ph])}
        self.first = {h: next(x if kind == 'p' else gm[x] for kind, x in occ[h][1:] if (x if kind == 'p' else gm[x]) != 0) for h in range(2 * v, n)}
        self.resp = {h: 0 for h in range(2 * v, n)}
        for f, t, ss in ret['D']:
            for s in ss: self.resp[s] ^= 1 << (t - v)
        retset = set(ret['ret']); self.H = [h for h in range(2 * v, n) if h not in retset]
        self.FRAMEL = [i for i in range(v) if sum(1 for x in ret['lines'][i] if x) == 1]
        assert len(self.FRAMEL) == 8
        self.axes = {h: [i for i in self.FRAMEL if self.first[h] >> i & 1] for h in self.H}
        self.C = [h for h in self.H if self.axes[h]]            # candidate carriers
    def dim(self, m): return self.L.dim(m) if m else 0

def rank_f2(vectors):
    basis = []
    for y in vectors:
        for b in basis: y = min(y, y ^ b)
        if y: basis.append(y)
    return len(basis)

def check_selection(G, sel, replicas=32):
    """exact conditions of PR #443's kernel() plus the F2 response relation; returns dict(entries, entrance_rank, donors, classes)"""
    L, resp, first = G.L, G.resp, G.first; ret = set(G.ret['ret'])
    piv, donor_at, tot = {}, {}, 0
    for E_lines, p, D in sel:
        E = L.close(sum(1 << i for i in E_lines)); assert E == sum(1 << i for i in E_lines) and E != 0
        assert L.close(sum(1 << i for i in G.FRAMEL if E >> i & 1)) == E, 'entrance must be a coordinate subspace (spanned by frame lines)'
        assert p in set(G.H) and p not in piv and p not in donor_at
        x = resp[p]
        for d in D:
            assert d in set(G.H) and d not in piv and d != p and donor_at.setdefault(d, E) == E, 'a donor serves one entrance'
            x ^= resp[d]
        assert x == 0, ('response relation fails', p)
        for h in [p] + list(D): assert E & ~first[h] == 0, ('entrance not inside first frame', h)
        piv[p] = E; tot += L.dim(E)
    assert not set(piv) & set(donor_at)
    assert replicas % 8 == 0 and replicas * (8 * G.ret['R'] - tot) % 64 == 0, 'residual coordinates must fill whole banks'
    return dict(entries=len(sel), entrance_rank=tot, donors=len(donor_at), pivots_by_entrance_rank={str(k): sum(1 for E in piv.values() if L.dim(E) == k) for k in sorted({L.dim(E) for E in piv.values()})})

def matroid_components(G):
    """connected components of the linear matroid of delivery vectors over the candidates (fundamental-circuit graph); sizes, largest first"""
    C, resp = G.C, G.resp; idx = {h: k for k, h in enumerate(C)}; basis = []; par = {h: h for h in C}
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    for h in C:
        y, cm = resp[h], 1 << idx[h]
        for bv, bs in basis:
            if y >> (bv.bit_length() - 1) & 1: y ^= bv; cm ^= bs
        if y: basis.append((y, cm)); basis.sort(key=lambda z: -z[0])
        else:
            for k in range(len(C)):
                if cm >> k & 1: par[find(C[k])] = find(h)
    sizes = {}
    for h in C: sizes[find(h)] = sizes.get(find(h), 0) + 1
    return sorted(sizes.values(), reverse=True)

def analysis(G):
    """all quantities of README section 'The pivot ceiling'"""
    C, resp, axes = G.C, G.resp, G.axes
    S = {i: [h for h in C if i in axes[h]] for i in G.FRAMEL}
    rkC = rank_f2([resp[h] for h in C])
    # a candidate can be a pivot only if resp(h) lies in the span of the other members of one of its classes
    pivot_ok = [h for h in C if any(rank_f2([resp[x] for x in S[i] if x != h] + [resp[h]]) == rank_f2([resp[x] for x in S[i] if x != h]) for i in axes[h])]
    return dict(helpers=len(G.H), candidates=len(C), response_rank_of_candidates=rkC, proved_ceiling=len(C) - rkC,
                axis_class_size={str(i): len(S[i]) for i in G.FRAMEL}, axis_class_rank={str(i): rank_f2([resp[h] for h in S[i]]) for i in G.FRAMEL},
                axis_class_nullity={str(i): len(S[i]) - rank_f2([resp[h] for h in S[i]]) for i in G.FRAMEL},
                candidates_that_can_be_pivots=len(pivot_ok), matroid_components=matroid_components(G), candidates_in_k_classes={str(k): sum(1 for h in C if len(axes[h]) == k) for k in sorted({len(axes[h]) for h in C})},
                first_frame_dim={str(k): sum(1 for h in G.H if G.dim(G.first[h]) == k) for k in sorted({G.dim(G.first[h]) for h in G.H})})

def controls(G, sel):
    """mutants of a valid selection that check_selection must reject; returns their names (raises if one is accepted)"""
    import copy
    names = []
    def must_reject(name, bad):
        try: check_selection(G, bad)
        except AssertionError: names.append(name); return
        raise AssertionError(('mutant accepted', name))
    i0 = next(i for i, e in enumerate(sel) if len(e[2]) >= 2)
    m = copy.deepcopy(sel); m[i0][2] = m[i0][2][1:]; must_reject('donor dropped (response relation fails)', m)
    m = copy.deepcopy(sel); m[i0][2] = m[i0][2][:-1] + [m[i0][1]]; must_reject('pivot used as its own donor', m)
    m = copy.deepcopy(sel); m[0][2] = m[0][2] + [m[1][1]]; must_reject('another pivot used as a donor', m)
    j = next(k for k, e in enumerate(sel) if G.axes[e[1]] != [e[0][0]] and len(G.axes[e[1]]) > 1 and e[0][0] in G.axes[e[1]])
    other = [a for a in G.axes[sel[j][1]] if a != sel[j][0][0]][0]
    m = copy.deepcopy(sel); m[j][0] = [other]; must_reject('entrance moved to another frame line (donors outside it)', m)
    m = copy.deepcopy(sel)[:-1]; must_reject('odd entrance-rank total (32-replica bank equation)', m)
    m = copy.deepcopy(sel); m[0][0] = [next(i for i in range(G.v) if i not in G.FRAMEL)]; must_reject('entrance that is not spanned by frame lines', m)
    return names

def build_kernel(U, ret, sel, replicas=32):
    """PR #443's replica kernel (unchanged) on the retimed word, PR #436's retiming after it, exact replay and interface check,
    and the residual isometries of the entrance frames (coordinate subspaces, as in kernel_rebuild.py).  Returns (word, isometries, info)."""
    kw, ent, rank, don = U.kernel(ret, sel, replicas)
    kw, mv2 = U.RT.retime(kw, sweeps=6, M=64)
    a = U.replay(kw, span_mode='z'); assert not a['viol'], a['viol'][:5]
    itf = U.check(kw, 192); assert itf['prefix_ok']
    v = kw['v']; Lk = U.Lat(kw['lines']); mk = U.to_masks(kw, Lk)
    FR = [i for i in range(v) if sum(1 for x in kw['lines'][i] if x) == 1]; iso = []
    for f in sorted(set(kw['start'][2 * v:])):
        m = mk[f]; eb = [i for i in FR if m >> i & 1]; rb = [i for i in FR if not m >> i & 1]
        assert (Lk.close(sum(1 << i for i in eb)) == m) if eb else m == 0, ('entrance not a coordinate subspace', f)
        mat = [list(kw['lines'][i]) for i in eb + rb]; red = [[x // 2 for x in r] for r in mat]; ops = []
        for i in range(8):
            j = next(j for j in range(i, 8) if red[j][i] != 0)
            if j != i: red[i], red[j] = red[j], red[i]; ops.append(['swap', i, j, None])
        iso.append(dict(frame=f, entrance_rank=len(eb), denominator=2, entrance_basis=eb, residual_basis=rb, orthogonal_rows_numerator=mat, gaussian_reduction=ops))
    info = dict(status='PASS_KERNEL_BUILD', entries=ent, entrance_rank=rank, donor_slots=don, replicas=replicas, post_retime_moves=mv2, interface_prefix_ok=itf['prefix_ok'])
    return kw, iso, info

def widths_of(U, kw):
    """width of every helper register = 8 - dim(start frame); the start frame is the entrance of a kernel pivot and the zero frame otherwise"""
    v = kw['v']; L = U.Lat(kw['lines']); masks = U.to_masks(kw, L)
    return [8 - (L.dim(masks[kw['start'][r]]) if masks[kw['start'][r]] else 0) for r in range(2 * v, 2 * v + kw['R'])]

def width_rule_check(U, kw, sel):
    """exact width rule on a kernel word: width_h = 8 - entrance rank for every helper; width_h < 8 exactly for the selected pivots, with the
    selected entrance rank; helpers outside the selection keep the zero start frame (width 8)"""
    v = kw['v']; wd = widths_of(U, kw); L = U.Lat(kw['lines']); piv = {p: L.dim(sum(1 << i for i in E)) for E, p, D in sel}
    assert len(wd) == kw['R']
    for r, w in enumerate(wd):
        h = 2 * v + r
        assert w == 8 - piv.get(h, 0), ('width rule fails', h, w)
        assert (w < 8) == (h in piv)
    hist = {}
    for w in wd: hist[w] = hist.get(w, 0) + 1
    return {str(k): hist[k] for k in sorted(hist)}

if __name__ == '__main__':
    R, wp, out = sys.argv[1:4]
    U = setup(R); w, ret, mv = primitive_retimed(U, wp); G = Geo(U, ret)
    a = analysis(G); a['pre_kernel_retime_moves'] = mv
    json.dump(a, open(out, 'w'), indent=1, sort_keys=True); print(json.dumps(a, sort_keys=True))
