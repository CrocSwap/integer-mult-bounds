"""Independent source-word interpreter for provider audit.

Arithmetic is explicitly reused from our frozen #5383 dyadic engine, whose
unmodified copy is retained beside this file. No author module is imported.
Every original field and every owned field starts with arbitrary input dirt.
Native generator order is free, with adjacent inverse cancellation only.
"""
from prior_dyadic_engine import initial, linear, scaled, warped, require


def interpret(canonical, program, owned, observations=(), require_owned_return=True):
    roles = {('L', i) for i in range(632)} | set(owned)
    rows = {r: initial(r) for r in roles}
    frames = {('L', i): f for i, f in enumerate(canonical['start'])}
    frames.update({r: None for r in owned if r[0] == 'C'})
    spaces, seen, events, paid = {}, {}, {}, {}
    writes = {r: [] for r in roles}
    reads = {r: [] for r in roles}
    live_owners, max_live = set(), 0
    def space(f):
        if f not in spaces:
            values = {0}
            for axis in canonical['frames'][f]:
                values |= {x ^ axis for x in tuple(values)}
            require(len(values) == 1 << len(canonical['frames'][f]), 'dependent binary frame')
            spaces[f] = values
        return spaces[f]
    for index, event in enumerate(program):
        tag = event[0]
        events[tag] = events.get(tag, 0) + 1
        if tag == 'scalar':
            op, frame = event[1:]
            action, dst = op[0], tuple(op[1])
            require(dst in roles and 0 <= frame < len(canonical['frames']), 'undeclared scalar role/frame')
            if action == 'clear':
                require(dst in owned, 'borrowed erasure')
                rows[dst], frames[dst] = ({}, 0), frame
                live_owners.discard(dst)
            else:
                require(frames[dst] == frame, 'destination scalar frame')
                if action in ('copy', 'add'):
                    src = tuple(op[2])
                    require(src in roles and src != dst and frames[src] == frame, 'source scalar frame')
                    reads[src].append(index)
                    if action == 'copy':
                        require(dst in owned and not rows[dst][0], 'COPY requires cleared owned destination')
                        rows[dst] = (dict(rows[src][0]), rows[src][1])
                    else:
                        rows[dst] = linear(rows[dst], rows[src], op[3], op[4])
                else:
                    require(action == 'scale', 'unknown scalar opcode')
                    q, d = op[2:]
                    require(q and d and abs(q) & (abs(q)-1) == 0 and abs(d) & (abs(d)-1) == 0, 'physical SCALE must be signed power of two')
                    reads[dst].append(index)
                    rows[dst] = scaled(rows[dst], q, d)
                if dst in owned and rows[dst][0]:
                    live_owners.add(dst)
            writes[dst].append((index, action))
        elif tag == 'warp':
            _, role, symbol, old, new = event
            dst = ('L', role) if isinstance(role, int) else tuple(role)
            require(dst in roles and frames[dst] == old and 1 <= abs(symbol) <= len(canonical['warps']), 'native warp declaration/frame')
            rows[dst] = warped(rows[dst], symbol)
            frames[dst] = new
            writes[dst].append((index, tag)); reads[dst].append(index)
        elif tag in ('center', 'climb'):
            if tag == 'center':
                _, field, old, new, rank = event
                dst = ('C', field)
                require(space(old) < space(new) or space(new) < space(old), 'center physical nested spaces')
            else:
                _, label, field, old, new, rank = event
                dst = ('L', field)
                require(space(old) < space(new), 'climb physical nested spaces')
            require(frames[dst] == old, 'paid source frame')
            require(rank == abs(len(canonical['frames'][old])-len(canonical['frames'][new])), 'paid exact rank')
            frames[dst] = new
            paid[rank] = paid.get(rank, 0) + 1
            writes[dst].append((index, tag)); reads[dst].append(index)
        elif tag == 'zero_retag':
            _, role, old, new = event
            dst = ('L', role) if isinstance(role, int) else tuple(role)
            require(frames[dst] == old and not rows[dst][0], 'zero retag requires complete exact zero row')
            frames[dst] = new
            writes[dst].append((index, tag)); reads[dst].append(index)
        else:
            require(tag in ('phase', 'adapter'), 'unknown word event')
        if index in observations:
            seen[index] = {r: (dict(rows[r][0]), rows[r][1]) for r in observations[index]}
        max_live = max(max_live, len(live_owners))
    for i in range(632):
        require(frames[('L', i)] == canonical['final'][i], 'wrong final borrowed frame')
    for role in owned if require_owned_return else ():
        require(not rows[role][0], 'owned return has dependence on arbitrary entry')
        require(writes[role] and writes[role][-1][1] == 'clear', 'owned final write must clear')
    return rows, seen, {'events': len(program), 'event_counts': events,
                       'paid': paid, 'max_live_owned_rows': max_live,
                       'original_inputs': 632, 'arbitrary_owned_inputs': len(owned),
                       'owner_lifetimes': {str(r): {'first_write': writes[r][0],
                           'last_write': writes[r][-1], 'last_read': max(reads[r], default=-1)}
                           for r in sorted(owned)}}
