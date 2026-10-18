#!/usr/bin/env python3
"""Audit optimal finite ternary echoes under a borrowed-array budget.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import importlib.util
from itertools import product
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
LIMIT = 243
SCRATCH = 10

def require(condition, message):
    if not condition:
        raise ValueError(message)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def symbolic(word, count, depth):
    # Each key is an input register and an ordered word in free map symbols.
    state = [{(r, ()): 1} for r in range(depth+2)]
    for src, dst, index, sign in word:
        require(0 <= index < count and src != dst, "Invalid instruction")
        for (origin, symbols), coefficient in list(state[src].items()):
            key = (origin, symbols+(index,))
            state[dst][key] = state[dst].get(key, 0)+sign*coefficient
            if not state[dst][key]:
                del state[dst][key]
    return state

def expected_symbolic(count, depth, sign):
    state = [{(r, ()): 1} for r in range(depth+2)]
    state[1][(0, tuple(range(count)))] = sign
    return state

def ceil_log2(q):
    exponent = q.numerator.bit_length()-q.denominator.bit_length()
    return exponent+int(F(2)**exponent < q)


def enumerate_small_trees(costs):
    @lru_cache(maxsize=None)
    def profiles(n):
        if n == 1:
            return ((0,1),)
        if n == 2:
            return ((1,4),)
        result = []
        for a in range(1,n-1):
            for b in range(1,n-a):
                c = n-a-b
                for x,y,z in product(profiles(a),profiles(b),profiles(c)):
                    result.append((2+max(x[0],y[0],z[0]), 2*x[1]+4*y[1]+2*z[1]))
        return tuple(result)
    trees = 0
    for n in range(1,15):
        all_trees = profiles(n)
        trees += len(all_trees)
        for s in range(SCRATCH+1):
            expected = min((c for depth,c in all_trees if depth <= s),default=None)
            require(expected == costs[s][n], 'Full small-tree enumeration differs')
    return dict(factor_counts='1..14', ordered_trees=trees, budget_comparisons=14*(SCRATCH+1))


def check_table(module, costs, choices, balanced):
    # This pass enumerates all ordered triples, without the pair convolution.
    independent = [[None]*(LIMIT+1) for _ in range(SCRATCH+1)]
    triples = 0
    for s in range(SCRATCH+1):
        independent[s][1] = 1
        if s >= 1:
            independent[s][2] = 4
        if s < 2:
            continue
        previous = independent[s-2]
        for n in range(3,LIMIT+1):
            best = None
            for a in range(1,n-1):
                for b in range(1,n-a):
                    c = n-a-b
                    if any(previous[j] is None for j in (a,b,c)):
                        continue
                    value = 2*previous[a]+4*previous[b]+2*previous[c]
                    triples += 1
                    best = value if best is None else min(best,value)
            independent[s][n] = best
    require(independent == costs, 'Independent full-table minimum differs')
    digest = hashlib.sha256()
    feasible = expanded = 0
    for s in range(SCRATCH+1):
        capacity = (1 if s%2 == 0 else 2)*3**(s//2)
        for n in range(1,LIMIT+1):
            require((costs[s][n] is not None) == (n <= capacity), 'Capacity boundary differs')
            if costs[s][n] is None:
                continue
            tree = module.build(n,s,costs,choices)
            count,depth,calls = module.resources(tree)
            require(count == n and depth <= s and calls == costs[s][n], 'Tree witness differs')
            seen = peak = 0
            transcript = hashlib.sha256()
            for src,dst,index,sign in module.instructions(tree):
                require(0 <= index < n and src != dst, 'Invalid emitted instruction')
                peak = max(peak,src,dst)
                seen += 1
                transcript.update(json.dumps([src,dst,index,sign]).encode())
            require(seen == calls and peak == depth+1, 'Expanded word resources differ')
            require(n == 1 or calls >= 4*n-4, 'Inherited all-role lower bill failed')
            digest.update(json.dumps([s,n,depth,calls,transcript.hexdigest()]).encode())
            feasible += 1
            expanded += seen
    examples = []
    for n,s in ((5,3),(71,8),(127,9),(127,10),(243,10)):
        tree = module.build(n,s,costs,choices)
        examples.append(dict(factors=n,scratch_cap=s,resources=module.resources(tree),
                             root_split=[module.resources(child)[0] for child in tree],
                             balanced_resources=balanced.resources(n),
                             tree=tree,tree_sha256=hashlib.sha256(json.dumps(tree).encode()).hexdigest()))
    return dict(domain=dict(factors=[1,LIMIT],scratch=[0,SCRATCH]),
                cells=LIMIT*(SCRATCH+1),feasible_cells=feasible,
                infeasible_cells=LIMIT*(SCRATCH+1)-feasible,feasible_ordered_triples=triples,
                expanded_leaf_instructions=expanded,transcript_sha256=digest.hexdigest(),
                examples=examples,small_tree_enumeration=enumerate_small_trees(costs))


def identities(module, costs, choices):
    cases = nonlinear = 0
    rng = random.Random(71)
    for count in list(range(1,17))+[31,71,127,243]:
        first = next(s for s in range(SCRATCH+1) if costs[s][count] is not None)
        for budget in sorted({first,min(SCRATCH,first+2)}):
            tree = module.build(count,budget,costs,choices)
            _,depth,_ = module.resources(tree)
            forward = list(module.instructions(tree))
            backward = list(module.instructions(tree,-1))
            require(backward == [(s,t,i,-q) for s,t,i,q in reversed(forward)], 'Wrong inverse word')
            for sign,word in ((1,forward),(-1,backward)):
                require(symbolic(word,count,depth) == expected_symbolic(count,depth,sign),
                        'Free noncommuting product or restoration failed')
                cases += 1
            before = [rng.randrange(-200,201) for _ in range(depth+2)]
            def run(word, initial):
                state = initial[:]
                for src,dst,index,sign in word:
                    x = state[src]
                    state[dst] += sign*((x*x+(index+1)*x+index*index+3) % 257)
                return state
            after = run(forward,before)
            require(after[:1]+after[2:] == before[:1]+before[2:], 'Nonlinear restoration failed')
            require(run(backward,after) == before, 'Nonlinear inverse failed')
            other = before[:]
            other[1] += 113
            second = run(forward,other)
            require(second[1]-other[1] == after[1]-before[1], 'Increment reads target')
            nonlinear += 1
    return dict(free_noncommutative_cases=cases,nonlinear_cases=nonlinear,seed=71)


def rounded(module, costs, choices, balanced, leaf):
    cases = []
    beta = F(1,2)
    for count in (5,8,17,23,31):
        old_calls,budget = balanced.resources(count)
        tree = module.build(count,budget,costs,choices)
        _,depth,calls = module.resources(tree)
        radius = count+1
        a = 13*(radius+1)/beta**3
        gain = 2+radius/beta
        factors = [(i%2 == 0,(F(1,4),F((-1)**i,8)),F(3 if i == 0 else 1)) for i in range(count)]
        for length in (1,2):
            phases = [(F(1),F(0)),(F(3,5),F(4,5))][:length]
            for direction in (-1,1):
                for dirt in (0,7):
                    before = [[(F(dirt+2*i+j,4),F(dirt-3*i-j,8)) for i in range(length)]
                              for j in range(depth+2)]
                    magnitude = max(abs(x)+abs(y) for row in before for x,y in row)
                    def precision(n):
                        return max(25+ceil_log2(n*a*(magnitude+1))+(n-1)*ceil_log2(gain),
                                   ceil_log2(a),ceil_log2(2/beta**2))
                    bits = precision(calls)
                    bound = calls*a*(magnitude+1)*F(1,1<<bits)*gain**(calls-1)
                    require(bound <= F(1,1<<25), 'Complete precision budget failed')
                    target = leaf.exact_operator(before[0],factors,phases,direction)
                    state = copy.deepcopy(before)
                    stats = module.compose(leaf,*state[:2],factors,state[2:],phases,beta,bits,direction,tree)
                    require(stats['leaves'] == calls and stats['scalar_steps'] == 3*length*calls,
                            'Rounded call or scan bill differs')
                    require(state[:1]+state[2:] == before[:1]+before[2:], 'Rounded restoration failed')
                    error = max(leaf.c.norm2(leaf.c.sub(leaf.c.sub(y,y0),z))
                                for y,y0,z in zip(state[1],before[1],target))
                    require(error <= bound**2, 'Dense exact inverse bound failed')
                    module.compose(leaf,*state[:2],factors,state[2:],phases,beta,bits,direction,tree,-1)
                    require(state == before, 'Rounded inverse failed')
                    cases.append(dict(factors=count,scratch=depth,length=length,direction=direction,
                                      dirt=dirt,calls=calls,bits=bits,balanced_bits=precision(old_calls),
                                      squared_error=str(error),bound=str(bound)))
    return cases


def controls(module, costs, choices):
    names = []
    for n,s in ((2,0),(3,1),(127,8),(243,9)):
        try:
            module.build(n,s,costs,choices)
        except ValueError as error:
            require(str(error) == 'infeasible scratch budget','Wrong capacity rejection')
            names.append('infeasible_%d_%d' % (n,s))
        else:
            raise ValueError('Infeasible plan admitted')
    tree = module.build(5,3,costs,choices)
    word = list(module.instructions(tree))
    depth = module.resources(tree)[1]
    for name,mutant in {
        'omit_restoration':word[:4]+word[5:],
        'reverse_factor_order':[(s,t,4-i,q) for s,t,i,q in word],
    }.items():
        require(symbolic(mutant,5,depth) != expected_symbolic(5,depth,1),name+' escaped')
        names.append(name)
    wrong_inverse = [(s,t,i,-q) for s,t,i,q in module.instructions(((),()))]
    require(symbolic(wrong_inverse,2,1) != expected_symbolic(2,1,-1),'Sign-only inverse escaped')
    names.append('sign_only_inverse_even_factors')
    actual = sum(1 for _ in module.instructions(module.build(127,9,costs,choices)))
    require(actual != costs[9][127]-1,'Underpaid leaf bill escaped')
    names.append('underpaid_leaf_bill')
    arrays = [[(F(1),F(0))] for _ in range(depth+2)]
    before = copy.deepcopy(arrays)
    factors = [(False,(F(1,4),F(0)),F(1))]*5
    for label,scratch,phases,fs,message in (
        ('phase_alias',arrays[2:],arrays[0],factors,'phase array aliases mutable data'),
        ('scratch_short',arrays[2:-1],[(F(1),F(0))],factors,'dirty depth'),
        ('factor_short',arrays[2:],[(F(1),F(0))],factors[:-1],'tree factor count'),
    ):
        try:
            module.compose(None,*arrays[:2],fs,scratch,phases,F(1,2),8,1,tree)
        except ValueError as error:
            require(str(error) == message and arrays == before,'Wrong or late rejection: '+label)
            names.append(label)
        else:
            raise ValueError('Invalid interface admitted: '+label)
    return names


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write',type=Path,help='Write a new receipt')
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(),'Output already exists')
    source = json.loads((HERE/'SOURCES.json').read_text())
    for name,digest in source['files'].items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest() == digest,'Source changed: '+name)
    module = load('echo_trees',HERE/'trees.py')
    balanced = load('pr689_ternary',HERE/'vendor/pr689/ternary.py')
    leaf = load('rounded_leaf',HERE/'vendor/pr628/dirty.py')
    costs,choices = module.optimize(LIMIT,SCRATCH)
    table = check_table(module,costs,choices,balanced)
    print('PASS exact table and all finite resource witnesses',flush=True)
    result = dict(status='PASS_TERNARY_ECHO_SPACE_AUDIT',table=table,
                  identities=identities(module,costs,choices),
                  rounded=rounded(module,costs,choices,balanced,leaf),
                  negative_controls=controls(module,costs,choices),cost_table=costs)
    result = json.loads(json.dumps(result))
    if args.write:
        args.write.write_text(json.dumps(result,indent=2)+'\n')
    else:
        recorded = json.loads((HERE/'CERTIFICATE.json').read_text())
        require(json.dumps(recorded,sort_keys=True) == json.dumps(result,sort_keys=True),
                'Receipt differs')
    print(result['status'],table['cells'],'cells;',table['feasible_cells'],'literal witnesses;',
          len(result['negative_controls']),'controls')


if __name__ == '__main__':
    main()
