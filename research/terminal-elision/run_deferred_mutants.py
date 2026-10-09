#!/usr/bin/env python3
"""Run malformed real-witness files through the actual independent checkers."""
import argparse
import copy
import gzip
import json
from pathlib import Path
import subprocess
import sys


def main():
    p=argparse.ArgumentParser();p.add_argument('--parent',type=Path,required=True)
    p.add_argument('--parent-audit',type=Path)
    p.add_argument('--terminal',type=Path);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    here=Path(__file__).resolve().parent
    w=json.loads(gzip.decompress((a.parent/'word.json.gz').read_bytes()))
    pr=json.loads((a.parent/'complex-profile.json').read_text())
    if a.terminal:
        assert a.parent_audit
        ew=json.loads(gzip.decompress((a.terminal/'word.json.gz').read_bytes()))
        ep=json.loads((a.terminal/'complex-profile.json').read_text())
    results=[]
    def run(name,W,P,terminal=False):
        folder=a.out/name;folder.mkdir()
        (folder/'word.json.gz').write_bytes(gzip.compress(json.dumps(W,separators=(',',':')).encode(),mtime=0))
        (folder/'complex-profile.json').write_text(json.dumps(P,indent=2)+'\n')
        command=[sys.executable,str(here/('verify_terminal_word.py' if terminal else 'verify_deferred_word.py')),
                 '--case',str(folder),'--output',str(folder/'audit')]
        if terminal:command+=['--parent',str(a.parent),'--parent-audit',str(a.parent_audit)]
        q=subprocess.run(command,text=True,capture_output=True,timeout=240)
        (folder/'stdout.log').write_text(q.stdout);(folder/'stderr.log').write_text(q.stderr)
        assert q.returncode!=0 and 'AssertionError' in q.stderr,(name,q.returncode,q.stderr)
        results.append(dict(name=name,rejected=True,returncode=q.returncode,command=command,
                            last_error=q.stderr.strip().splitlines()[-1]))
        print('REJECTED',name,flush=True)
    z=copy.deepcopy(w)
    s=next(i for i,row in enumerate(z['adjoint_ordinary']) if row)
    t=next(iter(z['adjoint_ordinary'][s]));z['adjoint_ordinary'][s][t]+=1
    run('adjoint-coefficient',z,pr)
    z=copy.deepcopy(w);centres={int(s) for s,j in z['role_root'].items() if z['kind'][j]}
    last=max(i for i,o in enumerate(z['ops']) if o[0]!='src' and centres.intersection(o[1:3]))
    assert last in z['phase_one'];z['phase_one'].remove(last)
    run('center-phase-omission',z,pr)
    z=copy.deepcopy(w)
    s=next(s for s,B in z['sigma'].items() if B and z['reach'][int(s)])
    target=z['reach'][int(s)][0];mask=z['frames'][str(target+1)][0]
    dim=len(z['sigma'][s]);bad=mask&-mask
    # Preserve dimension/order and nondegeneracy, but deliberately include
    # one norm-one vector outside the required target hyperplane.
    coordinates=[bad]+[1<<i for i in range(z['h']) if (1<<i)!=bad]
    z['sigma'][s]=coordinates[:dim]
    assert (mask&bad).bit_count()==1
    run('illegal-sigma-target-containment',z,pr)
    z=copy.deepcopy(pr);key=str(w['h']-1);z['child_multiplicities'][key]-=2*w['v']*w['h']
    run('omitted-copied-center-charge',w,z)
    if a.terminal:
        z=copy.deepcopy(ew);row=next(e for e in z['events'] if e[0] in ('direct_input','direct_aux'));row[3]*=-1
        run('redirect-coefficient',z,ep,True)
        z=copy.deepcopy(ew);i=next(i for i,e in enumerate(z['events']) if e[0]=='direct_aux');del z['events'][i]
        run('missing-redirected-incoming-update',z,ep,True)
    (a.out/'receipt.json').write_text(json.dumps(dict(status='PASS actual mutant files rejected',tests=results,
        reflection_sign_scope='Separately verified on an exact nontrivial Gaussian-rational dirty word in check_deferred_phase_gauges.py; not counted as a large-witness mutation.'),indent=2)+'\n')


if __name__=='__main__':main()
