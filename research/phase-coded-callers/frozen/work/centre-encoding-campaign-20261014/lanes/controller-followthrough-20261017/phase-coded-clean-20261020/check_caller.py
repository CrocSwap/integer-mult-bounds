#!/usr/bin/env python3
"""Check the ordered caller and its remaining phase invoice."""

import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LANES = HERE.parent.parent
PHASE = LANES / "native-escape-20261017/no-reset-triple-20261020"
PINS = {
    "phase_freeze": (
        PHASE / "FREEZE.json",
        "089425bdf431d81456e1c988a1fd21a837baca43e510bc92dee98dc2ee571791",
    ),
}


def need(test, message):
    if not test:
        raise ValueError(message)


def reduced(word):
    result = []
    for letter in word:
        if result and (result[-1], letter) in (("Q", "q"), ("q", "Q")):
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def add(*terms):
    result = {}
    for scale, poly in terms:
        for word, coefficient in poly.items():
            result[word] = result.get(word, F(0)) + scale * coefficient
            if not result[word]:
                del result[word]
    return result


def op(letter, poly):
    result = {}
    for word, coefficient in poly.items():
        key = reduced((letter,) + word)
        result[key] = result.get(key, F(0)) + coefficient
        if not result[key]:
            del result[key]
    return result


def neg(poly):
    return add((-1, poly))


def forward(state, reader):
    a, u, z, v = state
    return [neg(z), u, add((1, a), (1, op(reader, u))),
            add((1, v), (1, op("Q", u)))]


def backward(state, lower):
    a, u, z, v = state
    return [z, add((1, u), (1, op(lower, z)), (-1, op("q", v))),
            neg(a), v]


def encoded(poly):
    return [[list(word), str(value)] for word, value in sorted(poly.items())]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    for name, (path, pin) in PINS.items():
        need(sha256(path.read_bytes()).hexdigest() == pin,
             "Pinned route source " + name)

    a, u, z, v = [{(letter,): F(1)} for letter in ("a", "u", "z", "v")]
    alpha = add((1, a), (1, op("B0", u)))
    state0 = forward([a, u, z, v], "B0")
    state1 = backward(state0, "D1")
    state2 = forward(state1, "B2")
    r = add((1, op("D1", alpha)), (-1, op("q", v)))
    beta = add((1, alpha), (1, op("B2", r)))
    expected = [neg(z), r, beta, op("Q", add((1, u), (1, op("D1", alpha))))]
    need(state2 == expected, "The complete noncommuting content endpoint")

    full = state2[:3] + [op("q", state2[3])]
    need(full[3] == add((1, u), (1, op("D1", alpha))),
         "The ordinary output has a FULL representation")

    decoded = list(full)
    decoded[2] = add((1, decoded[2]), (-1, op("B2", decoded[1])))
    need(decoded[2] == alpha, "The selected record has no borrowed baseline")
    decoded[1] = add((1, decoded[1]), (-1, op("D1", decoded[2])))
    decoded[3] = add((1, decoded[3]), (-1, op("D1", decoded[2])))
    decoded[2] = add((1, decoded[2]), (-1, op("B0", decoded[3])))
    need(decoded == [neg(z), neg(op("q", v)), a, u],
         "Four ordered FULL shears")
    final = [decoded[0], op("Q", decoded[1]),
             op("QP", decoded[2]), op("Q", decoded[3])]
    need(final == [neg(z), neg(v), op("QP", a), op("Q", u)],
         "The canonical signed exchange of the original physical inputs")

    middle = list(state1)
    middle[1] = add((1, middle[1]), (-1, op("D1", middle[0])))
    alternate = forward(middle, "B2")
    alternate = alternate[:3] + [op("q", alternate[3])]
    need(alternate == [
        neg(z), neg(op("q", v)),
        add((1, alpha), (-1, op("B2", op("q", v)))), u
    ], "A current FULL middle scatter replaces two final scatters")
    alternate[2] = add((1, alternate[2]), (-1, op("B2", alternate[1])))
    alternate[2] = add((1, alternate[2]), (-1, op("B0", alternate[3])))
    need(alternate == decoded, "The shorter scalar decoder has the same result")

    bad = list(full)
    bad[2] = add((1, bad[2]), (1, op("B2", bad[1])))
    need(bad[2] != alpha, "A wrong selected correction fails")
    need(op("Q", op("B2", r)) != op("B2", op("Q", r)),
         "The checker does not commute Q through a reader")

    profile = {1: 3 * 1392 + 208, 2: 3 * 64, 3: 3 * 48, 8: 32, 9: 16}
    mass = sum(rank * count for rank, count in profile.items())
    need(mass == 25 * 224 == 5600, "The exact native mass reaches the threshold")
    receipt = {
        "status": "PASS_ORDERED_PHASE_CODED_CALLER",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "source_pins": {
            name: {"path": str(path), "sha256": pin}
            for name, (path, pin) in PINS.items()
        },
        "initial_contents": ["a=q_P X0_P", "u=q_R X0_R",
                             "z=Y0_P", "v=Y0_R"],
        "content_endpoint": [encoded(p) for p in state2],
        "full_endpoint": [encoded(p) for p in full],
        "decoded_full_endpoint": [encoded(p) for p in decoded],
        "canonical_endpoint": [encoded(p) for p in final],
        "native_profile_with_direct_terminal": profile,
        "native_mass_with_direct_terminal": mass,
        "direct_terminal_positive_lines": 208,
        "zero_order_scalar_port_invoice": {
            "three_local_words": 3 * 4632,
            "four_final_FULL_shears": 4 * 1760,
            "total": 3 * 4632 + 4 * 1760,
            "shorter_three_FULL_shear_total": 3 * 4632 + 3 * 1760,
        },
        "scope": (
            "The ordered algebra closes the signed exchange after direct "
            "phase correction. The source phase theorem admits the mixed "
            "boundaries. Exact routed decoder maps, recursive hosting, "
            "and numerical-grid costs remain separate. Native mass5600 "
            "is not a strict supplier improvement."
        ),
    }
    (args.out / "CALLER.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
