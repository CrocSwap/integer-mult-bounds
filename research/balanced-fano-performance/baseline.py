"""Balance the Fano DAG, then exhaust the local reversible binary model.

The meet-in-the-middle algorithm tests existence with a free permutation of
unprescribed roles. Keeping one prefix per key is sufficient for existence,
but not for enumerating all possible complete words or output permutations.
"""
from hashlib import sha256

from certify import require
from experiments.fano_completion import FANO_EDGES


GL2 = ((1, 2), (2, 1), (1, 3), (3, 2), (2, 3), (3, 1))


def balanced_fano():
    order = ('a', 'b', 'c', 'u1', 'u2', 'u3', 'u4', 'u5', 'u6', 'u7', 'u8', 'u9', 'u10', 'ta', 'tb', 'tc')
    source = {'a': 0, 'b': 1, 'c': 2}
    edge_roles = {}; next_role = 3; pairs = []; gates_at = []
    auxiliary_inputs = []; auxiliary_outputs = []; targets = {}
    for vertex in order:
        incoming = [i for i, (u, v) in enumerate(FANO_EDGES) if v == vertex]
        outgoing = [i for i, (u, v) in enumerate(FANO_EDGES) if u == vertex]
        roles = [edge_roles[i] for i in incoming]
        if vertex in source: roles.append(source[vertex])
        output_count = len(outgoing)+int(vertex in ('ta', 'tb', 'tc'))
        width = max(len(roles), output_count)
        require(width in (1, 2), 'Unexpected local width')
        while len(roles) < width:
            auxiliary_inputs.append((vertex, next_role))
            roles.append(next_role); next_role += 1
        if width == 2:
            pairs.append(tuple(roles)); gates_at.append(vertex)
        for edge, role in zip(outgoing, roles): edge_roles[edge] = role
        occupied = len(outgoing)
        if vertex in ('ta', 'tb', 'tc'):
            targets[vertex] = roles[occupied]; occupied += 1
        auxiliary_outputs.extend((vertex, r) for r in roles[occupied:])
    require(next_role == 10 and len(pairs) == 14, 'Wrong balanced model size')
    outputs = list(targets.values())+[r for v, r in auxiliary_outputs]
    require(sorted(outputs) == list(range(next_role)), 'Output roles are not a partition')
    return dict(W=next_role, pairs=pairs, gate_vertices=gates_at,
                prescribed={0: targets['ta'], 1: targets['tb'], 2: targets['tc']},
                auxiliary_inputs=auxiliary_inputs, auxiliary_outputs=auxiliary_outputs,
                edge_roles=[edge_roles[i] for i in range(len(FANO_EDGES))])


def execute(W, pairs, choices):
    require(len(pairs) == len(choices), 'One choice per gate required')
    rows = [1 << i for i in range(W)]
    for (a, b), k in zip(pairs, choices):
        values = (0, rows[a], rows[b], rows[a]^rows[b])
        x, y = GL2[k]
        rows[a], rows[b] = values[x], values[y]
    return tuple(rows)


def columns(rows):
    W = len(rows)
    return tuple(sum(((row >> j) & 1) << i for i, row in enumerate(rows)) for j in range(W))


def assignments(W, pairs):
    pairs = tuple(pairs)
    def descend(depth, rows, word):
        if depth == len(pairs):
            yield rows, word
            return
        a, b = pairs[depth]; x, y = rows[a], rows[b]
        values = (0, x, y, x^y)
        for k, (s, t) in enumerate(GL2):
            new = list(rows); new[a] = values[s]; new[b] = values[t]
            yield from descend(depth+1, tuple(new), word+(k,))
    yield from descend(0, tuple(1 << i for i in range(W)), ())


def inverse_choice(k):
    for j in range(6):
        if execute(2, [(0, 1), (0, 1)], [k, j]) == (1, 2): return j
    raise ValueError('GL2 inverse missing')


def existence(W, pairs, prescribed=None, half_budget=300000):
    """Exact complete search, not a heuristic or solver-unsat certificate."""
    prescribed = dict(prescribed or {})
    require(W >= 2 and all(0 <= i < W and 0 <= j < W for i, j in prescribed.items()), 'Invalid fixed terminals')
    require(len(set(prescribed.values())) == len(prescribed), 'Fixed terminal outputs repeat')
    require(all(len(p) == 2 and p[0] != p[1] and all(0 <= i < W for i in p) for p in pairs), 'Invalid ports')
    split = len(pairs)//2
    require(max(6**split, 6**(len(pairs)-split)) <= half_budget, 'Half-enumeration budget exceeded')
    source_fixed = tuple(sorted(prescribed))
    output_fixed = tuple(prescribed[i] for i in source_fixed)
    def key(cols, fixed):
        return tuple(cols[i] for i in fixed)+tuple(sorted(cols[i] for i in range(W) if i not in fixed))
    width = (W+7)//8
    def packed(key): return b''.join(v.to_bytes(width, 'big') for v in key)
    seen = {}; prefix_hash = sha256(); suffix_hash = sha256(); prefix_count = suffix_count = 0
    for rows, word in assignments(W, pairs[:split]):
        k = key(columns(rows), source_fixed)
        seen.setdefault(k, (rows, word))
        prefix_hash.update(packed(k)); prefix_count += 1
    found = None
    for rows, word in assignments(W, list(reversed(pairs[split:]))):
        # These are inverse-suffix words. Inversion is a bijection on GL2,
        # so this enumeration covers every possible suffix exactly once.
        cols = columns(rows); k = key(cols, output_fixed)
        suffix_hash.update(packed(k)); suffix_count += 1
        if k not in seen: continue
        A, prefix_word = seen[k]
        rho = tuple(cols.index(c) for c in columns(A))
        suffix_word = tuple(inverse_choice(j) for j in reversed(word))
        full_word = prefix_word+suffix_word
        transfer = execute(W, pairs, full_word)
        require(all(transfer[rho[i]] == 1 << i for i in range(W)), 'Recovered scalar permutation is wrong')
        require(all(rho[i] == j for i, j in prescribed.items()), 'Recovered terminals are wrong')
        found = dict(choices=full_word, rho=rho)
        break
    return dict(W=W, gates=len(pairs), split=split, prescribed=prescribed,
                prefix_assignments=prefix_count, prefix_keys=len(seen), suffix_assignments=suffix_count,
                prefix_sha256=prefix_hash.hexdigest(), suffix_sha256=suffix_hash.hexdigest(),
                full_assignment_count=6**len(pairs), exists=found is not None,
                exhaustive_negative=found is None, witness=found,
                scope='Existence with a free permutation of unprescribed roles; not an enumeration of every matching circuit.')
