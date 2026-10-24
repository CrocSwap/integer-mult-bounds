"""Source-bound two-target producer/consumer replay; read-only by default.

Hiroki KUMAZAKI (@kumagi), substantial OpenAI Codex assistance. Apache-2.0.
Predecessor code and proofs retain the attribution in README/PROOF.
Host geometry/oracles and keys are verification work, not hidden tape steps.
"""
from __future__ import annotations

import argparse
import hashlib
from itertools import product
import json
from pathlib import Path
import sys
import types

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SHAPES = ((1, 2, 5, 10, 0, 5, 0), (1, 2, 5, 10, 0, 5, 1),
          (1, 3, 5, 10, 0, 5, 0), (1, 2, 5, 12, 1, 7, 0))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def authenticate():
    data = {}
    for row in json.loads((PACKAGE/'SOURCES.json').read_text())['files']:
        if row['usage'] != 'input':
            continue
        raw = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == row['sha256'], 'source SHA256 mismatch: '+row['path'])
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'source Git blob mismatch: '+row['path'])
        data[row['path']] = raw
    need(len(data) == 13, 'exact thirteen-input scope')
    return data


def load(name, path, raw):
    module = types.ModuleType(name)
    module.__file__ = str(ROOT/path)
    sys.modules[name] = module
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module


def blank(machine, tape):
    return tape.head == 0 and tape.cells[0] == machine.LEFT and all(
        x == machine.BLANK for x in tape.cells[1:])


class Ports:
    """Observer-side registry; the producer sees only read/write/move ports."""
    def __init__(self, machine):
        self.machine = machine
        self.tapes = {}
        self.calls = [0, 0, 0]

    def make(self, cells=None):
        underlying = self.machine.Tape(cells)
        owner = self

        class Port:
            __slots__ = ()

            def read(self):
                owner.calls[0] += 1
                return underlying.read()

            def write(self, symbol):
                owner.calls[1] += 1
                underlying.write(symbol)

            def move(self, direction):
                owner.calls[2] += 1
                underlying.move(direction)

        port = Port()
        self.tapes[port] = underlying
        return port

    def unary(self, n):
        return self.make([self.machine.LEFT]+['1']*n+[self.machine.END, self.machine.BLANK])


def expected_atoms(shape):
    """Independent address-interval oracle; never used by the producer."""
    g, h, k, y, j0, j1, back = shape
    length = 2*h+y+back
    ranges = []
    for start in (0, h):
        for i in (0, 1):
            ranges.append((start+h-(i+1)*g, start+h-i*g, 'D'))
    for target in (j0, j1):
        ranges.append((2*h+y-target-k, 2*h+y-target-1, 'G'))
    low, high = 1 << (g+1), (1 << (k-1))-(1 << (g+1))
    result = []
    for position in range(length):
        found = [(a, b, kind) for a, b, kind in ranges if a <= position < b]
        need(len(found) <= 1, 'oracle disjoint intervals')
        if not found:
            result.append(('S', False, False, '0', '0'))
        else:
            a, b, kind = found[0]
            shift = b-1-position
            result.append((kind, position == a, position == b-1,
                           str((low >> shift) & 1) if kind == 'G' else '0',
                           str((high >> shift) & 1) if kind == 'G' else '0'))
    return result


def producer_bill(shape):
    g, h, k, y, j0, j1, back = shape
    return 46*h+20*k+38*y-24*g-j0+12*j1+12*back+438


def producer_space(shape):
    g, h, k, y, j0, j1, back = shape
    return 5*h+k+4*y-3*g+j1+2*back+47


def produce(machine, base, producer, shape, **mutants):
    ports = Ports(machine)
    inputs = tuple(ports.unary(n) for n in shape)
    before = [list(ports.tapes[p].cells) for p in inputs]
    work, stencil = producer.produce(*inputs, ports.make, base=base, **mutants)
    need(len(ports.tapes) == 19 and len(work) == 11, 'fixed nineteen producer roles')
    need(all(ports.tapes[p].cells == old for p, old in zip(inputs, before)), 'protected unary inputs')
    need(all(blank(machine, ports.tapes[p]) for p in work), 'producer work/END cleanup')
    need(all(t.head == 0 for t in ports.tapes.values()), 'all producer heads returned')
    tape = ports.tapes[stencil]
    need(tape.cells[0] == machine.LEFT and tape.cells[-1] == machine.END, 'stencil markers')
    actions = sum(t.actions for t in ports.tapes.values())
    need(actions == sum(ports.calls), 'independent primitive-call meter')
    space = sum(len(t.cells) for t in ports.tapes.values())
    if not any(mutants.values()):
        need(tape.cells[1:-1] == expected_atoms(shape), 'literal producer versus interval oracle')
        need(actions == producer_bill(shape), 'exact producer action formula')
        need(space == producer_space(shape), 'exact visited producer cells')
        length = 2*shape[1]+shape[3]+shape[6]
        need(actions <= 70*length+438 and space <= 6*length+47, 'linear producer bounds')
    return tape, actions, space


def stencil_grid(machine, base, producer):
    cases = 0
    largest = 0
    for g, extra, guard_extra, j0, gap, top, back in product(
            range(1, 4), range(3), range(3), (0, 1, 3), (0, 1, 2), (0, 1), (0, 1)):
        h, k = 2*g+extra, g+4+guard_extra
        j1 = j0+k+gap
        shape = g, h, k, j1+k+top, j0, j1, back
        _, actions, _ = produce(machine, base, producer, shape)
        largest = max(largest, actions)
        cases += 1
    # A long stencil checks marker loops without enumerating its address cube.
    large = (7, 31, 17, 500, 9, 400, 23)
    _, actions, space = produce(machine, base, producer, large)
    return dict(grid_shapes=cases, grid_max_actions=largest,
                large_shape=large, large_actions=actions, large_visited_cells=space)


def rejects(machine, base, producer):
    invalid = ((0, 2, 5, 10, 0, 5, 0), (2, 3, 6, 12, 0, 6, 0),
               (1, 2, 4, 10, 0, 5, 0), (1, 2, 5, 10, 2, 1, 0),
               (1, 2, 5, 10, 0, 4, 0), (1, 2, 5, 9, 0, 5, 0))
    tested = 0
    for shape in invalid + (SHAPES[0],)*3:
        ports = Ports(machine)
        inputs = tuple(ports.unary(n) for n in shape)
        if tested == len(invalid):
            ports.tapes[inputs[0]].cells[1] = 'x'
        elif tested == len(invalid)+1:
            ports.tapes[inputs[0]].cells[-1] = '1'
        elif tested == len(invalid)+2:
            ports.tapes[inputs[0]].head = 1
        before = [list(ports.tapes[p].cells) for p in inputs]
        try:
            producer.produce(*inputs, ports.make, base=base)
        except ValueError:
            pass
        else:
            raise ValueError('invalid geometry/grammar unexpectedly accepted')
        need(all(ports.tapes[p].cells == old for p, old in zip(inputs, before)), 'reject preserves inputs')
        need(all(t.head == 0 for t in ports.tapes.values()), 'reject restores heads')
        need(all(blank(machine, t) for p, t in ports.tapes.items() if p not in inputs),
             'reject cleans private/output markers')
        tested += 1
    return tested


def scan(machine, stencil):
    before = list(stencil.cells)
    length = len(before)-2
    previous = stencil.actions
    counter, mask = machine.transduce(stencil)
    invoice = stencil.actions-previous+counter.actions+mask.actions
    need(stencil.cells == before and stencil.head == mask.head == 0, 'scanner protected input/heads')
    need(blank(machine, counter), 'scanner work cleared')
    need(invoice == 8*(1 << length)*length+15*(1 << length)+13*length+18, 'unchanged scanner invoice')
    return mask, invoice


def expected_good(shape):
    g, h, k, y, j0, j1, back = shape
    return ((1 << g)-1)**4 * ((1 << (k-1))-(1 << (g+2)))**2 * (
        1 << (2*(h-2*g)+y-2*(k-1)+back))


def run_shape(machine, base, producer, joined, Word, crt, shape):
    g, h, k, y, j0, j1, back = shape
    length = 2*h+y+back
    size = 1 << length
    stencil, setup, visited = produce(machine, base, producer, shape)
    mask, scanning = scan(machine, stencil)
    bits = joined.read_mask(machine, mask)
    need(len(bits) == size, 'complete scanner mask')
    word = Word(g, h, y, (j0, j1), k)

    def source(current_y):
        return (((current_y >> (j0+1)) ^ (current_y >> (j1+2))) & 1,
                ((current_y >> (j1+1)) ^ (current_y >> (j0+2))) & 1)

    word.check_source(source)
    arrived, ideal_at, keys = [None]*size, [None]*size, [None]*size
    holes = []
    good = 0
    for address in range(size):
        u, t, middle, tail = joined.split_address(address, h, y, back)
        state = u, t, middle
        per_target = [(((u >> (i*g)) % (1 << g)) != (1 << g)-1
                       and ((t >> (i*g)) % (1 << g)) != (1 << g)-1
                       and 2*(1 << g) <= ((middle >> (j+1)) % (1 << (k-1)))
                       < (1 << (k-1))-2*(1 << g)) for i, j in enumerate((j0, j1))]
        hole = not all(per_target)
        need(hole == (bits[address] == '1'), 'produced mask is union of target failures')
        need(hole == (not word.good(state)) == (not crt.good(u, t, middle,
             bits=g, positions=(j0, j1), guard=k)), 'both retained good predicates')
        holes.append(hole)
        out = word.run(state, source)
        need(out == crt.compact(u, t, middle, source, bits=g, positions=(j0, j1),
                               ybits=y, control_bits=h), 'literal forward versus retained compact')
        origin = word.run(state, source, inverse=True)
        need(word.run(origin, source) == state, 'literal inverse/forward')
        wanted = word.ideal(state, source)
        need(word.good(out) == word.good(state) == word.good(wanted), 'good/bad invariance')
        if not hole:
            need(out == wanted, 'good endpoint equals ideal')
            good += 1
        image = joined.pack_address(*out, tail, h, y, back)
        need(arrived[image] is None, 'raw image injectivity')
        arrived[image] = address
        ideal_at[address] = joined.pack_address(*wanted, tail, h, y, back)
        if hole:
            keys[address] = joined.pack_address(*word.ideal(origin, source), tail, h, y, back)
    need(good == expected_good(shape) and all(x is not None for x in arrived), 'exact product count and bijection')
    mask_hash = hashlib.sha256(''.join(bits).encode()).hexdigest()
    layout, meters = joined.repair(machine, mask, length, size, length, holes, keys, arrived)
    need(all(layout[ideal_at[q]] == q for q in range(size)), 'complete ideal payload restoration')
    need(meters['evaluations'] == size-good, 'repair evaluates keys only at holes')
    dense, sparse, counter = joined.bounds(length, size, length, size-good)
    need(meters['dense'] <= dense and meters['sparse'] <= sparse and meters['counter'] <= counter,
         'retained record-cell repair bounds')
    need(blank(machine, mask), 'consumed mask cleanup')
    # The stencil is owned output from the predecessor; this caller explicitly retires it.
    old_actions = stencil.actions
    base.erase(stencil)
    retirement = stencil.actions-old_actions
    need(retirement == 5*length+7 and blank(machine, stencil), 'owned stencil retirement')
    return dict(shape=shape, addresses=size, good=good, holes=size-good, producer_actions=setup,
                producer_visited_cells=visited, scanner_actions=scanning,
                stencil_retirement_actions=retirement, mask_sha256=mask_hash,
                repaired_payload_sha256=hashlib.sha256(b''.join(x.to_bytes(4,'little') for x in layout)).hexdigest(),
                repair_record_cell_meters=meters)


def semantic_controls(machine, base, producer, joined, Word):
    shape = SHAPES[0]
    g, h, k, y, j0, j1, back = shape
    word = Word(g, h, y, (j0, j1), k)
    expected = [not word.good(joined.split_address(x,h,y,back)[:3]) for x in range(1 << (2*h+y+back))]
    results = []
    for name in ('omit_second_digit', 'omit_second_guard'):
        stencil, _, _ = produce(machine, base, producer, shape, **{name: True})
        mask, _ = scan(machine, stencil)
        bits = joined.read_mask(machine, mask)
        wrong = [i for i, (bit, want) in enumerate(zip(bits, expected)) if (bit == '1') != want]
        need(wrong and all(expected[i] and bits[i] == '0' for i in wrong), 'omission under-detects holes')
        results.append(dict(program=name, mismatch_count=len(wrong), first_missing_hole=wrong[0]))
    def cross_source(value):
        return (value >> j1) & 1, (value >> j0) & 1
    try:
        word.check_source(cross_source)
    except ValueError:
        pass
    else:
        raise ValueError('source reading other active target accepted')
    need(word.ideal((0,0,0),cross_source) == word.ideal((0,0,(1 << j0)|(1 << j1)),cross_source),
         'cross-target source produces an actual ideal collision')
    return dict(omitted_tests=results, cross_target_source_rejected=True, cross_target_ideal_collision=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    sources = authenticate()
    modules = []
    for name, path in (
        ('two_target_base','research/crt-unary-stencil-producer/producer.py'),
        ('two_target_machine','research/crt-dense-guard-scan/machine.py'),
        ('two_target_join','research/crt-joined-hole-repair/verify.py'),
        ('two_target_word','research/crt-arbitrary-source-repair/verify.py'),
        ('two_target_crt','research/unconditional-batched-crt/check_batched_crt.py')):
        modules.append(load(name,path,sources[path]))
    path = 'research/crt-two-target-stencil/producer.py'
    producer = load('two_target_producer',path,(ROOT/path).read_bytes())
    base, machine, joined, reverse, crt = modules
    result = dict(status='PASS_CRT_TWO_TARGET_STENCIL', authenticated_inputs=len(sources),
                  producer_grid=stencil_grid(machine,base,producer),
                  clean_rejections=rejects(machine,base,producer),
                  cases=[run_shape(machine,base,producer,joined,reverse.Word,crt,s) for s in SHAPES],
                  controls=semantic_controls(machine,base,producer,joined,reverse.Word))
    encoded = json.dumps(result,indent=2,sort_keys=True)+'\n'
    path = PACKAGE/'RESULT.json'
    if args.write_result:
        path.write_text(encoded)
    else:
        need(path.read_text() == encoded, 'frozen RESULT.json differs; no files rewritten')
    print(result['status'])
    print(str(sum(r['addresses'] for r in result['cases']))+' addresses; '+str(sum(r['holes'] for r in result['cases']))+' repaired holes')
    print('972 small and one long produced stencil; 9 cleaned rejections; 2 omission controls; source collision control')


if __name__ == '__main__':
    main()
