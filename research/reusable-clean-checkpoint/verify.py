"""Independent decorated-tree census and exact operator tests. Apache-2.0."""
import hashlib
import itertools
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from checkpoint import optimize, emit, execute, require

HERE = Path(__file__).resolve().parent


def shapes(lo, hi):
    if hi-lo == 1:
        yield ('leaf', lo)
    else:
        for k in range(lo+1, hi):
            for a in shapes(lo, k):
                for b in shapes(k, hi):
                    yield ('dirty', a, b)
                    yield ('clean', a, b)


def profile(t, weights, available=True):
    """Path-based oracle, no interval DP or emitter calls."""
    terms = []
    dirty_depths = []
    def walk(node, multiplier, dirty_depth, used_clean):
        if node[0] == 'leaf':
            terms.append(multiplier * weights[node[1]])
            dirty_depths.append(dirty_depth)
            return
        if node[0] == 'clean':
            if not available or used_clean:
                raise ValueError('two simultaneous clean connectors')
            walk(node[1], 2*multiplier, dirty_depth, True)
            walk(node[2], multiplier, dirty_depth, True)
        else:
            walk(node[1], 2*multiplier, dirty_depth+1, used_clean)
            walk(node[2], 2*multiplier, dirty_depth+1, used_clean)
    walk(t, 1, 0, False)
    return sum(terms), max(dirty_depths) + int(available)


def root_only(weights, cap):
    # Independent enumeration of all-dirty children, not balanced-only.
    best = None
    for tree in shapes(0, len(weights)):
        if tree[0] != 'clean':
            continue
        def all_dirty(t):
            return t[0] == 'leaf' or (t[0] == 'dirty' and all_dirty(t[1]) and all_dirty(t[2]))
        if not (all_dirty(tree[1]) and all_dirty(tree[2])):
            continue
        cost, space = profile(tree, weights)
        if space <= cap:
            best = cost if best is None else min(best, cost)
    return best


def matrix_value(factors, source):
    out = source[:]
    for m in factors:
        out = [sum(a*b for a,b in zip(row,out)) for row in m]
    return out


def check_word(tree, n, cap, nonlinear_check=True):
    word = emit(tree, dirty=tuple(range(3, cap+2)), clean=2)
    factors = [([[1, 1], [0, 1]] if i % 2 == 0 else [[1, 0], [1, 1]]) for i in range(n)]
    cases = 0
    # Complete real basis on every independent source/target/dirty coordinate.
    for role in [0, 1] + list(range(3,cap+2)):
        for coordinate in range(2):
            state = [[0,0] for _ in range(cap+2)]
            state[role][coordinate] = 1
            before = [a[:] for a in state]
            execute(word, state, factors, clean=2)
            expected = [a[:] for a in before]
            v = matrix_value(factors, before[0])
            expected[1] = [a+b for a,b in zip(expected[1], v)]
            require(state == expected, 'operator/order/restoration')
            execute(emit(tree, dirty=tuple(range(3,cap+2)), clean=2, sign=-1), state, factors, clean=2)
            require(state == before, 'inverse')
            cases += 1
    # Nonlinear zero-preserving leaves: restoration survives, ordered ideal
    # matrix-product semantics are deliberately not asserted for this case.
    if not nonlinear_check:
        return cases
    state = [[r+1,2-r] for r in range(cap+2)]
    state[2] = [0,0]
    before = [a[:] for a in state]
    nonlinear = lambda i,x: [(i+1)*v*v + v for v in x]
    execute(word,state,factors,clean=2,leaf=nonlinear)
    require(all(state[r] == before[r] for r in range(len(state)) if r != 1), 'nonlinear restoration')
    execute(emit(tree,dirty=tuple(range(3,cap+2)),clean=2,sign=-1),state,factors,clean=2,leaf=nonlinear)
    require(state == before, 'nonlinear inverse')
    return cases


def rejected(action):
    try:
        action()
    except ValueError:
        return 1
    raise ValueError('negative control accepted')


def run():
    comparisons = trees_checked = basis_cases = 0
    for n in range(2,7):
        valid = []
        for t in shapes(0,n):
            try:
                _,space = profile(t,[1]*n)
            except ValueError:
                continue
            valid.append((t,space))
            if n <= 5:
                basis_cases += check_word(t,n,space)
                trees_checked += 1
        for weights in itertools.product((1,3),repeat=n):
            oracle = [(profile(t,weights)[0],space) for t,space in valid]
            for cap in range(1,n):
                admissible = [cost for cost,space in oracle if space <= cap]
                if not admissible:
                    require(rejected(lambda: optimize(weights,cap)) == 1,'infeasible cap')
                else:
                    cost,tree = optimize(weights,cap)
                    require(cost == min(admissible),'independent minimum')
                    require(profile(tree,weights)[0] == cost and profile(tree,weights)[1] <= cap,'oracle witness')
                comparisons += 1
    fixtures = []
    for weights,cap in [([1,3,1,1],2),([1]*54,6),([1,3,1,1]*3,4)]:
        cost,tree = optimize(weights,cap)
        word = emit(tree,dirty=tuple(range(3,cap+2)),clean=2)
        require(sum(weights[i] for i,_,_,_ in word) == cost,'weighted word bill')
        if len(weights) <= 6:
            baseline = root_only(weights,cap)
        else:
            baseline = min(2*optimize(weights[:k],cap-1,False)[0]+optimize(weights[k:],cap-1,False)[0]
                           for k in range(1,len(weights)) if max(k,len(weights)-k) <= 2**(cap-1))
        # Large nonlinear words can grow astronomical integers. Full linear
        # basis replay still runs on these fixtures; nonlinear checks are small.
        if len(weights) <= 6:
            basis_cases += check_word(tree,len(weights),cap)
        else:
            basis_cases += check_word(tree,len(weights),cap,nonlinear_check=False)
        fixtures.append(dict(prices=weights,cap=cap,cost=cost,root_only_cost=baseline,leaf_calls=len(word),tree=tree))
    tree=fixtures[0]['tree'];word=emit(tree,dirty=(3,),clean=2)
    factors=[[[1,1],[0,1]],[[1,0],[1,1]],[[1,1],[0,1]],[[1,0],[1,1]]]
    initial=[[1,2],[3,4],[0,0],[5,6]]
    expected=[a[:] for a in initial];expected[1]=[a+b for a,b in zip(initial[1],matrix_value(factors,initial[0]))]
    mutations = [word[:-1],[(3-i,s,d,v) for i,s,d,v in word],[(i,s,d,-v if j==0 else v) for j,(i,s,d,v) in enumerate(word)]]
    for changed in mutations:
        state=[a[:] for a in initial];execute(changed,state,factors,clean=2)
        require(state!=expected,'mutation escaped detection')
    bad=[a[:] for a in initial];bad[2]=[1,0];snapshot=[a[:] for a in bad]
    negatives=rejected(lambda: execute(word,bad,factors,clean=2))
    require(bad==snapshot,'admission mutated arrays')
    negatives+=rejected(lambda: emit(tree,dirty=(2,),clean=2))
    negatives+=rejected(lambda: emit(tree,dirty=(),clean=2))
    negatives+=rejected(lambda: optimize([True],1))
    negatives+=rejected(lambda: execute(word,[initial[0],initial[0],[0,0],[5,6]],factors,clean=2))
    result=dict(base='66849e1475c930fd7732b1a0067ffee7e1e95f60',seed=54,comparisons=comparisons,trees_checked=trees_checked,basis_cases=basis_cases,negative_controls=negatives+len(mutations),fixtures=fixtures)
    pins=json.loads((HERE/'SOURCES.json').read_text())
    for name,sha in pins['sha256'].items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==sha,'source pin '+name)
    import importlib.util
    spec=importlib.util.spec_from_file_location('pr714',HERE/'vendor/pr714-checkpoint.py')
    predecessor=importlib.util.module_from_spec(spec);spec.loader.exec_module(predecessor)
    require(predecessor.plan(54)['leaf_calls']==fixtures[1]['cost']==2112,'actual predecessor uniform count')
    return json.loads(json.dumps(result))


if __name__ == '__main__':
    import sys
    result=run()
    if '--write' in sys.argv:
        (HERE/'EXPECTED.json').write_text(json.dumps(result,indent=2)+'\n')
    else:
        require(result==json.loads((HERE/'EXPECTED.json').read_text()),'certificate mismatch')
    print('PASS_REUSABLE_CLEAN_CHECKPOINT',result['comparisons'],'census cases;',result['basis_cases'],'basis cases; weighted 20 -> 16; uniform54 2112; no new kappa')
