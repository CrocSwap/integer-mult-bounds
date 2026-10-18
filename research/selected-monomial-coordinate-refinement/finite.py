"""Finite source/model binding, not a replacement for the quantified Lean proofs.

Unchanged PR2250 execution is deliberately tested as the implementation under
review. Independent arithmetic/address oracles do not import its compiler.
AAAmirinu with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import types

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def source_bytes(raw, pin):
    need(digest(raw) == pin["sha256"], "source SHA256: " + pin["path"])
    if "git_blob" in pin:
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(hashlib.sha1(blob).hexdigest() == pin["git_blob"], "source Git blob: " + pin["path"])


def authenticate():
    pins = read(HERE / "SOURCES.json")
    entries = pins["vendored_sources"] + [pins["archive_member"]]
    need(len(entries) == 14 and len({e["path"] for e in entries}) == 14, "exact source inventory")
    for entry in entries:
        source_bytes((HERE / entry["path"]).read_bytes(), entry)
    adapters = read(HERE / "sources/RESIDUAL-ADAPTERS.json")
    recipe = adapters["recipes"]["0:1000"]["right"]
    need(recipe == read(HERE / "RECIPE.json"), "selected recipe extraction")
    need(recipe == {
        "linear_Z4": [1, 3, 2, 3, 2, 2, 0, 2, 2],
        "matrix_rows": [1, 73, 4, 67, 16, 32, 128, 256, 75],
        "offset": 245, "phase": 2,
        "quadratic_rows": [65, 10, 0, 10, 0, 0, 1, 0, 0],
    }, "specified directed recipe")
    return entries, recipe


def load_implementation():
    # All three module bytes are authenticated before executing any source.
    for name in ("streams", "compact", "monomial"):
        path = HERE / "sources/pr2250" / (name + ".py")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules["streams"], sys.modules["compact"], sys.modules["monomial"]


def q(x):
    b = [(x >> i) & 1 for i in range(9)]
    return (b[0] + 3*b[1] + 2*b[2] + 3*b[3] + 2*b[4] + 2*b[5] +
            2*b[7] + 2*b[8] + 2*b[0]*b[6] + 2*b[1]*b[3]) % 4


def affine(x):
    rows = [1, 73, 4, 67, 16, 32, 128, 256, 75]
    out = 245
    for i, row in enumerate(rows):
        parity = 0
        for j in range(9):
            parity ^= ((row >> j) & 1) * ((x >> j) & 1)
        out ^= parity << i
    return out


def rotate(pair, phase):
    a, b = pair
    return ((a, b), (-b, a), (-a, -b), (b, -a))[phase % 4]


def bits(value, width):
    return bytes((value >> i) & 1 for i in range(width))


def unsigned(word):
    return sum(bit << i for i, bit in enumerate(word))


def signed(value, width):
    return value if value < 1 << (width-1) else value - (1 << width)


def guard(pair, phase, width):
    low = -(1 << (width-1))
    a, b = pair
    return (True, b != low, a != low and b != low, a != low)[phase % 4]


def word_run(word, x):
    for kind, target, source in word:
        if kind == "flip" or (x >> source) & 1:
            x ^= 1 << target
    return x


def lean_data_binding(recipe, word):
    text = (HERE / "lean/SelectedRecipe.lean").read_text(encoding="utf-8")
    for field, source in (("matrixRows", "matrix_rows"), ("alpha", "linear_Z4"),
                          ("quadraticRows", "quadratic_rows")):
        match = re.search(r"def " + field + r" : List Nat := (\[[^\]]*\])", text)
        need(match is not None and json.loads(match[1]) == recipe[source], "Lean literal " + field)
    for field, value in (("offset", 245), ("constantPhase", 2)):
        need(re.search(r"def " + field + r" : Nat := " + str(value) + r"\b", text),
             "Lean scalar literal " + field)
    body = text.split("def word : List Gate :=", 1)[1].split("def matrixRows", 1)[0]
    extracted = []
    for match in re.finditer(r"\.(add|flip)\s+(\d+)(?:\s+(\d+))?", body):
        extracted.append((match[1], int(match[2]), int(match[3]) if match[3] else -1))
    need(tuple(extracted) == word, "Lean literal word differs from authenticated Python compiler")
    return {"literal_gate_count": len(word), "matrix_dimension": 9,
            "recipe": "0:1000.right", "python_to_Lean_translation_formally_verified": False}


def phase_cases(streams, compact, mono, recipe):
    modular, exact, outside = 0, 0, 0
    receipts = []
    for width in range(2, 6):
        modulus = 1 << width
        pairs = [(signed(a, width), signed(b, width)) for a in range(modulus) for b in range(modulus)]
        raw = b"".join(bits(a % modulus, width) + bits(b % modulus, width) for a, b in pairs)
        # One address, all signed pairs as consecutive Gaussian coefficients.
        layout = compact.Layout(tuple(("v"+str(i), 0) for i in range(9)), len(raw))
        for phase in range(4):
            fixture = dict(recipe, phase=phase)
            for inverse in (False, True):
                effective = (-phase if inverse else phase) % 4
                out = mono.phase_pass(streams.Tape(streams.Meter(), raw), layout,
                                      fixture, 1, 1, 0, width, inverse)
                expected = bytearray()
                for pair in pairs:
                    answer = rotate(pair, effective)
                    expected.extend(bits(answer[0] % modulus, width))
                    expected.extend(bits(answer[1] % modulus, width))
                    actual = tuple(signed(component % modulus, width) for component in answer)
                    if guard(pair, effective, width):
                        need(actual == answer, "guard must imply exact signed rotation")
                        exact += 1
                    else:
                        need(actual != answer, "failed precise guard must change an integer component")
                        outside += 1
                    modular += 1
                need(out.data == expected, "actual phase_pass modular coefficient result")
                receipts.append(digest(bytes(out.data)))
    return {"modular_pairs": modular, "exact_guard_pairs": exact, "outside_guard_pairs": outside,
            "widths": [2, 3, 4, 5], "all_four_phases_and_both_directions": True,
            "receipt_sha256": digest("\n".join(receipts).encode())}


def physical_fixture(streams, compact, mono, recipe, width=5):
    fields = (("u", 1), ("t", 1)) + tuple(("v"+str(i), 1) for i in range(9)) + (("b", 1),)
    layout = compact.Layout(fields, 4*width)
    raw = bytearray()
    limit = (1 << (width-1))-1
    for index in range(layout.records):
        for k in range(2):
            a = (17*index + index//7 + 3*k) % (2*limit+1)-limit
            b = ((index ^ (index >> 2)) + 5*k) % (2*limit+1)-limit
            raw.extend(bits(a % (1 << width), width) + bits(b % (1 << width), width))
    expected = bytearray(len(raw))
    for index in range(layout.records):
        state = layout.decode(index)
        x = sum(state["v"+str(i)] << i for i in range(9))
        y = affine(x)
        new = dict(state)
        for i in range(9):
            new["v"+str(i)] = (y >> i) & 1
        dst = layout.encode(new)
        for k in range(2):
            start = index*layout.record_bits + 2*k*width
            pair = (signed(unsigned(raw[start:start+width]), width),
                    signed(unsigned(raw[start+width:start+2*width]), width))
            a, b = rotate(pair, 2+q(x))
            at = dst*layout.record_bits + 2*k*width
            expected[at:at+2*width] = bits(a % (1 << width), width)+bits(b % (1 << width), width)
    output = mono.execute_monomial(streams.Tape(streams.Meter(), raw), layout, recipe, 1, 1, 1, 0, width)
    need(output.data == expected, "actual full-array directed monomial differs from oracle")
    output_bytes = bytes(output.data)
    restored = mono.execute_monomial(output, layout, recipe, 1, 1, 1, 0, width, True)
    need(restored.data == raw, "actual inverse does not restore full dirty array")
    return {"columns": 1, "records": layout.records, "gaussian_coefficients_per_record": 2,
            "coefficient_bits": width, "arbitrary_spectator_combinations": 8,
            "output_sha256": digest(output_bytes), "inverse_restored": True}, layout, bytes(raw), output_bytes


def altered_module(source, transform):
    tree = ast.parse(source)
    transform(tree)
    ast.fix_missing_locations(tree)
    module = types.ModuleType("altered_source_control")
    exec(compile(tree, "<in-memory semantic control>", "exec"), module.__dict__)
    return module


def replay():
    entries, recipe = authenticate()
    streams, compact, mono = load_implementation()
    word = mono.binary_word(recipe)
    literal = lean_data_binding(recipe, word)
    for x in range(512):
        need(word_run(word, x) == affine(x) == mono.column_map(recipe, x), "actual affine column")
        need(word_run(tuple(reversed(word)), affine(x)) == x, "actual reversed word")
        need(mono.column_phase(recipe, x) == q(x), "actual strict-upper phase")
    negation_count = 0
    for width in range(2, 9):
        for value in range(1 << width):
            need(unsigned(mono.negate(bits(value, width))) == (-value) % (1 << width),
                 "actual LSB negate")
            negation_count += 1
    phase_receipt = phase_cases(streams, compact, mono, recipe)
    tensor_count = 0
    for f in (1, 2, 3, 7):
        for K, rho in ((1, 0), (3, 2)):
            for x in range(512):
                xs = [(x + j*73) % 512 for j in range(f)]
                state = {"v"+str(i): sum(((a >> i) & 1) << (rho+j*K) for j, a in enumerate(xs))
                         for i in range(9)}
                state.update({"u": 19, "t": 23, "b": 29})
                need(mono.tensor_phase(recipe, state, f, K, rho) ==
                     (2*f+sum(q(a) for a in xs)) % 4, "actual tensor phase staging")
                tensor_count += 1
    cases = []
    for width in (2, 5):
        receipt, layout, raw, output = physical_fixture(streams, compact, mono, recipe, width)
        cases.append(receipt)

    controls = []
    for entry in entries:
        original = (HERE / entry["path"]).read_bytes()
        try:
            source_bytes(bytes([original[0] ^ 1])+original[1:], entry)
        except ValueError as error:
            need(str(error).startswith("source SHA256"), "unexpected byte-control failure")
            controls.append("source-byte/" + entry["path"])
        else:
            raise ValueError("corrupt source accepted")

    source = (HERE / "sources/pr2250/monomial.py").read_text()
    def wrong_carry(tree):
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "phase_pass")
        assignments = [n for n in ast.walk(function) if isinstance(n, ast.Assign) and
                       isinstance(n.value, ast.Constant) and n.value.value == 1 and
                       any(isinstance(t, ast.Name) and t.id == "carry" for t in n.targets)]
        need(len(assignments) == 1, "one source carry initialization")
        assignments[0].value = ast.Constant(0)
    broken = altered_module(source, wrong_carry)
    try:
        phase_cases(streams, compact, broken, recipe)
    except ValueError as error:
        need("actual phase_pass modular coefficient result" in str(error), "carry control attribution")
        controls.append("ones-complement-carry")
    else:
        raise ValueError("wrong carry accepted")

    def wrong_inverse_order(tree):
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "execute_monomial")
        inverse_if = next(n for n in function.body if isinstance(n, ast.If) and
                          isinstance(n.test, ast.Name) and n.test.id == "inverse")
        loop = next(n for n in function.body if isinstance(n, ast.For))
        function.body.remove(inverse_if)
        function.body.insert(function.body.index(loop), inverse_if)
    broken = altered_module(source, wrong_inverse_order)
    restored = broken.execute_monomial(streams.Tape(streams.Meter(), output), layout, recipe, 1, 1, 1, 0, 5, True)
    need(restored.data != raw, "wrong inverse phase location escaped")
    controls.append("inverse-phase-before-recovered-address")

    flip_first = tuple(g for g in word if g[0] == "flip") + tuple(g for g in word if g[0] == "add")
    need(any(word_run(flip_first, x) != affine(x) for x in range(512)), "affine offset order control")
    controls.append("affine-offset-before-linear-word")
    zeros = {"v"+str(i): 0 for i in range(9)}
    need(mono.tensor_phase(recipe, zeros, 2, 1, 0) == 0 and
         mono.tensor_phase(recipe, zeros, 2, 1, 0, True) == 2, "missing repeated phase control")
    controls.append("omitted-f-times-constant")
    low = -16
    constant = dict(recipe, phase=2)
    singleton = compact.Layout(tuple(("v"+str(i), 0) for i in range(9)), 10)
    raw_min = bits(low % 32, 5)+bits(0, 5)
    wrapped = mono.phase_pass(streams.Tape(streams.Meter(), raw_min), singleton, constant, 1, 1, 0, 5)
    need(wrapped.data == raw_min and rotate((low, 0), 2) == (16, 0),
         "most-negative control")
    again = mono.phase_pass(wrapped, singleton, constant, 1, 1, 0, 5, True)
    need(again.data == raw_min, "modular inverse roundtrip should not detect signed overflow")
    controls.append("most-negative-roundtrip-is-not-integer-correctness")
    return {
        "status": "PASS_SELECTED_MONOMIAL_SOURCE_MODEL_BINDING",
        "kernel_checked": False,
        "literal_binding": literal,
        "column_cases": 512, "negation_words": negation_count,
        "phase_pass": phase_receipt, "tensor_phase_cases": tensor_count,
        "physical_full_array_cases": cases, "negative_controls": controls,
        "overflow_boundary": {"bits": 5, "input": [-16, 0], "phase": 2,
                              "decoded_output": [-16, 0], "integer_answer": [16, 0],
                              "byte_roundtrip_passes": True, "source_defect_claimed": False},
        "scope": "Finite execution/binding evidence only. Quantified statements require the separate Lean kernel receipt; completed Compact contract and Python-model correspondence remain explicit.",
    }
