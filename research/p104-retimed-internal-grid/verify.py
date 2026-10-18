"""Bind PR2725 to the sharp Clifford/quarter-grid precision contract."""

import argparse
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kernel import N, ZERO, add, chart, native, need, plan

HERE = Path(__file__).resolve().parent


def unique(pairs):
    out = {}
    for key, value in pairs:
        need(key not in out, "duplicate JSON key")
        out[key] = value
    return out


def read(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sources():
    pins = read(HERE / "SOURCES.json")["vendored_files"]
    need(len(pins) == 13, "source inventory")
    for pin in pins:
        data = (HERE / pin["local"]).read_bytes()
        need(hashlib.sha256(data).hexdigest() == pin["sha256"], "source SHA256")
        blob = hashlib.sha1(
            b"blob " + str(len(data)).encode() + b"\0" + data
        ).hexdigest()
        need(blob == pin["git_blob"], "source Git blob")
    word = read(HERE / "inputs/PR2725-WORD.json")
    raw = gzip.decompress((HERE / "inputs/PR2586-NATIVE.json.gz").read_bytes())
    need(len(raw) < 4_000_000, "native payload capacity")
    original = json.loads(raw, object_pairs_hook=unique)
    records = (
        original["transports"] + read(HERE / "inputs/PR2662-NATIVE.json")["transports"]
    )
    records += read(HERE / "inputs/PR2725-NATIVE.json")["transports"]
    need(len(records) == 1375 and len(word["program"]) == 5268, "source dimensions")
    need(
        word["chart"]
        == original["chart"]
        == "Delta_W = conjugate(Gamma_W) = Gamma_W^(-T)",
        "chart convention",
    )
    return word, records


def span(frame):
    need(len(frame) <= 9, "frame dimension")
    values = {0}
    for x in frame:
        need(type(x) is int and 0 < x < N and x not in values, "independent frame")
        values |= {y ^ x for y in values}
    return tuple(sorted(values))


def bind(word, records):
    pool, monomials = {}, {}
    for item in records:
        recipe = item["recipe"]
        need(set(recipe) == {"rank", "left", "right"}, "recipe schema")
        rank = recipe["rank"]
        need(type(rank) is int and 1 <= rank <= 8, "native rank")
        sides = []
        for side in ("left", "right"):
            key = encoded(recipe[side])
            if key not in monomials:
                monomials[key] = plan(recipe[side])
            sides.append(monomials[key])
        key = (tuple(item["old"]), tuple(item["new"]))
        compiled = (rank, *sides)
        need(key not in pool or pool[key] == compiled, "conflicting native binding")
        pool[key] = compiled
    uses, profile = {}, Counter()
    for i, event in enumerate(word["program"]):
        if event[0] == "transport":
            key = (tuple(event[2]), tuple(event[3]))
            need(key in pool and pool[key][0] == event[4], "missing native binding")
            uses[i] = pool[key]
            profile[event[4]] += 1
    need(
        dict(profile) == {1: 1502, 2: 58, 3: 74, 4: 93, 5: 57, 6: 56, 7: 91, 8: 9},
        "retimed profile",
    )
    return uses, {
        "occurrences": len(uses),
        "pool_edges": len(pool),
        "monomials": len(monomials),
        "rank_mass": sum(r * n for r, n in profile.items()),
    }


def quarter(row, message):
    need(all((4 * v).denominator == 1 for v in row.values()), message)


def row_add(target, source, coefficient):
    product = {s: coefficient * v for s, v in source.items()}
    quarter(product, "scalar product outside quarter grid")
    for s, value in product.items():
        result = target.get(s, Q(0)) + value
        if result:
            target[s] = result
        else:
            target.pop(s, None)
    return len(product), sum(map(abs, product.values()), Q(0))


def logical(word):
    initial = word["initial_frames"]
    need(len(initial) == 358, "public inputs")
    frames = {r: span(f) for r, f in initial.items()}
    rows = {r: {r: Q(1)} for r in initial}
    counts, visits, products, peak = Counter(), 0, 0, Q(1)
    for i, event in enumerate(word["program"]):
        op, role = event[:2]
        counts[op] += 1
        if op == "transport":
            old, new = span(event[2]), span(event[3])
            need(
                frames[role] == old and (set(old) < set(new) or set(new) < set(old)),
                "transport frame",
            )
            need(event[4] == abs(len(event[2]) - len(event[3])), "transport rank")
            frames[role] = new
        elif op == "add":
            need(
                role != event[2] and frames[role] == frames[event[2]] == span(event[4]),
                "ADD common frame",
            )
            n, norm = row_add(rows[role], rows[event[2]], Q(event[3]))
            products += n
            peak = max(peak, norm)
        elif op == "sign":
            need(event[2] == "-1" and frames[role] == span(event[3]), "sign frame")
            rows[role] = {s: -v for s, v in rows[role].items()}
        elif op == "zero":
            need(role == "C" and role not in rows, "private allocation")
            rows[role], frames[role] = {}, span(event[2])
        else:
            need(
                op == "erase"
                and role == "C"
                and not rows[role]
                and frames[role] == span(event[2]),
                "strict private erasure",
            )
            del rows[role], frames[role]
        if op != "erase":
            quarter(rows[role], "stored row outside quarter grid")
            visits += len(rows[role])
            peak = max(peak, sum(map(abs, rows[role].values()), Q(0)))
        if i == 2040:
            need(
                role == "D18"
                and frames[role] == tuple(range(N))
                and initial["Y2"] == []
                and rows[role]["Y2"] == -Q(1, 4),
                "sharp cut",
            )
    return finish_logical(word, rows, frames, counts, visits, products, peak)


def finish_logical(word, rows, frames, counts, visits, products, peak):
    need(
        frames == {r: span(f) for r, f in word["final_frames"].items()}, "final frames"
    )
    endpoint = {r: {s: str(v) for s, v in row.items()} for r, row in rows.items()}
    digest = hashlib.sha256(encoded(endpoint).encode()).hexdigest()
    need(
        digest
        == read(HERE / "inputs/PR2725-RESULT.json")["candidate"]["endpoint_sha256"],
        "credited complete endpoint",
    )
    need(
        counts == {"transport": 1940, "add": 3104, "sign": 208, "zero": 8, "erase": 8},
        "literal event counts",
    )
    need(peak == Q(127, 2) and products == 30007, "scalar envelope")
    return rows, {
        "counts": dict(counts),
        "term_visits": visits,
        "products": products,
        "l1_peak": str(peak),
        "endpoint_sha256": digest,
        "sharp_event": 2040,
    }


def execute(word, uses, start):
    values = dict(start)
    erases, witness = [], None
    for i, event in enumerate(word["program"]):
        op, role = event[:2]
        if op == "transport":
            values[role] = native(values[role], uses[i])
        elif op == "add":
            values[role] = add(values[role], values[event[2]], event[3])
        elif op == "sign":
            values[role] = tuple((-a, -b) for a, b in values[role])
        elif op == "zero":
            need(role not in values, "physical allocation")
            values[role] = ZERO
        else:
            need(op == "erase" and values[role] == ZERO, "physical private erasure")
            erases.append(i)
            del values[role]
        if i == 2040:
            witness = values["D18"][0]
    return values, erases, witness


def fixture(word, uses, rows, dense):
    start = {r: ZERO for r in word["initial_frames"]}
    if dense:
        for j, role in enumerate(start):
            start[role] = tuple(
                (128 * ((x + 3 * j) % 7 - 3), 128 * ((2 * x + j) % 5 - 2))
                for x in range(N)
            )
    else:
        start["Y2"] = ((128, 0),) + ZERO[1:]
    actual, erases, witness = execute(word, uses, start)
    inputs = {
        r: chart(v, word["initial_frames"][r], inverse=True) for r, v in start.items()
    }
    for role, row in rows.items():
        expected = ZERO
        for source, coefficient in row.items():
            expected = add(expected, inputs[source], coefficient)
        expected = chart(expected, word["final_frames"][role])
        need(actual[role] == expected, "canonical endpoint mismatch")
    need(len(erases) == 8, "eight physical erasures")
    if not dense:
        need(
            witness == (-1, 1) and actual["X0"][0] == (-2, 2), "sharp physical witness"
        )
    return {
        "input": "all-public dense complex" if dense else "Y2=delta_0",
        "matched_complex_coordinates": len(actual) * N,
        "erase_events": erases,
    }


def witness_depths():
    a, b = 1, 0
    guards = []
    for depth in range(1, 65):
        a, b = a + b, b - a
        denominator = 1 << (5 * depth + 2)
        real, imag = Q(a, denominator), Q(b, denominator)
        guard = max(real.denominator.bit_length(), imag.denominator.bit_length()) - 1
        need(guard == (9 * depth + 1) // 2 + 2, "tensor sharpness formula")
        guards.append(guard)
    return guards


def reject(action, fragment):
    try:
        action()
    except ValueError as error:
        need(fragment in str(error), "wrong failure: " + str(error))
        return
    raise ValueError("fault accepted: " + fragment)


def new_edge_check(records):
    vector = ((128, 0),) + ZERO[1:]
    for item in records[-2:]:
        recipe = item["recipe"]
        compiled = (recipe["rank"], plan(recipe["left"]), plan(recipe["right"]))
        direct = chart(chart(vector, item["old"], inverse=True), item["new"])
        need(native(vector, compiled) == direct, "new-edge exact phase column")
    return 2 * N


def controls(word, records):
    import copy

    wrong = copy.deepcopy(word)
    next(
        e for e in wrong["program"] if e[:3] == ["add", "X90", "N90"] and len(e[4]) == 9
    )[4] = []
    reject(lambda: logical(wrong), "ADD common frame")
    reject(lambda: row_add({"x": Q(1, 8)}, {"x": Q(1, 4)}, Q(1, 2)), "scalar product")
    wrong = copy.deepcopy(records)
    wrong[-1]["recipe"]["right"]["matrix_rows"][0] = 0
    reject(lambda: bind(word, wrong), "monomial bijection")
    wrong = copy.deepcopy(records)
    wrong[-1]["recipe"]["rank"] = 7
    reject(lambda: bind(word, wrong), "missing native binding")
    wrong = copy.deepcopy(records)
    wrong[-1]["recipe"]["left"]["phase"] ^= 2
    reject(lambda: new_edge_check(wrong), "new-edge exact phase column")
    wrong = copy.deepcopy(word)
    next(e for e in wrong["program"] if e[0] == "add" and e[1] == "C")[3] = "0"
    reject(lambda: logical(wrong), "strict private erasure")
    uses, _ = bind(word, records)
    coarse = {r: ZERO for r in word["initial_frames"]}
    coarse["Y2"] = ((64, 0),) + ZERO[1:]
    reject(lambda: execute(word, uses, coarse), "inexact internal halving")
    return [
        "stale retimed chart",
        "fine pre-add product",
        "nonbijective wrapper",
        "wrong native rank",
        "native global phase",
        "missing private update",
        "six-bit execution",
    ]


def compute():
    word, records = sources()
    uses, binding = bind(word, records)
    rows, scalar = logical(word)
    return {
        "schema_version": 1,
        "status": "PASS",
        "binding": binding,
        "scalar": scalar,
        "new_edge_phase_column_coordinates": new_edge_check(records),
        "fixtures": [fixture(word, uses, rows, dense) for dense in (False, True)],
        "sharp_guards_depths_1_to_64": witness_depths(),
        "controls": controls(word, records),
        "theorem": "g(lambda)=ceil(9*lambda/2)+2 for the exact PR2725 tensor lift",
        "scope": (
            "Changed-source exact precision; native identities inherited; "
            "no supplier or kappa"
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), "exclusive output")
    if args.sources_only:
        sources()
        print("PASS_RETIMED_GRID_SOURCES")
        return
    result = compute()
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    else:
        need(
            encoded(result) == encoded(read(HERE / "RESULT.json")),
            "complete typed receipt",
        )
    print(
        "PASS_P104_RETIMED_INTERNAL_GRID guards=7 transports=1940 "
        "products=30007 erasures=8"
    )


if __name__ == "__main__":
    main()
