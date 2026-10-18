#!/usr/bin/env python3
"""Independent dense finite-field controls for the exact free-algebra certificate.

No imports from verify.py or a predecessor. This is a cross-check, not the
rational identity proof. All 1,322 input coordinates are distinct columns.
Prepared for commdata2338 with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def need(value, message):
    if not value:
        raise RuntimeError(message)


def matrix(number, modulus, dual, inverse):
    # Determinant-one, noncommuting matrices: [[1,a],[b,1+ab]].
    a = number + 1
    b = number * number + 1
    m = (1, a, b, 1 + a*b)
    if dual:  # K^{-T}
        m = (m[3], -m[2], -m[1], m[0])
    if inverse:
        m = (m[3], -m[1], -m[2], m[0])
    return tuple(x % modulus for x in m)


def run(word, receipt, modulus):
    dual = receipt["orientation"] == "dual"
    n = 2 * word["report"]["v"] + word["report"]["R"]
    ordinary = sorted(set(range(n)) - set(word["removed"]))
    scratch = sorted(n + int(r) for r in word["helper_final"])
    width = 2 * len(ordinary)
    state = {}
    for j, r in enumerate(ordinary):
        state[r] = [[int(i == 2*j+k) for i in range(width)] for k in (0, 1)]
    for r in scratch:
        state[r] = [[0] * width, [0] * width]
    original = {r: [x.copy() for x in rows] for r, rows in state.items()}
    pool = {r: [x.copy() for x in rows] for r, rows in state.items() if r in ordinary}
    for slot in range(receipt["pool_slots"]):
        pool[-slot-1] = [[0]*width, [0]*width]
    allocation = {x["buffer"]: -x["slot"]-1 for x in receipt["static_plan"]}
    skipped = set(receipt["zero_noop_events"])
    active, observed = {}, []
    peak = 0
    column = {r: j for j, r in enumerate(ordinary)}

    def operation(storage, gate, renamed=False):
        kind = gate[0]
        destination = gate[1]
        if kind == "add":
            source = gate[2]
            q = gate[3] * pow(gate[4], -1, modulus) % modulus
            if dual:
                destination, source, q = source, destination, -q % modulus
            if renamed:
                destination = allocation.get(destination, destination)
                source = allocation.get(source, source)
            rows = storage[destination]
            other = storage[source]
            storage[destination] = [[(x + q*y) % modulus for x, y in zip(a, b)]
                                    for a, b in zip(rows, other)]
        elif kind == "scale":
            q = gate[2] * pow(gate[3], -1, modulus) % modulus
            if dual:
                q = pow(q, -1, modulus)
            if renamed:
                destination = allocation.get(destination, destination)
            storage[destination] = [[q*x % modulus for x in row] for row in storage[destination]]
        elif kind == "warp":
            if renamed:
                destination = allocation.get(destination, destination)
            a, b, c, d = matrix(abs(gate[2]), modulus, dual, gate[2] < 0)
            x, y = storage[destination]
            storage[destination] = [[(a*u+b*v) % modulus for u, v in zip(x, y)],
                                    [(c*u+d*v) % modulus for u, v in zip(x, y)]]
        else:
            raise RuntimeError("unknown literal opcode")
        return destination

    for step, gate in enumerate(word["cleanup"], 1):
        destination = gate[2] if dual and gate[0] == "add" else gate[1]
        before = any(any(row) for row in original[destination])
        destination = operation(original, gate)
        after = any(any(row) for row in original[destination])
        if destination in scratch:
            if after and not before:
                active[destination] = step
            elif before and not after:
                observed.append(dict(buffer=destination, start=active.pop(destination), end=step))
        peak = max(peak, len(active))
        if step == receipt["peak_after_event"]:
            for r, terms in receipt["peak_rows"]:
                expected = [[0]*width, [0]*width]
                for source, letters, text in terms:
                    need(not letters, "claimed peak is not operator-free")
                    numerator, slash, denominator = text.partition("/")
                    q = int(numerator) * pow(int(denominator) if slash else 1, -1, modulus) % modulus
                    expected[0][2*column[source]] = q
                    expected[1][2*column[source]+1] = q
                need(original[r] == expected, "dense peak-row certificate mismatch")
        if step not in skipped:
            operation(pool, gate, True)
        else:
            # Independently verify every skipped operator acts on a zero source.
            if gate[0] == "add":
                r = gate[1] if dual else gate[2]
                need(not any(any(row) for row in original[r]), "skipped nonzero ADD")
            else:
                need(not after, "skipped nonzero SCALE/WARP")
    observed.sort(key=lambda x: (x["start"], x["buffer"]))
    need(observed == receipt["intervals"], "dense and formal lifetimes differ")
    need(peak == receipt["pool_slots"], "dense and formal peaks differ")
    need(not active, "dense private exit")
    need(all(original[r] == pool[r] for r in ordinary), "dense pooled boundary mismatch")
    need(all(not any(any(row) for row in pool[-slot-1]) for slot in range(receipt["pool_slots"])),
         "dense pool exit")
    # A scalar commutative interpretation could conceal incorrect word order.
    k1 = matrix(1, modulus, False, False)
    k2 = matrix(2, modulus, False, False)
    product12 = (k1[0]*k2[1]+k1[1]*k2[3]) % modulus
    product21 = (k2[0]*k1[1]+k2[1]*k1[3]) % modulus
    need(product12 != product21, "commuting oracle control")
    return width


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, default=ROOT / "EXPECTED.json")
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    inputs = json.loads((ROOT / "INPUTS.json").read_text())
    for item in inputs["files"]:
        need(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest() == item["sha256"], "source pin")
    cases = 0
    for name in ("base", "extra"):
        word = json.loads(gzip.decompress((ROOT/"source"/f"BORROW-WORD-43{name}.json.gz").read_bytes()))
        for orientation in receipt["words"][name]:
            for modulus in (65537, 1000003):
                columns = run(word, orientation, modulus)
                cases += 1
    print(f"PASS_DENSE_POOL_ORACLE cases={cases} columns_per_case={columns} primes=65537,1000003 noncommuting=PASS")


if __name__ == "__main__":
    main()
