#!/usr/bin/env python3
"""Driver for the SAT instances (standard library only; needs `kissat` for solving and `drat-trim` for proof checking, both optional here).
  python3 run.py list [tag]                         list instances
  python3 run.py gen NAME [OUTDIR]                  write NAME.cnf and print its sha256
  python3 run.py solve OUTDIR [names|tags...]       generate, solve with kissat (proof to NAME.drat), check with drat-trim, append to OUTDIR/results.jsonl
  python3 run.py check NAME CNF [PROOF_OR_MODEL]    check a shipped result: CNF hash == regenerated; DRAT via drat-trim / model by clause evaluation
Environment: KISSAT (default `kissat`), DRAT_TRIM (default `drat-trim`), KISSAT_TIMEOUT seconds (default 1800)."""
import os, sys, json, hashlib, subprocess, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import instances as I

KISSAT = os.environ.get('KISSAT', shutil.which('kissat') or 'kissat')
DRAT = os.environ.get('DRAT_TRIM', shutil.which('drat-trim') or 'drat-trim')
TMO = int(os.environ.get('KISSAT_TIMEOUT', '1800'))
def sha(b): return hashlib.sha256(b).hexdigest()

def parse_model(out):
    pos = set()
    for line in out.splitlines():
        if line.startswith('v'):
            for x in line.split()[1:]:
                x = int(x)
                if x > 0: pos.add(x)
    return pos

def model_satisfies(cnf_text, pos):
    for line in cnf_text.splitlines():
        if not line or line[0] in 'pc': continue
        ok = False
        for x in line.split():
            x = int(x)
            if x == 0: break
            if (x > 0 and x in pos) or (x < 0 and -x not in pos): ok = True; break
        if not ok: return False
    return True

def solve(name, inst, outdir, tmo=TMO):
    cnf = inst['build']().dimacs(); path = os.path.join(outdir, name + '.cnf'); open(path, 'w').write(cnf)
    proof = os.path.join(outdir, name + '.drat')
    t0 = time.time()
    try:
        r = subprocess.run([KISSAT, '-q', path, proof], capture_output=True, text=True, timeout=tmo); out = r.stdout
    except subprocess.TimeoutExpired:
        return dict(name=name, status='TIMEOUT', seconds=tmo, cnf_sha256=sha(cnf.encode()), expect=inst['expect'])
    dt = time.time() - t0
    res = dict(name=name, expect=inst['expect'], cnf_sha256=sha(cnf.encode()), seconds=round(dt, 1))
    if 'UNSATISFIABLE' in out:
        res['status'] = 'UNSAT'; res['proof_bytes'] = os.path.getsize(proof)
        d = subprocess.run([DRAT, path, proof, '-t', '3000'], capture_output=True, text=True)
        res['drat'] = 'VERIFIED' if 's VERIFIED' in d.stdout else 'NOT VERIFIED'
        if os.environ.get('DROP_FILES') == '1': os.remove(proof); os.remove(path)
    elif 'SATISFIABLE' in out:
        pos = parse_model(out); res['status'] = 'SAT'; res['model_ok'] = model_satisfies(cnf, pos)
        open(os.path.join(outdir, name + '.model'), 'w').write(' '.join(map(str, sorted(pos))) + '\n')
        if os.path.exists(proof): os.remove(proof)
    else: res['status'] = 'UNKNOWN'
    return res

def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    A = I.all_instances()
    if a[0] != 'check' or a[1].startswith(('joint', 'floor')) or True:
        try: A.update(I.joint_instances())
        except FileNotFoundError: pass
    if a[0] == 'list':
        for k, v in A.items():
            if len(a) < 2 or v['tag'] == a[1]: print(k, v['expect'], v['tag'], '-', v['note'])
    elif a[0] == 'gen':
        out = a[2] if len(a) > 2 else '.'; os.makedirs(out, exist_ok=True)
        cnf = A[a[1]]['build']().dimacs(); open(os.path.join(out, a[1] + '.cnf'), 'w').write(cnf); print(sha(cnf.encode()), a[1])
    elif a[0] == 'solve':
        out = a[1]; os.makedirs(out, exist_ok=True); sel = a[2:]
        names = [k for k, v in A.items() if not sel or k in sel or v['tag'] in sel]
        for k in names:
            res = solve(k, A[k], out); print(json.dumps(res), flush=True)
            open(os.path.join(out, 'results.jsonl'), 'a').write(json.dumps(res) + '\n')
    elif a[0] == 'check':
        name, cnfp = a[1], a[2]; cnf = open(cnfp).read(); want = A[name]['build']().dimacs()
        print('cnf matches generator:', cnf == want)
        if len(a) > 3:
            if A[name]['expect'] == 'UNSAT':
                d = subprocess.run([DRAT, cnfp, a[3], '-t', '3000'], capture_output=True, text=True); print('drat:', 'VERIFIED' if 's VERIFIED' in d.stdout else 'NOT VERIFIED')
            else:
                pos = set(map(int, open(a[3]).read().split())); print('model satisfies cnf:', model_satisfies(cnf, pos))
if __name__ == '__main__': main()
