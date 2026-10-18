#!/usr/bin/env python3
"""Ordered R420 decoder chains. Adam Gall; substantial OpenAI Codex assistance.
Apache-2.0. Reuses Sagar Thakrar's PR708 auditor and eumemic's PR543 checker.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / "research/r420-decoder-sharing"
WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def transform(rows, chain):
    rows = [set(row) for row in rows]
    for a, b in chain:
        for row in rows:
            if a in row:
                row.symmetric_difference_update({b})
    return rows


def nominate(word, initial):
    original = [set(g[2]) for g in word["A"][-9:]]
    pool = sorted(set.union(*original) - set(word["ret"]))
    rows = transform(original, initial)
    rng = random.Random(7)
    chain, census = list(map(list, initial)), []
    for step in range(7):
        scores = [(sum(1 if b in row else -1 for row in rows if a in row) - 2,
                   rng.random(), a, b) for a in pool for b in pool if a != b]
        gain, _, a, b = max(scores)
        census.append({"step": step, "pairs_scored": len(scores),
                       "positive_pairs": sum(s[0] > 0 for s in scores),
                       "best_gain": gain, "chosen": [a, b]})
        if gain <= 0:
            break
        chain.append([a, b])
        rows = transform(rows, [[a, b]])
    return chain, census


def construct(word, chain):
    tail = word["A"][-9:]
    need([g[1] for g in tail] == word["ret"], "unexpected retained-total suffix")
    need(all(g[0] == 1 for g in tail), "non-FULL suffix")
    pool = set.union(*(set(g[2]) for g in tail)) - set(word["ret"])
    need(all(len(p) == 2 and p[0] != p[1] and set(p) <= pool for p in chain),
         "invalid non-retained helper shear")
    prefix = [[1, a, [b]] for a, b in chain]
    rows = transform([g[2] for g in tail], chain)
    result = copy.deepcopy(word)
    result["A"] = word["A"][:-9] + prefix + [
        [f, d, sorted(row)] for (f, d, _), row in zip(tail, rows)] + prefix[::-1]
    result["C"] = [[1, d, list(s)] for _, d, s in reversed(result["A"] + result["B"])
                   if not word["v"] <= d < 2 * word["v"]]
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--output", type=Path, help="new directory for native input words")
    args = parser.parse_args()
    need(__debug__, "run without -O; inherited checker uses assertions")
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, digest in pins["files_sha256"].items():
        need(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, "source pin: " + path)
    prior = load("prior_decoder", PRIOR / "verify.py")
    audit = load("decoder_audit", PRIOR / "audit.py")
    base = json.loads(gzip.decompress(WORD.read_bytes()))
    initial = json.loads((PRIOR / "recipe.json").read_text())["pairs"]
    chain, census = nominate(base, initial)
    candidate = construct(base, chain)
    n = 2 * base["v"] + base["R"]
    need(prior.scalar(candidate["A"], n) == prior.scalar(base["A"], n), "dirty A operator")
    independent = audit.compare(base, candidate)
    need(independent["status"] == "PASS", "independent whole-word/frame audit")
    checker = prior.load_checker()
    for word in (base, candidate):
        _, _, _, hypotheses, conclusions, _ = checker.check(word)
        need(all(hypotheses.values()) and all(conclusions.values()), "original interface")
    controls = []

    def reject(name, action):
        try:
            action()
        except (ValueError, checker.Reject):
            controls.append(name)
        else:
            raise ValueError("accepted control: " + name)

    def equal_a(word):
        need(prior.scalar(word["A"], n) == prior.scalar(base["A"], n), "A mismatch")

    missing = copy.deepcopy(candidate)
    missing["A"].pop()
    reject("missing restoration", lambda: equal_a(missing))
    wrong_order = copy.deepcopy(candidate)
    wrong_order["A"][-len(chain):] = wrong_order["A"][-len(chain):][::-1]
    reject("forward-order restoration", lambda: equal_a(wrong_order))
    wrong_rows = copy.deepcopy(candidate)
    wrong_rows["A"][-len(chain)-9:-len(chain)] = copy.deepcopy(base["A"][-9:])
    reject("untransformed decoder rows", lambda: equal_a(wrong_rows))
    wrong_transform = copy.deepcopy(candidate)
    reversed_rows = transform([g[2] for g in base["A"][-9:]], chain[::-1])
    wrong_transform["A"][-len(chain)-9:-len(chain)] = [
        [f, d, sorted(r)] for (f, d, _), r in zip(base["A"][-9:], reversed_rows)]
    reject("reverse-order covector substitution", lambda: equal_a(wrong_transform))
    stale = copy.deepcopy(candidate)
    stale["C"] = copy.deepcopy(base["C"])
    # Endpoint equality alone permits this; literal H4 does not.
    checker.Word(stale).full()
    reject("scalar-valid stale cleanup", lambda: need(
        checker.Word(stale).interface()[0]["H4_C_literal_reverse_at_full"], "literal H4"))
    early = copy.deepcopy(candidate)
    early["A"][-2*len(chain)-9][0] = 0
    reject("illegal preparation frame", lambda: checker.Word(early).full())
    reject("retained operand", lambda: construct(base, [[base["ret"][0], chain[0][1]]]))
    bad_d = copy.deepcopy(candidate)
    bad_d["D"][0][2].pop()
    reject("missing dirt compensation", lambda: checker.Word(bad_d).full())
    for corrupted in (missing, wrong_order, wrong_rows, wrong_transform):
        need(audit.compare(base, corrupted)["status"] == "FAIL", "independent control missed")
    noncommuting = [[i, j] for i, (a, b) in enumerate(chain)
                   for j, (c, d) in enumerate(chain) if i < j and (a == d or b == c)]
    need(noncommuting, "candidate collapses to commuting-star class")
    report = {
        "status": "PASS_R420_DECODER_CHAIN", "seed": 7, "chain": chain,
        "search": census, "stopping_rule": "seven accepted adaptive shears, not a fixed point",
        "noncommuting_shear_pairs": noncommuting, "columns": n,
        "decoder_before": sum(len(g[2]) for g in base["A"][-9:]),
        "decoder_after": sum(len(g[2]) for g in candidate["A"][-2*len(chain)-9:]),
        "native_additions_before": prior.additions(base),
        "native_additions_after": prior.additions(candidate),
        "baseline_canonical_sha256": hashlib.sha256(canonical(base)).hexdigest(),
        "candidate_canonical_sha256": hashlib.sha256(canonical(candidate)).hexdigest(),
        "independent": independent, "negative_controls": controls, "kappa_claim": "none"}
    target = HERE / "CERTIFICATE.json"
    if args.write_certificate:
        with target.open("x") as stream:
            stream.write(json.dumps(report, indent=2) + "\n")
    else:
        need(report == json.loads(target.read_text()), "certificate mismatch")
    if args.output:
        args.output.mkdir(parents=True, exist_ok=False)
        for name, word in (("baseline", base), ("candidate", candidate)):
            (args.output / (name + ".json.gz")).write_bytes(gzip.compress(canonical(word), mtime=0))
    print(f"PASS_R420_DECODER_CHAIN decoder={report['decoder_before']}->{report['decoder_after']} "
          f"ADDs={report['native_additions_before']}->{report['native_additions_after']} "
          f"columns={n} controls={len(controls)} noncommuting={len(noncommuting)} no_new_kappa")


if __name__ == "__main__":
    main()
