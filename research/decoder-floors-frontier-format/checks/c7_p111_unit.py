"""The P111 bit unit of PR #589's word (data/p111_lines.json): 111 of the 120 lines of the E8 line system in the doubled Hamming coordinates of that word.
Standard library only.  The rigidity SAT instances for it are replayed in c1 (P111_*); the 'at most 12 retained totals cost >= 63' statement is RECORDED, not checked here."""
import sys, os, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from report import check, finish
from roots import rank_f2, rank_q, maximal_cliques, popcount

L = json.load(open(os.path.join(HERE, '..', 'data', 'p111_lines.json')))['lines']
ip = lambda x, y: sum(a * b for a, b in zip(x, y))
canon = lambda v: tuple(v) if next(x for x in v if x) > 0 else tuple(-x for x in v)
check('c7.count', len(L) == 111 and len(set(canon(v) for v in L)) == 111, '111 distinct lines')
check('c7.norm', all(ip(v, v) == 4 for v in L), 'every line has squared norm 4 (so ip // 2 is the Gram entry 2 on the diagonal)')
check('c7.gram', all(ip(a, b) in (0, 2, -2) for a, b in itertools.combinations(L, 2)), 'distinct lines have inner product 0 or +-2, i.e. Gram entry 0 or +-1: the lines are roots of a root system (a sub-configuration of E8)')
# the 120-line completion of core.py: 8 axes (2 e_i) and, for each 4-support occurring among the live weight-4 lines, all sign patterns with the first entry +1
sup4 = sorted({tuple(i for i, x in enumerate(v) if x) for v in L if sum(1 for x in v if x) == 4})
full = {tuple(2 if k == i else 0 for k in range(8)) for i in range(8)}
for s in sup4:
    for signs in itertools.product((1, -1), repeat=3):
        v = [0] * 8; v[s[0]] = 1
        for k, j in enumerate(s[1:]): v[j] = signs[k]
        full.add(tuple(v))
full = sorted(full); live = set(canon(v) for v in L)
check('c7.e8', len(sup4) == 14 and len(full) == 120 and live <= set(canon(v) for v in full) and all(ip(a, b) in (0, 2, -2, 4) for a, b in itertools.combinations(full, 2)), 'the live lines lie in a 120-line root-line system (8 axes + 14 four-supports x 8 sign patterns): P111 = that system minus 9 lines')
check('c7.rankQ', rank_q([list(v) for v in L]) == 8, 'the 111 lines span Q^8')
orthmask = [sum(1 << s for s in range(111) if s != t and ip(L[t], L[s]) == 0) for t in range(111)]
Br = [sum(1 << s for s in range(111) if s == t or ip(L[t], L[s]) == 0) for t in range(111)]
check('c7.rankF2', rank_f2(Br) == 9, 'the dense pairing B_d = J + Abar of P111 has F2-rank 9 (so h = 9 is the minimal fitting rank when B_d is forced, Theorem R)')
w = max(popcount(c) for c in maximal_cliques(orthmask))
check('c7.frame', w == 8, 'P111 contains an orthogonal 8-frame (alpha_perp = 8, so every realisation has rank >= 8)')
finish()
