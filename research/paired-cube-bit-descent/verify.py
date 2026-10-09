#!/usr/bin/env python3
"""Read-only exact successor audit; prerequisite source files stay unchanged."""
import argparse
import copy
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
if hasattr(sys,'set_int_max_str_digits'):sys.set_int_max_str_digits(0)

def digest(p):return sha256(p.read_bytes()).hexdigest()
def js(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,dict):return {str(k):js(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)):return [js(v) for v in x]
    return x

def pins(root):
    manifest=json.loads((HERE/'SOURCE.json').read_text());base=root/'research/paired-cube-balanced-161'
    assert digest(base/'SOURCE.json')==manifest['prerequisite_manifest_sha256'],'PR163 source manifest drift'
    inherited=json.loads((base/'SOURCE.json').read_text())['files']
    assert {p:digest(root/p) for p in inherited}==inherited,'PR163 dependency drift'
    own=manifest['files'];assert {p:digest(HERE/p) for p in own}==own,'Successor source drift'
    return dict(prerequisite_manifest=manifest['prerequisite_manifest_sha256'],successor=own)

def run(command):
    result=subprocess.run(command,text=True,capture_output=True)
    if result.returncode:raise ValueError(result.stdout+result.stderr)
    return result.stdout

def build(root):
    base=root/'research/paired-cube-balanced-161'
    print('Reconstructing the exact deterministic frame plan.',file=sys.stderr,flush=True)
    run([sys.executable,'-B',str(HERE/'make_plan.py'),'--source',str(root)])
    sys.path.insert(0,str(base/'bit'));sys.path.insert(0,str(base/'arithmetic'));sys.path.insert(0,str(HERE))
    import word
    from prove import certify
    from prime_check import certificate as primes
    import certificate as arithmetic
    plan=json.loads((HERE/'descent.json').read_text())
    assert plan['provenance']['prerequisite_manifest_sha256']==digest(base/'SOURCE.json')
    assert plan['provenance']['prerequisite_descent_sha256']==digest(base/'bit/descent.json')
    oldplan=json.loads((base/'bit/descent.json').read_text())
    assert len(plan['frames'])==1464 and len(oldplan['frames'])==1296
    assert len(plan['provenance']['accepted_components'])==168
    # Candidate accepts a supplied plan in its plan directory; its checker and all
    # scalar/frame inputs remain the unmodified source-pinned PR163 implementation.
    word.HERE=HERE
    c=word.Candidate([]);c.exact_frames();row=c.row()
    assert row['changed_operation_frames']==1464 and row['reused_registers']==0
    print('Checking every F2 and integer source, target and dirty column.',file=sys.stderr,flush=True)
    formal=[c.formal(r) for r in (2,0)];controls=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,AssertionError,KeyError):controls.append(name)
        else:raise ValueError('Adverse control accepted: '+name)
    for tamper in ('omit_compensation','missing_partner'):reject(tamper,lambda t=tamper:c.formal(2,t))
    bad=word.Candidate([]);bad.opframe[bad.changed_frames[0]]=bad.register([])
    reject('zero_operation_frame',bad.exact_frames)
    prime=primes(HERE/'descent.json');assert prime['total_operation_frames']==1464
    moment=certify(row)
    print('Replaying the retained signed complex supplier and assembly controls.',file=sys.stderr,flush=True)
    complex_result=json.loads(run([sys.executable,'-B',str(base/'complex/prove.py')]))
    retained=json.loads((base/'certificate.json').read_text())
    assert complex_result==retained['complex'],'Retained complex proof no longer reproduces'
    old_arithmetic=arithmetic.certificate(complex_result['profile'],complex_result['physical'])
    assert old_arithmetic==retained['arithmetic'],'Retained arithmetic controls no longer reproduce'
    cr=complex_result['profile'];coarse=moment['coarse_saving'];atom=moment['atom_beta']
    final=arithmetic.price(cr,arithmetic.AC,coarse,arithmetic.BETA,arithmetic.ETA,arithmetic.WEAKENING,'balanced',atom)
    assert final['actual_bit_saving']==moment['ordinary_saving']
    assert final['kappa']==Q(594035602295411,10**18)>Q(retained['kappa'])
    finite=final['finite_bridge'];a=final['a'];k=final['kappa']
    def modified(change):
        out=copy.deepcopy(finite);change(out);return out
    reject('overstated_uniform_supplier',lambda:arithmetic.validate_shared_bridge(modified(lambda x:x['bit_uniform'].update(ordinary_saving=moment['ordinary_saving']+Q(1,10**24))),cr))
    prior=atom-Q(1,10**24)
    reject('unpaid_previous_atom',lambda:arithmetic.validate_shared_bridge(modified(lambda x:x['bit_uniform'].update(atom_beta=prior,ordinary_saving=(1-prior)*coarse+prior*arithmetic.OLD)),cr))
    reject('next_final_grid',lambda:arithmetic.assembly(finite,cr,a,k+Q(1,10**18),beta=arithmetic.BETA,h=arithmetic.ETA,a_complex=arithmetic.AC))
    return js(dict(status='PASS conditional finite successor',kappa=k,prerequisite_kappa=retained['kappa'],
        profile=row,formal=formal,prime_witnesses=prime,paid_moment=moment,assembly=final,
        retained_complex_certificate_sha256=digest(base/'certificate.json'),
        retained_complex_profile=cr,retained_controls=old_arithmetic['adverse_controls'],controls=controls,
        scope='Finite frame word, exact determinant factors, paid moment and 47 strict assembly constraints. The source-specified all-size Clifford/tensor, weighted bit, internal rows, paid balanced layout, analytic recovery and fixed-tape contracts remain assumptions.'))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',type=Path,default=HERE.parents[1]);p.add_argument('--write',action='store_true');args=p.parse_args()
    assert not sys.flags.optimize
    before=pins(args.source);record=build(args.source);target=HERE/'certificate.json'
    if args.write:target.write_text(json.dumps(record,sort_keys=True,indent=2)+'\n')
    else:assert record==json.loads(target.read_text()),'Canonical successor certificate changed'
    assert pins(args.source)==before,'Source closure changed during verification'
    print('PASS paired-cube-bit-descent; kappa=5.94035602295411e-4; 1464 frame descents; all formal columns; 47 constraints; seven margins.')

if __name__=='__main__':main()
