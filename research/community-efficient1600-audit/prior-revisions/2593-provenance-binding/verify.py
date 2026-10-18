#!/usr/bin/env python3
"""Exact evidence for the odd-kernel (triadic) native query pair. Apache-2.0.

Prepared by Wentao Li with substantial AI assistance.
Default verify is read-only. Admission uses need() (not assert); -O also passes.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import itertools
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHECKS = 0


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def check_sources():
    source = json.loads((ROOT / "SOURCES.json").read_text())
    need(source["schema_version"] == 1, "source schema")
    # Authored pin is recorded in SOURCES; tests may retarget base_commit in temp trees.
    need(isinstance(source["base_commit"], str) and len(source["base_commit"]) == 40, "base pin")
    for row in source["files"]:
        data = (REPO / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], f"sha256 {row['path']}")
        need(git_blob(row["path"]) == row["git_blob"], f"blob {row['path']}")
    return hashlib.sha256(canonical(source)).hexdigest()


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
    outer = set()
    for u in range(1, 1 << d):
        for v in range(1, 1 << d):
            if bin(u & v).count("1") % 2:
                outer.add(tuple(v if u & (1 << i) else 0 for i in range(d)))
    return sorted(outer)


def lowering_evidence(compiler):
    rational_columns = modular_columns = 0
    powers = [sign * 3 * (1 << j) for j in range(0, 5) for sign in (-1, 1)]
    admitted = (5, 7, 11, 13, 17, 19, 23, 25, 35, 49, 55, 77, 121)
    excluded = (3, 9, 15, 21, 27, 33, 45, 63, 75, 81, 99)
    for k in powers:
        need(compiler.odd_part(k) == 3, "odd kernel is 3")
        word = compiler.address_word(k)
        inverse = compiler.inverse_word(word)
        need(sum(e[0] == "child" for e in word) == 1, "one child")
        need(sum(e[0] == "affine" for e in word) == 6, "six affines")
        for event in word:
            if event[0] == "affine":
                need(all(i < event[1] for i, _ in event[3]), "ordered controls")
        for direction, events in ((1, word), (-1, inverse)):
            target_matrix = compiler.push_matrix(direction * k)
            for col in range(6):
                basis = tuple(int(i == col) for i in range(6))
                expected = tuple(target_matrix[i][col] for i in range(6))
                actual = compiler.run_address(basis, events)
                need(actual == expected, "rational column")
                need(
                    compiler.run_address(actual, compiler.inverse_word(events)) == basis,
                    "rational inverse",
                )
                rational_columns += 1
                for modulus in admitted:
                    need(compiler.modulus_admits(k, modulus), f"admit {modulus}")
                    target = tuple(
                        int(expected[i].numerator * pow(expected[i].denominator, -1, modulus) % modulus)
                        for i in range(6)
                    )
                    got = compiler.run_address(basis, events, modulus)
                    need(got == target, f"modular column m={modulus}")
                    modular_columns += 1
        for modulus in excluded:
            need(not compiler.modulus_admits(k, modulus), f"exclude {modulus}")
            try:
                compiler.run_address((1, 0, 0, 0, 0, 0), word, modulus)
            except ValueError:
                pass
            else:
                raise RuntimeError(f"excluded modulus {modulus} accepted")
    mixed_ok = 0
    for k in (3, -3, 6, 12, -24):
        word = compiler.address_word(k)
        for vec in itertools.product(range(-2, 3), repeat=6):
            if sum(abs(x) for x in vec) == 0:
                continue
            need(
                compiler.run_address(vec, word)
                == compiler.apply_matrix(compiler.push_matrix(k), vec),
                "closed form match",
            )
            mixed_ok += 1
            if mixed_ok >= 240:
                break
        if mixed_ok >= 240:
            break
    return {
        "kernel": 3,
        "signed_powers": powers,
        "rational_columns": rational_columns,
        "admitted_moduli": list(admitted),
        "excluded_moduli": list(excluded),
        "modular_columns": modular_columns,
        "mixed_rational_vectors": mixed_ok,
        "denominator_odd_part": 3,
    }


def laurent_evidence(compiler):
    symbolic = 0
    for j in range(0, 8):
        for sign in (-1, 1):
            a = sign * 3 * (1 << j)
            baseline = compiler.baseline_program(j, sign)
            fused = compiler.fused_program(j, sign)
            target = centered(a)
            need(polynomial_program(baseline) == target, "baseline Laurent")
            need(polynomial_program(fused) == target, "fused Laurent")
            inv = polynomial_program(compiler.inverse_program(fused))
            need(pmul(inv, target) == {0: eye(4)}, "Laurent inverse")
            symbolic += 1
    pairs = 0
    for d in (2, 3, 4):
        catalogue = projectors(d)
        target = centered(3, d)
        for p in catalogue:
            for q in catalogue:
                pq = bmul(p, q)
                for exponent in (-6, -3, -1, 1, 3, 6):
                    actual = clean(
                        {
                            0: bxor(bxor(eye(d), p), q),
                            exponent: bxor(p, pq),
                            -exponent: bxor(q, pq),
                        }
                    )
                    need(actual != target, "no two-query centered a=3 endpoint")
                    pairs += 1
    base_inv = compiler.invoice(compiler.baseline_program(0, 1))
    fuse_inv = compiler.invoice(compiler.fused_program(0, 1))
    need(base_inv["ordinary_children"] == 4 and fuse_inv["ordinary_children"] == 3, "children")
    need(base_inv["ordered_affine_events"] == 24 and fuse_inv["ordered_affine_events"] == 18, "affine")
    need(base_inv["aligned_xor_scans"] == 4 and fuse_inv["aligned_xor_scans"] == 2, "xor")
    return {
        "signed_symbolic_program_pairs": symbolic,
        "two_query_products_checked": pairs,
        "centered_survivors": 0,
        "baseline_invoice": base_inv,
        "fused_invoice": fuse_inv,
        "scope": "finite corroboration; universal exclusion is the written proof",
    }


def finite_array_evidence(compiler):
    columns = 0
    for modulus in (5, 7):
        domain = list(itertools.product(range(modulus), repeat=6))
        index = {addr: i for i, addr in enumerate(domain)}
        for j, sign in ((0, 1), (0, -1), (1, 1)):
            a = sign * 3 * (1 << j)
            fused = compiler.fused_program(j, sign)
            powers = sorted({e[2] for e in fused if e[0] == "query"})
            perms = {}
            for k in powers:
                need(compiler.modulus_admits(k, modulus), "domain admits k")
                word = compiler.address_word(k)
                perms[k] = tuple(index[compiler.run_address(addr, word, modulus)] for addr in domain)
            word_a = compiler.address_word(a)
            word_ma = compiler.address_word(-a)
            step = max(1, len(domain) // 30)
            for src_pos in range(0, len(domain), step):
                for tgt_pos in range(0, len(domain), step):
                    rows = [set(), set(), {0}, {1}]
                    rows[0].add(tgt_pos)
                    rows[1].add(src_pos)
                    before = [set(r) for r in rows]
                    compiler.run_bits(rows, fused, perms)
                    exp = set(before[0])
                    sa = {index[compiler.run_address(domain[p], word_a, modulus)] for p in before[1]}
                    sma = {index[compiler.run_address(domain[p], word_ma, modulus)] for p in before[1]}
                    exp ^= sa
                    exp ^= sma
                    need(rows[0] == exp, "dirty endpoint")
                    need(rows[1] == before[1], "source restored")
                    need(rows[2] == before[2] and rows[3] == before[3], "spectators")
                    columns += 1
    return {"full_dirty_endpoint_columns": columns, "moduli": [5, 7]}


def negative_controls(compiler):
    controls = []
    fused = compiler.fused_program(0, 1)
    target = centered(3)

    def reject(name, word):
        need(polynomial_program(word) != target, "ineffective " + name)
        controls.append(name)

    for i in range(len(fused)):
        reject(f"omit_fused_event_{i}", fused[:i] + fused[i + 1 :])
    bad = list(fused)
    bad[2] = ("query", 0, 3)
    reject("central_power_not_doubled", tuple(bad))
    bad = list(fused)
    bad[0] = ("query", 0, 3)
    reject("first_query_wrong_sign", tuple(bad))
    word = compiler.address_word(3)
    need(compiler.modulus_admits(3, 5), "admits 5")
    need(not compiler.modulus_admits(3, 3), "excludes 3")
    controls.append("kernel3_excludes_multiples_of_three")
    try:
        compiler.run_address((1, 0, 0, 0, 0, 0), word, 3)
    except ValueError:
        controls.append("modulus_three_execution_rejected")
    else:
        raise RuntimeError("modulus 3 accepted")
    try:
        compiler.run_address((1, 0, 0, 0, 0, 0), word, 2)
    except ValueError:
        controls.append("even_modulus_rejected")
    else:
        raise RuntimeError("even modulus accepted")
    p, q = (1, 0), (3, 0)
    product = pmul({0: bxor(eye(2), p), 1: p}, {0: bxor(eye(2), q), -1: q})
    need(product != centered(3, 2), "first-difference distinct")
    controls.append("first_difference_two_query_scope")
    row = {0}
    try:
        compiler.run_bits([row, row, set()], fused, {-3: (0,), 6: (0,)})
    except ValueError:
        controls.append("aliased_rows_rejected")
    else:
        raise RuntimeError("alias accepted")
    # Dyadic predecessor rejects non-dyadic universal claim; we change that premise.
    controls.append("complements_pr840_non_dyadic_exclusion")
    return controls


def build_certificate(compiler):
    source_digest = check_sources()
    baseline = compiler.baseline_program(0, 1)
    fused = compiler.fused_program(0, 1)
    return {
        "format": "triadic-native-query-pair-certificate-v1",
        "base_commit": json.loads((ROOT / "SOURCES.json").read_text())["base_commit"],
        "kernel": 3,
        "fixture": {"j": 0, "a": 3, "sign": 1},
        "new_kappa_claimed": False,
        "source_manifest_canonical_sha256": source_digest,
        "implementation_sha256": {
            name: sha256_file(ROOT / name)
            for name in ("program.py", "verify.py", "independent.py", "PROOF.md", "README.md")
        },
        "baseline_invoice": compiler.invoice(baseline),
        "fused_invoice": compiler.invoice(fused),
        "lowerings": lowering_evidence(compiler),
        "laurent": laurent_evidence(compiler),
        "finite_arrays": finite_array_evidence(compiler),
        "negative_controls": negative_controls(compiler),
        "claimed_scope": (
            "three-query completed native DATA shear for a=±3·2^j with odd moduli "
            "coprime to 3; paid lowering, not a supplier"
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="regenerate CERTIFICATE.json")
    args = parser.parse_args()
    compiler = load("program")
    # Placeholder files must exist before hashing into the certificate.
    for name in ("PROOF.md", "README.md", "independent.py", "SOURCES.json"):
        need((ROOT / name).is_file(), f"missing {name}")
    cert = build_certificate(compiler)
    path = ROOT / "CERTIFICATE.json"
    if args.write:
        path.write_text(json.dumps(cert, indent=2, sort_keys=True) + "\n")
    else:
        committed = json.loads(path.read_text())
        need(canonical(committed) == canonical(cert), "CERTIFICATE mismatch")
    inv = cert["fused_invoice"]
    base = cert["baseline_invoice"]
    print(
        "PASS_TRIADIC_QUERY_PAIR "
        f"children {base['ordinary_children']}->{inv['ordinary_children']}; "
        f"affine {base['ordered_affine_events']}->{inv['ordered_affine_events']}; "
        f"XOR {base['aligned_xor_scans']}->{inv['aligned_xor_scans']}; "
        f"kernel=3 excluded_moduli={len(cert['lowerings']['excluded_moduli'])} "
        f"rational={cert['lowerings']['rational_columns']} "
        f"modular={cert['lowerings']['modular_columns']} "
        f"two_query_census={cert['laurent']['two_query_products_checked']} "
        f"dirty_columns={cert['finite_arrays']['full_dirty_endpoint_columns']} "
        f"controls={len(cert['negative_controls'])} "
        f"checks={CHECKS} no_new_kappa"
    )


if __name__ == "__main__":
    main()
