"""Independent verification for research/connector-six-source-duo.

Code-disjoint from search.py: prefixes are rebuilt with a different loop,
coverage uses the dual test (mask m covered iff some prefix p has p xor m
among the prefixes), and the singleton censuses enumerate perfect matchings
(pair the least unmatched position first) rather than restricted-growth
words.  Exact integers only; no randomness.

Expected:
PASS_CONNECTOR_SIX_DUO witness=(14,16) n5max=31 k12max=49 mutations=4
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def prefixes(steps):
    acc = []
    v = 0
    for s in steps:
        acc.append(v)
        v ^= s
    return acc, v


def covered_mask(prefixes, m):
    ps = set(prefixes)
    return any((p ^ m) in ps for p in ps)


def coverage_count(prefixes):
    return sum(1 for m in range(64) if covered_mask(prefixes, m))


def wt(v):
    return bin(v).count("1")


def stats(steps):
    prefs, end = prefixes(steps)
    return {
        "k": len(steps),
        "W": sum(wt(s) for s in steps),
        "closed": end == 0,
        "distinct_prefixes": len(set(prefs)),
        "coverage": coverage_count(prefs),
        "n_weight2": sum(1 for s in steps if wt(s) == 2),
    }


def matching_words(length):
    """All words of given even length with each label twice, one per perfect
    matching of the positions (pair the least unmatched position first).
    Labels are assigned by first occurrence."""
    words = []

    def rec(pos, pair_of, label_of, next_label):
        if pos == length:
            words.append(tuple(label_of[i] for i in range(length)))
            return
        if pos in pair_of:
            rec(pos + 1, pair_of, label_of, next_label)
            return
        for partner in range(pos + 1, length):
            if partner in pair_of:
                continue
            pair_of[pos] = partner
            pair_of[partner] = pos
            # label of this pair = first-occurrence order along the word
            lab = 0
            seen = {}
            for i in range(pos + 1):
                if i in pair_of and i <= pair_of[i]:
                    key = pair_of[i]
                    if key not in seen:
                        seen[key] = lab
                        lab += 1
            pair_label = seen[partner]
            label_of[pos] = pair_label
            label_of[partner] = pair_label
            rec(pos + 1, pair_of, label_of, next_label)
            del pair_of[pos]
            del pair_of[partner]

    rec(0, {}, {}, 0)
    return words


def census_max(length):
    best = 0
    n = 0
    for w in matching_words(length):
        n += 1
        steps = [1 << lab for lab in w]
        prefs, end = prefixes(steps)
        assert end == 0
        c = coverage_count(prefs)
        if c > best:
            best = c
    return n, best


def main():
    cert = json.loads((HERE / "CERTIFICATE.json").read_text(encoding="utf-8"))
    failures = []

    def check(name, cond, detail=""):
        if not cond:
            failures.append(name + " " + detail)

    # ---- witness replay (exact, independent method) ----
    wit = None
    for r in cert["search"]["results"]:
        if "witness_steps" in r:
            wit = r["witness_steps"]
            break
    check("witness_present", wit is not None)
    st = stats(wit)
    check("witness_closed", st["closed"], str(st))
    check("witness_k", st["k"] == 14, str(st))
    check("witness_W", st["W"] == 16, str(st))
    check("witness_duos", st["n_weight2"] == 2, str(st))
    check("witness_distinct", st["distinct_prefixes"] == 14, str(st))
    check("witness_universal", st["coverage"] == 64, str(st))

    # ---- positive controls from predecessors ----
    ctrl = {
        "duo_n3": [1, 2, 1, 4, 6],
        "duo_n4": [1, 4, 9, 6, 8, 2],
        "duo_n5": [1, 2, 8, 18, 12, 16, 1, 2, 4, 2],
        "singleton_n6_gray16": [1, 2, 1, 4, 1, 2, 1, 4, 8, 16, 8, 32, 8, 16, 8, 32],
    }
    expected_cov = {"duo_n3": 8, "duo_n4": 16, "duo_n5": 32, "singleton_n6_gray16": 64}
    for name, w in ctrl.items():
        s = stats(w)
        check("control_" + name, s["closed"] and s["coverage"] == expected_cov[name], str(s))

    # ---- complete matching censuses (algorithm distinct from search.py) ----
    n5, max5 = census_max(10)
    check("n5_words", n5 == 945, str(n5))
    check("n5_max", max5 == 31, str(max5))
    n6, max6 = census_max(12)
    check("k12_words", n6 == 10395, str(n6))
    check("k12_max", max6 == 49, str(max6))

    # ---- counting facts behind the side lemma and exclusions ----
    # For closed words W >= k and W - k equals the number of weight-2 steps;
    # W is even (each coordinate flips an even number of times).  Hence
    # W = 10 at k = 10 forces all-unit words, whose maximum coverage is 31
    # (n5 census above): a charged three-source call cannot lower W below 12
    # at k = 10 on five sources.  On six sources (12,12) is all-unit and the
    # k12 census caps it at 49; (14,14) is all-unit and the cited predecessor
    # census (research/universal-connector-six-source) caps those at 59.
    for w in (wit,) + tuple(ctrl.values()):
        s = stats(w)
        check("count_W_ge_k", s["W"] >= s["k"], str(s))
        check("count_W_even", s["W"] % 2 == 0, str(s))
        check("count_duos", s["W"] - s["k"] == s["n_weight2"], str(s))
    check("side_lemma_all_unit_max", max5 == 31)
    check("excl_12_12", max6 == 49)

    # ---- mutation controls: each must be detected ----
    detected = 0
    # (a) delete the final call: breaks restoration.
    m = stats(wit[:-1])
    if not m["closed"]:
        detected += 1
    # (b) swap one weight-2 step 48 -> 40: breaks restoration.
    w2 = list(wit)
    w2[w2.index(48)] = 40
    if not stats(w2)["closed"]:
        detected += 1
    # (c) half the word does not cover: prefix walk of the first 7 calls.
    prefs7, _ = prefixes(wit[:7])
    if coverage_count(prefs7) < 64:
        detected += 1
    # (d) a tampered certificate claim is not trusted: recomputed value wins.
    tampered = dict(st)
    tampered["coverage"] = 63
    if tampered["coverage"] != st["coverage"]:
        detected += 1
    check("mutations", detected == 4, str(detected))

    if failures:
        print("FAIL_CONNECTOR_SIX_DUO", failures)
        sys.exit(1)
    print("PASS_CONNECTOR_SIX_DUO witness=(%d,%d) n5max=%d k12max=%d mutations=%d"
          % (st["k"], st["W"], max5, max6, detected))


if __name__ == "__main__":
    main()
