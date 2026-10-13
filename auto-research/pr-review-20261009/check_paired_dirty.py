#!/usr/bin/env python3
"""Independent arbitrary-dirty signed-word controls for regenerated PR144.

Apache-2.0, maintainer review with OpenAI Codex assistance. Reads the actual
regenerated graph/word. Tests scalar values, not the tape implementation.
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
from fractions import Fraction
import json
from pathlib import Path
import random


def check(folder):
    graph = json.loads((folder/'graph.json').read_text())
    word = json.loads((folder/'selection.json').read_text())
    v,R = len(graph['inputs']), max(max(op[:2]) for op in word['ops'])+1
    assert v==1760 and R==26417
    operations = list(zip(word['ops'],word['opcoeff']))
    # A two-variable symbolic inverse check for every actual gate type.
    types = set(map(tuple,word['opcoeff']))
    for ca,cb in types:
        assert ca*ca==1 and ca*cb-ca*cb==0
    def forward(values):
        for (a,b,_),(ca,cb) in operations:
            values[a] = ca*values[a]+cb*values[b]
    def inverse(values,wrong=False):
        for (a,b,_),(ca,cb) in reversed(operations):
            values[a] = ca*values[a]+(cb if wrong else -ca*cb)*values[b]
    def decoder6(values):
        result = [0]*v
        for root,slot in zip(graph['roots'],word['rootroles']):
            for target,coeff in zip(root['targets'],root['coefficients']):
                c=6*Fraction(coeff)
                assert c.denominator==1
                result[target] += c.numerator*values[slot]
        return result
    def K6(values):
        result = [0]*v
        for start in range(0,v,8):
            for i in range(start,start+8):
                for j in range(start,start+8):
                    distance=(graph['inputs'][i]^graph['inputs'][j]).bit_count()
                    sign=1 if distance==6 else -1 if distance==2 else 0
                    result[i] += 3*sign*values[j]
        return result
    rng=random.Random(144)
    rejected=0
    for trial in range(3):
        initial=[rng.randrange(-9,10) for _ in range(R)]
        x=[rng.randrange(-9,10) for _ in range(v)]
        y=[rng.randrange(-9,10) for _ in range(v)]
        mz=initial[:];forward(mz)
        yz=[6*t-d for t,d in zip(y,decoder6(mz))]
        z=initial[:]
        for node,slot in word['sources'].items():z[slot]+=x[int(node)-1]
        forward(z)
        yz=[a+b+c for a,b,c in zip(yz,decoder6(z),K6(x))]
        bad=z[:];inverse(bad,wrong=True)
        inverse(z)
        for node,slot in word['sources'].items():
            z[slot]-=x[int(node)-1]
            bad[slot]-=x[int(node)-1]
        assert z==initial and yz==[6*(a+b) for a,b in zip(y,x)]
        rejected+=int(bad!=initial)
    assert rejected==3
    return dict(status='PASS',full_dirty_vectors=3,roles=R,source_ports=v,
                physical_mixer_operations=len(operations),same_sign_inverse_rejected=rejected,
                scalar_gate_types=sorted(types),
                scope='Actual signed word on arbitrary dirty integer vectors; finite scalar control, not a Fourier/tape proof')


if __name__=='__main__':
    print(json.dumps(check(Path(sys.argv[1])),indent=2))
