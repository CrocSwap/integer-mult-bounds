# Abstraction: LCA K (size m), phi_beta child prefix with incoming entries per Lemma-1 case table,
# deeper scratch = independent fresh symbols. Exact free algebra per symbol. Returns max mass.
import sys
from census import word

def run_prefix(k, sign, src_entry, dst_entry, R):
    """Child call of size k (registers x=0 src, y=1 dst, scratch 2..R-1), entries dict reg->poly."""
    w = word(k, sign)
    col = {}
    if src_entry: col[0] = dict(src_entry)
    if dst_entry: col[1] = dict(dst_entry)
    for r in range(2, R): col[r] = {(('D', r),): 1}
    pk = max([sum(abs(c) for c in v.values()) for v in col.values()] + [0])
    for x, y, j, s in w:
        cx = col.get(x)
        if not cx: continue
        cy = col.setdefault(y, {})
        for m, c in cx.items():
            kk = (j,) + m; v = cy.get(kk, 0) + s * c
            if v: cy[kk] = v
            else: del cy[kk]
        pk = max(pk, sum(abs(c) for c in cy.values()))
    return pk

def Q(m):
    if m == 1: return 1
    B, A = m // 2, m - m // 2
    R = max((A - 1).bit_length(), 1) + 3
    X = {(('X',),): 1}
    Y = {(('Y',),): 1}
    AX = {tuple(range(A - 1, -1, -1)) + (('X',),): 1}   # parent A-product times X (child V' factors 0..A-1)
    cases = [  # (child size, child sign, src, dst)
        (A, 1, X, None),     # +: U->V
        (B, -1, None, Y),    # +: U->U'
        (A, -1, X, AX),      # +: U->V' (related)
        (B, -1, None, None), # +: V->U' / -: V->U' / V'->U'
        (A, -1, None, Y),    # +: V->V' ; -: V->V'
        (A, -1, X, None),    # +: U'->V' ; -: U->V'
        (B, 1, None, None),  # -: V->U
    ]
    return max(1, max(run_prefix(k, s, a, b, R) for k, s, a, b in cases))

if __name__ == '__main__':
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    best = 1
    for m in range(1, hi + 1):
        q = Q(m); best = max(best, q)
        if m >= lo: print(m, 'Q', q, 'cummax', best, 'floorlog2', max(1, m.bit_length() - 1), flush=True)
