"""Rebuild pinned U8 + A promotions and sweep a bounded cleanup move class.

Liamia supplied theoretical guidance and corrections; OpenAI Codex performed
the concrete implementation and verification. Public predecessor credits are
retained in vendor/pr869 and NOTICE.md. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
import contextlib
import gzip
import hashlib
import io
import json
from pathlib import Path

import experiment as E
import retiming as R

VENDOR = E.HERE / "vendor/pr869"
VENDOR_FILES = {
    "build_tri.py": ("11c43711144a98224d0bc166f217e9ae996ffeb2", "0fba65b31c2fd71864c291358bb0ad8d5f7e1be07e21df23f0ae73d7b966002e"),
    "RECIPE-U8.json": ("ee215a805a7487c300fe1e2b117bd4b5720d4d24", "292f0e9f82824c4111728cf4de929bf6e43320fbbdc77658aae9681906b0d652"),
    "PROOF-NOTE-BARCH.md": ("8cea5a6846a254a25136f8a53e24bb0ef665a44b", "c24f211b09358b25d6cf47dd18e4bbd8bcf4ecf279e6f1c6c90613cfa230818d"),
    "NOTICE.md": ("698daf7b0e5c05c3c6984da03b7ad843b4a36f7a", "c7e1a8e481b1741d3ee3335a4b8a9e1332dc9774a1b035b922871495a8965cc0"),
}
U8_PROFILE = {1:2548, 2:338, 3:446, 4:162, 5:72, 8:8}
COMBINED_PROFILE = {1:2492, 2:338, 3:446, 4:106, 5:128, 9:8}
IDLE = {1:1, 3:1, 44:1, 48:2396}


def source_inputs(vendor=VENDOR):
    provenance = json.loads((vendor / "SOURCE.json").read_bytes())
    E.require(provenance["commit"] == "73e86f69bf9a391e3c334999f7bbe3825dc42759", "PR869 commit pin")
    E.require(provenance["repository"] == "jeremykothe2/integer-mult-bounds"
              and provenance["upstream_pr"] == "https://github.com/CrocSwap/integer-mult-bounds/pull/869"
              and provenance["license"] == "Apache-2.0", "PR869 provenance")
    inventory = {item["file"]: (item["git_blob"], item["sha256"]) for item in provenance["files"]}
    E.require(len(provenance["files"]) == len(VENDOR_FILES) and inventory == VENDOR_FILES,
              "PR869 pinned source inventory")
    for item in provenance["files"]:
        raw = (vendor / item["file"]).read_bytes().replace(b"\r\n", b"\n")
        E.require(E.digest(raw) == item["sha256"], "vendored input SHA256")
        blob = hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
        E.require(blob == item["git_blob"], "vendored Git blob")
    tri = E.load_module(vendor / "build_tri.py", "credited_pr869_triangle_builder")
    recipe = json.loads((vendor / "RECIPE-U8.json").read_bytes())
    return tri, recipe, provenance


def compose(source, promoted, tri, recipe):
    E.require(E.digest(E.encode(source)) == recipe["base_sha256"], "U8 base word pin")
    u8 = tri.apply(source, recipe)
    inherited_encoding = json.dumps(u8, separators=(",", ":")).encode()
    E.require(E.digest(inherited_encoding) == recipe["expect_sha256"], "reconstructed U8 exact source pin")
    combined = tri.apply(promoted, recipe)
    E.refresh_report(u8); E.refresh_report(combined)
    E.require(E.ints(u8["report"]["local_profile"]) == U8_PROFILE, "U8 profile")
    E.require(E.ints(combined["report"]["local_profile"]) == COMBINED_PROFILE, "combined profile")
    # All proof-relevant scalar and frame data agree whichever disjoint edit
    # family is applied first. This check covers more than profile additivity.
    other_order = deepcopy(u8)
    other_order["A"] = deepcopy(promoted["A"])
    other_order["center_frames"] = deepcopy(promoted["center_frames"])
    E.refresh_report(other_order)
    E.require(other_order == combined, "edit-order commutation")
    actual_delta = Counter(E.ints(combined["report"]["local_profile"]))
    actual_delta.subtract(E.ints(promoted["report"]["local_profile"]))
    E.require({r:n for r,n in actual_delta.items() if n} == {3:16,4:-32,5:16}, "measured U8 delta on promoted base")
    return u8, combined


def audit_word(word, path, receipt):
    E.dump_compressed(path, word)
    with contextlib.redirect_stdout(io.StringIO()):
        E.AUDIT.run(path, receipt)
    E.retain_audit_receipt(receipt)


def control_outcomes(base, tri, recipe, out):
    out.mkdir(parents=True, exist_ok=True)
    outcomes = []
    names = [kind+suffix for kind in ("drop_restore", "restore_full", "drop_preread", "donation_after")
             for suffix in [""]+["@"+str(v["X"]) for v in recipe["variants"]]]
    E.require(len(names) == 36, "36 U8 restoration/order controls")
    for name in names:
        word = tri.apply(base, recipe, name)
        path = out / (name.replace("@", "-")+".json.gz")
        stage = "literal_frame_replay"
        try:
            E.refresh_report(word)
            stage = "independent_all_column_audit"
            audit_word(word, path, out / "unused-control-receipt.json")
        except (ValueError, RuntimeError) as exc:
            outcomes.append(dict(control=name, status="REJECTED", stage=stage, reason=str(exc)))
        else:
            raise ValueError("accepted faulty donation/restore control: "+name)
    return outcomes


def run(out, controls=True):
    E.require(__debug__, "Use normal Python for retained assertion-based engines")
    out.mkdir(parents=True, exist_ok=True)
    source, plan, _ = E.read_source()
    promoted, _ = E.build_word(source)
    tri, recipe, provenance = source_inputs()
    u8, combined = compose(source, promoted, tri, recipe)
    audit_word(u8, out / "U8.json.gz", out / "U8-AUDIT.json")
    audit_word(combined, out / "U8-A48.json.gz", out / "U8-A48-AUDIT.json")
    engines, bit, _ = E.pricing_engines()
    base_price = E.price(E.global_profile(E.NEW_PROFILE, IDLE), engines, bit)
    u8_price = E.price(E.global_profile(U8_PROFILE, IDLE), engines, bit)
    combined_price = E.price(E.global_profile(COMBINED_PROFILE, IDLE), engines, bit)
    E.require(u8_price["outer"]["kappa_decimal"] == "0.001661948695165034", "credited U8 price reproduction")
    E.require(combined_price["outer"]["kappa_decimal"] == "0.00129733659931971", "combined direct price")
    owner_path = E.ROOT / "research/gauge44-frames-x/data/OWNERS.json.gz"
    E.require(E.digest(owner_path.read_bytes()) == E.OWNER_SHA, "retained owner source pin")
    owners = json.loads(gzip.decompress(owner_path.read_bytes()))
    E.require(E.recount_idle(plan, owners, combined) == IDLE, "combined complete role/idle recount")
    print("U8 + A48 exact endpoints and direct cost: PASS", flush=True)
    studies = []
    for name, word in (("X4", source), ("A48", promoted), ("U8-A48", combined)):
        result = R.scan(word)
        evaluated = []
        for number, (profile, representative) in enumerate(result["representatives"].items()):
            candidate = R.candidate(word, representative)
            audit_word(candidate, out / (name+"-retimed-"+str(number)+".json.gz"),
                       out / (name+"-retimed-"+str(number)+"-AUDIT.json"))
            price = E.price(E.global_profile(dict(profile), IDLE), engines, bit)
            evaluated.append(dict(profile=dict(profile), kappa=price["outer"]["kappa_decimal"],
                                  cleanup_index=representative["cleanup_index"], tail_position=representative["tail_position"]))
        baseline = E.price(E.global_profile(word["report"]["local_profile"], IDLE), engines, bit)
        improving = [r for r in evaluated if E.Q(r["kappa"]) > E.Q(baseline["outer"]["kappa"])]
        study = dict(word=name, pool_size=len(result["pool"]), registers=len(result["registers"]),
            candidate_count=len(result["rows"]), classifications=result["categories"],
            distinct_valid_profiles=len(evaluated), improving_profiles=len(improving), evaluated=evaluated)
        if name in {"X4", "A48"}:
            E.require((study["pool_size"], study["registers"]) == (124,219), "124-gate/219-register pool reproduction")
        E.dump_compressed(out / (name+"-RETIMING-CENSUS.json.gz"), dict(
            pool=result["pool"], registers=result["registers"], candidates=result["rows"]))
        studies.append(study)
        print("Retiming", name, "pool", study["pool_size"], "candidates", study["candidate_count"],
              "valid profiles", len(evaluated), "improving", len(improving), flush=True)
    rejected = control_outcomes(promoted, tri, recipe, E.ROOT / "build/roadmap48-controls") if controls else []
    result = dict(status="PASS_U8_COMPOSITION_AND_BOUNDED_CLEANUP_RETIMING", source_pr869=provenance,
        u8_price=u8_price, promoted_base_price=base_price, combined_price=combined_price,
        gain_on_promoted_base=engines[0].decimal(E.Q(combined_price["outer"]["kappa"])-E.Q(base_price["outer"]["kappa"])),
        edit_orders_equal=True, profile_delta={3:16,4:-32,5:16}, helper_widths_unchanged=True,
        roles_recounted=36288, idle=IDLE, retiming_studies=studies,
        rejected_controls=rejected, controls_status="PASS" if controls else "NOT_RUN",
        credits=dict(human="Liamia: theoretical guidance and corrections",
                     assistant="OpenAI Codex: implementation and verification",
                     predecessor="NewBArch donation/restore construction in Jeremy Kothe's PR869 package; source AI disclosures preserved"),
        scope="Exact finite local constructions and direct stated-recurrence prices; no new globally admitted kappa or full multiplication theorem.")
    E.dump(out / "OPTIMIZATIONS.json", result)
    print(result["status"], "gain on A48", result["gain_on_promoted_base"], "controls", len(rejected), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=E.ROOT / "build/roadmap48-optimizations")
    parser.add_argument("--skip-controls", action="store_true", help="Diagnostic only; receipt explicitly records NOT_RUN")
    args = parser.parse_args()
    run(args.out.resolve(), not args.skip_controls)
