#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Relocate exact #7113 sources and run the signed 180-CLEAR application."""

import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import inspect
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import time


HEAD = "7e68d8dd62d9a38c0f3c942262a7a85ca7125b75"
SOURCE = "9ea1dab98cbd532af75ab780f284c513534d5df13fa366c3241a08a36c3610f8"
CANDIDATE = "5f555d6bb6736eb0c98826d9822f077ce1cbc6875c46b0c10731737665dbda6e"
B = "2ea3a954f053b4cec96f1b03830353b79c32bb74160a023b96e40872759ad560"
CALLER = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
PACKAGER = "af3b332298c24e6fd9d536d4aefc0fc9883d1d87b9121654f87c7d4cf8e6dbcd"
CLOSURE = "0867688e8dcf88a9d101e0a74f0bc673773b3d1df1360b81a63e6fa3bdfd622d"
OBSERVED = "2ae6b56b5338e824e31851e828a087b17e493641d51375c23f996b3c06c25754"
BASE_INVOICE = "18adee673515c4ece7208b53c7cc17a2e121843d55f62067d2e43e341872f0d5"
B_INVOICE = "f6fcd020e866625c4c10a40513f30dd368fa7adb7573b539d684580fadebe7ee"
B_BRACKET = ["0.0036810345257", "0.0036810345258"]
SCOPE = "fresh-signed-7636-lowered-c"


def require(test, message):
    if not test:
        raise ValueError(message)


def digest(raw):
    return sha256(raw).hexdigest()


def read(path, pin):
    raw = path.read_bytes()
    require(digest(raw) == pin, f"SHA-256 mismatch: {path.name}")
    return raw


def write(path, obj):
    with path.open("x") as stream:
        json.dump(obj, stream, sort_keys=True, indent=2)
        stream.write("\n")


def verify_native_and_clear(spec, inputs, w, source, life):
    native = json.loads(inputs["native_result"])
    mark = json.loads(inputs["native_receipt"])
    checked = binding_controls(spec, mark, native, digest(inputs["native_result"]))
    for name in ("walsh", "authorization"):
        require(mark[name + "_sha256"] == digest(inputs["native_" + name]), f"low native custody: {name}")
    build = json.loads(inputs["clear_result"])
    require(build["status"] == "PASS_7636_MATCHED_SCALAR_LOWERING_BUILD"
            and build["source_head"] == native["head"] == spec["source_head"] and native["pr"] == 7636
            and native["status"] == "PASS_7636_LOWERED_C_NATIVE", "matched lowering and actual low native result")
    for role, key, cert_key, word in (("source", "source_word", "source_clear", source),
                                      ("candidate", "word", "candidate_clear", w)):
        frozen = build[role]
        word_bytes, cert_bytes = inputs[key], inputs[cert_key]
        checks = {"canonical_sha256": digest(canonical(word)), "raw_sha256": digest(gzip.decompress(word_bytes)),
                  "gzip_sha256": digest(word_bytes), "clear_sha256": digest(cert_bytes)}
        require(all(frozen[k] == native[role][k] == v for k, v in checks.items())
                and frozen["events"] == len(word["program"]), f"native/word/CLEAR custody for {role}")
        certs = json.loads(cert_bytes)["clear_event_index"]
        clocks = [str(i) for i, row in enumerate(word["program"]) if row[0] == "CLEAR"]
        require(life == len(clocks) == len(certs) == 180 and set(certs) == set(clocks), "exact CLEAR inventory")
    route = native["route_columns"]
    require(route["all_forward"] == route["all_adjoint"] == 512 and route["wrong_phase"] == "rejected"
            and sum(len(block["composed_paths"]) for block in route["blocks"].values()) == 4,
            "fresh exact composed paths and wrong phase")
    finite = native["finite_replays"]
    require({(r["prime"], r["seed"]) for r in finite} == {(1000000009, 11), (998244353, 37)} and len(finite) == 2
            and all(r["endpoint_rows"] == 1501 and r["owned_zero_rows"] == 68 and r["source"]["clears"] == 180
                    and r["candidate"]["clears"] == 180 for r in finite), "both finite physical oracles")
    return checked


def bind_scope(spec, inputs):
    require(spec["source_pr"] == 7636 and spec["source_head"] == HEAD and spec["source_canonical_sha256"] == SOURCE
            and spec["candidate_canonical_sha256"] == spec["candidate_raw_sha256"] == CANDIDATE
            and spec["paid_positions"] == 109618, "frozen 180-CLEAR signed scope")
    require(digest(inputs["source_invoice"]) == BASE_INVOICE and digest(inputs["public_b_invoice"]) == B_INVOICE,
            "exact raw source invoice and public low-B comparator invoice")
    require(spec["public_b_bracket"] == B_BRACKET and Fraction(spec["claim"]) > Fraction(B_BRACKET[1]),
            "public same-family gain")
    independent = json.loads(inputs["independent_pair"])["source"]
    require(independent["head"] == HEAD and independent["literal_sha256"] == B
            and independent["price"]["kappa"] == B_BRACKET
            and independent["full_signed_invoice"] == json.loads(inputs["public_b_invoice"]),
            "independent lowered B invoice agrees with the public B price comparator")
    build = json.loads(inputs["clear_result"])
    for role, key in (("source", "source_word"), ("candidate", "word")):
        result = json.loads(inputs[role + "_resource_result"])
        finished = json.loads(inputs[role + "_resource_exit"])
        require(result["status"] == "PASS_LOWERED_7636_RESOURCE" and result["case"] == role
                and result["source_head"] == HEAD and result["caller_sha256"] == CALLER,
                f"fresh lowered {role} resource result")
        require(finished["status"] == "COMPLETE" and finished["result_sha256"] == digest(inputs[role + "_resource_result"]),
                f"guarded resource completion: {role}")
        case = build[role]
        require(result["canonical_sha256"] == case["canonical_sha256"] and digest(inputs[key]) == case["gzip_sha256"],
                f"exact lowered {role} resource word")
        prefix = "source_" if role == "source" else ""
        for filename, suffix in (("GRID.json", "grid"), ("ORDINARY.json", "ordinary"), ("TARIFF.json", "tariff"),
                                 ("LITERALS.json", "literals"), ("TAPE-SCALAR.json", "tape_scalar")):
            require(result["receipts"][filename] == digest(inputs[prefix + suffix]), f"resource receipt {role}/{filename}")
        require(result["ordinary_upper"] < 10**9 and result["context"] <= 4096, "retained resource caps")


def adapt_driver(driver):
    run = driver / "run.py"
    original = run.read_text()
    start = original.index("def verify_native_and_clear(")
    stop = original.index("def verify_grid(", start)
    source = original[:start] + inspect.getsource(verify_native_and_clear) + "\n\n" + original[stop:]
    replacements = [
        ("    head, raw_sha, zip_sha, life, entrance = SOURCE_PINS[pr]\n",
         "    require(pr == 7636, 'exact low branch')\n"
         "    head, _, _, life, entrance = SOURCE_PINS[pr]\n"
         f"    raw_sha, zip_sha = {SOURCE!r}, spec['inputs']['source_word']['sha256']\n"),
        ('    independent = json.loads(inputs["independent_pair"])\n',
         '    independent = json.loads(inputs["independent_pair"])\n'
         '    independent = {**independent, "source": independent["matched_lowered_7636"]}\n'),
        ('    write(work / "PRICE-OUTER.json", cost)\n',
         '    low_b = json.loads(inputs["public_b_invoice"])\n'
         '    b_cost = capture_price({**spec, "source_bracket": spec["public_b_bracket"]}, low_b, source_invoice | new)\n'
         '    require(b_cost["gate"] == cost["gate"], "same outer predicates with both comparators")\n'
         '    write(work / "PRICE-OUTER.json", {**cost, "public_low_B": b_cost})\n'),
        ('"price_outer": cost["gate"],', '"price_outer": cost["gate"], "public_low_B_comparison": b_cost,'),
    ]
    for old, new in replacements:
        require(source.count(old) == 1, f"exact driver adaptation anchor: {old.strip()}")
        source = source.replace(old, new)
    compile(source, str(run), "exec")
    run.write_text(source)


def run_signed(core, out, config, spec, go, expected):
    annex = core / "application-evidence" / "signed-replay"
    read(annex / "replay.py", PACKAGER)
    read(annex / "data" / "SOURCE-CLOSURE.json", CLOSURE)
    read(annex / "data" / "OBSERVED.json", OBSERVED)
    packager = runpy.run_path(str(annex / "replay.py"))
    driver, _ = packager["materialize"](out, core)
    adapt_driver(driver)
    resolved = {role: {**ref, "path": str((config.parent / ref["path"]).resolve())}
                for role, ref in spec["inputs"].items()}
    inputs = {role: read(Path(ref["path"]), ref["sha256"]) for role, ref in resolved.items()}
    bind_scope(spec, inputs)
    write(out / "SPEC.json", {**spec, "inputs": resolved})
    write(out / "GO.json", {**go, "scope": "fresh-signed-caller-outer", "source_head": HEAD,
                             "candidate_canonical_sha256": spec["candidate_canonical_sha256"],
                             "spec_sha256": digest((out / "SPEC.json").read_bytes()),
                             "driver_files": {p.name: digest(p.read_bytes()) for p in driver.glob("*.py")}})
    work = driver / "application"
    subprocess.run([sys.executable, "-I", "-B", str(driver / "run.py"), "--spec", str(out / "SPEC.json"),
                    "--go", str(out / "GO.json"), "--work", str(work)], cwd=driver, check=True)
    raw = (work / "RESULT.json").read_bytes()
    receipt = json.loads((work / "EXIT.json").read_bytes())
    result = json.loads(raw)
    require(receipt["status"] == "COMPLETE" and receipt["result_sha256"] == digest(raw)
            and result["status"] == "PASS_FRESH_SIGNED_CALLER_CONDITIONAL_COMPONENTS"
            and result["clear_lifetimes"] == 180 and result["ordinary"]["model_total"] < 10**9,
            "exact fresh low signed completion")
    scientific = packager["normalize_result"](result)
    # These three copies carry input-receipt hashes. The driver checks their
    # exact contents on each run, including a replay with newly timed receipts.
    working = scientific["source_copy_pins"]
    for path in ("replay/supplier7112/short-caller/BOUND-NATIVE-GRID.json",
                 "replay/supplier7112/short-caller/INGREDIENT-INPUT.json", "replay/supplier7112/RESULT.json"):
        del working[path]
    if expected is not None:
        require(scientific == json.loads(expected.read_bytes()), "normalized offline science differs")
    write(out / "NORMALIZED-RESULT.json", scientific)
    write(out / "REPLAY-RESULT.json", {"status": "PASS_PORTABLE_7636_LOWERED_C_SIGNED_APPLICATION",
                                       "candidate": spec["candidate_canonical_sha256"], "claim": spec["claim"],
                                       "catalogue_size": result["catalogue_size"], "result_sha256": digest(raw),
                                       "normalized_result_sha256": digest((out / "NORMALIZED-RESULT.json").read_bytes())})
    print("PASS_PORTABLE_7636_LOWERED_C_SIGNED_APPLICATION", spec["candidate_canonical_sha256"],
          "kappa=" + spec["claim"], f"catalogue_maps={result['catalogue_size']}", flush=True)


def main():
    require(sys.version_info[:2] == (3, 12) and sys.flags.isolated and sys.dont_write_bytecode and __debug__,
            "use Linux Python 3.12 -I -B with assertions")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--core", type=Path, required=True, help="retained #7660 package root")
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--go", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--expected", type=Path, help="compare a normalized prior result")
    args = parser.parse_args()
    config = args.spec.resolve()
    spec_bytes = config.read_bytes()
    spec = json.loads(spec_bytes)
    out = args.out.resolve()
    out.mkdir(exist_ok=False)
    write(out / "START-GUARD.json", {"started": datetime.now(timezone.utc).isoformat(), "scope": SCOPE,
                                     "spec_sha256": digest(spec_bytes),
                                     "candidate_canonical_sha256": spec["candidate_canonical_sha256"],
                                     "adapter_sha256": digest(Path(__file__).read_bytes())})
    try:
        limit = time.monotonic() + 120
        while not args.go.exists():
            require(time.monotonic() < limit, "signed authorization guard expired")
            time.sleep(0.2)
        go = json.loads(args.go.read_bytes())
        require(go["scope"] == SCOPE and go["status"] == "GO" and go["spec_sha256"] == digest(spec_bytes)
                and go["public_claim"] and go["event_id"] and go["receipt_id"], "recorded low signed authorization")
        require(go["cpu"] in os.sched_getaffinity(0) and 150 <= go["wall_seconds"] <= 900,
                "one available CPU and bounded signed gate")
        run_signed(args.core.resolve(), out, config, spec, go, args.expected)
    except BaseException as failure:
        write(out / "EXIT.json", {"ended": datetime.now(timezone.utc).isoformat(), "status": "INCOMPLETE",
                                   "failure": repr(failure)})
        raise
    write(out / "EXIT.json", {"ended": datetime.now(timezone.utc).isoformat(), "status": "COMPLETE",
                               "result_sha256": digest((out / "REPLAY-RESULT.json").read_bytes())})


if __name__ == "__main__":
    main()
