"""Source-bound route census only; does not run or claim native qualification.

Adapted from #7627 swarm30_native_pairs.routes/changed and the independently
written 28-custody independent_pairs.compare. No historical chart PASS is
inherited: the returned union is the complete *fresh* verification inventory.
"""
from collections import defaultdict


def routes(word):
    if type(word.get('public')) is not int or word['public'] <= 0:
        raise ValueError('public boundary')
    result = {i: [] for i in range(word['public'])}
    for event in word['program']:
        if not isinstance(event, list) or not event:
            raise ValueError('event')
        if event[0] == 'MOVE':
            if len(event) < 4 or any(type(v) is not int or v < 0 for v in event[1:4]):
                raise ValueError('MOVE')
            if event[1] in result:
                result[event[1]].append(tuple(event[2:4]))
    return result


def changed(left, right):
    if left.keys() != right.keys():
        raise ValueError('public boundary mismatch')
    fields = [i for i in left if left[i] != right[i]]
    return fields, {edge for i in fields for edge in left[i] + right[i]}


def independent_compare(left, right):
    """Independent aggregation from literal events, in the custody style."""
    if left['public'] != right['public']:
        raise ValueError('public boundary mismatch')
    def collect(word):
        result = defaultdict(list)
        for event in word['program']:
            if event[0] == 'MOVE' and event[1] < word['public']:
                result[event[1]].append((event[2], event[3]))
        return result
    a, b = collect(left), collect(right)
    fields, edges = [], set()
    for i in range(left['public']):
        if a[i] != b[i]:
            fields.append(i)
            edges.update(a[i]); edges.update(b[i])
    return fields, edges


def inventory(words, historical_pairs):
    """Caller authenticates the five words and old receipt before invocation."""
    labels = ('base', 'source7624', 'source7626', 'source7627', 'candidate')
    if set(words) != set(labels) or not historical_pairs:
        raise ValueError('missing word or prior pair inventory')
    comparisons = [('base', x) for x in labels[1:]] + [
        ('source7624', 'source7626'), ('source7626', 'source7627'),
        ('source7627', 'candidate')]
    union = set(historical_pairs)
    detail = {}
    for left, right in comparisons:
        a = changed(routes(words[left]), routes(words[right]))
        b = independent_compare(words[left], words[right])
        if a != b:
            raise ValueError('independent route inventory disagreement')
        fields, edges = a
        detail[left + '__' + right] = {'fields': fields,
                                      'pairs': [list(x) for x in sorted(edges)]}
        union.update(edges)
    return {'comparisons': detail, 'full_validation_pairs': [list(x) for x in sorted(union)],
            'historical_pairs_used_as_inventory_only': True}
