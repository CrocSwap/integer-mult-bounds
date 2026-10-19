#!/usr/bin/env python3
"""Rebase PR1047's helper shear onto seed-01's 236-star word."""
import argparse
import copy
import hashlib
import json
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_json(path):
    return json.loads(path.read_text(encoding="utf8"))


def check_source_pins():
    pins = load_json(HERE / "SOURCES.json")
    need(pins["base_commit"] == BASE, "wrong base commit")
    for source in pins["files"]:
        if source["usage"] != "input":
            continue
        path = ROOT / source["path"]
        need(hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"],
             "source hash: " + source["path"])


def histogram(owner):
    return {int(rank): int(count) for rank, count in owner["profile"].items()}


def run(write_result=False):
    check_source_pins()
    # Reuse the pinned R439 checker for the inherited literal, frame and owner
    # conventions; the rebase and its controls are constructed independently.
    inherited = runpy.run_path(str(ROOT / "research/r439-bsection-stars-seed01/verify.py"))
    word_path = ROOT / "research/r439-bsection-stars-seed01/candidate.json.gz"
    before = inherited["load"](word_path)
    census = load_json(ROOT / "research/r439-bsection-stars-seed01/candidate_search.json")
    stars = int(census["helper_edges"])
    v = int(before["v"])
    need((v, int(before["R"]), stars) == (111, 439, 236), "unexpected source word")
    need(len(before["D"]) == 2 * stars + 306 + v + 306,
         "unexpected five-part D itinerary")
    need(before["D"][-stars:] == list(reversed(before["D"][:stars])),
         "helper restoration does not reverse preparation")
    need(all(frame == 0 and len(donors) == 1
             for frame, _, donors in before["D"][:stars]), "helper preparation shape")
    need(all(frame == 0 and len(donors) == 1
             for frame, _, donors in before["D"][stars:stars + 306]),
         "pre-middle target shape")
    need(all(frame == 0 and len(donors) == 1
             for frame, _, donors in before["D"][stars + 306 + v:stars + 306 + v + 306]),
         "post-middle target shape")
    need(all(frame == 0 and len(donors) == 1
             for frame, _, donors in before["D"][-stars:]), "helper restoration shape")

    # PR1047's T = I + e_242 e_19^T acts on the 439 helper coordinates.
    # In this word those coordinates are registers 2v+242=464 and 2v+19=241.
    destination, source = 2 * v + 242, 2 * v + 19
    cut = stars + 306
    middle = copy.deepcopy(before["D"][cut:cut + v])
    need(len(middle) == v, "middle target block")
    need(all(frame == 0 and v <= target < 2 * v
             and all(2 * v <= donor < 2 * v + 439 for donor in donors)
             for frame, target, donors in middle), "unexpected middle block")

    source_rows = {i for i, (_, _, donors) in enumerate(middle) if source in donors}
    destination_rows = {i for i, (_, _, donors) in enumerate(middle) if destination in donors}
    common_rows = source_rows & destination_rows
    for _, _, donors in middle:
        if destination in donors:
            if source in donors:
                donors.remove(source)
            else:
                donors.append(source)
            donors.sort()

    edge = [0, destination, [source]]
    after = copy.deepcopy(before)
    after["D"] = (copy.deepcopy(before["D"][:cut]) + [edge] + middle +
                  [copy.deepcopy(edge)] + copy.deepcopy(before["D"][cut + v:]))

    # T^2=I and the row update is M' = M T, so M' T h = M h for every
    # dirty helper vector. The complete word's unchanged sections then retain
    # both directions of the full dirty boundary.
    want = [{i, i - v} if v <= i < 2 * v else {i}
            for i in range(2 * v + int(before["R"]))]
    expected_d = inherited["d_rows"](before)
    need(inherited["d_rows"](after) == expected_d, "rebased D endpoint")
    need(inherited["literal_rows"](after) == want, "forward full dirty boundary")
    need(inherited["literal_rows"](after, True) == want, "reverse full dirty boundary")

    paths_before = inherited["frame_paths"](before)
    paths_after = inherited["frame_paths"](after)
    need(paths_before == paths_after, "register frame itinerary changed")
    owner_before = inherited["owner"](before)
    owner_after = inherited["owner"](after)
    profile_before = histogram(owner_before)
    profile_after = histogram(owner_after)
    need(profile_before == profile_after, "paid histogram changed")
    need(profile_before == inherited["PROFILE"], "unexpected inherited profile")
    need(owner_before["copy_ranks"] == owner_after["copy_ranks"] == [7] * 9,
         "copy rank itinerary changed")

    bill_before = inherited["literal_bounds"](before)
    bill_after = inherited["literal_bounds"](after)
    need((bill_before["native_ADDs"], bill_before["D_adds"]) == (11500, 5548),
         "unexpected pre-rebase scalar bill")
    need((bill_after["native_ADDs"], bill_after["D_adds"]) == (11497, 5545),
         "unexpected rebased scalar bill")
    need(bill_before["F"] == bill_after["F"] == 25717, "forward bound")
    need((bill_before["B"], bill_after["B"]) == (5911840, 5913026), "reverse bound")
    need(bill_after["local_bits"] <= 104 and bill_after["nine_stage_bits"] <= 192,
         "precision guard")

    new_source_weight = len(source_rows) + len(destination_rows) - 2 * len(common_rows)
    scalar_saving = len(source_rows) - new_source_weight - 2
    need((len(source_rows), len(destination_rows), len(common_rows), new_source_weight,
          scalar_saving) == (16, 13, 9, 11, 3), "support-delta identity")

    # Failure controls: dropping either shear gate or the M T correction must
    # change the arbitrary-dirty D map.
    def reject(name, candidate):
        try:
            actual = inherited["d_rows"](candidate)
        except ValueError:
            return name
        if actual != expected_d:
            return name
        raise ValueError("negative control accepted: " + name)

    prep_missing = copy.deepcopy(after)
    prep_missing["D"].pop(cut)
    restore_missing = copy.deepcopy(after)
    restore_missing["D"].pop(cut + 1 + v)
    correction_missing = copy.deepcopy(after)
    correction_missing["D"][cut + 1:cut + 1 + v] = copy.deepcopy(before["D"][cut:cut + v])
    controls = [reject("missing preparation", prep_missing),
                reject("missing restoration", restore_missing),
                reject("missing column correction", correction_missing)]

    result = {
        "status": "PASS_R439_SHEAR_REBASE_236_PROFILE",
        "base_commit": BASE,
        "proposal": "PR1047 helper shear (destination 242, source 19)",
        "input": "PR seed-01 degree-two candidate; 236 helper edges",
        "chronology": {
            "frame": 0,
            "D_prefix_records_before_middle": cut,
            "middle_target_rows": v,
            "changed_middle_rows": len(destination_rows),
            "register_destination": destination,
            "register_source": source,
            "shear_gates": 2,
        },
        "support_delta": {
            "source_column_before": len(source_rows),
            "destination_column": len(destination_rows),
            "overlap": len(common_rows),
            "source_column_after": new_source_weight,
            "net_ADD_saving": scalar_saving,
        },
        "bill_before": bill_before,
        "bill_after": bill_after,
        "frame_paths_equal": True,
        "copy_ranks": owner_after["copy_ranks"],
        "paid_histogram_before": profile_before,
        "paid_histogram_after": profile_after,
        "paid_rank_mass": sum(rank * count for rank, count in profile_after.items()),
        "controls_rejected": controls,
        "scope": "one exact PR1047 shear rebased onto the 236-edge seed-01 candidate; no new kappa",
    }
    need(result["paid_rank_mass"] == 5129, "paid rank mass")
    canonical = json.dumps(result, indent=2, sort_keys=True) + "\n"
    expected_path = HERE / "RESULT.json"
    if write_result:
        expected_path.write_text(canonical, encoding="utf8")
    else:
        need(expected_path.read_text(encoding="utf8") == canonical, "RESULT.json mismatch")
    print("PASS_R439_SHEAR_REBASE_236_PROFILE ADDs=11500->11497 D=5548->5545 "
          "changed_rows=13 histogram=unchanged rank_mass=5129 F=25717 B=5911840->5913026 "
          "guards=95/182 controls=3 no_new_kappa")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true")
    run(parser.parse_args().write_result)
