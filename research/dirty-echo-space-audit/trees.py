"""Exact finite planning for ternary dirty echoes with a scratch limit.

The echo rule is from androolloyd's PR673. Ali Romman added the finite planner
with substantial OpenAI Codex assistance. Apache-2.0. See PROOF.md.
"""


def require(condition, message):
    if not condition:
        raise ValueError(message)


def optimize(limit, max_scratch):
    """Return every optimum and a split witness; None means infeasible."""
    require(type(limit) is int and limit >= 1, 'positive integer factor limit')
    require(type(max_scratch) is int and max_scratch >= 0, 'nonnegative integer scratch limit')
    costs = [[None]*(limit+1) for _ in range(max_scratch+1)]
    choices = [[None]*(limit+1) for _ in range(max_scratch+1)]
    for scratch in range(max_scratch+1):
        costs[scratch][1] = 1
        if scratch >= 1 and limit >= 2:
            costs[scratch][2] = 4
        if scratch < 2:
            continue
        child = costs[scratch-2]
        pairs = [None]*(limit+1)
        for total in range(2,limit):
            for first in range(1,total):
                second = total-first
                if child[first] is None or child[second] is None:
                    continue
                candidate = (2*child[first]+4*child[second],first,second)
                if pairs[total] is None or candidate < pairs[total]:
                    pairs[total] = candidate
        for count in range(3,limit+1):
            best = None
            for total in range(2,count):
                last = count-total
                if pairs[total] is None or child[last] is None:
                    continue
                value,first,second = pairs[total]
                candidate = (value+2*child[last],first,second,last)
                if best is None or candidate < best:
                    best = candidate
            if best is not None:
                costs[scratch][count] = best[0]
                choices[scratch][count] = best[1:]
    return costs, choices


def build(count, scratch, costs, choices):
    require(type(count) is int and 1 <= count < len(costs[0]), 'factor count outside table')
    require(type(scratch) is int and 0 <= scratch < len(costs), 'scratch outside table')
    require(costs[scratch][count] is not None, 'infeasible scratch budget')
    if count == 1:
        return ()
    if count == 2:
        return (), ()
    return tuple(build(n,scratch-2,costs,choices) for n in choices[scratch][count])


def resources(tree):
    """Return (factors, borrowed arrays, leaf calls) for an explicit tree."""
    if not tree:
        return 1,0,1
    require(len(tree) == 3 or (len(tree) == 2 and not any(tree)), 'invalid ternary tree')
    children = [resources(child) for child in tree]
    weights = [2,2] if len(tree) == 2 else [2,4,2]
    return (sum(row[0] for row in children), len(tree)-1+max(row[1] for row in children),
            sum(weight*row[2] for weight,row in zip(weights,children)))


def instructions(tree, sign=1):
    """Stream the PR673 echo on the explicit ordered tree."""
    require(sign in (-1,1), 'sign must be +1 or -1')
    resources(tree)
    def emit(node, first, src, dst, scratch_first, direction):
        if not node:
            yield src,dst,first,direction
            return
        k = len(node)
        offsets = [first]
        for child in node[:-1]:
            offsets.append(offsets[-1]+resources(child)[0])
        chain = [(node[i],offsets[i],src if i == 0 else scratch_first+i-1,
                  scratch_first+i,1) for i in range(k-1)]
        last = (node[-1],offsets[-1],scratch_first+k-2,dst,1)
        def inverse(operations):
            return [(child,start,s,t,-q) for child,start,s,t,q in reversed(operations)]
        operations = chain+[last]+inverse(chain)+chain[1:]+inverse([last])+inverse(chain[1:])
        if direction == -1:
            operations = inverse(operations)
        for child,start,s,t,q in operations:
            yield from emit(child,start,s,t,scratch_first+k-1,q)
    yield from emit(tree,0,0,1,2,sign)


def compose(leaf_module, x, y, factors, scratch, phases, beta, bits, direction, tree, sign=1):
    """Run the unchanged PR628 leaf with the explicit echo tree."""
    count,depth,calls = resources(tree)
    require(direction in (-1,1) and sign in (-1,1), 'orientation and sign')
    require(len(factors) == count, 'tree factor count')
    require(len(scratch) >= depth, 'dirty depth')
    arrays = [x,y]+scratch
    require(len({id(a) for a in arrays}) == len(arrays), 'all ancestor arrays distinct')
    require(not any(phases is a for a in arrays), 'phase array aliases mutable data')
    require(x and all(len(a) == len(x) for a in arrays) and len(phases) == len(x), 'array lengths')
    require(all(a*a+b*b == 1 for a,b in phases), 'unit phases')
    stats = dict(leaves=0,scalar_steps=0)
    for src,dst,index,q in instructions(tree,sign):
        leaf_module.leaf(arrays[src],arrays[dst],factors[index],phases,beta,bits,direction,q,stats)
    require(stats['leaves'] == calls, 'leaf accounting')
    return stats
