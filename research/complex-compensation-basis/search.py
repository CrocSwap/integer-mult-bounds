#!/usr/bin/env python3
"""Reproduce the bounded seed-24 nomination; this is not an optimality solver.

Sricharan Vagvala (@theon199), with substantial OpenAI Codex assistance.
Apache-2.0. See README.md for predecessor credit and scope.
"""
import argparse
import gzip
import json
import random
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
WORD = ROOT / "research/community-k492-audit/pr622/replay/jp8-local/CANONICAL-WORD.json.gz"


def price(q):
    """Existing cleared-work binary-Horner price, for two real components."""
    if not q:
        return 0
    a, b = abs(q.numerator), q.denominator
    if b & (b - 1):
        raise ValueError("non-dyadic coefficient")
    return 2 * (3 + a.bit_length() - 1 + a.bit_count() + b.bit_length() - 1)


def nominate():
    word = json.loads(gzip.decompress(WORD.read_bytes()))
    rows = {t: {} for t in range(112, 224)}
    for _, t, s, a, b, frame in word["compensation"]:
        if frame != 0 or s in rows or s in rows[t]:
            raise ValueError("unexpected compensation input")
        rows[t][s] = Fraction(a, b)
    coefficients = [Fraction(sign) * Fraction(2) ** k
                    for k in range(-2, 3) for sign in (-1, 1)]
    original_cost = {t: sum(map(price, row.values())) for t, row in rows.items()}
    candidates = []
    scored = 0
    for target, a in rows.items():
        for donor, b in rows.items():
            if target == donor:
                continue
            for q in coefficients:
                residual = {s: a.get(s, 0) - q * b.get(s, 0) for s in a.keys() | b.keys()}
                residual = {s: x for s, x in residual.items() if x}
                # Charge BOTH target preparation and target restoration.
                gain = original_cost[target] - sum(map(price, residual.values())) - 2 * price(q)
                scored += 1
                if gain > 0:
                    candidates.append((gain, target, donor, q, len(a) - len(residual) - 2))
    random.Random(24).shuffle(candidates)
    candidates.sort(key=lambda item: -item[0])
    used, pairs = set(), []
    for gain, target, donor, q, macros in candidates:
        if target in used or donor in used:
            continue
        used.update((target, donor))
        pairs.append(dict(target=target, donor=donor, coefficient=str(q),
                          saved_real_primitives=gain, saved_macros=macros))
    return dict(seed=24, provider="jp8", coefficient_domain=list(map(str, coefficients)),
                scored=scored, positive=len(candidates), pairs=pairs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a new nomination instead of checking RECIPE.json")
    args = parser.parse_args()
    result = nominate()
    if args.output:
        # An exploratory command must not silently replace a frozen recipe.
        with args.output.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    elif result != json.loads((HERE / "RECIPE.json").read_text()):
        raise ValueError("bounded search differs from the frozen recipe")
    print(f"PASS_SEED24_SEARCH scored={result['scored']} positive={result['positive']} "
          f"pairs={len(result['pairs'])} saved={sum(p['saved_real_primitives'] for p in result['pairs'])}")


if __name__ == "__main__":
    main()
