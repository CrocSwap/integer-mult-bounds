#!/usr/bin/env python3
"""Independent parity/Fraction oracle for the actual PR6678 rounded prefix.

Credit Nick Petalas6678, DreamingOfClouds6621 and the retained source NOTICE;
zxv6066, Nick Petalas5912/6573 and their credited rounding predecessors.
Written with substantial OpenAI Codex assistance. Apache-2.0.
This executes only the declared scalar prefixes, never a predecessor program.
"""

import argparse
from collections import Counter
from fractions import Fraction
import gzip
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
PIN_SHA = "1b680642e59f1c72fb6cbdf05de48a335bc25f7895ca53fe35f0c51719a7e1ee"
CASE_SHA = "a11f84b9e0e8eea4f0dd9f96b37327a04ef6eb9f84f02594b5a7b8c0ab462695"
WORD_SHA = "aa9821bb1705d721ac7039c23f711afceca49ecc367b61c1b64bd79b3d464d74"
SOURCES = (471, 525, 704)
DESTINATIONS = (119, 169, 191, 193, 204, 206)
OWNED = 770
COMMON = ("source_manifest_sha256", "case_manifest_sha256", "deterministic_rows",
          "stochastic_rows", "stochastic_moments")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def reject_number(token):
    raise ValueError("non-finite JSON number: " + token)


def reject_float(token):
    raise ValueError("JSON float forbidden: " + token)


def strict_json(raw):
    return json.loads(raw, object_pairs_hook=unique_object,
                      parse_constant=reject_number, parse_float=reject_float)


def exact_int(value, name):
    require(type(value) is int, name + " must be integer, not bool")
    return value


def pair(value):
    value = Fraction(value)
    return [value.numerator, value.denominator]


def integer_value(value):
    require(value.denominator == 1, "coarse grid result must be integer")
    return value.numerator


def load_inputs():
    raw = (ROOT / "SOURCE-PINS.json").read_bytes()
    require(sha(raw) == PIN_SHA, "source manifest changed")
    manifest = strict_json(raw)
    require(len(manifest["files"]) == 5, "five inert source files required")
    for entry in manifest["files"]:
        data = (ROOT / entry["local_path"]).read_bytes()
        require(sha(data) == entry["sha256"], "source digest changed")
        require(len(data) == entry["bytes"], "source byte count changed")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == entry["git_blob"],
                "source Git blob changed")
    case_raw = (ROOT / "CASES.json").read_bytes()
    require(sha(case_raw) == CASE_SHA, "case descriptor changed")
    cases = strict_json(case_raw)
    require(cases["source_roles"] == list(SOURCES), "source roles changed")
    require(cases["destination_roles"] == list(DESTINATIONS), "destinations changed")
    require(exact_int(cases["owned_slot"], "owned slot") == OWNED,
            "owned slot changed")
    data = gzip.decompress((ROOT / "inputs/WORD.json.gz").read_bytes())
    require(len(data) == 482221 and sha(data) == WORD_SHA, "word payload changed")
    return strict_json(data)


def old_expected():
    return [["ADD", destination, source, coefficient, 3]
            for destination in DESTINATIONS
            for source, coefficient in zip(SOURCES, ("1", "1/2", "2"))]


def shared_word():
    forward = [["ADD", OWNED, source, coefficient, 3]
               for source, coefficient in zip(SOURCES, ("1", "1/2", "2"))]
    delivery = [["ADD", destination, OWNED, "1", 3] for destination in DESTINATIONS]
    backward = [["ADD", OWNED, source, coefficient, 3]
                for source, coefficient in zip(reversed(SOURCES), ("-2", "-1/2", "-1"))]
    return [["INIT", OWNED, 3], *forward, *delivery, *backward, ["CLEAR", OWNED, 3]]


def bind_source(word):
    require(word["schema"] == "p104-accumulated-block-composition/2", "word schema changed")
    require(word["public"] == 770 and word["owned_fields"] == 29, "role counts changed")
    require(len(word["program"]) == 18561, "source event count changed")
    require(word["program"][:18] == old_expected(), "actual opening prefix changed")
    require(word["frames"][3] == [], "entry frame3 must be empty")
    for role in (*SOURCES, *DESTINATIONS):
        require(word["initial"][role] == 3, "public entry frame changed")
    require(len(word["initial"]) == OWNED, "owned slot unexpectedly initially public")
    first_init = next(index for index, event in enumerate(word["program"])
                      if event[:2] == ["INIT", OWNED])
    require(first_init == 8448 and word["program"][first_init] == ["INIT", OWNED, 737],
            "first source owned INIT changed")
    return word["program"][:18]


def nearest_even(value):
    lower = value.numerator // value.denominator
    left = value - lower
    right = lower + 1 - value
    if left < right:
        return lower
    if right < left:
        return lower + 1
    return lower if lower % 2 == 0 else lower + 1


def stochastic_round(value, bit):
    require(type(bit) is int and bit in (0, 1), "UP coin must be integer0or1")
    lower = value.numerator // value.denominator
    if value.denominator == 1:
        return lower
    require(value - lower == Fraction(1, 2), "only half-grid rounding permitted")
    return lower + bit


def entrance(x, y, z, destinations):
    require(len(destinations) == 6, "six destination entrances required")
    state = {role: Fraction(value) for role, value in zip(SOURCES, (x, y, z))}
    state.update({role: Fraction(value) for role, value in zip(DESTINATIONS, destinations)})
    return state


def literal(program, values, grid=Fraction(1), coins=None):
    state = dict(values)
    used = 0
    for event in program:
        operation = event[0]
        if operation == "INIT":
            require(event == ["INIT", OWNED, 3] and OWNED not in state,
                    "invalid owned INIT")
            state[OWNED] = Fraction(0)
            continue
        if operation == "CLEAR":
            require(event == ["CLEAR", OWNED, 3], "invalid CLEAR site")
            break
        require(operation == "ADD" and len(event) == 5, "only scalar ADD prefix allowed")
        _, destination, source, coefficient_text, frame = event
        require(destination != source and frame == 3, "invalid prefix role/frame")
        coefficient = Fraction(coefficient_text)
        total = state[destination] + coefficient * state[source]
        units = total / grid
        if coins is None:
            state[destination] = nearest_even(units) * grid
        elif coefficient.denominator == 2:
            require(used < len(coins), "insufficient coin bits")
            state[destination] = stochastic_round(units, coins[used]) * grid
            used += 1
        else:
            require(units.denominator == 1, "unfunded non-half stochastic site")
            state[destination] = total
    require(coins is None or used == len(coins), "unused coin bits")
    require(all(state[role] == values[role] for role in SOURCES), "public source changed")
    return state


def clear_guard(state):
    require(OWNED in state and state[OWNED] == 0, "CLEAR requires zero owned value")
    result = dict(state)
    del result[OWNED]
    return result


def public_values(state):
    return [integer_value(state[role]) for role in DESTINATIONS]


def parity_row(x, y, destinations, z=0):
    base = x + y // 2 + 2 * z
    if y % 2:
        shared_bit = (x + y // 2) % 2
        old_bits = [(destination + x + y // 2) % 2 for destination in destinations]
        old_error = [2 * bit - 1 for bit in old_bits]
        shared_error = [2 * shared_bit - 1] * 6
        cleanup = shared_bit - (x + shared_bit) % 2
    else:
        shared_bit, old_bits, old_error, shared_error, cleanup = 0, [0] * 6, [0] * 6, [0] * 6, 0
    old = [destination + base + bit for destination, bit in zip(destinations, old_bits)]
    shared = [destination + base + shared_bit for destination in destinations]
    equal, legal = old == shared, cleanup == 0
    return {"case": [x, y, *destinations], "old_public": old, "shared_public": shared,
            "old_error_twice": old_error, "shared_error_twice": shared_error,
            "public_delta": [new - prior for new, prior in zip(shared, old)],
            "cleanup_residue": cleanup, "public_equal": equal, "clear_ok": legal,
            "legal_equivalent": equal and legal}


def check_literal_row(prefix, row, z=0):
    x, y, *destinations = row["case"]
    values = entrance(x, y, z, destinations)
    old = literal(prefix, values)
    shared = literal(shared_word(), values)
    require(public_values(old) == row["old_public"], "parity/old literal mismatch")
    require(public_values(shared) == row["shared_public"], "parity/shared literal mismatch")
    require(integer_value(shared[OWNED]) == row["cleanup_residue"], "cleanup formula mismatch")
    ideal = Fraction(x) + Fraction(y, 2) + 2 * z
    for state, key in ((old, "old_error_twice"), (shared, "shared_error_twice")):
        actual = [integer_value(2 * (state[role] - destination - ideal))
                  for role, destination in zip(DESTINATIONS, destinations)]
        require(actual == row[key], "literal error definition mismatch")
    if row["clear_ok"]:
        require(OWNED not in clear_guard(shared), "legal CLEAR did not deactivate")
    else:
        try:
            clear_guard(shared)
        except ValueError:
            return
        raise ValueError("nonzero owned CLEAR accepted")


def deterministic(prefix):
    rows = []
    for x in (0, 1):
        for y in range(4):
            for destinations in product((0, 1), repeat=6):
                row = parity_row(x, y, destinations)
                check_literal_row(prefix, row)
                rows.append(row)
    return rows


def stochastic_row(bits):
    old_bits, preparation, inverse = bits[:6], bits[6], bits[7]
    return {"coins": list(bits), "old_public": [1 + bit for bit in old_bits],
            "shared_public": [1 + preparation] * 6,
            "old_error_twice": [2 * bit - 1 for bit in old_bits],
            "shared_error_twice": [2 * preparation - 1] * 6,
            "cleanup_residue": preparation + inverse - 1,
            "clear_ok": preparation + inverse == 1}


def stochastic(prefix):
    rows = []
    values = entrance(1, 1, 0, [0] * 6)
    for bits in product((0, 1), repeat=8):
        row = stochastic_row(bits)
        old = literal(prefix, values, coins=bits[:6])
        shared = literal(shared_word(), values, coins=bits[6:])
        require(public_values(old) == row["old_public"], "old stochastic literal mismatch")
        require(public_values(shared) == row["shared_public"], "shared stochastic literal mismatch")
        require(integer_value(shared[OWNED]) == row["cleanup_residue"], "stochastic cleanup mismatch")
        require(row["clear_ok"] == (shared[OWNED] == 0), "stochastic CLEAR status mismatch")
        rows.append(row)
    return rows


def covariance(vectors):
    size, count = len(vectors[0]), len(vectors)
    means = [sum(vector[index] for vector in vectors) / count for index in range(size)]
    return [[sum((vector[i] - means[i]) * (vector[j] - means[j])
                 for vector in vectors) / count for j in range(size)] for i in range(size)]


def moments(rows):
    old = [[Fraction(value, 2) for value in row["old_error_twice"]] for row in rows]
    shared = [[Fraction(value, 2) for value in row["shared_error_twice"]] for row in rows]
    extended = [vector + [Fraction(row["cleanup_residue"])]
                for vector, row in zip(shared, rows)]
    old_cov, shared_cov, extended_cov = covariance(old), covariance(shared), covariance(extended)
    require(old_cov == [[Fraction(i == j, 4) for j in range(6)] for i in range(6)],
            "old covariance not diagonal quarter")
    require(shared_cov == [[Fraction(1, 4)] * 6 for _ in range(6)],
            "shared covariance not all-ones quarter")
    histogram = Counter(row["cleanup_residue"] for row in rows)
    return {"old_covariance": [[pair(value) for value in line] for line in old_cov],
            "shared_covariance": [[pair(value) for value in line] for line in shared_cov],
            "shared_cleanup_covariance": [pair(extended_cov[i][6]) for i in range(6)],
            "cleanup_variance": pair(extended_cov[6][6]),
            "cleanup_histogram": sorted(map(list, histogram.items())), "coin_cases": len(rows)}


def fine_grid_positive(prefix, rows):
    for row in rows:
        x, y, *destinations = row["case"]
        values = entrance(x, y, 0, destinations)
        old = literal(prefix, values, Fraction(1, 2))
        shared = literal(shared_word(), values, Fraction(1, 2))
        ideal = Fraction(x) + Fraction(y, 2)
        require(all(old[role] == shared[role] == destination + ideal
                    for role, destination in zip(DESTINATIONS, destinations)),
                "exact half-grid public equivalence failed")
        require(shared[OWNED] == 0 and OWNED not in clear_guard(shared),
                "exact half-grid CLEAR failed")
    return {"exact_half_grid_classes": len(rows), "all_public_equal": True,
            "all_owned_clear_legal": True}


def signed_probes(prefix, rows):
    count = 0
    for row in rows:
        x, y, *destinations = row["case"]
        shifts = [(-8, -12, -7, [2 * (j - 3) for j in range(6)]),
                  (2 ** 20, -(2 ** 22), 2 ** 20, [2 ** 20 + 2 * j for j in range(6)])]
        for dx, dy, z, offsets in shifts:
            shifted = [destination + offset for destination, offset in zip(destinations, offsets)]
            actual = parity_row(x + dx, y + dy, shifted, z)
            check_literal_row(prefix, actual, z)
            for key in ("old_error_twice", "shared_error_twice", "public_delta",
                        "cleanup_residue", "public_equal", "clear_ok", "legal_equivalent"):
                require(canonical(actual[key]) == canonical(row[key]), "signed period law failed")
            count += 1
    return {"signed_large_literal_cases": count, "whole_period_translations": True}


def rejected(function, argument):
    try:
        function(argument)
    except ValueError:
        return True
    return False


def integer_control(value):
    return exact_int(value, "control")


def covariance_guard(matrix):
    require(matrix == [[[1, 4] for _ in range(6)] for _ in range(6)],
            "shared covariance must be all-ones quarter")
    return True


def controls(prefix, moment_data):
    bad_clear = literal(shared_word(), entrance(1, 1, 0, [0] * 6))
    reused = [literal(shared_word(), entrance(1, 1, 0, [0] * 6), coins=(bit, bit))[OWNED]
              for bit in (0, 1)]
    matched = [literal(shared_word(), entrance(1, 1, 0, [0] * 6), coins=(bit, 1 - bit))[OWNED]
               for bit in (0, 1)]
    result = {"nonzero_clear_rejected": rejected(clear_guard, bad_clear),
              "same_coin_inverse_fails": all(value != 0 for value in reused),
              "complemented_inverse_restores_credited_6066": matched == [0, 0],
              "half_up_differs_from_nearest_even": nearest_even(Fraction(1, 2)) != 1,
              "signed_tie_differs_from_truncation": nearest_even(Fraction(-3, 2)) != int(Fraction(-3, 2)),
              "public_equality_does_not_imply_clear": parity_row(1, 1, [0] * 6)["public_equal"] and bad_clear[OWNED] != 0,
              "false_diagonal_shared_covariance_rejected": rejected(covariance_guard, moment_data["old_covariance"]),
              "boolean_integer_rejected": rejected(integer_control, True),
              "duplicate_json_rejected": rejected(strict_json, '{"a":false,"a":1}'),
              "json_nan_rejected": rejected(strict_json, '{"a":NaN}'),
              "json_infinity_rejected": rejected(strict_json, '{"a":Infinity}'),
              "json_finite_float_rejected": rejected(strict_json, '{"a":1.5}'),
              "json_overflow_float_rejected": rejected(strict_json, '{"a":1e999}')}
    require(all(type(value) is bool and value for value in result.values()),
            "semantic discriminator did not distinguish")
    require(prefix != shared_word(), "literal source/replacement unexpectedly identical")
    return result


def generate():
    prefix = bind_source(load_inputs())
    rows = deterministic(prefix)
    stochastic_rows = stochastic(prefix)
    moment_data = moments(stochastic_rows)
    counts = {"classes": len(rows), "illegal_clear": sum(not row["clear_ok"] for row in rows),
              "public_differences": sum(not row["public_equal"] for row in rows),
              "both_failures": sum(not row["clear_ok"] and not row["public_equal"] for row in rows),
              "legal_equivalent": sum(row["legal_equivalent"] for row in rows)}
    require(counts == {"classes": 512, "illegal_clear": 128, "public_differences": 252,
                       "both_failures": 126, "legal_equivalent": 258}, "parity classification changed")
    return {"schema_version": 1, "source_manifest_sha256": PIN_SHA,
            "case_manifest_sha256": CASE_SHA, "deterministic_rows": rows,
            "deterministic_counts": counts, "stochastic_rows": stochastic_rows,
            "stochastic_moments": moment_data,
            "positive_control": fine_grid_positive(prefix, rows),
            "signed_translations": signed_probes(prefix, rows), "controls": controls(prefix, moment_data),
            "source_binding": {"source_event_count": 18561, "interpreted_old_events": 18,
                               "replacement_events": 14, "first_owned_init_zero_based": 8448,
                               "decompressed_word_sha256": WORD_SHA},
            "code_sha256": sha(Path(__file__).read_bytes())}


def compare_primary(receipt, path):
    primary = strict_json(path.read_bytes())
    require(type(primary) is dict, "primary receipt must be object")
    for key in COMMON:
        require(key in primary and canonical(primary[key]) == canonical(receipt[key]),
                "independent primary data mismatch: " + key)
    return {"actual_primary_deterministic_rows": 512, "actual_primary_stochastic_rows": 256,
            "complete_public_private_and_covariance_data": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-first", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    require(not (args.write_first and args.check_primary), "first receipt must remain blind")
    receipt = generate()
    if args.write_first:
        with args.write_first.open("x") as stream:
            json.dump(receipt, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        frozen = strict_json((ROOT / "ORACLE.json").read_bytes())
        require(canonical(frozen) == canonical(receipt), "frozen oracle receipt mismatch")
    if args.check_primary:
        print(json.dumps(compare_primary(receipt, args.check_primary), sort_keys=True))
    print("PASS_P104_SHARED_PREFIX_ROUNDED_ORACLE deterministic=512 stochastic=256")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError, StopIteration) as error:
        print("FAIL_P104_SHARED_PREFIX_ROUNDED_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
