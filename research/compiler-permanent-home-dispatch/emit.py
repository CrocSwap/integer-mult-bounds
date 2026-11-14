"""Expand the actual frozen source codec through every native checkpoint.

New material: Apache-2.0. Prepared for CubeJerry with OpenAI Codex assistance.
This is an offline compiler; dictionaries are not claimed to be physical RAM.
"""
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

for entry in json.loads((Path(__file__).parent/'SOURCES.json').read_text())['files']:
    data = (Path(__file__).parent/entry['local']).read_bytes()
    if sha256(data).hexdigest() != entry['sha256'] or len(data) != entry['bytes']:
        raise ValueError('changed frozen scientific input: '+entry['local'])
from inputs import leaf_index as L


@dataclass(frozen=True)
class Event:
    kind: str
    service: str
    owners: tuple
    context: tuple


class Emitter:
    """Native segments, complete calls, frames and private lifetimes.

    segments[j] is the finite native segment before paid site j, and the
    final segment follows the last paid site. An operation is (service, roles).
    The adapter callback supplies a service name, or None for the identity.
    It is a supplied whole-job primitive contract, not inferred from rank.
    """
    def __init__(self, compiler, segments, adapter=lambda context: None,
                 leaf_service=lambda n, axis, chain: 'FIRST'):
        self.c = compiler
        self.rule = compiler.rule
        if len(segments) != len(self.rule.rounds)+1:
            raise ValueError('one native segment at every checkpoint')
        allowed = {name for name, _ in self.rule.roles} | set(self.rule.owned)
        for segment in segments:
            for _, names in segment:
                if not names or len(names) != len(set(names)) or not set(names) <= allowed:
                    raise ValueError('distinct real native service operands')
        self.segments, self.adapter, self.leaf_service = segments, adapter, leaf_service
        self.events, self.live, self.frames = [], set(), {}
        self.homes = [L.SourceRow(compiler.namespace, row)
                      for row in range(compiler.row(compiler.maximum).width)]
        self.live.update(self.homes)
        self.home_index = {owner: i for i, owner in enumerate(self.homes)}

    def event(self, kind, service, owners, context):
        owners = tuple(owners)
        if len(owners) != len(set(owners)):
            raise ValueError('aliased simultaneous service operands')
        if kind == 'allocate':
            owner, = owners
            if owner in self.home_index or owner in self.live:
                raise ValueError('owned tag reused')
            self.home_index[owner] = len(self.homes)
            self.homes.append(owner)
            self.live.add(owner)
        elif not set(owners) <= self.live:
            raise ValueError('service on a dead or unknown owner')
        if kind == 'push':
            self.frames.setdefault(owners[0], []).append(context)
        elif kind == 'pop':
            stack = self.frames.get(owners[0], [])
            if not stack or stack.pop() != context:
                raise ValueError('whole-job frame return is not LIFO')
        elif kind == 'release':
            if self.frames.get(owners[0]):
                raise ValueError('release with a live descendant frame')
            if not isinstance(owners[0], L.OwnedBank):
                raise ValueError('productive source cannot be erased')
            self.live.remove(owners[0])
        self.events.append(Event(kind, service, owners, context))

    def wrap(self, owner, context, entering):
        service = self.adapter(context)
        # The return service is supplied separately for general adapters.
        if isinstance(service, tuple):
            service = service[0 if entering else 1]
        if service:
            self.event('push' if entering else 'pop', service, (owner,), context)

    def field(self, n, chain, replica, unit, name):
        node = self.c.node(n)
        if name in self.rule.owned:
            local = ('local', replica, 'owned', unit.path, unit.point, unit.ordinal, name)
        else:
            local = node.groups.index.flow.owner(unit, name, 'local', replica)
        _, b, kind, path, point, ordinal, role = local
        if kind == 'owned':
            return L.OwnedBank(self.c.namespace, chain, b, path, point, ordinal, role)
        return self.c.resolve_row(chain, node.groups.index.row(local))

    def child(self, n, chain, step):
        e, _ = self.c.node(n).step_data(step)
        child_chain = chain+(step,)
        ports = tuple(self.c.resolve_row(child_chain, i)
                      for i in range(self.c.row(e).width))
        if len(set(ports)) != len(ports):
            raise ValueError('whole child ports alias')
        context = ('call', child_chain)
        for i, owner in enumerate(ports):
            self.wrap(owner, context+(i,), True)
        self.event('call', '', ports, context+(e,))
        self.visit(e, child_chain)
        self.event('return', '', ports, context+(e,))
        for i in range(len(ports)-1, -1, -1):
            self.wrap(ports[i], context+(i,), False)

    def visit(self, n, chain=()):
        if n < self.rule.ambient:
            for axis in range(n):
                self.event('leaf', self.leaf_service(n, axis, chain), (self.c.resolve_row(chain, 0),),
                           (chain, n, axis))
            return
        node, a = self.c.node(n), self.c.row(n).replication
        for s in node.groups.ranks:
            if s < n:
                for invocation in range(node.complements.invocations(s)):
                    self.child(n, chain, L.Step(n, 'complement', s, invocation))

        def execute_class(path):
            units = tuple(node.groups.index.flow.iter_units(path))
            active = [(b, unit) for b in range(a) for unit in units]
            operands = {}
            for b, unit in active:
                key = (chain, b, unit.path, unit.point, unit.ordinal)
                fields = {name: self.field(n, chain, b, unit, name)
                          for name, _ in self.rule.roles}
                fields.update((name, self.field(n, chain, b, unit, name))
                              for name in self.rule.owned)
                operands[b, unit] = fields
                if len(set(fields.values())) != len(fields):
                    raise ValueError('one native instance has aliased fields')
                for name in self.rule.owned:
                    self.event('allocate', 'ZERO', (fields[name],), key+(name,))
                for name, _ in self.rule.roles:
                    self.wrap(fields[name], ('unit',)+key+(name,), True)
            # Native instances in a class are pairwise disjoint. Entered
            # ancestor roles on the same owner remain suspended and live.
            all_fields = [owner for fields in operands.values() for owner in fields.values()]
            if len(set(all_fields)) != len(all_fields):
                raise ValueError('class has simultaneous owner alias')
            for checkpoint, segment in enumerate(self.segments):
                for b, unit in active:
                    fields = operands[b, unit]
                    key = (chain, b, unit.path, unit.point, unit.ordinal, checkpoint)
                    for position, (service, names) in enumerate(segment):
                        if callable(service):
                            column = node.groups.index.flow.dilation(unit.path)*L.C.column(self.rule,unit.point)
                            service = service(n,chain,b,unit,column,checkpoint,position)
                        self.event('native', service, tuple(fields[name] for name in names),
                                   key+(position,))
                if checkpoint < len(self.rule.rounds):
                    if len(path) < node.height:
                        execute_class(path+(checkpoint,))
                    else:
                        cut = path+(checkpoint,)
                        e = node.exit_rank(cut)
                        for invocation in range(a//self.c.row(e).width):
                            self.child(n, chain, L.Step(n, 'exit', cut, invocation))
            for b, unit in reversed(active):
                key, fields = (chain, b, unit.path, unit.point, unit.ordinal), operands[b, unit]
                for name, _ in reversed(self.rule.roles):
                    self.wrap(fields[name], ('unit',)+key+(name,), False)
                for name in reversed(self.rule.owned):
                    self.event('release', 'ZERO', (fields[name],), key+(name,))

        execute_class(())

    def compile(self):
        self.visit(self.c.maximum)
        if self.live != set(self.homes[:self.c.row(self.c.maximum).width]):
            raise ValueError('unfinished owned lifetime at root return')
        if any(self.frames.values()):
            raise ValueError('unfinished adapter at root return')
        return tuple(self.events), tuple(self.homes)
