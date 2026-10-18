#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared for Ali Romman with substantial OpenAI Codex assistance.
"""Check source coverage and favorable directions outside the catalogue."""

import argparse
import copy
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("owner_bound", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def fail_for(action, reason):
    try:
        action()
    except ValueError as error:
        V.need(str(error) == reason, "control failed for the wrong reason: " + str(error))
    else:
        raise ValueError("control was accepted: " + reason)


def run():
    frozen = V.read(HERE / "CATALOGUE.json")
    actual = V.read_catalogue_sources(V.ROOT, frozen["sources"])
    V.validate_catalogue(frozen, actual)
    results = []

    def catalogue_control(name, change, reason):
        damaged = copy.deepcopy(frozen)
        change(damaged)
        fail_for(lambda: V.validate_catalogue(damaged, actual), reason)
        results.append(dict(name=name, rejection=reason))

    catalogue_control("missing_provider", lambda d: d["records"].pop(),
                      "catalogue record coverage mismatch")
    catalogue_control("provider_aliased_to_wrong_interface",
                      lambda d: d["records"][0].update(interface=d["records"][-1]["interface"]),
                      "catalogue record coverage mismatch")
    catalogue_control("missing_source", lambda d: d["sources"].pop(next(iter(d["sources"]))),
                      "catalogue source set or hash mismatch")
    catalogue_control("source_hash_changed",
                      lambda d: d["sources"].update({next(iter(d["sources"])): "0" * 64}),
                      "catalogue source set or hash mismatch")

    def change_profile(data):
        profile = data["interfaces"][0]["profile"]
        profile["1"] -= 2
        profile["2"] += 1

    catalogue_control("mass_preserving_profile_change", change_profile,
                      "catalogue cost interface mismatch")
    pins = V.read(HERE / "DEPENDENCIES.json")
    claim = V.read(V.ROOT / pins["roles"]["selected_claim"])
    engine = V.load_engine(V.ROOT, pins["roles"]["mercator"], "control_mercator")
    lo = Q(claim["complex_lower"])
    values = V.phi_values(engine, "mercator", lo, lo + Q(1, 10**24), range(1, 49))
    base_id = next(row["interface"] for row in frozen["records"]
                   if row["source"] == "research/complex-t21-owners/data/SPEC.json")
    baseline = next(row for row in frozen["interfaces"] if row["id"] == base_id)
    improved = copy.deepcopy(baseline)
    improved["id"] = "U10-profile-direction"
    for r, n in (("3", 4), ("4", -8), ("5", 4)):
        improved["profile"][r] += n
    gain = V.interval(V.reduced_form(improved, baseline), values)
    V.need(gain[1] < 0, "U10 direction is not certified favorable")
    fail_for(lambda: V.certify_providers([baseline, improved], baseline, values),
             "favorable or unresolved provider: U10-profile-direction")
    results.append(dict(name="favorable_new_provider_is_rejected", interval=list(map(str, gain)),
                        scope="The PR987 profile delta is a numerical direction. This control does not admit its program or owners."))
    leavers = [
        ("R489", "gauge44-leaver", "98fa99dbe6ceb58d6d5ad40974e18cd29c1bf1cf6aaf1e155f53a85d9e92078a",
         {"1": 2463, "2": 388, "3": 429, "4": 166, "5": 70, "8": 8},
         {"4": 65, "5": 32, "7": 39, "8": 122, "9": 231}),
        ("R480", "gauge44-leaver8", "1208c7c3ae84c158c21b80d69f0f448d376680a7d37e15d0abc77541d3cd61d8",
         {"1": 2412, "2": 418, "3": 418, "4": 170, "5": 68, "8": 8},
         {"4": 56, "5": 32, "7": 30, "8": 122, "9": 240}),
    ]
    for label, package, digest, profile, inventory in leavers:
        leaver = dict(id=label + "-outside-base", profile=profile, inventory=inventory)
        leaver_gain = V.interval(V.reduced_form(leaver, baseline), values)
        V.need(leaver_gain[1] < 0, label + " direction is not certified favorable")
        fail_for(lambda: V.certify_providers([baseline, leaver], baseline, values),
                 "favorable or unresolved provider: " + leaver["id"])
        results.append(dict(name=label + "_new_inventory_breaks_the_catalogue_bound",
                            interval=list(map(str, leaver_gain)), interface=leaver,
                            source_commit="779e80aef469bc3a28b19f1adde199871a9a22e3",
                            source_path="research/" + package + "/data/SPEC.json",
                            source_sha256=digest,
                            scope="This cost vector is outside the base catalogue. No program or owner admission is claimed."))
    bad_bin = V.interval(V.bin_form(1, 20), values)
    V.need(bad_bin[1] < 0, "an excessive rank-one signed price was accepted")
    results.append(dict(name="rank_one_credit_above_19_breaks_support", interval=list(map(str, bad_bin))))

    with tempfile.TemporaryDirectory(prefix="owner-bound-controls-") as directory:
        work = Path(directory)
        source = next(iter(frozen["sources"]))
        fixture = work / "source-fixture"
        target = fixture / source
        target.parent.mkdir(parents=True)
        shutil.copyfile(V.ROOT / source, target)
        small = json.loads(json.dumps(V.read_catalogue_sources(fixture, [source])))
        extra = fixture / "research/new-provider/data/SPEC.json"
        extra.parent.mkdir(parents=True)
        extra.write_text('{"providers":{"new-interface":{}}}\n', encoding="utf-8")
        V.validate_catalogue(small, V.read_catalogue_sources(fixture, small["sources"]))
        report = V.audit_current_tree(fixture, small)
        V.need(report["status"] == "ADDITIONAL_RECORDS_OUTSIDE_BOUND"
               and report["additional_records"] == [dict(source="research/new-provider/data/SPEC.json",
                                                         provider="new-interface")]
               and not report["changed_sources"], "later source growth was not kept outside the bound")
        results.append(dict(name="later_source_growth_is_reported_not_admitted", report=report))
        target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        fail_for(lambda: V.validate_catalogue(small, V.read_catalogue_sources(fixture, small["sources"])),
                 "catalogue source set or hash mismatch")
        V.need(V.audit_current_tree(fixture, small)["changed_sources"] == [source],
               "source drift was not distinguished from source growth")
        results.append(dict(name="existing_source_drift_is_rejected", source=source))
        rejected = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "verify.py"),
                                   "--out", str(work / "optimized.json")],
                                  capture_output=True, text=True, check=False)
        V.need(rejected.returncode != 0 and "retained outer arithmetic requires assertions" in rejected.stderr,
               "optimized primary did not reject for the required reason")
        results.append(dict(name="optimized_primary_rejected", returncode=rejected.returncode))
        accepted = subprocess.run([sys.executable, "-I", "-O", "-B", str(HERE / "independent_check.py"),
                                   "--out", str(work / "independent.json")],
                                  capture_output=True, text=True, check=False)
        V.need(accepted.returncode == 0 and "PASS_INDEPENDENT_INTEGER_MIXTURE_DUAL" in accepted.stdout,
               "optimized independent check failed: " + accepted.stderr)
        results.append(dict(name="optimized_independent_check_passed", returncode=accepted.returncode))
        retained = work / "retain.json"
        retained.write_text("retained evidence\n", encoding="utf-8")
        preserved = subprocess.run([sys.executable, "-B", str(HERE / "verify.py"),
                                    "--out", str(retained)], capture_output=True, text=True, check=False)
        V.need(preserved.returncode != 0 and "output exists; choose a new file" in preserved.stderr
               and retained.read_text(encoding="utf-8") == "retained evidence\n", "existing evidence was not preserved")
        results.append(dict(name="existing_output_preserved", returncode=preserved.returncode))
    return dict(status="PASS_HETEROGENEOUS_OWNER_CONTROLS", cases=results)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    V.need(not args.out.exists(), "output exists; choose a new file")
    result = run()
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], "cases=" + str(len(result["cases"])))


if __name__ == "__main__":
    main()
