"""Exact simultaneous color-refinement and optimistic stock price at Type A cut 1741."""
from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "inputs/R178-REVERSE.json": "ad9bbc64a9b866a89f48f1fac0b0346c18105c4b69e62aa41a9cd5575e5c5942",
    "inputs/R178-PRICE.json": "fbb1e5f1de9274bba2d0445b3868c50a04b178751c0f9244ebf5229128bc4651",
    "inputs/R92-PRICE.json": "05d7a5ebdd2eeedd6c8f534e8e2eeac22484daf9f387f4a6b88cc9eed22a6b8f",
    "inputs/pricing.py": "f4d0b6c9314b838d882d6d06020f24881c19a3fda97a7c00df87b1e920785182",
    "inputs/r179_replay.py": "720a921b8eb215675bf738c94dac3361592c342fd8f8eeda6d6efb6888061a5a",
}
HEAD = "aaeec8c0acf01e99a5f331ef363a698d9c084ace"
CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
CUT, N, PORTS, CASES, SECONDS = 1741, 36, 96, 20000, 60


def unique(items):
    result = dict(items)
    assert len(items) == len(result), "duplicate key"
    return result


def timeout(*_):
    raise TimeoutError("60-second cap")


def read(path, decode=True):
    raw = (ROOT / path).read_bytes()
    assert sha256(raw).hexdigest() == PINS[path], path
    return loads(raw, object_pairs_hook=unique) if decode else raw


def partition(keys):
    assigned, colors = {}, []
    for key in keys:
        colors.append(assigned.setdefault(key, len(assigned)))
    return colors


def refine(h):
    n = len(h)
    colors = partition(h[i][i] for i in range(n))
    history = [colors]
    while True:
        new = partition((colors[i], tuple(sorted((colors[j], h[i][j], h[j][i]) for j in range(n))))
                        for i in range(n))
        if new == colors:
            break
        assert len(set(new)) > len(set(colors))
        history.append(new)
        colors = new
    classes = defaultdict(list)
    for i, c in enumerate(colors):
        classes[c].append(i)
    return list(classes.values()), history


def rank(e, l):
    return 1 + 8*(e+l)


def histogram(early, late, perm):
    return Counter(rank(e, late[perm[i]]) for i, e in enumerate(early))


def opposite(early, late, classes, assignment=None):
    out = dict(assignment or {})
    for group in classes:
        left = sorted((i for i in group if i not in out), key=lambda i: (early[i], i))
        right = sorted((j for j in group if j not in out.values()), key=lambda j: (-late[j], j))
        out.update(zip(left, right, strict=True))
    return out


def scaled_delta(old, new):
    return {r: PORTS*(new[r]-old[r]) for r in sorted(old.keys() | new.keys()) if new[r] != old[r]}


def same_h(h, perm):
    n = len(h)
    return all(h[i][j] == h[perm[i]][perm[j]] for i in range(n) for j in range(n))


def verify_controls():
    # The 3-cycle survives although each individual pair swap fails.
    h = [[0, 1, 2], [2, 0, 1], [1, 2, 0]]
    classes, _ = refine(h)
    assert classes == [[0, 1, 2]] and same_h(h, [1, 2, 0])
    assert not same_h(h, [1, 0, 2])
    early = late = [0, 1, 2]
    assert histogram(early, late, opposite(early, late, classes)) == Counter({17: 3})
    broken = [[0, 4, 2], [2, 0, 1], [1, 2, 0]]
    assert refine(broken)[0] == [[0], [1], [2]]
    return ["directed three-cycle retained", "individual swap rejected", "altered edge separates classes",
            "reverse sorting balances ranks"]


def search(h, early, late, classes, old, price, progress):
    """Case count is one consistent assignment attempted, including singleton placements."""
    assigned = {g[0]: g[0] for g in classes if len(g) == 1}
    progress["assignments"] = len(assigned)
    seen = set(assigned.values())
    membership = {i: g for g in classes for i in g}

    def visit():
        relaxed = histogram(early, late, opposite(early, late, classes, assigned))
        if relaxed == old:
            progress["structurally_zero_branches"] += 1
            return None
        delta = scaled_delta(old, relaxed)
        if len(assigned) == N:
            assert same_h(h, assigned)
            progress["exact_automorphisms"] += 1
            interval = price(delta)
            if interval[0] > 0:
                return {"permutation": [assigned[i] for i in range(N)], "delta": delta, "gain": interval}
            progress["nonpositive_or_ambiguous"] += 1
            if interval[1] > 0:
                progress["interval_ambiguous"] += 1
            return None

        def choices(i):
            return [j for j in membership[i] if j not in seen and
                    all(h[i][a] == h[j][b] and h[a][i] == h[b][j] for a, b in assigned.items())]

        # Choose minimum domain size, using the role number for ties.
        all_choices = [(choices(i), i) for i in range(N) if i not in assigned]
        options, i = min(all_choices, key=lambda item: (len(item[0]), item[1]))
        if not options:
            progress["empty_domain_branches"] += 1
            return None
        for j in sorted(options, key=lambda j: (abs(early[i]+late[j]-8), j)):
            if progress["assignments"] == CASES:
                raise TimeoutError("20,000-assignment cap")
            progress["assignments"] += 1
            assigned[i] = j
            seen.add(j)
            result = visit()
            if result is not None:
                return result
            seen.remove(j)
            del assigned[i]
        return None

    return visit()


def main():
    assert __debug__
    signal(SIGALRM, timeout)
    alarm(SECONDS)
    report = {"head": HEAD, "caller": CALLER, "cut": CUT, "pins": PINS, "seconds_cap": SECONDS,
              "assignments_cap": CASES, "controls": verify_controls(), "capped": False}
    try:
        c, p, old_price, base = (read(path) for path in (
            "inputs/CALLER.json", "inputs/R178-REVERSE.json", "inputs/R178-PRICE.json", "inputs/R92-PRICE.json"))
        for path in ("inputs/pricing.py", "inputs/r179_replay.py"):
            read(path, False)
        assert (p["benchmark"], p["caller"], p["cut"]) == (HEAD, CALLER, CUT)
        assert (old_price["head"], old_price["caller"], old_price["cut"]) == (HEAD, CALLER, CUT)
        assert (base["head"], base["caller_head"]) == (HEAD, CALLER)
        assert len(c["events"]) == 4783 and c["events"][CUT] == ["A", "ADD", 10, 0, "2"]
        a = c["types"]["A"]
        assert a["roles"] == len(a["diagonal"]) == N and len(a["ports"]) == PORTS
        assert all(row[:2] == [-1, 0] for row in a["diagonal"])
        early, late = [sum(row[2:10]) for row in a["diagonal"]], [sum(row[10:]) for row in a["diagonal"]]
        algebra = run_path(str(ROOT / "inputs/r179_replay.py"))
        gp, gm = (algebra["expand"](p[key]) for key in ("prefix_plus", "prefix_minus"))
        h = algebra["solve"](gm, gp)
        assert algebra["product"](gm, h) == gp
        assert not algebra["noncommuting_entries"](algebra["identity"](), 0, 9)
        assert algebra["noncommuting_entries"](h, 0, 9)
        classes, history = refine(h)
        old = histogram(early, late, range(N))
        entire = histogram(early, late, opposite(early, late, [list(range(N))]))
        best_perm = opposite(early, late, classes)
        best = histogram(early, late, best_perm)
        delta = scaled_delta(old, best)
        assert sum(delta.values()) == sum(r*n for r, n in delta.items()) == 0
        engine = run_path(str(ROOT / "inputs/pricing.py"))
        k = Q(base["old_crossing_upper"])
        def price(change):
            return engine["cost"](change, k)
        assert price(scaled_delta(old, entire))[1] == Q(old_price["whole_reverse_sorted_upper"])
        upper = price(delta)
        report.update({"prefix_plus_nonzero": len(p["prefix_plus"]), "prefix_minus_nonzero": len(p["prefix_minus"]),
                       "h_nonzero": sum(bool(x) for row in h for x in row), "class_history": history,
                       "classes": [{"roles": group, "early_late": [[early[i], late[i]] for i in group]}
                                   for group in classes],
                       "old_histogram": old, "relaxed_histogram": best, "relaxed_delta": delta,
                       "relaxed_permutation": [best_perm[i] for i in range(N)],
                       "relaxed_upper_interval": upper,
                       "crossing_upper": str(k),
                       "price_scope": "96 Type A ports, unchanged paid histogram, zero seam cost",
                       "search": {"assignments": 0, "structurally_zero_branches": 0, "empty_domain_branches": 0,
                                  "exact_automorphisms": 0, "nonpositive_or_ambiguous": 0, "interval_ambiguous": 0}})
        if old == best:
            assert upper == (0, 0)
            report["status"] = "uniform zero optimistic gain"
        else:
            assert upper[1] > 0
            candidate = search(h, early, late, classes, old, price, report["search"])
            report["candidate"] = candidate
            report["status"] = "profitable exact signed survivor" if candidate else "exact assignment search exhausted"
            if candidate:
                stock = Counter({int(r): n for r, n in base["old_targets"].items()})
                stock.subtract({int(r): n for r, n in base["old_paid"].items()})
                stock.update(candidate["delta"])
                candidate["complete_at_old_crossing_upper"] = price(stock)
                candidate["complete_at_original_probe"] = engine["cost"](stock, Q(base["probe"]))
    except TimeoutError as exc:
        report["capped"] = True
        report["status"] = str(exc)
    finally:
        alarm(0)
    print(dumps(report, indent=2, sort_keys=True, default=str))
    if report["capped"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
