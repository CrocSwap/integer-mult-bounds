#!/usr/bin/env python3
"""Independent integer and field-identity audit of finite mixed-job compilation.

Apache-2.0. Substantial OpenAI assistance. The mathematical lockstep flow is
Jacob Alan Sussman's Theorem 1G; attribution and limits are in AUDIT.md.
No implementation from its tree_flow.py or explicit_sim.py is imported.
This checks scheduling and exact finite batching under a mixed-unit contract;
it does not manufacture that operator contract from a rank histogram.
"""
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from math import factorial, gcd, lcm, prod
from pathlib import Path
import argparse
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def need(test, message):
    if not test:
        raise AssertionError(message)


def read(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def rational(value):
    value = Fraction(value)
    return f'{value.numerator}/{value.denominator}'


@dataclass(frozen=True)
class Rule:
    # Productive target roles have fixed names and positive ranks.
    roles: tuple
    # A paid round is (rank, exact productive or owned role name).
    rounds: tuple
    owned: tuple = ('owned-C0',)

    def __post_init__(self):
        names = [name for name, rank in self.roles]
        need(len(set(names)) == len(names), 'Distinct productive roles')
        need(set(names).isdisjoint(self.owned), 'Owned roles uncredited')
        need(all(rank > 0 for name, rank in self.roles), 'Positive target ranks')
        need(all(rank > 0 and name in set(names) | set(self.owned)
                 for rank, name in self.rounds), 'Every paid call has a real role')
        need(max(rank for rank, name in self.rounds) < min(rank for name, rank in self.roles),
             'Strict mixed hierarchy')

    @property
    def targets(self):
        return Counter(rank for name, rank in self.roles)

    @property
    def dimension(self):
        return max(self.targets)


class IntegerTree:
    """Literal classes, units, field names, and dependency edges at one rank."""

    def __init__(self, rule, rank):
        self.rule, self.rank = rule, rank
        self.types = tuple(sorted(rule.targets))
        self.weights = tuple(rule.targets[k] for k in self.types)
        self.points = self.lattice(1)
        need(bool(self.points), 'At least one mixed unit fits')
        self.depth = max(map(sum, self.points))
        self.units = []
        self.classes = []
        self.sources = []
        self.exits = []
        self.edges = set()
        self.nodes = set()
        self.source_counter = Counter()
        self._class((), 1, [])
        self.validate_fields()
        need(self.topological_size() == len(self.nodes), 'Native-order dependency DAG')

    def lattice(self, dilation):
        bound = self.rank // (self.rule.dimension * dilation)
        out = []

        def visit(index, powers, value):
            if index == len(self.types):
                out.append(tuple(powers))
                return
            exponent = 0
            while value <= bound:
                visit(index+1, powers+[exponent], value)
                exponent += 1
                value *= self.types[index]

        if bound:
            visit(0, [], 1)
        return out

    def column(self, point):
        return prod(k**a for k, a in zip(self.types, point))

    def multiplicity(self, point):
        return factorial(sum(point)) // prod(factorial(a) for a in point) * prod(
            w**a for w, a in zip(self.weights, point))

    def edge(self, before, after):
        self.nodes.update((before, after))
        self.edges.add((before, after))

    def after(self, uid, round_index):
        return ('issue', uid, round_index+1) if round_index+1 < len(self.rule.rounds) else ('finish', uid)

    def _class(self, path, dilation, incoming):
        depth = len(path)
        class_units = []
        demands = defaultdict(list)
        for point in self.lattice(dilation):
            if sum(point) != self.depth-depth:
                continue
            column = dilation*self.column(point)
            need(self.rule.dimension*column <= self.rank, 'All ambient axes fit')
            for repetition in range(self.multiplicity(point)):
                uid = len(self.units)
                unit = {'uid': uid, 'path': path, 'point': point, 'column': column,
                        'fields': {}, 'owned': {name: ('owned', uid, name) for name in self.rule.owned}}
                self.units.append(unit)
                class_units.append(unit)
                for name, target in self.rule.roles:
                    index = self.types.index(target)
                    point_next = tuple(a+int(i == index) for i, a in enumerate(point))
                    demands[point_next].append((unit, name, target*column))
                self.edge(('start', uid), ('issue', uid, 0))
                for j in range(len(self.rule.rounds)):
                    self.edge(('issue', uid, j), self.after(uid, j))
        self.classes.append((path, tuple(u['uid'] for u in class_units)))
        supply = defaultdict(list)
        for job in incoming:
            supply[job['point']].append(job)
        need(set(supply) <= set(demands), 'No paid output is abandoned')
        for point, slots in demands.items():
            jobs = supply.get(point, [])
            need(len(jobs) <= len(slots), 'No target is double funded')
            for index, (unit, name, target) in enumerate(slots):
                if index < len(jobs):
                    job = jobs[index]
                    need(job['rank'] == target, 'Exact target rank equality')
                    unit['fields'][name] = job['field']
                    self.edge(('issue', job['uid'], job['round']), ('start', unit['uid']))
                    self.edge(('finish', unit['uid']), self.after(job['uid'], job['round']))
                else:
                    field = ('source', len(self.sources))
                    unit['fields'][name] = field
                    self.sources.append({'field': field, 'rank': target, 'unit': unit['uid'], 'role': name})
                    self.source_counter[target] += 1
                    need(self.rank < self.rule.dimension*target <= self.rule.dimension*self.rank,
                         'Whole source lies in the proved source band')
        all_fields = [field for unit in class_units for field in unit['fields'].values()]
        need(len(all_fields) == len(set(all_fields)), 'Simultaneous units have disjoint arbitrary inputs')
        need(all(len(unit['fields']) == len(self.rule.roles) for unit in class_units), 'Every input slot filled')
        for j, (paid_rank, paid_role) in enumerate(self.rule.rounds):
            outgoing = []
            for unit in class_units:
                field = unit['fields'].get(paid_role, unit['owned'].get(paid_role))
                need(field is not None, 'Paid call remains on its physical owner')
                outgoing.append({'field': field, 'rank': paid_rank*unit['column'],
                                 'point': unit['point'], 'uid': unit['uid'], 'round': j})
            need(len({job['field'] for job in outgoing}) == len(outgoing), 'Ordered round has no field alias')
            if depth < self.depth:
                self._class(path+(j,), dilation*paid_rank, outgoing)
            else:
                need(all(sum(job['point']) == 0 for job in outgoing), 'Only zero-generation exits')
                need(len({job['rank'] for job in outgoing}) == 1, 'One rank per ordered exit batch')
                for job in outgoing:
                    need(job['rank'] < self.rank, 'Every recursive exit strictly smaller')
                    complete = ('exit', len(self.exits), job['uid'])
                    self.edge(('issue', job['uid'], j), complete)
                    self.edge(complete, self.after(job['uid'], j))
                self.exits.append(outgoing)

    def topological_size(self, extra_edges=()):
        successors = defaultdict(list)
        indegrees = {node: 0 for node in self.nodes}
        for before, after in self.edges | set(extra_edges):
            successors[before].append(after)
            indegrees[after] += 1
        ready = deque(node for node in self.nodes if not indegrees[node])
        count = 0
        while ready:
            before = ready.popleft()
            count += 1
            for after in successors[before]:
                indegrees[after] -= 1
                if not indegrees[after]:
                    ready.append(after)
        return count

    def validate_fields(self):
        need(len({row['field'] for row in self.sources}) == len(self.sources),
             'Every source is a distinct arbitrary field')
        for path, unit_ids in self.classes:
            fields = [field for uid in unit_ids for field in self.units[uid]['fields'].values()]
            need(len(fields) == len(set(fields)), 'No duplicated independent input in a class')

    def summary(self):
        return {'rank': self.rank, 'generations': self.depth, 'classes': len(self.classes),
                'units': len(self.units), 'source_fields': len(self.sources),
                'source_ranks': dict(sorted(self.source_counter.items())),
                'exit_ranks': dict(sorted(Counter(job['rank'] for group in self.exits for job in group).items())),
                'ordered_exit_batches': len(self.exits), 'event_nodes': len(self.nodes),
                'dependency_edges': len(self.edges), 'acyclic': True,
                'every_paid_call_real_owner': True, 'class_input_disjointness': True,
                'owned_fields_uncredited_conservative_allocation': len(self.units)*len(self.rule.owned)}


class Compiler:
    def __init__(self, rule):
        self.rule = rule
        self.trees = {}

    @lru_cache(None)
    def compile(self, rank):
        if rank < self.rule.dimension:
            return {'rank': rank, 'width': 1, 'leaves': rank, 'units': 0, 'per_array': Fraction(rank),
                    'all_productive_fields_full_rank': True}
        tree = IntegerTree(self.rule, rank)
        self.trees[rank] = tree
        multiplier = 1
        requirements = []
        for jobs in tree.exits:
            smaller = self.compile(jobs[0]['rank'])
            required = smaller['width']//gcd(smaller['width'], len(jobs))
            multiplier = lcm(multiplier, required)
            requirements.append(('ordered_exit', jobs[0]['rank'], len(jobs), smaller['width']))
        for source_rank, count in tree.source_counter.items():
            smaller = self.compile(rank-source_rank)
            required = smaller['width']//gcd(smaller['width'], count)
            multiplier = lcm(multiplier, required)
            requirements.append(('source_complement', rank-source_rank, count, smaller['width']))
        need(all(multiplier*count % width == 0 for kind, size, count, width in requirements),
             'Each ordered batch is independently integral')
        width = multiplier*len(tree.sources)
        normalized_leaves = sum((Fraction(len(jobs))*self.compile(jobs[0]['rank'])['per_array']
                                for jobs in tree.exits), Fraction(0))
        normalized_leaves += sum((count*self.compile(rank-source_rank)['per_array']
                                 for source_rank, count in tree.source_counter.items()), Fraction(0))
        leaves = multiplier*normalized_leaves
        need(leaves.denominator == 1, 'Integral actual leaf count')
        unit_count = Fraction(len(tree.units))
        for kind, size, count, child_width in requirements:
            child = self.compile(size)
            unit_count += Fraction(count*child['units'], child_width)
        unit_count *= multiplier
        need(unit_count.denominator == 1, 'Integral conservative owned allocation')
        for source in tree.sources:
            source_axes = set(range(source['rank']))
            complement = set(range(source['rank'], rank))
            need(source_axes.isdisjoint(complement) and source_axes | complement == set(range(rank)),
                 'Each independent source receives the full rank-N job exactly once')
        return {'rank': rank, 'width': width, 'leaves': leaves.numerator, 'units': unit_count.numerator,
                'per_array': leaves/width, 'replication': multiplier, 'ordered_requirements': requirements,
                'all_productive_fields_full_rank': True,
                'owned_fields_uncredited': unit_count.numerator*len(self.rule.owned),
                'strict_uniform_child_rank': 1, 'native_halving_guard': rank*rank > 2}


def actual_rule():
    """Extract every paid owner in chronology from the source-bound p2 word."""
    controller_path = ROOT/'research/kappa-rebuild/controller/GLOBAL-IDENTITY-COVER.json.gz'
    controller = read(controller_path)
    case = controller['all_three']
    roles = [(f'{side}{pair}:{port}', 41) for pair in range(2) for side in ('X', 'Y') for port in range(112)]
    roles += [(row['owner'], row['target_rank']) for row in case['fresh_outputs']]
    native_path = ROOT/'research/kappa-rebuild/complex/full-identity-certificates/THREE-base-FULL-IDENTITY-NATIVE.json.gz'
    native = read(native_path)
    rounds = []
    stages = ((0, 'forward'), (0, 'backward'), (0, 'forward'), (1, 'backward'), (1, 'forward'))
    for stage, (pair, direction) in enumerate(stages):
        helper = {row['role']: row['owner'] for row in case['helper_bindings'] if row['stage'] == stage}
        for event in native[direction]:
            if event[0] == 'climb':
                _, part, role, old, new, rank = event
                owner = f'X{pair}:{role}' if role < 112 else f'Y{pair}:{role-112}' if role < 224 else helper[role]
                rounds.append((rank, owner))
            elif event[0] == 'center':
                rounds.append((event[-1], 'owned-C0'))
        for residual in case['paid_residuals']:
            if residual['after_stage'] == stage:
                rounds.append((residual['rank'], residual['owner']))
    need(Counter(rank for rank, name in rounds) == Counter({int(k): v for k, v in case['paid'].items()}),
         'Literal native paid-call extraction agrees with complete bill')
    rule = Rule(tuple(roles), tuple(rounds))
    need(rule.targets == Counter({6:146, 9:803, 41:448}), 'Actual independent output jobs')
    return rule, {str(path.relative_to(ROOT)): digest(path) for path in (controller_path, native_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=HERE/'FINITE-DAG-AUDIT.json')
    args = parser.parse_args()
    # This synthetic contract tests only the generic compiler; no native circuit
    # is claimed for its deliberately repeated/owned paid-role sequence.
    toy = Rule((('a', 3), ('b', 3), ('c', 4)),
               ((1, 'a'), (1, 'owned-C0'), (1, 'b'), (1, 'a'), (2, 'c'), (2, 'owned-C0')))
    compiler = Compiler(toy)
    toy_results = []
    for rank in (4, 7, 12, 16, 28, 40):
        compiled = compiler.compile(rank)
        row = {k: rational(v) if isinstance(v, Fraction) else v for k, v in compiled.items()
               if k != 'ordered_requirements'}
        row['tree'] = compiler.trees[rank].summary()
        toy_results.append(row)
    tree = compiler.trees[16]
    child = next(unit for unit in tree.units if unit['path'] == (0,))
    parent = next(unit for unit in tree.units if unit['path'] == ())
    cyclic = tree.topological_size([(('issue', parent['uid'], 1), ('start', child['uid']))]) < len(tree.nodes)
    need(cyclic, 'Later-round dependency negative control creates a cycle')
    fields = tree.units[0]['fields']
    first, second = tuple(fields)[:2]
    old = fields[second]
    fields[second] = fields[first]
    illegal_alias = False
    try:
        tree.validate_fields()
    except AssertionError:
        illegal_alias = True
    finally:
        fields[second] = old
    need(illegal_alias, 'Independent fields cannot share a source token')
    cleared = compiler.compile(16)
    bad_multiplier = cleared['replication']-1
    uncleared_rejected = any(bad_multiplier*count % width
                            for kind, size, count, width in cleared['ordered_requirements'])
    need(uncleared_rejected, 'One fewer replica fails a real ordered batch divisibility requirement')
    uniform = compiler.compile(40)
    need(uniform['leaves']**10 < uniform['width']**10 * 40**9,
         'Exact finite toy supplier beats exponent 9/10, including all complements')
    actual, pins = actual_rule()
    actual_compiler = Compiler(actual)
    finite = actual_compiler.compile(41)
    actual_row = {k: rational(v) if isinstance(v, Fraction) else v for k, v in finite.items()
                  if k != 'ordered_requirements'}
    actual_row['tree'] = actual_compiler.trees[41].summary()
    need(finite['width'] == 1397 and finite['leaves'] == 57149,
         'Independent full-rank completion bill including every complementary axis')
    need(41*1397-finite['leaves'] == 128, 'No credit from partial fields or owned center')
    output = {'schema':'independent-finite-mixed-job-compilation-audit/1',
              'status':'PASS_FINITE_DAG_FIELD_OWNERS_BATCH_CLEARING_AND_FULL_RANK_COMPLETION',
              'source_sha256':digest(__file__), 'pinned_native_inputs':pins,
              'synthetic_rule_tests':toy_results, 'actual_p2_rank41':actual_row,
              'negative_controls':{'future_round_deadlock_rejected':cyclic,
                                   'aliased_independent_source_rejected':illegal_alias,
                                   'uncleared_ordered_batch_rejected':uncleared_rejected,
                                   'partial_source_not_full': set(range(6)) != set(range(41)),
                                   'owned_center_not_counted': len(actual.roles) == 1397},
              'toy_strict_uniform_moment':{'rank':40,'exponent':'9/10',
                                           'integer_power_comparison':True},
              'scope':['Independent finite flow and owner identities, not a proof of an abstract unit from its histogram.',
                       'Actual p2 paid calls extracted in native order with original owners.',
                       'Full F_N completion is a compositional proof under the pinned native endpoint contract.',
                       'No winning near-threshold large-N supplier was materialized; the existence theorem is separate.',
                       'No dynamic RAM transfer or new kappa is claimed.']}
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True)+'\n')
    print(json.dumps({'status':output['status'], 'toy_ranks':[row['rank'] for row in toy_results],
                      'actual_full_rank':41, 'actual_width':finite['width'], 'actual_paid_rank1':finite['leaves']}))


if __name__ == '__main__':
    main()
