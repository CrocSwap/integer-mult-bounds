"""Separate field-value oracle using literal matched slot lists, not codecs.

No production emitter, owner resolver or tape graph is imported. Apache-2.0.
"""
from inputs import literal_oracle as O


def normalize(value):
    if hasattr(value, '__dataclass_fields__'):
        names = tuple(value.__dataclass_fields__)
        if names == ('namespace', 'row'):
            return ('source', value.namespace, value.row)
        if names == ('namespace', 'calls', 'replica', 'path', 'point', 'ordinal', 'role'):
            return ('owned', value.namespace, normalize(value.calls), value.replica,
                    value.path, value.point, value.ordinal, value.role)
        return tuple(normalize(getattr(value, name)) for name in names)
    if isinstance(value, (tuple, list)):
        return tuple(normalize(x) for x in value)
    return value


def apply(values, service, owners):
    if service == 'XOR':
        a, b = owners
        values[b] = ''.join(str(int(x)^int(y)) for x, y in zip(values[a], values[b]))
    elif service == 'REV':
        owner, = owners
        values[owner] = values[owner][::-1]
    elif service == 'NOT':
        owner, = owners
        values[owner] = ''.join(str(1-int(x)) for x in values[owner])
    elif service == 'FIRST':
        owner, = owners
        values[owner] = str(1-int(values[owner][0]))+values[owner][1:]
    elif service == 'ZERO':
        owner, = owners
        values[owner] = '0'*len(values[owner])
    elif service:
        raise ValueError('unknown independent primitive')


def run(roles, rounds, owned, ambient, root, rows, flows, segments, adapter, payloads,
        namespace='dispatch'):
    values = {('source', namespace, i): bits for i, bits in enumerate(payloads)}
    events, homes = [], list(values)
    width = len(payloads[0])

    def event(kind, service, fields, context):
        fields = tuple(fields)
        if kind == 'allocate':
            if fields[0] in values:
                raise ValueError('literal private identity alias')
            homes.append(fields[0])
            values[fields[0]] = '0'*width
        events.append((kind, service, fields, context))
        apply(values, service, fields)

    def wrap(field, context, entering):
        service = adapter(context)
        if isinstance(service, tuple):
            service = service[0 if entering else 1]
        if service:
            event('push' if entering else 'pop', service, (field,), context)

    def visit(n, chain, inputs):
        if n < ambient:
            for axis in range(n):
                event('leaf', 'FIRST', (inputs[0],), (chain, n, axis))
            return
        flow, a = flows[n], rows[n].replication

        def lift(replica, value):
            if value[0] == 'source':
                return inputs[replica*len(flow.fresh)+flow.fresh_index[value[1]]]
            _, (path, point, ordinal), name = value
            return ('owned', namespace, chain, replica, path, point, ordinal, name)

        def child(e, kind, key, batch):
            for offset in range(0, len(batch), rows[e].width):
                fields = tuple(batch[offset:offset+rows[e].width])
                child_chain = chain+((n, kind, key, offset//rows[e].width),)
                context = ('call', child_chain)
                for i, field in enumerate(fields):
                    wrap(field, context+(i,), True)
                event('call', '', fields, context+(e,))
                visit(e, child_chain, fields)
                event('return', '', fields, context+(e,))
                for i in range(len(fields)-1, -1, -1):
                    wrap(fields[i], context+(i,), False)

        for s in sorted({s for _, s in flow.fresh}):
            if s < n:
                batch = [inputs[b*len(flow.fresh)+i] for b in range(a)
                         for i, (_, rank) in enumerate(flow.fresh) if rank == s]
                child(n-s, 'complement', s, batch)

        def execute_class(path):
            active = [(b, unit) for b in range(a) for unit in flow.classes[path]]
            operands = {}
            for b, unit in active:
                key = (chain, b)+unit
                fields = {name: lift(b, flow.owners[unit+(name,)]) for name, _ in roles}
                fields.update((name, ('owned', namespace, chain, b)+unit+(name,))
                              for name in owned)
                operands[b, unit] = fields
                for name in owned:
                    event('allocate', 'ZERO', (fields[name],), key+(name,))
                for name, _ in roles:
                    wrap(fields[name], ('unit',)+key+(name,), True)
            for checkpoint, segment in enumerate(segments):
                for b, unit in active:
                    key, fields = (chain, b)+unit+(checkpoint,), operands[b, unit]
                    for position, (service, names) in enumerate(segment):
                        event('native', service, tuple(fields[name] for name in names),
                              key+(position,))
                if checkpoint < len(rounds):
                    if len(path) < flow.height:
                        execute_class(path+(checkpoint,))
                    else:
                        e, value = flow.exit(path+(checkpoint,))
                        child(e, 'exit', path+(checkpoint,), [lift(b, value) for b in range(a)])
            for b, unit in reversed(active):
                key, fields = (chain, b)+unit, operands[b, unit]
                for name, _ in reversed(roles):
                    wrap(fields[name], ('unit',)+key+(name,), False)
                for name in reversed(owned):
                    event('release', 'ZERO', (fields[name],), key+(name,))

        execute_class(())

    visit(root, (), tuple(homes))
    return tuple(events), tuple(homes), tuple(values[owner] for owner in homes)
