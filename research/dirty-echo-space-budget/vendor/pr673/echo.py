"""Multiway dirty echo composition of PR628's restored-input leaf shears.

Prepared for androolloyd with substantial OpenAI Codex assistance. Apache-2.0.
No new multiplication exponent is asserted. Read ECHO-PROOF.md for the storage
tradeoff and the complete inherited local error recurrence.
"""


def partition(count, fanout):
    if count < 1 or fanout < 2:
        raise ValueError('positive factor count and fanout >= 2 required')
    k = min(count, fanout)
    quotient, remainder = divmod(count, k)
    return [quotient + (i < remainder) for i in range(k)]


def resources(count, fanout):
    if count < 1 or fanout < 2:
        raise ValueError('positive factor count and fanout >= 2 required')
    if count == 1:
        return 0, 1
    sizes = partition(count, fanout)
    children = [resources(n, fanout) for n in sizes]
    scratch = len(sizes)-1 + max(depth for depth, _ in children)
    calls = sum((2 if i in (0, len(sizes)-1) else 4)*cost
                for i, (_, cost) in enumerate(children))
    return scratch, calls


def instructions(first, count, src, dst, scratch_first, fanout, sign=1):
    """Stream the exact instruction word or its reverse inverse."""
    if count == 1:
        yield src, dst, first, sign
        return
    sizes = partition(count, fanout)
    k = len(sizes)
    offsets = [first]
    for size in sizes[:-1]:
        offsets.append(offsets[-1]+size)
    # C: populate the whole dirty chain. D: the same chain without its first link.
    chain = [(offsets[i], sizes[i], src if i == 0 else scratch_first+i-1,
              scratch_first+i, 1) for i in range(k-1)]
    last = (offsets[-1], sizes[-1], scratch_first+k-2, dst, 1)
    invert = lambda commands: [(a,n,s,t,-q) for a,n,s,t,q in reversed(commands)]
    commands = chain + [last] + invert(chain) + chain[1:] + invert([last]) + invert(chain[1:])
    if sign == -1:
        commands = invert(commands)
    for a,n,s,t,q in commands:
        yield from instructions(a,n,s,t,scratch_first+k-1,fanout,q)


def compose(leaf_module, x, y, factors, scratch, phases, beta, bits, direction,
            sign=1, fanout=8):
    """Apply the dirty echo using a pinned PR628 leaf, restoring x and scratch."""
    if direction not in (-1,1) or sign not in (-1,1):
        raise ValueError('orientation and sign')
    depth, count = resources(len(factors), fanout)
    arrays = [x,y]+scratch
    if len(scratch) < depth:
        raise ValueError('dirty depth')
    if len({id(a) for a in arrays}) != len(arrays):
        raise ValueError('all ancestor arrays distinct')
    if any(phases is a for a in arrays):
        raise ValueError('phase array aliases mutable data')
    if not x or any(len(a) != len(x) for a in arrays) or len(phases) != len(x):
        raise ValueError('array lengths')
    if any(a*a+b*b != 1 for a,b in phases):
        raise ValueError('unit phases')
    stats = dict(leaves=0,scalar_steps=0)
    for src,dst,index,q in instructions(0,len(factors),0,1,2,fanout,sign):
        leaf_module.leaf(arrays[src],arrays[dst],factors[index],phases,beta,bits,
                         direction,q,stats)
    if stats['leaves'] != count:
        raise ValueError('leaf accounting')
    return stats
