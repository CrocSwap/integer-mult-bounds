#!/usr/bin/env python3
"""Optional proof producer; install python-sat==1.9.dev15 separately.

Cold verification uses neither this solver nor the converter. See README.md.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import time

import encoding


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--converter", type=Path, required=True)
    parser.add_argument("--dimension", type=int, choices=(8, 9), required=True)
    args = parser.parse_args()
    from pysat.solvers import Cadical153
    import pysat
    args.work.mkdir(parents=True, exist_ok=True)
    c = args.dimension
    clauses = []
    formula = encoding.archived(c, lambda i, row: clauses.append(list(row)))
    prefix = args.work/f"c{c}"
    cnf = prefix.with_suffix('.cnf')
    with cnf.open('w', encoding='ascii', newline='\n') as stream:
        stream.write(f'p cnf {formula.variables} {formula.clauses}\n')
        for row in clauses:
            stream.write(' '.join(map(str,row))+' 0\n')
    started = time.perf_counter()
    with Cadical153(bootstrap_with=clauses, with_proof=True) as solver:
        answer = solver.solve()
        if answer:
            prefix.with_suffix('.counterexample.json').write_text(json.dumps(solver.get_model())+'\n')
        encoding.need(answer is False, "unexpected SAT result: preserve the counterexample")
        proof = solver.get_proof()
        stats = solver.accum_stats()
    drat = prefix.with_suffix('.drat')
    drat.write_text('\n'.join(proof)+'\n', encoding='ascii')
    lrat = prefix.with_suffix('.lrat')
    process = subprocess.run([str(args.converter), str(cnf), str(drat), '-L', str(lrat), '-U', '-w'],
                             text=True, capture_output=True, timeout=600)
    prefix.with_suffix('.converter.log').write_text(process.stdout+process.stderr)
    encoding.need(process.returncode == 0 and 's VERIFIED' in process.stdout, "converter did not verify")
    # Removing deletions is sound for RUP: additional available premises do
    # not invalidate the explicit unit deductions. IDs are not renumbered.
    lines = [line for line in lrat.read_text().splitlines() if line.split()[1] != 'd']
    payload = ('\n'.join(lines)+'\n').encode('ascii')
    archive = prefix.with_suffix('.lrat.gz')
    archive.write_bytes(gzip.compress(payload, mtime=0))
    report = {'dimension':c, 'mode':'none' if c == 8 else 'neB0',
              'pysat':pysat.__version__, 'solver':'Cadical153', 'answer':'UNSAT',
              'variables':formula.variables, 'clauses':formula.clauses,
              'clause_payload_sha256':formula.payload_hash.hexdigest(),
              'cnf_sha256':hashlib.sha256(cnf.read_bytes()).hexdigest(),
              'drat_sha256':hashlib.sha256(drat.read_bytes()).hexdigest(),
              'proof_payload_sha256':hashlib.sha256(payload).hexdigest(),
              'proof_bytes':len(payload), 'compressed_bytes':archive.stat().st_size,
              'proof_additions':len(lines), 'seconds':time.perf_counter()-started,
              'stats':stats, 'positive_model_violated_clauses':formula.unsatisfied}
    prefix.with_suffix('.producer.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True),flush=True)


if __name__ == '__main__':
    main()
