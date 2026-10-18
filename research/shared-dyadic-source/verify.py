#!/usr/bin/env python3
"""Exact bounded checks for shared-source multi-output dyadic batches.

Hanson Sun, with substantial OpenAI Codex assistance. Apache-2.0.
The constructor only supplies literal words. oracle.py imports no constructor.
"""
import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parent.parent


def local_module(name):
    spec = importlib.util.spec_from_file_location("shared_dyadic_" + name, PACKAGE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


o = local_module("oracle")
builder = local_module("construct")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def source_pins():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = {}
    for entry in manifest["files"]:
        if entry["usage"] != "input":
            continue  # Historical provenance is checked by the registered Git hook.
        path = ROOT / entry["path"]
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        o.require(digest == entry["sha256"] and blob == entry["git_blob"], "source drift: " + entry["path"])
        checked[entry["path"]] = digest
    o.require(len(checked) == 10, "incomplete source inventory")
    return checked


def validate_certificate(cert):
    o.require(canonical(cert) == canonical(builder.certificate()), "certificate differs from literal constructor")
    o.require(cert["masks"] == [[0, 1, 4], [0, 2, 5], [1, 2, 5], [0, 2, 3], [3, 4, 5]],
              "seed-selected incidence matrix changed")
    for name in ("shared", "separate"):
        o.validate_word(cert[name], 5, name == "shared")
        o.require(o.laurent(cert[name], 7) == o.wanted_laurent(cert["masks"]), "wrong dirty-row endpoint")
        bill = o.recount(cert[name], cert["lowerings"])
        o.require(canonical(bill) == canonical(cert["invoices"][name]), "unpaid native event")
    o.require(o.incidence_counts(cert["masks"]) == (13, 40, 30), "wrong comparison")
    return cert["invoices"]


def check_case(masks, moduli, check_columns=True):
    rows = len(masks) + 2
    wanted = o.wanted_laurent(masks)
    words = (builder.shared_word(masks), builder.separate_word(masks))
    counts = o.incidence_counts(masks)
    columns = 0
    for index, word in enumerate(words):
        o.validate_word(word, len(masks), index == 0)
        o.require(o.laurent(word, rows) == wanted, "case Laurent endpoint")
        o.require(o.laurent(word + o.inverse_word(word), rows) == [{(j, 0)} for j in range(rows)],
                  "literal inverse did not restore all dirty rows")
        o.require(sum(e[0] == "Q" for e in word) == counts[index], "query formula")
        o.require(sum(e[0] == "X" for e in word) == counts[2], "XOR formula")
    for modulus in moduli:
        if check_columns:
            for row in range(rows):
                for address in range(modulus):
                    state = [0] * rows
                    state[row] = 1 << address
                    expected = o.orbit_expected(masks, state, modulus)
                    for word in words:
                        actual = o.orbit_replay(word, state, modulus)
                        o.require(actual == expected, "cyclic dirty-column endpoint")
                        o.require(o.orbit_replay(o.inverse_word(word), actual, modulus) == state,
                                  "cyclic literal inverse")
                    columns += 1
        rng = random.Random(55 + modulus + 101 * rows)
        state = [rng.getrandbits(modulus) for _ in range(rows)]
        expected = o.orbit_expected(masks, state, modulus)
        for word in words:
            actual = o.orbit_replay(word, state, modulus)
            o.require(actual == expected, "simultaneous arbitrary dirty values")
            o.require(o.orbit_replay(o.inverse_word(word), actual, modulus) == state, "dirty inverse")
    return columns


def incidence_census():
    patterns = columns = 0
    digest = hashlib.sha256()
    for outputs, indices in ((2, 4), (3, 3)):
        for vector in itertools.product(range(1 << indices), repeat=outputs):
            masks = [[j for j in range(indices) if bits & (1 << j)] for bits in vector]
            columns += check_case(masks, (7,))
            digest.update((canonical([masks, o.incidence_counts(masks)]) + "\n").encode())
            patterns += 1
    o.require((patterns, columns) == (768, 25088), "incomplete incidence census")
    return {"patterns": patterns, "dirty_columns_per_implementation": columns,
            "domain": [{"outputs": 2, "indices": 4}, {"outputs": 3, "indices": 3}],
            "orbit_modulus": 7, "count_digest": digest.hexdigest()}


def native_checks(lowerings):
    rational = modular = full = 0
    digest = hashlib.sha256()
    for power_string, events in sorted(lowerings.items(), key=lambda pair: int(pair[0])):
        power = int(power_string)
        parsed = o.parse_native(events)
        inverse = o.inverse_native(parsed)
        o.require(sum(e[0] == "C" for e in parsed) == 1, "ordinary child missing or duplicated")
        o.require(sum(e[0] == "A" for e in parsed) == 6, "affine event omitted")
        for column in range(8):
            vector = [Fraction(int(j == column)) for j in range(8)]
            actual = o.native_replay(parsed, vector)
            o.require(actual == o.native_expected(power, vector), "rational native column")
            o.require(o.native_replay(inverse, actual) == vector, "rational native inverse")
            rational += 1
        for modulus in (3, 5, 9, 25, 49, 257):
            forward_mod, inverse_mod = o.specialize(parsed, modulus), o.specialize(inverse, modulus)
            for column in range(8):
                vector = [int(j == column) for j in range(8)]
                actual = o.native_replay(forward_mod, vector, modulus)
                o.require(actual == o.native_expected(power, vector, modulus), "modular native column")
                o.require(o.native_replay(inverse_mod, actual, modulus) == vector, "modular native inverse")
                modular += 1
            if modulus not in (3, 5):
                continue
            for coordinates in itertools.product(range(modulus), repeat=6):
                for spectator0, spectator1 in itertools.product(range(2), repeat=2):
                    vector = [coordinates[0], spectator0, *coordinates[1:5], spectator1, coordinates[5]]
                    actual = o.native_replay(forward_mod, vector, modulus)
                    o.require(actual == o.native_expected(power, vector, modulus), "full native address")
                    o.require(o.native_replay(inverse_mod, actual, modulus) == vector, "full native inverse")
                    digest.update(bytes(actual))
                    full += 1
    return {"powers": sorted(map(int, lowerings)), "rational_columns": rational,
            "modular_columns": modular, "complete_address_inputs": full,
            "address_moduli": [3, 5], "interleaved_binary_spectators": 2,
            "full_address_digest": digest.hexdigest()}


def native_array_checks(cert):
    """Whole VALUE arrays, using the seven-event address interpreter for queries.

    This does not replace a native tape implementation. A full mod-3 domain
    with two spectator fields checks every arbitrary dirty input column.
    """
    modulus = 3
    addresses = [tuple([a[0], b, *a[1:5], c, a[5]])
                 for a in itertools.product(range(modulus), repeat=6)
                 for b, c in itertools.product(range(2), repeat=2)]
    index = {a: j for j, a in enumerate(addresses)}
    permutations = {}
    for power_string, events in cert["lowerings"].items():
        power = int(power_string)
        program = o.specialize(o.parse_native(events), modulus)
        permutations[power] = [index[tuple(o.native_replay(program, a, modulus))] for a in addresses]
        inverse = [0] * len(addresses)
        for before, after in enumerate(permutations[power]):
            inverse[after] = before
        if -power in permutations:
            o.require(permutations[-power] == inverse, "inconsistent inverse permutation")
        permutations[-power] = inverse
    desired = {}
    for mask in cert["masks"]:
        for j in mask:
            for power in (2 ** j, -(2 ** j)):
                desired[power] = [index[tuple(o.native_expected(power, a, modulus))] for a in addresses]

    def run(word, values):
        values = [set(v) for v in values]
        for op, row, argument in word:
            if op == "Q":
                permutation = permutations[argument]
                values[row] = {permutation[a] for a in values[row]}
            else:
                values[row] ^= values[argument]
        return values

    columns = 0
    for row in range(7):
        for address in range(len(addresses)):
            incoming = [set() for _ in range(7)]
            incoming[row].add(address)
            expected = [set(v) for v in incoming]
            if row == 0:
                for output, mask in enumerate(cert["masks"], 1):
                    for j in mask:
                        expected[output].symmetric_difference_update((desired[2 ** j][address],))
                        expected[output].symmetric_difference_update((desired[-(2 ** j)][address],))
            for name in ("shared", "separate"):
                actual = run(cert[name], incoming)
                o.require(actual == expected, "whole-array dirty-column endpoint")
                o.require(run(o.inverse_word(cert[name]), actual) == incoming, "whole-array literal inverse")
            columns += 1
    rng = random.Random(55)
    for _ in range(16):
        incoming = [{a for a in range(len(addresses)) if rng.randrange(13) == 0} for _ in range(7)]
        expected = [set(v) for v in incoming]
        for output, mask in enumerate(cert["masks"], 1):
            for j in mask:
                for power in (2 ** j, -(2 ** j)):
                    expected[output] ^= {desired[power][a] for a in incoming[0]}
        for name in ("shared", "separate"):
            actual = run(cert[name], incoming)
            o.require(actual == expected, "whole-array simultaneous dirt")
            o.require(run(o.inverse_word(cert[name]), actual) == incoming, "whole-array dirty inverse")
    return {"modulus": modulus, "six_field_addresses": modulus ** 6, "spectator_assignments": 4,
            "dirty_columns_per_implementation": columns, "simultaneous_dirty_fixtures": 16}


def negative_controls(cert):
    names = []
    masks = cert["masks"]
    expected = o.wanted_laurent(masks)
    word = cert["shared"]

    def wrong_word(name, candidate):
        o.require(o.laurent(candidate, 7) != expected, "undetected mathematical mutation: " + name)
        names.append(name)

    wrong_word("omit_source_return", word[:-1])
    wrong_word("omit_first_query", word[1:])
    bad = deepcopy(word)
    first_xor = next(i for i, e in enumerate(bad) if e[0] == "X")
    del bad[first_xor]
    wrong_word("omit_output_injection", bad)
    bad = deepcopy(word)
    bad[first_xor][1] = 1 if bad[first_xor][1] != 1 else 2
    wrong_word("wrong_output_port", bad)
    collapsed = [[op, 1 if op == "X" else row, argument] for op, row, argument in word]
    collapsed_state = o.laurent(collapsed, 7)
    sum_actual, sum_expected = set(), set()
    for row in range(1, 6):
        sum_actual ^= collapsed_state[row]
        sum_expected ^= expected[row]
    o.require(sum_actual == sum_expected, "collapsed-output control must preserve the aggregate")
    wrong_word("aggregate_correct_but_separate_outputs_wrong", collapsed)
    bad = deepcopy(word)
    bad[first_xor][2] = 6
    wrong_word("read_dirty_spectator", bad)
    bad = deepcopy(word)
    bad[0][2] *= -1
    wrong_word("reverse_one_query", bad)
    bad = deepcopy(word)
    bad[0][1] = 1
    wrong_word("query_output_instead_of_source", bad)
    wrong_word("destroy_spectator", word + [["X", 6, 0]])
    o.require(o.laurent(word[:1], 7)[0] != {(0, 0)}, "source-observation control is vacuous")
    names.append("source_observation_is_not_canonical")
    # A return that is valid on a period-3 fixture can be false as a uniform identity.
    alias_word = deepcopy(word)
    alias_word[0][2] += 3  # Deliberately outside the dyadic physical alphabet as well.
    incoming = [1, 0, 0, 0, 0, 0, 0]
    o.require(o.orbit_replay(alias_word, incoming, 3) == o.orbit_replay(word, incoming, 3),
              "modulus alias positive premise")
    wrong_word("finite_modulus_alias_is_not_uniform", alias_word)
    # Every one of the seven paid events matters on the rational ADDRESS domain.
    events = cert["lowerings"]["2"]
    for omitted in range(7):
        parsed = o.parse_native(events[:omitted] + events[omitted + 1:])
        found = False
        for column in range(8):
            vector = [Fraction(int(j == column)) for j in range(8)]
            found |= o.native_replay(parsed, vector) != o.native_expected(2, vector)
        o.require(found, "native omission was not detected")
        names.append("omit_native_event_" + str(omitted))
    # Arithmetic and interface rejection controls exercise the real predicates.
    rejected = [
        ("Boolean_query", lambda: o.validate_word([["Q", 0, True]], 5, True)),
        ("nondyadic_query", lambda: o.validate_word([["Q", 0, 3]], 5, True)),
        ("source_output_alias", lambda: o.validate_word([["X", 0, 0]], 5, True)),
        ("even_modulus", lambda: o.specialize(o.parse_native(events), 4)),
        ("negative_index", lambda: builder.shared_word([[-1]])),
        ("duplicate_index", lambda: builder.shared_word([[0, 0]])),
    ]
    for name, action in rejected:
        try:
            action()
        except (ValueError, TypeError, ZeroDivisionError):
            names.append(name)
        else:
            raise o.CheckError("invalid interface accepted: " + name)
    return names


def compute(cert):
    pins = source_pins()
    bills = validate_certificate(cert)
    census = incidence_census()
    selected_columns = check_case(cert["masks"], (3, 5, 9, 17, 25, 65, 257))
    # Explicitly include empty rows, identical outputs, gapped unions and no work.
    edge_masks = [[[]], [[], []], [[0], [0]], [[0], [2]], [[0, 2], [2, 4], []],
                  [[0, 1, 2], [], [0, 1, 2]]]
    edge_columns = sum(check_case(masks, (9,)) for masks in edge_masks)
    native = native_checks(cert["lowerings"])
    arrays = native_array_checks(cert)
    controls = negative_controls(cert)
    shared_hist = bills["shared"]["query_powers"]
    separate_hist = bills["separate"]["query_powers"]
    removed = {k: separate_hist.get(k, 0) - shared_hist.get(k, 0)
               for k in set(shared_hist) | set(separate_hist)}
    o.require(min(removed.values()) >= 0 and sum(removed.values()) == 27,
              "source tour introduces a differently priced query in the selected comparison")
    return {"status": "PASS_SHARED_DYADIC_SOURCE", "assignment_seed": 55,
            "scope": "finite exact interface evidence; written uniform proof; no new kappa",
            "source_sha256": pins, "invoices": bills, "incidence_census": census,
            "selected_orbit_columns_per_implementation": selected_columns,
            "edge_case_columns_per_implementation": edge_columns,
            "native": native, "whole_arrays": arrays, "controls": controls,
            "removed_queries_by_power": {k: v for k, v in sorted(removed.items(), key=lambda p: int(p[0])) if v}}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-evidence", type=Path, help="fresh path only; ordinary verification is read-only")
    ap.add_argument("--pins-only", action="store_true", help="source/fixture checks only; not mathematical replay")
    args = ap.parse_args()
    cert = json.loads((PACKAGE / "CERTIFICATE.json").read_text())
    if args.pins_only:
        source_pins()
        validate_certificate(cert)
        print("PASS_SHARED_DYADIC_PINS_ONLY")
        return
    receipt = compute(cert)
    if args.write_evidence:
        with args.write_evidence.open("x") as out:
            json.dump(receipt, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        expected = json.loads((PACKAGE / "EVIDENCE.json").read_text())
        o.require(canonical(receipt) == canonical(expected), "evidence receipt changed")
    print("PASS_SHARED_DYADIC_SOURCE children=40->13 affine=240->78 XOR=30 patterns=768 no_new_kappa")
    print("controls=" + str(len(receipt["controls"])) + " whole_array_columns=" +
          str(receipt["whole_arrays"]["dirty_columns_per_implementation"]))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, TypeError) as error:
        print("FAIL_SHARED_DYADIC_SOURCE: " + str(error), file=sys.stderr)
        raise SystemExit(1)
