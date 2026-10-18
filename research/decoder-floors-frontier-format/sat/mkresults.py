"""Author tool: solve every instance of the registry (kissat 4.0.4, binary DRAT proof), verify UNSAT proofs with drat-trim, decode SAT models,
and write results.jsonl (one JSON line per instance).  Optionally xz-ships selected proofs into proofs/.
usage: python3 mkresults.py OUTDIR [name ...]"""
import sys, os, json, time, lzma, shutil
SATDIR = os.path.dirname(os.path.abspath(__file__)); HERE = SATDIR
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from rigid import *
from solve import *
SHIP = set(os.environ.get('SHIP', '').split(','))
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
R = registry(); names = sys.argv[2:] or list(R)
rows = []
for nm in names:
    t0 = time.time(); nv, cls, info, *_ = build_named(nm); d = dimacs(nv, cls); h = sha(d)
    cnf = os.path.join(out, nm + '.cnf'); open(cnf, 'w').write(d); pr = os.path.join(out, nm + '.drat')
    st, model = run_kissat(cnf, pr)
    row = dict(name=nm, unit=R[nm]['unit'], h=R[nm]['h'], sym=R[nm]['sym'], mode=R[nm]['mode'], expect=R[nm]['expect'], nv=nv, ncls=len(cls),
               orth=info['orth'], gauge=R[nm]['S'], cnf_sha256=h, status=st)
    if st == 'UNSAT':
        row['drat'] = 'VERIFIED' if run_drat(cnf, pr) else 'FAILED'; row['proof_bytes'] = os.path.getsize(pr)
        if nm in SHIP:
            os.makedirs(os.path.join(SATDIR, 'proofs'), exist_ok=True)
            with open(pr, 'rb') as f, lzma.open(os.path.join(SATDIR, 'proofs', nm + '.drat.xz'), 'wb', preset=9) as g: shutil.copyfileobj(f, g)
    elif st == 'SAT':
        fit, z, n = decode_model(nm, model); row.update(model_fitting=fit, orth_zero=z, orth_total=n)
    os.remove(pr) if os.path.exists(pr) else None; os.remove(cnf)
    row['secs'] = round(time.time() - t0, 1); rows.append(row); print(json.dumps(row), flush=True)
