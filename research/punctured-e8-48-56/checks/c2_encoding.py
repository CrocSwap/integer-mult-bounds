"""Encoding checks of sat/middrv.py (needs numpy, python-sat, networkx, sympy; env OPTSDIR with opts56_7.npz, MIDWORK scratch dir).
(a) qcnt (at-least-k counter) vs. brute force on 1,800 assignments; (b) leafcnf with all 120 S-variables fixed vs. the direct numpy test
(|S| <= P, q_g >= k, frames hit, every live outside line bad by a rank test) on sets near the E7 non-spanning family, type 7, P = 56, k = 17
and P = 50, k = 0 (alpha bound off).  The solver is kissat (a small shim stands in for pysat's Minisat22 in the two original scripts).  Each line prints PASS only if every comparison agrees."""
import os, sys, shutil, subprocess
PKG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = os.environ['MIDWORK']; os.makedirs(W, exist_ok=True); shutil.copy(os.environ['OPTSDIR'] + '/opts56_7.npz', W + '/opts56_7.npz')
os.environ['MIDSKIPINV'] = '1'
SHIM = """
import subprocess, tempfile, os
class Minisat22:
    def __init__(self, bootstrap_with=()): self.cls = [list(c) for c in bootstrap_with]
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def solve(self):
        nv = max([abs(l) for c in self.cls for l in c] + [1])
        with tempfile.NamedTemporaryFile('w', suffix='.cnf', delete=False) as f:
            f.write('p cnf %d %d\\n' % (nv, len(self.cls))); f.write(''.join(' '.join(map(str, c)) + ' 0\\n' for c in self.cls))
        try: r = subprocess.run([os.environ.get('KISSAT', 'kissat'), '-q', f.name], capture_output=True, text=True).stdout
        finally: os.unlink(f.name)
        assert 's SATISFIABLE' in r or 's UNSATISFIABLE' in r, r[:200]
        return 's SATISFIABLE' in r
"""
def run(argv, env, code):
    r = subprocess.run([sys.executable, '-c', code], env=dict(os.environ, **env), capture_output=True, text=True)
    print(('PASS ' if r.returncode == 0 else 'FAIL ') + ' '.join(argv) + ': ' + (r.stdout.strip().splitlines() or ['(no output)'])[-1] + ('' if r.returncode == 0 else r.stderr[-300:]), flush=True)

QCODE0 = "os.environ['MIDLIB']='1'; sys.argv=['middrv.py','7','56','17','60']\nexec(open(os.environ['PKGSAT']+'/middrv.py').read())\nfrom pysat.solvers import Minisat22\nrandom.seed(2); n=0\nfor kk in (1,6,16,17,30,63):\n    for _ in range(300):\n        c = max(0, min(63, kk + random.randint(-3, 3))); on = set(random.sample(range(63), c))\n        cls = []; nv = qcnt(list(range(1, 64)), kk, 63, cls)\n        cls += [[i + 1] if i in on else [-(i + 1)] for i in range(63)]\n        with Minisat22(bootstrap_with=cls) as so: assert so.solve() == (c >= kk); n += 1\nprint('qcnt OK', n)\n"
MCODE0 = "import os, sys, random, itertools, networkx as nx, numpy as np\nsys.argv = sys.argv[:4] + ['60']; N = int(os.environ.get('NTEST', '300'))\nexec(open(os.environ['PKGSAT']+'/middrv.py').read())\nfrom pysat.solvers import Minisat22\ndef cnfsat(S):\n    nv, cls, _ = leafcnf(set(S), [t for t in range(120) if t not in S])\n    with Minisat22(bootstrap_with=cls) as so: return so.solve()\nrandom.seed(1); tests = []\nif typ == 7:\n    Np = [t for t in range(120) if G[alpha, t] != 0 and t != alpha]\n    Gn = nx.Graph([(a, b) for a, b in itertools.combinations(Np, 2) if G[a, b] != 0])\n    cl = [c for c in nx.find_cliques(Gn) if len(c) >= 7][:40]\n    for c in cl:\n        C = set(random.sample(c, 7)); S = (set(Np) | {alpha}) - C; tests.append(S)\nbase = list(tests)\nfor S in base[:20]:\n    for t in random.sample(sorted(S), 10): tests.append(S - {t})\n    for _ in range(10):\n        a = random.choice(sorted(S)); b = random.choice([x for x in range(120) if x not in S]); tests.append((S - {a}) | {b})\nwhile len(tests) < N:\n    S = set(random.sample(range(120), random.randint(P - 8, P))); tests.append(S)\nagree = 0; nsat = 0\nfor S in tests:\n    a, b = cnfsat(S), direct(S)\n    assert a == b, ('DISAGREE', sorted(S), a, b)\n    agree += 1; nsat += a\nprint('typ', typ, 'P', P, 'k', k, 'NOALPHA', bool(os.environ.get('NOALPHA')), 'tests', agree, 'SAT', nsat, 'ALL AGREE')\n"
QCODE = QCODE0.replace('from pysat.solvers import Minisat22', SHIM)
MCODE = MCODE0.replace('from pysat.solvers import Minisat22', SHIM)
PRE = 'import os, sys\n__file__ = os.environ["PKGSAT"] + "/middrv.py"\n'
env = dict(MIDLIB='1', PKGSAT=PKG + '/sat')
run(['qcnt'], env, PRE + 'import random\n' + QCODE)
run(['leafcnf vs direct, T7 P56 k17'], dict(env, NTEST='440'), PRE + 'sys.argv = ["m", "7", "56", "17", "60"]\n' + MCODE)
run(['leafcnf vs direct, T7 P50 k0 (NOALPHA)'], dict(env, NTEST='440', NOALPHA='1'), PRE + 'sys.argv = ["m", "7", "50", "0", "60"]\n' + MCODE)
