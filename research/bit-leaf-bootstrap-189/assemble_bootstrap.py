#!/usr/bin/env python3
"""Compose the record's own assembly with PR185's verified finite leaf bootstrap.

The record (PR194) prices its bit supplier with PR184's legacy ordinary leaf
saving OLD = 384599/10^10:

    effective = (1-atom)*coarse + atom*OLD,  atom = least payable atom on 10^-12

and PR194's own `assemble` sets

    kappa = a/(1+a),   a = min(bit_effective, (1-1e-9)*complex_saving - 10^-10).

PR185 (bit-leaf-bootstrap182, verified: "three finite bootstrap levels, 47 strict
constraints, 7 margins, 11 controls per depth, adjacent grids") replaced that
legacy leaf by a finite acyclic wrapper whose leaf value obeys

    a_0 = legacy effective,   a_{n+1} = (1-C)*C + C*a_n = C - C^n (C - a_0),

with C the coarse bit saving: the wrapper leaves converge to the coarse saving.

This script reproduces PR194's kappa from PR194's own inputs and machinery, then
applies that recurrence to the bit leaf and re-runs the unchanged assembly.
Complex supplier, bit word and assembly are PR194's.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, importlib.util, json, sys, tarfile

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pr194", type=Path, required=True, help="PR194 source-assisted-v4 dir")
    ap.add_argument("--pr189", type=Path, required=True,
                    help="PR189 package as vendored in PR194 (paired-cube-twin-local-168)")
    ap.add_argument("--pin-tarball", type=Path, required=True)
    ap.add_argument("--depths", type=int, nargs="+", default=[1, 2, 3])
    a = ap.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    PKG, PR189 = a.pr194.resolve(), a.pr189.resolve()
    cert = json.loads((PKG / "certificate.json").read_text())
    pr189 = json.loads((PR189 / "certificate.json").read_text())
    pr184 = load(PKG.parent / "source-assisted" / "global" / "assemble_profiles.py",
                 "attack_pr184")

    work = HERE / ".work"
    work.mkdir(exist_ok=True)
    if not (work / "pr168_fd25adb7").is_dir():
        with tarfile.open(a.pin_tarball.resolve()) as tf:
            tf.extractall(work)
    pin = work / "pr168_fd25adb7"
    assert (pin / "scripts" / "paired_cube_assembly.py").is_file(), \
        f"pinned assembly source missing under {pin}"
    proof = pr184.HERE / "FINITE_BRIDGE.txt"

    # Exactly PR194's inputs: complex profile = its complex certificate,
    # bit profile = PR189's certified bit profile.
    c = pr184.select(pr184.normalize(cert["complex_profile"]))
    row_bit = pr189["bit"]["profile"]
    assert row_bit["m"] == 72 and row_bit["deficit_per_vertex"] == 1936
    assert row_bit["terminal_sinks"] == 34 and row_bit["reused_registers"] == 1760
    b = pr184.select(pr184.normalize(row_bit), True)
    assert b["saving"] <= Q(pr189["bit"]["coarse"]["coarse_saving"])

    legacy = pr184.assemble(c, b, pin, proof)
    record = Q(cert["kappa"])
    print(f"[reproduce] PR194 kappa = {legacy['kappa']} vs certificate {record} "
          f"-> {'EXACT' if Q(legacy['kappa']) == record else 'MISMATCH'}")
    print(f"[reproduce] complex={float(c['saving']):.15g} bit_coarse={float(b['saving']):.15g} "
          f"bit_effective={float(b['effective_saving']):.15g} "
          f"atom={float(b['atom_exponent']):.15g} OLD={float(Q(b['ordinary_leaf_saving'])):.15g}")
    assert Q(legacy["kappa"]) == record, "harness does not reproduce the record"
    assert len(legacy["assembly"]["strict_constraints"]) == 47
    assert len(legacy["assembly"]["margins"]) == 7

    Cc, A0 = Q(b["saving"]), Q(b["effective_saving"])
    results = {}
    for depth in a.depths:
        values = [A0]
        for _ in range(depth):
            values.append((1 - Cc) * Cc + Cc * values[-1])
        assert values[-1] == Cc - Cc**depth * (Cc - A0), "closed-form recurrence"
        if depth:
            assert A0 < values[-1] < Cc, "wrapper leaves converge to the coarse saving"
        boot = dict(b)
        boot.update(effective_saving=values[-1], effective_saving_decimal=float(values[-1]),
                    ordinary_leaf_saving=values[-1], atom_exponent=Cc)
        out = pr184.assemble(c, boot, pin, proof)
        asm = out["assembly"]
        assert len(asm["strict_constraints"]) == 47 and len(asm["margins"]) == 7
        assert all(Q(x) > 0 for x in asm["strict_constraints"].values()), "47 strict constraints"
        assert all(Q(x) > Q(out["kappa"]) for x in asm["margins"].values()), "7 margins"
        k = Q(out["kappa"])
        results[depth] = dict(kappa=str(k), kappa_decimal=float(k),
                              leaf=str(values[-1]), leaf_decimal=float(values[-1]),
                              gain_vs_record=float(k / record - 1),
                              constraints=len(asm["strict_constraints"]),
                              margins=len(asm["margins"]),
                              kappa_decimal_grid=str(out["kappa"]))
        print(f"[depth {depth}] leaf={float(values[-1]):.15g}  kappa={k} ({float(k):.15g})  "
              f"gain vs record={float(k/record-1)*100:+.4f}%  [47 constraints, 7 margins]")
    # Strict tolls of the wrapper (PR185's paid atom and row inequalities) and
    # two controls: depth 0 is exactly the record (no gain without the wrapper),
    # and the untolled limit C is strictly overshooting, so the claimed leaf is
    # strictly below the limit rather than an artifact of an unpaid toll.
    best_entry = max(results.items(), key=lambda kv: kv[1]["kappa_decimal"])
    leaf_best = Q(best_entry[1]["leaf"])
    assert A0 < leaf_best < Cc < 1 - leaf_best, "strict paid atom and row tolls"
    limit = dict(b)
    limit.update(effective_saving=Cc, ordinary_leaf_saving=Cc, atom_exponent=Cc)
    out_limit = pr184.assemble(c, limit, pin, proof)
    assert Q(out_limit["kappa"]) >= Q(best_entry[1]["kappa"]), "claim sits below the limit"
    print(f"[control] depth 0 = record {legacy['kappa']};  untolled limit C gives "
          f"{out_limit['kappa']} vs claimed {best_entry[1]['kappa']} "
          f"(edge of the 10^-10 grid)")
    print(f"[control] strict tolls hold: {float(A0):.15g} < {float(leaf_best):.15g} "
          f"< {float(Cc):.15g} < {float(1-leaf_best):.15g}")

    best = best_entry
    print(f"[best] depth {best[0]}: kappa={best[1]['kappa']} vs record {record} "
          f"({best[1]['gain_vs_record']*100:+.4f}%)")
    (HERE / "bootstrap-result.json").write_text(json.dumps(dict(
        record_kappa=str(record), record_kappa_decimal=float(record),
        complex_saving=str(c["saving"]), complex_saving_decimal=float(c["saving"]),
        bit_coarse=str(Cc), bit_coarse_decimal=float(Cc),
        bit_legacy_effective=str(A0), bit_legacy_effective_decimal=float(A0),
        bit_legacy_atom=str(b["atom_exponent"]),
        bit_old_leaf=str(b["ordinary_leaf_saving"]),
        depths=results, best_depth=best[0], best=best[1],
        provenance=dict(
            complex="PR193 complex word as carried by PR194's certificate complex_profile",
            bit="PR189 face-diagonal bit word certificate bit.profile, priced by PR184's select()",
            bootstrap="PR185 bit-leaf-bootstrap182 finite acyclic leaf recurrence",
            assembly="PR194's unchanged 47-constraint balanced assembly with PR184's finite bridge",
            pinned_source="research/source-assisted/public/pr168_fd25adb7.tar.gz"),
    ), indent=1) + "\n")
    print(f"[write] {HERE/'bootstrap-result.json'}")


if __name__ == "__main__":
    main()
