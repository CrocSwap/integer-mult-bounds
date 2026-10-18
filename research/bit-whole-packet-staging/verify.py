"""Whole-invocation packet staging: selected census and sequential small model.

No predecessor implementation is imported. Python 3.12, standard library.
Substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HOST = 'research/community-hyperplane599-audit/pr589/bit589/v9/hosted/GLOBAL-TEMPLATE.json.gz'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def selected(template):
    """Independent support-disjointness and literal-word census, not geometry proof."""
    idle = {e['idx']: e for e in template['schedule'] if e['kind'] == 'idle'}
    family_counts = Counter()
    helper_pairs = 0
    for call in template['calls']:
        owners = call['owners']
        need(len(owners) == 661, 'selected role count')
        data = {f for f, _ in owners[:222]}
        need(len(data) == 222, 'data packet uniqueness')
        groups = defaultdict(list)
        for family, route in owners[222:]:
            need(family not in data and route[0] == 'hosted', 'helper/data separation')
            _, child, offset, width = route
            event = idle[child]
            start = 1 if event['source_level'] == -1 else 8 + 7 * event['source_level']
            axes = list(range(start, 8 + 7 * event['target_level']))[offset:offset+width]
            need(width == len(axes) == 8, 'complete helper support')
            groups[family].append(set(axes))
        for supports in groups.values():
            for a, b in combinations(supports, 2):
                need(a.isdisjoint(b), 'selected packet support collision')
                helper_pairs += 1
        family_counts[len(data) + len(groups)] += 1
    local = {}
    for orientation, events in template['local_programs'].items():
        need(hashlib.sha256(json.dumps(events, separators=(',', ':')).encode()).hexdigest()
             == next(c['local_hash'] for c in template['calls'] if c['orientation'] == orientation),
             'literal local hash')
        values = [1 << i for i in range(661)] + [0]
        live = None
        counts = Counter()
        for e in events:
            op, target = e[:2]
            counts[op] += 1
            if op == 1:
                source = e[2]
                need(target != live and (source != 661 or live is not None), 'live COPY safety')
                values[target] ^= values[source]
            elif op == 2:
                need(live is None and values[661] == 0, 'blank private slot')
                live = target
                values[661] = values[target]
            elif op == 3:
                need(live == target and values[661] == values[target], 'literal ERASE guard')
                values[661] = 0
                live = None
            else:
                need(op == 0, 'known literal opcode')
        expected = [(1 << i) ^ ((1 << (i-111)) if 111 <= i < 222 else 0)
                    for i in range(661)] + [0]
        need(values == expected and live is None, 'arbitrary dirty decoded endpoint')
        need(counts == {0:2911, 1:24305, 2:9, 3:9}, 'selected event inventory')
        local[orientation] = dict(events=len(events), counts=dict(sorted(counts.items())),
                                  symbolic_columns=661, final_private_zero=True)
    need(helper_pairs == 181056 and len(template['calls']) == 288, 'selected owner totals')
    return dict(calls=288, roles_per_call=661, helper_pairs=helper_pairs,
                touched_families_histogram=dict(sorted(family_counts.items())),
                family_scans_per_low_class_across_calls=2*sum(k*v for k,v in family_counts.items()),
                route_actions_per_call=1322, route_actions_across_calls=1322*288,
                local_programs=local)


@dataclass
class Meter:
    # One cell is a fixed 17-bit record, expanded to ordinary bit operations below.
    reads: int = 0
    writes: int = 0
    erases: int = 0
    head_moves: int = 0
    scratch_cells: int = 0
    peak_scratch_cells: int = 0
    family_scans: int = 0
    route_actions: int = 0
    shift_actions: int = 0


class Tape:
    def __init__(self, meter, cells=(), scratch=True):
        self.m = meter
        self.cells = list(cells)
        self.head = 0
        self.scratch = scratch
        if scratch:
            self.m.scratch_cells += len(self.cells)
            self.m.peak_scratch_cells = max(self.m.peak_scratch_cells, self.m.scratch_cells)

    def read(self):
        need(self.head < len(self.cells), 'sequential read bound')
        value = self.cells[self.head]
        self.head += 1
        self.m.reads += 1
        self.m.head_moves += 1
        return value

    def append(self, value):
        need(self.head == len(self.cells), 'append-only output')
        self.cells.append(value)
        self.head += 1
        self.m.writes += 1
        self.m.head_moves += 1
        if self.scratch:
            self.m.scratch_cells += 1
            self.m.peak_scratch_cells = max(self.m.peak_scratch_cells, self.m.scratch_cells)

    def replace_next(self, value):
        # The family head writes its current cell, then moves one cell.
        need(self.head < len(self.cells), 'in-place write bound')
        self.cells[self.head] = value
        self.head += 1
        self.m.writes += 1
        self.m.head_moves += 1

    def rewind(self):
        self.m.head_moves += self.head
        self.head = 0

    def end(self):
        need(self.head == len(self.cells), 'complete sequential pass')

    def clear(self):
        self.rewind()
        self.m.erases += len(self.cells)
        self.m.head_moves += 2*len(self.cells)
        if self.scratch:
            self.m.scratch_cells -= len(self.cells)
        self.cells.clear()


def transfer(source, target, count):
    for _ in range(count):
        target.append(source.read())


def route(tape, low, coefficient, q=3, high=3, suffix=3, omit_carry=False):
    """Right unit shear, executed as two sequential split/merge high shifts.

    Payload never uses indexed lookup. Low/chart arithmetic controls the cuts.
    The charts used by the fixture need no ordinary interchange child.
    """
    tape.m.route_actions += 1
    low = list(low)
    for row in range(2):
        x, y = low[2*row:2*row+2]
        new = (y + coefficient*x) % q
        carry = (y + coefficient*x - new) // q
        if omit_carry:
            carry = 0
        low[2*row+1] = new
        target = 2*row+1
        block = high**(3-target)*suffix
        prefixes = high**target
        left, right = Tape(tape.m), Tape(tape.m)
        tape.rewind()
        for prefix in range(prefixes):
            shift = (coefficient*(prefix % high) + carry) % high
            transfer(tape, left, (high-shift)*block)
            transfer(tape, right, shift*block)
        tape.end()
        tape.clear()
        left.rewind()
        right.rewind()
        out = Tape(tape.m)
        for prefix in range(prefixes):
            shift = (coefficient*(prefix % high) + carry) % high
            transfer(right, out, shift*block)
            transfer(left, out, (high-shift)*block)
        left.end()
        right.end()
        left.clear()
        right.clear()
        out.rewind()
        tape = out
        tape.m.shift_actions += 1
    return tape, tuple(low)


def xor(tapes, target, source):
    a, b = tapes[target], tapes[source]
    a.rewind()
    b.rewind()
    need(len(a.cells) == len(b.cells), 'complete XOR shapes')
    out = Tape(a.m)
    for _ in range(len(a.cells)):
        out.append(a.read() ^ b.read())
    a.end()
    b.end()
    a.clear()
    b.rewind()
    out.rewind()
    tapes[target] = out


def word(tapes, skip_restore=False):
    """Dirty helper wrap plus a live immutable snapshot; b <- b+a+h."""
    # a=0, b=1, h=2; both a and h must be restored.
    xor(tapes, 1, 2)
    xor(tapes, 2, 0)
    xor(tapes, 1, 2)
    if not skip_restore:
        xor(tapes, 2, 0)
    private = Tape(tapes[0].m)
    tapes[2].rewind()
    transfer(tapes[2], private, len(tapes[2].cells))
    tapes[2].rewind()
    private.rewind()
    tapes.append(private)
    xor(tapes, 1, 3)
    tapes[2].rewind()
    tapes[3].rewind()
    for _ in range(len(tapes[2].cells)):
        need(tapes[3].read() == tapes[2].read(), 'actual snapshot ERASE guard')
    tapes[2].rewind()
    tapes[3].rewind()
    tapes.pop().clear()


def matmul(a, b, modulus):
    return tuple(sum(a[2*i+k]*b[2*k+j] for k in range(2)) % modulus
                 for i in range(2) for j in range(2))


def shear(t, modulus):
    return (1, t % modulus, 0, 1)


def compile_call(full, lows, invocation, coefficients=(0,1,2), *, omit_carry=False,
                 wrong_return=False, skip_restore=False, partial_unused=False):
    """Gather, route, execute, unroute, in-place scatter. One physical family."""
    q, high, suffix = 3, 3, 3
    packet_cells = high**4*suffix
    owned = [matmul(invocation, shear(-t, q), q) for t in coefficients]
    need(len(set(owned)) == len(owned), 'complete low-packet alias')
    slots = {low: i for i, low in enumerate(owned)}
    packets = [Tape(full.m) for _ in owned]
    full.rewind()
    full.m.family_scans += 1
    for low in lows:
        for j in range(packet_cells):
            value = full.read()
            if low in slots and (not partial_unused or j % suffix != 2):
                packets[slots[low]].append(value)
    full.end()
    full.rewind()
    need(all(len(p.cells) == packet_cells for p in packets), 'complete unused spectator range')
    for i, t in enumerate(coefficients):
        packets[i], result_low = route(packets[i], owned[i], t, omit_carry=omit_carry)
        need(result_low == invocation, 'common invocation alignment')
    word(packets, skip_restore)
    for i, t in enumerate(coefficients):
        packets[i], result_low = route(packets[i], invocation, t if wrong_return else -t,
                                      omit_carry=omit_carry)
        need(result_low == owned[i], 'inverse owner alignment')
    full.m.family_scans += 1
    for low in lows:
        for _ in range(packet_cells):
            if low in slots:
                full.replace_next(packets[slots[low]].read())
            else:
                full.read()
    full.end()
    full.rewind()
    for p in packets:
        p.end()
        p.clear()
    need(full.m.scratch_cells == 0, 'all private work cleared')
    need(full.head == 0, 'physical family head restored')


def fixture():
    # Independent full-ring matrix oracle: no routing/carry code or compiler imported.
    q, modulus, suffix, bits = 3, 9, 3, 17
    lows = [a for a in product(range(q), repeat=4) if (a[0]*a[3]-a[1]*a[2]) % q]
    matrices = [tuple(a+q*b for a,b in zip(low, high))
                for low in lows for high in product(range(q), repeat=4)]
    index = {a:i for i,a in enumerate(matrices)}
    raw = [((i*1103515245 + 12345) ^ (i >> 2)) & ((1 << bits)-1)
           for i in range(len(matrices)*suffix)]
    invocations = [(1,0,0,1), (1,1,0,1)]

    def oracle(before, invocation):
        after = before[:]
        for d in matrices:
            if tuple(x % q for x in d) != invocation:
                continue
            a, b, h = [index[matmul(d, shear(-t, modulus), modulus)] for t in (0,1,2)]
            for u in range(suffix):
                after[b*suffix+u] = before[b*suffix+u] ^ before[a*suffix+u] ^ before[h*suffix+u]
        return after

    meter = Meter()
    full = Tape(meter, raw, scratch=False)
    expected = raw[:]
    for invocation in invocations:
        expected = oracle(expected, invocation)
        compile_call(full, lows, invocation)
        need(full.cells == expected, 'full physical endpoint including spectators')
    # Independent Boolean basis columns, one for every row/spectator record.
    # The same XOR/routing operator acts independently on all 17 payload bits.
    basis = [1 << i for i in range(len(raw))]
    symbolic = Tape(Meter(), basis, scratch=False)
    symbolic_expected = basis
    for invocation in invocations:
        symbolic_expected = oracle(symbolic_expected, invocation)
        compile_call(symbolic, lows, invocation)
        need(symbolic.cells == symbolic_expected, 'all physical Boolean basis columns')
    stale_second = oracle(raw, invocations[1])
    need(stale_second != expected, 'fresh state required at the next invocation')
    packet = 81*suffix
    need(meter.family_scans == 4 and meter.route_actions == 12, 'two scans and six routes per call')
    need(meter.peak_scratch_cells <= 5*packet, 'three roles, private COPY and one extra packet')
    controls = {}
    for name, options in (
        ('missing_high_carry', {'omit_carry': True}),
        ('wrong_return_direction', {'wrong_return': True}),
        ('dirty_helper_not_restored', {'skip_restore': True}),
        ('partial_unused_spectator', {'partial_unused': True}),
        ('same_low_alias', {'coefficients': (0,1,3)}),
    ):
        candidate = Tape(Meter(), raw, scratch=False)
        try:
            compile_call(candidate, lows, invocations[0], **options)
            rejected = candidate.cells != oracle(raw, invocations[0])
        except ValueError:
            rejected = True
        need(rejected, 'undetected semantic mutant '+name)
        controls[name] = 'REJECT'
    controls['stale_next_invocation'] = 'REJECT'
    untouched = 0
    selected_lows = {matmul(d, shear(-t, q), q) for d in invocations for t in (0,1,2)}
    for k, low in enumerate(lows):
        if low not in selected_lows:
            a,b = k*packet,(k+1)*packet
            need(full.cells[a:b] == raw[a:b], 'unowned low packet modified')
            untouched += 1
    return dict(ring='Z/9', group_rows=len(matrices), low_packets=len(lows),
                unused_values=suffix, payload_bits=bits, full_family_bits=len(raw)*bits,
                symbolic_record_columns=len(basis),
                packet_bits=packet*bits, invocations=2, preserved_low_packets=untouched,
                meter={k.replace('_cells','_bits'):(v*bits if k in ('reads','writes','erases','head_moves',
                                         'scratch_cells','peak_scratch_cells') else v)
                       for k,v in vars(meter).items()},
                controls=controls, endpoint_sha256=hashlib.sha256(
                    b''.join(x.to_bytes(3,'little') for x in full.cells)).hexdigest())


def result():
    source = json.loads((HERE/'SOURCES.json').read_text())
    for item in source['files']:
        if item['usage'] == 'input':
            need(hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest() == item['sha256'],
                 'source pin '+item['path'])
    template = json.loads(gzip.decompress((ROOT/HOST).read_bytes()))
    receipt = dict(selected=selected(template), physical_fixture=fixture(),
                   scope='Conditional node compiler; full recursive callees and invoice remain open.')
    import copy
    mutant = copy.deepcopy(template)
    mutant['calls'][0]['owners'][223] = mutant['calls'][0]['owners'][222]
    try:
        selected(mutant)
    except ValueError:
        receipt['selected_owner_collision_control'] = 'REJECT'
    else:
        raise ValueError('selected owner collision accepted')
    return receipt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', type=Path)
    args = parser.parse_args()
    receipt = result()
    if args.write:
        args.write.write_text(json.dumps(receipt, indent=2, sort_keys=True)+'\n')
    else:
        need(json.loads(json.dumps(receipt)) == json.loads((HERE/'RESULT.json').read_text()),
             'committed receipt mismatch')
    print('PASS_BIT_WHOLE_PACKET_STAGING calls=288 owners=190368 physical_rows=3888 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()
