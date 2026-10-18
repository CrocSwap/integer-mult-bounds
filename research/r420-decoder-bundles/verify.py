"""Exact finite decoder-star construction, with no new kappa claim.

Sagar Thakrar (@thakrarsagar), with substantial OpenAI Codex assistance.
Apache-2.0. Extends the restored disjoint-pair idea of PR708 to disjoint stars.
The source word and geometry/interface checker are eumemic's PR543 work.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
XCHECK = ROOT / "research/e8-bit-r420/code/xcheck.py"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def nominate(word, seed):
    """One oriented-edge census and one greedy star packing, without restarts."""
    rows = [set(g[2]) for g in word["A"][-9:]]
    pool = sorted(set.union(*rows) - set(word["ret"]))
    signatures = {r: sum(1 << i for i, row in enumerate(rows) if r in row) for r in pool}
    weights = {(a, b): 2 * (signatures[a] & signatures[b]).bit_count()
               - signatures[a].bit_count() - 2 for a in pool for b in pool if a != b}
    order = pool[:]
    random.Random(seed).shuffle(order)
    priority = {r: i for i, r in enumerate(order)}
    remaining = set(pool)
    stars, savings = [], []
    while remaining:
        candidates = []
        for a in remaining:
            leaves = sorted((b for b in remaining if b != a and weights[a, b] > 0),
                            key=priority.__getitem__)
            saving = sum(weights[a, b] for b in leaves)
            if saving:
                candidates.append((saving, -priority[a], a, leaves))
        if not candidates:
            break
        saving, _, a, leaves = max(candidates)
        stars.append([a, leaves])
        savings.append(saving)
        remaining.difference_update([a] + leaves)
    return stars, {"operands": len(pool), "oriented_edges_checked": len(weights),
                   "positive_edges": sum(w > 0 for w in weights.values()),
                   "packings_tried": 1, "star_savings": savings,
                   "unselected_operands": len(remaining),
                   "stopping_rule": "no positive edge remains among unused operands"}


def construct(word, stars):
    tail = word["A"][-9:]
    full = next(i for i, frame in enumerate(word["frames"]) if len(frame) == word["v"])
    need([g[1] for g in tail] == word["ret"], "tail is not the nine retained totals")
    need(all(g[0] == full for g in tail), "totals are not at FULL")
    pool = set().union(*(set(g[2]) for g in tail)) - set(word["ret"])
    used = set()
    for a, leaves in stars:
        group = [a] + leaves
        need(leaves and len(group) == len(set(group)), "invalid star")
        need(set(group) <= pool and not used.intersection(group), "stars must be disjoint non-retained operands")
        used.update(group)
    preparation = [[full, a, list(leaves)] for a, leaves in stars]
    totals = []
    for frame, destination, sources in tail:
        row = set(sources)
        for a, leaves in stars:
            if a in row:
                row.symmetric_difference_update(leaves)
        totals.append([frame, destination, sorted(row)])
    result = copy.deepcopy(word)
    result["A"] = result["A"][:-9] + preparation + totals + preparation[::-1]
    v = word["v"]
    result["C"] = [[full, d, list(s)] for _, d, s in reversed(result["A"] + result["B"])
                   if not v <= d < 2*v]
    return result


def scalar(gates, n):
    values = [1 << i for i in range(n)]
    for _, destination, sources in gates:
        for source in sources:
            values[destination] ^= values[source]
    return values


def additions(word):
    return sum(len(g[2]) for section in "DABC" for g in word[section]) + sum(map(len, word["scatter"]))


def check_pins(word):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(digest(word) == pins["word_canonical_sha256"], "word semantic pin mismatch")
    for name, expected in pins["files_sha256"].items():
        need(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, "source pin mismatch: " + name)


def verify(baseline, stars, search):
    candidate = construct(baseline, stars)
    n = 2 * baseline["v"] + baseline["R"]
    need(scalar(baseline["A"], n) == scalar(candidate["A"], n), "complete A operator changed")
    need(additions(baseline) - additions(candidate) == 2 * sum(search["star_savings"]), "paid saving mismatch")
    spec = importlib.util.spec_from_file_location("r420_xcheck", XCHECK)
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    for word in (baseline, candidate):
        _, _, _, hypotheses, conclusions, _ = checker.check(word)
        need(all(hypotheses.values()) and all(conclusions.values()), "original H1-H5 or conclusion failed")
    import audit
    independent = audit.compare(baseline, candidate)
    need(independent["status"] == "PASS", "independent audit failed")
    controls = []

    def rejects(name, action):
        try:
            action()
        except (ValueError, checker.Reject):
            controls.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    def same_a(word):
        need(scalar(word["A"], n) == scalar(baseline["A"], n), "A operator mismatch")

    missing = copy.deepcopy(candidate)
    missing["A"].pop()
    rejects("missing star restoration", lambda: same_a(missing))
    need(audit.compare(baseline, missing)["status"] == "FAIL", "independent audit missed restoration failure")
    wrong = copy.deepcopy(candidate)
    begin = len(baseline["A"]) - 9 + len(stars)
    hub, leaves = stars[0]
    index = next(i for i, g in enumerate(baseline["A"][-9:]) if hub in g[2])
    wrong["A"][begin + index][2] = sorted(set(wrong["A"][begin + index][2]) ^ {leaves[0]})
    rejects("uncancelled decoder operand", lambda: same_a(wrong))
    need(audit.compare(baseline, wrong)["status"] == "FAIL", "independent audit missed decoder failure")
    stale = copy.deepcopy(candidate)
    stale["C"] = baseline["C"]
    checker.Word(stale).full()
    rejects("scalar-valid nonliteral cleanup", lambda: need(
        checker.Word(stale).interface()[0]["H4_C_literal_reverse_at_full"], "H4 mismatch"))
    early = copy.deepcopy(candidate)
    early["A"][len(baseline["A"]) - 9][0] = next(i for i, f in enumerate(baseline["frames"]) if not f)
    rejects("unpaid frame-zero preparation", lambda: checker.Word(early).full())
    rejects("retained register used as hub", lambda: construct(baseline, [[baseline["ret"][0], leaves]]))
    rejects("overlapping stars", lambda: construct(baseline, stars + [stars[0]]))
    dirty = copy.deepcopy(candidate)
    dirty["D"][0][2].pop()
    rejects("missing dirty compensation", lambda: checker.Word(dirty).full())
    raw = copy.deepcopy(baseline)
    raw["A"][0][2] = []
    rejects("changed source word", lambda: check_pins(raw))
    # This three-register restriction separates stars from disjoint pairs.
    group = [515, 489, 347]
    need([group[0], group[1:]] in stars, "separating star absent")
    rows = [set(g[2]) for g in baseline["A"][-9:]]
    weights = [[a, b, sum(1 if b in row else -1 for row in rows if a in row) - 2]
               for a in group for b in group if a != b]
    star_saving = sum(gain for a, _, gain in weights if a == group[0])
    pair_ceiling = max(0, *(gain for _, _, gain in weights))
    need(star_saving == 4 and pair_ceiling == 2, "three-register separation failed")
    report = {"status": "PASS_R420_DECODER_BUNDLES", "assignment_seed": 19,
              "search": search, "stars": len(stars), "edges": sum(len(bs) for _, bs in stars),
              "columns": n, "decoder_additions_before": sum(len(g[2]) for g in baseline["A"][-9:]),
              "decoder_additions_after": sum(len(g[2]) for g in candidate["A"][-(9+2*len(stars)):]),
              "native_additions_before": additions(baseline), "native_additions_after": additions(candidate),
              "saved_with_cleanup": additions(baseline) - additions(candidate),
              "baseline_canonical_sha256": digest(baseline), "candidate_canonical_sha256": digest(candidate),
              "original_H1_H5": True, "independent": independent, "negative_controls": controls,
              "three_register_separation": {"group": group, "all_oriented_edge_weights": weights,
                  "star_saving": star_saving, "disjoint_pair_ceiling": pair_ceiling},
              "kappa_claim": "none"}
    return candidate, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for reconstructed words and report")
    args = parser.parse_args()
    need(__debug__, "run without -O: inherited checkers require assertions")
    baseline = json.loads(gzip.decompress(WORD.read_bytes()))
    check_pins(baseline)
    recipe = json.loads((HERE / "recipe.json").read_text())
    need(recipe["seed"] == 19, "assignment seed changed")
    stars, search = nominate(baseline, recipe["seed"])
    need(stars == recipe["stars"], "frozen recipe differs from bounded nomination")
    need(search == recipe["search"], "search coverage or stopping rule changed")
    candidate, report = verify(baseline, stars, search)
    need(report == json.loads((HERE / "CERTIFICATE.json").read_text()), "certificate mismatch")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        for name, word in (("baseline", baseline), ("candidate", candidate)):
            (args.output / (name + ".json.gz")).write_bytes(gzip.compress(canonical(word), mtime=0))
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    print("PASS_R420_DECODER_BUNDLES decoder=321->257 native_ADDs=26916->26788 saved=128 columns=660 controls=8 no_new_kappa")


if __name__ == "__main__":
    main()
