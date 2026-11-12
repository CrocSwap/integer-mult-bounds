"""Lazy chronological rank-one leaf locations and persistent field identities.

Prepared for CubeJerry with substantial OpenAI assistance. Apache-2.0.
Logical descriptors only: no payload execution or unpriced adapters.
"""
from dataclasses import dataclass
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = HERE / 'inputs/groups.py'
if sha256(SOURCE.read_bytes()).hexdigest() != '871b166c174958bb467952bebe9a2b776a0582f0c427b7dea9a94a128edad171':
    raise ValueError('frozen complement-port source')
spec = spec_from_file_location('leaf_groups', SOURCE)
G = module_from_spec(spec)
sys.modules[spec.name] = G
spec.loader.exec_module(G)
C, I = G.C, G.I


@dataclass(frozen=True)
class Step:
    parent: int
    kind: str
    key: object  # source rank, or full ordered exit path
    invocation: int


@dataclass(frozen=True)
class SourceRow:
    namespace: str
    row: int


@dataclass(frozen=True)
class OwnedBank:
    namespace: str
    calls: tuple
    replica: int
    path: tuple
    point: tuple
    ordinal: int
    role: str


@dataclass(frozen=True)
class Leaf:
    calls: tuple
    rank: int
    axis: int
    field: object


class Node:
    """One rank's source and weighted chronological-cut metadata."""
    def __init__(self, compiler, rank):
        self.compiler, self.rank = compiler, rank
        self.row = compiler.row(rank)
        self.groups = G.SourceGroups(compiler.rule, rank, self.row.replication, 'local')
        self.height = self.groups.index.height
        C.require(self.row.width == self.row.replication*self.groups.index.size,
                  'compiled source width recurrence')
        library = tuple((rank-s, compiler.row(rank-s).width)
                        for s in self.groups.ranks if s < rank)
        self.complements = G.ComplementRouter(self.groups, library)
        prefixes, self.pre = [], 0
        for source in self.groups.ranks:
            if source == rank:
                continue
            child = compiler.row(rank-source)
            size = self.complements.invocations(source)*child.leaves
            prefixes.append((source, self.pre, size))
            self.pre += size
        self.prefixes = tuple(prefixes)
        levels = [(1,)]
        for _ in range(self.height+1):
            levels.append(tuple(I.sorted_unique(rho*r for rho in levels[-1]
                                               for r in self.groups.index.paid)))
        keys = tuple((h, rho) for h, level in enumerate(levels) for rho in level)
        self.suffix = I.SortedStateTable(keys)
        for h in range(self.height+1, -1, -1):
            for rho in levels[h]:
                if h == self.height+1:
                    child = compiler.row(rho)
                    copies, remainder = divmod(self.row.replication, child.width)
                    C.require(remainder == 0, 'every individual exit cut is integral')
                    value = copies*child.leaves
                else:
                    value = sum(count*self.suffix[h+1, rho*r]
                                for r, count in self.groups.index.paid.items())
                self.suffix[h, rho] = value
        C.require(self.pre+self.suffix[0, 1] == self.row.leaves,
                  'complete ordered leaf count recurrence')

    def exit_rank(self, cut):
        C.require(type(cut) is tuple and len(cut) == self.height+1,
                  'complete chronological exit cut')
        return self.groups.index.flow.dilation(cut)

    def exit_owner(self, cut, replica):
        self.exit_rank(cut)
        C.natural(replica, 'replica')
        C.require(replica < self.row.replication, 'exit replica range')
        unit = C.Unit(cut[:-1], (0,)*len(self.groups.index.types), 0)
        return self.groups.index.flow.paid_owner(unit, cut[-1], 'local', replica)

    def exit_port(self, cut, owner):
        e = self.exit_rank(cut)
        C.require(type(owner) is tuple and len(owner) == 7, 'complete owner identifier')
        replica = owner[1]
        C.require(owner == self.exit_owner(cut, replica), 'owner at this cut')
        return divmod(replica, self.compiler.row(e).width)

    def step_data(self, step):
        """Validate one call; return (child rank, before-call leaf offset)."""
        C.require(type(step) is Step and step.parent == self.rank, 'correct parent rank')
        C.natural(step.invocation, 'whole invocation ordinal')
        if step.kind == 'complement':
            C.natural(step.key, 'complement source rank')
            for source, offset, _ in self.prefixes:
                if source == step.key:
                    child = self.compiler.row(self.rank-source)
                    C.require(step.invocation < self.complements.invocations(source),
                              'complement invocation range')
                    return self.rank-source, offset+step.invocation*child.leaves
            raise ValueError('positive complement source absent')
        C.require(step.kind == 'exit', 'typed chronological call')
        e = self.exit_rank(step.key)
        child = self.compiler.row(e)
        C.require(step.invocation < self.row.replication//child.width,
                  'exit invocation range')
        rho, offset = 1, self.pre
        for h, chosen in enumerate(step.key):
            for r, _ in self.compiler.rule.rounds[:chosen]:
                offset += self.suffix[h+1, rho*r]
            rho *= self.compiler.rule.rounds[chosen][0]
        return e, offset+step.invocation*child.leaves

    def locate(self, ordinal):
        C.natural(ordinal, 'leaf ordinal')
        C.require(ordinal < self.row.leaves, 'leaf ordinal range')
        for source, offset, size in self.prefixes:
            if ordinal < offset+size:
                child = self.compiler.row(self.rank-source)
                invocation, local = divmod(ordinal-offset, child.leaves)
                return Step(self.rank, 'complement', source, invocation), local
        local, rho, path = ordinal-self.pre, 1, ()
        for h in range(self.height+1):
            for chosen, (r, _) in enumerate(self.compiler.rule.rounds):
                size = self.suffix[h+1, rho*r]
                if local < size:
                    path += (chosen,)
                    rho *= r
                    break
                local -= size
            else:
                raise ValueError('weighted cut count disagreement')
        invocation, local = divmod(local, self.compiler.row(rho).leaves)
        return Step(self.rank, 'exit', path, invocation), local

    def caller_owner(self, step, child_row):
        e, _ = self.step_data(step)
        C.natural(child_row, 'child productive row')
        C.require(child_row < self.compiler.row(e).width, 'child productive row range')
        if step.kind == 'complement':
            row = self.complements.row(G.ComplementPort('local', step.key,
                                                       step.invocation, child_row))
            return self.groups.index.owner(row)
        replica = step.invocation*self.compiler.row(e).width+child_row
        return self.exit_owner(step.key, replica)


class Compiler:
    """Supplied exact library plus unexpanded logical occurrence metadata.

    A may exceed every target rank. Base ranks n<A use width one and n
    sequential leaves. The retained convenience generator is restricted
    to A=max(target rank); the general interface accepts supplied rows.
    """
    def __init__(self, rule, rows, namespace='compiler'):
        C.require(type(namespace) is str and bool(namespace), 'nonempty namespace')
        C.require(len(rows) >= 2 and rows[0] is None, 'no rank-zero library')
        self.rule, self.rows, self.namespace = rule, tuple(rows), namespace
        self.maximum = len(rows)-1
        self.nodes = [None]*len(rows)
        for rank, row in enumerate(rows[1:], 1):
            for value in (row.replication, row.width, row.leaves):
                C.natural(value, 'evaluated library integer')
                C.require(value > 0, 'positive library integer')
            if rank < rule.ambient:
                C.require((row.replication, row.width, row.leaves) == (1, 1, rank),
                          'sequential base library')

    def row(self, rank):
        C.natural(rank, 'library rank')
        C.require(0 < rank <= self.maximum, 'positive available library rank')
        return self.rows[rank]

    def node(self, rank):
        self.row(rank)
        C.require(rank >= self.rule.ambient, 'nonbase flow only')
        if self.nodes[rank] is None:
            self.nodes[rank] = Node(self, rank)
        return self.nodes[rank]

    def validate_calls(self, calls, root=None):
        C.require(type(calls) is tuple, 'tuple call path')
        rank = self.maximum if root is None else root
        self.row(rank)
        for step in calls:
            rank, _ = self.node(rank).step_data(step)
        return rank

    def resolve_row(self, calls, row, root=None):
        """Map a call's productive port to persistent root/owned identity."""
        rank = self.validate_calls(calls, root)
        C.natural(row, 'productive row')
        C.require(row < self.row(rank).width, 'productive row range')
        for at in range(len(calls)-1, -1, -1):
            step = calls[at]
            node = self.node(step.parent)
            owner = node.caller_owner(step, row)
            if owner[2] == 'owned':
                _, replica, _, path, point, ordinal, role = owner
                return OwnedBank(self.namespace, calls[:at], replica,
                                 path, point, ordinal, role)
            row = node.groups.index.row(owner)
        return SourceRow(self.namespace, row)

    def locate(self, ordinal, root=None):
        rank = self.maximum if root is None else root
        C.natural(ordinal, 'leaf ordinal')
        C.require(ordinal < self.row(rank).leaves, 'leaf ordinal range')
        calls = ()
        while rank >= self.rule.ambient:
            step, ordinal = self.node(rank).locate(ordinal)
            calls += (step,)
            rank, _ = self.node(rank).step_data(step)
        return Leaf(calls, rank, ordinal, self.resolve_row(calls, 0, root))

    def rank_leaf(self, leaf, root=None):
        C.require(type(leaf) is Leaf, 'typed leaf descriptor')
        rank = self.validate_calls(leaf.calls, root)
        C.require(rank == leaf.rank and rank < self.rule.ambient, 'correct base rank')
        C.natural(leaf.axis, 'base axis')
        C.require(leaf.axis < rank, 'base axis range')
        C.require(leaf.field == self.resolve_row(leaf.calls, 0, root),
                  'leaf physical field identity')
        ordinal = leaf.axis
        for step in reversed(leaf.calls):
            _, offset = self.node(step.parent).step_data(step)
            ordinal += offset
        return ordinal
