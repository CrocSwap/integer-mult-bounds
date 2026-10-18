"""Registry of all SAT instances of the package: name -> (expected status, builder).  Standard library only.
Every builder is deterministic, so the DIMACS text (hence its sha256) is reproducible.  Status strings: UNSAT (proof: DRAT) or SAT (model)."""
import os, sys, json, itertools
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from satgen import *
from dirs import *

DATA = os.path.join(HERE, '..', 'data')
def _p104():
    D = json.load(open(os.path.join(DATA, 'p104_frames.json'))); return D['F0'], D['F1'], D['pairs']

def nb_lines(L, x, live=None):
    live = list(range(len(L))) if live is None else live
    return [t for t in live if dot(L[t], L[x]) != 0]

def _clique(L, R, A, r):
    D = sorted(set(R) & set(A)); nog = nonorth_graph(L)
    return clique_in(nog, sum(1 << t for t in D))

def block_instance(L, R, A, r):
    """fitting minrank <= r of the block B[R, A] (symmetry breaking on a maximum non-orthogonal clique of R cap A)"""
    C = _clique(L, R, A, r)
    return fitting_cnf(L, R, A, r, C)

def e6_cliques5():
    nog = nonorth_graph(UNITS['E6'][0])
    return sorted(c for c in maximal_cliques(nog) if popcount(c) == 5)

def all_instances():
    """returns an ordered dict name -> dict(expect=..., build=callable -> CNF, tag=..., note=...)"""
    I = {}
    def add(name, expect, tag, note, build): I[name] = dict(expect=expect, tag=tag, note=note, build=build)
    # ---- (1) E6 global fitting minrank: B = U V^T of rank <= r on all 36 lines, B_tt = 1, B_ts = 0 on non-orthogonal pairs
    L6 = UNITS['E6'][0]; v6 = 36; allv = list(range(v6)); cl5 = e6_cliques5(); picks = [0, len(cl5) // 2, len(cl5) - 1]
    for k, ci in enumerate(picks):
        C = bits(cl5[ci])
        for r, ex in ((5, 'UNSAT'), (6, 'UNSAT')):
            add('e6glob_r%d_c%d' % (r, k), ex, 'glob', 'E6 global fitting minrank <= %d, symmetry-breaking clique #%d of the 5-cliques %s' % (r, ci, C),
                (lambda r=r, C=C: fitting_cnf(L6, allv, allv, r, C, fixV=(r == 5))))
    C0 = bits(cl5[picks[0]])
    add('e6glob_r7_c0', 'SAT', 'glob', 'E6 global fitting minrank <= 7 (exists)', lambda: fitting_cnf(L6, allv, allv, 7, C0))
    # ---- (2) char-2 shadow minranks of Gamma (non-orthogonality graph): N_tt = 1, N_ts = 0 on orthogonal pairs
    for unit, r, ex in (('E6', 6, 'UNSAT'), ('E7', 7, 'UNSAT')):
        Lg = UNITS[unit][0]; og = orth_graph(Lg)
        cls = sorted(maximal_cliques(og), key=lambda c: (-popcount(c), c))
        for k, c in enumerate([cls[0], cls[len(cls) // 2]]):
            C = bits(c)
            add('gamma_%s_r%d_c%d' % (unit, r, k), ex, 'gamma', '%s: F2-minrank of matrices with unit diagonal and zeros on orthogonal pairs <= %d' % (unit, r),
                (lambda Lg=Lg, r=r, C=C: gamma_cnf(Lg, r, C)))
    # ---- (3) E8 root blocks: fitting minrank of B[R_a, R_b]
    L8 = UNITS['E8'][0]; G8 = gram(L8)
    a = 0; nbr = next(t for t in range(120) if G8[a][t] != 0 and t != a); orr = next(t for t in range(120) if G8[a][t] == 0 and t != a)
    Ra = nb_lines(L8, a)
    add('e8blk_aa_r8', 'UNSAT', 'block', 'E8: fitting minrank of B[R_a, R_a] <= 8', lambda: block_instance(L8, Ra, Ra, 8))
    add('e8blk_anb_r8', 'UNSAT', 'block', 'E8: fitting minrank of B[R_a, R_b] <= 8, a, b non-orthogonal', lambda: block_instance(L8, Ra, nb_lines(L8, nbr), 8))
    add('e8blk_aor_r8', 'SAT', 'block', 'E8: fitting minrank of B[R_a, R_b] <= 8, a, b orthogonal (exists)', lambda: block_instance(L8, Ra, nb_lines(L8, orr), 8))
    # ---- (4) known optimal decoders: every term has fitting minrank = dense rank (UNSAT at dense - 1)
    F0, F1, pairs = _p104(); Br8 = b0rows(L8)
    live112 = [t for t in range(120) if t not in set(F0)]; live104 = [t for t in live112 if t not in set(F1)]
    def sub(live): return [L8[t] for t in live]
    def term_sets(live, x, y):
        Lsub = sub(live); idx = {t: i for i, t in enumerate(live)}
        R = [idx[t] for t in live if dot(L8[t], L8[x]) != 0]; A = [idx[t] for t in live if dot(L8[t], L8[y]) != 0]
        return Lsub, R, A
    def dense_rank(Lsub, R, A): return blk(b0rows(Lsub), R, A)
    # E8 frame normals (8 terms, dense 9) -- all lines of E8 are equivalent under W(E8); the 8 terms are nevertheless all included
    for i, x in enumerate(F0):
        Ls, R, A = term_sets(list(range(120)), x, x)
        add('rob_E8frame_%d' % i, 'UNSAT', 'robust', 'E8 frame-normal decoder, term %d: fitting minrank of B[R,R] <= 8 (dense rank 9)' % i, (lambda Ls=Ls, R=R, A=A: block_instance(Ls, R, A, 8)))
    # E8 standard-coordinate decoder: terms x_j = y_j = e_j, R = lines with nonzero coordinate j (78 lines)
    for j in (0, 7):
        Rj = [t for t in range(120) if L8[t][j] != 0]
        add('rob_E8coord_%d' % j, 'UNSAT', 'robust', 'E8 coordinate decoder, term %d (|R| = %d): fitting minrank <= 8 (dense 9)' % (j, len(Rj)), (lambda Rj=Rj: block_instance(L8, Rj, Rj, 8)))
    # E7 frame decoder (7 terms, dense 7)
    L7 = UNITS['E7'][0]; fr7 = bits(next(c for c in maximal_cliques(orth_graph(L7)) if popcount(c) == 7))
    for i, x in enumerate(fr7):
        R = nb_lines(L7, x)
        add('rob_E7frame_%d' % i, 'UNSAT', 'robust', 'E7 frame-normal decoder, term %d: fitting minrank of B[R,R] <= 6 (dense 7)' % i, (lambda R=R: block_instance(L7, R, R, 6)))
    # P112 removed-frame decoder (8 terms, dense 8)
    for i, x in enumerate(F0):
        Ls, R, A = term_sets(live112, x, x)
        add('rob_P112_%d' % i, 'UNSAT', 'robust', 'P112 removed-frame decoder, term %d: fitting minrank <= 7 (dense 8)' % i, (lambda Ls=Ls, R=R, A=A: block_instance(Ls, R, A, 7)))
    # P104 frame-pair decoder (8 terms, dense 7)
    for i, (x, y) in enumerate(pairs):
        Ls, R, A = term_sets(live104, x, y)
        add('rob_P104_%d' % i, 'UNSAT', 'robust', 'P104 frame-pair decoder, term %d: fitting minrank <= 6 (dense 7)' % i, (lambda Ls=Ls, R=R, A=A: block_instance(Ls, R, A, 6)))
    # ---- controls: at the dense rank the same blocks ARE feasible (the dense B itself is a solution)
    Ls, R, A = term_sets(list(range(120)), F0[0], F0[0])
    add('ctrl_E8frame_r9', 'SAT', 'control', 'control: E8 frame-normal block at its dense rank 9 is feasible', lambda: block_instance(Ls, R, A, 9))
    Ls, R, A = term_sets(live104, *pairs[0])
    add('ctrl_P104_r7', 'SAT', 'control', 'control: P104 frame-pair block at its dense rank 7 is feasible', lambda: block_instance(Ls, R, A, 7))
    Ra7 = nb_lines(L7, fr7[0])
    add('ctrl_E7frame_r7', 'SAT', 'control', 'control: E7 frame-normal block at its dense rank 7 is feasible', lambda: block_instance(L7, Ra7, Ra7, 7))
    # ---- (5) one E6 per-term drop: a rank-6 deficient pair with |R cap A| = 8 has fitting minrank 4 (exists), not 3
    dm = deficient_directions(L6, 6); X = sorted(set(dm.values())); Br6 = b0rows(L6)
    ex_pair = None
    for i in range(27):
        for j in range(27):
            R = support(L6, X[i]); A = support(L6, X[j])
            if blk(Br6, R, A) == 6 and len(set(R) & set(A)) == 8: ex_pair = (R, A); break
        if ex_pair: break
    R, A = ex_pair
    add('e6term_r4', 'SAT', 'term', 'E6: a deficient pair of dense rank 6 with |R cap A| = 8 has fitting minrank <= 4', lambda: block_instance(L6, R, A, 4))
    add('e6term_r3', 'UNSAT', 'term', 'E6: the same pair has fitting minrank > 3', lambda: block_instance(L6, R, A, 3))
    return I

def _compositions(n, k):
    """all k-tuples of non-negative integers with sum n, in lexicographic order"""
    if k == 1: yield (n,); return
    for a in range(n + 1):
        for rest in _compositions(n - a, k - 1): yield (a,) + rest

def joint_instances():
    """shared-B instances (E6 square decoders, total <= 35) and the per-term floor instances.  Returns name -> dict like all_instances()."""
    L = UNITS['E6'][0]
    D = json.load(open(os.path.join(DATA, 'e6_square_decoders.json')))['decoders']
    plan = json.load(open(os.path.join(DATA, 'e6_joint_plan.json')))
    tot = plan['total']; I = {}; seen = {}
    for p in plan['plan']:
        d = p['decoder']; dec = D[d]
        terms = [(support(L, dec['X'][j]), support(L, dec['Y'][j])) for j in range(6)]
        for j in range(6):
            lo = p['lo'][j]; key = (tuple(terms[j][0]), tuple(terms[j][1]))
            if lo > 1 and key not in seen:
                seen[key] = 'floor_d%02d_t%d' % (d, j)
                I[seen[key]] = dict(expect='UNSAT', tag='floor', note='E6 decoder %d term %d: fitting minrank of B[R,A] <= %d is impossible (so rank >= %d for every admissible B)' % (d, j, lo - 1, lo),
                                    build=(lambda R=terms[j][0], A=terms[j][1], r=lo - 1: block_instance(L, R, A, r)))
        if d in (0, 7, 18):
            I['jointctrl_d%02d' % d] = dict(expect='SAT', tag='jointctrl', note='control: E6 decoder %d with caps = its dense ranks %s (sum %d): the dense B is a solution' % (d, p['dense'], sum(p['dense'])),
                                            build=(lambda terms=terms, caps=tuple(p['dense']): joint_cnf(L, terms, list(caps))[0]))
        slack = tot - sum(p['lo'])
        for ex in _compositions(slack, 6):
            caps = tuple(a + b for a, b in zip(p['lo'], ex))
            I['joint_d%02d_%s' % (d, '-'.join(map(str, caps)))] = dict(expect='UNSAT', tag='joint',
                note='E6 decoder %d: one admissible B with rank B[R_j,A_j] <= %s for all j (sum = %d)' % (d, list(caps), tot),
                build=(lambda terms=terms, caps=caps: joint_cnf(L, terms, list(caps))[0]))
    return I
