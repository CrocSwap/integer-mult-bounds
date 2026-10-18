"""Replay the frozen nine-stage owner plan for both words, then compare invoices.

Adapted from Ali Romman / PR688 by Alluri with substantial OpenAI Codex assistance.
Apache-2.0. All inherited emitters, owner auditors and invoice engines are unchanged.
Uses the unchanged PR543 / PR510 / PR463 / PR442 verification chain.
"""
import json
import shutil
import subprocess
import sys


def run(root, out):
    package = root / "research/e8-bit-r420"
    predecessor = root / "research/e8-bit-carrier-skeleton"
    price = package / "vendor/pr510/e8-r480-nine-stage"
    code = price / "vendor/e8-r715-eleven-stage-whole/code"
    python = [sys.executable, "-B"]
    results = {}
    saving = json.loads((out / "LOCAL.json").read_text())["saved_additions"]

    def call(name, command):
        print("RUN", name, flush=True)
        with (out / (name + ".log")).open("w") as log:
            subprocess.run(list(map(str, command)), check=True, stdout=log, stderr=subprocess.STDOUT)

    geometry = out / "geometry"
    call("geometry", python + [predecessor / "code/nine/geometry.py", "--source", predecessor, "--out", geometry])
    # Geometry's only runtime field is excluded before it is hashed into the
    # generated template. Preserve every proof-relevant field and rebind hashes.
    gp = geometry / "GEOMETRY.json"
    geometry_data = json.loads(gp.read_text())
    geometry_data.pop("seconds")
    gp.write_text(json.dumps(geometry_data, sort_keys=True, indent=2) + "\n")
    call("parent-audit-adapter", python + [price / "code/adapt.py", code, out / "adapted"])
    for name in ("baseline", "replacement"):
        base = out / name
        parent = base / "nine"
        parent.mkdir()
        shutil.copy2(geometry / "GEOMETRY.json", parent / "GEOMETRY.json")
        word = out / (name + ".json.gz")
        call(name + "-parent", python + [code / "global_k.py", "--word", word,
             "--local-check", base, "--out", parent, "--isometries", predecessor / "data/eleven/residual-isometries.json"])
        call(name + "-parent-audit", python + [out / "adapted/audit_parent_k.py",
             "--word", word, "--local-check", base, "--out", parent])
        hosted = base / "hosted"
        call(name + "-hosted", python + [code / "emit_k.py", parent, base, hosted,
             "--selection", package / "data/selection9-r420.json", "--key", "bit"])
        call(name + "-hosted-audit", python + [code / "audit_hosted_k.py", base, hosted, hosted / "AUDIT.json"])

        # The unchanged pr484 price is a historical arithmetic control only.
        # No complex construction is replayed or selected by this command.
        call(name + "-invoice", python + [price / "code/assemble9.py", base, hosted,
             hosted / "AUDIT.json", predecessor, base / "PRICE.json", "pr484"])
        pg = json.loads((parent / "GLOBAL.json").read_text())
        parent_audit = json.loads((parent / "AUDIT.json").read_text())
        audit = json.loads((hosted / "AUDIT.json").read_text())
        invoice = json.loads((base / "PRICE.json").read_text())
        if (parent_audit["status"] != "PASS_INDEPENDENT_COMPRESSED_BIT_TEMPLATE_AUDIT"
                or audit["status"] != "PASS_INDEPENDENT_REPLICATED_HOSTING_AUDIT"
                or invoice["status"] != "PASS_NINE_STAGE_WHOLE_HOSTED_BIT_PRICE_AND_CITED_ASSEMBLY"):
            raise ValueError("Hosted verification did not pass")
        if audit["hosted_residuals"] != 120960 or audit["bank_assignments"] != 0:
            raise ValueError("Whole-owner inventory changed")
        if len(parent_audit["mutations_rejected"]) != 17 or len(audit["mutations_rejected"]) != 16:
            raise ValueError("Incomplete inherited mutation coverage")
        results[name] = {"parent_mutations": parent_audit["mutations_rejected"], "hosted_audit": audit,
                         "bit_lower": invoice["bit_lower"], "bit_lower_decimal": invoice["bit_lower_decimal"],
                         "invoice": invoice["bit"], "global_prefix_bound": pg["global_prefix_bound"],
                         "bit_profile": invoice["bit_profile"], "local_additions": pg["local_additions"]}
    old, new = results["baseline"], results["replacement"]
    if old["bit_profile"] != new["bit_profile"] or old["bit_lower"] != new["bit_lower"]:
        raise ValueError("The recursive profile or bit exponent changed")
    if new["bit_lower_decimal"] != "0.001653826988146798944268":
        raise ValueError("The original R420 bit price was not reproduced")
    if old["hosted_audit"]["emitted_events"] - new["hosted_audit"]["emitted_events"] != 288 * saving:
        raise ValueError("Wrong physical instruction saving")
    # Reprice the changed positive envelope. A larger raw prefix is not inherited
    # for free: assemble9 recomputes both rounded charges from the actual word.
    changing = {"prefix_bits", "charged_prefix_bits", "coefficient_bits", "two_level_coefficient_bits"}
    if ({k: v for k, v in old["invoice"].items() if k not in changing}
            != {k: v for k, v in new["invoice"].items() if k not in changing}):
        raise ValueError("A non-prefix finite invoice field changed")
    for result in results.values():
        invoice = result["invoice"]
        if (invoice["prefix_bits"] != int(result["global_prefix_bound"]).bit_length()
                or invoice["charged_prefix_bits"] < invoice["prefix_bits"]
                or invoice["charged_two_level_coefficient_bits"] < invoice["two_level_coefficient_bits"]):
            raise ValueError("Insufficient fresh precision invoice")
    return results
