"""Exact symbolic translation checks and a separate dense all-column oracle."""
from collections import Counter
from fractions import Fraction as F
from itertools import product as cartesian
from pathlib import Path
import hashlib
import importlib.util
import json
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "inputs"))
from translate import Emitter, Monomial, require
import schedule
import product


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


target = module("target_word", HERE / "inputs/target-finite_c_word.py")
ZERO, ONE = (F(0), F(0)), (F(1), F(0))


def plus(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]


def phase(a, exponent):
    r, i = a
    return ((r, i), (-i, r), (-r, -i), (i, -r))[exponent % 4]


def validate(word):
    ordinary = tuple(row for row in word["ops"] if row[0] != "scale")
    require(target.Word(word["dimension"], word["productive"], word["owned"], ordinary).valid_syntax(), "target grammar")
    for op, *args in word["ops"]:
        if op == "scale":
            require(len(args) == 4 and all(type(x) is int for x in args)
                    and 0 <= args[0] < word["productive"] + word["owned"] and args[-1] > 0,
                    "fixed Gaussian-rational SCALE syntax")
    if "paid" in word:
        require(sum(op[0] == "paid" for op in word["ops"]) == word["paid"], "actual emitted paid-site ledger")


def symbolic(word):
    """Use #7834's exact matrix keys, retaining absolute phase and exterior Q(i)."""
    validate(word)
    eye = target.Matrix.identity(word["dimension"])
    rows = [{(i, eye): ONE} for i in range(word["productive"])] + [{} for _ in range(word["owned"])]
    for op, row, *args in word["ops"]:
        old = rows[row]
        if op in ("add", "sub"):
            new = dict(old)
            for key, value in rows[args[0]].items():
                z = value if op == "add" else phase(value, 2)
                new[key] = plus(new.get(key, ZERO), z)
        elif op == "clear":
            new = {}
        elif op in ("scale", "half", "neg", "i"):
            scalar = (F(args[0], args[2]), F(args[1], args[2])) if op == "scale" else {
                "half": (F(1, 2), F(0)), "neg": (F(-1), F(0)), "i": (F(0), F(1))}[op]
            new = {key: times(value, scalar) for key, value in old.items()}
        else:
            new = {}
            for (owner, matrix), value in old.items():
                key = owner, matrix.left(op, args)
                new[key] = plus(new.get(key, ZERO), value)
        rows[row] = {key: value for key, value in new.items() if value != ZERO}
    desired = eye
    for axis in range(word["dimension"]):
        desired = desired.left("paid", (axis,))
    public = all(rows[i] == {(i, desired): ONE} for i in range(word["productive"]))
    private = all(not row for row in rows[word["productive"]:])
    return public, private


def c_axis(values, axis):
    result = [ZERO] * len(values)
    diagonal, off = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    for j, value in enumerate(values):
        result[j] = plus(times(diagonal, value), times(off, values[j ^ (1 << axis)]))
    return result


def dense(word, f, public):
    """Independent payload implementation; no Matrix.left or symbolic decoder."""
    size = 1 << (word["dimension"] * f)
    require(len(public) == word["productive"] and all(len(x) == size for x in public), "complete fields")
    rows = [list(x) for x in public] + [[ZERO] * size for _ in range(word["owned"])]
    for op, reg, *args in word["ops"]:
        current = rows[reg]
        if op in ("add", "sub"):
            other = rows[args[0]]
            rows[reg] = [plus(a, b if op == "add" else phase(b, 2)) for a, b in zip(current, other)]
        elif op == "clear":
            rows[reg] = [ZERO] * size
        elif op == "scale":
            scalar = F(args[0], args[2]), F(args[1], args[2])
            rows[reg] = [times(z, scalar) for z in current]
        elif op in ("half", "neg", "i", "unit"):
            rows[reg] = [(z[0] / 2, z[1] / 2) if op == "half" else
                         phase(z, 2 if op == "neg" else 1 if op == "i" else f) for z in current]
        elif op == "paid":
            for j in range(f):
                current = c_axis(current, args[0] * f + j)
            rows[reg] = current
        else:
            updated = [ZERO] * size
            for address, z in enumerate(current):
                out, exponent = address, 0
                for j in range(f):
                    a = args[0] * f + j
                    if op == "x":
                        out ^= 1 << a
                    elif op == "s":
                        exponent += address >> a & 1
                    else:
                        b = args[1] * f + j
                        if op == "cx":
                            out ^= ((address >> a) & 1) << b
                        elif op == "cz":
                            exponent += 2 * ((address >> a) & 1) * ((address >> b) & 1)
                        else:
                            raise ValueError("unknown oracle opcode")
                updated[out] = phase(z, exponent)
            rows[reg] = updated
    return rows


def invert_gates(ops):
    result = []
    for row in reversed(ops):
        result.extend([row] * (3 if row[0] in ("s", "unit") else 1))
    return result


def monomial_oracle(mono, columns, outer, address):
    stride = columns * outer
    result, exponent = 0, mono.constant * stride
    for j in range(stride):
        x = sum(((address >> (i * stride + j)) & 1) << i for i in range(len(mono.rows)))
        y = mono.offset
        for i, row in enumerate(mono.rows):
            y ^= ((row & x).bit_count() & 1) << i
        result |= sum(((y >> i) & 1) << (i * stride + j) for i in range(len(mono.rows)))
        exponent += sum(a * ((x >> i) & 1) for i, a in enumerate(mono.linear))
        exponent += 2 * sum(((x >> a) & 1) * ((x >> b) & 1) for a, b in mono.quadratic)
    return result, exponent % 4


def gate_basis(ops, outer, address):
    exponent = 0
    for op, _, *args in ops:
        if op == "unit":
            exponent += outer
            continue
        for j in range(outer):
            a = args[0] * outer + j
            if op == "s":
                exponent += address >> a & 1
            elif op == "x":
                address ^= 1 << a
            elif op == "cx":
                address ^= ((address >> a) & 1) << (args[1] * outer + j)
            elif op == "cz":
                exponent += 2 * ((address >> a) & 1) * ((address >> (args[1] * outer + j)) & 1)
    return address, exponent % 4


def monomial_checks():
    packets = basis = 0
    for n in (1, 2, 3):
        for rows in cartesian(range(1 << n), repeat=n):
            mono = Monomial(rows, (1 << n) - 1, 3,
                            tuple((i + sum(rows)) % 4 for i in range(n)),
                            tuple((a, b) for a in range(n) for b in range(a + 1, n) if (a + b + sum(rows)) % 2))
            try:
                mono.gates()
            except ValueError:
                continue
            for columns, outer in ((1, 1), (1, 2), (2, 1), (2, 2)):
                emitter = Emitter(max(2, n * columns), 2)
                emitter.monomial(0, mono, columns)
                # Every basis address: integer phase/address oracle only.
                for x in range(1 << (n * columns * outer)):
                    require(gate_basis(emitter.ops, outer, x) == monomial_oracle(mono, columns, outer, x),
                            "all-coordinate monomial lowering including absolute phase")
                    basis += 1
                packets += 1
    return {"packets": packets, "basis_phase_checks": basis, "dimensions": [1, 2, 3],
            "source_multiplicities": [1, 2], "external_lifts": [1, 2], "all_invertible_binary_matrices": True}


def toy_source():
    right = Monomial((3, 2), 1, 3, (1, 2), ((0, 1),))
    left = Monomial((1, 3), 2, 1, (3, 1), ())

    def emit(m, owner, mono, columns, inverse=False):
        start = len(m.ops)
        m.monomial(owner, mono, columns)
        if inverse:
            m.ops[start:] = invert_gates(m.ops[start:])

    def run(m, owners, columns):
        temp = m.zero()
        m.copy(temp, owners[0])
        m.scale(temp, F(2, 3), F(-1, 5))
        m.accumulate(owners[1], temp, F(3, 7), F(2, 11))
        m.accumulate(owners[1], temp, F(-3, 7), F(-2, 11))
        m.retire_zero(temp)
        for owner, rank in zip(owners, (1, 2)):
            # Normalized endpoint of the independently two-sided raw L C R.
            emit(m, owner, right, columns, True)
            emit(m, owner, right, columns)
            yield owner, tuple(reversed(range(rank * columns)))
            emit(m, owner, left, columns)
            emit(m, owner, left, columns, True)

    return product.Native(2, (1, 2), (1, 2), run)


def compiler_checks():
    raw = toy_source()
    word, native = product.specialize(raw, {1: 1, 2: 1}, 1)
    require((word.ambient, word.grade, word.roles, word.paid) == (4, 2, 2, (1,) * 9), "actual product and positive split order")
    m = Emitter(4, word.root_width(4))
    m.native = lambda owners, columns: native(m, owners, columns)
    schedule.expand(word, 4, list(range(m.productive)), m)
    compiled = m.finish()
    require(compiled["paid"] == m.productive * word.leaves_per_array(4) == 18, "exact source recurrence and no paid inflation")
    require(symbolic(compiled) == (True, True), "complete all-column public and private endpoints")
    runs = []
    for f in (1, 2):
        size = 1 << (4 * f)
        public = [[(F((j * 7 + row * 3) % 13 - 6), F((j * 11 + row) % 17 - 8))
                   for j in range(size)] for row in range(m.productive)]
        actual = dense(compiled, f, public)
        for row in range(m.productive):
            desired = public[row]
            for axis in range(4 * f):
                desired = c_axis(desired, axis)
            require(actual[row] == desired, "independent full-field tensor oracle")
        require(all(not any(z != ZERO for z in row) for row in actual[m.productive:]), "every private endpoint cleared")
        runs.append({"f": f, "values_per_productive_field": size})
    return compiled, {"source_ambient": 2, "product_power": 2, "compiled_dimension": 4,
                      "productive": m.productive, "owned": compiled["owned"], "instructions": len(compiled["ops"]),
                      "paid": compiled["paid"], "whole_job_moves": len(m.moves), "dense_runs": runs,
                      "all_column_symbolic_endpoint": True}


def source_macro_checks():
    packets = 0
    for sign in (-1, 1):
        for columns, f in ((1, 1), (1, 2), (1, 3), (2, 1), (2, 2)):
            m = Emitter(3 * columns, 2)
            m.global_lambda(0, 7, 3, columns, sign)
            word = m.finish()
            size = 1 << (3 * columns * f)
            public = [[(F((j * 11) % 19 - 9), F((j * 17) % 23 - 11)) for j in range(size)], [ZERO] * size]
            a, b = (F(1, 2), F(sign, 2)), (F(1, 2), F(-sign, 2))
            mask = size - 1  # Direction 111 on every source/external column.
            desired = [plus(times(a, z), times(b, public[0][j ^ mask])) for j, z in enumerate(public[0])]
            actual = dense(word, f, public)
            require(actual[0] == desired and word["paid"] == 0, "actual global LAMBDA coefficients stay exterior")
            require(all(z == ZERO for row in actual[2:] for z in row), "global LAMBDA scratch cleared")
            # Mutant: apply the unary normalizer independently on every column.
            tensorized = public[0]
            for j in range(columns * f):
                local = sum(1 << (i * columns * f + j) for i in range(3))
                tensorized = [plus(times(a, z), times(b, tensorized[k ^ local])) for k, z in enumerate(tensorized)]
            require((tensorized == desired) == (columns * f == 1), "global normalizer is not tensor-powered")
            packets += 1
    for alias in (False, True):
        m = Emitter(2, 2)
        m.swap(0, 0 if alias else 1)
        word = m.finish()
        public = [[(F(j + 3), F(2 * j - 1)) for j in range(16)],
                  [(F(5 - j), F(j * 3)) for j in range(16)]]
        actual = dense(word, 2, public)
        require(actual[:2] == (public if alias else list(reversed(public))) and word["paid"] == 0,
                "complete row SWAP preserves both owners and does not pay C")
        require(all(z == ZERO for row in actual[2:] for z in row), "row SWAP scratch cleared")
    caller = json.loads((HERE / "inputs/selected-caller.json").read_text())
    counts = Counter("NATIVE" if e[0] == "J" else e[1] for e in caller["events"])
    require(counts == {"ADD": 2108, "SWAP": 455, "LAMBDA": 226, "SCALE": 180,
                       "IDLE_ONE": 100, "QUERY": 8, "NATIVE": 18}, "complete compact selected caller opcode census")
    return {"global_lambda_packets": packets, "row_swap_packets": 2,
            "compact_caller_opcode_census": dict(counts), "global_lambda_tensor_power_mutation_rejected": True}


def controls(compiled):
    result = []
    # Scalar i and unit agree at f=1; they disagree at f=2.
    scalar = {"dimension": 2, "productive": 2, "owned": 0, "ops": (("i", 0),)}
    column = {**scalar, "ops": (("unit", 0),)}
    for f in (1, 2):
        public = [[ONE] * (1 << (2 * f)), [ZERO] * (1 << (2 * f))]
        same = dense(scalar, f, public) == dense(column, f, public)
        require(same == (f == 1), "phase control must fail beyond one column")
    result.append("scalar_i_is_not_columnwise_unit")
    mono = Monomial((1, 2), 0, 1, (0, 0), ())
    m = Emitter(4, 2); m.monomial(0, mono, 2)
    require(gate_basis(m.ops[:1], 1, 0) != monomial_oracle(mono, 2, 1, 0), "source multiplicity phase cannot be lost")
    result.append("source_multiplicity_absolute_phase")
    # C^-1 = (-i) Z C Z = X C. The two-sided factors are not an
    # inverse pair; their missing absolute phase is observable on every field.
    correct = (("s", 0, 0), ("s", 0, 0), ("paid", 0, 0),
               ("s", 0, 0), ("s", 0, 0), ("unit", 0), ("unit", 0), ("unit", 0))
    for f in (1, 2):
        size = 1 << (2 * f)
        public = [[(F(j + 1), F(2 - j)) for j in range(size)], [ZERO] * size]
        expected = public[0]
        for _ in range(3):
            for j in range(f):
                expected = c_axis(expected, j)
        sample = {"dimension": 2, "productive": 2, "owned": 0, "ops": correct}
        require(dense(sample, f, public)[0] == expected, "signed positive-child normal form")
        require(dense({**sample, "ops": correct[:-3]}, f, public)[0] != expected,
                "replacing two-sided factors by inverse pair loses phase")
        require(dense({**sample, "ops": (("x", 0, 0), ("paid", 0, 0))}, f, public)[0] == expected,
                "inverse C has one positive paid C and an ordinary X")
    result.append("independent_two_sided_factors_and_signed_C")
    # Restore the complete permutation, including every unmatched coordinate.
    placement = Emitter(4, 2)
    order = (2, 0, 1, 3)
    placement.move(0, order, False)
    placement.leaf(0, 0)
    prefix = tuple(placement.ops)
    placement.move(0, order, True)
    sample = placement.finish()
    for f in (1, 2):
        size = 1 << (4 * f)
        public = [[(F((j * 5) % 19), F((j * 7) % 23)) for j in range(size)], [ZERO] * size]
        desired = public[0]
        for j in range(f):
            desired = c_axis(desired, 2 * f + j)
        require(dense(sample, f, public)[0] == desired, "whole-job spectators restored")
        require(dense({**sample, "ops": prefix}, f, public)[0] != desired, "missing inverse placement")
    result.append("whole_job_placement_restores_spectators")
    alias = Emitter(2, 2)
    alias.accumulate(0, 0, F(2, 3), F(1, 5))
    sample = alias.finish()
    for f in (1, 2):
        public = [[ONE] * (1 << (2 * f)), [ZERO] * (1 << (2 * f))]
        require(dense(sample, f, public)[0] == [(F(5, 3), F(1, 5))] * len(public[0]),
                "alias-safe exterior scalar unchanged at every lift")
    result.append("exterior_scalar_and_alias_safe_staging")
    # A missing private paid request may leave public semantics unchanged.
    removable = next(i for i, op in enumerate(compiled["ops"]) if op[0] == "paid" and op[1] >= compiled["productive"])
    mutant = {**compiled, "ops": compiled["ops"][:removable] + compiled["ops"][removable + 1:]}
    require(sum(op[0] == "paid" for op in mutant["ops"]) != compiled["paid"], "paid ledger catches zero-owner deletion")
    result.append("paid_request_on_private_zero_not_dropped")
    # Original #7834 admission checks only productive endpoints.
    direct = tuple(("paid", owner, axis) for owner in range(2) for axis in range(2)) + (("add", 2, 0),)
    dirty = {"dimension": 2, "productive": 2, "owned": 1, "ops": direct}
    require(target.Word(2, 2, 1, direct).all_columns() and symbolic(dirty) == (True, False), "private endpoint extension is necessary")
    require(symbolic({**dirty, "ops": direct + (("clear", 2),)}) == (True, True), "charged final CLEAR repairs private endpoint")
    result.append("productive_only_admission_does_not_prove_private_zero")
    # Distinct owners remain necessary even for equal-valued fields.
    try:
        schedule.expand(schedule.Word(2, 2, 2, (1,)), 2, [0, 0], Emitter(2, 2))
    except ValueError:
        result.append("alias_productive_owners")
    else:
        raise ValueError("owner alias escaped source guard")
    bad = {**dirty, "ops": (("scale", 0, 1, 0, 0),)}
    try:
        validate(bad)
    except ValueError:
        result.append("zero_scalar_denominator")
    else:
        raise ValueError("bad SCALE escaped")
    return result


def pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if "local_input" in row]
    declared = json.loads((HERE / "VERIFY.json").read_text())["inputs"]
    require(sorted(row["local_input"] for row in rows) == sorted(declared), "all inputs declared for invalidation")
    root = HERE.parents[1]
    for row in rows:
        data = (root / row["local_input"]).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == row["git_blob"] and hashlib.sha256(data).hexdigest() == row["sha256"], "retained source-byte authentication")
    return len(rows)


def main():
    authenticated = pins()
    compiled, compiler = compiler_checks()
    selected = json.loads((HERE / "inputs/compiler-RESULT.json").read_text())["selected_complex"]
    saving = F(selected["uniform_saving"])
    require(saving > F(1, 500) and selected["source_ambient"] == 153
            and selected["source_target_count"] == 23392 and selected["source_paid_count"] == 117612,
            "exact selected source and target funding comparison")
    result = {"status": "PASS_COMPLEX_COMPILER_C_WORD_ADMISSION", "authenticated_inputs": authenticated,
              "monomials": monomial_checks(), "compiler": compiler, "controls": controls(compiled),
              "actual_source_macros": source_macro_checks(),
              "selected_uniform_saving": str(saving), "target_required_saving": "1/500",
              "strict_funding_gap": str(saving - F(1, 500)),
              "scope": "Conditional finite grammar translation; selected astronomical word and physical runtime not materialized."}
    if "--record" not in sys.argv:
        require(result == json.loads((HERE / "RESULT.json").read_text()), "complete deterministic receipt")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
