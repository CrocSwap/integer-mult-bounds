"""Walk-level search for universal seven-source words with small toggle-add bill.

State: a closed walk of k steps on F2^7, each step of Hamming weight 1
(singleton) or 2 (charged DUO), with XOR of all steps zero (restored word).
W = k + d where d = number of weight-2 steps. Universal iff the pairwise XORs
of the prefix set cover F2^7 (128 masks).

Mutation (fixed d): pick two positions i, j and replace steps (a, b) by
(a', b') with a' of the same weight as a and b' = a' ^ a ^ b of the same weight
as b. This preserves closure and d exactly.

Usage: python3 walk_search.py   (writes WALK-RESULT.json)
"""
import json
import random
import time

N = 7
NB = 1 << N
TARGETS = [
    # (k, d, seconds)
    (22, 2, 120),
    (20, 4, 90),
    (21, 3, 90),
    (22, 4, 60),
    (20, 2, 90),
    (23, 1, 90),
    (21, 5, 45),
    (22, 6, 45),
]


def prefixes_of(steps):
    q = 0
    pref = [0]
    for s in steps:
        q ^= s
        pref.append(q)
    return pref, q


def cov_mass(pref):
    seen = 1
    m = len(pref)
    for i in range(m):
        pi = pref[i]
        for j in range(i + 1, m):
            seen |= 1 << (pi ^ pref[j])
    return seen.bit_count()


WT1 = [1 << i for i in range(7)]
WT2 = [(1 << i) | (1 << j) for i in range(7) for j in range(i + 1, 7)]


def random_closed(k, d, rng):
    while True:
        steps = [rng.choice(WT2) for _ in range(d)] + [rng.choice(WT1) for _ in range(k - d)]
        rng.shuffle(steps)
        t = 0
        for s in steps:
            t ^= s
        if t == 0:
            return steps
        # fix: pick a pair whose replacement can absorb t
        for _ in range(200):
            i = rng.randrange(k)
            j = rng.randrange(k)
            if i == j:
                continue
            a, b = steps[i], steps[j]
            want = a ^ b
            pool = WT2 if (a.bit_count() == 2) else WT1
            a2 = rng.choice(pool)
            b2 = a2 ^ want
            if b2.bit_count() == b.bit_count() and b2 != 0:
                steps[i], steps[j] = a2, b2
                t2 = 0
                for s in steps:
                    t2 ^= s
                if t2 == 0:
                    return steps
    return None


def search(k, d, seconds, rng):
    t0 = time.time()
    best = 0
    best_steps = None
    restarts = 0
    while time.time() - t0 < seconds:
        steps = random_closed(k, d, rng)
        pref, q = prefixes_of(steps)
        mass = cov_mass(pref)
        stuck = 0
        for _ in range(20000):
            if mass == NB:
                return {"steps": steps, "W": k + d, "k": k, "d": d,
                        "restarts": restarts}
            i = rng.randrange(k)
            j = rng.randrange(k)
            if i == j:
                continue
            a, b = steps[i], steps[j]
            want = a ^ b
            pool = WT2 if (a.bit_count() == 2) else WT1
            a2 = rng.choice(pool)
            b2 = a2 ^ want
            if b2.bit_count() != b.bit_count() or b2 == 0:
                stuck += 1
                continue
            old = (a, b)
            steps[i], steps[j] = a2, b2
            pref, q = prefixes_of(steps)
            if q != 0:
                steps[i], steps[j] = old
                stuck += 1
                continue
            nm = cov_mass(pref)
            if nm >= mass:
                mass = nm
                stuck = 0
            elif stuck > 400 and nm >= mass - 3:
                mass = nm
                stuck = 0
            else:
                steps[i], steps[j] = old
                stuck += 1
            if mass > best:
                best = mass
                best_steps = list(steps)
        restarts += 1
    return {"steps": None, "k": k, "d": d, "best": best,
            "best_steps": best_steps, "restarts": restarts}


def main():
    rng = random.Random(20261015)
    out = {"N": N, "seed": 20261015, "targets": []}
    t0 = time.time()
    for k, d, sec in TARGETS:
        r = search(k, d, sec, rng)
        out["targets"].append(r)
        if r["steps"]:
            print("FOUND k=%d d=%d W=%d" % (k, d, k + d), flush=True)
            break
        else:
            print("k=%d d=%d: best %d/128 restarts %d"
                  % (k, d, r.get("best", -1), r["restarts"]), flush=True)
    out["elapsed_s"] = round(time.time() - t0, 1)
    with open("WALK-RESULT.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)
    print("elapsed", out["elapsed_s"])


if __name__ == "__main__":
    main()
