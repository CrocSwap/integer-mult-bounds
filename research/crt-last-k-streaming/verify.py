"""Source-bound finite audit of the conditional last-K sequential lowering.

The ordinary width-one exchange and the cost-bounded control evaluator are
explicit hypotheses, not supplied implementations. Tape is a cell/head model;
the proof, rather than Python timings, gives the quantified machine bound.
"""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import types


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


class Tape:
    """A finite simulation of one sequential tape with one movable head."""

    def __init__(self, cells=()):
        self.cells = list(cells)
        self.head = self.steps = self.maximum = 0

    def read(self, erase=False):
        need(self.head < len(self.cells), "read beyond tape contents")
        value = self.cells[self.head]
        need(value in (0, 1), "reading an erased cell")
        self.steps += 2  # Read, then move one cell to the right.
        if erase:
            self.cells[self.head] = None
            self.steps += 1
        self.head += 1
        self.maximum = max(self.maximum, self.head)
        return value

    def write(self, value):
        need(value in (0, 1), "nonbinary payload")
        if self.head == len(self.cells):
            self.cells.append(value)
        else:
            need(self.cells[self.head] is None, "overwriting a live staged bit")
            self.cells[self.head] = value
        self.steps += 2  # Write, then move one cell to the right.
        self.head += 1
        self.maximum = max(self.maximum, self.head)

    def rewind(self):
        # This macro expands into precisely head one-cell left moves.
        self.steps += self.head
        self.head = 0


def stream_slices(bits, length, suffix, record_bits, prepare):
    """Lower a|b|r -> a|(b XOR prepare(a))|r using four payload tapes.

    prepare is called ONCE for each complete pair of suffix slices. It is
    deliberately not assigned a unit-cost-machine implementation here.
    """
    need(isinstance(length, int) and length >= 1, "positive address length")
    need(isinstance(suffix, int) and 0 <= suffix < length, "proper suffix")
    need(isinstance(record_bits, int) and record_bits >= 1, "positive record width")
    need(len(bits) == (1 << length) * record_bits, "complete rectangle required")
    incoming, outgoing, zero, one = Tape(bits), Tape(), Tape(), Tape()
    width = (1 << suffix) * record_bits
    preparations = 0
    for prefix in range(1 << (length - suffix - 1)):
        flip = prepare(prefix)
        need(flip in (0, 1), "Boolean control")
        preparations += 1
        for staged in (zero, one):
            for _ in range(width):
                staged.write(incoming.read())
            staged.rewind()
        for staged in ((one, zero) if flip else (zero, one)):
            for _ in range(width):
                outgoing.write(staged.read(erase=True))
            staged.rewind()
    incoming.rewind()
    outgoing.rewind()
    need(all(cell is None for staged in (zero, one) for cell in staged.cells),
         "staging tapes must be erased and returned")
    need(all(t.head == 0 for t in (incoming, outgoing, zero, one)), "payload head returns")
    volume = len(bits)
    steps = sum(t.steps for t in (incoming, outgoing, zero, one))
    need(steps == 13 * volume, "exact payload-only cell/head invoice")
    return outgoing.cells, {
        "volume_bits": volume,
        "preparations": preparations,
        "payload_cell_head_steps": steps,
        "maximum_staging_bits": zero.maximum + one.maximum,
        "payload_tapes": 4,
    }


def exchange_address(word, length, a, b):
    """MSB physical positions; semantic reference for the assumed callee."""
    different = ((word >> (length - 1 - a)) ^ (word >> (length - 1 - b))) & 1
    return word ^ (different << (length - 1 - a)) ^ (different << (length - 1 - b))


def exchange_payload(records, length, a, b):
    # This direct array reference checks the ordinary callee's ENDPOINT ONLY.
    # Its random accesses are not part of stream_slices or its tape invoice.
    result = [None] * len(records)
    for address, record in enumerate(records):
        result[exchange_address(address, length, a, b)] = record
    return result


def lower_tail(records, length, suffix, record_bits, target, control,
               transform=True, restore=True):
    need(isinstance(record_bits, int) and record_bits >= 1, "positive record width")
    need(all(isinstance(record, int) and 0 <= record < (1 << record_bits)
             for record in records), "payload fits the declared record width")
    need(0 <= target < length - suffix, "target outside omitted suffix")
    last = length - suffix - 1
    placed = exchange_payload(records, length, target, last)
    serialized = [((record >> bit) & 1)
                  for record in placed for bit in range(record_bits - 1, -1, -1)]

    def prepare(prefix):
        # Both the target and suffix are set to zero. Omission makes their
        # choice irrelevant. Reconstruct the pre-exchange control address.
        representative = prefix << (suffix + 1)
        original = exchange_address(representative, length, target, last) if transform else representative
        return control(original)

    output, invoice = stream_slices(serialized, length, suffix, record_bits, prepare)
    placed_output = []
    cursor = iter(output)
    for _ in records:
        record = 0
        for _ in range(record_bits):
            record = 2 * record + next(cursor)
        placed_output.append(record)
    result = exchange_payload(placed_output, length, target, last) if restore else placed_output
    invoice["ordinary_width_one_exchanges"] = 2 if target != last else 0
    return result, invoice


def direct_switch(records, length, target, control):
    result = [None] * len(records)
    mask = 1 << (length - 1 - target)
    for address, record in enumerate(records):
        destination = address ^ (mask if control(address) else 0)
        need(result[destination] is None, "control violates switch independence")
        result[destination] = record
    return result


def all_functions():
    configurations = functions = addresses = 0
    digest = hashlib.sha256()
    max_payload_ratio = 0
    for prefix_bits in range(4):
        for suffix in range(4):
            length = prefix_bits + suffix + 1
            records = list(range(1 << length))
            for target in range(length - suffix):
                dependencies = [v for v in range(length - suffix) if v != target]
                configurations += 1
                for table in range(1 << (1 << prefix_bits)):
                    def control(word):
                        key = 0
                        for position in dependencies:
                            key = 2 * key + ((word >> (length - 1 - position)) & 1)
                        return (table >> key) & 1

                    result, invoice = lower_tail(records, length, suffix, length, target, control)
                    expected = direct_switch(records, length, target, control)
                    need(result == expected, "all Boolean functions/all dirty addresses")
                    recovered, repeated = lower_tail(result, length, suffix, length, target, control)
                    need(recovered == records, "all-function involution")
                    need(invoice == repeated, "payload-independent invoice")
                    need(invoice["preparations"] == 1 << prefix_bits, "one preparation per complete pair")
                    need(invoice["maximum_staging_bits"] == 2 * (1 << suffix) * length,
                         "two reusable complete slices")
                    max_payload_ratio = max(max_payload_ratio,
                                            invoice["payload_cell_head_steps"] // invoice["volume_bits"])
                    digest.update(bytes(result))
                    functions += 1
                    addresses += len(records)
    return {"configurations": configurations, "functions": functions,
            "dirty_address_checks": addresses, "forward_and_inverse_runs": 2 * functions,
            "maximum_payload_step_ratio": max_payload_ratio,
            "endpoint_sha256": digest.hexdigest()}


def caller_fixture(crt):
    """Source-bound root-axis control projection, NOT full placed CRT."""
    # Original axes are physically 3,2,1,0. Logical widths (2,3,3,4).
    # Exchange the unused root-right axis 2, positions [4,7), with the final
    # three bits. This transports controls and can split their source axes.
    # It is suffix-only transport, not the three-reservoir production placement.
    length, suffix, record_bits = 12, 3, 12

    def placement(word):
        for a, b in ((4, 9), (5, 10), (6, 11)):
            word = exchange_address(word, length, a, b)
        return word

    networks = {c: crt.benes(crt.rotation(16, 11, c)) for c in range(11)}
    need({tuple(bit for bit, table in net) for net in networks.values()} == {(0, 1, 2, 3, 2, 1, 0)},
         "actual root-axis common Beneš schedule")

    def values(word):
        return word & 3, (word >> 2) & 7, (word >> 5) & 7, (word >> 8) & 15

    def offset(word):
        a0, a1, _, _ = values(word)
        return (2 * crt.decode_group((a0, a1), (3, 5))) % 11 if a0 < 3 and a1 < 5 else 0

    controls = []
    for layer in range(7):
        def control(placed, layer=layer):
            original = placement(placed)
            return networks[offset(original)][layer][1][values(original)[3]]
        controls.append(control)

    records = exchange_payload(list(range(1 << length)), length, 4, 9)
    records = exchange_payload(records, length, 5, 10)
    records = exchange_payload(records, length, 6, 11)
    invoices = []
    omissions = 0
    for layer, control in enumerate(controls):
        bit = networks[0][layer][0]
        target = 3 - bit
        for address in range(1 << length):
            for position in (target, 9, 10, 11):
                need(control(address) == control(address ^ (1 << (11 - position))),
                     "actual transported CRT control omits target and suffix")
                omissions += 1
        expected = direct_switch(records, length, target, control)
        records, invoice = lower_tail(records, length, suffix, record_bits, target, control)
        need(records == expected, "actual CRT layer streaming endpoint")
        invoices.append(invoice)
    records = exchange_payload(records, length, 6, 11)
    records = exchange_payload(records, length, 5, 10)
    records = exchange_payload(records, length, 4, 9)
    for source in range(1 << length):
        target_value = values(source)[3]
        target_value = ((target_value + offset(source)) % 11 if target_value < 11 else target_value)
        destination = (source & 255) | (target_value << 8)
        need(records[destination] == source, "all padded/dirty root-axis rotation payloads")
    forward_placed = [None] * (1 << length)
    for source, record in enumerate(records):
        forward_placed[placement(source)] = record
    for layer in reversed(range(7)):
        target = 3 - networks[0][layer][0]
        forward_placed, _ = lower_tail(forward_placed, length, suffix, record_bits, target, controls[layer])
    need(all(forward_placed[placement(address)] == address for address in range(1 << length)),
         "full actual CRT inverse with dirty reservoir")
    return {"domain": "source-bound root-axis control projection with suffix-only transport; not full three-reservoir placement or a production tail instance",
            "moduli": [3, 5, 7, 11], "logical_widths": [2, 3, 3, 4],
            "address_bits": length, "suffix_bits": suffix, "root_target_axis": 3,
            "layers": 7, "dirty_addresses": 1 << length,
            "target_and_suffix_omission_checks": omissions,
            "preparations_per_layer": [i["preparations"] for i in invoices],
            "payload_steps_per_layer": [i["payload_cell_head_steps"] for i in invoices],
            "payload_permutation_sha256": hashlib.sha256(
                b"".join(record.to_bytes(2, "big") for record in records)).hexdigest()}


def controls_and_tariff():
    length, suffix, target = 5, 1, 0
    records = list(range(1 << length))
    control = lambda word: (word >> 1) & 1  # Old final-Y bit moves to the old target.
    expected = direct_switch(records, length, target, control)
    stale, _ = lower_tail(records, length, suffix, length, target, control, transform=False)
    unrestored, _ = lower_tail(records, length, suffix, length, target, control, restore=False)
    need(stale != expected, "stale control transform mutant detected")
    need(unrestored != expected, "omitted inverse exchange mutant detected")
    dependent = lambda word: word & 1
    wrong, _ = lower_tail(records, length, suffix, length, target, dependent)
    need(wrong != direct_switch(records, length, target, dependent), "suffix-dependence mutant detected")
    rejected = []
    for label, call in [
        ("incomplete dirty suffix rectangle", lambda: stream_slices([0] * 31, 5, 1, 1, lambda a: 0)),
        ("target inside suffix", lambda: lower_tail(records, 5, 1, 5, 4, control)),
        ("non-Boolean preparation", lambda: stream_slices([0] * 32, 5, 1, 1, lambda a: 2)),
        ("payload exceeds declared width", lambda: lower_tail([0, 2], 1, 0, 1, 0, lambda a: 0)),
    ]:
        try:
            call()
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("negative control accepted: " + label)
    # Exact arithmetic: C=1 coefficient is illustrative. The symbolic bound in
    # PROOF.md retains arbitrary fixed C and does not infer it from examples.
    tariffs = []
    for p, ell in ((2, 2), (63, 7), (1022, 10), (9240576, 24)):
        logarithm = (p + 1).bit_length()  # ceil(log2(p+2))
        g = 64 * (ell + logarithm)
        e = (1 << (4 * ell)) * (p + 2) ** 16
        need(e * (1 << (60 * ell)) * (p + 2) ** 48 <= 1 << g,
             "exact E/2^G inequality, no floating logarithm")
        tariffs.append({"p": p, "ell": ell, "G": g, "H": g,
                        "E_coefficient_one_bits": e.bit_length(),
                        "one_preparation_per_records": 1 << (g + 1)})
    # Re-evaluating per record has M calls instead of M/2^(H+1); endpoint
    # tests alone would miss this exact tariff regression.
    _, invoice = lower_tail(records, length, suffix, length, target, control)
    need(invoice["preparations"] == 8 and len(records) == 32,
         "per-record preparation tariff mutant detected")
    return {"semantic_mutants_detected": ["stale transformed control", "missing inverse exchange",
                                          "control depends on supposedly omitted suffix"],
            "admission_rejections": rejected,
            "tariff_mutants_detected": ["E preparation repeated per record"],
            "exact_integer_tariffs": tariffs}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    pins = json.loads((PACKAGE / "SOURCE-PINS.json").read_text())
    authenticated = {}
    for row in pins:
        data = (ROOT / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256: " + row["path"])
        need(hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest() == row["git_blob"],
             "source Git blob: " + row["path"])
        authenticated[row["path"]] = data
    path = "research/unconditional-batched-crt/check_batched_crt.py"
    module = types.ModuleType("_authenticated_crt_tail_caller")
    module.__file__ = str(ROOT / path)
    sys.modules[module.__name__] = module
    exec(compile(authenticated[path], module.__file__, "exec"), module.__dict__)
    result = {"schema_version": 1, "result": "PASS_CONDITIONAL_CRT_LAST_K_STREAMING",
              "base_commit": "12fa8c5c844be21bfefb38a19503fbd867a11244",
              "source_inputs_checked": len(authenticated), "all_functions": all_functions(),
              "actual_crt_caller": caller_fixture(module), "negative_controls": controls_and_tariff(),
              "limitations": ["Universal cost follows from the conditional written proof, not timing.",
                              "Ordinary width-one callee is a semantic hypothesis, not implemented.",
                              "Control evaluator and its E bound are hypotheses, not certified.",
                              "No full CRT, compact repair, multiplication theorem or new kappa."]}
    output = PACKAGE / "RESULT.json"
    if args.write_result:
        output.write_text(json.dumps(result, indent=2) + "\n")
    else:
        need(json.loads(output.read_text()) == result, "stored result differs from replay")
    print(json.dumps({"result": result["result"],
                      "all_functions": result["all_functions"]["functions"],
                      "dirty_addresses": result["all_functions"]["dirty_address_checks"],
                      "actual_caller_dirty_addresses": result["actual_crt_caller"]["dirty_addresses"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
