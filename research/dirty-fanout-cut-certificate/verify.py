#!/usr/bin/env python3
"""Exact compiler certificates, complete tiny searches and adversarial controls."""
import argparse
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256, sha1
from heapq import heappush, heappop
from itertools import product
import json
from pathlib import Path
from random import Random
import sys
import types

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def loads(raw):
    def unique(pairs):
        d = {}
        for k,v in pairs:
            need(k not in d, 'duplicate JSON key')
            d[k] = v
        return d
    return json.loads(raw, object_pairs_hook=unique)


def local(name):
    module = types.ModuleType(name)
    module.__file__ = str(HERE/(name+'.py'))
    sys.modules[name] = module
    exec(compile((HERE/(name+'.py')).read_bytes(),module.__file__,'exec'),module.__dict__)
    return module


solver, checker = local('synthesize'), local('check')


def sources():
    source = loads((HERE/'SOURCES.json').read_bytes())
    declared = loads((HERE/'VERIFY.json').read_bytes())['inputs']
    live = [p for p in source['files'] if p['usage'] == 'input']
    need(set(declared) == {p['path'] for p in live}, 'declared live inputs')
    for pin in live:
        raw = (ROOT/pin['path']).read_bytes()
        need(sha256(raw).hexdigest() == pin['sha256'], 'live source SHA256')
        need(sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
             == pin['git_blob'], 'live source blob')


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def forest_min(mu, add):
    """Independent exhaustive parent functions; does not use compiler helpers."""
    n, best, count = len(mu), sum(mu), 0
    for parent in product(*[[None]+[j for j in range(len(mu)) if j != i] for i in range(len(mu))]):
        for origin in range(n):
            seen, v = set(), origin
            while v is not None and v not in seen:
                seen.add(v)
                v = parent[v]
            if v is not None:
                break
        else:
            count += 1
            best = min(best,sum(mu[i] if j is None else 2*add[i][j] for i,j in enumerate(parent)))
    return best,count


def unrestricted_min(mu, add):
    """Dijkstra on actual affine maps, permitting every gate interleaving."""
    n = len(mu)
    initial = tuple(1 << i for i in range(n))
    target = tuple(v | (1 << n) for v in initial)
    queue, dist, visited = [(0,initial)], {initial:0}, 0
    while queue:
        price,state = heappop(queue)
        if price != dist[state]:
            continue
        visited += 1
        if state == target:
            return price, visited
        for i in range(n):
            for j in range(-1,n):
                if j == i:
                    continue
                out = list(state)
                out[i] ^= (1 << n) if j < 0 else state[j]
                out = tuple(out)
                cost = price+(mu[i] if j < 0 else add[i][j])
                if out not in dist or cost < dist[out]:
                    dist[out] = cost
                    heappush(queue,(cost,out))
    raise ValueError('unreachable endpoint')


def small():
    rng, rows, forests, states, sharing, mixed = Random(19), [], 0, 0, 0, 0
    # Complete positive {1,5} price cubes through q=3; 2^(q^2) matrices.
    # Unlike {1,2}, these include strictly profitable sharing, not only ties.
    for n in (1,2,3):
        for values in product((1,5), repeat=n*n):
            mu, it = list(values[:n]),iter(values[n:])
            add = [[None if i == j else next(it) for j in range(n)] for i in range(n)]
            cert = solver.synthesize(mu,add)
            answer = checker.check(mu,add,cert)
            want, visited = unrestricted_min(mu,add)
            need(Fraction(answer['cost']) == want, 'unrestricted affine optimum')
            sharing += want < sum(mu)
            mixed += 1 < answer['oracles'] < n
            states += visited
            rows.append((n,values,answer['cost'],digest(cert)))
    # Larger exact parent enumerations and fractional, asymmetric prices.
    for n in range(1,7):
        for case in range(8):
            mu = [Fraction(rng.randrange(1,41),rng.randrange(1,5)) for _ in range(n)]
            add = [[None if i == j else Fraction(rng.randrange(1,31),rng.randrange(1,5))
                    for j in range(n)] for i in range(n)]
            cert = solver.synthesize(mu,add)
            answer = checker.check(mu,add,cert)
            want, count = forest_min(mu,add)
            need(Fraction(answer['cost']) == want, 'independent forest optimum')
            forests += count
            rows.append((n,case,answer['cost'],digest(cert)))
    need(sharing > 0 and mixed > 0, 'nontrivial sharing and mixed-root coverage')
    return dict(affine_tariff_instances=530, affine_settled_states=states,
                strict_sharing_wins=sharing, mixed_root_certificates=mixed,
                rational_forest_instances=48, enumerated_forests=forests,
                receipt_sha256=digest(rows))


def hierarchical_prices(n):
    mu = [1 if i == 0 else 10000+(19*i)%23 for i in range(n)]
    add = [[None if i == j else 1+(i^j).bit_length()**2+(19*(i+1)+j)%3
            for j in range(n)] for i in range(n)]
    return mu,add


def examples():
    rows, certs = [], {}
    chain = loads((HERE/'examples/chain.json').read_bytes())
    cycle_mu = [1,100,100]
    cycle_add = [[None,100,100],[50,None,1],[50,1,None]]
    cases = [('chain',chain['mu'],chain['add']), ('cheap_cycle',cycle_mu,cycle_add)]
    cases += [('hierarchy_'+str(n),*hierarchical_prices(n)) for n in (8,16,31,64,112)]
    for name,mu,add in cases:
        cert = solver.synthesize(mu,add)
        answer = checker.check(mu,add,cert)
        masks = [sum(1 << i for i in c['rows']) for c in cert['cuts']]
        need(all((a & b) in (0,a,b) for a in masks for b in masks), 'compiler laminar cuts')
        need(len(masks) <= 2*len(mu)-1, 'compact dual support')
        rows.append(dict(name=name,**answer,tariffs_sha256=digest([mu,add]),
                         certificate_sha256=digest(cert), direct_cost=str(sum(mu)),
                         largest_cut=max(len(c['rows']) for c in cert['cuts'])))
        certs[name] = cert
    need(rows[0]['cost'] == '5' and rows[1]['cost'] == '103', 'credited chain/cycle controls')
    need(any(len(c['rows']) > 1 for c in certs['cheap_cycle']['cuts']), 'cycle needs joint cut')
    return rows,certs


def rejection(action, message):
    try:
        action()
    except ValueError as error:
        need(message in str(error), 'intended control: '+message+'; got '+str(error))
    else:
        raise ValueError('control accepted: '+message)


def controls():
    mu,add = hierarchical_prices(8)
    original = solver.synthesize(mu,add)
    cases = []
    def mutate(name, edit, error):
        c = deepcopy(original)
        edit(c)
        rejection(lambda: checker.check(mu,add,c),error)
        cases.append(name)
    mutate('missing_restore',lambda c:c['word'].pop(), 'arbitrary-dirt endpoint')
    mutate('missing_root',lambda c:c['word'].__setitem__(slice(None),[g for g in c['word'] if g[0]!='P']),
           'arbitrary-dirt endpoint')
    mutate('wrong_add_direction',lambda c:c['word'][0].__setitem__(slice(1,None),list(reversed(c['word'][0][1:]))),
           'arbitrary-dirt endpoint')
    mutate('inflated_cut',lambda c:c['cuts'][0].__setitem__('price','100000000'), 'root dual capacity')
    mutate('negative_cut',lambda c:c['cuts'][0].__setitem__('price','-1'), 'positive cut price')
    mutate('duplicate_row',lambda c:c['cuts'][0]['rows'].append(c['cuts'][0]['rows'][0]),'cut rows')
    mutate('typed_cost',lambda c:c.__setitem__('cost',True), 'canonical rational string')
    mutate('typed_row',lambda c:c['word'][0].__setitem__(1,False), 'gate operands')
    mutate('parent_cycle',lambda c:(c['parents'].__setitem__(0,1),c['parents'].__setitem__(1,0)), 'parent cycle')
    mutate('unpaid_cut',lambda c:c['cuts'].pop(), 'primal dual equality')
    c = dict(schema_version=1,q=2,parents=[None,0],
             cuts=[dict(rows=[0],price='10'),dict(rows=[1],price='10')],
             cost='20',word=[['ADD',1,0],['P',0],['ADD',1,0]])
    rejection(lambda:checker.check([10,10],[[None,1],[1,None]],c),'ADD dual capacity')
    cases.append('forgot_half_ADD_coefficient')
    for bad in (True,0,-1,0.5):
        rejection(lambda bad=bad:solver.synthesize([bad],[[None]]),'positive exact tariff')
        rejection(lambda bad=bad:checker.check([bad],[[None]],{}),'positive exact tariff')
    # Independently supplied crossing cuts: acceptance does not require the
    # compiler's laminar form or reconstruct the compiler's chosen certificate.
    c = dict(schema_version=1,q=3,parents=[None,0,1],cost='8',
             cuts=[dict(rows=[i],price='2') for i in range(3)]
                  +[dict(rows=[0,1],price='1'),dict(rows=[1,2],price='1')],
             word=[['ADD',2,1],['ADD',1,0],['P',0],['ADD',1,0],['ADD',2,1]])
    need(checker.check([3,4,3],[[None,10,10],[Fraction(3,2),None,10],[10,1,None]],c)['cost']=='8',
         'valid nonlaminar certificate accepted')
    return dict(rejected_mutations=cases,invalid_price_types=4,nonlaminar_certificate=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--emit',action='store_true')
    parser.add_argument('--suite',choices=('small','examples','controls','all'),default='all')
    args = parser.parse_args()
    sources()
    result = {}
    if args.suite in ('small','all'):
        result['small'] = small()
    if args.suite in ('examples','all'):
        result['examples'], certificates = examples()
        if args.emit:
            (HERE/'CERTIFICATES.json').write_text(canonical(certificates)+'\n')
        else:
            need(canonical(certificates) == canonical(loads((HERE/'CERTIFICATES.json').read_bytes())),
                 'complete typed certificates')
    if args.suite in ('controls','all'):
        result['controls'] = controls()
    if not args.emit:
        expected = loads((HERE/'RESULT.json').read_bytes())
        if args.suite != 'all':
            expected = {args.suite:expected[args.suite]}
        need(canonical(result) == canonical(expected), 'complete typed receipt')
    print(json.dumps(result,sort_keys=True,indent=2))
    if not args.emit:
        print('PASS_DIRTY_FANOUT_CUT_SYNTHESIS')


if __name__ == '__main__':
    main()
