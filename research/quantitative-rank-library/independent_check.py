"""Independent literal-word oracle for complete rank-library metadata.

Constructs every bounded physical target field and actual parent paid edge.
No compressed histogram recurrence, author source predicate, or profile helper
is used to determine fresh sources. Prepared for CubeJerry with OpenAI assistance.
"""
from collections import Counter
from itertools import product
from math import gcd, lcm, prod
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
from types import ModuleType


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def literal_census(targets, paid, n):
    ambient, smallest = max(targets), min(targets)
    height, column = 0, 1
    while ambient * column * smallest <= n:
        height += 1
        column *= smallest
    fields, incoming, exits = {}, set(), []
    units = []
    for depth in range(height + 1):
        for path in product(range(len(paid)), repeat=depth):
            dilation = prod(paid[j] for j in path)
            for word in product(range(len(targets)), repeat=height-depth):
                rank_product = dilation * prod(targets[i] for i in word)
                if ambient * rank_product > n:
                    continue
                units.append((path, word, rank_product))
                for role, rank in enumerate(targets):
                    field = path, word, role
                    require(field not in fields, 'distinct target fields')
                    fields[field] = rank_product * rank
    for path, word, rank_product in units:
        for site, paid_rank in enumerate(paid):
            if word:
                destination = path+(site,), word[1:], word[0]
                require(destination in fields, 'all nondeepest paid edges fit')
                require(fields[destination] == rank_product*paid_rank, 'edge rank')
                require(destination not in incoming, 'unique incoming paid edge')
                incoming.add(destination)
            else:
                exits.append(rank_product*paid_rank)
    sources = Counter(rank for field, rank in fields.items() if field not in incoming)
    require(sum(sources.values()) > 0, 'positive independent source set')
    return dict(height=height, units=len(units), sources=dict(sorted(sources.items())),
                exits=tuple(exits), fields=len(fields), incoming=len(incoming))


def literal_library(targets, paid, cap, pool_exits=False):
    require(min(targets)>=2 and paid and 0<min(paid)<=max(paid)<min(targets),
            'strictly separated finite role lists')
    rows = {}
    censuses = {}
    for n in range(1, cap+1):
        if n < max(targets):
            rows[n] = dict(a=1, B=1, P=n, O=0)
            continue
        c = literal_census(targets, paid, n)
        factors = []
        for source_rank, count in c['sources'].items():
            if source_rank < n:
                width = rows[n-source_rank]['B']
                factors.append(width//gcd(width,count))
        if pool_exits:
            for rank, count in Counter(c['exits']).items():
                width=rows[rank]['B']
                factors.append(width//gcd(width,count))
        else:
            factors.extend(rows[rank]['B'] for rank in c['exits'])
        a=lcm(*factors)
        B=a*sum(c['sources'].values())
        leaves, units = 0, a*c['units']
        for source_rank, count in c['sources'].items():
            if source_rank < n:
                child=rows[n-source_rank]
                require(a*count % child['B']==0, 'whole complement invocation')
                copies=a*count//child['B']
                leaves += copies*child['P']
                units += copies*child['O']
        for rank in c['exits']:
            child=rows[rank]
            if pool_exits and a % child['B']:
                return rows, censuses, dict(rank=n, exit_rank=rank,
                    width=child['B'], replication=a, exit_count=c['exits'].count(rank))
            require(a % child['B']==0, 'every original chronological cut is integral')
            copies=a//child['B']
            leaves += copies*child['P']
            units += copies*child['O']
        rows[n]=dict(a=a,B=B,P=leaves,O=units)
        censuses[n]=c
    return rows,censuses,None


CASES = (
    ((2,3),(1,1),48),
    ((3,4,6),(1,2,2),48),
    ((3,4),(2,2),32),
    ((3,3,5),(2,2),48),
    ((2,),(1,1),48),
    ((2,),(1,1,1),48),
    ((2,4,8),(1,1),64),
)


def main():
    result=[]
    package=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parent
    actual=None
    if package:
        spec=spec_from_file_location('root_rank_library_under_review',package/'library.py')
        actual=module_from_spec(spec);sys.modules[spec.name]=actual;spec.loader.exec_module(actual)
    for targets,paid,cap in CASES:
        rows,censuses,_=literal_library(targets,paid,cap)
        _,_,negative=literal_library(targets,paid,cap,pool_exits=True)
        if actual:
            rule=actual.Rule(tuple(sorted(Counter(targets).items())),tuple(sorted(Counter(paid).items())))
            library=actual.compile_library(rule,cap)
            for n,expected in rows.items():
                got=library.rows[n]
                require((got.replication,got.width,got.leaves,got.units)==
                        tuple(expected[k] for k in ('a','B','P','O')), 'literal complete library row')
            work=actual.Work();limits=actual.Limits();height=actual.height(rule,cap)
            tt=actual.product_tables(rule.targets,height,limits,work)
            rr=actual.product_tables(rule.paid,height+1,limits,work)
            for n,expected in censuses.items():
                got=actual.census(rule,n,tt,rr,limits,work)
                require(got.units==expected['units'] and dict(got.sources)==expected['sources']
                        and dict(got.exits)==dict(Counter(expected['exits'])), 'literal source and cut census')
            envelope=actual.envelope(rule,cap)
            require(all((x.width+x.leaves+x.units).bit_length()<=envelope['combined_output_bits']
                        for x in library.rows[1:]), 'stated fully evaluated output bound')
        result.append(dict(targets=targets,paid=paid,cap=cap,rows=rows,
            source_fields=sum(sum(c['sources'].values()) for c in censuses.values()),
            units=sum(c['units'] for c in censuses.values()),
            incoming_edges=sum(c['incoming'] for c in censuses.values()),
            exit_pooling_witness=negative))
    controls=[]
    if actual:
        text=(package/'library.py').read_text()
        old='factor = child(rows, flow.rank, exit_rank).width'
        require(text.count(old)==1,'unique exit constraint seam')
        mutant=ModuleType('root_pooled_exit_mutant');sys.modules[mutant.__name__]=mutant
        exec(compile(text.replace(old,old+'\n        factor //= gcd(factor, multiplicity)'),
                     'pooled-exit-negative-control','exec'),mutant.__dict__)
        rule=mutant.Rule(((3,1),(4,1)),((2,2),))
        try:
            mutant.compile_library(rule,12)
        except ValueError as error:
            require(str(error)=='nonintegral chronological child batch','pooling rejection reason')
        else:
            raise AssertionError('exit pooling mutant survived')
        controls.append('exit pooling rejected by original rank-4 cut at n=12')
        expected,_,_=literal_library((3,4),(2,2),12)
        require(expected[12]['a']==2 and expected[12]['B']==8,'small explicit cut witness')
        try:
            actual.compile_library(actual.Rule(((3,1),(4,1)),((2,2),)),12,actual.Limits(max_rank=11))
        except actual.BudgetError:
            controls.append('explicit rank budget failure')
        else:
            raise AssertionError('rank budget guard survived')
        try:
            actual.Rule(((2,1),),((2,1),))
        except ValueError:
            controls.append('nonseparated rule rejected')
        else:
            raise AssertionError('nonseparated rule admitted')
    output=dict(status='PASS_INDEPENDENT_RANK_LIBRARY' if actual else 'INDEPENDENT_EXPECTED_LIBRARY_BUILT',method='literal role words and unique parent edges',
                rules=len(result),ranks=sum(x['cap'] for x in result),cases=result)
    if actual:
        output['controls']=controls
        output['core_sha256']={name:sha256((package/name).read_bytes()).hexdigest() for name in ('library.py','PROOF.md')}
    destination=Path(__file__).with_name('INDEPENDENT-RESULT.json')
    destination.write_text(json.dumps(output,indent=2)+'\n')
    print(json.dumps({k:v for k,v in output.items() if k!='cases'}))


if __name__=='__main__':
    main()
