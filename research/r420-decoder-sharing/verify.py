"""Finite R420 decoder-total circuit check. Apache-2.0.

Prepared for Sagar Thakrar (@thakrarsagar) with substantial OpenAI Codex assistance.
Uses eumemic's unchanged PR543 xcheck; independent replay is in audit.py.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
XCHECK = ROOT / "research/e8-bit-r420/code/xcheck.py"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def nominate(word, seed):
    """One exhaustive pair census, then one seeded greedy disjoint matching."""
    rows = [set(g[2]) for g in word["A"][-9:]]
    pool = sorted(set.union(*rows) - set(word["ret"]))
    scored = []
    for a, b in itertools.permutations(pool, 2):
        saving = sum((1 if b in row else -1) for row in rows if a in row) - 2
        if saving > 0:
            scored.append((saving, a, b))
    random.Random(seed).shuffle(scored)
    scored.sort(key=lambda item: -item[0])
    chosen, used = [], set()
    for saving, a, b in scored:
        if a not in used and b not in used:
            chosen.append([a, b])
            used.update((a, b))
    return chosen, dict(operands=len(pool), oriented_pairs=len(pool)*(len(pool)-1),
                        positive_pairs=len(scored), matchings_tried=1)


def construct(word, pairs):
    tail = word["A"][-9:]
    need([g[1] for g in tail] == word["ret"], "tail is not the retained-total circuit")
    need(all(g[0] == 1 for g in tail), "totals not at FULL")
    pool = set().union(*(set(g[2]) for g in tail)) - set(word["ret"])
    flat = [r for pair in pairs for r in pair]
    need(all(len(pair) == 2 for pair in pairs), "malformed pair")
    need(len(flat) == len(set(flat)) and set(flat) <= pool, "pairs must be disjoint non-retained operands")
    prefix = [[1, a, [b]] for a, b in pairs]
    transformed = []
    for frame, dst, srcs in tail:
        row = set(srcs)
        for a, b in pairs:
            if a in row:
                row.symmetric_difference_update({b})
        transformed.append([frame, dst, sorted(row)])
    result = copy.deepcopy(word)
    result["A"] = result["A"][:-9] + prefix + transformed + list(reversed(prefix))
    v = word["v"]
    result["C"] = [[1, d, list(srcs)] for _, d, srcs in reversed(result["A"] + result["B"])
                   if not v <= d < 2*v]
    return result


def scalar(gates, n):
    values = [1 << r for r in range(n)]
    for _, dst, srcs in gates:
        for source in srcs:
            values[dst] ^= values[source]
    return values


def additions(word):
    return sum(len(g[2]) for sec in "DABC" for g in word[sec]) + sum(map(len, word["scatter"]))


def check_pins(word):
    pins = json.loads((HERE / "SOURCES.json").read_text())
    need(hashlib.sha256(canonical(word)).hexdigest() == pins["word_canonical_sha256"], "word semantic pin mismatch")
    for name, expected in pins["files_sha256"].items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, "source pin mismatch: " + name)


def load_checker():
    spec = importlib.util.spec_from_file_location("r420_xcheck", XCHECK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="new directory for reconstructed words and report")
    parser.add_argument("--show-report", action="store_true")
    args = parser.parse_args()
    need(__debug__, "run without -O: inherited checkers require assertions")
    baseline = json.loads(gzip.decompress(WORD.read_bytes()))
    check_pins(baseline)
    recipe = json.loads((HERE / "recipe.json").read_text())
    pairs, search = nominate(baseline, recipe["seed"])
    need(pairs == recipe["pairs"], "frozen recipe differs from bounded nomination")
    candidate = construct(baseline, pairs)
    n = 2*baseline["v"] + baseline["R"]
    need(scalar(baseline["A"], n) == scalar(candidate["A"], n), "complete A operator changed")
    need(all(candidate[k] == baseline[k] for k in baseline if k not in ("A", "C")), "unrelated field changed")
    checker = load_checker()
    for word in (baseline, candidate):
        _, _, _, hypotheses, conclusions, _ = checker.check(word)
        need(all(hypotheses.values()) and all(conclusions.values()), "original H1-H5 or conclusion failed")
    import audit
    independent = audit.compare(baseline, candidate)
    need(independent["status"] == "PASS", "independent comparison failed")
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
    del missing["A"][-1]
    rejects("missing helper restoration", lambda: same_a(missing))
    need(audit.compare(baseline, missing)["status"] == "FAIL", "independent checker missed unrestored helper")
    wrong = copy.deepcopy(candidate)
    wrong["A"][-len(pairs)-9][2].append(pairs[0][1])
    rejects("uncancelled decoder operand", lambda: same_a(wrong))
    need(audit.compare(baseline, wrong)["status"] == "FAIL", "independent checker missed changed decoder")
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(baseline["C"])
    # Equal A operators make old cleanup scalar-valid, but it is not literal H4.
    checker.Word(stale).full()
    rejects("scalar-valid nonliteral cleanup", lambda: need(
        checker.Word(stale).interface()[0]["H4_C_literal_reverse_at_full"], "H4 mismatch"))
    early = copy.deepcopy(candidate)
    early["A"][-len(pairs)*2-9][0] = 0
    rejects("illegal frame-zero preparation", lambda: checker.Word(early).full())
    rejects("retained register used as temporary", lambda: construct(baseline, [[baseline["ret"][0], pairs[0][1]]]))
    rejects("overlapping temporary pairs", lambda: construct(baseline, pairs + [pairs[0]]))
    bad_d = copy.deepcopy(candidate)
    bad_d["D"][0][2].pop()
    rejects("missing dirty compensation", lambda: checker.Word(bad_d).full())

    report = dict(status="PASS_R420_DECODER_SHARING", assignment_seed=recipe["seed"],
                  search=search, pairs=len(pairs), columns=n,
                  decoder_additions_before=sum(len(g[2]) for g in baseline["A"][-9:]),
                  decoder_additions_after=sum(len(g[2]) for g in candidate["A"][-(9+2*len(pairs)):]),
                  native_additions_before=additions(baseline), native_additions_after=additions(candidate),
                  saved_with_cleanup=additions(baseline)-additions(candidate),
                  baseline_canonical_sha256=hashlib.sha256(canonical(baseline)).hexdigest(),
                  candidate_canonical_sha256=hashlib.sha256(canonical(candidate)).hexdigest(),
                  original_H1_H5=True, independent=independent, negative_controls=controls,
                  kappa_claim="none")
    certificate = HERE / "CERTIFICATE.json"
    need(report == json.loads(certificate.read_text()), "certificate mismatch")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        for name, word in (("baseline", baseline), ("candidate", candidate)):
            (args.output / (name + ".json.gz")).write_bytes(gzip.compress(canonical(word), mtime=0))
        (args.output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    if args.show_report:
        print(json.dumps(report, indent=2))
    print("PASS_R420_DECODER_SHARING decoder=321->264 native_ADDs=26916->26802 saved=114 columns=660 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
