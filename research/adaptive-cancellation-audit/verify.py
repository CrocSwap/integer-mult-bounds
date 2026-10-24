#!/usr/bin/env python3
"""Exact independent audit of the sharp cancellation step. Apache-2.0.

OpenAI assistance for Chris R / Clear1nsight. No predecessor acceptance function
is imported. Rational fixtures test the universal argument in PROOF.md.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE='research/rank-convergence/PROOF.md'
BLOB='75f451837204bd141f357e7f5e5d6c6f42e1423e'

def need(ok,why):
    if not ok: raise ValueError(why)

def authenticate():
    path=ROOT/SOURCE
    need(path.is_file() and not path.is_symlink(),'Missing or aliased source')
    data=path.read_bytes()
    need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==BLOB,'Changed proof source')
    return hashlib.sha256(data).hexdigest()

def validate(beta,eta,I,B,F,A):
    need(0<=beta<eta<1,'Ordered contraction domain')
    need(min(I,B,F,A)>=0,'Nonnegative potentials')
    need(I==B+F+A,'Actual source/exit cancellation')
    need(B<=beta*I,'Pointwise mirror premise')

def audit(beta,eta,I,B,F,A):
    validate(beta,eta,I,B,F,A)
    margin=(eta-beta)*A-(1-eta)*F
    mirror=beta*I-B
    lhs=(1-beta)*(eta*I-B-F)
    rhs=margin+(1-eta)*mirror
    need(lhs==rhs,'Exact nonnegative-slack identity')
    if margin>=0:need(B+F<=eta*I,'Sufficient cancellation implication')
    if A+F:
        bound=(beta*A+F)/(A+F)
        need((B+F)/I<=bound,'Sharp maximal exit fraction')
    else:need(I==B==F==A==0,'Zero-mass endpoint')
    return margin

def extremal(beta,A,F):
    need(0<=beta<1 and A>=0 and F>=0,'Extremal domain')
    I=(A+F)/(1-beta);B=beta*I
    return I,B

def controls():
    checks=0; sharp=0; zero=0
    for den in range(2,10):
        for bi in range(den-1):
            for ei in range(bi+1,den):
                beta,eta=Q(bi,den),Q(ei,den)
                for A in map(Q,(0,1,2,7)):
                    for F in (Q(0),Q(1,3),Q(1),Q(5)):
                        Imax,Bmax=extremal(beta,A,F)
                        for weight in (Q(0),Q(1,3),Q(1)):
                            B=weight*Bmax;I=B+A+F
                            audit(beta,eta,I,B,F,A);checks+=1
                        if A+F:
                            need((Bmax+F)/Imax==(beta*A+F)/(A+F),'Extremiser attainment');sharp+=1
                        else:zero+=1
                F=Q(1);threshold=(1-eta)/(eta-beta)
                for A,should_pass in ((threshold,True),(threshold*Q(3,4),False),(threshold+1,True)):
                    I,B=extremal(beta,A,F)
                    need((audit(beta,eta,I,B,F,A)>=0)==should_pass,'Threshold direction')
                    need((B+F<=eta*I)==should_pass,'Necessary threshold in extremal family');checks+=1
    bad=[(Q(1,2),Q(1,2),Q(0),Q(0),Q(0),Q(0)),
         (Q(1,4),Q(1,2),Q(1),Q(0),Q(2),Q(-1)),
         (Q(1,4),Q(1,2),Q(2),Q(0),Q(1),Q(0)),
         (Q(1,4),Q(1,2),Q(2),Q(1),Q(0),Q(1))]
    for case in bad:
        try:audit(*case)
        except ValueError:pass
        else:raise ValueError('Invalid premise accepted')
    beta,eta=Q(1,4),Q(1,2)
    G,R,F=Q(2),Q(1,2),Q(1);A=G-R;I,B=extremal(beta,A,F)
    need((eta-beta)*G==(1-eta)*F,'Root omission false positive calibration')
    need(audit(beta,eta,I,B,F,A)<0 and (B+F)/I==Q(11,20),'Root debit counterexample')
    A,F=Q(0),Q(1);I,B=extremal(beta,A,F)
    need((eta-beta)*A>=0 and audit(beta,eta,I,B,F,A)<0,'Leaf omission counterexample')
    for beta,eta in ((Q(0),Q(1,2)),(Q(1,4),Q(1,2)),(Q(3,4),Q(7,8))):
        for A,F,B in ((Q(1),Q(0),Q(0)),(Q(0),Q(1),Q(0)),(Q(0),Q(0),Q(1))):
            I=B+F+A
            need((1-beta)*(eta*I-B-F)==(eta-beta)*A-(1-eta)*F+(1-eta)*(beta*I-B),'Linear coefficient control')
    return dict(rational_positive_cases=checks,extremal_attainments=sharp,zero_mass_cases=zero,
                invalid_premises_rejected=len(bad),root_omission_exit_fraction='11/20',
                root_omission_required_fraction='1/2',leaf_omission_rejected=True,
                linear_coefficient_cases=9)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');ap.add_argument('--write',action='store_true');args=ap.parse_args()
    result=dict(schema='adaptive-cancellation-audit/v1',status='PASS_SHARP_CANCELLATION_AUDIT',
                source_blob=BLOB,controls=controls(),new_kappa=False,
                universal_argument='PROOF.md, exact slack identity and explicit extremisers',
                not_covered=['Chernoff occupation and root bounds','mirror guard certification','native and physical premises','majorant funding','new compiler rank or outer theorem'])
    if not args.self_test: result['source_sha256']=authenticate()
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:(HERE/'RESULT.json').write_text(text)
    elif not args.self_test and (HERE/'RESULT.json').exists():need(json.loads((HERE/'RESULT.json').read_bytes())==result,'Receipt changed')
    print(text,end='')

if __name__=='__main__':main()
