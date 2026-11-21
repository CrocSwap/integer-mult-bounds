#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact extremal integer h for one frozen normalized logarithmic bound."""
from argparse import ArgumentParser
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import signal

OLD = 'bb3f7384b8c17a396256c32d78cf8efa6a0270bb82988fa694a950f17b7f0bed'
BIT = '538b785f93517b41229186e9070281d240f5d506f80a7e1ed705dd91c68f8749'
TICK = F(1,10**14)


def ensure(ok, message):
    if not ok:
        raise ValueError(message)


def pinned_json(path, expected):
    raw = path.read_bytes()
    ensure(sha256(raw).hexdigest() == expected, path.name)
    return json.loads(raw)


def evaluate(producer):
    bit = pinned_json(producer / 'BIT-451.json', BIT)
    old = pinned_json(Path(__file__).with_name('RESULT.json'), OLD)
    theorem = Path(__file__).with_name('SHIFTED-LOG.md')
    ensure(sha256(theorem.read_bytes()).hexdigest() == '04eba2e0a2a6cdd4ee512254142cbe45e647a73b66ad67b2c1c0a62e0883238a', 'theorem pin')
    h0, p, theta, H = old['h'], old['p'], F(old['theta']), old['H']
    C = F(bit['separation']['trial'])
    v = bit['partition']['factors']
    require_stock = (v, H, h0, p, theta, C)
    ensure(require_stock == (451,1202400000000000,1024,60,F(13,15),F('.003879928046148')), 'frozen geometry')
    A, r, k = 134**v,11**v,16**v
    a,b = theta.numerator,theta.denominator
    ensure(r**b < k**a and theta**p < F(bit['uniform']['eta'][0]), 'old exit and capacity conditions')

    # 2^((b-a)*h) <= A^a/r^b. Both sides can be compared after flooring the ratio.
    quotient = A**a // r**b
    floor_log = quotient.bit_length()-1
    h = floor_log//(b-a)
    shift = 1 << ((b-a)*h)
    ensure(shift <= quotient < shift << (b-a), 'two adjacent scale endpoints')
    # log2(A) >= floor_log_A; this one rational lower endpoint suffices even
    # at the least favorable h. The base endpoint decreases as h increases.
    floor_log_A = A.bit_length()-1
    ambient_upper = F(bit['uniform']['ambient_power'][1])
    ensure(ambient_upper < (1+F(floor_log_A,h))**p, 'all base ranks for every permitted scale')
    # Strict loss inequality (1+H/h)^p < 2^J; exact integer division handles
    # equality to a power of two by returning the next larger integer.
    numerator = (h+H)**p
    denominator = h**p
    J = (numerator//denominator).bit_length()
    ensure((denominator << (J-1)) <= numerator < (denominator << J), 'minimum integral uniform budget')
    e = F(J,H)
    ensure(e*(H+1)>2*p, 'uniform tail throughout the permitted scale range')
    d = F(old['charged_cover_loss'])
    ensure(d==F(1,H*2**44) and F(bit['cover_and_stock']['bad_surcharge_upper'])<H*d/2,'fixed cover')
    rate = C-e-d
    rho = F(bit['cover_and_stock']['rho'])
    last = F(bit['cover_and_stock']['seed'])
    steps=[]
    for _ in range(7):
        envelope = (1-rho)*rate+rho*last
        scale=10**24
        step = F((scale*envelope).__floor__()-1,scale)
        ensure(last<step<envelope<rate<rho<1-envelope,'all three root terms')
        steps.append([str(last),str(step),str(envelope-step)])
        last=step
    cap = F((10**17*last).__floor__(),10**17)
    claim = (cap//TICK-8)*TICK
    tested = claim+7*TICK
    old_rate = F(old['candidate_grid_claim'])
    native_upper = F(bit['raw_crossing'][1])
    generous = native_upper-F(old['uniform_loss'])-7*TICK
    ensure(cap>tested>claim>generous>old_rate,'separation of complete fixed-loss analyses')
    return dict(pins={'BIT-451.json':BIT,'RESULT.json':OLD},
                predecessor='f1649c6ddc1e2e1b6bf4b63118512ba08332fa38',
                fixed_power=p,theta=str(theta),H=H,integer_h_interval=[1,h],
                shift_midpoint_log_floor=floor_log,
                shift_boundaries=[[h,True],[h+1,False]],floor_log2_ambient=floor_log_A,
                base_guard_count=1,uniform_integer_J_minimum=J,uniform_J_rejected=J-1,
                uniform_loss=str(e),charged_cover_loss=str(d),covered=str(rate),stages=steps,
                cap=str(cap),candidate_tested=str(tested),candidate_grid_claim=str(claim),
                previous_claim=str(old_rate),absolute_gain=str(claim-old_rate),
                exact_relative_percent=str(100*(claim-old_rate)/old_rate),
                old_cover_forgiven_upper=str(generous),separation=str(claim-generous))


def bind(result, directory):
    receipt=json.loads((directory/'receipt.json').read_bytes())
    app=json.loads((directory/'APPLICATION.json').read_bytes())
    audit=json.loads((directory/'AUDIT.json').read_bytes())
    ensure(F(receipt['cap'])==F(app['binary_ordinary'])==F(audit['outer']['pinned_binary_cap'])==F(result['cap']),'cap binding')
    ensure(F(receipt['claim'])==F(app['application']['claim'])==F(result['candidate_grid_claim']),'claim binding')
    ensure(F(receipt['tested'])==F(audit['outer']['finite_compiler']['tested'])==F(result['candidate_tested']),'tested binding')
    for name in ('APPLICATION.json','AUDIT.json'):
        ensure(sha256((directory/name).read_bytes()).hexdigest()==receipt['output_sha256'][name],name)


if __name__=='__main__':
    signal.alarm(60)
    parser=ArgumentParser(description=__doc__)
    parser.add_argument('producer',type=Path)
    parser.add_argument('out',type=Path)
    parser.add_argument('--outer',type=Path)
    args=parser.parse_args()
    result=evaluate(args.producer)
    if args.outer:
        bind(result,args.outer)
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print('PASS_451_INTEGER_SCALE_ENDPOINT',result['integer_h_interval'],result['uniform_integer_J_minimum'],result['candidate_grid_claim'])
