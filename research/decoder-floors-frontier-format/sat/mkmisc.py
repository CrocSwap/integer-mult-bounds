"""Author tool for sat/misc.py (see mkresults.py).  usage: python3 mkmisc.py OUTDIR [--slow] [name ...]  -> JSON lines on stdout.
Instances flagged slow are solved WITHOUT a proof (UNSAT recorded as 'UNSAT (no proof)')."""
import sys, os, json, time, lzma, shutil, hashlib
SATDIR = os.path.dirname(os.path.abspath(__file__)); HERE = SATDIR
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from misc import *
from solve import *
args = [a for a in sys.argv[1:] if not a.startswith('--')]; out = args[0]; os.makedirs(out, exist_ok=True)
R = registry(); names = args[1:] or [n for n in R if not R[n]['slow'] or '--slow' in sys.argv]
SHIP = set(os.environ.get('SHIP', '').split(','))
for nm in names:
    t0 = time.time(); d = dimacs_of(nm); cnf = os.path.join(out, nm + '.cnf'); open(cnf, 'w').write(d); pr = os.path.join(out, nm + '.drat')
    slow = R[nm]['slow']; st, model = run_kissat(cnf, None if slow else pr, tmo=3000)
    row = dict(name=nm, expect=R[nm]['expect'], slow=slow, cnf_sha256=hashlib.sha256(d.encode()).hexdigest(), status=st)
    if st == 'UNSAT' and not slow:
        row['drat'] = 'VERIFIED' if run_drat(cnf, pr) else 'FAILED'; row['proof_bytes'] = os.path.getsize(pr)
        if nm in SHIP:
            os.makedirs(os.path.join(SATDIR, 'proofs'), exist_ok=True)
            with open(pr, 'rb') as f, lzma.open(os.path.join(SATDIR, 'proofs', nm + '.drat.xz'), 'wb', preset=9) as g: shutil.copyfileobj(f, g)
    elif st == 'SAT': row['model_ok'] = check_model(nm, model)
    for p in (cnf, pr):
        if os.path.exists(p): os.remove(p)
    row['secs'] = round(time.time() - t0, 1); print(json.dumps(row), flush=True)
