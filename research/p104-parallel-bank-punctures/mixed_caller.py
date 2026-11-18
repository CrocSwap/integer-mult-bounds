"""Construct the finite P104 caller with sixteen body blocks. Apache-2.0."""
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
MIXED_SHA256 = '54a44134a6f9bb3d9e1a27d3bd7ba5fb1cffea3cdfe00f6a72e80f0bbd99d2d7'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def split_templates(caller):
    """Use zero-based stage colors and private register numbers in each template."""
    words = {}
    for kind, spec in caller['types'].items():
        off = spec['offset']
        events = []
        for event in caller['events']:
            if event[0] == 'J':
                if kind == 'A':
                    regs = event[2]
                    need((Fraction(spec['alpha2']), Fraction(spec['beta2'])) == (-1, 0),
                         'secondary shear coefficients')
                else:
                    regs = event[3][:2]
                    need(tuple(map(Fraction, event[3][2:])) == (-1, Fraction(1, 2)),
                         'coupled port coefficients')
                events.append(['HOST_' + kind, event[1] - 1, *(i - off for i in regs)])
            elif event[0] == kind:
                op, target, *args = event[1:]
                target -= off
                if op == 'ADD':
                    args = [args[0] - off, [args[1], '0']]
                elif op == 'SCALE':
                    args = [[args[0], '0']]
                elif op in ('SWAP', 'QUERY'):
                    args[0] -= off
                elif op in ('IDLE_ONE', 'IDLE_ODD'):
                    args[0] = [j - 1 for j in args[0]]
                else:
                    need(op == 'LAMBDA', 'known inherited caller event')
                events.append([op, target, *args])
        rows = []
        for phase, scalar, *mask in spec['diagonal']:
            need(scalar == 0 and len(mask) == 16 and set(mask) <= {0, 1}, 'source target mask')
            rows.append([phase, [j for j, bit in enumerate(mask) if bit]])
        words[kind] = (events, rows)
    raw = gzip.decompress((HERE / 'data/CONJUGATE-CALLER.json.gz').read_bytes())
    need(sha256(raw).hexdigest() == MIXED_SHA256, 'conjugate word digest')
    mixed = json.loads(raw)
    need((mixed['schema'], mixed['roles'], mixed['local_calls']) == ('p104-conjugate-root/1', 30, 16),
         'conjugate word schema')
    words['mixed'] = (mixed['events'], mixed['diagonal'])
    for kind, (events, rows) in words.items():
        heads = [e for e in events if e[0].startswith('HOST_')]
        need([e[1] for e in heads] == list(range(16)), 'sixteen ordered calls per root')
        if kind == 'mixed':
            need([e[0] for e in heads] == ['HOST_A']*7 + ['HOST_B']*2 + ['HOST_A']*7,
                 'two central quarter-turns')
        for op, *args in events:
            if op.startswith('HOST_'):
                regs = args[1:]
                need(len(regs) == len(set(regs)) == (4 if op == 'HOST_A' else 2),
                     'native template input width')
            else:
                regs = args[:2] if op in ('ADD', 'SWAP', 'QUERY') else args[:1]
            need(all(0 <= r < len(rows) for r in regs), 'local register owner')
        need(all(q in (-1, 1) and ss and len(set(ss)) == len(ss) and all(0 <= j < 16 for j in ss)
                 for q, ss in rows), 'positive whole recursive targets')
    return words


def place_roots(caller, calls):
    """Return one chronological list of (real call, physical port) per root."""
    need(calls >= 32 and calls % 16 == 0, 'whole batches of sixteen calls')
    ports = {k: tuple(s['ports']) for k, s in caller['types'].items()}
    need(len(ports['A']) == 96 and len(ports['B']) == 8 and
         sorted(ports['A'] + ports['B']) == list(range(104)), 'native port partition')
    occupied = [set() for _ in range(calls)]
    roots = defaultdict(list)
    starts = range(2, calls - 15, 2)
    for block, start in enumerate(starts):
        for slot in range(16):
            t = start + slot
            kind = 'B' if slot in (7, 8) else 'A'
            free = [p for p in ports[kind] if p not in occupied[t]][:8]
            need(len(free) == 8, 'eight free ports for a new group')
            for pair, port in enumerate(free):
                roots['mixed', 8*block + pair].append((t, port))
            occupied[t].update(free)
    for kind, pp in ports.items():
        by_color = [[] for _ in range(16)]
        for t in range(calls):
            by_color[t % 16].extend((t, p) for p in pp if p not in occupied[t])
        need(len({len(v) for v in by_color}) == 1, 'equal capacity in the sixteen colors')
        for i, visits in enumerate(zip(*by_color, strict=True)):
            roots[kind, i] = sorted(visits)
    return dict(sorted(roots.items()))


def layout_bindings(words, roots, layout, calls):
    """Bind every template occurrence to distinct native main and helper addresses."""
    hosted = layout['hosted']
    second = dict(zip(hosted['Dports'], zip(hosted['X2'], hosted['Y2'], strict=True), strict=True))
    need(len(layout['live']) == 104 and len(second) == 96, 'all physical ports')
    need(tuple(Fraction(hosted[k]) for k in ('alpha', 'beta', 'alpha2', 'beta2')) ==
         (-1, Fraction(1, 2), -1, 0), 'signed native coefficients')
    slots = {p: (x, x+112) + second.get(p, ()) for p, x in enumerate(layout['live'])}
    main = {r for regs in slots.values() for r in regs}
    labels = layout['source_labels']
    need(len(labels) == len(set(labels)) == layout['public'] and len(main) == 400
         and main <= set(range(len(labels))), 'physical owner inventory')
    helpers = sorted(label for r, label in enumerate(labels) if r not in main)
    local = {k: [e for e in ev if e[0].startswith('HOST_')] for k, (ev, _) in words.items()}
    bound = [{} for _ in range(calls)]
    offsets = {}
    roles = 0
    for root, visits in sorted(roots.items()):
        kind, _ = root
        need(len(visits) == 16 and visits == sorted(visits) and
             sorted(t % 16 for t, _ in visits) == list(range(16)), 'independent root colors')
        offsets[root] = roles
        for j, (t, port) in enumerate(visits):
            op, slot, *regs = local[kind][j]
            native_kind = 'A' if port in second else 'B'
            need(0 <= t < calls and port in slots and op == 'HOST_' + native_kind and slot == j,
                 'native port type and time')
            need(port not in bound[t] and len(set(regs)) == len(regs) == len(slots[port]),
                 'signed main owner alias')
            bound[t][port] = [r + roles for r in regs]
        roles += len(words[kind][1])
    digest = sha256()
    helper_digest = sha256(json.dumps(helpers, separators=(',', ':')).encode()).hexdigest()
    for t, ports in enumerate(bound):
        need(set(ports) == set(slots), 'all physical ports at each call')
        labels_in_use = {label: owner for port in ports
                         for label, owner in zip(slots[port], ports[port], strict=True)}
        need(set(labels_in_use) == main and len(set(labels_in_use.values())) == 400,
             'four hundred independent main inputs')
        # A helper address is (native occurrence, source label). Caller owners have a separate namespace.
        record = [t, t % 16, sorted(labels_in_use.items()), helper_digest]
        digest.update(json.dumps(record, separators=(',', ':')).encode())
    counts = Counter(root[0] for root in roots)
    receipt = dict(calls=calls, local_colors=16, ambient=137, template_roots=dict(counts),
                   root_owners=roles, stage_helper_owners=calls*len(helpers),
                   physical_port_contacts=104*calls, native_main_bindings=400*calls,
                   stage_binding_sha256=digest.hexdigest(), helper_label_sha256=helper_digest)
    return bound, offsets, receipt


def instructions(words, roots, bindings, offsets):
    """Emit the full chronological program. A NATIVE row contains all 104 port bindings."""
    chunks = {}
    for kind, (events, _) in words.items():
        chunks[kind] = [[]]
        for op, *args in events:
            if op.startswith('HOST_'):
                chunks[kind].append([])
            else:
                chunks[kind][-1].append((op, args))
    tails = defaultdict(list)
    for root, visits in sorted(roots.items()):
        times = [t for t, _ in visits] + [len(bindings)]
        for t, block in zip(times, chunks[root[0]], strict=True):
            tails[t].append((offsets[root], visits, block))
    for t in range(len(bindings)+1):
        for offset, visits, block in tails[t]:
            for op, local in block:
                args = local.copy()
                args[0] += offset
                if op in ('ADD', 'SWAP', 'QUERY'):
                    args[1] += offset
                if op.startswith('IDLE_'):
                    args[1] = [visits[j][0] % 16 for j in args[1]]
                yield [op, *args]
        if t < len(bindings):
            ports = [bindings[t][p] for p in range(104)]
            yield ['PORT_VIEWS', 'ENTER', t, ports]
            yield ['NATIVE', t, t % 16, ports]
            yield ['PORT_VIEWS', 'EXIT', t, ports]
