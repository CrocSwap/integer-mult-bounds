#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Read-only data audit of one completed PR3044 cold run; no author imports.

This checks actual file bindings and recomputes invoice aggregation, not native
semantics, chronological owner legality, or the analytic release inequalities.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path

SOURCE = "research/rank7-shared-restore-fanin"
SOURCE_PINS = {
    "SOURCES.json": "cecdd18771ced65d3a2c67ef1a4d3b0021f3a0fc639c8dabafe4956462af796e",
    "evidence/BINDINGS.json": "32ca273ea8ab57418fcf35fb73ed7e422b1ef88801f98e3f2ff5ea0faed68ce4",
}
STAGES = ["source-preflight", "export-pr2894", "export-pr2833",
          "fresh-retained-bootstrap", "four-kernel-stage", "preload-stage",
          "parent-paired-stage", "paired-extension-stage", "rank7-overlay-stage",
          "declared-edit-stage", "derive-closed-adapters", "fresh-current-native",
          "complete-admission"]
PROFILE = {1: 1643016, 2: 471528, 3: 159468, 4: 71928,
           5: 13716, 8: 5328, 48: 28190}
LOCAL = {1: 2441, 2: 708, 3: 232, 4: 108, 5: 18, 8: 8}


def need(ok, label):
    if not ok:
        raise ValueError(label)


def sha(path):
    need(path.is_file() and not path.is_symlink(), "regular file: " + str(path))
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def unique(pairs):
    d = {}
    for k, v in pairs:
        need(k not in d, "duplicate JSON key: " + k)
        d[k] = v
    return d


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as stream:
        return json.load(stream, object_pairs_hook=unique)


def histogram(d):
    need(isinstance(d, dict), "histogram object")
    need(all(type(v) is int and v >= 0 for v in d.values()), "histogram counts")
    out = {int(k): v for k, v in d.items()}
    need(len(out) == len(d) and all(k > 0 for k in out), "histogram ranks")
    return out


def safe(root, name):
    p = Path(name)
    need(not p.is_absolute() and ".." not in p.parts, "relative inventory path")
    return root / p


def inventory(root, expected, exclude=()):
    actual = {}
    for p in root.rglob("*"):
        need(not p.is_symlink(), "symlink in source/cache")
        if p.is_file() and p.relative_to(root).as_posix() not in exclude:
            actual[p.relative_to(root).as_posix()] = sha(p)
    need(actual == expected, "complete inventory: " + str(root))
    return len(actual)


def published(repo):
    p = repo / SOURCE
    for name, expected in SOURCE_PINS.items():
        need(sha(p / name) == expected, "pinned publication: " + name)
    for item in read(p / "SOURCES.json")["files"]:
        if item["usage"] == "input":
            need(sha(safe(repo, item["path"])) == item["sha256"], "published input pin")
    bindings = read(p / "evidence/BINDINGS.json")
    for name, expected in bindings.items():
        need(sha(safe(p / "evidence", name)) == expected, "published evidence pin")
    return p


def load(work, repo):
    pub = published(repo)
    run = work / "run"
    strict = run / "candidate/release/verify/strict"
    audit = strict / "global/audit"
    paths = {
        "result": work / "RESULT.json",
        "admission": run / "candidate/RESULT.json",
        "release": run / "candidate/release/RELEASE-RECEIPT.json",
        "native": run / "native/NATIVE-RECEIPT.json",
        "bootstrap": run / "retained/NATIVE-RECEIPT.json",
        "bootstrap_result": run / "retained/RESULT.json",
        "derivation": run / "source-edits-DERIVATION.json",
        "stages": work / "STAGES.json",
        "invoice": audit / "PREFIX-AND-INVOICE.json",
        "owner": audit / "OWNERS-AND-PROFILE.json",
        "controller": audit / "ASYNC-AUDIT.json",
        "idle": audit / "IDLE-REMAINDER-FRAMES.json",
        "independent": strict / "INDEPENDENT.json",
        "assembly": strict / "ASSEMBLY.json",
        "manifest": run / "source-edits/MANIFEST.json",
        "package_manifest": run / "candidate/package/MANIFEST.json",
    }
    # Missing or unfinished output is an error, never an alternate evidence path.
    records = {k: read(p) for k, p in paths.items()}
    observed = {k: sha(p) for k, p in paths.items()}
    observed["source_files"] = inventory(run / "source-edits", records["manifest"], ("MANIFEST.json",))
    observed["admitted_package_files"] = inventory(run / "candidate/package", records["package_manifest"], ("MANIFEST.json",))
    observed["cache_files"] = inventory(run / "native/native-cache", records["native"]["cache_files"])
    need(records["manifest"] == read(pub / "evidence/SOURCE-MANIFEST.json"), "published complete source inventory")
    observed["published_kappa"] = read(pub / "evidence/RESULT.json")["kappa"]
    observed["logs"] = {n: sha(work / (n + ".log")) for n in STAGES}
    observed["allocation"] = {n: sha(work / "pr3015/allocation" / n)
                              for n in ("FILL.json.gz", "ORDER.json", "DISPATCH.json")}
    observed["words"] = {}
    observed["native_files"] = {}
    for tag in ("base", "extra"):
        word = run / f"source-edits/new/borrow/words/BORROW-WORD-43{tag}.json.gz"
        need(read(word) == read(pub / "evidence" / f"WORD-{tag}.json.gz"), "complete published word payload")
        observed["words"][tag] = sha(word)
        ndir = run / "native/native-cache" / sha(word)
        observed["native_files"][tag] = {name: sha(safe(ndir, name))
            for name in records["native"]["providers"][tag]["complete_native_files"]}
    template = strict / "global/hosted/GLOBAL-TEMPLATE.json.gz"
    need(template.is_file() and not template.is_symlink(), "regular hosted template")
    observed["hosted_template_payload_sha256"] = hashlib.sha256(gzip.decompress(template.read_bytes())).hexdigest()
    frames = strict / "global/hosted/IDLE-REMAINDER-FRAMES.json.gz"
    raw = gzip.decompress(frames.read_bytes())
    observed["idle_payload_sha256"] = hashlib.sha256(raw).hexdigest()
    rows = json.loads(raw, object_pairs_hook=unique)
    need(isinstance(rows, list), "literal idle rows")
    counts = Counter()
    for row in rows:
        rank = row["rank"]
        need(type(rank) is int and 0 < rank <= 73, "literal idle rank")
        need(len(row["orthogonal_axes"]) == rank, "literal idle axis count")
        counts[rank] += 1
    observed["idle_recount"] = dict(counts)
    cache = run / "native/native-cache"
    parent_receipts = list((cache / "_receipts").glob("*/RECEIPT.json"))
    need(len(parent_receipts) == 1, "one retained parent receipt")
    pr = parent_receipts[0]
    observed["parent_receipt"] = sha(pr)
    parent = read(pr)
    for name, expected in parent["files"].items():
        need(sha(safe(pr.parent, name)) == expected, "retained parent artifact")
    old = run / "source-edits/vendor/pr1297"
    need(parent["vendor_manifest_sha256"] == sha(old / "MANIFEST.json"), "retained parent source")
    need(parent["claim_sha256"] == sha(old / "CLAIM.json"), "retained parent claim")
    cached_result = read(pr.parent / "RESULT.json")
    need(cached_result["status"] == "PASS_GLOBAL_MIXED_X54_FUSIONS_NATIVE_AND_STRICT_ADMISSION", "retained parent success")
    need(cached_result["kappa"] == read(old / "CLAIM.json")["kappa"], "retained parent endpoint")
    recipe = read(work / "RECIPE.json")
    original = deepcopy(read(run / "PREFLIGHT.json")["commands"])
    allowed = [("declared-edit-stage", "--local-package"),
               ("derive-closed-adapters", "--source-profile"),
               ("derive-closed-adapters", "--source-commit"),
               ("complete-admission", "--source-profile")]
    need([(x["stage"], x["flag"]) for x in recipe["changes"]] == allowed, "four permitted recipe changes")
    for change in recipe["changes"]:
        command = next(c for n, c in original if n == change["stage"])
        i = command.index(change["flag"]) + 1
        need(command[i] == change["old"], "recipe mutation preimage")
        expected = str(work / "parameters") if change["flag"] == "--local-package" else "rank7-shared-restore-fanin"
        need(change["new"] == expected, "recipe mutation target")
        command[i] = expected
    need(original == recipe["commands"], "complete unchanged recipe apart from four fields")
    return records, observed


def validate(r, o):
    a, n, i, b = r["admission"], r["native"], r["invoice"], r["invoice"]["blocknorm"]
    need(r["result"]["status"] == "PASS_SHARED_RESTORE_COMPLETE_RELEASE", "final status")
    need(a["status"] == "PASS_REPLICA_ORDER_FILL_DERIVATIVE_COMPLETE_RELEASE", "admission status")
    need(r["release"]["status"] == "PASS_RELEASE", "release status")
    need(o["source_files"] == a["source_file_count"] == 642, "source file count")
    need(o["admitted_package_files"] == 646, "admitted package file count")
    need(o["manifest"] == a["source_manifest_sha256"] == n["manifest_sha256"]
         == r["result"]["source_manifest_sha256"] == r["derivation"]["manifest_sha256"], "source manifest chain")
    need(a["native_receipt_sha256"] == o["native"], "native receipt chain")
    need(a["release_receipt_sha256"] == r["result"]["release_receipt_sha256"] == o["release"], "release receipt chain")
    need(r["result"]["admission_sha256"] == o["admission"], "admission receipt chain")
    need(a["package_manifest_sha256"] == r["release"]["manifest_sha256"] == o["package_manifest"], "admitted package chain")
    for k in ("result", "admission", "release"):
        q = r[k]["kappa_decimal"] if k == "release" else r[k]["kappa"]
        need(Fraction(q) == Fraction(o["published_kappa"]), "exact published endpoint")
    for field, name in (("fill_sha256", "FILL.json.gz"), ("order_sha256", "ORDER.json"), ("dispatch_sha256", "DISPATCH.json")):
        need(a[field] == o["allocation"][name], "literal allocation binding")
    need([s["stage"] for s in r["stages"]] == STAGES, "complete stage sequence")
    for s in r["stages"]:
        need(s["exit_code"] == 0 and s["log_sha256"] == o["logs"][s["stage"]], "successful bound stage log")
    need(n["fresh_current_provider_count"] == 2 and n["reused_retained_native_count"] == 2
         and n["fresh_retained_native_count"] == 0 and n["reused_retained_parent"] is True
         and n["fresh_retained_parent"] is False, "fresh/reused native accounting")
    need(n["retained_reuse_receipt_sha256"] == o["bootstrap"], "same-run bootstrap receipt")
    need(r["bootstrap_result"]["native_receipt_sha256"] == o["bootstrap"], "bootstrap result receipt")
    need(r["bootstrap"]["fresh_retained_native_count"] == 2 and r["bootstrap"]["fresh_retained_parent"] is True, "fresh bootstrap prerequisites")
    need(n["retained_parent_receipt_sha256"] == r["bootstrap"]["retained_parent_receipt_sha256"] == o["parent_receipt"], "same-run retained parent")
    for pid, tag in (("gauge44", "base"), ("extra", "extra")):
        ent = n["providers"][tag]
        need(ent["word_sha256"] == o["words"][tag], "actual native word")
        need(ent["complete_native_files"] == o["native_files"][tag] and len(ent["complete_native_files"]) == 12, "complete native files")
        actual = {name.removeprefix("local/"): h for name, h in o["native_files"][tag].items() if name.startswith("local/")}
        need(len(actual) == 11 and i["providers"][pid]["artifacts"] == actual, "invoice/native artifact chain")
        need(histogram(i["providers"][pid]["paid_profile"]) == LOCAL, "provider local paid profile")
    need(i["owner_audit_sha256"] == o["owner"] and i["controller_audit_sha256"] == o["controller"], "invoice owner/controller binding")
    need(i["template_sha256"] == r["owner"]["template_sha256"] == r["idle"]["template_sha256"]
         == o["hosted_template_payload_sha256"], "actual hosted owner/idle template")
    need(r["idle"]["uncompressed_frames_sha256"] == o["idle_payload_sha256"], "literal idle payload binding")
    idle = histogram(r["idle"]["rank_profile"])
    need(idle == o["idle_recount"] == histogram(r["independent"]["idle"]), "idle rank recount")
    need(sum(idle.values()) == r["idle"]["children"] == 52184, "idle child census")
    need(i["provider_counts"] == {"gauge44": 250, "extra": 416}, "provider dispatch counts")
    local = Counter()
    for pid, count in i["provider_counts"].items():
        local.update({rank: count * amount for rank, amount in histogram(i["providers"][pid]["paid_profile"]).items()})
    need(dict(local) == histogram(i["selected_local_paid_profile"]), "paid call aggregation")
    local.update(idle)
    for profile in (a["profile"], r["result"]["profile"], r["owner"]["paid_profile"], r["independent"]["profile"], r["assembly"]["complex_profile"]):
        need(dict(local) == histogram(profile) == PROFILE, "complete local-plus-idle profile")
    need(sum(rank * amount for rank, amount in local.items()) == r["owner"]["rank_mass"] == 4816512, "complete rank mass")
    expected = {"data_and_owner_families": 66304, "local_helpers": 408,
                "private_centres": 8, "private_zero_buffers": 91, "coefficient_work": 2}
    need(i["physical_stock_identity"] == expected and sum(expected.values()) == i["physical"] == 66813, "complete physical stock")
    need(i["private_zero_buffers"] == 91 and i["live"] == 66304, "physical buffer census")
    need(i["complete_invocation_sweeps"] == i["bridge_sweeps"] == sum(i["provider_counts"].values()) == 666, "complete sweeps")
    group = 1 << (36 * 36)
    for k in range(1, 37):
        group *= (1 << (2 * k)) - 1
    stockbits = (group * i["physical"]).bit_length()
    need(stockbits == b["physical_stock_bits"] == 2644 and (stockbits + 1) // 2 == b["stock_l2_bits"] == 1322, "full physical stock exponent")
    localbits = max(z["prefix_bits"] for p in i["providers"].values() for z in p["local"].values())
    need(localbits == b["local_actual_prefix_bits"] == 93, "actual local prefix")
    need(b["input_l2_bits"] == 37 and b["max_active_depth"] == b["boundary_depth_bits"] == 18
         and b["partial_cover_bits"] == 1 and b["local_reserve_bits"] == 128,
         "declared prefix summands")
    need(localbits + 37 + 18 + b["stock_l2_bits"] + 1 + 4 == b["actual_prefix_bits"] == i["global_prefix_bits"] == 1475, "actual prefix arithmetic")
    need(128 + 37 + 18 + b["stock_l2_bits"] + 1 + 4 == b["required_reserve_bits"] == 1510, "reserve arithmetic")
    need(b["required_reserve_bits"] < i["charged_prefix_bits"] == b["retained_payload_bits"] == 2048, "charged prefix allowance")
    need(set(i["strict_checks"]) == {"local_primitive_bound", "logical", "router", "literal", "mass", "precision", "tape", "row", "halving"}
         and all(x is True for x in i["strict_checks"].values()), "nine named finite checks")


def controls(records, observed):
    cases = [
        ("missing_stage", lambda r: r["stages"].pop(3)),
        ("stale_bootstrap", lambda r: r["native"].__setitem__("retained_reuse_receipt_sha256", "0" * 64)),
        ("unbound_native_artifact", lambda r: r["invoice"]["providers"]["extra"]["artifacts"].__setitem__("CLIFFORD-RECIPES.json", "0" * 64)),
        ("coherent_stale_template_claim", lambda r: [r[k].__setitem__("template_sha256", "0" * 64)
                                                    for k in ("invoice", "owner", "idle")]),
        ("idle_rank_count", lambda r: r["idle"]["rank_profile"].__setitem__("1", 17311)),
        ("paid_call_aggregation", lambda r: r["invoice"]["selected_local_paid_profile"].__setitem__("1", 1625707)),
        ("private_buffer_omission", lambda r: r["invoice"]["physical_stock_identity"].__setitem__("private_zero_buffers", 90)),
        ("missing_bridge", lambda r: r["invoice"].__setitem__("bridge_sweeps", 665)),
        ("understated_stock", lambda r: r["invoice"]["blocknorm"].__setitem__("stock_l2_bits", 1321)),
        ("understated_prefix", lambda r: r["invoice"].__setitem__("global_prefix_bits", 1474)),
        ("wrong_release_endpoint", lambda r: r["release"].__setitem__("kappa_decimal", "0.001729")),
    ]
    rejected = []
    for name, mutate in cases:
        r = deepcopy(records)
        mutate(r)
        try:
            validate(r, observed)
        except ValueError as error:
            rejected.append({"name": name, "reason": str(error)})
        else:
            raise ValueError("accepted mutant: " + name)
    return rejected


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--work", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    args = ap.parse_args()
    records, observed = load(args.work.resolve(), args.repo.resolve())
    validate(records, observed)
    result = {"status": "PASS_INDEPENDENT_PR3044_FRESH_RUN_BINDINGS",
              "source_files": observed["source_files"], "admitted_package_files": observed["admitted_package_files"],
              "native_cache_files": observed["cache_files"],
              "native_provider_files": 24, "invoice_native_artifact_bindings": 22,
              "fresh_stages": 13, "idle_children_recounted": 52184,
              "complete_profile": PROFILE, "physical_families": 66813,
              "rank_mass": 4816512, "global_prefix_bits": 1475,
              "required_reserve_bits": 1510, "charged_prefix_bits": 2048,
              "kappa": records["result"]["kappa"],
              "checked_record_sha256": {k: v for k, v in observed.items() if isinstance(v, str) and k != "published_kappa"},
              "rejected_controls": controls(records, observed),
              "scope": "Data bindings and invoice aggregation; no independent native, owner-legality, analytic or full-theorem proof."}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
