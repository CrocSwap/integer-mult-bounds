"""Build the 48-call P104 word. See CLOSED-CALLER.md. Apache-2.0."""
from collections import defaultdict

from mixed_caller import need, split_templates


CALLS = 48
CUT = 1641


def templates(caller):
    """Rotate the source word at its restored middle basis."""
    source = split_templates(caller)
    original, targets = source['mixed']
    rotated = []
    for row in original[CUT:] + original[:CUT]:
        op, first, *args = row
        if op.startswith('HOST_'):
            rotated.append([op, (first + 8) % 16, *args])
        elif op == 'IDLE_ONE':
            rotated.append([op, first, [(j + 8) % 16 for j in args[0]]])
        else:
            need(op in ('ADD', 'SCALE', 'SWAP', 'LAMBDA'), 'source ordinary opcode')
            rotated.append(row)
    hosts = [(r[0], r[1]) for r in rotated if r[0].startswith('HOST_')]
    need(hosts == list(zip(['HOST_B'] + ['HOST_A'] * 14 + ['HOST_B'], range(16))), 'two end contacts')
    outputs = [[q, [(j + 8) % 16 for j in mask]] for q, mask in targets]
    return {'A': source['A'], 'rotated': (rotated, outputs)}


def placement(caller):
    """Assign all physical ports at all calls. Each root uses every body color once."""
    ports = {k: sorted(s['ports']) for k, s in caller['types'].items()}
    need(tuple(map(len, (ports['A'], ports['B']))) == (96, 8), 'physical port inventory')
    roots = defaultdict(list)
    used = [set() for _ in range(CALLS)]
    for start in range(24):
        for member, port in enumerate(ports['B']):
            root = ('rotated', 8 * start + member)
            for time in (start, start + 24):
                roots[root].append((time, port))
                used[time].add(port)

    unused = []
    for color in range(16):
        starts = [s for s in range(24) if color not in (s % 16, (s + 24) % 16)]
        for time in range(color, CALLS, 16):
            available = [s for s in starts if s < time < s + 24]
            for group, start in enumerate(available[:12]):
                starts.remove(start)
                for member, port in enumerate(ports['A'][8 * group:8 * group + 8]):
                    roots['rotated', 8 * start + member].append((time, port))
                    used[time].add(port)
        need(not starts, 'all interior mixed visits fit')
        unused.append([(t, p) for t in range(color, CALLS, 16) for p in ports['A'] if p not in used[t]])
    need(all(len(items) == 120 for items in unused), 'residual visits of each color')
    for index, visits in enumerate(zip(*unused, strict=True)):
        roots['A', index] = list(visits)
    return {r: sorted(visits) for r, visits in sorted(roots.items())}
