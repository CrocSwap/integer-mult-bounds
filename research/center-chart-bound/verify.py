"""Exact global subspace closure; Apache-2.0, OpenAI Codex assistance.

Source word: Cao Yifan/PR4610. Phase-chart predecessor: Dugongue/PR4654.
This checks a nine-axis monotone-frame model, not a multiplication theorem.
"""
from collections import Counter, deque
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
FULL = (1 << 512) - 1


def need(ok, message):
    if not ok:
        raise ValueError(message)


def space(basis):
    points = {0}
    for v in basis:
        need(type(v) is int and 0 < v < 512, 'nonzero nine-bit vector')
        points |= {x ^ v for x in tuple(points)}
    need(len(points) == 2 ** len(basis), 'independent binary basis')
    return sum(1 << x for x in points)


def dim(bits):
    size = bits.bit_count()
    need(size > 0 and size & (size - 1) == 0, 'power-of-two subspace size')
    return size.bit_length() - 1


def mv(columns, x):
    out = 0
    for i, v in enumerate(columns):
        if x >> i & 1:
            out ^= v
    return out


def invert(columns):
    table = {mv(columns, x): x for x in range(512)}
    need(len(table) == 512, 'invertible logical warp')
    return [table[1 << i] for i in range(9)]


def join(x, y):
    if x & y == x:
        return y
    if x & y == y:
        return x
    out, todo = y, x
    while todo:
        bit = todo & -todo
        todo -= bit
        v = bit.bit_length() - 1
        if not out >> v & 1:
            old = out
            while old:
                z = old & -old
                old -= z
                out |= 1 << (v ^ (z.bit_length() - 1))
    return out


def build(c, word):
    spaces = list(map(space, c['frames']))
    nodes, fixed, arcs, centers = [], set(), [], []
    current, zero = {}, True
    paid = Counter()

    def node(f, freeze=False):
        n = len(nodes)
        nodes.append(spaces[f])
        if freeze:
            fixed.add(n)
        return n

    def inclusion(a, b, tag=0):
        arcs.append((a, b, tag))

    for r, f in enumerate(c['start']):
        current['L', r] = node(f, r < 224)
    for e in word:
        kind = e[0]
        if kind in ('climb', 'center'):
            if kind == 'climb':
                _, _, r, a, b, width = e
                role = ('L', r)
                need(spaces[a] & spaces[b] == spaces[a], 'ascending persistent transport')
            else:
                _, r, a, b, width = e
                role = ('C', r)
            old = current[role]
            need(nodes[old] == spaces[a], 'paid input chart')
            need(width > 0 and width == abs(dim(spaces[a]) - dim(spaces[b])), 'paid width')
            new = node(b)
            low, high = (old, new) if dim(spaces[a]) < dim(spaces[b]) else (new, old)
            need(nodes[low] & nodes[high] == nodes[low], 'nested center/paid spaces')
            if kind == 'center':
                centers.append((low, high))
            else:
                inclusion(low, high)
            paid[width] += 1
            current[role] = new
        elif kind == 'warp':
            _, reg, op, a, b = e
            role = tuple(reg)
            old = current[role]
            need(nodes[old] == spaces[a], 'logical warp input chart')
            new = node(b)
            inclusion(old, new, op)
            inclusion(new, old, -op)
            current[role] = new
        elif kind == 'adapter':
            fixed.add(current['L', e[2]])
        elif kind == 'scalar':
            g, f = e[1:]
            role, contact = tuple(g[1]), node(f)
            if g[0] == 'clear':
                need(role == ('C', 0), 'only owned scratch cleared')
                current[role], zero = contact, True
                continue
            need(g[0] in ('add', 'copy', 'scale'), 'known scalar operation')
            refs = g[1:3] if g[0] in ('add', 'copy') else g[1:2]
            for typ, r in refs:
                old = current[typ, r]
                need(nodes[old] == spaces[f], 'original common scalar chart')
                if typ == 'L':
                    inclusion(old, contact)
                elif not zero:
                    # The retained owned protocol has no call between these contacts.
                    inclusion(old, contact)
                    inclusion(contact, old)
                current[typ, r] = contact
            if any(typ == 'C' for typ, _ in refs):
                zero = False
        else:
            need(kind == 'phase', 'known inert marker')
    for r, f in enumerate(c['final']):
        old = current['L', r]
        need(nodes[old] == spaces[f], 'original final chart')
        inclusion(old, node(f, r < 224))
    need(paid == {1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}, 'entire paid source profile')
    need(len(centers) == 8, 'eight complete center calls')
    return nodes, fixed, arcs, centers


def solve(c, word, reverse_queue=False):
    nodes, fixed, arcs, centers = build(c, word)
    maps = {w['op']: w['G_columns'] for w in c['warps']}
    maps.update({-op: invert(cols) for op, cols in list(maps.items())})
    permutations = {op: [mv(cols, x) for x in range(512)] for op, cols in maps.items()}
    cache = {}

    def image(bits, tag):
        if not tag or bits in (1, FULL):
            return bits
        key = bits, tag
        if key not in cache:
            out, todo = 0, bits
            while todo:
                z = todo & -todo
                todo -= z
                out |= 1 << permutations[tag][z.bit_length() - 1]
            cache[key] = out
        return cache[key]

    successors, predecessors = [[] for _ in nodes], [[] for _ in nodes]
    for a, b, tag in arcs:
        need(image(nodes[a], tag) & nodes[b] == image(nodes[a], tag), 'original graph feasibility')
        successors[a].append((b, tag))
        predecessors[b].append((a, -tag))
    reports = {}
    for lower in (True, False):
        bounds = [1 if lower else FULL for _ in nodes]
        q = deque(sorted(fixed))
        for i in q:
            bounds[i] = nodes[i]
        adjacency = successors if lower else predecessors
        while q:
            a = q.pop() if reverse_queue else q.popleft()
            for b, tag in adjacency[a]:
                moved = image(bounds[a], tag)
                value = join(bounds[b], moved) if lower else bounds[b] & moved
                if value != bounds[b]:
                    bounds[b] = value
                    q.append(b)
        need(all(bounds[i] == nodes[i] for i in fixed), 'fixed physical interfaces preserved')
        for i, old in enumerate(nodes):
            need(bounds[i] & old == (bounds[i] if lower else old), 'source lies inside certified interval')
        for a, b, tag in arcs:
            need(image(bounds[a], tag) & bounds[b] == image(bounds[a], tag), 'fixed-point arc closure')
        reports['lower' if lower else 'upper'] = [[dim(bounds[a]), dim(bounds[b])] for a, b in centers]
    need(all(pair == [0, 8] for pair in reports['lower']), 'every center high contains eight forced axes')
    need(all(pair[0] == 0 for pair in reports['upper']), 'every center low is forced zero')
    return {'nodes':len(nodes), 'fixed_nodes':len(fixed), 'inclusion_arcs':len(arcs),
            'center_bounds_low_high':reports, 'unavoidable_center_rank_mass':64}


def main():
    raw = (HERE/'inputs/round3-native.json.gz').read_bytes()
    pins = json.loads((HERE/'SOURCES.json').read_text())
    pin = next(x for x in pins['files'] if x['path'].endswith('round3-native.json.gz'))
    need(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'original PR4610 bytes')
    payload = json.loads(gzip.decompress(raw))
    need(set(payload['programs']) == {'forward', 'backward'}, 'both source orientations')
    c = payload['canonical']
    need(len(c['start']) == len(c['final']) == 632, 'all persistent fields')
    result = {d:solve(c, w) for d, w in sorted(payload['programs'].items())}
    for d, w in payload['programs'].items():
        need(solve(c, w, True) == result[d], 'opposite fixed-point worklist order')
    changed = deepcopy(c)
    for basis in changed['frames']:
        if len(basis) >= 2:
            basis[0] ^= basis[1]
    need(solve(changed, payload['programs']['forward']) == result['forward'], 'all frame basis changes')
    need(dim(join(space([1]), space([2]))) == 2 and join(space([1]), space([2])) == space([1,2]),
         'join is XOR span, not set union')
    rejected = []
    for label in ('center_width', 'warp_chart', 'dependent_frame_basis'):
        bad = deepcopy(payload)
        word = bad['programs']['forward']
        if label == 'center_width':
            next(e for e in word if e[0] == 'center')[4] -= 1
        elif label == 'warp_chart':
            next(e for e in word if e[0] == 'warp' and bad['canonical']['frames'][e[3]])[4] = 0
        else:
            basis = next(b for b in bad['canonical']['frames'] if len(b) >= 2)
            basis[0] = basis[1]
        try:
            solve(bad['canonical'], word)
        except (ValueError, KeyError):
            rejected.append(label)
        else:
            raise ValueError('source mutation accepted: '+label)
    result['controls'] = {'source_mutations_rejected':rejected,
                          'opposite_worklist_order':True, 'all_frame_basis_changes':True,
                          'xor_span_join':True}
    path = HERE/'RESULT.json'
    if '--write' in sys.argv:
        path.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        need(result == json.loads(path.read_text()), 'committed center interval equality')
    print('PASS_CENTER_CHART_BOUND: both orientations; every retained center has rank >=8; no new kappa')


if __name__ == '__main__':
    main()
