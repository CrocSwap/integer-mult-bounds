"""fusion: read-fusion candidates (generalized U8 triangle-hybrid delivery).
A target t reads A (coef a, at iA) and H (coef h, at iH) in B.  Donate q*A into H (q = a/h) at p <= iH, delete t's read
of A, restore H -= q*A later (in B, in an early tail, or as a FULL-cleanup prepend).  Candidates satisfy the structural
preconditions (A unchanged between donation and its old read and until the restore; no other reader / scale of H in
the donation window); exactness is re-checked by the harness."""
import collections, sys
from fractions import Fraction as Q
from harness import regs, V
def dyadic(q): return q != 0 and (q.denominator & (q.denominator - 1)) == 0
def index(w):
    B = w['B']; W = collections.defaultdict(list); RD = collections.defaultdict(list); SC = collections.defaultdict(list)
    for i, e in enumerate(B):
        W[e[1]].append(i)
        if e[0] == 'scale': SC[e[1]].append(i)
        else: RD[e[2]].append(i)
    T = [w['cleanup'][i] for i, U in w['early_cleanup']]
    TW = collections.defaultdict(list); TR = collections.defaultdict(list)
    for j, e in enumerate(T):
        TW[e[1]].append(j)
        if e[0] == 'add': TR[e[2]].append(j)
    ent = set(map(int, w['start_extra'])); low = set(map(int, w['helper_final']))
    firstW = {r: min(v) for r, v in W.items()}
    return dict(B=B, W=W, RD=RD, SC=SC, T=T, TW=TW, TR=TR, ent=ent, low=low, firstW=firstW)
def data_reads(w, I):
    out = collections.defaultdict(list)
    for i, e in enumerate(I['B']):
        if e[0] == 'add' and V <= e[1] < 2 * V:
            s = e[2]
            if s in I['ent'] and (s not in I['firstW'] or i < I['firstW'][s]): continue     # entrance pre-read
            out[e[1]].append((i, s, Q(e[3], e[4])))
    return out
def any_in(lst, lo, hi): return any(lo <= x < hi for x in lst)
def candidates(w, I=None, targets=None):
    I = I or index(w); B = I['B']; nB = len(B); reads = data_reads(w, I); out = []
    for t, rs in reads.items():
        if targets is not None and t not in targets: continue
        for (iA, A, a) in rs:
            for (iH, H, h) in rs:
                if A == H or iA == iH or A == t or H == t: continue
                lo_t, hi_t = min(iA, iH), max(iA, iH)
                if any_in(I['RD'][t] + I['SC'][t], lo_t, hi_t + 1): continue          # t is read/scaled while its delivered content differs
                q = a / h
                if not dyadic(q): continue
                lwH = max([x for x in I['W'][H] if x < iH], default=-1)
                ps = sorted({iH, lwH + 1} | ({iA + 1} if iA < iH else set()))
                for p in ps:
                    if p > iH or p < 0: continue
                    lo, hi = (p, iA) if p <= iA else (iA + 1, p)
                    if any_in(I['W'][A], lo, hi): continue                     # A must hold the value t read
                    rests = []
                    nxtH = min([x for x in I['RD'][H] + I['SC'][H] if x > iH], default=nB)
                    # R1: right after t's read of H; R2: just before H's next read/scale (both inside B)
                    for rpos, tag in ((iH + 1, "B-after"), (nxtH, "B-before-next")):
                        if rpos > nB: continue
                        if any_in(I['W'][A], p, rpos): continue
                        if any_in([x for x in I['RD'][H] + I['SC'][H] if x != iH], p, rpos): continue
                        if rpos == nB and tag == "B-before-next": continue
                        rests.append(("B", rpos, tag))
                    # tails / prepend need A unchanged to the end of B and H untouched by readers after iH
                    if not any_in(I['W'][A], p, nB) and not any_in([x for x in I['RD'][H] + I['SC'][H] if x != iH], p, nB):
                        jmax = min(I['TW'][A] + I['TR'][H] + [len(I['T'])])
                        for j in sorted({0, jmax}): rests.append(("T", j, "tail@%d" % j))
                        if A not in I['low'] and H not in I['low'] and not I['TW'][A] and not I['TR'][H]: rests.append(("P", 0, "prepend"))
                    for kind, pos, tag in rests:
                        g = ['add', H, A, q.numerator, q.denominator, []]; gr = ['add', H, A, -q.numerator, q.denominator, []]
                        ed = dict(delete=[iA], insert=[(p, g)], tail=[], prepend=[])
                        if kind == "B": ed['insert'].append((pos, gr))
                        elif kind == "T": ed['tail'].append((pos, gr))
                        else: ed['prepend'].append(gr)
                        out.append(dict(t=t, A=A, H=H, iA=iA, iH=iH, p=p, rest=tag, ed=ed))
    return out
if __name__ == "__main__":
    # usage: python -B fusion.py FULL-WORD.json.gz
    import harness as C
    w = C.load(sys.argv[1]); cs = candidates(w)
    print("fusion candidates:", len(cs))
