#!/usr/bin/env python3
"""Independent soundness check of PR #4585 (mihir-s-05): receiver-window floors via mandatory contacts and bridges.

#4585 (head 025f37fe; CERTIFICATE.json vendored, blob 74424627, sha256-pinned) lists per window a set of coarsened
"relaxed_partitions" and proves that every finite scalar-shear word costs at least the incumbent. Its argument needs
every actually realisable word profile to be listed or to refine (split into) a listed partition; concavity then
carries the floor. #4585's sets differ from the identical sets of #4567/#4581/#4582/#4587 in 33 windows, so this is
checked directly against exact geometry:

  * the 128 windows are extracted from main's #4470 constructor by windows_lib.py (my #4567 code);
  * every word of length <= 5 with the window endpoint is enumerated (unit shears), and an exact search over actual
    nested subspaces of F_2^9 (joint incidence enforced across all gates) yields every exactly realisable profile;
  * each realisable profile must be listed or refine a listed partition (exact multiset bin-packing);
  * the incumbent must be listed and dominate every listed partition in capped rank sums (equal mass,
    sum min(r, k) for k <= 9), the certificate #4585 uses for every concave price.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
CERT = HERE / "PR4585-CERTIFICATE.json"
CERT_SHA256 = "bb5c60a41074ea26d09f263755426b7db4a80b369de5daa64fa63be2d3fd66f7"
MAX_LEN = 5


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def part(h):
    return tuple(sorted((r for r, n in enumerate(h) for _ in range(n)), reverse=True))


def refines(R, C):
    R, C = tuple(sorted(R, reverse=True)), tuple(sorted(C, reverse=True))
    if sum(R) != sum(C):
        return False

    @lru_cache(None)
    def go(rest, caps):
        if not rest:
            return all(c == 0 for c in caps)
        x, tail, seen = rest[0], rest[1:], set()
        for i, cap in enumerate(caps):
            if cap >= x and cap not in seen:
                seen.add(cap)
                nc = list(caps)
                nc[i] -= x
                if go(tail, tuple(sorted(nc, reverse=True))):
                    return True
        return False

    return go(R, C)


def main():
    ns = {"__name__": "windows_lib", "__file__": str(HERE / "windows_lib.py")}
    exec(compile((HERE / "windows_lib.py").read_bytes(), str(HERE / "windows_lib.py"), "exec"), ns)
    raw = CERT.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == CERT_SHA256, "vendored #4585 CERTIFICATE.json")
    listed = {w["index"]: set(tuple(sorted(p, reverse=True)) for p in w["relaxed_partitions"])
              for w in json.loads(raw)["windows"]}
    c, program = ns["construct"]()
    wins = ns["extract_windows"](c, program)
    need(len(wins) == 128 and set(listed) == {w["index"] for w in wins}, "same 128 windows")

    def geo_profiles(starts, ends, word):
        cur, upper = list(ends), [None] * len(word)
        for k in range(len(word) - 1, -1, -1):
            i, j, _ = word[k]
            f = cur[i] & cur[j]
            upper[k] = f
            cur[i] = cur[j] = f
        out = set()

        def rec(k, state, hist):
            if k == len(word):
                h = list(hist)
                for r in range(3):
                    if not state[r] <= ends[r]:
                        return
                    g = ns["dim"](ends[r]) - ns["dim"](state[r])
                    if g:
                        h[g] += 1
                out.add(part(tuple(h)))
                return
            i, j, _ = word[k]
            L, U = ns["ssum"](state[i], state[j]), upper[k]
            for dd in range(ns["dim"](L), ns["dim"](U) + 1):
                for F in ns["subspaces_between"](L, U, dd):
                    h, st = list(hist), list(state)
                    for r in (i, j):
                        g = ns["dim"](F) - ns["dim"](st[r])
                        if g:
                            h[g] += 1
                        st[r] = F
                    rec(k + 1, tuple(st), tuple(h))

        rec(0, tuple(starts), (0,) * 10)
        return out

    def capped(p, k):
        return sum(min(r, k) for r in p)

    stats = {"windows": 0, "realisable_profiles": 0, "listed": 0, "refining_a_listed_partition": 0}
    for w in wins:
        lst = listed[w["index"]]
        old = part(ns["actual_profile"](w["starts"], w["ends"], w["frames"]))
        need(old in lst, f"incumbent listed, window {w['index']}")
        need(all(sum(old) == sum(p) and all(capped(old, k) <= capped(p, k) for k in range(1, 10)) for p in lst),
             f"incumbent dominates, window {w['index']}")
        ms, _ = ns["matches"](*w["coefficients"], MAX_LEN)
        realisable = set()
        for word in ms:
            realisable |= geo_profiles(w["starts"], w["ends"], word)
        need(old in realisable, "incumbent realisable")
        for R in realisable:
            stats["realisable_profiles"] += 1
            if R in lst:
                stats["listed"] += 1
            else:
                need(any(refines(R, C) for C in lst), f"profile {R} refines a listed partition, window {w['index']}")
                stats["refining_a_listed_partition"] += 1
        stats["windows"] += 1
    print(json.dumps({"status": "PASS_PR4585_GEOMETRY_SOUNDNESS", "max_word_length": MAX_LEN, **stats,
                      "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
