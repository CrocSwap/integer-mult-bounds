#!/usr/bin/env python3
"""Source-bound checks of the all-rank argument, not a new native audit.

The pinned #4507 flow/width implementation supplies the object being studied.
growth.py separately implements breakpoints, valuations and envelopes.
Mihir Srivastava, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from bisect import bisect_right
from functools import lru_cache
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from growth import (check_descent, check_envelope, depth_bound, factor,
                    from_valuations, join_valuations, next_valuations,
                    rank_primes, require, smooth_numbers, universal_parameters)


def authenticate():
    for row in json.loads((HERE/'VENDOR.json').read_text(encoding='utf-8')):
        raw = (HERE/row['path']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256: '+row['path'])
        framed = b'blob '+str(len(raw)).encode()+b'\0'+raw
        require(hashlib.sha1(framed).hexdigest() == row['git_blob'], 'source Git blob: '+row['path'])


def load_flow():
    spec = importlib.util.spec_from_file_location('pinned_batches', HERE/'vendor/batches.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def integer_record(n):
    return {'bits': n.bit_length(), 'unsigned_big_endian_sha256':
            hashlib.sha256(n.to_bytes(max(1,(n.bit_length()+7)//8),'big')).hexdigest()}


def receipt_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def breakpoints(flow, targets, paid, cap):
    m = max(targets)
    primes = rank_primes(targets, paid)
    smooth = smooth_numbers(primes, cap)
    require(len(smooth) == len(set(smooth)), 'distinct breakpoint products')
    exhaustive = []
    for value in range(1,cap+1):
        rest = value
        for prime in primes:
            while rest % prime == 0:
                rest //= prime
        if rest == 1:
            exhaustive.append(value)
    require(smooth == exhaustive, 'complete smooth inventory')
    prior, changes, constant_intervals = None, [], 0
    representative = {}
    for c in range(1,cap+1):
        current = flow(targets,paid,m*c)
        require(flow(targets,paid,m*c+m-1) == current, 'floor-cutoff interval')
        t = smooth[bisect_right(smooth,c)-1]
        if t not in representative:
            representative[t] = flow(targets,paid,m*t)
        require(current == representative[t], 'complete flow constant between prime products')
        total = sum(current['sources'].values())
        if prior is not None and total != prior:
            require(c in smooth, 'source-count change at a prime product')
            changes.append(c)
        if c != t:
            constant_intervals += 1
        prior = total
    params = universal_parameters(targets,paid,m*cap)
    require(len(smooth) <= params['prime_box_count'], 'prime exponent box')
    return {'cap':cap,'rank_primes':primes,'smooth_products':len(smooth),
            'nontrivial_constant_comparisons':constant_intervals,
            'source_count_changes':len(changes),'change_points_sha256':receipt_hash(changes)}


def compile_check(module, name, targets, paid, maximum, expected):
    compiled = module.compile_widths(targets,paid,maximum)
    require(integer_record(compiled['widths'][-1]) == expected['width'], 'pinned final width')
    m = max(targets)
    params = universal_parameters(targets,paid,maximum)
    smooth = smooth_numbers(params['rank_primes'],params['cap'])
    flows = {}
    def flow_at(n):
        c = n//m
        if c not in flows:
            flows[c] = module.direct_flow(targets,paid,m*c)
        return flows[c]
    factors = lru_cache(None)(factor)
    sampled_sources = {sum(flow_at(m*t)['sources'].values()) for t in smooth}
    sampled_lcm = join_valuations(*(factors(s) for s in sampled_sources))
    source_lcm, seen_sources, values, records = {}, set(), [{} for _ in range(m)], []
    constraints = 0
    first_depth_needed = None
    first_denominator_needed = None
    for n in range(m,maximum+1):
        f = flow_at(n)
        S = sum(f['sources'].values())
        require(S <= params['source_ceiling'], 'polynomial source bound')
        rows = module.requirements(f,n)
        check_descent(rows,n,m)
        depth = depth_bound(n,m)
        require(all(depth_bound(e,m) < depth for e,_ in rows), 'decreasing depth envelope')
        powers = next_valuations(values,rows,factors(S))
        exact = from_valuations(powers)
        require(exact == compiled['widths'][n], 'prime recurrence equals chronological width')
        source_lcm = join_valuations(source_lcm,factors(S))
        seen_sources.add(S)
        check_envelope(powers,source_lcm,depth)
        check_envelope(powers,sampled_lcm,depth)
        if first_depth_needed is None and any(e>source_lcm.get(p,0) for p,e in powers.items()):
            first_depth_needed = {'n':n,'width':exact,'source_lcm':from_valuations(source_lcm)}
        without_counts = next_valuations(values,[(e,1) for e,_ in rows],factors(S))
        if first_denominator_needed is None and without_counts != powers:
            first_denominator_needed = {'n':n,'width':exact,'without_gcd':from_valuations(without_counts)}
        require(exact <= 1 << params['power_of_two_exponent'], 'explicit binary upper bound')
        values.append(powers)
        records.append([n,sorted(powers.items()),depth])
        constraints += len(rows)
    require(seen_sources == sampled_sources, 'breakpoints cover every source total')
    require(source_lcm == sampled_lcm, 'sampled and full source LCM agree')
    return {'rule':name,'maximum':maximum,'compiled_ranks':maximum-m+1,
            'batch_constraints':constraints,'width':integer_record(compiled['widths'][-1]),
            'source_values':len(sampled_sources),'source_lcm':integer_record(from_valuations(sampled_lcm)),
            'all_rank_valuation_sha256':receipt_hash(records),
            'parameters':params,'first_depth_needed':first_depth_needed,
            'first_denominator_needed':first_denominator_needed}


def controls(module, compilations):
    rejected = []
    def reject(name, operation, message):
        try:
            operation()
        except ValueError as error:
            require(message in str(error), 'wrong rejection: '+name)
            rejected.append(name)
        else:
            raise ValueError('control accepted: '+name)
    reject('paid rank reaches ambient',lambda:rank_primes({2:1,5:1},{5:1}),'strict rank')
    reject('target rank one',lambda:rank_primes({1:1,5:1},{2:1}),'strict rank')
    reject('noncontracting batch',lambda:check_descent([(9,1)],10,5),'uniform rank')
    reject('zero batch count',lambda:check_descent([(2,0)],10,5),'uniform rank')
    reject('nonprime breakpoint alphabet',lambda:smooth_numbers([2,4],20),'ordered primes')
    targets, paid = {2:1,5:1}, {1:2,3:1}
    a = module.direct_flow(targets,paid,10)
    b = module.direct_flow(targets,paid,15)
    require(rank_primes(targets,paid)==[2,3,5], 'paid-prime positive control')
    require(smooth_numbers([2,5],3)==[1,2], 'target-only alias')
    reject('omit paid breakpoint prime',lambda:require(a==b,'changed flow'),'changed flow')
    require(sum(a['sources'].values())!=sum(b['sources'].values()), 'changed source total witness')
    rule_t, rule_p = {2:4,3:1}, {1:6,2:2}
    first = module.compile_widths(rule_t,rule_p,3)['widths'][3]
    require(first==5 and rank_primes(rule_t,rule_p)==[2,3], 'new width prime witness')
    reject('confuse width primes with rank primes',lambda:check_envelope(factor(first),{2:1,3:1},1),'source LCM')
    witness = next(r['first_depth_needed'] for r in compilations if r['first_depth_needed'])
    reject('drop recursive depth factor',lambda:check_envelope(factor(witness['width']),factor(witness['source_lcm']),1),'source LCM')
    denominator = next(r['first_denominator_needed'] for r in compilations if r['first_denominator_needed'])
    reject('omit gcd cancellation in exact recurrence',lambda:require(denominator['width']==denominator['without_gcd'],'wrong exact valuation'),'wrong exact')
    reject('omit source multiplier',lambda:require(next_valuations([{}, {}, {}],[(0,1)],{})=={5:1},'source multiplier'),'source multiplier')
    return {'rejections':rejected,'paid_prime_counterexample':{
            'targets':{str(k):v for k,v in targets.items()},
            'paid':{str(k):v for k,v in paid.items()},
            'n_before':10,'n_after':15,'source_total_before':sum(a['sources'].values()),
            'source_total_after':sum(b['sources'].values())},
            'new_width_prime':{'rank_primes':[2,3],'first_width':first},
            'depth_counterexample':witness,'gcd_counterexample':denominator}


def run():
    authenticate()
    module = load_flow()
    native = json.loads((HERE/'vendor/p7-RESULT.json').read_text())['strictification']['native_inventory']
    parse = lambda d: {int(k):v for k,v in d.items()}
    expected = json.loads((HERE/'vendor/batch-RESULT.json').read_text())['compilations']
    cases = [('strict-overlap',{2:1,5:1},{1:2,4:1},100),
             ('source-open-equality',{2:4,3:1},{1:6,2:2},100),
             ('raw-p7',parse(native['targets']),parse(native['paid']),1000)]
    compilations = [compile_check(module,*case,ref) for case,ref in zip(cases,expected,strict=True)]
    epochs = [dict(rule=name,**breakpoints(module.direct_flow,t,p,256)) for name,t,p,_ in cases]
    epochs.append(dict(rule='paid-prime-control',**breakpoints(module.direct_flow,{2:1,5:1},{1:2,3:1},64)))
    return {'claim_type':'all-rank conditional width upper bound with finite exact checks',
            'compilations':compilations,'breakpoints':epochs,'controls':controls(module,compilations)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true',help='authoring only: regenerate RESULT.json')
    args = parser.parse_args()
    result = run()
    path = HERE/'RESULT.json'
    if args.write:
        path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    else:
        require(result==json.loads(path.read_text(encoding='utf-8')), 'complete receipt mismatch')
    print('PASS_CHRONOLOGICAL_WIDTH_GROWTH ranks='+str(sum(r['compiled_ranks'] for r in result['compilations']))
          +' breakpoint_caps='+str(sum(r['cap'] for r in result['breakpoints']))
          +' controls='+str(len(result['controls']['rejections'])))


if __name__ == '__main__':
    main()
