#!/usr/bin/env python3
"""Independently check the finite certificate; no generator imports."""
import argparse
from collections import Counter
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = "91a2094f2e022930069e8cfdc810a3ea1b81cd09"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def expected_map(n, rows, operators=None, extra=()):
    roles = [f"x{j}" for j in range(n)] + [f"y{i}" for i in range(len(rows))] + ["z"] + list(extra)
    state = {role: {(role,)} for role in roles}
    for i, mask in enumerate(rows):
        for j in range(n):
            if mask >> j & 1:
                a, b = f"A{i}", f"B{j}"
                factors = (a, b) if operators is None else tuple(operators[a][::-1] + operators[b][::-1])
                state[f"y{i}"].symmetric_difference_update({factors + (f"x{j}",)})
    return state


def interpret(operations, state, allowed):
    state = {role: set(poly) for role, poly in state.items()}
    for coefficient, source, target in operations:
        need(coefficient in allowed, "unknown operator")
        need(source in state and target in state and source != target, "invalid/aliased port")
        state[target].symmetric_difference_update({(coefficient,) + term for term in state[source]})
    return state


def root_operations(item):
    n, rows = item["sources"], item["rows"]
    need(type(n) is int and 1 <= n <= 5, "invalid source dimension")
    need(all(type(r) is int and 0 < r < (1 << n) for r in rows), "invalid row mask")
    result = []
    for op in item["word"]:
        need(type(op) is list and len(op) == 2, "invalid query record")
        kind, index = op
        need(kind in ("A", "B") and type(index) is int, "invalid query type")
        need(0 <= index < (n if kind == "B" else len(rows)), "invalid query index")
        source, target = (f"x{index}", "z") if kind == "B" else ("z", f"y{index}")
        result.append((f"{kind}{index}", source, target))
    return result


def check_schedule(item):
    ops = root_operations(item)
    target = expected_map(item["sources"], item["rows"])
    initial = {role: {(role,)} for role in target}
    allowed = {f"B{j}" for j in range(item["sources"])} | {f"A{i}" for i in range(len(item["rows"]))}
    out = interpret(ops, initial, allowed)
    need(out == target, "root free-algebra identity or restoration failed")
    need(interpret(ops[::-1], out, allowed) == initial, "root inverse failed")
    need(item["queries"] == len(ops), "unpaid root call")
    actual_source = [i for kind, i in item["word"] if kind == "B"]
    need(actual_source == item["source_word"], "source projection mismatch")
    slots, slot = [[] for _ in item["rows"]], 0
    for kind, i in item["word"]:
        if kind == "B":
            slot += 1
        else:
            slots[i].append(slot)
    need(slots == item["readout_slots"], "readout metadata mismatch")
    return Counter(op[0] for op in ops)


def balanced_price(n):
    k = n.bit_length() - 1
    return (1 << k) * (3 * n - (1 << (k + 1)))


def check_lowering(lowered, item):
    lengths = lowered["factor_lengths"]
    need(lengths == {"B": [1, 2, 3, 4, 5], "A": [1] * 31}, "changed lowering fixture")
    factors = {f"{k}{i}": [f"{k}{i}.{j}" for j in range(n)] for k in ("B", "A") for i, n in enumerate(lengths[k])}
    need(lowered["factors"] == factors, "factor identity/order metadata")
    prices = {f"{k}{i}": balanced_price(n) for k in ("B", "A") for i, n in enumerate(lengths[k])}
    need(lowered["query_leaf_prices"] == prices, "unpaid recursive child")
    counts = Counter(f"{k}{i}" for k, i in item["word"])
    paid = sum(counts[name] * price for name, price in prices.items())
    ops = lowered["leaf_word"]
    need(len(ops) == paid == lowered["leaf_calls"], "leaf count mismatch")
    need(lowered["borrowed_dirty_arrays"] == 4, "underpriced workspace")
    scratch = [f"scratch{k}" for k in range(3)]
    target = expected_map(5, item["rows"], factors, scratch)
    initial = {role: {(role,)} for role in target}
    allowed = {f for fs in factors.values() for f in fs}
    actual = interpret(ops, initial, allowed)
    need(actual == target, "lowered map, factor order or dirty restoration failed")
    need(interpret(ops[::-1], actual, allowed) == initial, "lowered inverse failed")
    used = {r for _, s, t in ops for r in (s, t) if r.startswith("scratch")}
    need(used == set(scratch), "scratch inventory mismatch")
    return paid


def check_sources():
    sources = json.loads((ROOT / "SOURCES.json").read_text())
    need(sources["base"] == BASE, "base pin mismatch")
    for entry in sources["references"]:
        content = (ROOT / entry["local_path"]).read_bytes()
        need(sha256(content).hexdigest() == entry["sha256"], "reference SHA256 mismatch")
        blob = sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        need(blob == entry["git_blob"], "reference Git blob mismatch")
    # Optional workspace context is checked when present; relocation is standalone.
    repo = ROOT.parent.parent
    count = 0
    for path, digest in sources["context"].items():
        if (repo / path).is_file():
            need(sha256((repo / path).read_bytes()).hexdigest() == digest, "base context drift: " + path)
            count += 1
    return len(sources["references"]), count


def check_star_comparators(rows):
    """Build both ordinary restored star comparators without generator code."""
    columns, rowwise = [], []
    for j in range(5):
        readers = [["A", i] for i, row in enumerate(rows) if row >> j & 1]
        columns += [["B", j]] + readers + [["B", j]] + readers
    for i, row in enumerate(rows):
        toggles = [["B", j] for j in range(5) if row >> j & 1]
        rowwise += toggles + [["A", i]] + toggles[::-1] + [["A", i]]
    result = {}
    for name, word in (("column_stars", columns), ("row_stars", rowwise)):
        ops = root_operations({"sources": 5, "rows": rows, "word": word})
        target = expected_map(5, rows)
        initial = {role: {(role,)} for role in target}
        allowed = {op[0] for op in ops}
        need(interpret(ops, initial, allowed) == target, "invalid star comparator")
        need(interpret(ops[::-1], target, allowed) == initial, "star inverse")
        paid = sum(balanced_price(int(name[1:]) + 1) if name.startswith("B") else 1 for name, _, _ in ops)
        result[name] = {"queries": len(ops), "leaf_calls": paid}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-summary", action="store_true")
    args = parser.parse_args()
    cert = json.loads((ROOT / "CERTIFICATE.json").read_text())
    need(cert["schema"] == "universal-connector-boundary-v1" and cert["base"] == BASE and cert["assignment_seed"] == 52, "certificate header")
    independent = module("independent")
    need([c["sources"] for c in cert["censuses"]] == [4, 5], "missing census")
    census_summary = []
    for reported in cert["censuses"]:
        n = reported["sources"]
        entries = sorted((list(word), mask) for word, mask in independent.pairing_covers(n))
        need(len(entries) == len({tuple(w) for w, _ in entries}), "duplicate matching")
        hist = Counter(mask.bit_count() for _, mask in entries)
        digest = sha256(json.dumps(entries, separators=(",", ":")).encode()).hexdigest()
        need(reported == {"sources": n, "pairings": len(entries), "histogram": dict(sorted((str(k), v) for k, v in hist.items())), "canonical_entries_sha256": digest, "max_coverage": max(hist)}, "independent census mismatch")
        need(len(entries) == (105 if n == 4 else 945), "domain incomplete")
        need(max(hist) == (16 if n == 4 else 31), "boundary failed")
        census_summary.append({"sources": n, "pairings": len(entries), "max_coverage": max(hist)})
    schedules = cert["schedules"]
    need(set(schedules) == {"four_all", "five_extra_source", "five_extra_output"}, "schedule coverage")
    queries = {}
    for name, item in schedules.items():
        need(item["rows"] == list(range(1, 1 << item["sources"])), "all nonzero rows missing")
        counts = check_schedule(item)
        need(all(c % 2 == 0 for c in counts.values()), "odd oracle multiplicity")
        need(item["queries"] == (38 if name == "four_all" else 74), "unit optimality witness")
        queries[name] = item["queries"]
    # Check full universality directly, not only counts in a receipt.
    for name in ("four_all", "five_extra_source"):
        need(all(len(s) == 2 for s in schedules[name]["readout_slots"]), "not paired readouts")
    needs_four = [r for r, slots in zip(schedules["five_extra_output"]["rows"], schedules["five_extra_output"]["readout_slots"]) if len(slots) == 4]
    need(needs_four == [21], "wrong missing-row repair")
    lowered = {name: check_lowering(data, schedules[name]) for name, data in cert["lowered"].items()}
    need(lowered == {"five_extra_source": 200, "five_extra_output": 182}, "lowering coverage")
    rows = schedules["five_extra_output"]["rows"]
    column_stars = 2 * sum(1 + sum(bool(r >> j & 1) for r in rows) for j in range(5))
    row_stars = 2 * sum(1 + r.bit_count() for r in rows)
    need(cert["five_source_comparators"] == {"column_stars": column_stars, "row_stars": row_stars}, "star pricing")
    star_comparators = check_star_comparators(rows)
    need(star_comparators == {"column_stars": {"queries": 170, "leaf_calls": 278}, "row_stars": {"queries": 222, "leaf_calls": 1950}}, "star leaf pricing")
    controls = []

    def reject(name, action):
        try:
            action()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("negative control accepted: " + name)

    def mutated(item):
        return json.loads(json.dumps(item))

    bad = mutated(schedules["five_extra_source"])
    del bad["word"][-1]
    reject("omitted_final_source", lambda: check_schedule(bad))
    bad = mutated(schedules["five_extra_source"])
    index = next(k for k in range(len(bad["word"]) - 1) if bad["word"][k][0] != bad["word"][k + 1][0])
    bad["word"][index], bad["word"][index + 1] = bad["word"][index + 1], bad["word"][index]
    reject("readout_crosses_source_toggle", lambda: check_schedule(bad))
    bad = mutated(schedules["five_extra_output"])
    index = next(k for k, op in enumerate(bad["word"]) if op == ["A", 20])
    del bad["word"][index:index + 1]
    reject("unpaid_missing_row_readout", lambda: check_schedule(bad))
    bad = mutated(schedules["five_extra_source"])
    bad["rows"][0] ^= 2
    reject("wrong_target_pattern", lambda: check_schedule(bad))
    bad = mutated(cert["lowered"]["five_extra_output"])
    bad["borrowed_dirty_arrays"] = 3
    reject("underpriced_scratch", lambda: check_lowering(bad, schedules["five_extra_output"]))
    bad = mutated(cert["lowered"]["five_extra_output"])
    bad["query_leaf_prices"]["B4"] -= 1
    reject("unpaid_recursive_child", lambda: check_lowering(bad, schedules["five_extra_output"]))
    bad = mutated(cert["lowered"]["five_extra_output"])
    bad["leaf_word"][0][2] = bad["leaf_word"][0][1]
    reject("aliased_child_ports", lambda: check_lowering(bad, schedules["five_extra_output"]))
    bad = mutated(cert["lowered"]["five_extra_output"])
    # Reverse only one nontrivial operator's coefficient order; count unchanged.
    for op in bad["leaf_word"]:
        if op[0].startswith("B1."):
            op[0] = "B1." + str(1 - int(op[0].split(".")[1]))
    reject("wrong_factor_order", lambda: check_lowering(bad, schedules["five_extra_output"]))
    dense = module("dense_checks").check_dense(cert)
    refs, _ = check_sources()
    summary = {"censuses": census_summary, "queries": queries, "leaf_calls": lowered,
               "root_controls": controls, "dense": dense, "pinned_reference_files": refs,
               "scalar_leaf_baseline": 2 * (sum(balanced_price(n) for n in range(1, 6)) + 31),
               "unit_lower_bound": 74, "star_comparators": star_comparators}
    target = ROOT / "EXPECTED.json"
    if args.write_summary:
        target.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    else:
        need(json.loads(target.read_text()) == summary, "expected evidence differs")
    print("PASS_UNIVERSAL_CONNECTOR_BOUNDARY pairings=945 max_coverage=31 queries=74 leaves=182")


if __name__ == "__main__":
    main()
