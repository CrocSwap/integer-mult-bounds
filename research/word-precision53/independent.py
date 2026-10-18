"""Independent finite scalar-corner audit; no imports from either implementation."""
import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path

P = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def affine(word, n, initial):
    # Each row is a formal expression in the n initial values and one fresh
    # error symbol per stage. This retains separate injections, not one max.
    rows = [[F(i == j) for j in range(n)] + [F(0)]*len(word) for i in range(n)]
    trace = []
    for k, (s,t,a,sign) in enumerate(word):
        rows[t] = [x+a*y for x,y in zip(rows[t],rows[s])]
        rows[t][n+k] = 1
        trace.append(dict(magnitude=[str(sum(row[:n])*initial+sum(row[n:])) for row in rows],
                          error_units=[str(sum(row[n:])) for row in rows]))
    return trace


def main():
    receipt = json.loads((P/'EXPECTED.json').read_text())
    fwd = receipt['source_stages']
    whole = fwd + [[s,t,k,-z] for s,t,k,z in reversed(fwd)]
    comparisons = 0
    for case in receipt['cases']:
        beta=F(case['beta']); norms=[3/beta**2,2/beta**2]
        trace=affine([(s,t,norms[k],z) for s,t,k,z in whole],3,F(1))
        need(trace == case['prefix_trace'], 'source fixture expression expansion')
        units=max(map(F,trace[-1]['error_units']))
        bits=int(case['new']['coarse_bits'])
        need(2*units <= 2**(bits-40), 'fixture coarse bound')
        need(2*units > 2**(bits-1-40), 'fixture minimal coarse guard')
        comparisons+=len(trace)
    # Bounded audit, not the all-word proof: every signed two-port word
    # through four stages, norms 1 or 3, all +-1 initial corners and errors.
    alphabet=[(s,1-s,a,z) for s in (0,1) for a in (1,3) for z in (-1,1)]
    words,executions,sharp=0,0,0
    for length in range(1,5):
        for word in itertools.product(alphabet,repeat=length):
            trace=affine(word,2,F(1)); words+=1
            for start in itertools.product((-1,1),repeat=2):
                for defects in itertools.product((-1,1),repeat=length):
                    actual=list(start); ideal=list(start)
                    for k,(s,t,a,z) in enumerate(word):
                        actual[t]+=z*a*actual[s]+defects[k]
                        ideal[t]+=z*a*ideal[s]
                        for j in (0,1):
                            need(abs(actual[j])<=F(trace[k]['magnitude'][j]),'scalar magnitude')
                            need(abs(actual[j]-ideal[j])<=F(trace[k]['error_units'][j]),'scalar error')
                    executions+=1
            if all(z==1 for s,t,a,z in word):
                actual=[1,1]; ideal=[1,1]
                for s,t,a,z in word:
                    actual[t]+=a*actual[s]+1;ideal[t]+=a*ideal[s]
                need(list(map(str,actual))==trace[-1]['magnitude'],'positive magnitude saturation')
                need([str(x-y) for x,y in zip(actual,ideal)]==trace[-1]['error_units'],'positive error saturation')
                sharp+=1
    need((words,executions,sharp,comparisons)==(4680,279616,340,240),'finite inventory')
    print('PASS_INDEPENDENT53 words=%d corner_executions=%d sharp_words=%d fixture_prefixes=%d' %
          (words,executions,sharp,comparisons))


if __name__=='__main__':main()
