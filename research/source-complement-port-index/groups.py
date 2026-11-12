"""True source-rank buckets and exact whole-complement invocation ports.

Offline metadata only; no payload movement or smaller native program is free.
Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from bisect import bisect_left
from dataclasses import dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
INPUT = HERE/'inputs/source_index/source_index.py'
EXPECTED = 'e978025591b06770026b9879f1e5b10827424f410794fb2b1e1f10a720f49176'
if sha256(INPUT.read_bytes()).hexdigest() != EXPECTED:
    raise ValueError('frozen source-row index hash')
spec = spec_from_file_location('grouping_source_index', INPUT)
I = module_from_spec(spec)
sys.modules[spec.name] = I
spec.loader.exec_module(I)
C = I.C


class ProductCounts:
    """Sorted integer products and exact word counts; absent products count zero."""
    def __init__(self, rows):
        ordered = sorted(rows)
        keys, values = [], []
        for key, value in ordered:
            if keys and key == keys[-1]:
                values[-1] += value
            else:
                keys.append(key)
                values.append(value)
        self.keys, self.values = tuple(keys), tuple(values)

    def get(self, key):
        at = bisect_left(self.keys, key)
        return self.values[at] if at < len(self.keys) and self.keys[at] == key else 0

    def items(self):
        return zip(self.keys, self.values)


class _RankBucket:
    """One retained true-rank subtree table; every physical path stays distinct."""
    def __init__(self, groups, source_rank):
        self.groups, self.rank = groups, source_rank
        self.local = I.SortedStateTable(groups.states)
        self.total = I.SortedStateTable(groups.states)
        for state in reversed(groups.states):
            h, rho, previous = state
            local = self._local(state)
            total = local
            if h < groups.index.height:
                for rank, multiplicity in groups.index.paid.items():
                    total += multiplicity*self.total[h+1, rho*rank, rank]
            self.local[state], self.total[state] = local, total
        self.size = self.total[0, 1, 0]

    def fresh(self, state):
        h, _, previous = state
        return h == 0 or self.groups.rule.ambient*self.rank > self.groups.rank*previous

    def _local(self, state):
        if not self.fresh(state):
            return 0
        h, rho, _ = state
        words = self.groups.products[self.groups.index.height-h]
        count = 0
        for rank, weight in zip(self.groups.index.types, self.groups.index.weights):
            divisor = rho*rank
            if (self.groups.rule.ambient*self.rank <= self.groups.rank*rank
                    and self.rank % divisor == 0):
                count += weight*words.get(self.rank//divisor)
        return count

    def blocks(self, state):
        if not self.fresh(state):
            return
        h, rho, _ = state
        for point, column, units in self.groups.index.point_data[self.groups.index.height-h]:
            product = rho*column
            if self.rank % product:
                continue
            role_rank = self.rank//product
            i = bisect_left(self.groups.index.types, role_rank)
            if (i < len(self.groups.index.types) and self.groups.index.types[i] == role_rank
                    and self.groups.rule.ambient*product <= self.groups.rank):
                yield point, column, units, self.groups.index.weights[i], role_rank

    def roles(self, rank):
        return tuple(name for name, value in self.groups.rule.roles if value == rank)

    def rank_source(self, unit, role):
        self.groups.index.flow.validate_unit(unit)
        C.require(self.groups.job_rank(unit, role) == self.rank, 'true source-rank mismatch')
        state, offset = (0, 1, 0), 0
        for chosen in unit.path:
            h, rho, _ = state
            offset += self.local[state]
            for rank, _ in self.groups.rule.rounds[:chosen]:
                offset += self.total[h+1, rho*rank, rank]
            rank = self.groups.rule.rounds[chosen][0]
            state = (h+1, rho*rank, rank)
        for point, _, units, weight, rank in self.blocks(state):
            if point < unit.point:
                offset += units*weight
            elif point == unit.point:
                return offset+unit.ordinal*weight+self.roles(rank).index(role)
            else:
                break
        raise ValueError('not a fresh source of this rank')

    def unrank_source(self, ordinal):
        C.natural(ordinal, 'rank-bucket ordinal')
        C.require(ordinal < self.size, 'rank-bucket ordinal range')
        state, path = (0, 1, 0), ()
        while True:
            if ordinal < self.local[state]:
                for point, _, units, weight, rank in self.blocks(state):
                    if ordinal < units*weight:
                        unit, role = divmod(ordinal, weight)
                        return C.Unit(path, point, unit), self.roles(rank)[role]
                    ordinal -= units*weight
                raise ValueError('local rank-bucket count disagreement')
            ordinal -= self.local[state]
            h, rho, _ = state
            C.require(h < self.groups.index.height, 'rank-bucket has no further child')
            for site, (rank, _) in enumerate(self.groups.rule.rounds):
                child = h+1, rho*rank, rank
                if ordinal < self.total[child]:
                    state, path = child, path+(site,)
                    break
                ordinal -= self.total[child]
            else:
                raise ValueError('rank-bucket subtree count disagreement')


class SourceGroups:
    """All true source-rank counts, with at most one retained bucket DP."""
    def __init__(self, rule, rank, replicas=1, namespace='flow'):
        self.rule, self.rank = rule, rank
        self.index = I.SourceIndex(rule, rank, replicas, namespace)
        self.states = tuple(self.index.total)
        self.products = [ProductCounts(((1, 1),))]
        for _ in range(self.index.height+1):
            self.products.append(ProductCounts(
                (product*k, count*weight)
                for product, count in self.products[-1].items()
                for k, weight in zip(self.index.types, self.index.weights)))
        candidates = []
        previous = None
        for h, rho, _ in self.states:
            if (h, rho) == previous:
                continue
            previous = h, rho
            for product in self.products[self.index.height-h+1].keys:
                source_rank = rho*product
                if rule.ambient*source_rank > rank and source_rank <= rank:
                    candidates.append(source_rank)
        candidates = I.sorted_unique(candidates)
        self.candidate_count = len(candidates)
        self.ranks, self.counts = [], []
        for source_rank in candidates:
            bucket = _RankBucket(self, source_rank)
            if bucket.size:
                self.ranks.append(source_rank)
                self.counts.append(bucket.size)
        self.ranks, self.counts = tuple(self.ranks), tuple(self.counts)
        C.require(sum(self.counts) == self.index.size, 'true-rank buckets partition sources')
        self._active = None

    def _position(self, source_rank):
        C.natural(source_rank, 'source rank')
        at = bisect_left(self.ranks, source_rank)
        C.require(at < len(self.ranks) and self.ranks[at] == source_rank,
                  'source rank absent from catalogue')
        return at

    def count(self, source_rank):
        return self.counts[self._position(source_rank)]

    def _prepare(self, source_rank):
        self._position(source_rank)
        if self._active is None or self._active.rank != source_rank:
            self._active = _RankBucket(self, source_rank)
        return self._active

    def job_rank(self, unit, role):
        i = self.rule.type_of(role)
        return self.index.flow.dilation(unit.path)*C.column(self.rule, unit.point)*self.index.types[i]

    def rank_source(self, source_rank, unit, role):
        return self._prepare(source_rank).rank_source(unit, role)

    def unrank_source(self, source_rank, ordinal):
        return self._prepare(source_rank).unrank_source(ordinal)


@dataclass(frozen=True)
class ComplementPort:
    namespace: str
    source_rank: int
    invocation: int
    slot: int


@dataclass(frozen=True)
class NoComplement:
    namespace: str
    source_rank: int
    ordinal: int


class ComplementRouter:
    """Logical child-port bijection for the positive complement phase only.

    library lists exactly the needed positive (complement rank, program width)
    pairs. These are supplied widths, not a proof of the smaller programs.
    Exit-cut feasibility and all payload moves remain separate obligations.
    """
    def __init__(self, groups, library):
        self.groups = groups
        pairs = sorted(library)
        for rank, width in pairs:
            C.natural(rank, 'complement rank')
            C.natural(width, 'complement program width')
            C.require(0 < rank < groups.rank and width > 0,
                      'positive smaller complement only; no B_0')
        C.require(all(a[0] < b[0] for a, b in zip(pairs, pairs[1:])),
                  'distinct complement library ranks')
        required = tuple(sorted(groups.rank-s for s in groups.ranks if s < groups.rank))
        C.require(tuple(rank for rank, _ in pairs) == required,
                  'exact positive complement library')
        self.library_ranks = tuple(rank for rank, _ in pairs)
        self.library_widths = tuple(width for _, width in pairs)
        for source_rank in groups.ranks:
            if source_rank < groups.rank:
                C.require(groups.index.replicas*groups.count(source_rank) % self.width(source_rank) == 0,
                          'whole complement batch divisibility')

    def width(self, source_rank):
        rank = self.groups.rank-source_rank
        at = bisect_left(self.library_ranks, rank)
        C.require(at < len(self.library_ranks) and self.library_ranks[at] == rank,
                  'positive complement program absent')
        return self.library_widths[at]

    def invocations(self, source_rank):
        count = self.groups.count(source_rank)
        C.require(source_rank < self.groups.rank, 'zero complement has no invocation')
        return self.groups.index.replicas*count//self.width(source_rank)

    def locate(self, row):
        namespace, replica, _, path, point, ordinal, role = self.groups.index.owner(row)
        unit = C.Unit(path, point, ordinal)
        source_rank = self.groups.job_rank(unit, role)
        local = self.groups.rank_source(source_rank, unit, role)
        grouped = replica*self.groups.count(source_rank)+local
        if source_rank == self.groups.rank:
            return NoComplement(namespace, source_rank, grouped)
        invocation, slot = divmod(grouped, self.width(source_rank))
        return ComplementPort(namespace, source_rank, invocation, slot)

    def row(self, location):
        C.require(type(location) in (ComplementPort, NoComplement), 'typed complement location')
        C.require(location.namespace == self.groups.index.namespace, 'invocation namespace')
        source_rank = location.source_rank
        count = self.groups.count(source_rank)
        if type(location) is NoComplement:
            C.require(source_rank == self.groups.rank, 'no-complement rank must be N')
            C.natural(location.ordinal, 'no-complement ordinal')
            grouped = location.ordinal
        else:
            C.require(source_rank < self.groups.rank, 'zero complement has no invocation')
            C.natural(location.invocation, 'complement invocation')
            C.natural(location.slot, 'complement slot')
            width = self.width(source_rank)
            C.require(location.slot < width, 'complement slot range')
            grouped = location.invocation*width+location.slot
        C.require(grouped < self.groups.index.replicas*count, 'complement group range')
        replica, local = divmod(grouped, count)
        unit, role = self.groups.unrank_source(source_rank, local)
        return replica*self.groups.index.size+self.groups.index.rank_source(unit, role)
