#!/usr/bin/env python3
"""Offline finite JP8 circuit certificate. Python 3.11+, standard library.

Philipp (@mightyOil), with substantial OpenAI Codex assistance. Apache-2.0.
This is a scalar circuit result, not a formal multiplication theorem.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
PROVIDER = ROOT / "research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8"
SOURCE_NAMES = {
    "certificates/checkpoints/k492626.json",
    "research/complex-k492-owner-repair/data/SPEC.json",
    "research/complex-k492-owner-repair/code/hpe_emit_local.py",
    "research/complex-k492-owner-repair/code/invoice_allcold.py",
    "research/complex-dyadic-lowering/lower.py",
    *{str(PROVIDER.relative_to(ROOT) / name) for name in
      ("LOCAL-PROGRAMS.json.gz", "LOCAL-CHECKS.json", "INDEPENDENT-LOCAL-REPLAY.json")},
}
VENDOR_NAMES = {"vendor/pr837/lower.py", "vendor/pr837/vendor/pr696_lower.py"}
DOMAIN = {"maximum_numerator":127, "maximum_denominator":16,
          "magnitude_bound":"abs(numerator)", "scratch_grid":"1/denominator",
          "unit_handling":"direct accumulation plus private clear, cost 2; outside graph search"}
PROVENANCE = {
    "base_commit":"f567884aeb8851b6e794af1184119a3bfbe1e631",
    "historical_provider":"PR626 JP8; not a PR799 implementation change",
    "source_heads":{
        "626":"660de893d27bb7abd1d5b01b1640207528a5c851",
        "622":"f69477f4f6d3c7eb1f740b166881bffed4ffa9f6",
        "696":"5a3f983715027c4fd83f50bc9001d4b18463bed1",
        "837":"0a2977195efc8fb2a918fbfb694ec8d294387f08",
    },
}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == ".gz" else data)


def check_pins():
    pins = read(HERE / "SOURCES.json")
    need(canonical({key:pins.get(key) for key in PROVENANCE}) == canonical(PROVENANCE),
         "source provenance identity")
    need(set(pins["files"]) == SOURCE_NAMES and set(pins["vendored"]) == VENDOR_NAMES,
         "source manifest coverage")
    for section, root in (("files", ROOT), ("vendored", HERE)):
        for name, pin in pins[section].items():
            payload = (root / name).read_bytes()
            if pin["representation"] == "decompressed-payload":
                payload = gzip.decompress(payload)
            else:
                need(pin["representation"] == "exact-bytes", "unknown pin representation")
            need(sha(payload) == pin["sha256"], "source pin mismatch: " + name)
    checkpoint = read(ROOT / "certificates/checkpoints/k492626.json")
    spec = read(ROOT / "research/complex-k492-owner-repair/data/SPEC.json")
    need(checkpoint["audited_source_head"] == pins["source_heads"]["626"], "historical source head")
    need(Q(checkpoint["kappa"]) == Q(spec["expected"]["kappa"]), "historical SPEC binding")
    return spec


def macro_check(q, word, budget):
    """Dense exact T,S,W map, local magnitude and grid, and paid word length."""
    t, s, w = ("T", 0), ("S", 0), ("W", 0)
    rows = {t: [Q(1), Q(0), Q(0)], s: [Q(0), Q(1), Q(0)],
            w: [Q(0), Q(0), Q(1)]}
    target_start, target_end = rows[t].copy(), [Q(1), q, Q(0)]
    initialized = False
    for primitive in word:
        op, dst = primitive[:2]
        need(dst in rows, "unknown register")
        need(dst != s, "source write")
        if op == "copy":
            rows[dst] = rows[primitive[2]].copy()
        elif op == "clear":
            rows[dst] = [Q(0)]*3
        elif op in ("double", "halve", "negate"):
            factor = {"double": Q(2), "halve": Q(1, 2), "negate": Q(-1)}[op]
            rows[dst] = [factor*x for x in rows[dst]]
        elif op in ("add", "subtract"):
            sign = 1 if op == "add" else -1
            rows[dst] = [x+sign*y for x, y in zip(rows[dst], rows[primitive[2]])]
        else:
            raise ValueError("unknown primitive")
        need(rows[t] in (target_start, target_end), "target prefix")
        if dst == w:
            initialized = True
        if initialized:
            need(rows[w][0] == rows[w][2] == 0, "dirty work dependency")
            coefficient = rows[w][1]
            need(abs(coefficient) <= abs(q.numerator), "magnitude bound")
            need(coefficient.denominator <= q.denominator, "fractional grid")
    need(rows == {t: target_end, s: [Q(0), Q(1), Q(0)], w: [Q(0)]*3},
         "macro endpoint or private clear")
    need(len(word) == budget, "primitive count")


def negative_controls(entries):
    import synth
    t, s, w = ("T", 0), ("S", 0), ("W", 0)
    q = Q(5, 2)
    good = synth.lower(["add", list(t), list(s), 5, 2], entries)
    grid = good[:1] + [("halve", w)]*2 + [("double", w)]*2 + good[1:]
    growth = good[:1] + [("double", w)]*3 + [("halve", w)]*3 + good[1:]
    cases = {
        "missing_clear": (good[:-1], len(good)-1, "macro endpoint or private clear"),
        "missing_copy": (good[1:], len(good)-1, "dirty work dependency"),
        "wrong_accumulation_sign": (good[:-2]+[("subtract",t,w)]+good[-1:], len(good), "target prefix"),
        "endpoint_neutral_grid_excursion": (grid, len(grid), "fractional grid"),
        "endpoint_neutral_magnitude_excursion": (growth, len(growth), "magnitude bound"),
        "source_modified_then_restored": ([("double",s),("halve",s)]+good, len(good)+2, "source write"),
        "uncharged_extra_clear": (good+[("clear",w)], len(good), "primitive count"),
    }
    rejected = {}
    for name, (word, cost, reason) in cases.items():
        try:
            macro_check(q, word, cost)
        except ValueError as error:
            need(str(error) == reason, "wrong rejection reason for " + name)
            rejected[name] = str(error)
        else:
            raise ValueError("accepted negative control: " + name)
    for name, op in {
        "source_target_alias": ["add", list(t), list(t), 5, 2],
        "scratch_alias": ["add", list(t), list(w), 5, 2],
        "nondyadic": ["add", list(t), list(s), 5, 3],
        "zero_coefficient": ["add", list(t), list(s), 0, 1],
    }.items():
        try:
            synth.lower(op, entries)
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise ValueError("accepted invalid macro: " + name)
    return rejected


def collect():
    spec = check_pins()
    import synth
    import crosscheck
    import integer_replay
    import pareto
    from replay import replay

    programs = read(PROVIDER / "LOCAL-PROGRAMS.json.gz")
    checks = read(PROVIDER / "LOCAL-CHECKS.json")
    inherited = read(PROVIDER / "INDEPENDENT-LOCAL-REPLAY.json")
    provider_spec = spec["providers"]["jp8"]
    need(set(programs) == {"forward", "backward"}, "orientation coverage")
    need(sha(canonical(programs)) == provider_spec["artifact_semantic_sha256"]["LOCAL-PROGRAMS.json.gz"],
         "SPEC program payload")
    counts = {}
    for orientation, events in programs.items():
        need(sha(canonical(events)) == checks[orientation]["sha256"] ==
             provider_spec["program_hashes"][orientation], "orientation source binding")
        counts[orientation] = Counter(abs(Q(e[1][3],e[1][4])) for e in events
                                      if e[0] == "scalar" and e[1][0] == "add")
    coefficients = sorted({q for counter in counts.values() for q in counter
                           if q != 1 and q.numerator <= 127 and q.denominator <= 16})
    coefficients = coefficients[33:] + coefficients[:33]
    certificate = read(HERE / "CERTIFICATE.json")
    need(certificate["schema"] == "jp8-grid-bounded-synthesis/1" and
         type(certificate["seed"]) is int and certificate["seed"] == 33,
         "certificate identity")
    need(canonical(certificate["domain"]) == canonical(DOMAIN), "certificate search domain")
    rebuilt = []
    for q in coefficients:
        entry = synth.solve(q.numerator, q.denominator)
        entry["horner_macro_costs"] = synth.comparisons(entry)
        entry["strict_horner_improvement"] = synth.improved(entry)
        rebuilt.append(entry)
    # JSON true, 1 and 1.0 have different certificate types although Python
    # equality conflates them. Verify the submitted witness itself after a
    # type-preserving reconstruction comparison, not only the regenerated one.
    need(canonical(certificate["entries"]) == canonical(rebuilt), "certificate reconstruction mismatch")
    independent = crosscheck.run(certificate["entries"], source=PROVIDER / "LOCAL-PROGRAMS.json.gz")
    entries = {Q(x["numerator"],x["denominator"]): x for x in rebuilt}
    census = []
    for q, entry in entries.items():
        # Check every graph witness directly, even when it is not used.
        for sign in (-1, 1):
            t, s, w = ("T",0), ("S",0), ("W",0)
            word = [("copy",w,s)]
            word += [(op,w,s) if op in ("add","subtract") else (op,w)
                     for op in entry["operations"]]
            word += [("add" if sign*entry["end_sign"]>0 else "subtract",t,w),("clear",w)]
            macro_check(sign*q, word, entry["preparation_steps"]+3)
        if synth.improved(entry):
            census.append({"coefficient": str(q), "real_component_macro_cost": entry["preparation_steps"]+3,
                           "horner_macro_costs": entry["horner_macro_costs"],
                           "occurrences": {k: c[q] for k,c in counts.items()},
                           "scratch_operations": entry["operations"]})
    controls = negative_controls(entries)
    complete = replay(programs, checks, inherited, entries)
    integer_result = integer_replay.verify(programs, checks, inherited, certificate)
    for orientation in ("forward", "backward"):
        other = integer_result["programs"][orientation]
        for lowering in ("pr696", "replacement"):
            need(canonical(other["lowerings"][lowering]) ==
                 canonical(complete[orientation]["lowerings"][lowering]),
                 "independent integer primitive trace disagreement")
        for field in ("total_exact_input_columns", "logical_input_columns",
                      "arbitrary_private_input_columns", "arbitrary_helper_columns_restored",
                      "private_registers_erased", "events", "scalar_macros", "changed_macros",
                      "addition_macros_with_coefficient_work_clear", "saved_real_primitives_vs_pr696",
                      "extra_real_source_reads_vs_pr696", "non_scalar_event_indexed_sha256",
                      "scalar_frame_indexed_sha256", "paid_profile"):
            need(canonical(other[field]) == canonical(complete[orientation][field]),
                 "independent integer accounting disagreement: " + field)
    source_read_pareto = pareto.verify(certificate["entries"])
    for orientation in ("forward", "backward"):
        costs = source_read_pareto["selected_occurrence_totals_both_real_components"][orientation]
        need(costs["binary-forward"][0] - costs["current"][0] ==
             complete[orientation]["saved_real_primitives_vs_pr696"],
             "Pareto instruction accounting disagrees with full replay")
        need(costs["current"][1] - costs["binary-forward"][1] ==
             complete[orientation]["extra_real_source_reads_vs_pr696"],
             "Pareto source-read accounting disagrees with full replay")
    comparator_saving = {orientation: 2*sum(
        c[q]*(min(entry["horner_macro_costs"].values()) - entry["preparation_steps"]-3)
        for q,entry in entries.items() if synth.improved(entry))
        for orientation,c in counts.items()}
    return {"status":"PASS_JP8_GRID_BOUNDED_SYNTHESIS", "searched_nonunit_coefficients":len(rebuilt),
            "improved_coefficients":len(census), "improvements":census,
            "saved_real_primitives_vs_four_horner_at_replacements":comparator_saving,
            "full_pr837_composition_claimed":False,
            "independent_graph":independent, "programs":complete,
            "independent_integer_replay":integer_result,
            "source_read_pareto":source_read_pareto,
            "negative_controls":controls, "kappa_claim":None,
            "scope":"Historical PR626 JP8 scalar projections; finite graph class optimum only."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write", type=Path, help="development only: create a new receipt; never overwrite")
    args = parser.parse_args()
    if args.write:
        need(not args.write.exists(), "output already exists")
    result = collect()
    if args.write:
        with args.write.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        need(canonical(result) == canonical(read(HERE / "EXPECTED.json")), "expected receipt mismatch")
    if args.json:
        print(json.dumps(result,indent=2,sort_keys=True))
    else:
        savings = ",".join(str(result["saved_real_primitives_vs_four_horner_at_replacements"][o])
                           for o in ("forward","backward"))
        print(f"{result['status']} coefficients={result['searched_nonunit_coefficients']} "
              f"improved={result['improved_coefficients']} extra_vs_four_horner={savings} "
              "columns=716+9 kappa=unchanged")


if __name__ == "__main__":
    main()
