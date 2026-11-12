"""Independent direct chronology/field oracle; no author oracle or library DP.

The tested implementation is loaded only to compare its public results.
"""
from dataclasses import dataclass
from hashlib import sha1, sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys
import types

EXPECTED = 'fed9b8fe71f69d02bd1dc796f13d4311b8460d24860c246ce246997d5ca96724'


def need(truth, message):
    if not truth:
        raise ValueError(message)


@dataclass(frozen=True)
class Row:
    replication: int
    width: int
    leaves: int


def height(rank, ambient):
    h = 0
    while ambient*2**(h+1) <= rank:
        h += 1
    return h


def library(ambient, maximum):
    """One rank-two role, three rank-one sites; intentionally nonminimal a."""
    rows = [None]
    for n in range(1, maximum+1):
        if n < ambient:
            rows.append(Row(1, 1, n))
        else:
            h = height(n, ambient)
            e = n-2**(h+1)
            # Sole fresh source has rank 2**(h+1). All later x slots inherit.
            t = 1+n % 3
            a = t*rows[e].width
            rows.append(Row(a, a, t*rows[e].leaves+a*3**(h+1)))
    return rows


def direct(ambient, rows, rank, namespace):
    """Materialize ordered calls and leaves using explicit physical vectors."""
    leaves, calls = [], []
    sites = ('x', 'bank', 'x')

    def visit(n, path, fields):
        calls.append((path, tuple(fields)))
        if n < ambient:
            need(len(fields) == 1, 'direct base width')
            for axis in range(n):
                leaves.append((path, n, axis, fields[0]))
            return
        h = height(n, ambient)
        s, e = 2**(h+1), n-2**(h+1)
        a, child_width = rows[n].replication, rows[e].width
        need(a == len(fields), 'direct source width')
        for v in range(a//child_width):
            step = (n, 'complement', s, v)
            block = fields[v*child_width:(v+1)*child_width]
            visit(e, path+(step,), block)
        for cut in product(range(3), repeat=h+1):
            for replica in range(a):
                field = fields[replica]
                # A bank site selects this unit's fresh field. Later x sites
                # carry that identity. No production owner routine is used.
                for at, site in enumerate(cut):
                    if sites[site] == 'bank':
                        field = ('owned', namespace, path, replica,
                                 cut[:at], (h-at,), 0, 'bank')
                visit(1, path+((n, 'exit', cut, replica),), [field])

    visit(rank, (), [('source', namespace, row) for row in range(rows[rank].width)])
    need(len(leaves) == rows[rank].leaves, 'direct recurrence count')
    return leaves, calls


def canonical_steps(steps):
    return tuple((s.parent, s.kind, s.key, s.invocation) for s in steps)


def canonical_field(value):
    if hasattr(value, 'row'):
        return ('source', value.namespace, value.row)
    return ('owned', value.namespace, canonical_steps(value.calls), value.replica,
            value.path, value.point, value.ordinal, value.role)


def canonical_leaf(value):
    return canonical_steps(value.calls), value.rank, value.axis, canonical_field(value.field)


def reconstructed_leaf(module, expected):
    calls, rank, axis, field = expected
    calls = tuple(module.Step(*s) for s in calls)
    if field[0] == 'source':
        identity = module.SourceRow(field[1], field[2])
    else:
        _, namespace, prefix, replica, path, point, ordinal, role = field
        identity = module.OwnedBank(namespace, tuple(module.Step(*s) for s in prefix),
                                    replica, path, point, ordinal, role)
    return module.Leaf(calls, rank, axis, identity)


def load(path, name, mutation=None):
    if mutation is None:
        spec = spec_from_file_location(name, path)
        module = module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    source = path.read_text()
    old, new = mutation
    need(source.count(old) == 1, 'unique independent mutant seam')
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(source.replace(old, new), str(path), 'exec'), module.__dict__)
    return module


def check(module, ambient, maximum, all_ranks=True):
    rows = library(ambient, maximum)
    namespace = 'independent-A'+str(ambient)
    rule = module.C.Rule((('x', 2),), ((1, 'x'), (1, 'bank'), (1, 'x')),
                         ('bank',), ambient)
    engine = module.Compiler(rule, rows, namespace)
    totals = {'leaves': 0, 'calls': 0, 'ports': 0, 'wide_calls': 0,
              'owned_leaves': 0, 'nested_owner_namespace_leaves': 0}
    digest = sha256()
    for rank in (range(1, maximum+1) if all_ranks else (maximum,)):
        expected, calls = direct(ambient, rows, rank, namespace)
        for ordinal, want in enumerate(expected):
            actual = engine.locate(ordinal, rank)
            need(canonical_leaf(actual) == want, 'direct chronological leaf/field mismatch')
            need(engine.rank_leaf(reconstructed_leaf(module, want), rank) == ordinal,
                 'independently formed descriptor inverse')
            if want[3][0] == 'owned':
                totals['owned_leaves'] += 1
                totals['nested_owner_namespace_leaves'] += int(len(want[3][2]) > 0)
            digest.update((repr(want)+'\n').encode())
        for path, fields in calls:
            typed = tuple(module.Step(*s) for s in path)
            actual = tuple(canonical_field(engine.resolve_row(typed, i, rank))
                           for i in range(len(fields)))
            need(actual == fields, 'direct input-vector return map')
            need(len(set(actual)) == len(actual), 'one whole call aliases fields')
            totals['wide_calls'] += int(len(fields) > 1)
            totals['ports'] += len(fields)
        totals['calls'] += len(calls)
        totals['leaves'] += len(expected)
    totals['trace_sha256'] = digest.hexdigest()
    totals['ambient'] = ambient
    totals['maximum'] = maximum
    return totals


def run(path):
    need(sha256(path.read_bytes()).hexdigest() == EXPECTED, 'frozen program changed')
    manifest = json.loads((path.parent/'SOURCES.json').read_text())
    for item in manifest['files']:
        data = (path.parent/item['local']).read_bytes()
        need(len(data) == item['bytes'], 'source size')
        need(sha256(data).hexdigest() == item['sha256'], 'source SHA256')
        blob = sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(blob == item['git_blob'], 'source Git blob')
    module = load(path, 'independent_subject')
    records = [check(module, 3, 36), check(module, 5, 18)]
    mutations = (
        ('complement_invocation',
         'step.invocation, child_row))', '0, child_row))'),
        ('base_axis',
         'return Leaf(calls, rank, ordinal, self.resolve_row',
         'return Leaf(calls, rank, (ordinal+1)%rank, self.resolve_row'),
        ('owned_call_prefix', 'calls[:at], replica,', '(), replica,'),
    )
    detected = []
    for number, (label, old, new) in enumerate(mutations):
        mutant = load(path, 'independent_mutant_'+str(number), (old, new))
        try:
            check(mutant, 3, 20)
        except ValueError as error:
            detected.append({'mutation': label, 'failure': str(error)})
        else:
            raise ValueError('independent oracle failed to detect '+label)
    return {'status': 'PASS_INDEPENDENT_DIRECT_RECURSION',
            'program_sha256': EXPECTED, 'source_pins': len(manifest['files']),
            'cases': records, 'mutants': detected,
            'scope': 'single rank-two role, three ordered rank-one sites, nonminimal supplied libraries; no selected native instantiation'}


if __name__ == '__main__':
    print(json.dumps(run(Path(sys.argv[1]).resolve()), sort_keys=True, indent=2))
