#!/usr/bin/env python3
"""Join the one-target CRT hole mask, reverse-word keys and sparse repair.

The mask is the unary producer composed with the three-tape scanner. Keys at
holes are the #4169 reverse shears followed by the ideal map. The repair
consumes that mask. No host table of S is inverted to obtain a key.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import types

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

PRODUCER = ROOT / "research/crt-unary-stencil-producer/producer.py"
MACHINE = ROOT / "research/crt-dense-guard-scan/machine.py"
REVERSE = ROOT / "research/crt-arbitrary-source-repair/verify.py"
COMPACT = ROOT / "research/unconditional-batched-crt/check_batched_crt.py"
OBLIGATION = ROOT / "research/pr4100-crt-repair-tariff/README.md"

SHAPES = (
    (1, 1, 5, 5, 0, 0),
    (1, 1, 5, 5, 0, 1),
    (1, 2, 6, 7, 1, 0),
    (1, 3, 5, 6, 0, 2),
    (2, 2, 6, 8, 2, 0),
)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    sys.modules[name] = module
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


def authenticate():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    count = 0
    for row in manifest["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"],
             "source SHA256 mismatch: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"],
             "source Git blob mismatch: " + row["path"])
        count += 1
    need(count == 5, "expected five live inputs")
    text = OBLIGATION.read_text()
    need("Compose the hole mask, key evaluator and repair into one fixed-tape\n   program."
         in text, "repair-tariff open question missing")
    return count


def admitted(g, h, k, y, j, b):
    need(g >= 1 and h >= g and k >= g + 4 and j >= 0 and b >= 0 and y >= j + k,
         "admitted one-target geometry")
    return 2 * h + y + b


def expected_atoms(g, h, k, y, j, b):
    """MSB-first stencil from the counting argument in PROOF.md."""
    length = admitted(g, h, k, y, j, b)
    intervals = ((h - g, h, "D"), (2 * h - g, 2 * h, "D"),
                 (2 * h + y - j - k, 2 * h + y - j - 1, "G"))
    low, high = 1 << (g + 1), (1 << (k - 1)) - (1 << (g + 1))
    skip = ("S", False, False, "0", "0")
    atoms = []
    for position in range(length):
        atom = skip
        for start, stop, kind in intervals:
            if start <= position < stop:
                need(atom == skip, "interval overlap")
                shift = stop - 1 - position
                atom = (kind, position == start, position == stop - 1,
                        str((low >> shift) & 1) if kind == "G" else "0",
                        str((high >> shift) & 1) if kind == "G" else "0")
        atoms.append(atom)
    return atoms


def split_address(address, h, y, b):
    back = address % (1 << b)
    y_word = (address >> b) % (1 << y)
    t_word = (address >> (b + y)) % (1 << h)
    u_word = address >> (b + y + h)
    return u_word, t_word, y_word, back


def pack_address(u, t, y, back, h, y_bits, b):
    return (((u << h) | t) << y_bits | y) << b | back


def hole_predicate(u, t, y, g, k, j):
    radix = 1 << g
    if (u % radix) == radix - 1 or (t % radix) == radix - 1:
        return True
    higher = (y >> (j + 1)) % (1 << (k - 1))
    return not (2 * radix <= higher < (1 << (k - 1)) - 2 * radix)


def unary(machine, n):
    return machine.Tape([machine.LEFT] + ["1"] * n + [machine.END, machine.BLANK])


def blank(machine, tape):
    return (tape.head == 0 and tape.cells[0] == machine.LEFT
            and all(cell == machine.BLANK for cell in tape.cells[1:]))


def rewind(tape, left):
    while tape.read() != left:
        tape.move(-1)


def read_mask(machine, mask):
    rewind(mask, machine.LEFT)
    mask.move(1)
    bits = []
    while True:
        symbol = mask.read()
        if symbol == machine.END:
            break
        need(symbol in ("0", "1"), "mask alphabet")
        bits.append(symbol)
        mask.move(1)
    rewind(mask, machine.LEFT)
    return bits


def erase_mask(machine, mask):
    rewind(mask, machine.LEFT)
    mask.move(1)
    while True:
        symbol = mask.read()
        mask.write(machine.BLANK)
        if symbol == machine.END:
            break
        mask.move(1)
    rewind(mask, machine.LEFT)


class RecordTape:
    """Cell tape used by the repair schedule. Records are opaque payloads."""

    def __init__(self, width):
        self.w = width
        self.pos = 0
        self.end = 0
        self.moves = 0
        self.cells = []

    def goto(self, index):
        self.moves += abs(index - self.pos) * self.w
        self.pos = index

    def write(self, value):
        if self.pos == len(self.cells):
            self.cells.append(value)
        else:
            self.cells[self.pos] = value
        self.pos += 1
        self.moves += self.w
        self.end = max(self.end, self.pos)

    def read(self):
        need(self.pos < self.end, "read past end")
        value = self.cells[self.pos]
        self.pos += 1
        self.moves += self.w
        return value

    def truncate(self):
        self.end = self.pos
        del self.cells[self.pos:]

    def erase(self):
        self.goto(self.end)
        self.goto(0)
        self.moves += self.end * self.w
        self.end = 0
        self.cells = []


class Counter:
    def __init__(self, length):
        self.bits = [0] * length
        self.moves = 0
        self.length = length

    def increment(self):
        i = 0
        while i < self.length and self.bits[i]:
            self.bits[i] = 0
            i += 1
        if i < self.length:
            self.bits[i] = 1
        self.moves += 2 * (i + 1)

    def value(self):
        self.moves += 2 * self.length
        return sum(bit << i for i, bit in enumerate(self.bits))

    def reset(self):
        self.bits = [0] * self.length
        self.moves += 2 * self.length


def bounds(length, size, width, holes):
    dense = 9 * size * width + 5 * size
    sparse = holes * (length + width) * (9 * length + 6)
    counter = 8 * size + 4 * length * holes + 4 * length
    return dense, sparse, counter


def produce_mask(machine, producer, shape):
    g, h, k, y, j, b = shape
    length = admitted(g, h, k, y, j, b)
    inputs = tuple(unary(machine, n) for n in shape)
    before = [list(tape.cells) for tape in inputs]
    work, stencil = producer.produce(*inputs, machine.Tape)
    need(all(list(tape.cells) == old for tape, old in zip(inputs, before)),
         "geometry inputs rewritten")
    need(all(blank(machine, tape) for tape in work), "producer private tape survived")
    need(all(tape.head == 0 for tape in inputs + work + (stencil,)),
         "producer head not returned")
    atoms = tuple(stencil.cells[1:-1])
    need(stencil.cells[0] == machine.LEFT and stencil.cells[-1] == machine.END,
         "stencil sentinels")
    need(atoms == tuple(expected_atoms(*shape)), "stencil atoms differ from the counting table")
    invoice = sum(tape.actions for tape in inputs + work + (stencil,))
    need(invoice == 33 * h + 25 * k + 38 * y - 6 * g - j + 12 * b + 335,
         "producer invoice")
    previous = stencil.actions
    counter, mask = machine.transduce(stencil)
    need(list(stencil.cells) == [machine.LEFT, *atoms, machine.END], "scanner rewrote the stencil")
    need(blank(machine, counter), "scanner counter survived")
    need(mask.head == stencil.head == 0, "scanner head not returned")
    scan = stencil.actions - previous + counter.actions + mask.actions
    size = 1 << length
    need(scan == 8 * size * length + 15 * size + 13 * length + 18, "scanner invoice")
    return mask, invoice, scan


def repair(machine, mask, length, size, width, holes, keys, payloads_at_s):
    """#4328 schedule. holes[x] and keys[x] are already the mask and reverse-word outputs."""
    data, good, bad = RecordTape(width), RecordTape(width), RecordTape(length + width)
    buckets = [RecordTape(length + width), RecordTape(length + width)]
    counter = Counter(length)
    bits = read_mask(machine, mask)
    need(bits == ["1" if hole else "0" for hole in holes], "repair did not read the mask tape")
    for address in range(size):
        data.write(payloads_at_s[address])
    data.truncate()
    data.goto(0)
    data.moves = 0
    evaluations = 0
    for address in range(size):
        hole = bits[address] == "1"
        record = data.read()
        if hole:
            need(counter.value() == address, "counter")
            evaluations += 1
            bad.write((keys[address], record))
        else:
            good.write(record)
        counter.increment()
    bad.truncate()
    good.truncate()
    hole_count = bad.end
    for bit in range(length):
        bad.goto(0)
        for _ in range(hole_count):
            key, record = bad.read()
            buckets[(key >> bit) & 1].write((key, record))
        for bucket in buckets:
            bucket.truncate()
        bad.goto(0)
        for bucket in buckets:
            bucket.goto(0)
            for _ in range(bucket.end):
                bad.write(bucket.read())
            bucket.erase()
        bad.truncate()
    bad.goto(0)
    bits = read_mask(machine, mask)
    good.goto(0)
    data.goto(0)
    counter.reset()
    layout = []
    for address in range(size):
        if bits[address] == "1":
            key, record = bad.read()
            need(counter.value() == address and key == address, "sorted key is not this hole")
        else:
            record = good.read()
        data.write(record)
        layout.append(record)
        counter.increment()
    for tape in (good, bad):
        tape.erase()
    erase_mask(machine, mask)
    need(blank(machine, mask), "mask not erased")
    need(good.end == bad.end == 0 and buckets[0].end == buckets[1].end == 0,
         "repair scratch survived")
    dense = data.moves + good.moves
    # Mask head motion is on the scanner tape; charge one cell per bit read
    # and the erasure sweep already performed above. The two reads and the
    # erase are the tariff's 5M mask allowance at width 1, checked separately.
    sparse = bad.moves + buckets[0].moves + buckets[1].moves
    return layout, dict(dense=dense, sparse=sparse, counter=counter.moves,
                        evaluations=evaluations, holes=hole_count)


def run_shape(machine, producer, word_cls, crt, shape, source, key_mode="ideal"):
    g, h, k, y, j, b = shape
    length = admitted(*shape)
    size = 1 << length
    mask, producer_invoice, scan_invoice = produce_mask(machine, producer, shape)
    bits = read_mask(machine, mask)
    need(len(bits) == size, "mask length")
    word = word_cls(g, h, y, (j,), k)
    for state_y in range(1 << y):
        bit = source(state_y)
        need(bit == source(state_y ^ (1 << j)) and bit in ((0,), (1,)),
             "source meets the target")
    holes = []
    forward_ok = inverse_ok = good_agreement = 0
    keys = [None] * size
    arrived = [None] * size
    ideal_at = [None] * size
    for address in range(size):
        u, t, y_word, back = split_address(address, h, y, b)
        hole = hole_predicate(u, t, y_word, g, k, j)
        need(hole == (bits[address] == "1"), "mask bit differs from the integer hole set")
        need(hole == (not crt.good(u, t, y_word, bits=g, positions=(j,), guard=k)),
             "integer hole set differs from the pinned predicate")
        need(hole == (not word.good((u, t, y_word))), "reverse-word predicate differs")
        holes.append(hole)
        state = (u, t, y_word)
        forward = word.run(state, source)
        pinned = crt.compact(u, t, y_word, source, bits=g, positions=(j,),
                             ybits=y, control_bits=h)
        need(forward == pinned, "reverse-word forward shear differs from compact")
        origin = word.run(state, source, inverse=True)
        need(word.run(origin, source) == state, "reverse shears are not a left inverse")
        need(word.run(forward, source, inverse=True) == state, "reverse shears are not a right inverse")
        forward_ok += 1
        inverse_ok += 1
        ideal = word.ideal(state, source)
        need(pack_address(*ideal, back, h, y, b)
             == pack_address(u, t, y_word ^ (source(y_word)[0] << j), back, h, y, b),
             "ideal map")
        if not hole:
            need(forward == ideal, "S and T disagree on a good address")
            good_agreement += 1
        image = pack_address(*forward, back, h, y, b)
        need(arrived[image] is None, "S is not injective")
        arrived[image] = address
        if key_mode == "ideal":
            key_state = word.ideal(origin, source)
        elif key_mode == "origin":
            key_state = origin
        else:
            raise ValueError(key_mode)
        keys[address] = pack_address(*key_state, back, h, y, b)
        ideal_at[address] = pack_address(*ideal, back, h, y, b)
    need(all(item is not None for item in arrived), "S is not surjective")
    need(good_agreement > 0 and good_agreement < size, "hole set is trivial")
    # Payload of origin q is placed at S(q).
    placed = [arrived[address] for address in range(size)]
    width = length
    layout, meters = repair(machine, mask, length, size, width, holes, keys, placed)
    for origin in range(size):
        need(layout[ideal_at[origin]] == origin, "payload was not restored")
    dense_bound, sparse_bound, counter_bound = bounds(length, size, width, meters["holes"])
    need(meters["evaluations"] == meters["holes"], "a good address was evaluated")
    need(meters["sparse"] <= sparse_bound and meters["counter"] <= counter_bound,
         "repair exceeded the #4328 sparse or counter bound")
    # DATA is charged here without the tariff's initial zeroing. The documented
    # dense bound also covers the mask at width 1 and a full-width good stream.
    need(meters["dense"] <= dense_bound, "repair exceeded the #4328 dense bound")
    return dict(addresses=size, holes=meters["holes"], good_agreements=good_agreement,
                forward=forward_ok, inverse=inverse_ok,
                producer=producer_invoice, scanner=scan_invoice,
                dense=meters["dense"], sparse=meters["sparse"], counter=meters["counter"])


def expect_flipped_mask_mismatch(machine, producer, word_cls, shape, source):
    """A complemented mask still has keys equal to its marked addresses.

    S equals T on the good set, so T(S^{-1}(x)) = x there. The address test
    therefore accepts the complemented mask. The payloads, which were moved by
    the true S, are not the ideal image.
    """
    g, h, k, y, j, b = shape
    length = admitted(*shape)
    size = 1 << length
    mask, _, _ = produce_mask(machine, producer, shape)
    rewind(mask, machine.LEFT)
    mask.move(1)
    for _ in range(size):
        need(mask.read() in ("0", "1"), "mask alphabet")
        mask.write("0" if mask.read() == "1" else "1")
        mask.move(1)
    rewind(mask, machine.LEFT)
    word = word_cls(g, h, y, (j,), k)
    holes = []
    keys = [None] * size
    placed = [None] * size
    ideal_at = [None] * size
    for address in range(size):
        u, t, y_word, back = split_address(address, h, y, b)
        holes.append(not hole_predicate(u, t, y_word, g, k, j))
        state = (u, t, y_word)
        forward = word.run(state, source)
        origin = word.run(state, source, inverse=True)
        key_state = word.ideal(origin, source)
        keys[address] = pack_address(*key_state, back, h, y, b)
        image = pack_address(*forward, back, h, y, b)
        need(placed[image] is None, "S collided under the flipped-mask control")
        placed[image] = address
        ideal = word.ideal(state, source)
        ideal_at[address] = pack_address(*ideal, back, h, y, b)
    layout, _meters = repair(machine, mask, length, size, length, holes, keys, placed)
    mismatches = sum(layout[ideal_at[origin]] != origin for origin in range(size))
    need(mismatches > 0, "complemented mask restored every ideal payload")


def main():
    authenticate()
    machine = load(MACHINE, "joined_scanner")
    producer = load(PRODUCER, "joined_producer")
    reverse = load(REVERSE, "joined_reverse_word")
    crt = load(COMPACT, "joined_compact")
    rows = []
    for shape in SHAPES:
        j = shape[4]
        rows.append(run_shape(machine, producer, reverse.Word, crt, shape,
                              lambda y, j=j: ((y >> (j + 1)) & 1,)))
    rows.append(run_shape(machine, producer, reverse.Word, crt, SHAPES[0],
                          lambda y: ((y >> 2) & 1,)))
    # Origin keys permute holes and fail the ideal restoration.
    try:
        run_shape(machine, producer, reverse.Word, crt, SHAPES[0],
                  lambda y: ((y >> 1) & 1,), key_mode="origin")
    except ValueError as exc:
        need("payload was not restored" in str(exc), "origin-key control failed differently")
    else:
        raise ValueError("origin keys restored the ideal payload")
    expect_flipped_mask_mismatch(machine, producer, reverse.Word, SHAPES[0],
                                lambda y: ((y >> 1) & 1,))
    # A source that reads the target is outside the hypothesis.
    try:
        run_shape(machine, producer, reverse.Word, crt, SHAPES[0],
                  lambda y: ((y >> 0) & 1,))
    except ValueError as exc:
        need("source meets the target" in str(exc), "target-dependent source failed differently")
    else:
        raise ValueError("target-dependent source was accepted")
    addresses = sum(row["addresses"] for row in rows)
    holes = sum(row["holes"] for row in rows)
    print("PASS_CRT_JOINED_HOLE_REPAIR")
    print(json.dumps({"shapes": len(rows), "addresses": addresses, "holes": holes,
                      "rows": rows}, sort_keys=True))


if __name__ == "__main__":
    main()
