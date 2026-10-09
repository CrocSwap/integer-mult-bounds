#!/usr/bin/env python3
"""Verify the composed diagonal-bit bootstrap record.

    python3 -B research/composed-diagonal-bit-bootstrap/verify.py

Checks, in order: every pinned byte against SOURCE.json; an exact regeneration of
certificate.json from the vendored inputs; two published cross-checks (the
depth-0 value against PR200's announced value for this composition, and PR184's
grid legacy leaf against PR200's published atom-wrapper value); the standing
claim; the bit branch's own ceiling; the finite-leaf tolls; the adjacent final
grid; and the corruption controls. The physical words are inherited pins and are
not replayed here.
"""
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORK = HERE / ".work"
GRID = 10 ** 10
OLD = Q(384599, GRID)

# Published references, quoted from the open pull requests.
PR197_KAPPA = Q(135216063303877, 200000000000000000)   # #197 packed bit: standing claim
PR200_LEGACY_KAPPA = Q(6768823, GRID)                  # #200's own value for this composition
PR200_THETA = Q(677340914792209011107, 10 ** 24)       # #200 README atom-wrapper exponent
PR200_A0 = Q(677773948354561, 10 ** 18)                # #200 README bit coarse saving
PR194_KAPPA = Q(1668581, 2500000000)                   # #194 as published


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def rejects(name, operation, errors=(AssertionError, ValueError, KeyError)):
    try:
        operation()
    except errors:
        return name
    raise AssertionError("control accepted: " + name)


def tolls(coarse, leaf):
    """compose.py's own guard, mirrored so the control exercises that condition."""
    assert Q(leaf) < Q(coarse) < 1 - Q(leaf), "strict paid tolls"


def main():
    assert not sys.flags.optimize, "refusing -O"
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)

    # 1. Every pinned byte.
    manifest = json.loads((HERE / "SOURCE.json").read_text())
    drift = sorted(rel for rel, digest in manifest["files"].items()
                   if sha(ROOT / rel) != digest)
    assert not drift, ("pinned byte drift", drift)
    print("[pins] {} package and input files match SOURCE.json".format(len(manifest["files"])))

    # 2. Regenerate the certificate from the vendored inputs alone.
    WORK.mkdir(exist_ok=True)
    regenerated = WORK / "certificate.json"
    if regenerated.exists():
        regenerated.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "compose.py"), "--out", str(regenerated)],
                   check=True, stdout=subprocess.DEVNULL)
    record = json.loads(regenerated.read_text())
    assert record == json.loads((HERE / "certificate.json").read_text()), \
        "regenerated certificate differs from the committed one"
    print("[regenerate] certificate.json reproduced exactly from the vendored pins")

    pr184 = load(HERE / "references/pr184/assemble_profiles.py", "verify_pr184")
    bit_cert = json.loads((HERE / "inputs/pr200-bit-certificate.json").read_text())
    complex_cert = json.loads((HERE / "references/pr194/certificate.json").read_text())
    row = bit_cert["bit"]["profile"]
    coarse = Q(record["bit_coarse_saving"])
    legacy = Q(record["legacy_leaf"])
    depths = record["depths"]
    best_depth = max(depths, key=lambda d: Q(depths[d]["kappa"]))
    best = Q(depths[best_depth]["kappa"])

    # 3. The suppliers are the ones the certificate names.
    assert Q(record["complex_supplier"]["saving"]) == Q(complex_cert["complex_saving"])
    assert Q(complex_cert["kappa"]) == PR194_KAPPA, "PR194 reference"
    assert all(depths[d]["binding"] == "bit" for d in depths), "the bit branch must bind"
    assert all(Q(depths[d]["kappa"]) <= best for d in depths), "best is not the maximum"
    print("[pins] complex saving = {} (PR194 as published, kappa {}), binding branch = bit at "
          "every depth".format(record["complex_supplier"]["saving"], PR194_KAPPA))

    # 4. The depth-0 row must equal what PR200 announced for this composition.
    assert Q(depths["0"]["kappa"]) == PR200_LEGACY_KAPPA, "PR200 announced legacy value"
    assert depths["0"]["binding"] == "bit"
    print("[cross-check] depth 0 kappa = {} equals PR200's announced value for this "
          "composition".format(PR200_LEGACY_KAPPA))

    # 5. PR184's grid legacy leaf against PR200's published atom wrapper. The two
    #    suppliers define the same wrapper at different precision, so the control is
    #    what the difference does to the price: exactly one grid step at depth 0, and
    #    nothing at all once the wrapper is bootstrapped. PR184's select() is the
    #    pricing path the record's assembly is defined with, so the record uses it.
    complex_row = pr184.select(pr184.normalize(complex_cert["complex_profile"]))
    bit_row = pr184.select(pr184.normalize(row), True)
    assert Q(bit_row["saving"]) == coarse and Q(bit_row["effective_saving"]) == legacy

    def price(leaf):
        boot = dict(bit_row)
        boot["effective_saving"] = Q(leaf)
        return Q(pr184.assemble(complex_row, boot, HERE / "references/pr168-v4",
                                HERE / "references/pr184/FINITE_BRIDGE.txt")["kappa"])

    published_leaf = (1 - PR200_THETA) * PR200_A0 + PR200_THETA * OLD
    assert 0 < published_leaf - legacy < Q(1, GRID), "legacy leaf disagreement"
    assert price(published_leaf) - price(legacy) == Q(1, GRID), "one grid step at depth 0"
    alternative = [published_leaf]
    for _ in range(int(best_depth)):
        alternative.append((1 - coarse) * coarse + coarse * alternative[-1])
    assert price(alternative[-1]) == best, "the bootstrapped price must not depend on the start"
    print("[cross-check] PR184 legacy leaf {:.15g} vs PR200 published {:.15g} (delta {:.3g}): "
          "one grid step at depth 0, identical at depth {}".format(
              float(legacy), float(published_leaf), float(published_leaf - legacy), best_depth))

    # 6. The standing claim, the ceiling, and the exhaustion of pricing.
    assert best > PR197_KAPPA, "does not beat the standing claim"
    assert best > PR200_LEGACY_KAPPA, "does not beat the unbootstrapped composition"
    assert best > PR194_KAPPA
    ceiling = Q(record["ceiling"])
    assert best <= ceiling < best + Q(1, GRID), "not within one grid unit of the ceiling"
    assert Q(depths["1"]["kappa"]) < best == Q(depths["2"]["kappa"]), "depth 2 is not the claim"
    print("[claim] kappa = {} ({:.15g}) at depth {}; vs #197 {:+.4f}%, vs PR200 announced "
          "{:+.4f}%".format(best, float(best), best_depth,
                            float(best / PR197_KAPPA - 1) * 100,
                            float(best / PR200_LEGACY_KAPPA - 1) * 100))
    print("[ceiling] C/(1+C) = {:.15g}; the claim sits {:.3g} below it, under one grid unit "
          "({:.1g})".format(float(ceiling), float(ceiling - best), 1 / GRID))

    # 7. The finite-leaf tolls, recomputed independently in closed form.
    assert legacy < coarse < 1 - coarse, "coarse saving must be a strict leaf toll"
    chain = [legacy]
    for _ in range(int(best_depth)):
        chain.append((1 - coarse) * coarse + coarse * chain[-1])
    assert chain[-1] == coarse - coarse ** int(best_depth) * (coarse - legacy)
    for i in range(1, len(chain)):
        assert chain[i - 1] < chain[i] < coarse < 1 - chain[i], "strict paid tolls"
    assert Q(depths[best_depth]["leaf"]) == chain[-1], "recorded leaf"
    print("[tolls] a_0 < a_1 < ... < a_{} < C < 1 - a_{}".format(best_depth, best_depth))

    # 8. The assembly's minimum margin must be that closed form, and the next grid
    #    point must lie beyond it, so no finer leaf can buy another grid step.
    eta, stop = Q(1, 10 ** 8), Q(1, 10 ** 9)
    q = chain[-1] * (1 - 2 * eta)
    minimum = (1 - eta) * q / (1 + q)
    assert Q(depths[best_depth]["minimum_margin"]) == minimum, "recorded minimum margin"
    assert minimum < best + Q(1, GRID), "the next grid point is inside the minimum margin"
    print("[adjacent grid] minimum margin = {:.15g} lies in (kappa, kappa + 1e-10)".format(
        float(minimum)))

    # 9. Corruption controls, each of which must be refused.
    def accept_only_a_better_composition():
        assert PR200_LEGACY_KAPPA > best, "the unbootstrapped value must not reach the claim"

    rejected = [
        rejects("bit profile with a perturbed W",
                lambda: pr184.normalize(dict(row, W_per_vertex=row["W_per_vertex"] + 1))),
        rejects("leaf at or above the coarse saving",
                lambda: tolls(coarse, coarse + Q(1, GRID))),
        rejects("unbootstrapped depth-0 value offered as the claim",
                accept_only_a_better_composition),
    ]
    print("[controls] rejected: " + ", ".join(rejected))

    # 10. The lever model: what the next word-side move is worth. It must reproduce the
    #     three published values it can be checked on, and it must stay a model.
    lever_out = WORK / "levers.json"
    if lever_out.exists():
        lever_out.unlink()
    subprocess.run([sys.executable, "-B", str(HERE / "levers.py"), "--out", str(lever_out)],
                   check=True, stdout=subprocess.DEVNULL)
    levers = json.loads(lever_out.read_text())
    assert levers == json.loads((HERE / "levers.json").read_text()), "levers.json drift"
    for item in levers["validations"]:
        assert Q(item["relative_error"]) < Q(1, 10 ** 11), item["name"]
    banked = levers["pr200_banked"]
    assert Q(banked["W_per_vertex"]) == Q(56402, 3), "banked stock"
    assert Q(banked["ceiling"]) / Q(levers["claim"]["kappa"]) - 1 > Q(1, 200), "lever too small"
    assert levers["status"].startswith("MODELLED"), "the lever must not be presented as built"
    print("[levers] three published values reproduced to {:.1e}; banking the rank-60 "
          "exterior corrections is worth {:+.4f}% of kappa ({:.10g} -> {:.10g}), which "
          "this package models and does not build".format(
              max(float(Q(i["relative_error"])) for i in levers["validations"]),
              float(levers["gain_vs_claim"]) * 100,
              float(Q(levers["pr200_unpacked"]["ceiling"])),
              float(Q(banked["ceiling"]))))
    print("PASS composed-diagonal-bit-bootstrap kappa = {} at depth {}; 47 strict constraints "
          "and 7 margins per depth".format(best, best_depth))


if __name__ == "__main__":
    main()
