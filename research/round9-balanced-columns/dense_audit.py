"""Independent dense supports for both balanced-column scalar graphs.

Dominik Scholz with substantial OpenAI GPT-6 Astra assistance. Apache-2.0.
Does not use the graph's memoized/provenance-based support routine.
"""
from hashlib import sha256
from pathlib import Path
import json
import run


def audit(h):
    c = run.schedule_variant.reorder(run.coarse_graph.graph(h, coarse='columns'))
    support = [0] * len(c.args)
    point_rows = [0] * h
    for i, triple in enumerate(c.inputs):
        support[i + 1] = 1 << i
        for point in triple:
            point_rows[point] |= 1 << i
    additions = 0
    for node in sorted(c.active):
        if not c.args[node]:
            assert node <= len(c.inputs)
            continue
        a, b = c.args[node]
        assert a < node and b < node
        assert support[a] and support[b]
        assert not support[a] & support[b]
        support[node] = support[a] | support[b]
        assert c.core[node] == c.core[a] & c.core[b]
        assert c.union[node] == c.union[a] | c.union[b]
        additions += 1
    for (common, target), node in c.outputs.items():
        expected = point_rows[common]
        for point in target:
            if point != common:
                expected &= ~point_rows[point]
        assert support[node] == expected
    return dict(h=h, inputs=len(c.inputs), additions=additions,
                outputs=len(c.outputs), all_dense_additions_disjoint=True,
                all_dense_partial_outputs_exact=True,
                original_common_point_envelopes_exact=True)


if __name__ == '__main__':
    root = Path(__file__).resolve().parent
    result = {'scope': 'Finite dense scalar/data-output identity audit',
              'axes': {str(h): audit(h) for h in (23, 25)},
              'sources': {name: sha256((root/name).read_bytes()).hexdigest()
                          for name in ('dense_audit.py', 'coarse_graph.py',
                                       'schedule_variant.py')}}
    (root/'dense-audit.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
