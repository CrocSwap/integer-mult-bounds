#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Replay the exact five-helper cyclic search, endpoint and priced word."""
import gzip
import hashlib
import json
import argparse
import runpy
import subprocess
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "research/r439-bsection-stars-seed01/"
BASE_WORD = ROOT / (BASE + "candidate.json.gz")
BASE_PACKAGE_VERIFY = ROOT / (BASE + "verify.py")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def verify_source_rows():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    base = manifest["base_commit"]
    for row in manifest["files"]:
        path = row["path"]
        pinned = subprocess.check_output(["git", "show", base + ":" + path], cwd=ROOT)
        blob = subprocess.check_output(["git", "rev-parse", base + ":" + path], cwd=ROOT).decode().strip()
        need(blob == row["git_blob"], "source Git blob changed: " + path)
        need(hashlib.sha256(pinned).hexdigest() == row["sha256"], "source provenance digest changed: " + path)
        if row["usage"] == "input":
            live = (ROOT / path).read_bytes()
            need(live == pinned, "live input differs from pinned base: " + path)
    old = runpy.run_path(str(BASE_PACKAGE_VERIFY))
    builder = old["Bd"]
    builder["pins"](ROOT)
    return manifest, old


def d_boundary(old, word):
    return old["d_rows"](word)


def require_bad_control(label, candidate, old_rows, old):
    need(d_boundary(old, candidate) != old_rows, "negative control accepted: " + label)


def controls(base_word, candidate, parts, old):
    expected = d_boundary(old, base_word)
    n0 = len(parts["helper_prep"])
    n1 = len(parts["target_prep"])
    n2 = len(parts["injection"])
    n3 = len(parts["target_restore"])
    prep_start = n0
    injection_start = n0 + 5 + n1
    restore_start = injection_start + n2 + n3
    report = []

    bad = json.loads(json.dumps(candidate))
    del bad["D"][prep_start]
    require_bad_control("missing helper preparation edge", bad, expected, old)
    report.append("missing helper preparation edge rejected by D boundary")

    bad = json.loads(json.dumps(candidate))
    del bad["D"][restore_start]
    require_bad_control("missing inverse restoration edge", bad, expected, old)
    report.append("missing inverse restoration edge rejected by D boundary")

    bad = json.loads(json.dumps(candidate))
    bad["D"][injection_start:injection_start + n2] = parts["injection"]
    require_bad_control("stale injection J0", bad, expected, old)
    report.append("stale injection rejected by D boundary")

    bad = json.loads(json.dumps(candidate))
    edges = candidate["D"][prep_start:prep_start + 5]
    bad["D"][restore_start:restore_start + 5] = edges
    require_bad_control("wrong inverse order", bad, expected, old)
    report.append("wrong inverse order rejected by D boundary")

    bad = json.loads(json.dumps(candidate))
    gate = bad["D"][injection_start]
    source = gate[2][0]
    if source in gate[2]:
        gate[2].remove(source)
    else:
        gate[2].append(source)
    require_bad_control("mutated injection coefficient", bad, expected, old)
    report.append("mutated injection coefficient rejected by D boundary")
    return report


def verify(write_certificate=False):
    manifest, old = verify_source_rows()
    search = runpy.run_path(str(HERE / "search.py"))
    base_word = search["load_word"]()
    parts = search["split_d"](base_word)
    columns = search["injection_columns"](base_word, parts["injection"])
    word, got_parts, got_columns, replay = search["search"]()
    need(canonical(word) == canonical(base_word), "search loaded a different source word")
    need(got_parts == parts and got_columns == columns, "D source decomposition changed")

    candidate_path = HERE / "CANDIDATE.json.gz"
    candidate_bytes = candidate_path.read_bytes()
    candidate = json.loads(gzip.decompress(candidate_bytes))
    selected = replay["best_64"][0]
    expected_candidate = search["candidate_for"](base_word, parts, columns, selected)
    need(canonical(candidate) == canonical(expected_candidate), "candidate is not the exact search winner")
    need(selected["saving"] == 12 and selected["injection_weight"] == 4442,
         "selected five-cycle cost changed")

    expected_search = dict(replay)
    expected_search["candidate_sha256"] = hashlib.sha256(canonical(candidate)).hexdigest()
    expected_search["candidate_gzip_sha256"] = hashlib.sha256(candidate_bytes).hexdigest()
    expected_search["selected_candidate"] = selected
    stored_search = json.loads((HERE / "SEARCH-RESULT.json").read_text())
    need(stored_search == expected_search, "bounded search receipt differs")
    need(replay["candidates"] == 1_860_480 and replay["positive_saving_candidates"] == 56,
         "bounded search coverage changed")
    need(replay["optimistic_max_net_ADD_saving"]["net"] == 109,
         "optimistic fully charged ceiling changed")

    need(d_boundary(old, candidate) == d_boundary(old, base_word), "D arbitrary-input endpoint changed")
    controls_found = controls(base_word, candidate, parts, old)

    original = old["load"](old["ROOT"] / old["WORD"])
    helper_star = old["load"](old["ROOT"] / "research/r439-helper-stars-seed19/candidate.json.gz")
    reference_owner_all = old["owner"](helper_star)
    reference_owner = {k: reference_owner_all[k] for k in ("hypotheses", "conclusions")}
    with tempfile.TemporaryDirectory(prefix="r439-five-cycle-") as temp:
        checks = old["word_checks"]("five_cycle", candidate, original, reference_owner, Path(temp))

    baseline_owner = old["owner"](base_word)
    candidate_owner = old["owner"](candidate)
    need(candidate_owner["profile"] == baseline_owner["profile"], "paid profile changed")
    need(sum(r * c for r, c in candidate_owner["profile"].items()) == 5129,
         "paid rank mass changed")
    need(checks["literal"]["D_adds"] == 5536, "complete D ADD invoice changed")
    need(checks["literal"]["native_ADDs"] == 11488, "complete word ADD invoice changed")
    need(checks["literal"]["F"] == 27061 and checks["literal"]["B"] == 5921344,
         "F/B evidence changed")
    need(checks["literal"]["local_bits"] <= 104 and checks["literal"]["nine_stage_bits"] <= 192,
         "precision guard failed")
    local_bound = 64 * checks["literal"]["F"]**3 * checks["literal"]["B"]**2
    nine_stage_bound = (1 << 18) * checks["literal"]["F"]**5 * checks["literal"]["B"]**4
    need(local_bound < (1 << 104) and nine_stage_bound < (1 << 192),
         "exact precision inequality failed")

    report = {
        "status": "PASS_R439_FIVE_CYCLE",
        "base_commit": manifest["base_commit"],
        "selected_record_sha256": manifest["selected_record_sha256"],
        "search": {
            "supports": replay["supports"], "sweeps_per_support": replay["sweeps_per_support"],
            "candidates": replay["candidates"], "positive_saving_candidates": replay["positive_saving_candidates"],
            "optimistic_max_net_ADD_saving": replay["optimistic_max_net_ADD_saving"]["net"],
            "selected": selected,
        },
        "word": checks,
        "exact_precision": {
            "local": {"lhs": str(local_bound), "rhs": str(1 << 104)},
            "nine_stage": {"lhs": str(nine_stage_bound), "rhs": str(1 << 192)},
        },
        "paid_profile": candidate_owner["profile"],
        "paid_rank_mass": 5129,
        "controls": controls_found,
        "new_kappa": False,
        "unrun": ["native C++ replay", "supplier adoption", "outer assembly replay", "all-size/compiler and analytic proof obligations"],
    }
    # JSON object keys (including paid-profile ranks) are strings in the receipt.
    report = json.loads(json.dumps(report))
    certificate_path = HERE / "CERTIFICATE.json"
    if write_certificate:
        certificate_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        stored = json.loads(certificate_path.read_text())
        need(stored == report, "certificate differs from replay")
    print(json.dumps(report, sort_keys=True))
    print("PASS_R439_FIVE_CYCLE candidates=1860480 best_saving=12 ADDs=11500->11488 columns=661 controls=5 no_new_kappa")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    args = parser.parse_args()
    verify(write_certificate=args.write_certificate)
