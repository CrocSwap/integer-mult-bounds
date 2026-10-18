"""E2: scalar-layer enumeration of ALL pair-preserving monomial rho (P = 2, 3 pairs) over F2.
Builds inputs/r39s/rho01.cpp (0-1 BFS over bank matrices; generators: pair-local shears Y+=X / X+=Y, bridges
X_d+=X_s, Y_s+=Y_d) with the system C++ compiler, runs it, compares the output byte-for-byte with the shipped
evidence/E2/rho01_P{2,3}.txt, and checks the claims.  Without a compiler only the shipped evidence is parsed."""
import hashlib, os, re, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ok_all = True
def check(cid, ok, detail=''):
    global ok_all
    ok_all &= bool(ok)
    print(('PASS ' if ok else 'FAIL ') + cid + ('  ' + detail if detail else ''), flush=True)
cxx = shutil.which('c++') or shutil.which('g++') or shutil.which('clang++')
exe = None
if cxx:
    tmp = tempfile.mkdtemp()
    exe = os.path.join(tmp, 'rho01')
    subprocess.run([cxx, '-O2', '-std=c++17', '-o', exe, os.path.join(ROOT, 'inputs', 'r39s', 'rho01.cpp')], check=True)
for P, states in ((2, 720), (3, 1451520)):
    ev = open(os.path.join(ROOT, 'evidence', 'E2', 'rho01_P%d.txt' % P)).read()
    if exe:
        out = subprocess.run([exe, str(P)], capture_output=True, text=True, check=True).stdout
        check('E2.rerun-P%d' % P, out == ev, 'fresh run identical to shipped evidence (sha256 %s)' % hashlib.sha256(ev.encode()).hexdigest()[:16])
    else:
        out = ev
    m = re.search(r'^states (\d+)$', out, re.M)
    check('E2.reachable-P%d' % P, m and int(m.group(1)) == states, 'reachable set %s = |Sp(%d,2)|' % (m.group(1), 2 * P))
    rows = re.findall(r'perm=(\d+) swapmask=(\d+) : locals=(\d+) bridges=(\d+)', out)
    import math
    check('E2.targets-P%d' % P, len(rows) == math.factorial(P) * 2 ** P, '%d pair-preserving targets, none unreached' % len(rows))
    good = True; ratios = []
    for perm, mask, loc, br in rows:
        k = bin(int(mask)).count('1'); loc = int(loc); br = int(br)
        good &= (loc == (0 if k == 0 else 2 * k + 1))
        if k: ratios.append((loc / k, perm, mask))
    check('E2.locals=2k+1-P%d' % P, good, 'locals = 0 if k=0 else 2k+1, k = number of exchanged pairs, every target')
    full = [(l, b) for p, mk, l, b in rows if p == ''.join(map(str, range(P))) and int(mk) == 2 ** P - 1][0]
    check('E2.B_K-P%d' % P, full == {2: ('5', '3'), 3: ('7', '6')}[P], 'full exchange (identity perm) = %s locals, %s bridges' % (full[0], full[1]))
    best = min(r[0] for r in ratios)
    check('E2.no-rho-beats-B_K-P%d' % P, abs(best - (2 * P + 1) / P) < 1e-12, 'min locals per exchanged pair %.4f = (2P+1)/P = B_K; multiplier 1.000' % best)
# python BFS cross-check at P = 2 (independent implementation)
ev = open(os.path.join(ROOT, 'evidence', 'E2', 'rho_bfs_P2.txt')).read()
py = subprocess.run([sys.executable, '-I', '-B', os.path.join(ROOT, 'inputs', 'r39s', 'rho_bfs.py'), '2'], capture_output=True, text=True, check=True).stdout
check('E2.python-P2', py == ev and len(ev.splitlines()) == 8, 'rho_bfs.py 2 reproduces the shipped output (8 targets)')
sys.exit(0 if ok_all else 1)
