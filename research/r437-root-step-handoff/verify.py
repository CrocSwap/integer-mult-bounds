#!/usr/bin/env python3
"""Conditional original-root metadata edge; codyw912 / OpenAI Codex, Apache-2.0."""
import argparse
import ast
import copy
from dataclasses import replace
from hashlib import sha256, sha1
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import FunctionType, MethodType, SimpleNamespace

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "b58ad9ef4d4e861b0eaa5dba41742bdc072dca51"
PREP = "research/r437-preparation-composition"
MARKER = "PASS_R437_CONDITIONAL_ROOT_STEP_HANDOFF"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(data):
    return sha256(data).hexdigest()


def reject(label, operation, controls):
    try:
        operation()
    except ValueError:
        controls.append(label)
    else:
        raise ValueError("accepted negative control: " + label)


def authenticated_closure(destination):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    need(manifest["base_commit"] == BASE, "canonical source base")
    env = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1")
    inputs = set(json.loads((HERE / "VERIFY.json").read_bytes())["inputs"])
    mappings = {}
    for row in manifest["files"]:
        name = row["path"]
        path = ROOT / name
        if row["usage"] == "provenance":
            data = subprocess.check_output(["git", "cat-file", "blob", BASE + ":" + name], cwd=ROOT, env=env)
        else:
            need(name in inputs, "declared live input")
            need(not any(p.is_symlink() for p in (path, *path.parents)), "no input symlinks")
            data = path.read_bytes()
        need(digest(data) == row["sha256"], "source SHA256: " + name)
        need(sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest() == row["git_blob"], "source Git blob: " + name)
        if "mapped_path" in row:
            target = row["mapped_path"]
            need(not Path(target).is_absolute() and ".." not in Path(target).parts, "relative closure mapping")
            need(target not in mappings or mappings[target] == data, "overlapping mappings have identical bytes")
            mappings[target] = data
    pins = json.loads((ROOT / PREP / "PREDECESSORS.json").read_bytes())
    raw = (ROOT / PREP / "POOLED-SOURCES.json").read_bytes()
    need(digest(raw) == pins["pooled_manifest_sha256"], "authenticated historical inventory")
    rows = json.loads(raw)
    expected = {r["path"]: r["sha256"] for r in rows}
    need(len(rows) == len(expected) == 154, "exact 154-file archive")
    dirs = {str(p) for name in expected for p in Path(name).parents if str(p) != "."}
    vendor = ROOT / PREP / "vendor"
    need(vendor.is_dir() and not vendor.is_symlink(), "regular historical root")
    files_seen, dirs_seen = set(), set()
    for path in vendor.rglob("*"):
        need(not path.is_symlink(), "no historical links")
        name = path.relative_to(vendor).as_posix()
        if path.is_dir():
            dirs_seen.add(name)
        else:
            need(path.is_file(), "regular historical file")
            files_seen.add(name)
    need(files_seen == set(expected) and dirs_seen == dirs, "exact historical files and directories")
    for name, pin in expected.items():
        need(digest((vendor / name).read_bytes()) == pin, "historical source bytes")
        need(name in mappings and digest(mappings[name]) == pin, "historical mapping preserved")
    need(digest(mappings["certificates/selected-result.json"]) == "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129", "accepted historical runtime selection")
    for name, data in mappings.items():
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return len(mappings)


def word_value(word):
    raw = bytes(word.cells)
    need(raw[0] == 2 and raw[-1] == 3 and all(b in (0, 1) for b in raw[1:-1]), "independent word grammar")
    return sum(bit << i for i, bit in enumerate(raw[1:-1]))


def parse_program(raw, index_bits, residue_bits, code_bits):
    """Independent parser: never calls Program.root/step or constructor helpers."""
    need(raw and raw[0] == 2, "program left boundary")
    position = 1
    spans = {}

    def symbol(expected):
        nonlocal position
        need(position < len(raw) and raw[position] == expected, "program tag/delimiter")
        position += 1

    def integer(bits, name):
        nonlocal position
        start = position
        cells = raw[position:position + bits]
        need(len(cells) == bits and all(b in (0, 1) for b in cells), "program binary field")
        position += bits
        symbol(5)
        spans[name] = (start, bits)
        return sum(b << i for i, b in enumerate(cells))

    symbol(7)
    root = [integer(index_bits, "root_size"), integer(residue_bits, "root_unit"), integer(index_bits, "history")]
    symbol(6)
    steps = []
    while position < len(raw) and raw[position] != 4:
        symbol(8)
        metadata = [integer(code_bits if i == 1 else 16, "step_" + name) for i, name in enumerate(("kind", "code", "rank", "field", "reverse", "half"))]
        parent = integer(index_bits, "parent_width")
        child = integer(index_bits, "child_width")
        symbol(6)
        steps.append(metadata + [parent, child])
    need(all(b == 4 for b in raw[position:]), "no trailing program data")
    need(root[2] == len(steps), "exact serialized history")
    return root, steps, spans


def check_program(raw, Q, code, child=True):
    root, steps, spans = parse_program(raw, 13, 255, Q)
    need(root == [2048, 1, int(child)], "unchanged original root size/unit and chronological history")
    expected = [[0, code, 2, 0, 0, 0, 2048, 64]] if child else []
    need(steps == expected, "exact source-bound GOOD root-to-64 STEP")
    return spans


# A symbolic count has a canonical expression c*A^a*q^b, not a unique integer
# factorization. A is fixed as 28416*|GL64(q)|*q^4096. This is NOT Count's
# binary integer encoding and cannot be used as a production packet count.
def monomial(c=1, a=0, b=0):
    need(type(c) is int and c > 0 and type(a) is int and a >= 0 and type(b) is int and b >= 0, "positive symbolic monomial")
    return (c, a, b)


def product(x, y):
    return monomial(x[0] * y[0], x[1] + y[1], x[2] + y[2])


def count_codec(records):
    class SymbolicCount:
        def __init__(self, value):
            self.value = decode(value.tape) if hasattr(value, "tape") else monomial(*value)
            self.tape = encode(self.value)

        @classmethod
        def literal(cls, n):
            return cls(monomial(n))

        @classmethod
        def product(cls, x, y):
            return cls(product(decode(x.tape), decode(y.tape)))

        def marginal(self):
            return type(self)(self)

        def close(self):
            self.tape.clear()

    def encode(value):
        # Separate symbolic transport grammar: UTF-8 JSON carried as bits.
        data = canonical(["symbolic-count-v1", *value]).encode()
        out = records.Tape()
        for byte in data:
            for i in range(8):
                out.append((byte >> i) & 1)
        out.rewind()
        return out

    def decode(tape):
        bits = bytes(tape.cells)[1:]
        if 4 in bits:
            bits = bits[:bits.index(4)]
        need(len(bits) % 8 == 0 and all(b in (0, 1) for b in bits), "symbolic port bit grammar")
        raw = bytes(sum(bits[j + i] << i for i in range(8)) for j in range(0, len(bits), 8))
        value = json.loads(raw)
        need(value[0] == "symbolic-count-v1" and len(value) == 4, "symbolic port version")
        result = monomial(*value[1:])
        need(raw == canonical(["symbolic-count-v1", *result]).encode(), "canonical symbolic port")
        return result

    return SymbolicCount, encode, decode


def regional_residual(cat, top, binding, source, low):
    """Extract unchanged production nested emitter, not a surrogate event."""
    import macro_code
    from control import LocalState
    call = top.call(0, 0)
    state = LocalState(call)
    role = None
    for position in range(source["position"] + 1):
        opcode, role = state.accept(position)
    need(opcode == 0 and call.requests[source["position"]] == source["identifier"], "literal LocalState MOVE dispatch")
    text = Path(macro_code.__file__).read_bytes()
    tree = ast.parse(text)
    outer, = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "compile_node"]
    nested, = [n for n in outer.body if isinstance(n, ast.FunctionDef) and n.name == "residual"]
    operations = []
    namespace = dict(vars(macro_code), operations=operations, binding=binding, mode=0)
    exec(compile(ast.Module(body=[nested], type_ignores=[]), macro_code.__file__, "exec"), namespace)
    namespace["residual"](("stage", role), source["identifier"], True, low)
    need([r[0] for r in operations] == ["residual_begin", "block", "block", "block", "residual_end"], "actual good residual grammar")
    definition = operations[0][2]
    need(operations[2][1] is definition and operations[2][2] == ("good", 1, 0), "literal emitted GOOD block")
    return definition, operations[2][2], {"module_sha256": digest(text), "function": "compile_node.residual", "lines": [nested.lineno, nested.end_lineno], "stage_role": role, "operation_tags": [r[0] for r in operations]}


def install_ordinal_counts(codes):
    """Sum the literal codec's skipped candidates; preserve its GL ordering."""
    import low_codes

    def prefix(constraints, reduced, stop, total):
        if constraints.inconsistent:
            excluded = 0
        elif reduced[2] is not None:
            excluded = stop * constraints.q ** (len(constraints.rows) - len(constraints.basis) - 1)
        else:
            excluded = int(reduced[1] < stop) * constraints.q ** (len(constraints.rows) - len(constraints.basis))
        return stop * total - excluded

    def rank(self, rows, vector):
        constraints, ordinal = low_codes.Constraints(rows, self.q), 0
        for column, value in enumerate(vector):
            reduced = constraints.next(column)
            ordinal += prefix(constraints, reduced, value, self.q ** (self.dimension - column - 1))
            constraints.choose(reduced, value)
        need(constraints.inconsistent, "independent low row")
        return ordinal

    def unrank(self, rows, ordinal):
        constraints, vector = low_codes.Constraints(rows, self.q), []
        for column in range(self.dimension):
            reduced = constraints.next(column)
            total = self.q ** (self.dimension - column - 1)
            need(0 <= ordinal < prefix(constraints, reduced, self.q, total), "low-row rank range")
            lo, hi = 0, self.q
            while lo < hi:
                mid = (lo + hi) // 2
                if prefix(constraints, reduced, mid + 1, total) <= ordinal:
                    lo = mid + 1
                else:
                    hi = mid
            need(lo < self.q, "low-row rank range")
            ordinal -= prefix(constraints, reduced, lo, total)
            constraints.choose(reduced, lo)
            vector.append(lo)
        need(ordinal == 0 and constraints.inconsistent, "complete independent low row")
        return tuple(vector)

    finite = low_codes.LowCodes(3, 2)
    import itertools
    vectors = list(itertools.product(range(3), repeat=2))
    checks = []
    prefixes = [[]] + [[v] for v in vectors if v != (0, 0)]
    for rows in prefixes:
        for vector in vectors:
            try:
                original = finite.vector_rank(rows, vector)
            except ValueError:
                reject("dependent_row", lambda r=rows, v=vector: rank(finite, r, v), checks)
            else:
                need(rank(finite, rows, vector) == original, "ordinal prefix sum matches exhaustive codec")
                need(unrank(finite, rows, original) == finite.vector_unrank(rows, original) == vector, "ordinal inverse matches exhaustive codec")
        total = 3**2 - 3**len(rows)
        for ordinal in range(total):
            need(unrank(finite, rows, ordinal) == finite.vector_unrank(rows, ordinal), "all finite inverse intervals including plateaus")
        for ordinal in (-1, total):
            reject("invalid_ordinal", lambda r=rows, o=ordinal: unrank(finite, r, o), checks)
    codes.vector_rank = MethodType(rank, codes)
    codes.vector_unrank = MethodType(unrank, codes)
    # Repeated source resolution has the same complete GL ordinal. Cache only
    # exact pure codec results, never source authentication or admission.
    from functools import lru_cache
    codes.rank = lru_cache(maxsize=32)(codes.rank)
    codes.unrank = lru_cache(maxsize=32)(codes.unrank)


def child_worker(closure):
    sys.path.insert(0, str(closure / "research/r437-carrier-integration"))
    import admission
    import compiler
    import numerical
    cat, top = admission.load_certified("D")
    admission.authenticate_certified(cat)
    install_ordinal_counts(cat.codes)
    from catalogue import Specifications
    import oracle
    import macro_binding
    import macro_machine
    import records
    import words
    import numeric
    import layout
    import residual_blocks
    from cardinal_counts import Count

    controls = []
    source = compiler.early_source87(cat, top, 0, 0)
    key = tuple(source["key"])
    need(key[:3] == ("MOVE", 0, 0), "actual stage0 replica0 MOVE")
    preparation = oracle.reduce_rational(cat.template_for(source["identifier"], True).preparation, cat.q)
    low = tuple(map(tuple, oracle.inverse(preparation, cat.q)))
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    need(tuple(map(tuple, oracle.multiply(low, preparation, cat.q))) == identity, "source-derived good common low class")
    specs = Specifications(cat)
    handle = compiler.source_handle(cat, source["identifier"], True, low)

    def source_check(h, table=specs):
        need(h.request_key == key, "expected actual caller request")
        identifier, common, decoded = cat.codes.decode(h.code)
        need(common is True and decoded == low and identifier == source["identifier"], "exact common source and low class")
        spec = compiler.resolve_handle(cat, table, h)
        need(spec.good and spec.template.rank == 2, "source-bound good rank two")
        return spec

    spec = source_check(handle)
    Q = cat.codes.bits
    q = cat.q
    need(q == 2**127 - 1, "named original prime")
    numerical.check_root_domain(2048, 2048, 2, 0, q, 255, 13, Q)
    numerical.check_fallback(q, [2])
    need(Q == (2 * len(cat.requests) * numerical.gl_order(q) - 1).bit_length(), "actual complete source Q")
    need(top.families == numerical.W == 28416 and cat.dimension == 64, "actual fresh-row family and dimension factors")
    need(cat.codes.size == numerical.gl_order(q), "actual GL low-class cardinality")
    need(numerical.STOCK_MULTIPLIER == 9475 * top.families, "retained conservative stock coefficient")
    # Exact symbolic stock; no numerical Count or gigantic payload is claimed.
    D = numerical.depth(2048)
    need(D >= 2 and numerical.depth(64) == 1, "remaining depth distinct from stored history")
    old_rows = monomial(9475**D, D, 0)
    sharp_rows = monomial(9475, D, 0)
    unused = monomial(9475**D, D - 1, 0)
    need(product(unused, monomial(1, 1, 0)) == old_rows and unused[0] % 9475 == 0, "exact parent quotient and local stock")
    need(sharp_rows[0] % old_rows[0] != 0, "sharp theorem is not stronger old root guard")

    other = compiler.early_source87(cat, top, 0, 1)
    wrong_replica = compiler.source_handle(cat, other["identifier"], True, low)
    reject("valid_other_replica", lambda: source_check(replace(wrong_replica, request_key=key)), controls)
    reject("native_instead_of_common", lambda: source_check(compiler.source_handle(cat, source["identifier"], False, low)), controls)
    reject("stale_source_identity", lambda: source_check(replace(handle, identity="0" * 64)), controls)
    reject("foreign_specifications_catalogue", lambda: source_check(handle, Specifications(copy.copy(cat))), controls)

    binding = macro_binding.SelectedBinding(specs)
    definition, block, emitter = regional_residual(cat, top, binding, source, low)
    need(definition.code == handle.code and definition.common and definition.plan.good and definition.plan.rank == 2, "emitted definition binds actual source")
    ia, ra = words.Arena(13, 512), words.Arena(255, 512)
    modulus = ra.literal(q**2)
    ring = words.Ring(modulus)
    program = records.Program(ia, ra, Q)
    program.tape.append(records.ROOT)
    for arena, value in ((ia, 2048), (ra, 1), (ia, 0)):
        word = arena.literal(value)
        records.append_word(program.tape, word)
        arena.free(word)
    program.tape.append(records.RECORD_END)
    program.tape.rewind()
    root_bytes = bytes(program.tape.cells)
    check_program(root_bytes, Q, handle.code, child=False)
    # One canonical member of the directory producer's domain, NOT its output.
    # h=0 has one empty old prefix; 4096 zero high digits each lie in [0,q).
    fields_record = records.Fields.fixture(ia, ra, [(handle.code, [[0] * 64 for _ in range(64)])], Q)
    need(0 < q == (q**2) // q, "zero raw high-field membership")
    size, depth, columns, fields = [ia.literal(n) for n in (2048, 0, 32, 1)]
    page = numeric.Geometry(definition.plan, ia, columns, depth, handle.code, program)
    trace = residual_blocks.events(page, block)
    event = next(trace)

    def event_check(e):
        need(e.kind == "enter" and e.parent_identity is program, "exact parent Program identity")
        need(e.source_code == definition.code == handle.code, "event source identity")
        need((word_value(e.first), word_value(e.second), word_value(e.width), word_value(e.depth)) == (0, 4032, 64, 1), "literal root child geometry/depth")
        need(e.child_kind == "good" and e.field == 0 and not e.reverse and not e.half, "GOOD event metadata")
        need(word_value(e.width) >= 64, "recursive cutoff")

    event_check(event)
    other_program = records.Program(ia, ra, Q)
    from directory import append_tape
    append_tape(program.tape, other_program.tape)
    other_program.tape.rewind()
    reject("equal_bytes_distinct_parent_program", lambda: event_check(replace(event, parent_identity=other_program)), controls)
    for name, value in (("width", 65), ("depth", 2)):
        mutant_word = ia.literal(value)
        reject("event_" + name, lambda n=name, v=mutant_word: event_check(replace(event, **{n: v})), controls)
        ia.free(mutant_word)
    reject("event_source", lambda: event_check(replace(event, source_code=wrong_replica.code)), controls)
    # Use an actual emitted below-cutoff event, not an invented namespace.
    leaf_columns = ia.literal(1)
    leaf_page = numeric.Geometry(definition.plan, ia, leaf_columns, depth, handle.code, program)
    leaf_trace = residual_blocks.events(leaf_page, block)
    leaf_event = next(leaf_trace)
    need(word_value(leaf_event.width) == 2, "literal below-cutoff width")
    reject("below_cutoff_false_recursion", lambda: need(word_value(leaf_event.width) >= 64, "recursive cutoff"), controls)
    leaf_trace.close()
    leaf_page.close()
    ia.free(leaf_columns)

    SymbolicCount, encode, decode = count_codec(records)
    # Execute the ORIGINAL Layout geometry/control with only Count arithmetic
    # replaced by exact symbolic products and q^(w*atom_count).
    def positive(value):
        monomial(*decode(value.tape))

    def atom_power(value, atoms, supplied_ring, supplied_q):
        need(supplied_ring is ring and supplied_q == q, "symbolic geometry original field")
        old = decode(value.tape)
        value.tape.clear()
        value.value = monomial(old[0], old[1], old[2] + 2 * word_value(atoms))
        value.tape = encode(value.value)

    globals_adapter = dict(vars(layout), Count=SymbolicCount, positive=positive, multiply_atom_power=atom_power)
    adapted_init = FunctionType(layout.Layout.__init__.__code__, globals_adapter)
    adapted_extents = FunctionType(layout.Layout.child_extents.__code__, globals_adapter)
    geometry = object.__new__(layout.Layout)
    B, G, S = [SymbolicCount.literal(n) for n in (2, 3, 5)]
    adapted_init(geometry, page, size, ring, q, B, G, S, True)
    geometry.child_extents = lambda first, second, width, *, before: adapted_extents(geometry, first, second, width, before=before)
    machine = object.__new__(macro_machine.Machine)
    machine.indices, machine.arena, machine.binding = ia, ra, binding
    machine.size, machine.depth, machine.program = size, depth, program
    machine.context = SimpleNamespace(ring=ring)
    machine.roles = {name: records.Tape() for name in macro_machine.NAMES}
    machine.handoff = {name: records.Tape() for name in macro_machine.CAPSULE}
    machine.roles["directory"] = fields_record.tape
    machine.roles["unused"] = encode(unused)
    machine.roles["rows"] = encode(old_rows)
    machine.roles["leading"] = encode(product(unused, monomial(2)))
    machine.roles["before"] = B.tape
    machine.roles["prefixes"] = encode(monomial(1, 0, 4096))
    # Empty source is a typed placeholder at a metadata boundary, NOT payload.
    # The capsule's source port is copied literally, but no payload claim follows.
    expected_input = {name: bytes(machine.roles[src].cells) for name, src in (("source", "current"), ("old_directory", "directory"), ("old_count", "prefixes"), ("rows", "unused"))}
    grants = machine.prepare_child(definition, event, geometry, fields)
    child_bytes = bytes(machine.handoff["program"].cells)
    spans = check_program(child_bytes, Q, handle.code)
    need(bytes(program.tape.cells) == root_bytes, "original root Program preserved")
    for name, raw in expected_input.items():
        need(bytes(machine.handoff[name].cells) == raw, "literal capsule port " + name)
    expected_extents = (monomial(2), monomial(3, 0, 7936), monomial(5))
    actual_extents = tuple(decode(machine.handoff[name]) for name in ("before", "gap", "suffix"))

    def check_rows(rows):
        need(product(rows, monomial(1, 1, 0)) == old_rows, "child rows are exact parent/A, not just divisible")

    def check_extents(extents):
        need(extents == expected_extents, "all three ordered complete spectators")
        volume = product(product(extents[0], extents[1]), extents[2])
        need(product(volume, monomial(1, 0, 4 * 64)) == monomial(30, 0, 4 * 2048), "complete parent/child spectator volume")

    check_rows(decode(machine.handoff["rows"]))
    check_extents(actual_extents)
    need(tuple(map(word_value, grants)) == (q**2, 64, 1), "literal unchanged modulus and event grants")
    reject("doubled_child_rows", lambda: check_rows(product(unused, monomial(2))), controls)
    reject("leading_instead_of_unused_B_gt_one", lambda: check_rows(decode(machine.roles["leading"])), controls)
    for label, mutant in (("missing_external_gap", (monomial(2), monomial(1, 0, 7936), monomial(5))), ("doubled_external_gap", (monomial(2), monomial(6, 0, 7936), monomial(5))), ("missing_unselected_atoms", (monomial(2), monomial(3), monomial(5))), ("missing_before", (monomial(1), expected_extents[1], monomial(5))), ("missing_suffix", (monomial(2), expected_extents[1], monomial(1)))):
        reject(label, lambda m=mutant: check_extents(m), controls)
    for label, value in (("root_size", 64), ("root_unit", 2), ("history", 2), ("step_rank", 3), ("step_code", wrong_replica.code), ("parent_width", 64), ("child_width", 2), ("step_field", 1)):
        raw = bytearray(child_bytes)
        start, bits = spans[label]
        raw[start:start + bits] = bytes((value >> i) & 1 for i in range(bits))
        reject("serialized_" + label, lambda r=bytes(raw): check_program(r, Q, handle.code), controls)
    for label, args in (("child_reset_precision", (2048, 64, 1, 1, q, 128, 13, Q)), ("root_index_reset", (2048, 64, 2, 1, q, 255, 8, Q)), ("root_modulus_changed", (2048, 2048, 2, 0, 3, 5, 13, Q))):
        reject(label, lambda a=args: numerical.check_root_domain(*a), controls)
    trace.close()
    geometry.close()
    page.close()
    return {
        "schema": "r437-conditional-original-root-step-v1",
        "base_commit": BASE,
        "runtime_selection": "historical bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129; not current orientation",
        "count_adapter": {"source_sha256": digest(Path(__file__).read_bytes()), "algorithm": "exact excluded-prefix sums and strict-upper-bound binary search; original Constraints and encode/decode/rank/unrank guards", "finite_parity": "q3 dimension2 all independent row prefixes, all candidate rows and all ordinals; dependent rows and invalid endpoints reject", "q127_roundtrip": True},
        "source": {"variant": "D", "request": source["identifier"], "key": list(key), "identity": cat.source_identity, "common": True, "low_sha256": digest(canonical(low).encode()), "preparation_sha256": digest(canonical(preparation).encode()), "code_bits": Q, "code_sha256": digest(handle.code.to_bytes((Q + 7) // 8, "little"))},
        "root": {"e": 2048, "n": 2048, "h": 0, "w": 2, "L": 255, "I": 13, "Q": Q, "q": str(q), "modulus": str(q**2), "unit": 1, "program_sha256": digest(root_bytes)},
        "emitter": emitter,
        "edge": {"rank": 2, "first": 0, "second": 4032, "child_width": 64, "child_history": 1, "program_sha256": digest(child_bytes), "capsule_sha256": {name: digest(bytes(tape.cells)) for name, tape in sorted(machine.handoff.items())}},
        "symbolic": {"grammar": "[c,a,b] means c*A^a*q^b; NOT production binary Count", "A": "28416*product(q^64-q^i,i=0..63)*q^4096", "D": D, "parent_rows": old_rows, "child_rows": unused, "sharp_theorem_rows": sharp_rows, "leading": product(unused, monomial(2)), "spectators": actual_extents, "directory_prefix_count": [1, 0, 4096]},
        "controls": sorted(controls),
        "boundary": {"literal": ["authenticated source preparation", "original nested residual emitter", "Cursor GOOD block", "residual_blocks.events", "root-only Program bytes", "child_program/Callback/children.extend", "independent Program parser", "Machine.prepare_child eight-port copies", "modulus/width/depth word copies"], "adapted": ["regional dispatch instead of complete schedule/GL expansion", "symbolic count port grammar", "Layout count arithmetic only; original geometric control", "one zero-high raw prefix member, not produced full directory", "metadata-only Machine allocation without q^2 scratch pool"], "unexecuted": ["Machine.node/block/call/run", "complete high-field directory", "forward/payload/backward operations", "physical integer row arithmetic", "supplier admission", "cost/kappa claim"]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=Path)
    parser.add_argument("--write", action="store_true", help="explicitly record observed receipt in TASK.json")
    args = parser.parse_args()
    if args.worker is not None:
        print(canonical(child_worker(args.worker)))
        return
    with tempfile.TemporaryDirectory(prefix="r437-root-step-") as directory:
        destination = Path(directory)
        mapped = authenticated_closure(destination)
        # Fresh process: every imported ROOT naturally resolves inside closure.
        # No preexisting bytecode exists there; isolate any other cache namespace.
        command = [sys.executable, "-I", "-B"]
        if sys.flags.optimize:
            command.append("-O")
        command += ["-X", "pycache_prefix=" + str(destination / "cache"), str(Path(__file__).resolve()), "--worker", str(destination)]
        run = subprocess.run(command, cwd=destination, text=True, capture_output=True, timeout=580)
        need(run.returncode == 0, "isolated worker failed:\n" + run.stderr)
        receipt = json.loads(run.stdout)
        receipt["mapped_source_files"] = mapped
        task_path = HERE / "TASK.json"
        task = json.loads(task_path.read_bytes())
        if args.write:
            task["expected_receipt"] = receipt
            task_path.write_text(json.dumps(task, indent=2, sort_keys=True) + "\n")
        else:
            need(task.get("expected_receipt") == receipt, "observed receipt differs or is absent; explicit --write is required once")
        print(canonical(receipt))
        print(MARKER)


if __name__ == "__main__":
    main()
