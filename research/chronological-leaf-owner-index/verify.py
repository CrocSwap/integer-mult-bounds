"""Bounded exact program expansion and failure controls; no native admission."""
import argparse
from dataclasses import replace
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import types

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def steps(seq):
    return tuple((s.parent, s.kind, s.key, s.invocation) for s in seq)


def field(value):
    if hasattr(value, 'row'):
        return ('source', value.namespace, value.row)
    return ('owned', value.namespace, steps(value.calls), value.replica,
            value.path, value.point, value.ordinal, value.role)


def leaf(value):
    return steps(value.calls), value.rank, value.axis, field(value.field)


CASES = (
    ((('x', 2),), ((1, 'x'),), (), 2, 12),
    ((('x', 2), ('y', 3)), ((1, 'x'), (1, 'bank')), ('bank',), 3, 12),
    ((('x', 3), ('y', 5)), ((1, 'x'), (2, 'bank'), (2, 'y')), ('bank',), 5, 16),
    ((('x', 2), ('y', 2), ('z', 4)), ((1, 'x'), (1, 'bank'), (1, 'y')), ('bank',), 4, 12),
    ((('x', 2), ('y', 3)), ((1, 'x'), (1, 'bank')), ('bank',), 6, 14),
    ((('high', 8), ('low', 4), ('mid', 4)),
     ((2, 'low'), (3, 'private'), (2, 'private'), (1, 'high')), ('private',), 8, 12),
)


def run():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for source in manifest['files']:
        data = (HERE/source['local']).read_bytes()
        require(sha256(data).hexdigest() == source['sha256'], 'source byte pin')
        require(sha256(b'changed'+data).hexdigest() != source['sha256'], 'source mutation')
    X = load('checked_leaf_index', HERE/'leaf_index.py')
    O = load('independent_literal_oracle', HERE/'literal_oracle.py')
    L = load('retained_rank_library', HERE/'inputs/library.py')
    totals = {'ranks': 0, 'leaves': 0, 'calls': 0, 'ports': 0,
              'owned_leaves': 0, 'cross_replica_complements': 0}
    records, fixtures = [], []
    digest = sha256()
    for roles, rounds, owned, ambient, maximum in CASES:
        rows, flows = O.library(roles, rounds, owned, ambient, maximum)
        rule = X.C.Rule(roles, rounds, owned, ambient)
        engine = X.Compiler(rule, rows)
        if ambient == max(k for _, k in roles):
            target = tuple((k, sum(t == k for _, t in roles)) for k in sorted({k for _, k in roles}))
            paid = tuple((r, sum(t == r for t, _ in rounds)) for r in sorted({r for r, _ in rounds}))
            old = L.compile_library(L.Rule(target, paid), maximum)
            require([(r.replication, r.width, r.leaves, r.units) for r in rows[1:]] ==
                    [(r.replication, r.width, r.leaves, r.units) for r in old.rows[1:]],
                    'separate complete rank library')
        count = 0
        for n in range(1, maximum+1):
            expected, calls = O.expand(roles, rounds, owned, ambient, rows, flows, n)
            for ordinal, want in enumerate(expected):
                got = engine.locate(ordinal, n)
                require(leaf(got) == want, 'complete expanded leaf/owner order')
                require(engine.rank_leaf(got, n) == ordinal, 'ordinal inverse')
                totals['owned_leaves'] += int(want[3][0] == 'owned')
                digest.update((repr(want)+'\n').encode())
            for chain, q, inputs in calls:
                path = tuple(X.Step(*s) for s in chain)
                actual = tuple(field(engine.resolve_row(path, row, n))
                               for row in range(len(inputs)))
                require(actual == inputs, 'nested whole-child port vector')
                require(len(set(actual)) == len(actual), 'whole-input nonaliasing')
                totals['ports'] += len(inputs)
            if n >= ambient:
                node = engine.node(n)
                for source, _, _ in node.prefixes:
                    q, width = n-source, rows[n-source].width
                    size = node.groups.count(source)
                    for invocation in range(node.complements.invocations(source)):
                        first, last = invocation*width, (invocation+1)*width-1
                        totals['cross_replica_complements'] += int(first//size != last//size)
                for cut in flows[n].cuts:
                    for b in range(rows[n].replication):
                        owner = node.exit_owner(cut, b)
                        invocation, slot = node.exit_port(cut, owner)
                        step = X.Step(n, 'exit', cut, invocation)
                        require(node.caller_owner(step, slot) == owner,
                                'exit cut owner/port inverse')
            totals['ranks'] += 1
            totals['calls'] += len(calls)
            totals['leaves'] += len(expected)
            count += len(expected)
        records.append({'ambient': ambient, 'maximum': maximum,
                        'roles': roles, 'rounds': rounds, 'leaves': count})
        fixtures.append((roles, rounds, owned, ambient, rows, flows, maximum))

    controls = []

    def rejects(label, action):
        try:
            action()
        except (ValueError, TypeError, IndexError):
            controls.append(label)
            return
        raise ValueError('negative control accepted: '+label)

    roles, rounds, owned, a, rows, flows, n = fixtures[1]
    engine = X.Compiler(X.C.Rule(roles, rounds, owned, a), rows)
    item = engine.locate(rows[n].leaves-1)
    rejects('negative leaf', lambda: engine.locate(-1))
    rejects('one-past leaf', lambda: engine.locate(rows[n].leaves))
    rejects('wrong base axis', lambda: engine.rank_leaf(replace(item, axis=item.rank)))
    rejects('wrong physical return', lambda: engine.rank_leaf(replace(item, field=X.SourceRow('wrong', 0))))
    rejects('rank-zero program', lambda: engine.row(0))
    rejects('missing complete cut', lambda: engine.node(n).exit_rank(()))
    rejects('wrong child row', lambda: engine.resolve_row(item.calls, 1))
    rejects('zero complement call', lambda: engine.node(n).step_data(X.Step(n, 'complement', n, 0)))
    bad = list(rows)
    bad[n] = replace(bad[n], leaves=bad[n].leaves+1)
    rejects('wrong expanded leaf total', lambda: X.Compiler(engine.rule, bad).node(n))
    bad = list(rows)
    bad[1] = replace(bad[1], width=2)
    rejects('wrong sequential base', lambda: X.Compiler(engine.rule, bad))

    # Distinct cuts can revisit the SAME field. Only the qualified descriptor
    # is invertible; a global field->leaf map would be false.
    same_rule = X.C.Rule((('x', 2),), ((1, 'x'), (1, 'x')), ())
    same_rows, _ = O.library(same_rule.roles, same_rule.rounds, (), 2, 2)
    same = X.Compiler(same_rule, same_rows)
    left, right = same.locate(0), same.locate(1)
    require(left.field == right.field and left.calls != right.calls,
            'same owner at distinct chronological cuts')
    require(same.rank_leaf(left) != same.rank_leaf(right), 'cut qualification necessary')
    controls.append('owner-only key loses a leaf')

    # Source-preserving mutations of NEW code are checked against the separate
    # explicit recursive expansion, not against a second run of the index.
    original = (HERE/'leaf_index.py').read_text()
    mutations = (
        ('drop repeated paid-site multiplicity',
         'sum(count*self.suffix[h+1, rho*r]', 'sum(self.suffix[h+1, rho*r]'),
        ('merge chronological cuts', 'path += (chosen,)', 'path += (0,)'),
        ('merge replicas at exit',
         'replica = step.invocation*self.compiler.row(e).width+child_row',
         'replica = child_row'),
        ('drop owned invocation namespace', 'calls[:at], replica,', '(), replica,'),
    )
    for number, (label, old, new) in enumerate(mutations):
        require(original.count(old) == 1, 'unique mutation seam')
        mutant = types.ModuleType('leaf_mutant_'+str(number))
        mutant.__file__ = str(HERE/'leaf_index.py')
        sys.modules[mutant.__name__] = mutant
        exec(compile(original.replace(old, new), mutant.__file__, 'exec'), mutant.__dict__)
        detected = False
        for roles, rounds, owned, ambient, rows, flows, maximum in fixtures[1:4]:
            try:
                machine = mutant.Compiler(mutant.C.Rule(roles, rounds, owned, ambient), rows)
                expected, _ = O.expand(roles, rounds, owned, ambient, rows, flows, maximum)
                for ordinal, want in enumerate(expected):
                    if leaf(machine.locate(ordinal)) != want:
                        detected = True
                        break
            except ValueError:
                detected = True
            if detected:
                break
        require(detected, 'undetected semantic mutation: '+label)
        controls.append(label)

    # Large chronological cut set, with a direct base-eight/last-owned oracle.
    n, paid_count = 4096, 8
    roles = (('x', 2),)
    rounds = tuple((1, 'bank' if j % 3 == 1 else 'x') for j in range(paid_count))
    lib = L.compile_library(L.Rule(((2, 1),), ((1, paid_count),)), n)
    engine = X.Compiler(X.C.Rule(roles, rounds, ('bank',)), lib.rows, 'large-cuts')
    node = engine.node(n)
    size = lib.rows[n].leaves
    require(size == paid_count**(node.height+1), 'large explicit cut count')
    samples = sorted({0, 1, 7, 8, 9, size//3, size//2, size-2, size-1, 123456789})
    for ordinal in samples:
        value, cut = ordinal, [0]*(node.height+1)
        for j in range(node.height, -1, -1):
            value, cut[j] = divmod(value, paid_count)
        cut = tuple(cut)
        got = engine.locate(ordinal)
        want_call = ((n, 'exit', cut, 0),)
        bank = next((j for j in range(node.height, -1, -1)
                     if rounds[cut[j]][1] == 'bank'), None)
        want_field = (('source', 'large-cuts', 0) if bank is None else
                      ('owned', 'large-cuts', (), 0, cut[:bank],
                       (node.height-bank,), 0, 'bank'))
        require(leaf(got) == (want_call, 1, 0, want_field), 'large direct path/owner oracle')
        require(engine.rank_leaf(got) == ordinal, 'large ordinal inverse')
    large = {'rank': n, 'leaves': size, 'chronological_cuts': size,
             'suffix_states': len(node.suffix), 'source_states': len(node.groups.states),
             'queries': len(samples), 'expanded': False}

    # Independent explicit fields above are supplemented by a large replication
    # query; no enumeration or native interpretation is attached to this case.
    lib = L.compile_library(L.Rule(((3, 1), (5, 1)), ((1, 1), (2, 2))), 256)
    engine = X.Compiler(X.C.Rule((('x', 3), ('y', 5)),
                                ((1, 'x'), (2, 'bank'), (2, 'y')), ('bank',)), lib.rows)
    row = lib.rows[-1]
    positions = [0, 1, row.leaves//3, row.leaves//2, row.leaves-2, row.leaves-1]
    for ordinal in positions:
        require(engine.rank_leaf(engine.locate(ordinal)) == ordinal, 'large replica round trip')
    replication = {'rank': 256, 'replication': row.replication, 'width': row.width,
                   'leaves': row.leaves, 'queries': len(positions), 'expanded': False}
    require(totals['cross_replica_complements'] > 0, 'cross-replica coverage')
    return {'status': 'PASS_CHRONOLOGICAL_LEAF_OWNER_INDEX', 'totals': totals,
            'fixtures': records, 'expanded_trace_sha256': digest.hexdigest(),
            'negative_controls': controls, 'large_cut_fixture': large,
            'large_replication_fixture': replication, 'new_kappa': None}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    # JSON is the receipt's declared representation; tuples in input fixtures
    # are normalized to arrays before comparing, without changing science.
    result = json.loads(json.dumps(run(), sort_keys=True))
    destination = HERE/'VALIDATION.json'
    if args.write:
        destination.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    else:
        require(result == json.loads(destination.read_text()), 'committed receipt disagreement')
    print(json.dumps(result, sort_keys=True))
