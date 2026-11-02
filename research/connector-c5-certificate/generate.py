"""Regenerate the target and binary DRAT with pinned python-sat (costly).

This is not needed for archived LRAT replay. Proof bytes may vary across
solver/compiler versions; correctness comes from replay against the exact CNF.
"""
import argparse
import ctypes
import hashlib
import json
import shutil
import time
from importlib.metadata import version
from pathlib import Path

from checks import build_instance, audit_counter_bridge


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output', type=Path, help='new or empty output directory')
    args = parser.parse_args()
    if version('python-sat') != '1.9.dev15':
        raise SystemExit('requires python-sat==1.9.dev15')
    args.output.mkdir(parents=True, exist_ok=True)
    if any(args.output.iterdir()):
        raise SystemExit('output directory must be empty')
    from pysat.solvers import Solver
    cnf, pool = build_instance()
    audit_counter_bridge(cnf, pool)
    cnf_path = args.output / 'instance.cnf'
    cnf.to_file(str(cnf_path))
    start = time.monotonic()
    with Solver(name='cadical195', bootstrap_with=cnf.clauses, with_proof=True) as s:
        if s.solve():
            raise SystemExit('unexpected SAT; no exclusion established')
        solve_seconds = time.monotonic() - start
        # Python's flush does not flush the native wrapper's separate FILE*.
        # fflush(NULL) is the POSIX/C interface for flushing output streams.
        libc = ctypes.CDLL(None)
        libc.fflush.argtypes = [ctypes.c_void_p]
        libc.fflush.restype = ctypes.c_int
        if libc.fflush(None) != 0:
            raise OSError('native proof stream flush failed')
        # Pinned PySAT wrapper exposes its binary proof file here. Avoid
        # get_proof(), which expands the trace into millions of Python strings.
        proof = s.solver.prfile
        proof.flush()
        proof.seek(0)
        with (args.output / 'proof.bdrat').open('wb') as out:
            shutil.copyfileobj(proof, out)
    receipt = {'solver': 'cadical195', 'python_sat': version('python-sat'),
               'solve_seconds': solve_seconds, 'variables': cnf.nv,
               'clauses': len(cnf.clauses),
               'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in [cnf_path, args.output / 'proof.bdrat']}}
    (args.output / 'generation.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, sort_keys=True))


if __name__ == '__main__':
    main()
