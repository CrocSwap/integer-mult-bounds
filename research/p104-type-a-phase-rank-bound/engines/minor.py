"""Certify a required Type A phase rank above two by a 3x3 minor."""
import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import json
from math import isqrt
from pathlib import Path
import runpy
import signal
from time import monotonic

PINS = {
    "round45/CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "round45/PRICE.json": "8c7862be17c0ba549d4135af3f0e8dfb6b7dcec08bb8a91895194978280097d6",
    "round45/transport.py": "2595d5c4bf6da66e322d03aa71962d4431baa4a2dede36dfa19369bb402dc243",
}


def determinant(a):
    return sum((-1 if sum(p[i] > p[j] for i in range(3) for j in range(i+1, 3)) % 2 else 1)
               * a[0][p[0]] * a[1][p[1]] * a[2][p[2]] for p in permutations(range(3)))


def controls(prime):
    a = [[1, 0, 0], [0, 1, 0], [0, 0, 2]]
    assert determinant(a) % prime == 2
    a[2][2] = prime
    assert determinant(a) == prime and determinant(a) % prime == 0
    return ["nonzero_minor", "modular_rank_drop_requires_exact_fallback"]


def save(out, name, value):
    temp = out / (name + ".tmp")
    temp.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temp.replace(out / name)


def run(root, out, seconds):
    start = monotonic()
    for rel, expected in PINS.items():
        if sha256((root / rel).read_bytes()).hexdigest() != expected:
            raise ValueError(f"changed dependency {rel}")
    old = json.loads((root / "round45/PRICE.json").read_bytes())
    c = json.loads((root / "round45/CALLER.json").read_bytes())
    assert old["native_copies"] == 17 and old["type_a_ports"] == 96
    assert old["credit_paid_rank_one_per_alternative"] == 96 and len(old["alternatives"]) == 68
    baseline = list(map(Fraction, old["old_margin_interval"]))
    price = {"head": old["head"], "pins": PINS, "alternatives": 68,
             "baseline_interval": list(map(str, baseline)),
             "optimistic_saving_upper_per_alternative": "96",
             "optimistic_complete_margin_interval": [str(x + 96) for x in baseline],
             "grant": "all extra adapters, phase, ownership, setup, and restoration free in the upper"}
    save(out, "PRICE.json", price)

    m = runpy.run_path(str(root / "round45/transport.py"))
    p = m["PRIME"]
    assert all(p % d for d in range(2, isqrt(p)+1))
    alpha = m["residue"](c["types"]["A"]["alpha2"])
    gates, queries, hosts = m["trace"](c)
    results = []
    all_cases = [(q, h) for q in queries for h in hosts]
    assert len(all_cases) == 68
    for q, h in all_cases:
        if monotonic() - start >= seconds - 1:
            break
        d, s = queries[q]
        stage, (x, y, u, v) = hosts[h]
        lo, hi = sorted((q, h))
        window = [gate for gate in gates if lo < gate[0] < hi]
        write, read = m["transport"](window, d, s, h < q)
        # Required minus block has update -2*w*r relative to old minus.
        # The old minus shears multiply on the right before the query
        # and on the left after it, preserving outside components.
        if h < q:
            read[x] = (read[x] - read[y]) % p
            read[v] = (read[v] - alpha * read[u]) % p
        else:
            write[y] = (write[y] - write[x]) % p
            write[u] = (write[u] - alpha * write[v]) % p
        output = m["outside"](write, {y, u})
        source = m["outside"](read, {x, v})
        witness = None
        if output and source:
            rr = [y, u, output[0]]
            cc = [x, v, source[0]]
            old_difference = {(y, x): -2, (u, v): -2 * alpha}
            minor = [[(old_difference.get((i,j), 0) - 2*write[i]*read[j]) % p for j in cc] for i in rr]
            value = determinant(minor) % p
            assert value
            witness = {"rows": rr, "columns": cc, "minor": minor, "determinant_residue": value}
        results.append({"query": q, "host": h, "stage": stage, "rank_three_witness": witness})
    unresolved = [[r["query"],r["host"]] for r in results if r["rank_three_witness"] is None]
    unresolved.extend(all_cases[len(results):])
    save(out, "SUPPORT.json", {"head": old["head"], "price_sha256": sha256((out/"PRICE.json").read_bytes()).hexdigest(),
          "prime": p, "checked": len(results), "excluded": len(all_cases)-len(unresolved),
          "unresolved": unresolved, "rows": results, "controls": controls(p)})


if __name__ == "__main__":
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dependencies", type=Path)
    parser.add_argument("out", type=Path)
    parser.add_argument("--seconds", type=int, choices=range(2,61), default=60)
    a = parser.parse_args()

    def cap(*_):
        raise TimeoutError("phase rank watchdog")

    signal.signal(signal.SIGALRM, cap)
    signal.alarm(a.seconds)
    a.out.mkdir()
    run(a.dependencies.resolve(), a.out.resolve(), a.seconds)
