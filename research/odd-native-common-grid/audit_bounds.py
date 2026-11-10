"""Exact source-specific prefix bounds; draft research, no supplier admission.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
Independent implementation; source word and caller retain predecessor credit.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import json


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def ceil_log2(q: Fraction | int) -> int:
    q = Fraction(q)
    require(q > 0, "positive logarithm argument")
    k = q.numerator.bit_length() - q.denominator.bit_length()
    if k >= 0:
        if q.numerator > q.denominator << k:
            k += 1
    elif q.numerator << -k > q.denominator:
        k += 1
    return k


def v2(n: int) -> int:
    require(n > 0, "positive denominator")
    return (n & -n).bit_length() - 1


def word_bounds(word: dict, scale: int = 1125) -> dict:
    n = len(word["initial"])
    rows = [{i: Fraction(1)} for i in range(n)] + [dict() for _ in range(word["owned_fields"])]
    frames = list(word["initial"]) + [None] * word["owned_fields"]
    active = set()
    maximum_mass = Fraction(scale)
    height = 0
    max_numerator_bits = 0
    visits = 0
    witness = None
    operations = Counter()

    def visit(row: dict, event: int, kind: str) -> None:
        nonlocal maximum_mass, height, visits, witness
        mass = Fraction(0)
        for value in row.values():
            value *= scale
            require(value.denominator == 1 << v2(value.denominator),
                    f"odd clearing fails at event {event} ({kind})")
            height = max(height, v2(value.denominator))
            mass += abs(value)
            visits += 1
        if mass > maximum_mass:
            maximum_mass, witness = mass, (event, kind)

    for index, event in enumerate(word["program"]):
        op, target = event[:2]
        operations[op] += 1
        if op == "INIT":
            require(target >= n and target not in active, "fresh owned INIT")
            active.add(target)
            frames[target] = event[2]
            rows[target] = {}
        elif op == "CLEAR":
            require(target in active and frames[target] == event[2], "owned CLEAR")
            active.remove(target)
            frames[target] = None
            rows[target] = {}
        elif op == "MOVE":
            require(frames[target] == event[2], "MOVE source frame")
            frames[target] = event[3]
        elif op == "SCALE":
            factor = Fraction(event[2])
            require(frames[target] == event[3], "SCALE frame")
            max_numerator_bits = max(max_numerator_bits, abs(factor.numerator).bit_length())
            rows[target] = {key: factor * value for key, value in rows[target].items() if factor * value}
            visit(rows[target], index, "scale")
        elif op in ("ADD", "COPY"):
            source, factor = event[2], Fraction(event[3])
            require(source != target and frames[source] == frames[target] == event[4], "ADD common frame")
            require(op != "COPY" or target in active and not rows[target], "COPY into owned zero")
            max_numerator_bits = max(max_numerator_bits, abs(factor.numerator).bit_length())
            product = {key: factor * value for key, value in rows[source].items() if factor * value}
            visit(product, index, "pre-add product")
            new = rows[target].copy()
            for key, value in product.items():
                new[key] = new.get(key, Fraction(0)) + value
                if not new[key]:
                    del new[key]
            rows[target] = new
            visit(new, index, "stored add")
        else:
            raise ValueError("unknown word opcode " + op)
    require(not active, "all owned lifetimes complete")
    require(frames[:n] == word["final"], "public endpoint frames")
    require(all(value.denominator == 1 << v2(value.denominator)
                for row in rows[:n] for value in row.values()), "public endpoint dyadic")
    require(all(not row for row in rows[n:]), "owned endpoint zero")
    return {"events": len(word["program"]), "public_fields": n, "odd_scale": scale,
            "dyadic_height": height, "maximum_scaled_mass": str(maximum_mass),
            "scaled_mass_bits": ceil_log2(maximum_mass), "mass_witness": witness,
            "coefficient_numerator_bits": max_numerator_bits, "coefficient_visits": visits,
            "operations": dict(sorted(operations.items()))}


def caller_bounds(caller: dict) -> dict:
    """Majorize the noncommutative expansion in Clifford words, not a character.

    Each complete native/idle/query Clifford has coefficient mass one. LAMBDA
    is expanded as ((1+s*i) I + (1-s*i) Q^2)/2.  Gaussian coefficient mass is
    |Re|+|Im|; both coefficients therefore have mass one.  No commutativity
    or cancellation is used in this bound.
    """
    count = caller["roles"]
    masses = [Fraction(1) for _ in range(count)]
    heights = [0 for _ in range(count)]
    peak = Fraction(1)
    peak_height = 0
    pre_joint_peak = Fraction(1)
    pre_joint_height = 0
    crude_mass_bits = crude_height = 0
    operations = Counter()

    def note() -> None:
        nonlocal peak, peak_height
        peak = max(peak, *masses)
        peak_height = max(peak_height, *heights)

    def combine(t: int, s: int, factor: Fraction) -> None:
        nonlocal crude_mass_bits, crude_height
        require(t != s, "caller aliases")
        require(factor.denominator == 1 << v2(factor.denominator), "caller scalar must be dyadic")
        masses[t] += abs(factor) * masses[s]
        heights[t] = max(heights[t], heights[s] + v2(factor.denominator))

    for event in caller["events"]:
        if event[0] == "J":
            operations["J"] += 1
            pre_joint_peak = max(pre_joint_peak, *masses)
            pre_joint_height = max(pre_joint_height, *heights)
            s, t, x, y = event[2]
            require(len({s, t, x, y}) == 4, "four distinct A ports")
            a2 = Fraction(caller["types"]["A"]["alpha2"])
            combine(t, s, Fraction(1))
            combine(x, y, a2)
            bs, bt, al, be = event[3]
            al, be = Fraction(al), Fraction(be)
            require(bs != bt and {bs, bt}.isdisjoint({s, t, x, y}), "joint ports disjoint")
            ms, mt, hs, ht = masses[bs], masses[bt], heights[bs], heights[bt]
            require((al, be) == (Fraction(-1), Fraction(1, 2)), "retained B endpoint")
            masses[bs] = ms + mt
            masses[bt] = (ms + mt) / 2
            heights[bs] = max(hs, ht)
            heights[bt] = max(hs, ht) + 1
            crude_mass_bits += max(1, ceil_log2(1 + abs(a2)))
            crude_height += 1
            note()
            continue
        op = event[1]
        operations[op] += 1
        t = event[2]
        if op == "ADD":
            q = Fraction(event[4]); combine(t, event[3], q)
            crude_mass_bits += max(0, ceil_log2(1 + abs(q)))
            crude_height += v2(q.denominator)
        elif op == "SCALE":
            q = Fraction(event[3]); require(q != 0, "nonzero SCALE")
            require(q.denominator == 1 << v2(q.denominator), "dyadic SCALE")
            masses[t] *= abs(q); heights[t] += v2(q.denominator)
            crude_mass_bits += max(0, ceil_log2(abs(q)))
            crude_height += v2(q.denominator)
        elif op == "SWAP":
            s = event[3]; require(s != t, "distinct SWAP")
            masses[t], masses[s] = masses[s], masses[t]
            heights[t], heights[s] = heights[s], heights[t]
        elif op == "QUERY":
            combine(t, event[3], Fraction(1)); crude_mass_bits += 1
        elif op == "LAMBDA":
            require(event[3] in (-1, 1), "LAMBDA sign")
            masses[t] *= 2; heights[t] += 1
            crude_mass_bits += 1; crude_height += 1
        elif op == "IDLE_ONE":
            pass
        else:
            raise ValueError("unknown caller opcode " + op)
        note()
    require(peak <= 2**crude_mass_bits and peak_height <= crude_height, "independent coarse envelope")
    return {"events": len(caller["events"]), "maximum_mass": str(peak),
            "mass_bits": ceil_log2(peak), "denominator_height": peak_height,
            "pre_joint_mass_bits": ceil_log2(pre_joint_peak), "pre_joint_height": pre_joint_height,
            "coarse_mass_bits": crude_mass_bits, "coarse_height": crude_height,
            "operations": dict(sorted(operations.items()))}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    args = ap.parse_args()
    word = json.loads(gzip.decompress((args.source / "word.json.gz").read_bytes()))
    caller = json.loads((args.source / "caller.json").read_text())
    result = {"word": word_bounds(word), "caller": caller_bounds(caller)}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
