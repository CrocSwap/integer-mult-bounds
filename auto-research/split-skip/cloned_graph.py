"""Replay pinned whole-chain clones with original core/cover envelopes.

Adapted from RaD/hipotures PR51 alternative_producer_clones.py, applied to Avi Eisenberg's PR53 skip-prefix graph (with Anthropic Claude assistance), retaining
Chafik Boukhalfa/OpenAI Codex's original-envelope graph family and finite
checks. The source-partition cloning idea and full-chain rewrite are credited
to RaD; this exact original-envelope specialization was prepared with OpenAI
Codex assistance. Apache-2.0. No search or optimization runs in this module.
"""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import array
import struct
import sys
from clone_io import read, require, integer
import importlib.util

ROOT = Path(__file__).resolve().parents[2]
# Adaptation: apply the unchanged PR54 replay to our pinned split-pair DAG.
from split_graph import graph as base_graph

HERE = Path(__file__).resolve().parent


def index(value, length, name, minimum=0):
    integer(value, name, minimum)
    require(value < length, 'Out-of-range '+name)
    return value


def pair(value, name):
    require(type(value) is list and len(value) == 2, 'Expected pair: '+name)
    return value


def digest(c):
    require(sys.byteorder == 'little', 'Little-endian binary interface required')
    roots = list(c.outputs.values())
    kinds = [int(len(target) == 1) for _, target in c.outputs]
    parts = [struct.pack('<4I', c.h, len(c.inputs), len(c.args), len(roots))]
    parts.append(array.array('I', (y for args in c.args for y in (args or (0, 0)))).tobytes())
    for code, values in [('Q', c.core), ('Q', c.union), ('I', roots), ('I', kinds)]:
        parts.append(array.array(code, values).tobytes())
    parts.append(bytes(int(x in c.active) for x in range(len(c.args))))
    return sha256(b''.join(parts)).hexdigest()


def scalar_supports(c, verify_outputs=True):
    h, n = c.h, len(c.args)
    triples = list(combinations(range(h), 3))
    require(c.inputs == triples, 'Wrong triple source enumeration')
    require(len(c.core) == len(c.union) == n, 'Wrong envelope array length')
    supports = [0]*n
    additions = 0
    for node in sorted(c.active):
        index(node, n, 'active node', 1)
        args = c.args[node]
        if args is None:
            index(node, len(triples)+1, 'source node', 1)
            mask = sum(1 << i for i in triples[node-1])
            require(c.core[node] == c.union[node] == mask, 'Wrong source envelope')
            supports[node] = 1 << (node-1)
        else:
            require(type(args) in (list, tuple) and len(args) == 2, 'Invalid addition')
            a, b = args
            for child in (a, b):
                index(child, node, 'addition operand', 1)
                require(child in c.active, 'Inactive addition operand')
            require(not supports[a]&supports[b], 'Overlapping scalar sources')
            supports[node] = supports[a]|supports[b]
            require(c.core[node] == c.core[a]&c.core[b], 'Wrong addition core')
            require(c.union[node] == c.union[a]|c.union[b], 'Wrong addition cover')
            require(c.core[node].bit_count() in (1, 2), 'Addition has no valid common core')
            additions += 1
    require(additions == c.additions, 'Wrong addition count')
    require(all(node in c.active for node in range(1, len(triples)+1)), 'Missing source')
    if verify_outputs:
        expected_keys = {(common, triple) for triple in triples for common in triple}
        expected_keys.update((common, (common,)) for common in range(h))
        require(set(c.outputs) == expected_keys, 'Incomplete terminal output enumeration')
        for (common, target), node in c.outputs.items():
            require(node in c.active, 'Inactive terminal output')
            omitted = set(target)-{common}
            expected = sum(1 << i for i, triple in enumerate(triples)
                           if common in triple and not omitted.intersection(triple))
            require(supports[node] == expected, 'Wrong exact scalar output')
            require(c.core[node] == 1 << common, 'Wrong output common point')
            require(c.union[node] == ((1 << h)-1)-sum(1 << x for x in omitted), 'Wrong output cover')
    return supports


class ClonedCircuit:
    def __init__(self, old, args, core, union, outputs, additions, clone_count):
        self.h = old.h
        self.inputs = old.inputs[:]
        self.args, self.core, self.union = args, core, union
        self.outputs, self.additions = outputs, additions
        self.active = set(range(1, len(args)))
        self.merged = old.merged
        self.clone_count = clone_count

    def verify(self):
        scalar_supports(self)
        return dict(h=self.h, inputs=len(self.inputs), partial_outputs=len(self.outputs),
                    additions=self.additions, roles=self.additions+len(self.outputs),
                    merged_additions=self.merged, cloned_additions=self.clone_count,
                    all_additions_disjoint=True, all_partial_outputs_exact=True,
                    every_node_has_common_point=True, circuit_sha256=digest(self))


def replay_round(c, document):
    require(type(document) is dict and set(document) == {
        'source_graph_sha256', 'output_graph_sha256', 'matching_before', 'jobs'}, 'Unexpected clone round fields')
    for key in ('source_graph_sha256', 'output_graph_sha256'):
        value = document[key]
        require(type(value) is str and len(value) == 64 and
                all(x in '0123456789abcdef' for x in value), 'Invalid graph digest')
    require(digest(c) == document['source_graph_sha256'], 'Clone source graph differs from pin')
    scalar = scalar_supports(c)
    n = len(c.args)
    ranks = [0]*n
    for x in c.active:
        ranks[x] = 1 if c.args[x] is None else c.union[x].bit_count()-c.core[x].bit_count()
    order = sorted(c.active, key=lambda x: (ranks[x], x))
    times = {x: i for i, x in enumerate(order)}
    roots = list(c.outputs.values())
    users = [[] for _ in range(n)]
    for x in order:
        if c.args[x] is not None:
            for pos, child in enumerate(c.args[x]):
                users[child].append(2*x+pos)
    for j, node in enumerate(roots):
        users[node].append((1 << 31)|j)

    def gate(node):
        index(node, n, 'gate', 1)
        require(node in c.active and c.args[node] is not None, 'Inactive or source gate')
        return node

    def use(e):
        integer(e, 'use index')
        require(e < 1 << 32, 'Use index does not fit uint32')
        if e >> 31:
            j = index(e & 0x7fffffff, len(roots), 'terminal use')
            return roots[j], roots[j], len(order)+j, n+j
        owner = gate(e//2)
        return c.args[owner][e%2], owner, times[owner], owner

    def nested(a, b):
        return not (c.core[b]&~c.core[a] or c.union[a]&~c.union[b])

    incoming, donors, next_use = set(), set(), {}
    links = document['matching_before']
    require(type(links) is list, 'Prior matching must be an array')
    for entry in links:
        donor, e = pair(entry, 'prior matching edge')
        gate(donor)
        value, target, _, event = use(e)
        require(donor not in donors and e not in incoming, 'Prior matching collision')
        require(value in c.args[donor], 'Prior carrier does not preserve actual operand')
        require((ranks[donor], donor) < (ranks[target], event), 'Noncausal prior carrier')
        require(nested(donor, target), 'Nonnested prior carrier')
        pos = c.args[donor].index(value)
        next_use[2*donor+pos] = e
        donors.add(donor)
        incoming.add(e)

    jobs = document['jobs']
    require(type(jobs) is list and jobs, 'Clone jobs must be a nonempty array')
    capacities, parents, formal, move, before, terminal = set(), set(), set(), {}, {}, []
    for i, job in enumerate(jobs):
        require(type(job) is dict and set(job) == {
            'parent', 'providers', 'source_children', 'first', 'chain'}, 'Unexpected clone job fields')
        parent = gate(job['parent'])
        providers = pair(job['providers'], 'providers')
        children = pair(job['source_children'], 'source children')
        first_value, _, first_time, _ = use(job['first'])
        require(first_value == parent and job['first'] not in incoming, 'Clone must start an actual parent chain')
        require(sum(e not in incoming for e in users[parent]) >= 2, 'Parent would lose its last chain')
        require(parent not in parents and parent not in formal, 'Conflicting clone parent')
        require(not set(children)&parents, 'Clone partition depends on another cloned parent')
        require(providers[0] != providers[1], 'Providers must be distinct')
        for provider, child in zip(providers, children):
            gate(provider)
            index(child, n, 'source child', 1)
            require(child in c.active and child in c.args[provider], 'Provider lacks named source child')
            require(provider not in donors and provider not in capacities, 'Provider capacity already used')
            require(times[provider] < first_time, 'Provider is not earlier than clone placement')
            require(nested(provider, parent), 'Provider does not fit original parent envelope')
        left, right = children
        require(not scalar[left]&scalar[right] and scalar[left]|scalar[right] == scalar[parent],
                'Clone partition does not equal parent with disjoint sources')
        require(c.core[left]&c.core[right] == c.core[parent] and
                c.union[left]|c.union[right] == c.union[parent], 'Clone original envelope differs from parent')
        chain = job['chain']
        require(type(chain) is list and chain, 'Clone chain must be a nonempty array')
        expected, seen, e = [], set(), job['first']
        while True:
            require(e not in seen, 'Prior chain contains a cycle')
            seen.add(e)
            require(use(e)[0] == parent, 'Chain does not preserve parent value')
            expected.append(e)
            if e not in next_use:
                break
            e = next_use[e]
        require(all(type(e) is int for e in chain) and chain == expected, 'Clone must replace one whole continuation chain')
        for e in chain:
            require(e not in move, 'Clone chains collide')
            move[e] = i
        if job['first'] >> 31:
            terminal.append(i)
        else:
            before.setdefault(job['first']//2, []).append(i)
        capacities.update(providers)
        parents.add(parent)
        formal.update(children)

    args, core, union, mapping, clones = [None], [0], [0], {}, {}

    def clone(i):
        job = jobs[i]
        parent, node, children = job['parent'], len(args), []
        for provider, old_child in zip(job['providers'], job['source_children']):
            edge = 2*provider+c.args[provider].index(old_child)
            require(edge not in move, 'Conservative clone source was itself replaced')
            require(old_child in mapping, 'Clone source is not yet available')
            children.append(mapping[old_child])
        require(all(child < node for child in children), 'Clone is not topological')
        clones[i] = node
        args.append(tuple(children))
        core.append(c.core[parent])
        union.append(c.union[parent])

    for old in order:
        for i in before.get(old, []):
            clone(i)
        mapping[old] = len(args)
        if c.args[old] is None:
            require(mapping[old] == old <= len(c.inputs), 'Source IDs changed')
            args.append(None)
        else:
            args.append(tuple(clones[move[e]] if e in move else mapping[c.args[old][e%2]]
                              for e in (2*old, 2*old+1)))
        core.append(c.core[old])
        union.append(c.union[old])
    for i in terminal:
        clone(i)
    outputs = {}
    for j, (target, old) in enumerate(c.outputs.items()):
        e = (1 << 31)|j
        outputs[target] = clones[move[e]] if e in move else mapping[old]
    result = ClonedCircuit(c, args, core, union, outputs, c.additions+len(jobs),
                           getattr(c, 'clone_count', 0)+len(jobs))
    scalar_supports(result)
    require(digest(result) == document['output_graph_sha256'], 'Clone output graph differs from pin')
    return result


def graph(h, document=None):
    require(type(h) is int and h in (23, 25), 'Uncertified clone dimension')
    document = read(HERE/f'clone-jobs-{h}.json') if document is None else document
    require(type(document) is dict and set(document) == {'h', 'rounds'}, 'Unexpected clone document fields')
    require(type(document['h']) is int and document['h'] == h, 'Wrong clone dimension')
    require(type(document['rounds']) is list and document['rounds'], 'Clone rounds must be a nonempty array')
    c = base_graph(h)
    for stage in document['rounds']:
        c = replay_round(c, stage)
    return c
