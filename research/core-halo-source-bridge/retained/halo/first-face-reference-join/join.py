#!/usr/bin/env python3
"""Stream first-face transport through a source-bound shrinking halo consumer.

Actual reads/writes/unit moves are executed across both tape representations.
Sparse control-word arithmetic is an explicit O(w^2) macro tariff, as in the
consumer; this composed program does NOT claim transport's finite-local-only
control boundary. There is no host regrouping of saved payloads.
"""

from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys


PACKAGE = Path(__file__).resolve().parent
RESEARCH = PACKAGE.parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


B = load("join_transport", RESEARCH / "sparse-halo-tape-transaction/tapes.py")
M = load("shrinking_halo_engine", RESEARCH / "shrinking-reference-halo/engine.py")
T = load("join_tensor", RESEARCH / "shrinking-reference-halo/tensor.py")
S = load("join_source", RESEARCH / "shrinking-reference-halo/source.py")


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Shape:
    ell: int
    ks: tuple
    spectator_width: int
    boundary: int
    halo: int
    payload_width: int

    def __post_init__(self):
        need(self.ell >= 1 and self.ks and all(k >= 1 for k in self.ks), "dyadic shape")
        need(0 <= self.halo < self.boundary and self.length > 4 * self.boundary, "first-face geometry")

    @property
    def length(self):
        return 1 << self.ell

    @property
    def g(self):
        return len(self.ks)

    @property
    def coordinate_width(self):
        return self.spectator_width + sum(k + self.ell for k in self.ks)

    @property
    def prefix_width(self):
        return self.spectator_width + sum(self.ks) + self.g + 1

    @property
    def saved_key_width(self):
        return 2 * self.coordinate_width + 3 * self.g + 1


def read_unsigned(tape, width):
    """Read each B cell; reconstruct one bounded scalar control field."""
    value = 0
    for _ in range(width):
        bit = tape.read()
        need(bit in "01", "truncated or nonbinary saved key")
        value = 2 * value + (bit == "1")
        tape.move(1)
    return value


def write_unsigned(tape, value, width):
    need(0 <= value < 1 << width, "canonical return carrier")
    for shift in range(width - 1, -1, -1):
        B.append(tape, "1" if (value >> shift) & 1 else "0")


def delimiter(tape):
    need(tape.read() == "#", "saved field delimiter")
    tape.move(1)


class Codec:
    """One current rectangle, one pending prefix, no host payload container.

    Tuples here contain only encoded geometry/control words, total O(w) bits.
    Their arithmetic is priced separately from executed tape primitives.
    """

    def __init__(self, transport, shape, archive, pool, bill, fault=None):
        self.transport = transport
        self.shape = shape
        self.archive = archive
        self.pool = pool
        self.bill = bill
        self.fault = fault
        self.prefix = None
        self.previous_prefix = -1
        self.copied_records = 0
        self.returned_records = 0
        self.rectangles = 0
        self.cropped_records = 0
        self._fault_used = False
        need(len(archive.plans) == shape.g, "one reference plan per active axis")
        need(all(p.period == 1 << (k + shape.ell) for p, k in zip(archive.plans, shape.ks)), "shared periodic coordinates")
        need(all(p.halo <= shape.halo for p in archive.plans), "saved domain covers every consumer halo")
        need(all(2 * p.data_width == shape.payload_width for p in archive.plans), "common exact payload codec")
        B.home(transport.saved)
        B.end(transport.returns)

    def begin_rectangle(self, prefix):
        s = self.shape
        need(prefix > self.previous_prefix, "strictly ordered unique rectangle prefixes")
        self.prefix = self.previous_prefix = prefix
        side = prefix & 1
        onehot = (prefix >> 1) & ((1 << s.g) - 1)
        need(onehot != 0 and onehot & (onehot - 1) == 0, "one-hot first face")
        face = s.g - onehot.bit_length()
        prefix >>= s.g + 1
        core = [0] * s.g
        for i in range(s.g - 1, -1, -1):
            core[i] = prefix & ((1 << s.ks[i]) - 1)
            prefix >>= s.ks[i]
        self.spectator = prefix
        need(prefix < 1 << s.spectator_width, "spectator prefix width")
        targets = []
        for i, c in enumerate(core):
            if i < face:
                lo, length = s.boundary, s.length - 2 * s.boundary
            elif i == face:
                lo, length = (0 if side == 0 else s.length - s.boundary), s.boundary
            else:
                lo, length = 0, s.length
            targets.append((c * s.length + lo, length))
        self.targets = tuple(targets)
        self.full_lengths = tuple(length + 2 * s.halo for _, length in targets)
        self.expected_offsets = [0] * s.g
        self.full_count = 1
        for length in self.full_lengths:
            self.full_count *= length
        self.read_count = self.kept_count = 0
        self.layout = T.Layout.make(self.archive.plans, self.targets)
        self.input = self.pool.rectangles[0]
        need(all(t.head == 0 and t.live_bits == 0 and not t.readonly for t in self.pool.roles), "one reused blank consumer workspace")

    def advance_offsets(self):
        axis = self.shape.g - 1
        while axis >= 0:
            self.expected_offsets[axis] += 1
            if self.expected_offsets[axis] < self.full_lengths[axis]:
                break
            self.expected_offsets[axis] = 0
            axis -= 1

    def canonical_key(self, coordinates):
        key = self.spectator
        for x, k in zip(coordinates, self.shape.ks):
            axis_width = k + self.shape.ell
            key = (key << axis_width) | (x & ((1 << axis_width) - 1))
        return key

    def accept_record(self):
        s = self.shape
        tape = self.transport.saved
        offsets = tuple(read_unsigned(tape, s.ell + 2) for _ in s.ks)
        if self.fault == "offset" and not self._fault_used:
            offsets = (offsets[0] + 1,) + offsets[1:]
            self._fault_used = True
        need(self.read_count < self.full_count and offsets == tuple(self.expected_offsets), "complete ordered saved offsets")
        source_key = read_unsigned(tape, s.coordinate_width)
        coordinates = tuple(lo - s.halo + off for (lo, _), off in zip(self.targets, offsets))
        expected_source = self.canonical_key(coordinates)
        if self.fault == "omit_wrap" and not self._fault_used and any(x < 0 for x in coordinates):
            expected_source = self.canonical_key(tuple(max(0, x) for x in coordinates))
            self._fault_used = True
        need(source_key == expected_source, "canonical source suffix binds saved offset")
        delimiter(tape)
        delta = tuple(s.halo - p.halo for p in self.archive.plans)
        keep = all(d <= off < length - d for off, d, length in zip(offsets, delta, self.full_lengths))
        if keep:
            recoded = tuple(off - d for off, d in zip(offsets, delta))
            key = self.layout.key(recoded)
            dropping = self.fault == "drop_saved" and not self._fault_used
            if dropping:
                self._fault_used = True
            else:
                T.put_unsigned(self.input, key, self.layout.key_width)
        else:
            dropping = False
        for place in range(s.payload_width):
            bit = tape.read()
            need(bit in "01", "complete saved payload")
            tape.move(1)
            if self.fault == "payload_magnitude" and place == 2:
                bit = "0" if bit == "1" else "1"
                self._fault_used = True
            if keep and not dropping:
                self.input.write(1 if bit == "1" else 0)
                self.input.step(1)
        delimiter(tape)
        self.read_count += 1
        self.copied_records += 1
        if keep and not dropping:
            self.kept_count += 1
        else:
            self.cropped_records += 1
        self.advance_offsets()

    def finish_rectangle(self):
        if self.prefix is None:
            return
        need(self.read_count == self.full_count, "complete common-halo rectangle")
        need(self.kept_count == self.layout.volume, "complete consumer-halo rectangle")
        self.input.rewind()
        output = T.apply_tensor(self.archive, self.targets, self.input, self.bill, workspace=self.pool)
        prior = -1
        for _ in range(output.count):
            local_key = T.get_unsigned(output.tape, output.layout.key_width)
            need(local_key > prior, "ordered unique consumer targets")
            prior = local_key
            coordinates = tuple(output.layout.lowers[i] + output.layout.coordinate(local_key, i) for i in range(self.shape.g))
            need(all(lo <= x < lo + length for x, (lo, length) in zip(coordinates, self.targets)), "consumer target-only coordinate")
            key = self.canonical_key(coordinates)
            if self.fault == "return_key" and not self._fault_used:
                key ^= 1
                self._fault_used = True
            write_unsigned(self.transport.returns, key, self.shape.coordinate_width)
            B.append(self.transport.returns, "#")
            # Copy the exact C payload cells. No host decoded numeric word is
            # substituted into the production return stream.
            for _ in range(self.shape.payload_width):
                bit = output.tape.read()
                output.tape.step(1)
                B.append(self.transport.returns, "1" if bit else "0")
            B.append(self.transport.returns, "#")
            self.returned_records += 1
        output.tape.clear()
        need(all(t.live_bits == 0 and t.head == 0 for t in self.pool.roles), "consumer roles cleaned between rectangles")
        self.rectangles += 1

    def run(self):
        tape = self.transport.saved
        while tape.read() != "!":
            prefix = read_unsigned(tape, self.shape.prefix_width)
            if prefix != self.prefix:
                self.finish_rectangle()
                self.begin_rectangle(prefix)
            self.accept_record()
        self.finish_rectangle()
        self.prefix = None

    def receipt(self):
        # Observer-only tariff description. Include the full encoded plan,
        # especially arbitrary J when W=0, and monotone history counters.
        record_width = self.shape.saved_key_width + self.shape.payload_width + self.shape.coordinate_width + 2
        metadata = [self.shape.ell, self.shape.spectator_width,
                    self.shape.boundary, self.shape.halo, self.shape.payload_width,
                    self.shape.g, *self.shape.ks]
        for plan in self.archive.plans:
            metadata.extend((plan.period, plan.halfwidth, plan.bits, plan.terms,
                             plan.normalizer_shift, plan.radius,
                             Q(plan.gap).numerator, Q(plan.gap).denominator))
        metadata_bits = sum(abs(value).bit_length() + 2 for value in metadata)
        counter_bits = sum(value.bit_length() + 2 for value in
                           (self.copied_records, self.returned_records, self.rectangles))
        carrier_units = record_width + metadata_bits + counter_bits
        return {
            "saved_records": self.copied_records, "returned_records": self.returned_records,
            "rectangles": self.rectangles, "cropped_records": self.cropped_records,
            "transport_record_width": record_width,
            "encoded_plan_descriptor_bits": metadata_bits,
            "cumulative_counter_bits": counter_bits,
            "control_carrier_units": carrier_units,
            "quadratic_codec_tariff_units": (self.copied_records + self.returned_records + self.rectangles) * carrier_units * carrier_units,
            "tariff_scope": "The complete encoded control block is O(control_carrier_units); an O(1) multiple of reported quadratic units covers sparse geometry/key macros. These are not measured binary transitions. Numeric source/consumer scalar macros remain separately charged.",
        }


def sigmag(n, width):
    need(abs(n) < 1 << (width - 1), "fixture sign-magnitude carrier")
    return str(int(n < 0)) + format(abs(n), f"0{width - 1}b")


def decode_word(word, width):
    need(len(word) == 2 * width, "observer payload width")
    pair = []
    for part in (word[:width], word[width:]):
        magnitude = int(part[1:], 2)
        need(part[0] == "0" or magnitude, "observer negative zero")
        pair.append(-magnitude if part[0] == "1" else magnitude)
    return tuple(pair)


def literal_totals(transport):
    rows = transport.ledger().values()
    return {"finite_alphabet_actions": sum(row.get(k, 0) for row in rows for k in ("read", "write", "move")),
            "retained_finite_alphabet_cells": sum(row["retained_cells"] for row in transport.ledger().values()),
            "roles": len(transport.roles)}


def execute(raw, gap, words, *, saved_halo=4, fault=None):
    """Execute one complete actual-reference transaction; observers come last."""
    plan = M.Plan(64, 4, 28, 2, 1, gap, 1)
    shape = Shape(5, (1,), 0, 5, saved_halo, 2 * plan.data_width)
    source = "".join("".join(sigmag(value, plan.data_width) for value in pair) + "#" for pair in words)
    transport = B.Program(source, "&@0#00000;", "0100000", "0000101", format(saved_halo, "07b"))
    transport.gather()
    transport.sort(transport.saved)
    saved_before = transport.saved.inspect()  # Passive ownership observer.
    transport.core_complement_test_double()
    bill = M.Bill()
    producer = S.make_reference(raw, (61, 3, 2, 1, 8, 32))
    producer.require_narrow_gap()
    table, height = M.prepare_table(plan, lambda r, c: S.source_entry(producer, r, c), producer.description_hash, bill)
    archive = T.pack_tables((table,), bill)
    pool = T.TensorWorkspace.create(bill)
    codec = Codec(transport, shape, archive, pool, bill, fault=fault)
    codec.run()
    need(transport.saved.inspect() == saved_before, "numeric consumer changed original saved copies")
    source_setup = S.source_receipt(producer)
    S.clear_reference(producer)
    archive.tape.readonly = False
    archive.tape.clear()
    transport.merge_returns()
    final = transport.final.inspect().split("#")[:-1]
    targets = {r for r in range(64) if r % 32 < 5 or r % 32 >= 27}
    actual = {r: decode_word(final[r], plan.data_width) for r in targets}
    for row in range(64):
        if row not in targets:
            original = source.split("#")[row]
            need(final[row] == "".join("0" if bit == "1" else "1" for bit in original), "current opaque core interior preserved")
    before_erase = literal_totals(transport)
    transport.erase_work()
    after_erase = literal_totals(transport)
    need(after_erase["retained_finite_alphabet_cells"] >= before_erase["retained_finite_alphabet_cells"], "retained B backing after erase")
    need(all(t.live_bits == 0 and t.head == 0 for t in pool.roles), "all local consumer roles blank")
    c_roles = pool.roles + (archive.tape, table.tape)
    receipt = {
        "codec": codec.receipt(), "transport": after_erase,
        "consumer_binary_actions": bill.reads + bill.writes + bill.moves,
        "consumer_bill": bill.record(),
        "consumer_retained_binary_cells": sum(t.extent for t in c_roles),
        "consumer_data_roles_including_prepared_table": len(c_roles),
        "binary_tape_primitive_upper_bound_before_scalar_macros": 10 * after_erase["finite_alphabet_actions"] + bill.reads + bill.writes + bill.moves,
        "source_setup": source_setup, "source_height": height,
        "final_sha256": sha256(transport.final.inspect().encode()).hexdigest(),
    }
    return actual, plan, receipt


def standalone_consumer(raw, gap, words):
    """Independent delivery oracle, explicitly outside the production codec."""
    plan = M.Plan(64, 4, 28, 2, 1, gap, 1)
    bill = M.Bill()
    source = S.make_reference(raw, (61, 3, 2, 1, 8, 32))
    table, _ = M.prepare_table(plan, lambda r, c: S.source_entry(source, r, c), source.description_hash, bill)
    archive = T.pack_tables((table,), bill)
    pool = T.TensorWorkspace.create(bill)
    answers = {}
    for lower in (0, 27, 32, 59):
        targets = ((lower, 5),)
        layout = T.Layout.make(archive.plans, targets)
        external_values = (words[x % 64] for x in range(layout.lowers[0], layout.lowers[0] + layout.lengths[0]))
        input_tape = T.rectangle_input(layout, external_values, bill, tape=pool.rectangles[0])
        output = T.apply_tensor(archive, targets, input_tape, bill, workspace=pool)
        for _ in range(output.count):
            key, value = T.get_record(output.tape, output.layout)
            canonical = (output.layout.lowers[0] + output.layout.coordinate(key, 0)) % 64
            need(canonical not in answers, "oracle target uniqueness")
            answers[canonical] = value
        output.tape.clear()
    return answers


def main():
    oracle = load("join_independent_source_oracle", PACKAGE / "oracle.py")
    _, raw, matrix, gap, source_receipt = oracle.source_fixture()
    words = oracle.fixture_words(64, 28)
    expected_bits = standalone_consumer(raw, gap, words)
    expected_inverse = oracle.exact_inverse_action(matrix, words, 28, 2)
    actual, plan, receipt = execute(raw, gap, words)
    need(actual == expected_bits, "streamed codec differs bitwise from independent rectangle delivery")
    maximum = max(sum(abs(Q(actual[row][j], 1 << plan.bits) - expected_inverse[row][j]) for j in range(2)) for row in actual)
    bound = plan.numeric_error + plan.tail_error
    need(maximum <= bound, "actual original-reference inverse error")
    controls = []
    for fault in ("offset", "omit_wrap", "drop_saved", "return_key"):
        try:
            execute(raw, gap, words, fault=fault)
        except (ValueError, B.Reject):
            controls.append(fault)
        else:
            raise ValueError("joined control failed to reject: " + fault)
    wrong, _, _ = execute(raw, gap, words, fault="payload_magnitude")
    need(wrong != expected_bits, "wrong saved payload magnitude escaped exact delivery oracle")
    controls.append("payload_magnitude_exact_mismatch")
    receipt.update(source=source_receipt, returned_targets=len(actual),
                   exact_delivery_match=True,
                   maximum_original_inverse_error=[maximum.numerator, maximum.denominator],
                   proved_error_bound=[bound.numerator, bound.denominator],
                   controls=controls,
                   scope="Actual-reference sparse codec/consumer/return; core is destructive test double, source/consumer scalar macros explicitly priced; no new kappa")
    print("PASS_FIRST_FACE_REFERENCE_JOIN")
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
