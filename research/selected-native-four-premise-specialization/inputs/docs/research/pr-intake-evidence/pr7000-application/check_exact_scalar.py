#!/usr/bin/env python3
"""Finite-control exact fixed-rational scalar construction and source census.

Executable bit-state reference, not a whole tape machine. The written review
accounts for scans, signs, staging and complete field returns. Apache-2.0;
prepared with OpenAI Codex assistance for Douglas Colkitt.
"""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from hashlib import sha256
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = (ROOT/path).read_bytes()
    pins = json.loads((HERE/'SOURCES.json').read_text())['files']
    need(sha256(raw).hexdigest()==next(p['sha256'] for p in pins if p['path']==path), 'source hash')
    return json.loads(gzip.decompress(raw) if path.endswith('.gz') else raw)


def encode(x, width):
    need(0 <= x < 2**width, 'unsigned input fit')
    return [(x >> i) & 1 for i in range(width)]


def decode(row):
    return sum(v << i for i,v in enumerate(row))


def multiply(row, coefficient):
    """LSB first fixed carry transducer; coefficient is compiled control data."""
    need(coefficient >= 0, 'nonnegative fixed multiplier')
    carry = 0
    out = []
    for bit in row + [0]*(coefficient.bit_length()+1):
        value = carry + coefficient*bit
        out.append(value & 1); carry = value >> 1
        need(0 <= carry <= coefficient, 'finite multiplier carry state')
    need(carry == 0, 'complete product including high guard bits')
    return out


def divide_exact(row, divisor):
    """MSB first fixed remainder transducer; no rounded odd division."""
    need(divisor > 0, 'positive fixed divisor')
    remainder = 0
    out = []
    for bit in reversed(row):
        value = 2*remainder + bit
        digit = int(value >= divisor)
        remainder = value-divisor*digit
        need(0 <= remainder < divisor, 'finite division remainder state')
        out.append(digit)
    need(remainder == 0, 'nonzero exact-division remainder')
    return out[::-1]


def rational(x, coefficient, width):
    q = Q(coefficient)
    result = divide_exact(multiply(encode(abs(x),width), abs(q.numerator)),q.denominator)
    return (-1 if (x < 0) != (q.numerator < 0) else 1)*decode(result)


def main():
    prefix='research/shared-wire-split-composition/'
    word=read(prefix+'data/final.json.gz'); caller=read(prefix+'data/caller.json')
    scalars=Counter()
    local_sites=Counter(e[0] for e in word['program'])
    for e in word['program']:
        if e[0] in ('ADD','COPY','SCALE'):
            scalars[str(Q(e[2] if e[0]=='SCALE' else e[3]))] += 18
    caller_sites=Counter()
    for e in caller['events']:
        if e[0]=='J':continue
        ty,op,*a=e; ports=len(caller['types'][ty]['ports']);caller_sites[op]+=ports
        if op in ('ADD','SCALE'):
            scalars[str(Q(a[2] if op=='ADD' else a[1]))]+=ports
    # Input/output per-call conversions and LAMBDA's fixed half coefficients.
    scalars['1125']+=18*word['public'];scalars['1/1125']+=18*word['public']
    scalars['1/2']+=2*caller_sites['LAMBDA']
    need(max(abs(Q(q).numerator).bit_length() for q in scalars)<=24, 'source numerator bound')
    need(max(Q(q).denominator.bit_length() for q in scalars)<=19, 'source divisor bound')
    tests=rejected=0
    for spelling in scalars:
        q=Q(spelling);b=q.denominator
        for width in (1,7,25,65):
            limit=(2**width-1)//b
            for multiple in sorted({0,1 if limit else 0,limit//2,limit}):
                x=multiple*b
                for sign in (-1,1):
                    got=rational(sign*x,q,width)
                    need(got==sign*x*q, 'bit-state rational result')
                    need(abs(got)<2**(width+24), 'temporary multiplication bound')
                    tests+=1
        if b>1:
            try:divide_exact(encode(1,max(1,b.bit_length())),b)
            except ValueError as error:
                need(str(error)=='nonzero exact-division remainder','remainder guard');rejected+=1
            else:raise ValueError('nonexact division accepted')
    # Count complete scalar services conservatively, including real/imaginary
    # arithmetic, COPY-as-ADD, init/clear and all per-call conversions.
    native_events=18*sum(local_sites[k] for k in ('ADD','COPY','SCALE','INIT','CLEAR'))
    caller_events=sum(caller_sites.values())
    conversions=2*18*word['public']
    service_bound=32*(native_events+caller_events+conversions+1)
    need(service_bound<2**26, 'new finite scalar-service bound')
    # Each complete fixed-rational service has a deliberately loose 2^20
    # unit-bit transition allowance per padded component bit in the review's
    # explicit stream implementation. Routing is a separate retained tariff.
    print(json.dumps(dict(status='PASS_EXACT_FIXED_RATIONAL_SERVICES',
        source_scalar_coefficients=len(scalars),source_coefficient_digest=sha256(json.dumps(dict(sorted(scalars.items())),separators=(',',':')).encode()).hexdigest(),
        bit_state_cases=tests,nonexact_remainder_controls=rejected,
        native_scalar_admin_events=native_events,caller_events_expanded_by_port=caller_events,
        per_call_boundary_conversions=conversions,scalar_service_bound=service_bound,
        unit_bit_transition_bound_per_component_bit=2**20,
        raw_scalar_bit_transition_coefficient=service_bound*2**20,
        scope='Exact fixed-rational scan construction, conditional on common-grid divisibility. '
              'Reference tests use complete bit lists; tape-layout cost proof and inherited '
              'movement/storage interfaces are separate. No rounded-ADD provider substitution.'),indent=2))


if __name__=='__main__':main()
