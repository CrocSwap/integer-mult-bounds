#!/usr/bin/env python3
"""Source-bound replay and semantic controls. SPDX-License-Identifier: Apache-2.0.

Prepared by AAAmirinu with substantial OpenAI Codex assistance.
Only our independently implemented explicit-set ledger is imported.
"""
import argparse
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

from ledger import LedgerError, audit_word, compare_words, require, span

HERE = Path(__file__).resolve().parent
HEADS = {
    "pr2312": "fb76f799ccf078f51780076ebed3fd26b1db11c0",
    "pr2322": "002304ef01c4416a127916169ae6d94c1bee052b",
}
EXPECTED_DELTA = {"1": -8, "2": 8, "3": 4, "4": -4, "5": -4}
C5_DELTA = {"1": 12, "2": -8, "3": -4, "4": 4}
C4 = [260, 132, 75, 51]
C5 = [260, 132, 75, 42, 25]
HIGH = [619, 621, 622, 623]
LOW = [616, 617, 618, 620]
LENDERS = [1, 4, 6, 12]


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def verify_blob(raw, entry):
    require(hashlib.sha256(raw).hexdigest() == entry["sha256"],
            "source SHA256 mismatch: " + entry["path"])
    blob = b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw
    require(hashlib.sha1(blob).hexdigest() == entry["git_blob"],
            "source Git blob mismatch: " + entry["path"])


def authenticate():
    entries = read_json(HERE / "SOURCES.json")["vendored_sources"]
    paths = [entry["path"] for entry in entries]
    expected = {
        "sources/pr2312/base.json.gz", "sources/pr2312/extra.json.gz",
        "sources/pr2312/MANIFEST.json", "sources/pr2322/base.json.gz",
        "sources/pr2322/extra.json.gz", "sources/pr2322/PACKAGE-MANIFEST.json",
        "sources/pr2322/CLAIM.json", "sources/pr2322/GENERATOR-NOTICE.txt",
    }
    require(len(paths) == len(expected) and set(paths) == expected, "source inventory mismatch")
    for entry in entries:
        owner = entry["path"].split("/")[1]
        require(entry["commit"] == HEADS[owner], "source commit mismatch")
        verify_blob((HERE / entry["path"]).read_bytes(), entry)
    by_path = {entry["path"]: entry for entry in entries}
    source_manifest = read_json(HERE / "sources/pr2312/MANIFEST.json")
    candidate_manifest = read_json(HERE / "sources/pr2322/PACKAGE-MANIFEST.json")
    for kind in ("base", "extra"):
        require(source_manifest["new/borrow/words/BORROW-WORD-43" + kind + ".json.gz"] ==
                by_path["sources/pr2312/" + kind + ".json.gz"]["sha256"],
                "adopted manifest/word mismatch")
        require(candidate_manifest["words/" + kind + ".json.gz"] ==
                by_path["sources/pr2322/" + kind + ".json.gz"]["sha256"],
                "candidate manifest/word mismatch")
    for name in ("CLAIM.json", "GENERATOR-NOTICE.txt"):
        require(candidate_manifest[name] == by_path["sources/pr2322/" + name]["sha256"],
                "candidate manifest/metadata mismatch")
    claim = read_json(HERE / "sources/pr2322/CLAIM.json")
    require(claim["source_head"] == HEADS["pr2312"], "claim adopted a different source head")
    return entries, claim


def add_delta(profile, delta):
    out = dict(profile)
    for rank, change in delta.items():
        out[rank] = out.get(rank, 0) + change
        require(out[rank] >= 0, "negative count in control fixture")
    return {k: v for k, v in out.items() if v}


def compact_ledger(ledger):
    keys = ("local_profile", "rank_mass", "section_profiles", "helper_width_inventory",
            "helper_width_mass", "raw_helpers", "live_helpers", "charged_events_sha256",
            "scalar_event_counts")
    result = {key: ledger[key] for key in keys}
    result["handoffs"] = len(ledger["map_checks"])
    result["ambient_images_per_handoff"] = 512
    return result


def compact_comparison(comparison):
    result = {key: value for key, value in comparison.items() if key not in ("source", "candidate")}
    result["source"] = compact_ledger(comparison["source"])
    result["candidate"] = compact_ledger(comparison["candidate"])
    return result


def check_four_role_identity(comparison, claim):
    require(comparison["local_profile_delta"] == EXPECTED_DELTA, "four-role profile identity")
    require(comparison["section_deltas"] == {
        "A": {}, "private-cut": {}, "B": {"1": -8, "2": 8, "3": 4, "4": -4},
        "restore": {}, "end": {"5": -4},
    }, "section-level pricing identity")
    require(comparison["newly_removed_raw_roles"] == HIGH, "raw retirement identity")
    require(comparison["removed_source_compact_indices"] ==
            claim["removed_old_helper_indices"] == [384, 386, 387, 388],
            "source compact index binding")
    require(comparison["removed_widths"] == {str(role): 4 for role in HIGH},
            "retired width identity")
    require(comparison["rank_mass_delta"] == comparison["helper_width_mass_delta"] == -16,
            "local mass/width identity")
    require(comparison["candidate"]["live_helpers"] == claim["native_helpers"] == 434,
            "candidate helper inventory binding")
    require(set(comparison["changed_roles"]) == set(map(str, HIGH + LOW + LENDERS)),
            "changed-role support")
    for roles, expected in (
        (LOW, {"1": -1, "2": 1, "3": 1, "4": -1}),
        (HIGH, {"1": -4}),
        (LENDERS, {"1": 3, "2": 1, "5": -1}),
    ):
        for role in roles:
            require(comparison["changed_roles"][str(role)]["delta"] == expected,
                    "role-class identity: " + str(role))


def replay():
    entries, claim = authenticate()
    positive, negative, comparisons, c5_results = [], [], {}, {}

    def rejected(name, operation, fragment):
        try:
            operation()
        except LedgerError as error:
            require(fragment in str(error), name + ": unexpected rejection " + str(error))
            negative.append({"name": name, "rejection": str(error)})
        else:
            raise LedgerError(name + ": invalid control was accepted")

    for entry in entries:
        raw = (HERE / entry["path"]).read_bytes()
        corrupted = bytes([raw[0] ^ 1]) + raw[1:]
        rejected("source-byte/" + entry["path"],
                 lambda raw=corrupted, entry=entry: verify_blob(raw, entry), "source SHA256 mismatch")

    for kind in ("base", "extra"):
        source = json.loads(gzip.decompress((HERE / ("sources/pr2312/" + kind + ".json.gz")).read_bytes()))
        candidate = json.loads(gzip.decompress((HERE / ("sources/pr2322/" + kind + ".json.gz")).read_bytes()))
        comparison = compare_words(source, candidate)
        check_four_role_identity(comparison, claim)
        comparisons[kind] = comparison
        positive.extend([kind + "/source-word", kind + "/candidate-word"])

        def mutation(name, change, fragment):
            altered = deepcopy(candidate)
            change(altered)
            rejected(kind + "/" + name, lambda: audit_word(altered), fragment)

        def wrong_report(word):
            # -2 H_1 + H_2 leaves the total paid rank unchanged.
            word["report"]["local_profile"] = add_delta(word["report"]["local_profile"], {"1": -2, "2": 1})

        mutation("equal-mass-false-report", wrong_report, "reported local profile differs")
        mutation("wrong-width-report",
                 lambda w: w["report"]["width_inventory"].__setitem__("4", 34),
                 "reported helper-width inventory differs")
        mutation("float-profile-count",
                 lambda w: w["report"]["local_profile"].__setitem__("1", 2335.0),
                 "reported local_profile counts must be positive integers")
        mutation("float-width-count",
                 lambda w: w["report"]["width_inventory"].__setitem__("4", 33.0),
                 "reported width_inventory counts must be positive integers")
        mutation("noncanonical-rank-key",
                 lambda w: w["report"]["local_profile"].__setitem__("01", 1),
                 "reported local_profile has a noncanonical rank key")
        mutation("removed-role-reference", lambda w: w["A"][0].__setitem__(1, HIGH[0]),
                 "removed role referenced")
        mutation("duplicate-removal", lambda w: w["removed"].append(w["removed"][0]),
                 "duplicate removed role")
        mutation("duplicate-port", lambda w: w["ports"].__setitem__(1, w["ports"][0]),
                 "duplicate port")
        mutation("singular-map", lambda w: w["warps"][-1][2].__setitem__(0, w["warps"][-1][2][1]),
                 "not an ambient bijection")
        mutation("wrong-map-subspace", lambda w: w["warps"][-1].__setitem__(4, [1, 2, 4, 8]),
                 "carries the wrong subspace")
        mutation("wrong-handoff-time", lambda w: w["warps"][-1].__setitem__(0, len(w["B"]) + 1),
                 "outside B chronology")
        mutation("wrong-handoff-source", lambda w: w["warps"][-1].__setitem__(3, [1, 2, 4, 8]),
                 "does not start at the current source frame")
        mutation("nonzero-unpriced-frame",
                 lambda w: w["precondition"].append(["add", 0, 1, 1, 1, [1]]),
                 "nonzero frame outside this pricing interface")
        mutation("zero-scale", lambda w: w["precondition"].append(["scale", 0, 0, 1, []]),
                 "noninvertible scalar scale")
        mutation("invalid-private-source", lambda w: w["cut"][0].__setitem__(2, LOW[0]),
                 "private cut must copy a center")
        mutation("noncontaining-frame", lambda w: w["B"][-1].__setitem__(-1, []),
                 "noncontaining frame")
        mutation("same-rank-wrong-subspace",
                 lambda w: w["B"][1019].__setitem__(-1, [260, 132, 75, 50]),
                 "noncontaining frame at B[1019], role 616")

        # Equivalent redundant generators must not change an event ledger.
        equivalent = deepcopy(candidate)
        for event in equivalent["B"]:
            if event[-1]:
                event[-1].extend([0, event[-1][0]])
        for event in equivalent["warps"]:
            for chart in (event[3], event[4]):
                chart.extend([0, chart[0]])
        equivalent_ledger = audit_word(equivalent)
        require(equivalent_ledger == comparison["candidate"], "basis spelling changed semantic ledger")
        positive.append(kind + "/redundant-generators")

        # Actual-source semantic mutant: keep all four rank-4 handoff destinations
        # but change ONLY the 12 moved preparation charts from C4 to C5.
        mutant = deepcopy(candidate)
        prep = mutant["B"][1019:1031]
        require(len(prep) == 12 and all(e[0] == "add" and e[1] in LOW and e[2] in LENDERS
                                      and e[-1] == C4 for e in prep), "preparation locator drift")
        require(span(C4) < span(C5), "control must enlarge the actual chart by one dimension")
        for event in prep:
            event[-1] = list(C5)
        rejected(kind + "/C5-stale-report", lambda: audit_word(mutant), "reported local profile differs")
        mutant["report"]["local_profile"] = add_delta(candidate["report"]["local_profile"], C5_DELTA)
        mutant_ledger = audit_word(mutant)
        require(mutant_ledger["rank_mass"] == comparison["candidate"]["rank_mass"] == 5371,
                "C5 control must preserve rank mass")
        require(mutant_ledger["helper_widths"] == comparison["candidate"]["helper_widths"],
                "C5 control must preserve helper widths")
        c5_results[kind] = {
            "profile": mutant_ledger["local_profile"], "delta_from_candidate": C5_DELTA,
            "rank_mass": mutant_ledger["rank_mass"], "widths_unchanged": True,
            "charged_events_sha256": mutant_ledger["charged_events_sha256"],
            "scope": "Frame-ledger-admissible; scalar identity and physical phases are NOT certified.",
        }
        positive.append(kind + "/C5-corrected-report")

    result = {
        "status": "PASS_INDEPENDENT_FOUR_ROLE_RAW_FRAME_LEDGER",
        "source_heads": HEADS,
        "method": "Explicit GF(2)^9 span sets and all-512-vector map tables; no producer imports.",
        "comparisons": {kind: compact_comparison(value) for kind, value in comparisons.items()},
        "equal_mass_actual_source_controls": c5_results,
        "positive_controls": positive,
        "negative_controls": negative,
        "scope": {
            "checked": ["exact eight-source hashes and manifest joins", "both raw provider words",
                        "monotone paid frame visits and nested private-copy bills",
                        "raw role retirement, retained widths, event/role/section profile deltas",
                        "zero-rank handoff subspace mapping and ambient invertibility"],
            "not_checked": ["scalar algebra and cleanup correctness", "physical Clifford phases",
                            "emitted native stream", "global owner chronology or idle bills",
                            "moment roots", "all-size and outer theorem admission"],
            "selected_frontier_changed": False,
        },
    }
    return result, comparisons


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true", help="explicitly regenerate RESULT.json")
    parser.add_argument("--full-ledger-output", type=Path, help="optionally export all event ledgers to this JSON file")
    args = parser.parse_args()
    result, comparisons = replay()
    if args.write_result:
        (HERE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    else:
        require(read_json(HERE / "RESULT.json") == result, "committed result differs from reconstructed evidence")
    if args.full_ledger_output:
        args.full_ledger_output.write_text(json.dumps(comparisons, indent=2) + "\n", encoding="utf-8")
    print(result["status"] + ": " + str(len(result["positive_controls"])) + " positive, " +
          str(len(result["negative_controls"])) + " negative controls")


if __name__ == "__main__":
    main()
