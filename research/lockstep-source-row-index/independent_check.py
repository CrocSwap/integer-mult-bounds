"""Independent finite word enumeration and adversarial state-hash witness.

Author code is never edited. The expected source list does not use its
multiplicity, parent, local-count or block implementation.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from math import comb, prod
from pathlib import Path
from types import ModuleType
import json
import sys

HERE = Path(__file__).resolve().parent
PACKAGE = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else HERE


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_source():
    path = PACKAGE/'source_index.py'
    module = ModuleType('peer_source_index')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def word_sources(index):
    rule, height = index.rule, index.height
    types = tuple(sorted(set(k for _, k in rule.roles)))
    expected = []
    for depth in range(height+1):
        for path in product(range(len(rule.rounds)), repeat=depth):
            dilation = prod(rule.rounds[j][0] for j in path)
            groups = Counter()
            for word in product(range(len(rule.roles)), repeat=height-depth):
                ranks = tuple(rule.roles[j][1] for j in word)
                if rule.ambient*dilation*prod(ranks) <= index.rank:
                    groups[tuple(ranks.count(k) for k in types)] += 1
            for point, count in groups.items():
                column = prod(k**a for k, a in zip(types, point))
                parent_dilation = prod(rule.rounds[j][0] for j in path[:-1])
                for ordinal in range(count):
                    for role_index, (role, target) in enumerate(rule.roles):
                        if not path or rule.ambient*parent_dilation*column*target > index.rank:
                            expected.append((path, point, ordinal, role_index, role))
    expected.sort()
    return expected


def check_case(module, rule, rank):
    index = module.SourceIndex(rule, rank, replicas=5, namespace='peer')
    expected = word_sources(index)
    need(index.size == len(expected), 'ordered-word source total')
    for row, (path, point, ordinal, _, role) in enumerate(expected):
        unit = module.C.Unit(path, point, ordinal)
        need(index.rank_source(unit, role) == row, 'declared source order')
        need(index.unrank_source(row) == (unit, role), 'source inverse')
        for replica in range(5):
            owner = ('peer', replica, 'source', path, point, ordinal, role)
            physical = replica*index.size+row
            need(index.row(owner) == physical and index.owner(physical) == owner,
                 'replicated source interval')
    for illegal in (-1, 5*index.size):
        try:
            index.owner(illegal)
        except ValueError:
            pass
        else:
            raise ValueError('row boundary accepted')
    sample = index.owner(0)
    try:
        index.row(sample[:2]+('owned',)+sample[3:])
    except ValueError:
        pass
    else:
        raise ValueError('owned role received source credit')
    q, d, height = len(index.paid), len(rule.types), index.height
    need(len(index.total) <= 1+q*comb(height+q-1, q), 'state-count envelope')
    profiles = index.point_data.values() if isinstance(index.point_data, dict) else index.point_data
    need(sum(map(len, profiles)) == comb(height+d, d), 'target-profile count')
    return {'height':height, 'paid_alphabet':q, 'target_alphabet':d,
            'sources':len(expected), 'replicas':5, 'states':len(index.total)}


def collision_family(module):
    hmod = sys.hash_info.modulus
    rule = module.C.Rule((('single',8*hmod),),
                        tuple((hmod*p,'single') for p in (1,2,3,5,7)))
    result = []
    for height in (1,2,3,4):
        index = module.SourceIndex(rule, rule.ambient*(8*hmod)**height)
        states = [(rho,last) for h,rho,last in index.total if h == height]
        count = 5*comb(height+3,4)
        need(len(states) == count, 'collision family exact cardinality')
        need(len(set(map(hash,states))) == 1, 'all states share hash')
        need(index.size == 1, 'collision-family source total')
        result.append({'height':height, 'layer_states':count,
                       'distinct_hashes':1, 'sources':index.size})
    return {'integer_hash_modulus':hmod, 'cases':result}


def main():
    module = load_source()
    rule1 = module.C.Rule((('seven_a',7),('eleven',11),('seven_b',7)),
                         ((1,'seven_a'),(2,'seven_b'),(3,'bank'),(6,'eleven')),
                         ambient=13)
    rule2 = module.C.Rule((('one',5),),
                         ((1,'one'),(2,'bank'),(2,'one'),(4,'one')),ambient=8)
    cases = [check_case(module,rule,rule.ambient*min(rule.types)**height+delta)
             for rule in (rule1,rule2) for height in (0,1,2,3)
             for delta in (0,min(rule.types)-1)]
    result = {'status':'PASS_SOURCE_INDEX_PEER_FUNCTIONAL_CHECKS',
              'package_hashes':{name:sha256((PACKAGE/name).read_bytes()).hexdigest()
                                for name in ('source_index.py','PROOF.md','verify.py')},
              'bounded_cases':cases, 'sources_checked':sum(x['sources'] for x in cases),
              'collision_witness':collision_family(module)}
    (HERE/'INDEPENDENT-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'], 'cases='+str(len(cases)),
          'sources='+str(result['sources_checked']), 'hash_collision_cases=4')


if __name__ == '__main__':
    main()
