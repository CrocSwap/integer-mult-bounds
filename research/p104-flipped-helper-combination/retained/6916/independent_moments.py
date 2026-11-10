#!/usr/bin/env python3
"""Independent rational moment check; no construction or interval imports.

Recounts the literal native/caller invoice. Rational logarithm bounds use
atanh series after power-of-two range reduction. Alternating exponential
series give certified moments; floating point appears only in diagnostics.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import argparse, gzip, json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def log_unit(x):
    z = (x - 1) / (x + 1)
    need(0 <= z <= F(1, 3), 'log range')
    terms = 48
    total = 2 * sum((z ** (2*j+1) / (2*j+1) for j in range(terms)), F(0))
    tail = 2 * z ** (2*terms+1) / ((2*terms+1) * (1-z*z))
    return total, total + tail


def log_bounds(n):
    need(type(n) is int and n >= 1, 'positive rank')
    s = n.bit_length()-1
    a,b = log_unit(F(n, 2**s))
    c,d = log_unit(F(2))
    return a+s*c, b+s*d


def exponential_partial(t, terms):
    need(0 <= t < 1, 'alternating exponential domain')
    value = current = F(1)
    for j in range(1, terms+1):
        current *= -t / j
        value += current
    return value


def exp_interval(a,b):
    # exp(-t) decreases in t; odd/even partial sums bracket exp(-t).
    need(0 <= a <= b < 1, 'exponential interval')
    return exponential_partial(b,35), exponential_partial(a,36)


def signed_moment(signed, saving, logs):
    low = high = F(0)
    for rank, coefficient in signed.items():
        a,b = logs[rank]
        l,u = exp_interval(saving*a,saving*b)
        l *= rank; u *= rank
        low += coefficient*(l if coefficient >= 0 else u)
        high += coefficient*(u if coefficient >= 0 else l)
    return low,high


def invoice(word,caller):
    dims = list(map(len,word['frames']))
    main = set(word['live']) | {r+112 for r in word['live']} | set(word['hosted']['X2']) | set(word['hosted']['Y2'])
    need(len(main)==416 and len(word['ports'])==104, 'source main/port inventory')
    helper = Counter(dims[b]-dims[a] for r,(a,b) in enumerate(zip(word['initial'],word['final'])) if r not in main)
    moves = Counter(abs(dims[e[3]]-dims[e[2]]) for e in word['program'] if e[0]=='MOVE')
    need(min(helper)>0 and min(moves)>0, 'positive native jobs')
    targets,paid = Counter(),Counter()
    stages = []
    for e in caller['events']:
        if e[0]=='HOST2':
            stages.append(e[1]); targets.update(helper); paid.update(moves)
        elif e[0]=='QUERY':
            need(e[3] in (-1,1), 'odd thin query')
            paid[1]+=104
        elif e[0]=='IDLE_ONE':
            need(e[2] and len(set(e[2]))==len(e[2]), 'distinct idle axes')
            paid[8*len(e[2])]+=104
        else:
            need(e[0] in ('ADD','SCALE','SWAP','LAMBDA'),'priced opcode')
    need(sorted(stages)==list(range(1,19)), 'one host per stage')
    for q,z,*mask in caller['diagonal']:
        need(z==0 and len(mask)==18 and all(x in (0,1) for x in mask),'target mask')
        targets[(q%2)+8*sum(mask)]+=104
    return targets,paid


def check(word, caller, claim):
    t,p = invoice(word,caller)
    signed = Counter(t);signed.subtract(p)
    logs={r:log_bounds(r) for r in signed}
    expected_mass=sum(r*c for r,c in signed.items())
    need(expected_mass==1520,'unchanged rank surplus')
    result={}
    for name in ('kappa','tested','raw_lower','raw_upper'):
        a,b=signed_moment(signed,F(claim[name]),logs)
        need(b<0 if name=='raw_upper' else a>0,'certified sign '+name)
        result[name]={'saving':claim[name],'lower_sign':1 if a>0 else -1,'upper_sign':1 if b>0 else -1,'diagnostic_lower':float(a),'diagnostic_upper':float(b)}
    pin=F('.00376669'); upper=F(0)
    for rank,c in signed.items():
        a,b=logs[rank]
        el,eu=exp_interval(pin*a,pin*b)
        upper += -c*rank*el*a if c>=0 else -c*rank*b
    need(upper<0,'strictly decreasing signed moment on the whole pin interval')
    return {'targets':dict(sorted(t.items())),'paid':dict(sorted(p.items())),'productive_fields':sum(t.values()),'paid_jobs':sum(p.values()),'rank_surplus':expected_mass,'moments':result,'derivative_upper_diagnostic':float(upper),'certified_derivative_negative':True}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--word',required=True);ap.add_argument('--caller',required=True);ap.add_argument('--claim-file',required=True);ap.add_argument('--output');args=ap.parse_args()
    result=check(read(args.word),read(args.caller),read(args.claim_file)['claim'])
    if args.output:Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True));print('PASS_INDEPENDENT_LITERAL_MOMENT')


if __name__=='__main__':main()
