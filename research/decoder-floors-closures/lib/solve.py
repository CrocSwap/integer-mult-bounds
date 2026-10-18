"""Thin wrappers around kissat and drat-trim (both optional).  Never uses CaDiCaL."""
import os, shutil, subprocess
def find(env, name):
    p = os.environ.get(env) or shutil.which(name)
    return p if p and os.path.exists(p) else None
def kissat(): return find('KISSAT', 'kissat')
def drat_trim(): return find('DRAT_TRIM', 'drat-trim')
def run_kissat(cnf, proof=None, tmo=900):
    """returns (status 'SAT'|'UNSAT'|'UNKNOWN', set of true variables or None)"""
    cmd = [kissat(), '-q'] + ([cnf, proof] if proof else [cnf])
    try: o = subprocess.run(cmd, capture_output=True, text=True, timeout=tmo).stdout
    except subprocess.TimeoutExpired: return 'UNKNOWN', None
    if 'UNSATISFIABLE' in o: return 'UNSAT', None
    if 'SATISFIABLE' in o:
        return 'SAT', set(int(x) for l in o.splitlines() if l.startswith('v') for x in l.split()[1:] if int(x) > 0)
    return 'UNKNOWN', None
def run_drat(cnf, proof, tmo=3000):
    d = subprocess.run([drat_trim(), cnf, proof, '-t', str(tmo)], capture_output=True, text=True)
    return 's VERIFIED' in d.stdout
