"""Exact entry data for the existing sampler core. Ali Romman, with Codex. Apache-2.0."""

PHASES = tuple(pow(2, k, 169) for k in range(156))


def weights(a, b):
    if type(a) is not int or type(b) is not int or not (0 <= a < 52 and 0 <= b < 52):
        raise ValueError('floor residues must be integers from 0 through 51')
    return ((52 - a) * (52 - b), (52 - a) * b, a * (52 - b), a * b)


def describe(a, b):
    original = weights(a, b)
    tail = tuple(value % 169 for value in original)
    roots = sum(tail) // 169
    result = dict(a=a, b=b, tail=list(tail), roots=roots)
    if a % 13 and b % 13:
        c, d = (10 * a) % 13, (10 * b) % 13
        phase = a * b * pow(c * d, -1, 169) % 169
        result.update(kind='core', c=c, d=d, phase=phase, phase_index=PHASES.index(phase))
    elif roots == 0:
        result['kind'] = 'dyadic'
    elif a == 0 or b == 0:
        result['kind'] = 'endpoint'
    else:
        result['kind'] = 'mixed'
    return result


def prefix(a, b, coins):
    original = weights(a, b)
    if len(coins) != 4 or any(type(coin) is not int or coin not in (0, 1) for coin in coins):
        raise ValueError('supply four binary prefix coins')
    if a == b == 0:
        return dict(label=0, node=None, used=0)
    node = 0
    for depth, coin in enumerate(coins, 1):
        leaves = [i for i, value in enumerate(original)
                  if ((1 << depth) * value) // 2704 - 2 * (((1 << (depth - 1)) * value) // 2704)]
        child = 2 * node + coin
        if child < len(leaves):
            return dict(label=leaves[child], node=None, used=depth)
        node = child - len(leaves)
    return dict(label=None, node=node, used=4)
