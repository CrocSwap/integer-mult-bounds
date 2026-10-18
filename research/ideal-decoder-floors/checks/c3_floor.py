"""CHECKED (exact): Theorem 4 (root-code floor).  For every unit: the F2 factorisation of the dense pairing B (rank k+1), the proper subspaces W_z
and their sums (the 'types'), the minimum term rank r_min over all pairs of row/column types, the floor T * r_min, and the size omega of a largest
orthogonal live set (the hypothesis omega = T under which the number of terms is >= T for every exact decoder with dense B)."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from report import check, finish
from units import UNITS, E8, E7, gram, first_frame, decoder_cost, true, unit_vectors
import floor as FL
import p104

# (name, roots, dead set, T, expected: k+1, #proper W_z, #types, r_min, omega_live)
cases = []
for nm in ('D4', 'D5', 'D6', 'E6', 'E7', 'E8'):
    cases.append((nm, UNITS[nm][0], set(), UNITS[nm][1]))
F8 = first_frame(gram(E8), 8)
cases.append(('P112', E8, set(F8), 8))
F7 = first_frame(gram(E7), 7)
cases.append(('E7-F0', E7, set(F7), 7))
G, F0, frames, F1, sols = p104.build()
cases.append(('P104', E8, set(F0) | set(F1), 8))

EXPECT = {  # k+1, proper W_z (rows), #types (rows), r_min, floor, omega(live)
    'D4': (3, 0, 1, 3, 12, 4), 'D5': (5, 5, 6, 3, 15, 4), 'D6': (5, 0, 1, 5, 30, 6),
    'E6': (7, 27, 28, 5, 30, 4), 'E7': (7, 0, 1, 7, 49, 7), 'E8': (9, 0, 1, 9, 72, 8),
    'P112': (9, 8, 9, 8, 64, 8), 'E7-F0': (7, 7, 8, 6, 42, 7), 'P104': (9, 16, 17, 7, 56, 8)}
for name, L, dead, T in cases:
    a = FL.analyse(L, dead, T)
    Gm = gram(L)
    live = [t for t in range(len(L)) if t not in dead]
    om = FL.max_orthogonal(Gm, live, T)
    k1, npw, nty, rmin, flo, omg = EXPECT[name]
    good = (a['k1'], a['proper'][0], a['types'][0], a['rmin'], a['floor'], om) == (k1, npw, nty, rmin, flo, omg) and a['proper'][0] == a['proper'][1] and a['types'][0] == a['types'][1]
    check('F1.' + name, good,
          '%s: v=%d T=%d k+1=%d, proper W_z %d (rows) / %d (cols), types %d / %d, r_min=%d, floor T*r_min=%d, omega(live orthogonal)=%d%s' %
          (name, a['v'], T, a['k1'], a['proper'][0], a['proper'][1], a['types'][0], a['types'][1], a['rmin'], a['floor'], om,
           '' if good else '   EXPECTED %s' % (EXPECT[name],)))

# sharpness: an explicit exact decoder (c2_decoders.py) whose cost equals the floor T * r_min
live8 = [E8[i] for i in range(120) if i not in set(F8)]
live7 = [E7[i] for i in range(63) if i not in set(F7)]
sharp = [('E8', E8, unit_vectors(8), 72), ('P112', live8, [true(E8[i]) for i in F8], 64), ('E7', E7, [true(E7[i]) for i in F7], 49),
         ('E7-F0', live7, [true(E7[i]) for i in F7], 42), ('D4', UNITS['D4'][0], unit_vectors(4), 12), ('D6', UNITS['D6'][0], unit_vectors(6), 30)]
for name, roots, basis, floor in sharp:
    ok, cost, ranks, P, Q = decoder_cost(roots, basis)
    check('F1.sharp-' + name, ok and cost == floor, '%s: exact decoder cost %d = floor %d (sharp, any number of terms in the root-code class with dense B)' % (name, cost, floor))
G, F0, frames, F1, sols = p104.build()
ok, ranks, live104 = p104.cost_of_pairs(G, sols[0], set(F0) | set(F1))
check('F1.sharp-P104', ok and sum(ranks) == 56, 'P104: frame-pair decoder cost %d = floor 56' % sum(ranks))
ok, cost, ranks, P, Q = decoder_cost(UNITS['D5'][0], unit_vectors(5))
check('F1.D5-gap', ok and cost == 20, 'D5: coordinate decoder costs %d = v = 20; the pairwise floor is only 15 (square decoders: 20, see c4_coupling.py)' % cost)
finish()
