"""Scoped barrier: restored pair sharing cannot reach the selected R439 word's copy path.

Assignment seed 42 (structural decoder research). The selected #589 R439 bit
word is priced along three avenues before any large implementation:

  T. decoder totals: nine retained totals read 27 sources with pairwise
     disjoint source sets, so oriented-pair sharing is vacuous;
  D. frame-zero dirt section: 43k+ arithmetically positive oriented pairs,
     but every helper-writing D gate violates H2 of the unchanged interface
     lemma, and target-written temps provably save nothing;
  A. same-frame A groups: bounded greedy nomination totals 1 ADD.

Controls C1-C3 run the unchanged xcheck_p checker against constructed
variants to separate scalar-valid from interface-legal. Apache-2.0.
"""
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import random
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
XCHECK = ROOT / "research/e8-bit-p111-tuned/code/xcheck_p.py"
SEED = 42


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_checker():
    spec = importlib.util.spec_from_file_location("r439_xcheck_p", XCHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_pins(word):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(hashlib.sha256(canonical(word)).hexdigest() == pins["word_canonical_sha256"],
         "word semantic pin mismatch")
    for name, expected in pins["files_sha256"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
             "source pin mismatch: " + name)


def census_totals(word):
    """Late retained-total gates: reads per total and pairwise source overlap."""
    ret = set(word["ret"])
    early = [g for g in word["A"] if g[1] in ret and len(g[2]) == 1 and g[0] < 100]
    late = [g for g in word["A"] if g[1] in ret and g[0] >= 100]
    by_total = defaultdict(set)
    for g in late:
        by_total[g[1]].update(g[2])
    by_total = dict(sorted(by_total.items()))
    overlap = [(r, s) for r, s in itertools.combinations(sorted(by_total), 2)
               if by_total[r] & by_total[s]]
    return {"early_single_source_gates": len(early),
            "late_total_gates": len(late),
            "late_source_reads": sum(len(g[2]) for g in late),
            "per_total_sources": {str(k): sorted(v) for k, v in by_total.items()},
            "overlapping_total_pairs": [[r, s] for r, s in overlap]}


def nominate_d(word, seed):
    """Exhaustive oriented-pair census over D rows, then one seeded greedy matching."""
    v, ret = word["v"], set(word["ret"])
    rows = [set(g[2]) for g in word["D"]]
    pool = sorted(set.union(*rows) - ret - set(range(2 * v)))
    need(min(pool) >= 2 * v, "D reads a non-helper")
    scored = []
    for a, b in itertools.permutations(pool, 2):
        saving = sum((1 if b in row else -1) for row in rows if a in row) - 2
        if saving > 0:
            scored.append((saving, a, b))
    random.Random(seed).shuffle(scored)
    scored.sort(key=lambda item: -item[0])
    chosen, used, total = [], set(), 0
    for saving, a, b in scored:
        if a not in used and b not in used:
            chosen.append([a, b])
            used.update((a, b))
            total += saving
    return chosen, {"operands": len(pool), "oriented_pairs": len(pool) * (len(pool) - 1),
                    "positive_pairs": len(scored),
                    "best_saving": scored[0][0] if scored else 0,
                    "best_pair": list(scored[0][1:]) if scored else [],
                    "matching_pairs": len(chosen), "matching_saving": total}


def construct_d(word, pairs):
    """Wrap the whole D section in prep/restore temporaries (helper temps)."""
    v, ret = word["v"], set(word["ret"])
    rows_pool = set().union(*(set(g[2]) for g in word["D"]))
    flat = [r for pair in pairs for r in pair]
    need(all(len(pair) == 2 for pair in pairs), "malformed pair")
    need(len(flat) == len(set(flat)), "pairs must be disjoint")
    need(all(r >= 2 * v and r not in ret for r in flat) and set(flat) <= rows_pool,
         "temps must be non-retained D-operand helpers")
    pre = [[0, a, [b]] for a, b in pairs]
    body = []
    for frame, dst, srcs in word["D"]:
        need(frame == 0 and v <= dst < 2 * v, "D gate not frame-zero target write")
        row = set(srcs)
        for a, b in pairs:
            if a in row:
                row.symmetric_difference_update({b})
        body.append([frame, dst, sorted(row)])
    result = copy.deepcopy(word)
    result["D"] = pre + body + list(reversed(pre))
    return result


def census_a_sameframe(word, seed):
    """Bounded greedy pair-sharing nomination inside each same-frame A group."""
    ret = set(word["ret"])
    byframe = defaultdict(list)
    for g in word["A"]:
        byframe[g[0]].append(g)
    rng = random.Random(seed)
    total, groups = 0, 0
    for frame in sorted(byframe):
        gates = byframe[frame]
        rows = [set(g[2]) for g in gates if len(g[2]) > 1]
        if len(rows) < 2:
            continue
        dsts = set(g[1] for g in gates)
        pool = sorted(set.union(*rows) - ret - dsts)
        if len(pool) < 2:
            continue
        scored = []
        for a, b in itertools.permutations(pool, 2):
            saving = sum((1 if b in row else -1) for row in rows if a in row) - 2
            if saving > 0:
                scored.append((saving, a, b))
        rng.shuffle(scored)
        scored.sort(key=lambda item: -item[0])
        used = set()
        for saving, a, b in scored:
            if a not in used and b not in used:
                used.update((a, b))
                total += saving
                groups += 1
    return {"positive_groups": groups, "greedy_saving": total}


def main():
    need(__debug__, "run without -O: inherited checker requires assertions")
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    check_pins(word)
    checker = load_checker()
    _, _, _, hypotheses, conclusions, _ = checker.check(word)
    need(all(hypotheses.values()) and all(conclusions.values()), "baseline H1-H5 failed")

    totals = census_totals(word)
    need(totals["late_source_reads"] == 27, "unexpected decoder-total reads")
    need(totals["overlapping_total_pairs"] == [], "decoder totals share sources")

    matching, d_census = nominate_d(word, SEED)
    need(matching, "expected arithmetically positive D pairs")

    a_census = census_a_sameframe(word, SEED)

    def values_d(w):
        return checker.Word(w).replay(sections=("D",), frames_on=False)[0]

    base_d = values_d(word)
    controls = []

    # C1: full helper-temp construction preserves the scalar D operator but
    # violates H2 (D gates must write targets).
    full_variant = construct_d(word, [matching[0]])
    need(values_d(full_variant) == base_d, "C1 construction changed the D operator")
    checker.Word(full_variant).full()
    h2 = checker.Word(full_variant).interface()[0]["H2_D_frame0_targets_from_helpers"]
    need(h2 is False, "C1 construction unexpectedly satisfies H2")
    controls.append("helper-temp D construction scalar-valid but H2-rejected")

    # C2: target-written temps are H2-legal (writes a target, reads a helper)
    # but provably useless: no target appears in any D source set.
    need(all(all(s >= 2 * word["v"] for s in g[2]) for g in word["D"]),
         "a target feeds D")
    target, helper = word["D"][0][1], matching[0][1]
    need(not any(target in g[2] for g in word["D"]), "target temp occurs in D sources")
    legal = copy.deepcopy(word)
    legal["D"] = [[0, target, [helper]]] + [list(g) for g in word["D"]] + [[0, target, [helper]]]
    need(values_d(legal) == base_d, "C2 variant changed the D operator")
    checker.Word(legal).full()
    need(checker.Word(legal).interface()[0]["H2_D_frame0_targets_from_helpers"] is True,
         "C2 variant unexpectedly violates H2")
    need(sum(len(g[2]) for g in legal["D"]) - sum(len(g[2]) for g in word["D"]) == 2,
         "C2 variant cost is not exactly +2")
    controls.append("target-temp D construction H2-legal but +2 with no saving")

    # C3: prep without restoration is caught by the endpoint check.
    unrestored = copy.deepcopy(full_variant)
    del unrestored["D"][-1]
    try:
        checker.Word(unrestored).full()
    except checker.Reject:
        controls.append("unrestored helper temp rejected at endpoints")
    else:
        raise ValueError("negative control accepted: unrestored helper temp")

    report = {"status": "PASS_R439_COPY_PATH_SHARING_BARRIER", "assignment_seed": SEED,
              "columns": 2 * word["v"] + word["R"], "decoder_totals": totals,
              "d_section": dict(d_census, greedy_matching=matching),
              "a_sameframe": a_census,
              "baseline_canonical_sha256": hashlib.sha256(canonical(word)).hexdigest(),
              "original_H1_H5": True, "negative_controls": controls, "kappa_claim": "none"}
    certificate = HERE / "CERTIFICATE.json"
    if certificate.exists():
        need(report == json.loads(certificate.read_text()), "certificate mismatch")
    else:
        (HERE / "DRAFT-REPORT.json").write_text(json.dumps(report, indent=2) + "\n")
        print("draft report written; inspect DRAFT-REPORT.json, then freeze as CERTIFICATE.json")
    print("PASS_R439_COPY_PATH_SHARING_BARRIER totals_reads=%d d_positive=%d d_best=%d "
          "a_sameframe=%d controls=%d no_new_kappa"
          % (totals["late_source_reads"], d_census["positive_pairs"], d_census["best_saving"],
             a_census["greedy_saving"], len(controls)))


if __name__ == "__main__":
    main()
