"""joint: joint triangle-hybrid candidates per copy pair (h = E_h + r after copy gate ic).
Each movable read m = (j, t, src, coef) of the pair is either kept, swapped (sw4 rule) or fused into a holder H that t
reads elsewhere (donation q*src into H right after H's last write before t's read of H; restore by end type: FULL
prepend if both ends are full, else an early tail before src's first tail write; optionally right after t's read).
Family: 1 <= |fused| <= max_fused, remaining reads all swapped or all kept (plus single swaps when allow_partial)."""
import collections, itertools, sys
from fractions import Fraction as Q
from harness import V
from fusion import index, data_reads, dyadic, any_in
from exchange import copy_pairs, movable_reads, prereads
def holder_options(w, I, reads_t, m, h, r, ic, restores=("canon",)):
    j, t, src, (a0, b0) = m; a = Q(a0, b0); out = []
    for (iH, H, cH) in reads_t:
        if iH == j or H in (h, r, t): continue
        q = a / cH
        if not dyadic(q): continue
        lo_t, hi_t = min(j, iH), max(j, iH)
        if any_in(I['RD'][t] + I['SC'][t], lo_t, hi_t + 1): continue
        lwH = max([x for x in I['W'][H] if x < iH], default=-1); p = lwH + 1
        if src == h: p = max(p, ic + 1)
        if p > iH: continue
        lo, hi = (p, j) if p <= j else (j + 1, p)
        if any_in(I['W'][src], lo, hi): continue
        nB = len(I['B']); rs = []
        if not any_in(I['W'][src], p, nB) and not any_in([x for x in I['RD'][H] + I['SC'][H] if x != iH], p, nB):
            if src not in I['low'] and H not in I['low'] and not I['TW'][src] and not I['TR'][H]: rs.append(("P", 0))
            else: rs.append(("T", min(I['TW'][src] + I['TR'][H] + [len(I['T'])])))
        if "after" in restores and not any_in(I['W'][src], p, iH + 1) and not any_in([x for x in I['RD'][H] + I['SC'][H] if x != iH], p, iH + 1): rs.append(("B", iH + 1))
        for kind, pos in rs:
            g = ['add', H, src, q.numerator, q.denominator, []]; gr = ['add', H, src, -q.numerator, q.denominator, []]
            ed = dict(delete=[j], insert=[(p, g)], tail=[], prepend=[])
            if kind == "B": ed['insert'].append((pos, gr))
            elif kind == "T": ed['tail'].append((pos, gr))
            else: ed['prepend'].append(gr)
            out.append((dict(H=H, iH=iH, p=p, rest=kind + str(pos)), ed))
    return out
def swap_edit(w, h, r, ic, m):
    j, t, src, (a, b) = m; pre = prereads(w, h, ic); by_t = {tt: (jj, c) for jj, (tt, c) in pre.items()}
    if src == h:
        if t not in by_t or by_t[t][1] != (-a, b): return None
        return dict(delete=[j, by_t[t][0]], insert=[(j, ['add', t, r, a, b, []])], tail=[], prepend=[])
    if t in by_t: return None
    ins = (max(pre) + 1) if pre else ic
    return dict(delete=[j], insert=[(j, ['add', t, h, a, b, []]), (ins, ['add', t, h, -a, b, []])], tail=[], prepend=[])
def merge(eds):
    out = dict(delete=[], insert=[], tail=[], prepend=[])
    for e in eds:
        for k in out: out[k] += e[k]
    if len(set(out['delete'])) != len(out['delete']): return None
    return out
def candidates(w, max_fused=2, allow_partial=False, restores=("canon",), pairs_only=None):
    I = index(w); reads = data_reads(w, I); out = []
    for h, (r, ic) in copy_pairs(w).items():
        if pairs_only is not None and h not in pairs_only: continue
        M = [(j, t, s, c) for (j, t, s, c) in movable_reads(w, h, r, ic)]
        if not M: continue
        opts = {m[0]: holder_options(w, I, reads[m[1]], m, h, r, ic, restores) for m in M}
        sw = {m[0]: swap_edit(w, h, r, ic, m) for m in M}
        for k in range(1, min(max_fused, len(M)) + 1):
            for Fset in itertools.combinations(M, k):
                rest = [m for m in M if m not in Fset]
                swap_choices = [()]
                if rest and all(sw[m[0]] is not None for m in rest): swap_choices.append(tuple(m[0] for m in rest))
                if allow_partial and len(rest) > 1: swap_choices += [(m[0],) for m in rest if sw[m[0]] is not None]
                for combo in itertools.product(*[opts[m[0]] for m in Fset]):
                    for sc in swap_choices:
                        ed = merge([e for _, e in combo] + [sw[x] for x in sc])
                        if ed is None: continue
                        out.append(dict(h=h, r=r, fused=[(m[0], m[1], m[2], c[0]['H'], c[0]['rest']) for m, c in zip(Fset, combo)], swapped=list(sc), ed=ed))
    return out
if __name__ == "__main__":
    # usage: python -B joint.py FULL-WORD.json.gz
    import harness as C
    w = C.load(sys.argv[1]); cs = candidates(w)
    print("joint candidates:", len(cs))
