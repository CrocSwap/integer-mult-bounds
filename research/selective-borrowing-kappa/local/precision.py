"""All-cut noncancellation Hilbert-norm envelope for literal local words.

This establishes a sufficient implication under an explicit completed-instruction
defect contract. It does not instantiate rounded recursive children or an all-size
stock/row envelope. Native Clifford factors and monomial adapters are unitary.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

def need(ok,label):
    if not ok:raise ValueError(label)

def binary_ceiling(x):
    need(x>0,'positive norm bound')
    power=max(0,x.numerator.bit_length()-x.denominator.bit_length())
    while Q(2)**power<x:power+=1
    need(x<=Q(2)**power,'exact binary majorant')
    return power

def expanded(events):
    for e in events:
        if e[0]!='swap':yield e;continue
        _,d,s,F=e
        yield ['add',d,s,'1',F]
        yield ['add',s,d,'-1',F]
        yield ['add',d,s,'1',F]
        yield ['scale',s,'-1',F]

def primitive_expansion(trace):
    """Literal Horner arithmetic using one owned complex coefficient-work row."""
    used=set(trace['active_registers'])
    for e in trace['events']:
        if len(e)>1 and type(e[1]) is int:used.add(e[1])
    work=max(used)+1
    yield ['zero_buffer',work,[],trace['active_registers'][0]]
    for e in expanded(trace['events']):
        kind=e[0]
        if kind=='add':
            _,target,source,q,F=e;q=Q(q);a,b=abs(q.numerator),q.denominator
            need(a>0 and b&(b-1)==0,'dyadic Horner coefficient')
            yield ['clear',work,F]
            for index,bit in enumerate(bin(a)[2:]):
                if index:yield ['scale',work,'2',F]
                if bit=='1':yield ['add',work,source,'1',F]
            for _ in range(b.bit_length()-1):yield ['scale',work,'1/2',F]
            yield ['add',target,work,str(1 if q>0 else -1),F]
            yield ['clear',work,F]
        elif kind=='scale':
            _,r,q,F=e;q=Q(q);a,b=abs(q.numerator),q.denominator
            need(a>0 and a&(a-1)==0 and b&(b-1)==0,'power-of-two scalar unit')
            if q<0:yield ['scale',r,'-1',F]
            power=a.bit_length()-b.bit_length()
            for _ in range(abs(power)):yield ['scale',r,'2' if power>0 else '1/2',F]
        else:yield e
    # The explicit implementation postlude clears every owned array exactly.
    private={e[1] for e in trace['events'] if e[0] in ('copy','zero_buffer')}
    for r in sorted(private):yield ['clear',r,[]]
    yield ['clear',work,[]]

def calculate(trace):
    ideal={r:Q(1) for r in trace['active_registers']}
    errors={r:Q(0) for r in trace['active_registers']}
    P,K=Q(1),Q(0);peakP=peakK=None;count=0
    for index,e in enumerate(primitive_expansion(trace)):
        count+=1;kind=e[0];r=e[1]
        if kind=='add':
            q=abs(Q(e[3]));s=e[2]
            ideal[r]+=q*ideal[s];errors[r]+=q*errors[s];local=2*(1+q)
        elif kind=='scale':
            q=abs(Q(e[2]));ideal[r]*=q;errors[r]*=q;local=2*max(Q(1),q)
        elif kind=='copy':
            s=e[2];ideal[r]=ideal[s];errors[r]=errors[s];local=Q(1)
        elif kind in ('clear','zero_buffer'):
            # Writing the exact zero bit-pattern incurs no numerical rounding.
            ideal[r]=errors[r]=Q(0);local=Q(0)
        elif kind in ('transport','handoff','logical_monomial','dual_handoff','dual_monomial','zero_reframe'):
            # Physical native factors are unitary; zero reframe is literal identity.
            need(r in ideal,'allocated physical stream')
            local=Q(1)
        else:raise ValueError(('unsupported physical instruction',kind))
        errors[r]+=local
        if ideal[r]>P:P=ideal[r];peakP=[index,r]
        if errors[r]>K:K=errors[r];peakK=[index,r]
    p,k=binary_ceiling(P),binary_ceiling(K)
    guard=p+k+3
    u=Q(1,2**guard)
    need(K*u<Q(1,2),'feedback contraction at b=0')
    need(K*u*P/(1-K*u)<1,'unit precision target at b=0')
    return dict(status='PASS_ALL_CUT_NONCANCELLATION_ENVELOPE',instructions_after_horner_and_swap_expansion=count,
        ideal_prefix_P=str(P),uniform_completed_instruction_defect_K=str(K),
        P_binary_upper=p,K_binary_upper=k,local_sufficient_guard_bits=guard,
        ideal_peak=peakP,error_peak=peakK,
        completed_instruction_defect_contract='For each completed recursive unitary/COPY step, Hilbert defect <= u times maximum current stream norm. Each real arithmetic primitive has defect <= u times its row norm times that maximum; the envelope charges a factor two when combining the real and imaginary components. All compound ADD coefficients are expanded through an actual owned Horner work row; SCALE and SWAP are expanded to their real primitives. Exact clear/zero allocation writes zero.',
        sufficient_implication='For every b >= 0 and initial maximum stream norm B >= 0, u <= 2^(-b-guard) gives every-cut error <= B*2^(-b), strictly when B > 0. At B=0 the stated relative-defect contract forces exact zero.',
        proof='The nonnegative recurrence bounds every ideal state by P*B and every sequence of uniform unit defects by K at every cut. For E the maximum actual error, linear propagation gives E <= K*u*(P*B+E). Since K*u < 1/2, E <= K*u*P*B/(1-K*u). The recorded dyadic guard makes this less than B*2^(-b).',
        scope='Finite local conditional precision implication only. This is neither a rounded-child implementation nor selected global stock/row or all-size admission.')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('trace',type=Path);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();trace=json.loads(args.trace.read_bytes());result=calculate(trace)
    result['trace_sha256']=hashlib.sha256(args.trace.read_bytes()).hexdigest()
    args.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(result['status'],'P<=2^'+str(result['P_binary_upper']),'K<=2^'+str(result['K_binary_upper']),'guard',result['local_sufficient_guard_bits'])
