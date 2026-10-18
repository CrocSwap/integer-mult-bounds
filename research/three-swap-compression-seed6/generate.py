#!/usr/bin/env python3
"""Generate independent SAT certificates; optional pinned build dependencies.
Cinna Davis with OpenAI Codex assistance. Apache-2.0.
"""
import gzip,json,time
from pathlib import Path
from pysat.solvers import Glucose3
import pysat
import cnf
ROOT=Path(__file__).resolve().parent
results=[]
for index in list(range(6,35))+list(range(6)):
    labels=cnf.patterns()[index];formula=cnf.encode(labels);started=time.monotonic()
    with Glucose3(bootstrap_with=formula.clauses,with_proof=True) as solver:
        sat=solver.solve();proof=solver.get_proof()
        if sat:raise RuntimeError('SAT in independent encoder: '+labels)
    # If the formula is contradictory at load time, get_proof may be empty.
    # Empty-clause RUP checking still verifies that directly.
    if not proof or proof[-1]!='0':proof.append('0')
    item={'index':index,'labels':labels,'variables':formula.variables,'clauses':formula.clauses,'proof':proof}
    results.append(item)
    print(json.dumps({'index':index,'labels':labels,'variables':formula.variables,'clauses':len(formula.clauses),'proof_lines':len(proof),'seconds':round(time.monotonic()-started,6)}),flush=True)
payload={'format':'CNF-and-DRUP-v1','generator':'python-sat '+pysat.__version__+' Glucose3','results':sorted(results,key=lambda x:x['index'])}
raw=(json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode()
with gzip.GzipFile(filename='',mode='wb',fileobj=(ROOT/'CERTIFICATES.json.gz').open('wb'),mtime=0) as stream:stream.write(raw)
print('DONE patterns='+str(len(results))+' payload_bytes='+str(len(raw)),flush=True)
