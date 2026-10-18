"""Exact target-coordinate unions without enumerating descendant bits.

Douglas R. Colkitt's historical frame_data supplies the unchanged descendant
and source-union calculations. Adaptation by Stephan Arrington with substantial
OpenAI Codex assistance; Apache-2.0. See NOTICE.md and README.md.
"""
from certify import require


def frame_data(self):
    """Return the same three maps as DisjointTensor.frame_data.

    Union commutes with union: propagating the ground-coordinate mask of each
    output alongside its descendant bit gives the union over exactly the same
    reachable outputs. No target bitset, source union or rectangle check is
    omitted. As in the original, active nodes are topologically numbered.
    """
    descendants = {node: 0 for node in self.active}
    target_union = {node: 0 for node in sorted(self.active)}
    for i, target in enumerate(sorted(self.outputs)):
        node = self.outputs[target]
        descendants[node] |= 1 << i
        target_union[node] |= target
    for node in sorted(self.active, reverse=True):
        if self.args[node]:
            for parent in self.args[node]:
                descendants[parent] |= descendants[node]
                target_union[parent] |= target_union[node]
    source_union = {}
    for node in sorted(self.active):
        if self.args[node]:
            a, b = self.args[node]
            source_union[node] = source_union[a] | source_union[b]
        else:
            source_union[node] = self.inputs[node - 1]
        union = target_union[node]
        require(union and not union & source_union[node],
                'Node is not a disjoint rectangle')
    return descendants, source_union, target_union
