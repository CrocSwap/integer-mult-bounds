#!/usr/bin/env python3
"""Price a bit supplier with the finite leaf bootstrap against PR193's complex.

The record's assembly computes kappa = a/(1+a) with

    a = min(bit_effective, (1-1e-9)*complex_saving - 1e-10),

and every bit supplier published so far has been priced with PR184's legacy
ordinary leaf OLD = 384599/10^10, which holds the effective value below the
supplier's coarse saving C. PR185's finite acyclic bootstrap

    a_0 = legacy effective,  a_{n+1} = (1-C)*C + C*a_n = C - C^n (C - a_0)

recovers it. This script applies that to an arbitrary certified bit profile and
reports the exact composition, so a new supplier can be priced the moment its
certificate exists.

    python3 -B next_bit_composition.py \
        --bit-certificate <pkg>/certificate.json  (bit.profile / bit.coarse) \
        --complex-certificate <pr194>/certificate.json  (complex_profile) \
        --pr184 <pr194>/research/source-assisted/global/assemble_profiles.py \
        --pin-tarball <pr194>/research/source-assisted/public/pr168_fd25adb7.tar.gz
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys, tarfile

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bit_profile(cert):
    """A bit profile, from a `bit.profile` block or a bare profile dict."""
    node = cert["bit"]["profile"] if isinstance(cert, dict) and "bit" in cert else cert
    for key in ("m", "W_per_vertex", "deficit_per_vertex", "child_histogram"):
        assert key in node, f"bit profile lacks {key}"
    return node


def complex_profile(cert):
    if "complex_profile" in cert:
        return cert["complex_profile"]
    if "complex" in cert and isinstance(cert["complex"], dict) and "profile" in cert["complex"]:
        return cert["complex"]["profile"]
    for key in ("combined_fixed_boundary_profile",):
        if key in cert:
            return cert[key]
    raise SystemExit("complex profile not found")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bit-certificate", type=Path, required=True)
    ap.add_argument("--complex-certificate", type=Path, required=True)
    ap.add_argument("--pr184", type=Path, required=True)
    ap.add_argument("--pin-tarball", type=Path, required=True)
    ap.add_argument("--work", type=Path, default=HERE / ".work")
    ap.add_argument("--depths", type=int, nargs="+", default=[0, 1, 2, 3])
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    pr184 = load(a.pr184.resolve(), "next_comp_pr184")
    a.work.mkdir(exist_ok=True)
    if not (a.work / "pr168_fd25adb7").is_dir():
        with tarfile.open(a.pin_tarball.resolve()) as tf:
            tf.extractall(a.work)
    pin = a.work / "pr168_fd25adb7"
    proof = pr184.HERE / "FINITE_BRIDGE.txt"

    bit_cert = json.loads(a.bit_certificate.read_text())
    comp_cert = json.loads(a.complex_certificate.read_text())
    row_bit = bit_profile(bit_cert)
    c = pr184.select(pr184.normalize(complex_profile(comp_cert)))
    b = pr184.select(pr184.normalize(row_bit), True)
    Cc, A0 = Q(b["saving"]), Q(b["effective_saving"])
    print(f"[bit supplier] m={row_bit['m']} W={row_bit['W_per_vertex']} "
          f"deficit={row_bit['deficit_per_vertex']} sinks={row_bit.get('terminal_sinks')} "
          f"coarse={Cc} ({float(Cc):.15g})")
    print(f"[complex] saving={c['saving']} ({float(c['saving']):.15g})")
    print(f"[legacy]  effective={A0} ({float(A0):.15g})  slack below coarse="
          f"{float(Cc)-float(A0):.6g}")
    rows = {}
    for depth in a.depths:
        values = [A0]
        for _ in range(depth):
            values.append((1 - Cc) * Cc + Cc * values[-1])
        assert values[-1] == Cc - Cc**depth * (Cc - A0)
        if depth:
            assert A0 < values[-1] < Cc
        boot = dict(b)
        boot.update(effective_saving=values[-1], effective_saving_decimal=float(values[-1]),
                    ordinary_leaf_saving=values[-1], atom_exponent=Cc)
        out = pr184.assemble(c, boot, pin, proof)
        asm = out["assembly"]
        assert len(asm["strict_constraints"]) == 47 and len(asm["margins"]) == 7
        assert all(Q(x) > 0 for x in asm["strict_constraints"].values())
        assert all(Q(x) > Q(out["kappa"]) for x in asm["margins"].values())
        k = Q(out["kappa"])
        rows[depth] = dict(kappa=str(k), kappa_decimal=float(k), leaf=str(values[-1]),
                           leaf_decimal=float(values[-1]), binding="bit" if Cc < c["saving"] else "complex")
        print(f"[depth {depth}] leaf={float(values[-1]):.15g}  kappa={k} ({float(k):.15g})"
              f"  [47 constraints, 7 margins]")
    best = max(rows.items(), key=lambda kv: kv[1]["kappa_decimal"])
    prev = {197: "135216063303877/200000000000000000", 199: "267141/400000000"}
    print(f"[best] depth {best[0]}: kappa={best[1]['kappa']}")
    for n, val in prev.items():
        q = Q(val)
        print(f"        vs #{n}: {float(best[1]['kappa_decimal']/float(q)-1)*100:+.4f}%")
    if a.out:
        a.out.write_text(json.dumps(dict(
            bit_supplier=dict(source=a.bit_certificate.name, sha256=sha(a.bit_certificate),
                              m=row_bit["m"], W=row_bit["W_per_vertex"],
                              terminal_sinks=row_bit.get("terminal_sinks")),
            complex_supplier=dict(source=a.complex_certificate.name, sha256=sha(a.complex_certificate),
                                  saving=str(c["saving"])),
            coarse=str(Cc), legacy_effective=str(A0), depths=rows,
            best_depth=best[0], best=best[1]), indent=1) + "\n")
        print(f"[write] {a.out}")


if __name__ == "__main__":
    main()
