#!/usr/bin/env python3
"""Exact finite controllers, independent semantics, source-bound exponent ledger."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from random import Random
import sys
import types

HERE = Path(__file__).resolve().parent


def load_local(name):
    module = types.ModuleType(name)
    module.__file__ = str(HERE/(name+'.py'))
    sys.modules[name] = module
    exec(compile((HERE/(name+'.py')).read_bytes(), module.__file__, 'exec'), module.__dict__)
    return module


sources = load_local('sources')
hierarchy = load_local('hierarchy')
need = sources.need
old, prior, gaussian = sources.authenticate()


def reference(program, source, target, projection):
    state = list(source)
    for op, dst, left, right in program:
        if op == 'set':
            result = left
        elif op == 'copy':
            result = state[left]
        elif op == 'not':
            result = 1-state[left]
        elif op == 'xor':
            result = (state[left]+state[right]) % 2
        elif op == 'and':
            result = state[left]*state[right]
        else:
            raise ValueError('reference opcode')
        state[dst] = result
    return [(a+state[j]) % 2 for a,j in zip(target,projection,strict=True)]


def program_fixture(size, steps):
    result = []
    for t in range(steps):
        j, k = t % size, (t+1) % size
        result.append((('set',j,t % 2,0), ('xor',j,j,k), ('and',j,j,k),
                       ('not',j,j,0), ('copy',j,k,0))[t % 5])
    return result


def controller_cases():
    cases, digest = 0, sha256()
    for size in range(1,4):
        for steps in (0,1,2,7,19):
            program = program_fixture(size,steps)
            for radix in (2,3):
                for height in range(4):
                    expected_invoice = hierarchy.expected_invoice(steps,size,radix,height)
                    for source_bits in product((0,1),repeat=size):
                        for target_bits in product((0,1),repeat=size):
                            source, target = list(source_bits),list(target_bits)
                            expected = reference(program,source,target,range(size))
                            invoice = hierarchy.evaluate(prior,program,source,target,radix,height)
                            need(source == list(source_bits) and target == expected, 'independent protected endpoint')
                            need(invoice == expected_invoice, 'complete hierarchical invoice')
                            hierarchy.evaluate(prior,program,source,target,radix,height)
                            need(target == list(target_bits), 'dirty XOR involution')
                            digest.update(bytes(expected))
                            cases += 1
    return dict(exhaustive_source_target_cases=cases, sha256=digest.hexdigest(),
                sizes=[1,2,3], steps=[0,1,2,7,19], radices=[2,3], heights=[0,1,2,3])


def plans():
    cases, digest = 0, sha256()
    for size in (1,2,7,31,128):
        for steps in range(257):
            for radix in range(2,7):
                p = hierarchy.relative_plan(steps,size,radix)
                h = p['height']
                need(size*radix**h >= steps and (h == 0 or size*radix**(h-1) < steps),
                     'minimal configuration-relative height')
                need(p['leaf_bound'] <= size, 'configuration-scale leaves')
                for height in range(5):
                    balance = hierarchy.balanced_plan(steps,size,height)
                    b = balance['radix']
                    need(size*b**(height+1) >= steps and
                         (b == 2 or size*(b-1)**(height+1) < steps), 'exact fixed-height balance')
                    invoice = hierarchy.expected_invoice(steps,size,radix,height)
                    p = hierarchy.shape(steps,size,radix,height)
                    C,L,Q = p['leaf_calls'],p['leaf_bound'],p['checkpoint_slots']*size
                    need(invoice['forward_steps'] <= C*L, 'weighted leaf work envelope')
                    need(invoice['checkpoint_moves'] <= 8*C*Q, 'complete bank-span routing envelope')
                    need(hierarchy.payload_work(invoice) <= C*(2*L+4*size+8*Q)+2*Q,
                         'complete finite payload-work envelope')
                    need(invoice['peak_clean_payload_bits'] == Q+size+L, 'allocated payload space')
                    digest.update(json.dumps((steps,size,radix,height,invoice),sort_keys=True).encode())
                    cases += 1
    # An input-volume control: scaling T and S equally must leave tree height
    # fixed; a unit-transition tree has an unwanted log N dependence.
    relative = [hierarchy.relative_plan(60*scale,scale,2)['height'] for scale in (1,2,16,256,4096)]
    unit = [hierarchy.relative_plan(60*scale,1,2)['height'] for scale in (1,2,16,256,4096)]
    need(len(set(relative)) == 1 and len(set(unit)) > 1, 'relative versus absolute hierarchy depth')
    return dict(integer_invoice_cases=cases, sha256=digest.hexdigest(),
                relative_heights=relative, unit_step_heights=unit,
                payload_work_bound='C*(2*L+4*S+8*Q)+2*Q',
                definitions='C=(2b-1)^H; L=ceil(T/b^H); Q=H*(b-1)*S')


def exponents():
    epsilon, spacing, sigma = Fraction(997,1000),Fraction(1,500),Fraction(599,600)
    # b=2^1200 gives log_b(2b-1)-1 < 1/1200, using integer inequalities only.
    radix = 1 << 1200
    need(radix < 2*radix-1 < 2*radix, 'strict branching power sandwich')
    alpha = Fraction(1,1200)
    old_time = 2-epsilon*(1-sigma)
    target = 2-epsilon/1200
    charges = dict(full_fast_groups=old_time+epsilon*sigma*alpha,
                   short_group=1+epsilon*(spacing+sigma)+epsilon*sigma*alpha,
                   narrow=1+epsilon*(1+alpha),
                   low_suffix=2-epsilon, tail=1+epsilon*spacing)
    need(all(exponent < target for exponent in charges.values()) and target < 2,
         'all charges leave a strict margin for log r')
    fixed = {str(H):str(1+epsilon*sigma/Fraction(H+1)) for H in (0,1,2,3,7)}
    need(fixed['1'] == '1797203/1200000', 'recover predecessor two-level point')
    return dict(radix='2^1200', alpha_strict_upper=str(alpha),
                prior_time=str(old_time), near_input_space_time=str(target),
                time_charges_before_log_absorption={key:str(value) for key,value in charges.items()},
                positive_log_absorption_gaps={key:str(target-value) for key,value in charges.items()},
                clean_space='O(N*r*log(r+2)) for fixed inherited compiler allowance F',
                fixed_height_clean_exponents=fixed,
                fixed_height_time=str(old_time),
                scope='Conditional source-relative Bennett tradeoff; no new simulation theorem, supplier or kappa.')


def compare_gaussian():
    rng = Random(24)
    n, axes, width = 3,(0,1,2),16
    values = [(rng.randrange(-9,10),rng.randrange(-9,10)) for _ in range(1<<n)]
    dirty = [(rng.randrange(1<<width),rng.randrange(1<<width)) for _ in values]
    rows = []
    for inverse in (False,True):
        code,size,projection = gaussian.compile_linear(n,axes,width,inverse)
        state = gaussian.encode_input(values,width,size)
        initial = gaussian.encode_output(old.decode(dirty,width),width)
        expected = old.xor_words(dirty,old.encode(old.scaled(values,axes,inverse),width))
        expected_bits = gaussian.encode_output(old.decode(expected,width),width)
        prior_target = list(initial)
        prior_invoice = prior.evaluate(code,state,prior_target,projection)
        need(prior_target == expected_bits, 'same-input predecessor baseline')
        for radix,height in ((2,0),(2,1),(2,2),(2,3),(2,4),(2,5),(2,6),(3,3),(4,2),(8,1)):
            source,target = list(state),list(initial)
            invoice = hierarchy.evaluate(prior,code,source,target,radix,height,projection)
            need(source == state and target == expected_bits, 'Gaussian independent linear oracle')
            need(invoice == hierarchy.expected_invoice(len(code),size,radix,height,len(projection)),
                 'Gaussian complete invoice')
            rows.append(dict(inverse=inverse,radix=radix,height=height,
                             program_steps=len(code),configuration_bits=size,
                             input_sha256=sha256(bytes(state)+bytes(initial)).hexdigest(),
                             peak_payload_bits=invoice['peak_clean_payload_bits'],
                             payload_work=hierarchy.payload_work(invoice),invoice=invoice,
                             predecessor_peak_payload_bits=prior_invoice['peak_clean_payload_bits'],
                             predecessor_invoice=prior_invoice))
    return rows


class HierarchicalOracle:
    def __init__(self):
        self.calls = []

    def apply(self,source,target,axes,width,inverse=False):
        n = len(source).bit_length()-1
        code,size,projection = gaussian.compile_linear(n,axes,width,inverse)
        state = gaussian.encode_input(source,width,size)
        saved = list(state)
        bits = gaussian.encode_output(old.decode(target,width),width)
        invoice = hierarchy.evaluate(prior,code,state,bits,2,3,projection)
        need(state == saved, 'macro source preservation')
        need(invoice == hierarchy.expected_invoice(len(code),size,2,3,len(projection)), 'macro invoice')
        answer = old.encode(gaussian.decode_output(bits,width),width)
        need(answer == old.xor_words(target,old.encode(old.scaled(source,axes,inverse),width)),
             'macro scaled orientation')
        self.calls.append((tuple(axes),inverse))
        return answer


def macros():
    rng, oracle = Random(24),HierarchicalOracle()
    rows = []
    for axes in ((0,),(0,2),(0,1,2)):
        values = [(rng.randrange(-6,7),rng.randrange(-6,7)) for _ in range(8)]
        begin = len(oracle.calls)
        forward = old.inplace_block(values,axes,16,oracle)
        need(forward == old.lifted(values,axes), 'unchanged nonlinear endpoint')
        back = old.inplace_block(forward,axes,16,oracle,True)
        need(back == values and len(oracle.calls)-begin == 8, 'four-call consumer exact inverse')
        rows.append(dict(axes=list(axes),calls_each_direction=4,exact_return=True,
                         result_sha256=sha256(json.dumps(forward).encode()).hexdigest()))
    return dict(oracle_calls=len(oracle.calls),cases=rows)


def expect_failure(action, text):
    try:
        action()
    except ValueError as error:
        need(text in str(error), 'intended rejection: '+text+'; got '+str(error))
    else:
        raise ValueError('failed to reject '+text)


def controls():
    program = [('set',0,1,0)]*17
    for level in range(3):
        expect_failure(lambda: hierarchy.evaluate(prior,program,[0],[0],2,3,
                       omit_cleanup_level=level), 'checkpoint cleanup')
    expect_failure(lambda: hierarchy.evaluate(prior,program,[0],[0],2,3,
                   corrupt_history=True), 'inverse transition consistency')
    aliased = [0]
    expect_failure(lambda: hierarchy.evaluate(prior,program,aliased,aliased,2,3), 'source/target alias')
    expect_failure(lambda: hierarchy.evaluate(prior,[],[0,1],[0,0],2,3,[1,0]), 'streaming projection order')
    for args in ((1,1,1,0),(-1,1,2,0),(1,0,2,0),(1,1,2,-1),(True,1,2,0)):
        expect_failure(lambda args=args: hierarchy.shape(*args), 'integer plan' if args[0] is True else 'plan domain')
    # Incorrect segment offsets can preserve the gate count yet change the map.
    p = [('set',0,0,0),('set',0,1,0)]
    target = [0]
    hierarchy.evaluate(prior,p,[0],target,2,1,wrong_interval=True)
    need(target != reference(p,[0],[0],[0]), 'wrong-interval negative control')
    # Every local head return must be priced; a zero routing invoice is false.
    invoice = hierarchy.expected_invoice(19,3,2,3)
    need(invoice['checkpoint_moves'] > 0, 'nonzero multilevel routing bill')
    code = (HERE/'hierarchy.py').read_text()
    before = 'move(slot)\n            need(not any(banks[slot]), message)'
    need(code.count(before) == 1, 'routing mutation target')
    mutant = sources.module(code.replace(before, 'need(not any(banks[slot]), message)').encode(),
                            'undercharged_scan_routing')
    got = mutant.evaluate(prior, program_fixture(3,19), [0,1,0], [1,0,1], 2,3)
    need(got != invoice and got['checkpoint_moves'] < invoice['checkpoint_moves'],
         'unpriced entry/cleanup scan routing detected')
    return dict(omitted_cleanup_levels=3, corrupt_history=True, alias=True,
                unordered_projection=True, invalid_plans=5, wrong_interval=True,
                nonzero_routing=invoice['checkpoint_moves'], unpriced_scan_routing=True)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit',action='store_true')
    parser.add_argument('--suite',choices=('controller','plans','exponents','gaussian','macros','controls','all'),default='all')
    args = parser.parse_args()
    suites = dict(controller=controller_cases,plans=plans,exponents=exponents,
                  gaussian=compare_gaussian,macros=macros,controls=controls)
    result = {key:run() for key,run in suites.items() if args.suite in (key,'all')}
    if not args.emit:
        expected = sources.loads((HERE/'RESULT.json').read_bytes())
        if args.suite != 'all':
            expected = {args.suite:expected[args.suite]}
        need(canonical(result) == canonical(expected), 'complete typed hierarchy receipt')
    print(json.dumps(result,sort_keys=True,indent=2))
    if not args.emit:
        print('PASS_LIFTING_RELATIVE_HISTORY')


if __name__ == '__main__':
    main()
