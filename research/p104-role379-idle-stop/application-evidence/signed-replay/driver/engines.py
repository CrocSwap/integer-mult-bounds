# SPDX-License-Identifier: Apache-2.0
"""Prior source pins and counted adapters for the actual #7113 entry points."""

from fractions import Fraction
import importlib.util
import json
from pathlib import Path

from guard import digest, patch, read, require, write

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parents[1] / "kappa-7641-successor-20261118"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
CALLER_FREEZE = "ac57680f5a9c2ba97840b3b5bd10f1b7b77db1fe20d54e6197a1e18c08842045"
PINS = {
    "resources/vendor/check_odd_fixed_tape_counts.py": "e6246e9f8fbeae3077d82e585eafd3647c1a8758c58f33c7c13e7efa6c1e42bb",
    "resources/vendor/interval_gate.py": "60a743d13f668ef86db4b8215b4d5d04430a671ba6f1fe06d9c1c4c3dfe86da5",
    "resources/vendor/evaluate_recursive_power.py": "52b20f41fd0bb55fa88dccd6015af2ce358917817b9506720f3e60ce681cc3ad",
    "resources/vendor/compare_recursive_invoices.py": "3930c22c11da7bc6042cfeb6e459ecb06e4478430037bee3469d034353855fc6",
    "resources/fixed/controls.py": "3492500899f8858040bc3c7be5c2de5bf597688318ec314e74eda513ac2e8156",
}
SOURCE_PINS = {
    7658: ("0a0e71c34a5ee5a1b59a8fe7bc6abd35a4d3dd82",
           "fa84fcdecb534700cd00dc81b74889f549a653daa2fb3658cb8142e1eeb9b9e6",
           "dde0a987c2dd9e221208ca5043dfd6e2bdfbb8c4289fa20e2b93fae1696b3ea9", 234, (281, 3)),
    7636: ("7e68d8dd62d9a38c0f3c942262a7a85ca7125b75",
           "98b8c12ece2f323a6ff5cac8c7ed2f78ba3835438ea56b16bd7d4698ec5ad5b2",
           "1b4e33c3e3b69d1f1b42d019a2e372ac612fa28494bd8da18a734618f9bda659", 180, (281, 285)),
}
ASSUMPTIONS = ["native_all_columns", "owned_erasure", "compiler", "precision_tape", "analytic_recovery"]


def verify_sources():
    pins = json.loads(read(PRIOR / "caller/FREEZE.json", CALLER_FREEZE))["files"]
    for rel, pin in pins.items():
        read(PRIOR / "caller" / rel, pin)
    for rel, pin in PINS.items():
        read(PRIOR / rel, pin)
    return pins


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def capture_price(spec, old, new):
    interval = module("signed_interval", PRIOR / "resources/vendor/interval_gate.py")
    dyadic = module("signed_dyadic", PRIOR / "resources/vendor/evaluate_recursive_power.py")
    claim, probe = map(Fraction, (spec["claim"], spec["probe"]))
    lo, hi = map(Fraction, spec["bracket"])
    old_lo, old_hi = map(Fraction, spec["source_bracket"])
    zero = dict(old, paid={}, targets={})

    def check(invo, at, accept):
        hist = {int(r): invo["targets"].get(r, 0) - invo["paid"].get(r, 0)
                for r in invo["targets"].keys() | invo["paid"].keys()}
        bounds = interval.moment(hist, at)
        require((bounds[0] > 0 if accept else bounds[1] < 0), f"Log/exp price at {at}")
        result = dyadic.evaluate(zero, invo, 1 - at, bits=256)
        require(result["classification"] == ("new_cost_lower" if accept else "new_cost_higher"),
                f"Integer-power price at {at}")
        return {"kappa": str(at), "logexp_bounds": interval.show(bounds), "integer_power": result}

    points = {"source_lower": check(old, old_lo, True), "source_upper": check(old, old_hi, False),
              "claim": check(new, claim, True), "probe": check(new, probe, True),
              "lower": check(new, lo, True), "upper": check(new, hi, False)}
    if spec["candidate_canonical_sha256"] != spec["source_canonical_sha256"]:
        require(old_hi < claim and old["targets"] == new["targets"], "Strict gain with equal targets")
        points["source_at_claim"] = check(old, claim, False)
    inv = {"P": {int(r): n for r, n in new["paid"].items()},
           "T": {int(r): n for r, n in new["targets"].items()}}
    gate = interval.gate(inv, claim, probe, lo, hi, spec["bit_pin"])
    require(gate["outer"]["strict_count"] == 54 and gate["outer"]["functional_count"] == 4
            and Fraction(gate["outer"]["minimum_margin"]) > 0, "Complete outer predicates")
    return points | {"gate": gate}


def prepare(spec, inputs, grid, work, pins):
    root = PRIOR / "caller"
    copies = {}
    for rel, pin in pins.items():
        if not rel.startswith("replay/") or ".log" in rel:
            continue
        path = work / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(read(root / rel, pin))
        copies[rel] = pin
    folder = work / "replay/supplier7112/short-caller"
    stale_result = folder.parent / "RESULT.json"
    stale_result.unlink()
    del copies[str(stale_result.relative_to(work))]
    scale = grid["integer_grid"]["odd_scale_lcm"]
    for role, path in (("word", folder.parent / "WORD.json.gz"), ("grid", folder / "BOUND-NATIVE-GRID.json")):
        path.write_bytes(inputs[role])
        copies[str(path.relative_to(work))] = digest(inputs[role])
    adapted = {}
    patch(folder / "emit_odd_type_ab.py", [
        ('invoice=next(x for x in json.loads((root/"SHORT-CALLER-RAW-PRICE.json").read_text())["rows"] if tuple(x["shape"])==shape)',
         'invoice=json.loads((root/"COHORT-PRICE.json").read_text())'),
    ], adapted)
    patch(folder / "check_odd_precision.py", [
        ('previous=json.loads((root/"SHORT-PRECISION.json").read_text())',
         'previous=json.loads((root/"BOUND-NATIVE-GRID.json").read_text())'),
        ('previous["native_sha256"]==sha', 'previous["canonical_word_sha256"]==sha'),
        ('wg=previous["native_grid"]\nwr=previous["rounded_native"]',
         'wg=previous["integer_grid"]\nwr=previous["native_envelope"]'),
        ('+(1125).bit_length()', '+int(wg["odd_scale_lcm"]).bit_length()'),
    ], adapted)
    patch(folder / "check_odd_partial_admission.py", [
        ('previous=json.loads((root/"SHORT-ADMISSION-PARTIAL.json").read_text())\nassert previous["native_sha256"]==digest and not N["bad_inputs"]',
         'actual_native=ind.native(w)\nassert actual_native==N and not N["bad_inputs"], "Fresh native adjoint and inventory"'),
        ('claim=Q(".00363797977")\ntested=claim+Q(7,10**17)',
         f'claim=Q({spec["claim"]!r})\ntested=Q({spec["probe"]!r})'),
        ('g=gate(invoice,claim,tested,*bracket,r["gate"]["BIT_pin"])',
         'g=gate(invoice,claim,tested,*bracket,r["gate"]["BIT_pin"])\n'
         'try:\n    gate(invoice,claim,Q(bracket[0]),*bracket,r["gate"]["BIT_pin"])\n'
         'except AssertionError:\n    crossing_probe_rejected=True\n'
         'else:\n    raise AssertionError("Probe at lower crossing unexpectedly accepted")'),
        ('"scope":"Reuse exact same native word all-column adjoint;',
         '"crossing_probe_rejected":crossing_probe_rejected,"scope":"Fresh changed-native arbitrary-input adjoint;'),
    ], adapted)
    tape = folder / "check_odd_fixed_tape_counts.py"
    read(tape, PINS["resources/vendor/check_odd_fixed_tape_counts.py"])
    patch(tape, [("scalars.append(Q(1125))", f"scalars.append(Q({scale}))"),
                 ("scalars.append(Q(1,1125))", f"scalars.append(Q(1,{scale}))")], adapted)
    controls = work / "controls.py"
    controls.write_bytes(read(PRIOR / "resources/fixed/controls.py", PINS["resources/fixed/controls.py"]))
    patch(controls, [
        ("source=R/'stage'", "source=R/'replay/supplier7112'"),
        ("676c20c53ebd40120903af86bf17c2116f654ab8ce4aa1833f388a2fc400b511", digest(inputs["word"])),
        ("d0d3a2b549a119f9132ad9cdc0c1d75a7bf1daac85435df51921661afb44d76c", digest(tape.read_bytes())),
    ], adapted)
    copies.update({str((folder / name).relative_to(work)): record["adapted_sha256"]
                   for name, record in adapted.items() if name != "controls.py"})
    copies["controls.py"] = adapted["controls.py"]["adapted_sha256"]
    write(work / "ADAPTATION.json", adapted)
    return folder, copies
