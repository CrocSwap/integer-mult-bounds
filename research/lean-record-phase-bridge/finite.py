"""Independent Gaussian record oracle against the unchanged PR2250 interpreter.

PR2378 already checks packed phase cases and two-field full arrays. These cases
support the new formal composition; their size alone is not novel coverage.
Gareth Davidson with substantial OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import ast
import hashlib
import json
import re
import sys
import types

HERE = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def predecessor():
    pins = json.loads((HERE / "PREDECESSOR.json").read_bytes())
    for name, row in pins["files"].items():
        need(sha((HERE / name).read_bytes()) == row["sha256"], "predecessor bytes: " + name)
    recipe = json.loads((HERE / "sources/pr2378/RECIPE.json").read_bytes())
    adapters = json.loads((HERE / "sources/RESIDUAL-ADAPTERS.json").read_bytes())
    need(canonical(recipe) == canonical(adapters["recipes"]["0:1000"]["right"]), "selected recipe binding")
    return recipe


def target(override=None):
    """Load only authenticated source modules, without leaking shared import names."""
    folder = HERE / "sources/pr2250"
    saved = {name: sys.modules.get(name) for name in ("streams", "compact", "monomial")}
    loaded = {}
    try:
        for name in ("streams", "compact", "monomial"):
            path = folder / (name + ".py")
            module = types.ModuleType(name)
            module.__file__ = str(path)
            sys.modules[name] = module
            source = override if name == "monomial" and override is not None else path.read_text()
            exec(compile(source, str(path), "exec"), module.__dict__)
            loaded[name] = module
    finally:
        for name, module in saved.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module
    return loaded["streams"], loaded["compact"], loaded["monomial"]


def phase(recipe, x):
    linear = sum(recipe["linear_Z4"][i] * ((x >> i) & 1) for i in range(9))
    cross = sum(((x >> i) & 1) * ((x >> j) & 1)
                for i in range(9) for j in range(i + 1, 9)
                if (recipe["quadratic_rows"][i] >> j) & 1)
    return (recipe["phase"] + linear + 2 * cross) % 4


def affine(recipe, x):
    return recipe["offset"] ^ sum(((row & x).bit_count() % 2) << i
                                   for i, row in enumerate(recipe["matrix_rows"]))


def rotate(pair, k):
    # Integer matrix multiplication, independent of bit/carry and emit branches.
    matrix = (((1, 0), (0, 1)), ((0, -1), (1, 0)),
              ((-1, 0), (0, -1)), ((0, 1), (-1, 0)))[k % 4]
    return tuple(sum(c * value for c, value in zip(row, pair)) for row in matrix)


def fits(pair, k, width):
    minimum = -(1 << (width - 1))
    return (k % 4 not in (2, 3) or pair[0] != minimum) and (k % 4 not in (1, 2) or pair[1] != minimum)


def encode(pair, width):
    return bytes((value >> j) & 1 for value in pair for j in range(width))


def decode(raw, width):
    need(len(raw) == 2 * width and all(x in (0, 1) for x in raw), "Gaussian field width")
    out = []
    for start in (0, width):
        unsigned = sum(raw[start + j] << j for j in range(width))
        out.append(unsigned - (1 << width) if raw[start + width - 1] else unsigned)
    return tuple(out)


def literal_binding(recipe, mono):
    text = (HERE / "lean/SelectedRecipe.lean").read_text()
    for key, name in (("matrix_rows", "matrixRows"), ("linear_Z4", "alpha"),
                      ("quadratic_rows", "quadraticRows")):
        match = re.search(r"def " + name + r" : List Nat := (\[[^\]]*\])", text)
        need(match is not None and ast.literal_eval(match[1]) == recipe[key], "Lean literal " + name)
    for key, name in (("offset", "offset"), ("phase", "constantPhase")):
        need(re.search(r"def " + name + r" : Nat := " + str(recipe[key]) + r"\b", text), "Lean scalar " + name)
    body = text.split("def word : List Gate :=", 1)[1].split("def matrixRows", 1)[0]
    gates = [(kind, int(a), int(b) if b else -1) for kind, a, b in
             re.findall(r"\.(add|flip)\s+(\d+)(?:\s+(\d+))?", body)]
    need(tuple(gates) == mono.binary_word(recipe) and len(gates) == 22, "literal directed word")
    for x in range(512):
        need(affine(recipe, x) == mono.column_map(recipe, x), "independent affine map")
        need(phase(recipe, x) == (recipe["phase"] + mono.column_phase(recipe, x)) % 4,
             "independent phase map")
    return sha(canonical(gates).encode())


def phase_census(streams, compact, mono, recipe):
    counts = {"cases": 0, "signed_exact": 0, "outside_headroom": 0}
    digest = hashlib.sha256()
    for width in (3, 6):
        half = 1 << (width - 1)
        pairs = [(a, b) for a in range(-half, half) for b in range(-half, half)]
        raw = b"".join(encode(pair, width) for pair in pairs)
        layout = compact.Layout(tuple(("v" + str(i), 0) for i in range(9)), len(raw))
        for k in range(4):
            for inverse in (False, True):
                effective = (-k if inverse else k) % 4
                source = streams.Tape(streams.Meter(), raw)
                out = mono.phase_pass(source, layout, dict(recipe, phase=k), 1, 1, 0, width, inverse)
                need(not source.data and out.head == 0 and len(out.data) == len(raw), "complete phase traversal")
                for j, pair in enumerate(pairs):
                    got_bytes = bytes(out.data[2 * width * j:2 * width * (j + 1)])
                    answer = rotate(pair, effective)
                    need(got_bytes == encode(answer, width), "modular field rotation")
                    exact = decode(got_bytes, width) == answer
                    need(exact == fits(pair, effective, width), "precise field headroom")
                    counts["cases"] += 1
                    counts["signed_exact"] += exact
                    counts["outside_headroom"] += not exact
                digest.update(out.data)
    return dict(counts, widths=[3, 6], output_sha256=digest.hexdigest())


def full_fixture(streams, compact, mono, recipe, width, fields_per_record):
    fields = (("u", 1), ("t", 1)) + tuple(("v" + str(i), 1) for i in range(9)) + (("b", 1),)
    layout = compact.Layout(fields, 2 * width * fields_per_record)
    half = 1 << (width - 1)
    raw = b"".join(encode(((index * 31 + field * 7 + index // 3) % (2 * half - 1) - half + 1,
                           ((index ^ (index >> 3)) + field * 11) % (2 * half - 1) - half + 1), width)
                   for index in range(layout.records) for field in range(fields_per_record))
    expected = bytearray(len(raw))
    for index in range(layout.records):
        state = layout.decode(index)
        x = sum(state["v" + str(i)] << i for i in range(9))
        y = affine(recipe, x)
        destination = dict(state, **{"v" + str(i): (y >> i) & 1 for i in range(9)})
        to = layout.encode(destination)
        for field in range(fields_per_record):
            start = index * layout.record_bits + 2 * width * field
            pair = decode(raw[start:start + 2 * width], width)
            need(fits(pair, phase(recipe, x), width), "full fixture headroom")
            at = to * layout.record_bits + 2 * width * field
            expected[at:at + 2 * width] = encode(rotate(pair, phase(recipe, x)), width)
    source = streams.Tape(streams.Meter(), raw)
    out = mono.execute_monomial(source, layout, recipe, 1, 1, 1, 0, width)
    need(not source.data and bytes(out.data) == expected, "every record field and dirty spectator")
    forward_bytes = bytes(out.data)
    restored = mono.execute_monomial(out, layout, recipe, 1, 1, 1, 0, width, True)
    need(bytes(restored.data) == raw, "whole multi-field inverse")
    result = {"columns": 1, "records": layout.records, "fields_per_record": fields_per_record,
              "coefficient_bits": width, "spectator_combinations": 8,
              "input_sha256": sha(raw), "output_sha256": sha(forward_bytes), "inverse_restored": True}
    return result, layout, raw, forward_bytes


def replay():
    recipe = predecessor()
    streams, compact, mono = target()
    word_digest = literal_binding(recipe, mono)
    census = phase_census(streams, compact, mono, recipe)
    full = []
    for width, fields in ((3, 1), (5, 3), (7, 5)):
        row, layout, raw, forward = full_fixture(streams, compact, mono, recipe, width, fields)
        full.append(row)

    controls = []
    width = 3
    singleton = compact.Layout(tuple(("v" + str(i), 0) for i in range(9)), 18)
    packed = b"".join(encode(pair, width) for pair in ((1, 0), (2, 1), (0, 1)))
    constant = dict(recipe, phase=1)
    original = (HERE / "sources/pr2250/monomial.py").read_text()
    changed = original.replace("for _ in range(layout.record_bits//(2*coefficient_bits)):",
                               "for payload_index in range(layout.record_bits//(2*coefficient_bits)):")
    changed = changed.replace("if phase==0:emit(real,False);emit(imag,False)",
                              "if phase==0 or payload_index>0:emit(real,False);emit(imag,False)")
    need(changed != original and changed.count("payload_index") == 2, "skip-field mutation site")
    _, _, broken = target(changed)
    out = broken.phase_pass(streams.Tape(streams.Meter(), packed), singleton, constant, 1, 1, 0, width)
    answer = b"".join(encode(rotate(decode(packed[j:j + 6], 3), 1), 3) for j in range(0, 18, 6))
    need(len(out.data) == len(answer) and out.data[:6] == answer[:6] and bytes(out.data) != answer,
         "first-field-only shortcut should fail full record")
    controls.append("all bytes consumed but only first field phased")
    bad = b"".join(encode(pair, 3) for pair in ((1, 0), (-4, 0), (0, 1)))
    out = mono.phase_pass(streams.Tape(streams.Meter(), bad), singleton, dict(recipe, phase=2), 1, 1, 0, 3)
    need(decode(out.data[:6], 3) == (-1, 0) and decode(out.data[6:12], 3) != (4, 0),
         "headroom on first field is insufficient")
    restored = mono.phase_pass(out, singleton, dict(recipe, phase=2), 1, 1, 0, 3, True)
    need(bytes(restored.data) == bad, "modular roundtrip control")
    controls.append("later-field overflow survives byte roundtrip")
    positive = mono.phase_pass(streams.Tape(streams.Meter(), packed), singleton, recipe, 2, 1, 0, 3)
    need(bytes(positive.data) == packed, "two-column repeated constant positive control")
    out = mono.phase_pass(streams.Tape(streams.Meter(), packed), singleton, recipe, 2, 1, 0, 3,
                          omit_tensor_constant=True)
    need(bytes(out.data) != packed, "one constant instead of repeated tensor phase")
    controls.append("omitted repeated phase changes whole record")
    for record_bits, data, message in ((17, packed, "Gaussian record extent"),
                                       (18, packed[:-1], "sequential read boundary")):
        try:
            mono.phase_pass(streams.Tape(streams.Meter(), data), compact.Layout(singleton.fields, record_bits),
                            constant, 1, 1, 0, 3)
        except ValueError as error:
            need(str(error) == message, "wrong record-extent failure")
        else:
            raise ValueError("malformed record accepted")
        controls.append(message)
    # Incorrect composition of the unchanged operations: inverse phase too early.
    wrong = mono.phase_pass(streams.Tape(streams.Meter(), forward), layout, recipe, 1, 1, 0, 7, True)
    neutral = dict(recipe, phase=0, linear_Z4=[0] * 9, quadratic_rows=[0] * 9)
    wrong = mono.execute_monomial(wrong, layout, neutral, 1, 1, 1, 0, 7, True)
    need(bytes(wrong.data) != raw, "wrong inverse phase position")
    controls.append("inverse phase at output instead of recovered address")
    return {"status": "PASS_RECORD_PHASE_SOURCE_BINDING_ONLY", "kernel_checked": False,
            "literal_word_sha256": word_digest, "phase_census": census,
            "complete_record_fixtures": full, "controls": controls,
            "new_coverage": "Formal all-field composition; finite packed cases in PR2378 are credited.",
            "physical_primitives_formalized": False, "new_kappa_claim": False}


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
