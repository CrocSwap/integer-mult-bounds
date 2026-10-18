#!/usr/bin/env python3
"""Exact complete-word and native-binding checks; no supplier admission."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core


def inverse(word):
    out = []
    for event in reversed(word):
        if event[0] == "add":
            out.append((*event[:3], -event[3]))
        elif event[0] == "scale":
            out.append((*event[:2], str(1 / core.F(event[2]))))
        else:
            out.append((*event[:2], (-event[2]) % 4))
    return out


def controls(expected):
    modules, _, _ = core.load()
    word = core.compile_shear(1)
    pivots = modules["source"].PIVOTS
    cases = {}

    def differs(name, mutant):
        rows, _ = core.replay(mutant)
        core.need(rows != expected, "semantic mutant accepted: " + name)
        cases[name] = "rejected_by_complete_map"

    index = next(i for i, e in enumerate(word)
                 if e[0] == "add" and e[1] - core.N in pivots
                 and 224 <= e[2] < core.N and e[2] not in pivots)
    differs("omitted_dirty_nonpivot_load", word[:index] + word[index + 1:])
    index = next(i for i, e in enumerate(word) if e[0] == "add" and e[3] == -1 and e[1] < core.N + 112)
    mutant = list(word)
    mutant[index] = (*word[index][:3], 1)
    differs("lost_signed_data_edge", mutant)
    index = next(i for i, e in enumerate(word) if e[0] == "z" and e[2] == 3)
    mutant = list(word)
    mutant[index] = (*word[index][:2], 1)
    differs("wrong_payload_orientation", mutant)
    index = max(i for i, e in enumerate(word) if e[0] == "scale")
    differs("missing_inverse_basis_scale", word[:index] + word[index + 1:])
    index = next(i for i, e in enumerate(word)
                 if e[0] == "add" and e[2] < 112 and e[1] != e[2] + core.N)
    mutant = list(word)
    mutant[index] = ("add", word[index][1], word[index][2] + core.N, word[index][3])
    differs("dirty_destination_used_as_source", mutant)
    naive = core.data_shear(1, 1) + [("add", core.N + j, j, 1) for j in range(112, core.N)]
    rows, _ = core.replay(naive)
    core.need(rows != expected, "helper-identity mutant must fail")
    strip = lambda rs: [{j: p for j, p in row.items() if j < 224 or j >= core.N} for row in rs]
    core.need(strip(rows) == strip(expected), "helper mutant must pass data/work-only columns")
    cases["coherent_helper_identity"] = "passes_data_and_work_columns_but_fails_dirty_source_helpers"
    temporary_write = [("scale", 0, "2"), ("scale", 0, "1/2")] + word
    core.need(core.replay(temporary_write)[0] == expected, "transient-write control endpoint")
    try:
        core.replay(temporary_write, readonly=True)
    except ValueError as error:
        core.need("read-only" in str(error), "correct read-only guard")
    else:
        raise ValueError("transient source write accepted")
    cases["endpoint_correct_transient_source_write"] = "rejected_by_prefix_contract"
    for phase, sign in ((True, 1), (4, 1), (1, True), (1, 0)):
        try:
            core.compile_shear(phase, sign)
        except ValueError:
            pass
        else:
            raise ValueError("invalid typed phase/sign accepted")
    cases["invalid_phase_or_sign"] = "four_rejections"
    return cases


def run():
    modules, data, _ = core.load()
    identity = modules["algebra"].identity(2 * core.N)
    results = []
    positive = None
    for phase in range(4):
        for sign in (-1, 1):
            word = core.compile_shear(phase, sign)
            actual, bounds = core.replay(word, metrics=True, readonly=True)
            baseline, _ = core.replay(core.compile_shear(phase, sign, "full"))
            factored, _ = core.replay(core.compile_shear(phase, sign, "factored"))
            core.need(actual == baseline == factored, "complete arbitrary-dirt equality")
            core.need(actual[:core.N] == identity[:core.N], "source endpoint")
            restored, _ = core.replay(inverse(word), actual, readonly=True)
            core.need(restored == identity, "literal inverse restores both banks")
            restored, _ = core.replay(core.compile_shear(phase, -sign), actual, readonly=True)
            core.need(restored == identity, "opposite sign is exact transported ERASE")
            inv = core.invoice(word)
            core.need(inv["source_writing_events"] == 0 and inv["CLEAR"] == 0,
                      "no source mutation or dirty-work disposal")
            results.append({"phase": phase, "sign": sign,
                            "word_sha256": core.digest(word),
                            "operator_sha256": core.digest(core.encoded(actual)),
                            "new": inv, "prefix": bounds,
                            "full_sandwich": core.invoice(core.compile_shear(phase, sign, "full")),
                            "factored_sandwich": core.invoice(core.compile_shear(phase, sign, "factored"))})
            if (phase, sign) == (1, 1):
                positive = actual
    # Original native checks are a source-bound positive control, not new code.
    native = modules["native_check"].run(data)
    sigma = data["sigma"]
    frame_pairs = 0
    for phase in range(4):
        for source, (target, _) in enumerate(core.signed_power(data, phase)):
            domain = modules["source"].span(data["word"]["frames"][data["word"]["start"][target]])
            for _ in range((-phase) % 4):
                domain = {modules["source"].binary(sigma, x) for x in domain}
            expected = modules["source"].span(data["word"]["frames"][data["word"]["start"][source]])
            core.need(domain == expected, "data ADD intermediate frame alignment")
            frame_pairs += 1
    table = list(range(512))
    powers = []
    for phase in range(4):
        core.need(len(set(table)) == 512, "native monomial is a permutation")
        powers.append(core.digest(table))
        table = [modules["source"].binary(sigma, x) for x in table]
    core.need(table == list(range(512)), "native fourth power")
    climbs = Counter(e[-1] for e in data["program"][7401:12550] if e[0] == "climb")
    core.need(climbs == {1: 936, 4: 56}, "unchanged reader-prefix child inventory")
    return {"status": "finite_readonly_transported_shear", "field_count": 1408,
            "phases": 4, "signs": 2, "cases": results,
            "native_predecessor_receipt_sha256": core.digest(native),
            "payload_power_map_sha256": powers,
            "checked_data_intermediate_frame_pairs": frame_pairs,
            "controls": controls(positive),
            "reader_prefix_climbs": {str(k): v for k, v in sorted(climbs.items())},
            "four_prefix_echo_climb_rank_mass": 4 * sum(k * v for k, v in climbs.items()),
            "deleted_centre_children": 0, "added_positive_rank_children": 0,
            "supplier_admission": False, "new_kappa": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    parser.add_argument("--emit-words", action="store_true")
    args = parser.parse_args()
    if args.emit_words:
        print(core.canonical([{"phase": t, "sign": s, "word": core.compile_shear(t, s)}
                              for t in range(4) for s in (-1, 1)]))
        return
    result = run()
    if args.emit:
        print(json.dumps(result, sort_keys=True, indent=2))
        return
    expected = json.loads((core.HERE / "RESULT.json").read_text())
    core.need(core.canonical(result) == core.canonical(expected), "complete typed receipt mismatch")
    print("PASS_READONLY_TRANSPORTED_SHEAR phases=4 signs=2 fields=1408 "
          "quarter_scalar=3336->1732 factored=2664->1732 no_new_kappa")


if __name__ == "__main__":
    main()
