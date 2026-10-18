"""lbforced.py WORD -- frame lower bound for ANY exact restore-only rewrite of the word (auditor semantics, A/B/warps/cut/
endpoints fixed). Every restored helper c ends with its own input, a FIXED combination M[c][.] of the (independent) restore-
entry rows; so for every register r with M[c][r] != 0 the content of r must reach c along gates with nested frames inside E_c,
and r's restore-entry frame is inside E_c. LB = certified optimum of the word with an EMPTY restore and the caps
cap[r] = intersection of E_c over those c (applied from r's last pre-restore vertex to its end climb; toolkit BorrowGraph caps).
Any exact rewrite R satisfies the caps, and merging its restore-phase jumps of every register into one end climb never costs
more (c_{a+b} <= c_a + c_b), so cost(R) >= LB. If LB == cost(current word), the current restore is optimal in the whole class."""
import sys
sys.path.insert(0, '/private/tmp/claude-501/-Users-mdumitrean-Desktop-dev-aigent-math-prime/c80ebb8e-fc28-4d1d-b7ef-b214d4660f98/scratchpad/r15/agents/K/code')
from screen4 import *
def lb_forced(w, extra_caps=None, M=None):
    if M is None: M = restore_map(w)
    E = end_frames(w); Rs = restored_set(w)
    capf = {}
    for c in Rs:
        for r, x in M[c].items():
            if r == c or not x: continue
            capf.setdefault(r, set(span(FULL)))
            capf[r] &= set(span(E[c]))
    if extra_caps:
        for r, U in extra_caps.items():
            capf.setdefault(r, set(span(FULL))); capf[r] &= set(span(U))
    w0 = dict(w); w0['restore'] = []
    w2, meta = bp.build_problem(w0)
    al = aliases(w0, meta)
    caps = {al[r][-1]: tuple(basis(tuple(U))) for r, U in capf.items()}
    g = bp.BorrowGraph(w2, meta['eq_end'], check_literal=False, tail_mutable=True, caps=caps, cut_equality=True)
    res = bp.F.optimal_frames(w2, bp.costs(), check_literal=False, graph=g)
    cd = bp.centre_descents(w0); prof = collections.Counter(res['profile']); prof.update(cd)
    return dict(cost=res['cost'] + bp.costs().profile_cost(cd), certified=res['certified'], profile=dict(sorted(prof.items())),
                ncaps=len(caps), assign=res['assign'], graph=g, meta=meta, w0=w0)
if __name__ == '__main__':
    w = W(sys.argv[1]); cur = solve(w)
    lb = lb_forced(w)
    print('current', cur['cost'], cur['profile'])
    print('LB_forced', lb['cost'], lb['certified'], lb['profile'], 'caps', lb['ncaps'])
    print('gap (max possible gain of any exact restore-only rewrite)', cur['cost'] - lb['cost'])
