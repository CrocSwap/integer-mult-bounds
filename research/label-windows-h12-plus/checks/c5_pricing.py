"""c5: the arithmetic of the closures under the INHERITED pricing model (lib/pricing.py).  The model itself is RECORDED, not derived here.
  c5.a  break-even table be(h) = largest cost c <= 64 with X(112,c,h)/base >= 1 and roof/rb >= 1, h = 11..18  ->  55 51 46 42 38 33 29 25  (full scan from c = 64 down)
  c5.b  floors vs break-even:  h=12: 8*7=56 > 51;  h=13: 8*6=48 > 46;  h=14: 8*6=48 > 42;  h=15..18: 8*5=40 > be(h) (38, 33, 29, 25)
  c5.c  X(112,40,h)/base for every integer h = 15..200: all < 1 and strictly decreasing (max at h = 15); h > 112 is beyond the table's 112 columns, included anyway
  c5.d  X(112,c,h) strictly decreasing in c on c = 40..112 (step 4; FULL=1: step 1 and h = 15..112; X = 0 where the skeleton has D <= 0, i.e. c >= 100) for h in a grid, so cost >= 40 never reaches base; margins reported
Standard library only."""
import hashlib, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
RES = os.path.dirname(os.path.dirname(HERE))
pins = json.load(open(os.path.join(HERE, '..', 'SOURCES.json')))['repo_imports']
pinok = all(hashlib.sha256(open(os.path.join(RES, p), 'rb').read()).hexdigest() == h for p, h in pins.items())
import pricing as P
FULL = os.environ.get('FULL') == '1'; fail = 0; t0 = time.time()
want = {11: 55, 12: 51, 13: 46, 14: 42, 15: 38, 16: 33, 17: 29, 18: 25}
got = {h: P.breakeven(h) for h in want}
print(('PASS' if got == want and pinok else 'FAIL') + ' c5.a  model files pinned by sha256 (%s), break-even by full scan, h = 11..18: ' % ('ok' if pinok else 'PIN MISMATCH') + ' '.join(str(got[h]) for h in sorted(got)) + ' (%ds)' % (time.time() - t0)); fail += not (got == want and pinok)
floors = {12: 7, 13: 6, 14: 6, 15: 5, 16: 5, 17: 5, 18: 5}
ok = all(8 * f > got[h] for h, f in floors.items()) and [8 * floors[h] for h in (12, 13, 14)] == [56, 48, 48]
print(('PASS' if ok else 'FAIL') + ' c5.b  8 * per-term floor > break-even: ' + ', '.join('h=%d: %d > %d' % (h, 8 * f, got[h]) for h, f in floors.items())); fail += not ok
t0 = time.time(); M = [P.Xc(112, 40, h) / P.base for h in range(15, 201)]
ok = max(M) < 1 and all(M[i] > M[i + 1] for i in range(len(M) - 1))
print(('PASS' if ok else 'FAIL') + ' c5.c  X(112,40,h)/base < 1 and strictly decreasing for h = 15..200: %.4f at h=15, %.4f at h=112, %.4f at h=200 (%ds)' % (M[0], M[112 - 15], M[-1], time.time() - t0)); fail += not ok
t0 = time.time(); step = 1 if FULL else 4
hs = list(range(15, 113)) if FULL else [15, 16, 17, 18, 19, 20, 21, 22, 24, 32, 48, 64, 96, 112]
ok = True
for h in hs:
    col = [P.Xc(112, c, h) / P.base for c in range(40, 113, step)]
    ok &= all(col[i] > col[i + 1] or col[i] == col[i + 1] == 0 for i in range(len(col) - 1)) and col[0] < 1 and col[-1] == 0
print(('PASS' if ok else 'FAIL') + ' c5.d  X(112,c,h) strictly decreasing in c on 40..112 (step %d; zero once D <= 0) and < base, %d widths h in {%s...} (%ds)' % (step, len(hs), ','.join(map(str, hs[:6])), time.time() - t0)); fail += not ok
sys.exit(1 if fail else 0)
