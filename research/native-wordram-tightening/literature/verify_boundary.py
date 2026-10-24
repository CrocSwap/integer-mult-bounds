"""Exact arithmetic controls for the positive universal boundary transfer."""
from fractions import Fraction as F
import json


def construct(c,qc,kappa):
    if not (0<c<F(1,2) and qc>0 and 0<kappa<min(qc,c)):
        raise ValueError("parameters outside the proved open range")
    q=(kappa+min(qc,c))/2
    delta=min(F(1,100),(q-kappa)/(4*(q+1)),(c-q)/16,(F(1,2)-c)/4)
    epsilon=1-delta; beta=1-3*delta; layout=delta/100
    xi=epsilon*(1+q)-c+layout; rg=delta/10
    stop=(qc-q)/(2*qc)
    slacks=[qc*(1-stop)-q,delta,1-epsilon-rg,xi-F(1,2),epsilon-xi,1-(beta+2*xi-2+rg)]
    savings=[epsilon*q,F(1),1-epsilon+q*beta,F(1),1-epsilon+beta,c+xi-epsilon,F(1,2)+xi-epsilon,epsilon,79-epsilon-beta]
    if slacks[-1] != 2*(c-q)+delta*(F(122,25)+2*q):
        raise ValueError("chirp guard identity failed")
    if not all(s>0 for s in slacks) or not all(s>kappa for s in savings):
        raise ValueError("positive guard or complete-row margin failed")
    return q,delta,min(s-kappa for s in savings)


def main():
    if not 7**125 < 2**351:
        raise ValueError("Strassen rational ceiling certificate failed")
    count=above_third=0; minmargin=None
    for c in [F(3,32),F(12,125),F(1,4),F(3,8),F(49,100),F(499,1000)]:
        for qc in [F(1,10**8),F(30217758,10**10),F(156,10**4),F(1,3),F(2,5),F(1,2),F(3,4)]:
            for part in [F(1,1000),F(1,3),F(99,100),F(999999,10**6)]:
                kappa=part*min(c,qc);q,delta,margin=construct(c,qc,kappa)
                above_third += q>F(1,3); count+=1
                minmargin=margin if minmargin is None else min(minmargin,margin)
    rejected=0
    for args in [(F(1,2),F(1,4),F(1,8)),(F(1,4),F(1,8),F(1,8)),(F(1,4),F(0),F(1,8)),(F(1,4),F(1,8),F(0))]:
        try:construct(*args)
        except ValueError:rejected+=1
        else:raise ValueError("strict boundary control was accepted")
    print(json.dumps({"status":"PASS_FIXED_BILINEAR_BOUNDARY_TRANSFER","exact_cases":count,"q_above_one_third_cases":above_third,"rejected_boundary_controls":rejected,"minimum_nine_row_margin":str(minmargin),"strassen_exact_certificate":"7^125 < 2^351","new_kappa_established":False},sort_keys=True))


if __name__ == "__main__":main()
