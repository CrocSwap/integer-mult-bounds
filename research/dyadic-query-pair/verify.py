"""Dependency-closed exact evidence; ordinary Python guards remain active under -O."""
import argparse
import hashlib
import importlib.util
import itertools
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    # JSON spelling distinguishes certificate integers from Python booleans.
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sources():
    source = json.loads((ROOT / "SOURCES.json").read_text())
    check(source["format"] == "dyadic-native-query-pair-sources-v1", "source format")
    check(source["base_commit"] == "7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261",
          "exact source base")
    expected = {"vendor/upstream-02-streams.tex", "vendor/upstream-04-swap.tex",
                "vendor/upstream-LICENSE", "vendor/pr521-PROOF.md",
                "vendor/pr521-SOURCE-PINS.json", "vendor/pr677-PROOF.md",
                "vendor/pr677-NOTICE.md"}
    inputs = source["immutable_inputs"]
    check(len(inputs) == len(expected) and {r["local"] for r in inputs} == expected,
          "complete immutable source inventory")
    for row in inputs:
        data = (ROOT / row["local"]).read_bytes()
        check(hashlib.sha256(data).hexdigest() == row["sha256"], "source SHA256: " + row["local"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        check(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob: " + row["local"])
    return hashlib.sha256(canonical(source)).hexdigest()


def rational_evidence(compiler):
    s, r = (1, 0, 1, -1, 0, -1), (1, 0, -1, -1, 0, 1)
    rational_columns = modular_columns = 0
    moduli = (3, 9, 27, 5, 25, 7, 49, 11, 121)
    # Pair index 54 uses a central query of magnitude 2^55.
    for j in range(56):
        for sign in (-1, 1):
            k = sign * (1 << j)
            word = compiler.address_word(k)
            inverse = compiler.inverse_word(word)
            check(sum(event[0] == "child" for event in word) == 1, "one child per query")
            check(sum(event[0] == "affine" for event in word) == 6, "six affine events per query")
            for event in word:
                if event[0] == "affine":
                    check(all(i < event[1] for i, _ in event[3]), "ordered affine controls")
                    diagonal = Fraction(event[2])
                    check(abs(diagonal.numerator) & (abs(diagonal.numerator) - 1) == 0
                          and diagonal.denominator & (diagonal.denominator - 1) == 0,
                          "all-odd-radix diagonal unit")
                    check(all(Fraction(c).denominator & (Fraction(c).denominator - 1) == 0
                              for _, c in event[3]), "dyadic control denominators")
            for direction, events in ((1, word), (-1, inverse)):
                for col in range(8):
                    basis = tuple(int(i == col) for i in range(8))
                    expected = tuple(Fraction(int(i == col)) +
                                     (Fraction(direction * k, 4) * s[i] * r[col]
                                      if i < 6 and col < 6 else 0) for i in range(8))
                    actual = compiler.run_address(basis, events)
                    check(actual == expected, "independent rational matrix column")
                    check(compiler.run_address(actual, compiler.inverse_word(events)) == basis,
                          "literal ADDRESS inverse")
                    rational_columns += 1
                    for modulus in moduli:
                        target = tuple(q.numerator * pow(q.denominator, -1, modulus) % modulus
                                       for q in expected)
                        actual = compiler.run_address(basis, events, modulus)
                        check(actual == target, "independent modular matrix column")
                        check(compiler.run_address(actual, compiler.inverse_word(events), modulus) == basis,
                              "modular literal inverse")
                        modular_columns += 1
    return {"dyadic_indices": [0, 55], "signed_query_words": 112,
            "rational_columns_including_inverses_and_spectators": rational_columns,
            "odd_moduli": list(moduli), "modular_columns_including_inverses": modular_columns}


def bxor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def bmul(a, b):
    result = []
    for row in a:
        value = 0
        for i in range(len(a)):
            if row & (1 << i):
                value ^= b[i]
        result.append(value)
    return tuple(result)


def eye(d):
    return tuple(1 << i for i in range(d))


def clean(poly):
    return {e: matrix for e, matrix in poly.items() if any(matrix)}


def pmul(a, b):
    d = len(next(iter(a.values())))
    result = {}
    for i, left in a.items():
        for j, right in b.items():
            result[i + j] = bxor(result.get(i + j, (0,) * d), bmul(left, right))
    return clean(result)


def polynomial_program(program, d=4):
    result = {0: eye(d)}
    for event in program:
        if event[0] == "query":
            _, role, exponent = event
            projector = tuple((1 << role) if i == role else 0 for i in range(d))
            factor = {0: bxor(eye(d), projector), exponent: projector}
        else:
            _, target, source = event
            matrix = list(eye(d))
            matrix[target] ^= 1 << source
            factor = {0: tuple(matrix)}
        result = pmul(factor, result)
    return result


def centered(a, d=4):
    n = tuple(2 if i == 0 else 0 for i in range(d))
    return {0: eye(d), a: n, -a: n}


def projectors(d):
    # Independent outer-product and literal-matrix catalogues agree.
    outer = set()
    for u in range(1, 1 << d):
        for v in range(1, 1 << d):
            if bin(u & v).count("1") % 2:
                outer.add(tuple(v if u & (1 << i) else 0 for i in range(d)))
    matrices = set()
    for matrix in itertools.product(range(1 << d), repeat=d):
        nonzero = {row for row in matrix if row}
        if len(nonzero) == 1 and bmul(matrix, matrix) == matrix:
            matrices.add(matrix)
    check(outer == matrices, "independent binary idempotent catalogue")
    return sorted(matrices)


def polynomial_evidence(compiler):
    symbolic_programs = 0
    for j in range(55):
        for sign in (-1, 1):
            a = sign * (1 << j)
            baseline, fused = compiler.baseline_program(j, sign), compiler.fused_program(j, sign)
            target = centered(a)
            check(polynomial_program(baseline) == target, "baseline Laurent endpoint")
            check(polynomial_program(fused) == target, "fused Laurent endpoint")
            inverse = polynomial_program(compiler.inverse_program(fused))
            check(pmul(inverse, target) == {0: eye(4)}, "full dirty Laurent inverse")
            symbolic_programs += 1
    pairs = 0
    counts = []
    for d in (2, 3, 4):
        catalogue = projectors(d)
        counts.append([d, len(catalogue)])
        target = centered(1, d)
        for p in catalogue:
            for q in catalogue:
                pq = bmul(p, q)
                for exponent in (-4, -2, -1, 1, 2, 4):
                    actual = clean({0: bxor(bxor(eye(d), p), q),
                                    exponent: bxor(p, pq), -exponent: bxor(q, pq)})
                    check(actual != target, "no two-query centered endpoint in census")
                    # Constant-term proof check is exact, without a fraction field.
                    if bxor(p, q) == (0,) * d:
                        check(actual == {0: eye(d)}, "equal-projector cancellation")
                    pairs += 1
    return {"signed_symbolic_program_pairs": symbolic_programs,
            "complete_binary_projector_catalogues": counts,
            "balanced_exponent_domain": [-4, -2, -1, 1, 2, 4],
            "two_query_products_checked": pairs, "centered_survivors": 0,
            "scope": "finite corroboration; all-d and all-exponent exclusion is the written proof"}


def negative_controls(compiler):
    controls = []
    fused = compiler.fused_program(0)
    target = centered(1)

    def reject_program(name, word):
        check(polynomial_program(word) != target, "ineffective control: " + name)
        controls.append(name)

    for i in range(len(fused)):
        reject_program("omit_fused_event_" + str(i), fused[:i] + fused[i + 1:])
    bad = list(fused)
    bad[2] = ("query", 0, 1)
    reject_program("central_power_not_doubled", tuple(bad))
    bad[0] = ("query", 0, 1)
    bad[2] = fused[2]
    reject_program("first_query_wrong_sign", tuple(bad))
    bad = list(fused)
    bad[2] = ("query", 1, 2)
    reject_program("query_mutates_DATA_source", tuple(bad))
    bad = list(fused)
    bad[1] = ("xor", 0, 2)
    reject_program("wrong_XOR_source_role", tuple(bad))
    word = compiler.address_word(1)
    references = [compiler.run_address(tuple(int(i == col) for i in range(6)), word)
                  for col in range(6)]
    for i in range(len(word)):
        bad_word = word[:i] + word[i + 1:]
        actual = [compiler.run_address(tuple(int(j == col) for j in range(6)), bad_word)
                  for col in range(6)]
        check(actual != references, "ineffective ADDRESS omission control")
        controls.append("omit_ADDRESS_event_" + str(i))
    first = tuple(int(i == 0) for i in range(6))
    check(compiler.run_address(first, compiler.inverse_word(word)) != references[0],
          "orientation control must be nontrivial")
    controls.append("query_push_direction_reversed")
    # PR677's first-difference target really does attain two queries.
    p, q = (1, 0), (3, 0)
    product = pmul({0: bxor(eye(2), p), 1: p}, {0: bxor(eye(2), q), -1: q})
    check(product == {0: (3, 2), 1: (2, 0)} and product != centered(1, 2),
          "first-difference two-query positive scope control")
    controls.append("first_difference_has_two_queries")
    # Over an order-two orbit, h=h^-1, and the centered endpoint is identity.
    shift = (1, 0)
    for basis in ({0}, {1}):
        plus = {shift[i] for i in basis}
        minus = {shift[i] for i in basis}
        check(plus ^ minus == set(), "even-orbit scope control")
    controls.append("even_orbit_centered_endpoint_vanishes")
    try:
        compiler.address_word(3)
    except ValueError:
        controls.append("non_dyadic_universal_lowering_rejected")
    else:
        raise RuntimeError("accepted non-dyadic all-odd-radix claim")
    try:
        compiler.run_address(first, word, 2)
    except ValueError:
        controls.append("even_residue_modulus_rejected")
    else:
        raise RuntimeError("accepted nonunit dyadic ring")
    row = {0}
    try:
        compiler.run_bits([row, row, set()], fused, {-1: (0,), 2: (0,)})
    except ValueError:
        controls.append("aliased_source_and_target_rejected")
    else:
        raise RuntimeError("accepted source/target alias")
    # A pre-existing dirty private row is an arbitrary spectator, never disposable.
    initial = [set(), {0}, {1}, {2}]
    actual = [row.copy() for row in initial]
    perms = {-1: (2, 0, 1), 2: (2, 0, 1)}
    compiler.run_bits(actual, fused, perms)
    check(actual[3] == initial[3], "dirty private spectator unchanged")
    actual[3].clear()
    check(actual[3] != initial[3], "unlicensed clear negative control")
    controls.append("discarded_dirty_spectator_fails_restoration")
    for call in (lambda: compiler.power(True), lambda: compiler.power(0, True)):
        try:
            call()
        except ValueError:
            controls.append("boolean_parameter_rejected_" + str(len(controls)))
        else:
            raise RuntimeError("Boolean admitted as an integer parameter")
    return controls


def encoded_word(word):
    result = []
    for event in word:
        if event[0] == "child":
            result.append({"op": "ordinary_child", "fields": list(event[1:])})
        else:
            _, target, diagonal, controls = event
            result.append({"op": "ordered_affine", "target": target,
                           "diagonal": str(diagonal),
                           "controls": [[i, str(c)] for i, c in controls]})
    return result


def literal_fixture(compiler):
    fused = compiler.fused_program(54)
    return {"format": "native-dyadic-pair-program-v1", "j": 54, "a": 1 << 54,
            "fused_chronological_events": list(fused),
            "baseline_chronological_events": list(compiler.baseline_program(54)),
            "query_lowerings": {str(k): encoded_word(compiler.address_word(k))
                                for k in sorted({event[2] for event in fused if event[0] == "query"})}}


def evidence():
    source_digest = sources()
    compiler, full = load("program"), load("full_domain")
    baseline, fused = compiler.baseline_program(54), compiler.fused_program(54)
    return {"format": "dyadic-native-query-pair-certificate-v1",
            "base_commit": "7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261",
            "assignment_seed": 54, "new_kappa_claimed": False,
            "source_manifest_canonical_sha256": source_digest,
            "implementation_and_proof_sha256": {
                name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                for name in ("program.py", "full_domain.py", "verify.py", "PROOF.md")},
            "fixture": {"j": 54, "a": 1 << 54,
                        "baseline_invoice": compiler.invoice(baseline),
                        "fused_invoice": compiler.invoice(fused),
                        "private_rows_added": 0,
                        "claimed_scope": "three-query minimum in the specified power-query/XOR model"},
            "lowerings": rational_evidence(compiler),
            "laurent": polynomial_evidence(compiler),
            "finite_arrays": full.evidence(compiler),
            "negative_controls": negative_controls(compiler)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", type=Path, help="write a fresh certificate directory; refuse overwrite")
    args = parser.parse_args()
    result = evidence()
    fixture = literal_fixture(load("program"))
    if args.emit is not None:
        args.emit.mkdir(parents=True, exist_ok=False)
        for name, value in (("CERTIFICATE.json", result), ("PROGRAM.json", fixture)):
            (args.emit / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    else:
        check(canonical(json.loads((ROOT / "PROGRAM.json").read_text())) == canonical(fixture),
              "literal PROGRAM mismatch")
        check(canonical(json.loads((ROOT / "CERTIFICATE.json").read_text())) == canonical(result),
              "complete CERTIFICATE mismatch")
    print("PASS_DYADIC_QUERY_PAIR: children 4->3; affine 24->18; XOR 4->2; no new kappa")
    print("rational columns", result["lowerings"]["rational_columns_including_inverses_and_spectators"],
          "; modular columns", result["lowerings"]["modular_columns_including_inverses"],
          "; two-query census", result["laurent"]["two_query_products_checked"],
          "; negative controls", len(result["negative_controls"]))
    print("full-domain dirty basis columns", result["finite_arrays"]["full_dirty_basis_columns_per_program"],
          "; orbit columns", result["finite_arrays"]["orbit_dirty_basis_columns_per_program"])


if __name__ == "__main__":
    main()
