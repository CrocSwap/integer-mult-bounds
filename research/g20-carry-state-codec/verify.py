"""Exact checks of the new state codec. Produced by Nick Petalas. Apache-2.0."""

import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import codec  # noqa: E402


def check(condition, message):
    if not condition:
        raise ValueError(message)


def authenticated_inputs():
    expected = {
        "PR6503-PROOF.md": "b042a414fdbcac23f3b8f5116b427310fed16f5f25910c6da73a831cc756bfcc",
        "RUNTIME.bin": "db2fac1c7fa27af26179880713c69dcc3e799877011092b5c00ff645022233bb",
        "RUNTIME.json": "2e5b5dd2a7e82df50627d603561284bb775488dda7966bd6278eb3846d34a59f",
    }
    for name, digest in expected.items():
        check(hashlib.sha256((HERE / "inputs" / name).read_bytes()).hexdigest() == digest, name)
    source = HERE.parents[1] / "research/g20-fused-qadic-carries/inputs/source-RESULT.json"
    check(hashlib.sha256(source.read_bytes()).hexdigest() ==
          "44511d9c7da1c88e265f32ba5d77559b92edb6ca1430180231e84727d939d318", "column source")
    descriptors = json.loads((HERE / "inputs/RUNTIME.json").read_text())
    data = (HERE / "inputs/RUNTIME.bin").read_bytes()
    return codec.source_columns(json.loads(source.read_text())), descriptors, data


def reference_step(model, state, row):
    """Unpacked contract; compare using eight separate signed floor recurrences."""
    quotient, comparisons, residue, high, last, phase = state
    bitmap, bit = row & 255, row >> 8
    if phase == 0:
        check(bit == 1, "reference odd radix")
    digit = sum(model.coefficients[i] * ((row >> i) & 1) for i in range(8))
    quotient = model.next_quotient(quotient, digit, bit)
    mask = 0
    for i in range(8):
        old = ((comparisons >> i) & 1) - 1
        updated = (old + ((bitmap >> i) & 1) - bit) // 2
        check(updated in (-1, 0), "comparison closure")
        mask |= (updated + 1) << i
    if phase < 2:
        residue = (residue + (digit << phase)) % model.denominator
        if phase == 1:
            high = bit
        phase += 1
    return quotient, mask, residue, high, bit, phase


def row_stream(q, values):
    check(1 <= q.bit_length() <= codec.MAX_ROWS, "fixture width")
    return tuple(sum(((x >> j) & 1) << i for i, x in enumerate((*values, q)))
                 for j in range(q.bit_length()))


def check_stream(model, rows):
    state = (model.start, 255, 0, 0, 0, 0)
    code = queries = 0
    for position, row in enumerate(rows, 1):
        state = reference_step(model, state, row)
        code, used = codec.step(model, code, row)
        queries += used
        observed, deferred = codec.decoded(model, code)
        check(observed == state, "prefix state equivalence")
        check(queries + deferred == position, "prefix query accounting")
        check(code < 1 << 24, "retained 24-bit bound")
    packet, final_code, used = codec.produce(model, rows)
    q = sum((row >> 8) << j for j, row in enumerate(rows))
    xs = [sum(((row >> i) & 1) << j for j, row in enumerate(rows)) for i in range(8)]
    numerator = sum(a * x for a, x in zip(model.coefficients, xs))
    c = (numerator - model.denominator * ((numerator * pow(model.denominator, -1, q)) % q)) // q if q > 1 else 0
    check(packet == c * (4 // model.denominator) + 16, "new producer modular endpoint")
    check(final_code == code and used == len(rows) + 1, "query and final-state contract")
    return len(rows)


def codec_census():
    states = codec.MAX_STATES
    count = 0
    for quotient in range(states):
        for tail in range(4096):
            comparison, rest = divmod(tail, 16)
            residue, rest = divmod(rest, 4)
            high, last = divmod(rest, 2)
            code = codec.pack_mature(states, quotient, comparison, residue, high, last)
            check(code == 257 + 4096 * quotient + tail, "ordered bijection")
            check(codec.unpack_mature(states, code) ==
                  (quotient, comparison, residue, high, last), "codec inverse")
            count += 1
    check(count + 257 == 9855233, "complete representation domain")
    for m in range(1, states + 1):
        check(codec.capacity(m) <= 1 << 24, "all-model capacity")
    check(codec.capacity(states) > 1 << 23, "full-domain 23-bit obstruction")
    return count


def phase_census(model):
    count = 0
    for first in range(256):
        initial, used = codec.step(model, 0, first | 256)
        check(initial == first + 1 and used == 0, "deferred first row")
        reference = reference_step(model, (model.start, 255, 0, 0, 0, 0), first | 256)
        check(codec.decoded(model, initial) == (reference, 1), "first-row decoding")
        for second in range(512):
            code, used = codec.step(model, initial, second)
            check(codec.decoded(model, code)[0] == reference_step(model, reference, second),
                  "complete two-row transition domain")
            check(used == 2, "two deferred lookups")
            count += 1
    return count


def mature_fixtures(models):
    count = 0
    for model in models:
        for quotient in sorted({0, model.states // 2, model.states - 1}):
            for row in range(512):
                mask = (row * 73 + quotient) & 255
                residue = (row // 17) % model.denominator
                old = (quotient, mask, residue, (row >> 1) & 1, row & 1, 2)
                code = codec.pack_mature(model.states, *old[:5])
                nxt, used = codec.step(model, code, row)
                check(codec.decoded(model, nxt)[0] == reference_step(model, old, row),
                      "mature transition equivalence")
                check(used == 1, "mature lookup count")
                count += 1
    return count


def rejecting_controls(model):
    calls = [
        (codec.capacity, (0,)), (codec.capacity, (2407,)),
        (codec.unpack_mature, (2406, 256)), (codec.unpack_mature, (2406, 9855233)),
        (codec.pack_mature, (2406, 2406, 0, 0, 0, 0)),
        (codec.pack_mature, (2406, 0, 256, 0, 0, 0)),
        (codec.pack_mature, (2406, 0, 0, 4, 0, 0)),
        (codec.pack_mature, (2406, 0, 0, 0, 2, 0)),
        (codec.pack_mature, (2406, 0, 0, 0, 0, -1)),
        (codec.step, (model, 0, 0)), (codec.step, (model, 0, 512)),
        (codec.step, (model, -1, 256)), (codec.step, (model, 0, True)),
        (codec.finish, (model, 0)), (codec.finish, (model, 256)),
        (codec.produce, (model, ())), (codec.produce, (model, (511,))),
    ]
    for function, arguments in calls:
        try:
            function(*arguments)
        except ValueError:
            continue
        raise ValueError("accepted invalid codec/stream contract")
    # The two faulty encoders collide on distinct legal representation states.
    early_last = 1 + 255
    bad_mature_first = 256 + 4096 * 0
    check(early_last == bad_mature_first and early_last < codec.MATURE_BASE,
          "wrong phase-base collision detected")
    bad_second_block = codec.MATURE_BASE + 4095
    check(codec.unpack_mature(model.states, bad_second_block) != (1, 0, 0, 0, 0),
          "wrong stride inverse failure detected")
    return len(calls), 2


def main():
    check(sys.version_info[:2] == (3, 12), "CPython 3.12 replay")
    check(len(sys.argv) == 1, "no verifier arguments")
    columns, descriptors, data = authenticated_inputs()
    models = [codec.bind(c, descriptors, data) for c in columns]
    representatives = {}
    for model in models:
        representatives.setdefault((model.states, model.digits, model.edge_offset), model)
    largest = max(models, key=lambda m: m.states)
    check(len(columns) == 729 and len(representatives) == 23 and largest.states == 2406,
          "frozen input binding, not quotient-minimality replay")
    rows = streams = 0
    for index, model in enumerate(models):
        for width in (1, 2, 3, 8, 31):
            q = (1 << width) - 1
            values = tuple((index * 1103515245 + i * 12345 + width) % q for i in range(8))
            rows += check_stream(model, row_stream(q, values))
            streams += 1
    rows += check_stream(largest, row_stream((1 << 4097) - 1, tuple(range(8))))
    streams += 1
    phases = phase_census(largest)
    mature = mature_fixtures(tuple(representatives.values()))
    controls, mutations = rejecting_controls(largest)
    mature_codes = codec_census()
    hashes = {}
    paths = tuple(HERE.rglob("*"))
    check(len(paths) <= 64, "bounded package inventory")
    for path in sorted(p for p in paths if p.is_file() and "__pycache__" not in p.parts):
        check(path.stat().st_size <= 1024 * 1024, "bounded source file")
        hashes[path.relative_to(HERE).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    print(json.dumps(dict(status="PASS_G20_CARRY_STATE_CODEC", retained_bits=24,
                          representation_codes=mature_codes + 257, mature_codes=mature_codes,
                          source_columns=len(models), models=len(representatives), streams=streams,
                          stream_rows=rows, two_row_cases=phases, mature_cases=mature,
                          rejecting_controls=controls, collision_controls=mutations,
                          source_sha256=hashes,
                          live_input_sha256={"research/g20-fused-qadic-carries/inputs/source-RESULT.json":
                                             "44511d9c7da1c88e265f32ba5d77559b92edb6ca1430180231e84727d939d318"}),
                     sort_keys=True))


if __name__ == "__main__":
    main()
