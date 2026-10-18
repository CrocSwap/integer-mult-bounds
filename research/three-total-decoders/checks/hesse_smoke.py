"""Group X2 (harness only): the Hesse configuration over Z[w], and an exhaustive-cost smoke run of the sampler of g1/hesse.py with fixed seeds.
This is NOT the experiment: it shows the harness is exact (every configuration is evaluated over all 2^f admissible B) and records what the
smoke sample gives.  The running experiment's counts are in README 'Outcome X2'."""
import sys, os, random, json, itertools
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import hesse as H
pts, lines, xp = H.hesse()
ppl = sorted(sum(H.inc(p, l) for p in pts) for l in lines); lpp = sorted(sum(H.inc(p, l) for l in lines) for p in pts)
print("HS Hesse configuration over Z[w] (w^2+w+1=0): %d points, %d lines, points per line %s, lines per point %s; intersection points of the lines %d" % (
    len(pts), len(lines), sorted(set(ppl)), sorted(set(lpp)), len(xp)))
# the 9 points are the 9 flexes: any two lie on a common line with a third (Sylvester-Gallai fails: no ordinary line)
third = all(any(H.inc(a, l) and H.inc(b, l) for l in lines) for a, b in itertools.combinations(pts, 2))
print("HS every pair of the 9 points lies on one of the 12 lines (no ordinary line): %s" % third)
rng = random.Random(2026); mins = []; done = 0; tight = 0
while done < 16:
    P, Q = H.random_config(rng, xp, pts, lines)
    v, f, best = H.evaluate(P, Q, cap=20)
    if best is None or f < 6: continue
    done += 1; mins.append(best - v); tight += (best == v)
print("HS smoke sample: %d random configurations on the Hesse points/lines (v 6-12, 6 <= f <= 20), evaluated exhaustively over all B: smallest cost - v = %d, cost = v in %d, cost < v in %d" % (done, min(mins), tight, sum(1 for m in mins if m < 0)))
