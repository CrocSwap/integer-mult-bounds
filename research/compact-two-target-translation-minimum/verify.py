#!/usr/bin/env python3
"""Exact two-target invariant-agreement and translation certificate. Apache-2.0."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def raw(u, t, y):
    """Fixed B=8, two 6-bit data blocks, constant source pair (1,1)."""
    for step in range(2):
        z0, z1 = u % 2, (u // 8) % 2
        y = (y + 2*z0*(t % 8) + 128*z1*(t // 8)) % 4096
        t = (t + y % 2 + 8*((y // 64) % 2)) % 64
        y = (y + z0*(1-2*(t % 8)) + 64*z1*(1-2*(t // 8))) % 4096
        t = (t - ((y % 2) ^ z0) - 8*(((y // 64) % 2) ^ z1)) % 64
        if step == 0:
            u = (u + 9) % 64
    return (u - 9) % 64, t, y


def literal(u, t, y):
    """Separate packed-update implementation using explicit digit vectors."""
    for step in range(2):
        parity = [(u // (8**i)) % 2 for i in range(2)]
        temporary = [(t // (8**i)) % 8 for i in range(2)]
        increment = sum(2*parity[i]*temporary[i]*(64**i) for i in range(2))
        y = (y + increment) % 4096
        target = [(y // (64**i)) % 2 for i in range(2)]
        t = (t + sum(target[i]*(8**i) for i in range(2))) % 64
        live = [(t // (8**i)) % 8 for i in range(2)]
        increment = sum(parity[i]*(1-2*live[i])*(64**i) for i in range(2))
        y = (y + increment) % 4096
        target = [(y // (64**i)) % 2 for i in range(2)]
        t = (t - sum((target[i] ^ parity[i])*(8**i) for i in range(2))) % 64
        if step == 0:
            u = (u + 1 + 8) % 64
    return (u - 1 - 8) % 64, t, y


def core(x):
    a, b, c, w = x
    return a < 7 and b < 7 and c < 7 and w + b < 32


def translate(x, shift):
    return tuple((v+d) % period for v, d, period in zip(x, shift, (8, 8, 8, 32)))


def validate_menu(menu):
    if not isinstance(menu, (list, tuple)) or not 1 <= len(menu) <= 5:
        raise ValueError("menu needs one through five entries")
    for row in menu:
        if not isinstance(row, (list, tuple)) or len(row) != 4:
            raise ValueError("translation needs four coordinates")
        if any(type(v) is not int or not 0 <= v < p
               for v, p in zip(row, (8, 8, 8, 32))):
            raise ValueError("noncanonical translation coordinate")


def defeat_four(menu):
    """Return one restored-coordinate orbit missed by an arbitrary short menu."""
    validate_menu(menu)
    if len(menu) > 4:
        raise ValueError("four-entry adversary does not cover five entries")
    rows = list(menu) + [menu[-1]]*(4-len(menu))
    c, d = (0, 1) if (rows[1][1]-rows[0][1]) % 8 != 1 else (1, 0)
    t0 = (7-rows[c][1]) % 8
    td = (t0+rows[d][1]) % 8
    require(td != 0, "ordered-pair choice must leave a nonzero digit")
    witness = ((7-rows[2][0]) % 8, t0, (7-rows[3][2]) % 8,
               (32-td-rows[d][3]) % 32)
    require(all(not core(translate(witness, row)) for row in rows),
            "adversary must defeat every entry")
    return witness


def quotient_check():
    counts = {"quotient_states": 0, "quotient_agreement": 0, "quotient_core": 0}
    for u0, z1, t0, t1, w, b0, b1 in itertools.product(
            range(8), range(2), range(8), range(8), range(32), range(2), range(2)):
        u, t, y = u0+8*z1, t0+8*t1, b0+2*w+64*b1
        first, second = literal(u, t, y), literal(u, t, y ^ 65)
        require(first == raw(u, t, y) and second == raw(u, t, y ^ 65),
                "independent packed-update disagreement")
        agreement = first == (u, t, y ^ 65)
        invariant = agreement and second == (u, t, y)
        require(invariant == core((u0, t0, t1, w)), "exact core classification")
        counts["quotient_states"] += 1
        counts["quotient_agreement"] += agreement
        counts["quotient_core"] += invariant
    return counts


def full_check():
    counts = {"full_states": 0, "full_agreement": 0, "full_core": 0}
    for u, t in itertools.product(range(64), repeat=2):
        for y in range(4096):
            agreement = raw(u, t, y) == (u, t, y ^ 65)
            invariant = agreement and raw(u, t, y ^ 65) == (u, t, y)
            require(invariant == core((u % 8, t % 8, t // 8, (y // 2) % 32)),
                    "full-field core classification")
            counts["full_states"] += 1
            counts["full_agreement"] += agreement
            counts["full_core"] += invariant
    return counts


def cover_check():
    menu = [(k, k, k, 6*k) for k in range(5)]
    validate_menu(menu)
    selected = [0]*5
    for x in itertools.product(range(8), range(8), range(8), range(32)):
        phases = [k for k, row in enumerate(menu) if core(translate(x, row))]
        require(bool(phases), "five entries must cover every restored-coordinate orbit")
        selected[phases[0]] += 1
    require(sum(selected) == 16384, "complete coordinate domain")
    return {"upper_menu": menu, "least_phase_counts": selected,
            "covered_coordinate_tuples": sum(selected)}


def adversary_check():
    count = 0
    for digits in itertools.product(range(8), repeat=4):
        # Every t0-translation profile, with varied other coordinates.
        seed = sum(v*(8**i) for i, v in enumerate(digits))
        menu = [((seed+3*i) % 8, digits[i], (seed//8+5*i) % 8,
                 (seed//64+7*i) % 32) for i in range(4)]
        witness = defeat_four(menu)
        for row in menu:
            a, b, c, w = translate(witness, row)
            u, t, y = a, b+8*c, 2*w
            require(not (literal(u, t, y) == (u, t, y ^ 65)
                         and literal(u, t, y ^ 65) == (u, t, y)),
                    "adversary must fail the actual invariant endpoint")
        count += 1
    for size in range(1, 4):
        defeat_four([(0, 0, 0, 0)]*size)
    return {"all_t0_shift_profiles": count, "short_menu_fixtures": 3}


def rejection_controls():
    fixtures = [(7, 0, 0, 0), (0, 7, 0, 0), (0, 0, 7, 0), (0, 1, 0, 31)]
    for omitted, x in enumerate(fixtures):
        a, b, c, w = x
        clauses = (a < 7, b < 7, c < 7, w+b < 32)
        require(all(v for i, v in enumerate(clauses) if i != omitted),
                "clause-omission fixture must isolate its clause")
        u, t, y = a, b+8*c, 2*w
        require(not (raw(u, t, y) == (u, t, y ^ 65)
                     and raw(u, t, y ^ 65) == (u, t, y)), "omission must fail")
    require(raw(0, 7, 0) == (0, 7, 65)
            and raw(0, 7, 65) != (0, 7, 0), "agreement is not an invariant guard")
    invalid = [[], [(0, 0, 0)], [(True, 0, 0, 0)], [(8, 0, 0, 0)],
               [(0, 0, 0, 32)], [(0, 0, 0, 0)]*6]
    for menu in invalid:
        try:
            validate_menu(menu)
        except ValueError:
            continue
        raise ValueError("invalid menu accepted")
    try:
        defeat_four([(0, 0, 0, 0)]*5)
    except ValueError:
        return {"clause_omissions": 4, "agreement_without_invariance": 1,
                "invalid_menus": len(invalid), "five_entry_adversary_rejected": 1}
    raise ValueError("adversary improperly accepted a five-entry menu")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path, help="write new receipt, never overwrite")
    args = parser.parse_args()
    result = {"status": "PASS_COMPACT_TWO_TARGET_TRANSLATION_MINIMUM",
              "claim_type": "finite certificate and scoped combinatorial proof",
              "geometry": {"B": 8, "window_values": 32, "source": [1, 1],
                           "control_modulus": 64, "data_modulus": 4096},
              "minimum_invariant_translation_menu": 5}
    result.update(quotient_check())
    result.update(full_check())
    result.update(cover_check())
    result.update(adversary_check())
    result["controls"] = rejection_controls()
    require(result["full_states"] == 16777216, "complete full-field enumeration")
    require(result["full_core"] == 128*result["quotient_core"], "quotient lifting")
    package = Path(__file__).resolve().parent
    files = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
    result["package_sha256"] = {}
    for name in files:
        path = package / name
        require(path.stat().st_size <= 1048576, "bounded package source file")
        result["package_sha256"][name] = hashlib.sha256(path.read_bytes()).hexdigest()
    encoded = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.receipt:
        with args.receipt.open("x", encoding="utf-8") as output:
            output.write(encoded)
    print(encoded, end="")


if __name__ == "__main__":
    main()
