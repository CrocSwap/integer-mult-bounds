#!/usr/bin/env python3
"""Exact evidence for the general odd-kernel query-pair pattern. Apache-2.0.

Prepared by Wentao Li with substantial AI assistance.
Default verify is read-only. Admission uses need() (not assert); -O also passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
CHECKS = 0

# Primary kernels beyond dyadic (1) and the pending triadic (3) cross-check.
KERNELS = (1, 3, 5, 7, 9, 15)
PRIMARY_NEW = (5, 7, 9, 15)
PROBE_MODULI = (
    2, 4, 6, 8, 10,
    3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 33, 35, 39, 45, 49, 55, 63, 77, 105,
)


def need(ok, message):
    global CHECKS
    CHECKS += 1
    if not ok:
        raise RuntimeError(message)


def load_program():
    import importlib.util

    spec = importlib.util.spec_from_file_location("okqp", ROOT / "program.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def git_blob(path: str) -> str:
    return subprocess.check_output(
        ["git", "-C", str(REPO), "rev-parse", f"HEAD:{path}"], text=True
    ).strip()


def check_sources():
    source = json.loads((ROOT / "SOURCES.json").read_text())
    need(source["schema_version"] == 1, "source schema")
    need(isinstance(source["base_commit"], str) and len(source["base_commit"]) == 40, "base")
    for row in source["files"]:
        data = (REPO / row["path"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row["sha256"], f"sha256 {row['path']}")
        need(git_blob(row["path"]) == row["git_blob"], f"blob {row['path']}")
    return hashlib.sha256(canonical(source)).hexdigest()


def reject_duplicate_keys(text: str):
    bad = []

    def hook(items):
        keys = [k for k, _ in items]
        if len(keys) != len(set(keys)):
            bad.append(True)
        return dict(items)

    json.loads(text, object_pairs_hook=hook)
    need(not bad, "duplicate JSON keys")


def mm(A, B):
    return tuple(
        tuple(sum(A[i][k] * B[k][j] for k in range(6)) for j in range(6))
        for i in range(6)
    )


def build_certificate(prog):
    per_kernel = {}
    for kernel in KERNELS:
        # Invoice invariance.
        base = prog.invoice(prog.baseline_program(0, 1, kernel), kernel)
        fuse = prog.invoice(prog.fused_program(0, 1, kernel), kernel)
        need(base["ordinary_children"] == 4 and fuse["ordinary_children"] == 3, "children")
        need(base["ordered_affine_events"] == 24 and fuse["ordered_affine_events"] == 18, "affine")
        need(base["aligned_xor_scans"] == 4 and fuse["aligned_xor_scans"] == 2, "xor")

        # Exclusion pattern vs closed form for fused powers at several j.
        admitted = []
        excluded = []
        for modulus in PROBE_MODULI:
            closed = prog.modulus_admits_kernel(kernel, modulus)
            ok_all = True
            for j, sign in ((0, 1), (0, -1), (1, 1), (2, -1), (3, 1)):
                for k in prog.fused_query_powers(j, sign, kernel):
                    need(prog.odd_part(k) == kernel, "odd part equals kernel")
                    if prog.modulus_admits(k, modulus) != closed:
                        ok_all = False
                        break
                if not ok_all:
                    break
            need(ok_all, f"pattern mismatch kernel={kernel} m={modulus}")
            if closed:
                admitted.append(modulus)
            else:
                excluded.append(modulus)

        # Rational columns + selected modular specializations.
        rational = modular = 0
        for j, sign in ((0, 1), (1, -1), (2, 1)):
            for k in set(prog.fused_query_powers(j, sign, kernel)):
                word = prog.address_word(k)
                target = prog.push_matrix(k)
                for col in range(6):
                    basis = tuple(int(i == col) for i in range(6))
                    expected = tuple(target[i][col] for i in range(6))
                    need(prog.run_address(basis, word) == expected, "rational column")
                    rational += 1
                    for modulus in admitted[:4]:
                        got = prog.run_address(basis, word, modulus)
                        want = tuple(
                            int(
                                expected[i].numerator
                                * pow(expected[i].denominator, -1, modulus)
                                % modulus
                            )
                            for i in range(6)
                        )
                        need(got == want, f"modular k={k} m={modulus}")
                        modular += 1
                for modulus in excluded[:3]:
                    need(not prog.modulus_admits(k, modulus), "exclude")
                    try:
                        prog.run_address((1, 0, 0, 0, 0, 0), word, modulus)
                    except ValueError:
                        pass
                    else:
                        raise RuntimeError(f"excluded modulus {modulus} accepted")

        # Query product identity M(-a)M(2a)M(-a)=I.
        a = prog.odd_kernel_power(0, 1, kernel)
        I = tuple(tuple(Fraction(i == j) for j in range(6)) for i in range(6))
        need(
            mm(mm(prog.push_matrix(-a), prog.push_matrix(2 * a)), prog.push_matrix(-a)) == I,
            "query product",
        )

        per_kernel[str(kernel)] = {
            "kernel": kernel,
            "excluded_odd_primes": list(prog.odd_primes(kernel)),
            "baseline_invoice": base,
            "fused_invoice": fuse,
            "admitted_probe_moduli": admitted,
            "excluded_probe_moduli": excluded,
            "rational_columns": rational,
            "modular_columns": modular,
            "pattern": "odd modulus coprime to kernel",
        }

    # No typed-cost improvement over dyadic.
    dyadic = per_kernel["1"]["fused_invoice"]
    for kernel in PRIMARY_NEW:
        fuse = per_kernel[str(kernel)]["fused_invoice"]
        need(fuse["ordinary_children"] == dyadic["ordinary_children"], "children invariant")
        need(fuse["ordered_affine_events"] == dyadic["ordered_affine_events"], "affine invariant")
        need(fuse["aligned_xor_scans"] == dyadic["aligned_xor_scans"], "xor invariant")

    # Dyadic recovers all-odd admission among probes.
    need(
        set(per_kernel["1"]["admitted_probe_moduli"])
        == {m for m in PROBE_MODULI if m % 2 == 1},
        "dyadic admits every odd probe",
    )
    need(
        set(per_kernel["1"]["excluded_probe_moduli"])
        == {m for m in PROBE_MODULI if m % 2 == 0},
        "dyadic excludes exactly the even probes",
    )

    return {
        "format": "odd-kernel-query-pair-certificate-v1",
        "claimed_scope": (
            "general odd kernel q: three-query fused native DATA shear at a=±q·2^j "
            "on odd moduli coprime to q; typed costs 4→3 / 24→18 / 4→2; no new kappa"
        ),
        "kernels": list(KERNELS),
        "primary_new_kernels": list(PRIMARY_NEW),
        "probe_moduli": list(PROBE_MODULI),
        "per_kernel": per_kernel,
        "typed_cost_improvement_over_dyadic": False,
        "no_new_kappa": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    prog = load_program()
    cert = build_certificate(prog)
    pretty = json.dumps(cert, indent=2, sort_keys=True) + "\n"
    reject_duplicate_keys(pretty)
    path = ROOT / "CERTIFICATE.json"
    if args.write:
        path.write_text(pretty)
        print("WROTE_CERTIFICATE", path)
    else:
        need(path.is_file(), "missing CERTIFICATE.json; pass --write once")
        existing = path.read_text()
        reject_duplicate_keys(existing)
        need(json.loads(existing) == cert, "certificate drift")
    sources = check_sources()
    print(
        "PASS_ODD_KERNEL_QUERY_PAIR "
        f"kernels={list(KERNELS)} "
        f"primary_new={list(PRIMARY_NEW)} "
        f"children=4->3 affine=24->18 xor=4->2 "
        f"no_typed_gain_over_dyadic "
        f"sources={sources[:12]} checks={CHECKS} no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
