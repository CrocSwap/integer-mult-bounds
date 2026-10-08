"""PR74 scalar-envelope order composed with PR71 and PR70 carry exchanges.

The reorder function is preserved from Thomas DiFiore's PR74 producer,
prepared with OpenAI Codex assistance. PR71 is Chafik Boukhalfa's split
construction; the copied carried-signal runner credits Alejandro's PR70.
Composition experiment: Dominik Scholz, substantial OpenAI GPT-6 Astra
assistance. Apache-2.0 and all inherited notices apply.
"""


def reorder(c):
    """Preserve source IDs and same-envelope order; verify scalar identities."""
    groups = {}
    for node in sorted(c.active):
        if c.args[node]:
            groups.setdefault((c.core[node], c.union[node]), []).append(node)

    def key(item):
        (core, union), nodes = item
        return union.bit_count() - core.bit_count(), -core, union, min(nodes)

    variables = len(c.inputs)
    ids = list(range(variables + 1)) + [
        x for _, nodes in sorted(groups.items(), key=key) for x in nodes
    ]
    mapping = {x: i for i, x in enumerate(ids)}
    args, core, union, provenance = c.args, c.core, c.union, c.provenance
    c.args = [tuple(mapping[y] for y in args[x]) if args[x] else None for x in ids]
    c.core = [core[x] for x in ids]
    c.union = [union[x] for x in ids]
    c.provenance = [provenance[x] for x in ids]
    c.active = {mapping[x] for x in c.active}
    c.outputs = {k: mapping[v] for k, v in c.outputs.items()}
    c.verify()
    return c
