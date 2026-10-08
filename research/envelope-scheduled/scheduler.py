"""Region-order hook for the scheduled envelope-balanced candidate.

The pinned envelope-balanced compiler fixes one region order per axis through
`balanced_split_graph.configuration(h)['schedule']` (axis 23 `cover-core`,
axis 25 `reverse-node`).  Everything else about the compiler -- the graph, the
groups, the coarse/future-completion settings, the carry-exchange passes, the
coordinate-conjugated oracle pricing, the exchange engine and the ranking -- is
untouched.

This module records the substitution used for the two candidate axes: the same
`ordered_build` contract, with the region order taken from one of the keys
below instead of the pinned schedule.  The wrapper keeps the topological and
carrier-candidate assertions of the pinned builder, so an order that would
break the schedule is rejected rather than silently compiled.

`research/envelope-balanced/compiler.py` embeds this table inside its
`local_ordered_build` and selects the entry through the `B82_MODE` environment
variable; `verify.py --regenerate` recompiles both axes through that compiler
and asserts byte equality with the shipped words, so the embedded table and
this record cannot drift apart.
"""

MODES = {23: 'node-asc', 25: 'width-node'}

COVER_CORE = 'cover-core'


def order_keys(mode, blocks, hashlib):
    """Return the sort key selecting the region order for one compiled axis."""
    rank = lambda g: blocks[g]['rank']
    frame = lambda g: blocks[g]['frame']
    width = lambda g: frame(g)[1].bit_count() - frame(g)[0].bit_count()
    random_key = lambda seed, g: int(hashlib.sha256(('%d:%d' % (seed, g)).encode()).hexdigest()[:12], 16)
    table = {
        COVER_CORE:    lambda g: (rank(g), frame(g)[1], frame(g)[0]),
        'reverse-node': lambda g: (rank(g), -min(blocks[g]['nodes'])),
        'core-asc':    lambda g: (rank(g), frame(g)[0], frame(g)[1]),
        'core-desc':   lambda g: (rank(g), -frame(g)[0], -frame(g)[1]),
        'node-asc':    lambda g: (rank(g), min(blocks[g]['nodes'])),
        'union-desc':  lambda g: (rank(g), -frame(g)[1], frame(g)[0]),
        'width-asc':   lambda g: (rank(g), width(g), frame(g)[1]),
        'width-desc':  lambda g: (rank(g), -width(g), frame(g)[1]),
        'width-node':  lambda g: (rank(g), width(g), min(blocks[g]['nodes'])),
    }
    if mode.startswith('rnd'):
        seed = int(mode[3:] or 0)
        return lambda g: (rank(g), random_key(seed, g))
    if mode not in table:
        raise ValueError(mode)
    return table[mode]


def ordered_build(original, h, mode):
    """Same contract as the pinned region builder with an explicit region order."""
    import hashlib

    key = order_keys(mode, {}, hashlib)  # validates the mode name eagerly

    def build(dimension):
        parts = list(original(dimension))
        blocks, uses, owner = parts[1], parts[2], parts[4]
        parts[6] = sorted(range(len(blocks)), key=order_keys(mode, blocks, hashlib))
        position = {g: i for i, g in enumerate(parts[6])}
        for g, block in enumerate(blocks):
            for x in block['inputs']:
                assert position[owner[x]] < position[g], 'Non-topological region order'
            for u, _ in block['candidates']:
                assert position[g] < position[uses[u][1]], 'Backward carrier candidate'
        return tuple(parts)

    assert key is not None
    return build


def control():
    """The pinned schedule reproduced by the cover-core key.

    `cover-core` is the pinned schedule of axis 23; with that mode the compiler
    regenerates `research/envelope-balanced/original-23.json.gz` byte for byte.
    """
    return COVER_CORE
