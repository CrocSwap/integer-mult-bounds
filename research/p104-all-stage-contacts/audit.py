"""Exact contact checks by phase evaluation, not predecessor polynomial code.

Prepared with substantial OpenAI Codex assistance. Apache-2.0.
"""
from itertools import combinations

def need(ok, why):
    if not ok:
        raise ValueError(why)

def dot(a, b):
    return (a & b).bit_count() % 2

def phase(terms, x):
    return sum(c * dot(a, x) for a, c in terms) % 4

def core(q, basis):
    need(0 < q < 512 and dot(q, q) == 1, 'central port')
    need(len(basis) == 8 and all(0 < b < 512 for b in basis), 'central basis size')
    need(all(dot(b, q) == 0 for b in basis), 'basis fixes port')
    need(all(dot(a, b) == int(i == j) for i, a in enumerate(basis)
             for j, b in enumerate(basis)), 'orthonormal basis')
    axes = [1 << i for i in range(17)]
    swaps = [b ^ axes[9+i] for i, b in enumerate(basis)]
    def route(x):
        out = x
        for v in swaps:
            if dot(x, v):
                out ^= v
        return out
    columns = [route(x) for x in axes]
    need(all(route(route(x)) == x for x in axes), 'involution')
    need(all(dot(a, b) == int(i == j) for i, a in enumerate(columns)
             for j, b in enumerate(columns)), 'orthogonal route')
    need(route(q) == q, 'fixed port')
    center = [(a, 1) for a in axes[:9]]
    fresh = [(a, 1) for a in axes[9:]]
    pairs = [(center, fresh + [(q, 1)]),
             (center + [(q, -1)], fresh),
             (center + fresh, center + fresh),
             (center + fresh + [(q, -1)], center + fresh + [(q, -1)])]
    # A parity polynomial modulo four has degree at most two. Values at zero,
    # singleton and pair inputs determine every coefficient (see README).
    probes = [0, *axes, *(a | b for a, b in combinations(axes, 2))]
    maps = []
    for old, new in pairs:
        differences = [(phase(new, a) - phase(old, route(a))) % 4 for a in axes]
        need(all(d in (0, 2) for d in differences), 'even translation')
        shift = sum(a for a, d in zip(axes, differences) if d == 2)
        inverse = route(shift)
        for x in probes:
            need((phase(old, route(x)) + 2*dot(shift, x)) % 4 == phase(new, x),
                 'forward phase')
            need((phase(new, route(x)) + 2*dot(inverse, x)) % 4 == phase(old, x),
                 'inverse phase')
        maps.append({'translation': shift, 'inverse_translation': inverse})
    return maps

def embed(value, stage):
    return (value & 511) | ((value >> 9) << (9+8*(stage-1)))

def audit(caller, phases, ports):
    need(caller['ambient_rank'] == 161 and caller['stages'] == 19, 'caller dimensions')
    events = [e for e in caller['events'] if e[0] == 'LOCAL']
    need([e[1] for e in events] == list(range(1, 20)), 'ordered nineteen stages')
    need(len(ports) == 104 and len(set(ports)) == 104, 'port inventory')
    recipes = {r['q']: r for r in phases['recipes']}
    need(len(recipes) == len(phases['recipes']), 'unique recipes')
    cores = {q: core(q, recipes[q]['idle_children'][0]['orthogonal_axes'][:8]) for q in ports}
    records = []
    for _, stage, src, dst in events:
        need(src != dst and 0 <= src < 34 and 0 <= dst < 34, 'caller roles')
        for q in ports:
            maps = [{k: embed(v, stage) for k, v in m.items()} for m in cores[q]]
            need(all(v.bit_length() <= 161 and v.bit_count() <= 17
                     for m in maps for v in m.values()), 'translation allowance')
            records.append([stage, q, maps])
    return records
