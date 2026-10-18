#!/usr/bin/env python3
"""Source-bound exact correlated-update certificate. Apache-2.0.

Adam Gall, with substantial OpenAI Codex assistance. No supplier/kappa claim.
"""
from __future__ import annotations

import argparse
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import re
import sys

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from model import Invalid, coherent_optimum, layout, multiply, optimum, replay, require, word
from oracle import cheapest, exhaustive_parities


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def bindings():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    checked = []
    for item in manifest["files"]:
        if item["usage"] != "input":
            continue
        data = (ROOT / item["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == item["sha256"], "source SHA256 drift: " + item["path"])
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        require(blob == item["git_blob"], "source Git blob drift: " + item["path"])
        checked.append(item["path"])
    selection = json.loads((PACKAGE / "SELECTION.json").read_text())
    task = json.loads((PACKAGE / "TASK.json").read_text())
    require(selection["seed"] == task["seed"] == "829a355b1cafac3569bc060e0062cf20", "selection seed")
    require(selection["base_commit"] == task["base_commit"] == manifest["base_commit"], "selection base")
    require(any(card["task_id"] == task["task_id"] for card in selection["suggestions"]), "unemitted task")
    return checked


def price(events, b, a, correction):
    total = Fraction(0)
    for kind, i in events:
        if kind == "B":
            total += b[i]
        elif kind == "A":
            total += a[i]
        elif kind == "D":
            total += correction[i]
    return total


def tariffs(k):
    return (
        ([2 + 3 * (i % 2) for i in range(k)], [1 + 2 * (i % 2) for i in range(k)], [1 + 3 * (j % 2) for j in range(k - 1)]),
        ([7] * k, [3 + i % 2 for i in range(k)], [2] * (k - 1)),
        ([Fraction(i + 2, 3) for i in range(k)], [Fraction(i + 1, 5) for i in range(k)], [Fraction(j + 3, 7) for j in range(k - 1)]),
    )


def census():
    rows = []
    settled = 0
    parity_words = 0
    coherent_gains = 0
    for d in (1, 2):
        for k in range(1, 5):
            for vectors in product(range(1 << d), repeat=k - 1):
                for tariff, (b, a, correction) in enumerate(tariffs(k)):
                    cost, q, t = optimum(vectors, d, b, a, correction)
                    independent, count = cheapest(vectors, d, b, a, correction)
                    brute, legal = exhaustive_parities(vectors, d, b, a, correction)
                    require(cost == independent == brute, "independent price mismatch")
                    events = word(q, t)
                    require(price(events, b, a, correction) == cost, "unpaid emitted operation")
                    replay(events, vectors, d, (1,), (1,), ((1,),) * k, 1)
                    # Invertible renaming of the two independent update rows.
                    if d == 2:
                        renamed = tuple(((v & 1) << 1) | ((v >> 1) & 1) for v in vectors)
                        require(optimum(renamed, d, b, a, correction)[0] == cost, "basis-dependent price")
                    coherent_gains += cost < coherent_optimum(vectors, b, a, correction)[0]
                    settled += count
                    parity_words += legal
                    rows.append([d, k, list(vectors), tariff, str(cost), list(q), list(t)])
    return {"instances": len(rows), "rows_sha256": digest(rows), "oracle_settled": settled,
            "feasible_parity_words_summed": parity_words, "strict_coherence_gains": coherent_gains}


def specializations():
    independent_count = 0
    for k in range(1, 9):
        vectors = tuple(1 << j for j in range(k - 1))
        for b, a, correction in tariffs(k)[:2]:
            require(optimum(vectors, k - 1, b, a, correction)[0] == coherent_optimum(vectors, b, a, correction)[0], "independent-update predecessor mismatch")
            independent_count += 1
    repeated = []
    for k in range(1, 25):
        cost, q, t = optimum((1,) * (k - 1), 1, [7] * k, [1] * k, [100] * (k - 1))
        source_calls = k + ((k + 1) // 2) % 2 + (k // 2) % 2
        require(cost == 2 * k + 7 * source_calls and not any(t), "period-four corollary")
        repeated.append([k, source_calls, str(cost)])
    return {"independent_update_cases": independent_count, "periodic_cases": repeated}


def source_fixture():
    """Read the named predecessor's actual pilot, not a regenerated random map."""
    text = (ROOT / "research/mutable-connector-delivery-optimum/README.md").read_text()
    def vector(pattern):
        matches = re.findall(pattern, text)
        require(len(matches) == 1, "ambiguous predecessor fixture")
        return tuple(int(value) for value in matches[0].split(","))
    B = vector(r"three-bit `B=\(([0-9,]+)\)`")
    C = vector(r"updates `C_i=\(([0-9,]+)\)`")
    first = vector(r"readers alternating `\(([0-9,]+)\)`")
    second = vector(r"readers alternating `\([0-9,]+\)` and `\(([0-9,]+)\)`")
    return B, C, (first, second) * 2


def direct_pilot(B, C, readers):
    x, updates, z, outputs, bits = layout(3, 1, 3, 3, 1, 4)
    rows = [1 << j for j in range(bits)]
    gates = []
    for i, reader in enumerate(readers):
        for target, mask in zip(outputs[i], multiply(reader, B)):
            for j, source in enumerate(x):
                if mask >> j & 1:
                    rows[target] ^= rows[source]
                    gates.append((source, target))
        if i < 3:
            for target, mask in zip(x, C):
                if mask:
                    rows[target] ^= rows[updates[0][0]]
                    gates.append((updates[0][0], target))
    return rows, gates


def walk_head(gates):
    steps = 0
    for source, target in gates:
        position = 0
        for next_position in (source + 1, target + 1, 0):
            steps += abs(next_position - position)
            position = next_position
    return steps


def scalar_inputs(events):
    result = replay(events, (1, 1, 1), 1, (1,), (1,), ((1,),) * 4, 1)
    bits = result["bits"]
    for state in range(1 << bits):
        actual = [(state >> j) & 1 for j in range(bits)]
        for source, target in result["gates"]:
            actual[target] ^= actual[source]
        expected = [(mask & state).bit_count() % 2 for mask in result["matrix"]]
        require(actual == expected, "dirty scalar execution")
    return 1 << bits


def pilot():
    B, C, readers = source_fixture()
    vectors = (1, 1, 1)
    b, a, correction = [7] * 4, [3, 4, 3, 4], [2] * 3
    plans = {"correlated": optimum(vectors, 1, b, a, correction),
             "coherent": coherent_optimum(vectors, b, a, correction),
             "closed": (Fraction(84), (0,) * 4, (0,) * 3)}
    output = {}
    endpoint = None
    dirty_executions = 0
    for name, (cost, q, t) in plans.items():
        events = word(q, t)
        result = replay(events, vectors, 1, B, C, readers, 1)
        require(price(events, b, a, correction) == cost, "pilot query invoice")
        require(result["xor"] == cost + 3, "omitted mandatory source update cost")
        require(result["head_steps"] == walk_head(result["gates"]), "head-movement invoice")
        result["unit_backend_total"] = result["head_steps"] + 5 * result["xor"]
        if endpoint is None:
            endpoint = result["matrix"]
        require(result["matrix"] == endpoint, "pilot endpoint mismatch")
        dirty_executions += scalar_inputs(events)
        output[name] = {"query_cost": str(cost), "q": q, "t": t, "events": events, **result}
    require([output[name]["xor"] for name in ("correlated", "coherent", "closed")] == [59, 63, 87], "pilot saving")
    direct, gates = direct_pilot(B, C, readers)
    require(direct == endpoint and len(gates) == 31, "unrestricted fusion comparator")
    output["unrestricted_direct_fusion"] = {"xor": len(gates), "head_steps": walk_head(gates), "scope": "outside indivisible query alphabet; cheaper, so no unrestricted circuit optimum"}
    output["scalar_dirty_executions"] = dirty_executions
    output["fixed_map_basis_columns_per_word"] = len(endpoint)
    return output


def map_checks():
    matrices = tuple(product(range(4), repeat=2))
    vectors = (1, 3, 2)
    _, q, t = optimum(vectors, 2, [7] * 4, [1] * 4, [2] * 3)
    events = word(q, t)
    count = 0
    for B, C, reader in product(matrices, repeat=3):
        replay(events, vectors, 2, B, C, (reader, (2, 1), (3, 2), reader), 2)
        count += 1
    return {"map_triples": count, "basis_columns_per_map": 16, "update_vectors": vectors, "q": q, "t": t}


def controls():
    B, C, readers = source_fixture()
    good = list(word((1, 1, 1, 1), (0, 0, 0)))
    coherent = list(word((1, 1, 1, 1), (1, 0, 1)))
    checked = []

    def reject(name, callback):
        try:
            callback()
        except Invalid as error:
            checked.append({"name": name, "rejection": str(error)})
        else:
            raise Invalid("control accepted: " + name)

    def run(events, vectors=(1, 1, 1), d=1):
        return replay(events, vectors, d, B, C, readers, 1)

    reject("independent_last_update_not_alias", lambda: run(good, (1, 1, 2), 2))
    reject("omit_final_source_query", lambda: run([event for event in good if event != ("B", 3)]))
    reject("omit_old_dirty_read", lambda: run(good[1:]))
    reject("prewrite_future_output", lambda: run([("A", 1)] + good))
    after_delivery = good.index(("deliver", 0)) + 1
    reject("write_after_delivery", lambda: run(good[:after_delivery] + [("A", 0)] + good[after_delivery:]))
    reject("omit_imposed_mutation", lambda: run([event for event in good if event != ("M", 0)]))
    reject("omit_one_coherent_repair", lambda: run([event for event in coherent if event != ("D", 0)]))
    misplaced = [event for event in coherent if event != ("D", 0)]
    next_read = misplaced.index(("A", 1)) + 1
    reject("delay_repair_past_its_cut", lambda: run(misplaced[:next_read] + [("D", 0)] + misplaced[next_read:]))
    reject("unpriced_operation", lambda: require(price(good, [7] * 4, [3, 4, 3, 4], [2] * 3) == 55, "unpaid query"))
    reject("negative_complete_tariff", lambda: optimum((1, 1, 1), 1, [-1, 7, 7, 7], [3, 4, 3, 4], [2] * 3))
    reject("unregistered_update_coordinate", lambda: optimum((1, 1, 2), 1, [7] * 4, [3, 4, 3, 4], [2] * 3))
    return checked


def evidence():
    return {"schema_version": 1, "status": "PASS_CORRELATED_UPDATE_DELIVERY", "source_inputs": bindings(),
            "census": census(), "specializations": specializations(), "pilot": pilot(),
            "arbitrary_map_fixtures": map_checks(), "controls": controls(),
            "limits": "Exact declared-query theorem and finite evidence only; no admitted supplier, rank-profile gain, kappa, physical tape admission, or formal-kernel theorem."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    try:
        result = evidence()
        if args.write_result:
            with args.write_result.open("x") as stream:
                json.dump(result, stream, indent=2)
                stream.write("\n")
        else:
            saved = json.loads((PACKAGE / "RESULT.json").read_text())
            require(canonical(result) == canonical(saved), "receipt mismatch")
        print(f"PASS_CORRELATED_UPDATE_DELIVERY instances={result['census']['instances']} "
              f"pilot=59/63/87 direct_fusion=31 maps={result['arbitrary_map_fixtures']['map_triples']} "
              f"controls={len(result['controls'])} no_new_kappa")
    except (Invalid, OSError, KeyError, ValueError) as error:
        raise SystemExit("FAIL_CORRELATED_UPDATE_DELIVERY " + str(error)) from error


if __name__ == "__main__":
    main()
