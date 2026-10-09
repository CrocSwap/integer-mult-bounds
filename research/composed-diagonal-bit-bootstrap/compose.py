#!/usr/bin/env python3
"""Compose a certified bit supplier with PR184's finite leaf and PR194's complex.

The record's assembly sets

    a = min(bit_effective, (1-stop)*complex_saving - 1/SELECT_GRID),
    kappa = floor( (1-eta)*q/(1+q) * SELECT_GRID ) / SELECT_GRID,  q = a*(1-2*eta),

with the case-dependent `eta`, `stop` of PR184's `assemble_profiles.py`. Every bit
supplier published so far has been handed to it through PR184's *legacy* ordinary
leaf, `effective = (1-beta)*C + beta*OLD` with `OLD = 384599/10^10`, which holds
the effective value strictly below the supplier's coarse saving `C`. PR185
replaced that leaf by a finite acyclic wrapper whose value obeys

    a_0 = legacy effective,   a_{n+1} = (1-C)*C + C*a_n = C - C^n (C - a_0).

This script applies that recurrence to an arbitrary certified bit profile,
composes it with a certified complex profile through PR194's unchanged assembly,
and reports the exact kappa at each depth together with the bit branch's own
ceiling `C/(1+C)`.

    python3 -B compose.py [--out certificate.json]

Inputs, digests and provenance are in SOURCE.json; the paths below are the
vendored pins, so this runs from the package directory alone.
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
SELECT_GRID = 10 ** 10
OLD = Q(384599, SELECT_GRID)
DEFAULTS = dict(
    bit=HERE / "inputs/pr200-bit-certificate.json",
    complex=HERE / "references/pr194/certificate.json",
    pr184=HERE / "references/pr184/assemble_profiles.py",
    pr168_v4=HERE / "references/pr168-v4",
    finite_bridge=HERE / "references/pr184/FINITE_BRIDGE.txt",
)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bit_profile(certificate):
    """The bit profile block of a supplier certificate."""
    node = certificate["bit"]["profile"] if "bit" in certificate else certificate
    for key in ("m", "W_per_vertex", "deficit_per_vertex", "child_histogram"):
        assert key in node, "bit profile lacks " + key
    return node


def complex_profile(certificate):
    if "complex_profile" in certificate:
        return certificate["complex_profile"]
    if "combined_fixed_boundary_profile" in certificate:
        return certificate["combined_fixed_boundary_profile"]
    if "complex" in certificate and "profile" in certificate["complex"]:
        return certificate["complex"]["profile"]
    raise SystemExit("complex profile not found in the complex certificate")


def bootstrap_chain(coarse, initial, depth):
    values = [initial]
    for _ in range(depth):
        values.append((1 - coarse) * coarse + coarse * values[-1])
    assert values[-1] == coarse - coarse ** depth * (coarse - initial)
    return values


def price(pr184, complex_row, bit_row, coarse, chain, work):
    """Assemble one bootstrapped leaf, returning the exact record row."""
    leaf = chain[-1]
    assert chain[0] == bit_row["effective_saving"]
    if len(chain) > 1:
        assert chain[0] < leaf < coarse < 1 - leaf
    boot = dict(bit_row)
    boot.update(effective_saving=leaf, effective_saving_decimal=float(leaf),
                ordinary_leaf_saving=leaf, atom_exponent=coarse)
    out = pr184.assemble(complex_row, boot, work["pr168_v4"], work["finite_bridge"])
    assembly = out["assembly"]
    assert len(assembly["strict_constraints"]) == 47, "strict constraints"
    assert len(assembly["margins"]) == 7, "margins"
    assert all(Q(v) > 0 for v in assembly["strict_constraints"].values())
    kappa = Q(out["kappa"])
    assert all(Q(v) > kappa for v in assembly["margins"].values())
    margin = Q(assembly["minimum_margin"])
    assert 0 < margin <= coarse / (1 + coarse), "the bit branch ceiling"
    assert kappa <= margin < kappa + Q(1, SELECT_GRID), "kappa is the last grid point"
    return dict(leaf=str(leaf), leaf_decimal=float(leaf), kappa=str(kappa),
                kappa_decimal=float(kappa),
                minimum_margin=str(assembly["minimum_margin"]),
                minimum_margin_decimal=float(assembly["minimum_margin"]),
                binding="bit" if coarse <= complex_row["saving"] else "complex",
                assembly_source_sha256=out["assembly_source_sha256"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bit-certificate", type=Path, default=DEFAULTS["bit"])
    parser.add_argument("--complex-certificate", type=Path, default=DEFAULTS["complex"])
    parser.add_argument("--pr184", type=Path, default=DEFAULTS["pr184"])
    parser.add_argument("--pr168-v4", type=Path, default=DEFAULTS["pr168_v4"])
    parser.add_argument("--finite-bridge", type=Path, default=DEFAULTS["finite_bridge"])
    parser.add_argument("--depths", type=int, nargs="+", default=[0, 1, 2, 3, 8])
    parser.add_argument("--out", type=Path, default=HERE / "certificate.json")
    args = parser.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    assert not sys.flags.optimize, "assertions must stay enabled"
    pr184 = load(args.pr184.resolve(), "composed_pr184")
    work = dict(pr168_v4=args.pr168_v4.resolve(), finite_bridge=args.finite_bridge.resolve())
    assert (work["pr168_v4"] / "scripts/paired_cube_assembly.py").is_file(), "assembly pin"
    assert work["finite_bridge"].is_file(), "finite bridge pin"

    bit_cert = json.loads(args.bit_certificate.read_text())
    complex_cert = json.loads(args.complex_certificate.read_text())
    row = bit_profile(bit_cert)
    complex_row = pr184.select(pr184.normalize(complex_profile(complex_cert)))
    bit_row = pr184.select(pr184.normalize(row), True)
    coarse, initial = Q(bit_row["saving"]), Q(bit_row["effective_saving"])
    assert initial < coarse, "the legacy leaf must sit below the coarse saving"
    print(f"[bit supplier] m={row['m']} W={row['W_per_vertex']} "
          f"deficit={row['deficit_per_vertex']} sinks={row.get('terminal_sinks')} "
          f"coarse={coarse} ({float(coarse):.15g}) "
          f"legacy leaf={initial} ({float(initial):.15g})")
    print(f"[complex] saving={complex_row['saving']} "
          f"({float(complex_row['saving']):.15g})")

    rows = {}
    for depth in args.depths:
        chain = bootstrap_chain(coarse, initial, depth)
        rows[str(depth)] = price(pr184, complex_row, bit_row, coarse, chain, work)
        print(f"[depth {depth}] leaf={rows[str(depth)]['leaf_decimal']:.15g} "
              f"kappa={rows[str(depth)]['kappa']} "
              f"({rows[str(depth)]['kappa_decimal']:.15g}) "
              f"[47 strict constraints, 7 margins, binding {rows[str(depth)]['binding']}]")

    ceiling = coarse / (1 + coarse)
    best_depth = max(rows, key=lambda d: rows[d]["kappa_decimal"])
    best = Q(rows[best_depth]["kappa"])
    assert best <= ceiling, "kappa cannot exceed the bit branch ceiling"
    print(f"[bit ceiling] C/(1+C) = {float(ceiling):.15g}; best depth {best_depth} sits "
          f"{float(ceiling - best):.3g} below it (grid {1 / SELECT_GRID:.1g})")
    for name, value in (("#197 packed bit", Q(135216063303877, 200000000000000000)),
                        ("#200 legacy, announced", Q(6768823, SELECT_GRID))):
        print(f"[comparison] vs {name}: {float(best / value - 1) * 100:+.4f}%")
    comparisons = {
        "pr197_published": str(Q(135216063303877, 200000000000000000)),
        "pr200_announced_legacy": str(Q(6768823, SELECT_GRID)),
        "pr194_published": str(Q(complex_cert["kappa"])) if "kappa" in complex_cert else None,
    }
    out = dict(
        claim=dict(kappa=str(best), kappa_decimal=float(best), best_depth=int(best_depth),
                   binding=rows[best_depth]["binding"],
                   gain_vs_pr197=float(best / Q(comparisons["pr197_published"]) - 1),
                   gain_vs_pr200_announced_legacy=float(
                       best / Q(comparisons["pr200_announced_legacy"]) - 1)),
        bit_supplier=dict(source=args.bit_certificate.name, sha256=digest(args.bit_certificate),
                          m=row["m"], W_per_vertex=row["W_per_vertex"],
                          deficit_per_vertex=row["deficit_per_vertex"],
                          terminal_sinks=row.get("terminal_sinks"),
                          profile=row),
        complex_supplier=dict(source=args.complex_certificate.name,
                              sha256=digest(args.complex_certificate),
                              saving=str(complex_row["saving"]),
                              published_kappa=complex_cert.get("kappa")),
        assembly=dict(pr184=args.pr184.name, pr184_sha256=digest(args.pr184),
                      pr168_v4_assembly_sha256=rows[best_depth]["assembly_source_sha256"],
                      strict_constraint_count=47, margin_count=7),
        bit_coarse_saving=str(coarse), legacy_leaf=str(initial), old_leaf=str(OLD),
        ceiling=str(ceiling), ceiling_decimal=float(ceiling),
        depths=rows, comparisons={k: v for k, v in comparisons.items() if v},
        scope=("Conditional composition: the physical complex and bit words are the suppliers' "
               "certified artifacts, vendored and priced, not rebuilt or replayed. The finite "
               "leaf wrapper is PR185's construction, not one built here."))
    args.out.write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    print(f"[write] {args.out}")


if __name__ == "__main__":
    main()
