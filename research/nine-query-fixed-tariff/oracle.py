#!/usr/bin/env python3
"""Independent forest scan, parity BFS and dirty free-map word oracle.

Credit6059/1340 for the prior nine-point geometry, Nick Petalas6696/5935
for the prior floor/witness and source XOR results, Wentao Li2677/2686/2643,
Arham Tahir1898, ywz65/2455, Ross Richardson943 and retained1370 lineage.
Only the fixed-price corollary is new here. Substantial OpenAI Codex
assistance. Apache-2.0. No predecessor/primary implementation is imported.
"""
import argparse
from collections import Counter, deque
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PIN_SHA = "0d1cbe7daa2cd1092c1a64a3615521b651faf8f83102b7db03896c17a0a09a1a"
CASE_SHA = "fc2c9be60d410124b45da970af462acc749275a35e20a16969527dca5b56f4ea"
SCHEMA_SHA = "0d5089118230203c2f689e2084292997f1c6d07a735f9c3641fc788cb03f99c1"
PAIRS = tuple(itertools.combinations(range(9), 2))
COMMON = {"schema_version", "source_manifest_sha256", "case_manifest_sha256", "floor", "witness"}
FLOOR_KEYS = {"classes", "labeled_walks", "coordinate_labelings", "minimum_R", "histogram", "records_sha256"}
WITNESS_KEYS = {"closed", "Q", "R", "X", "tariff", "invoice"}
INVOICE_KEYS = {"map_leaves", "echo_nodes", "source_XORs", "root_dispatches", "borrowed_dirty_rows", "total"}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    return sha((canonical(value) + "\n").encode())


def unique(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, "duplicate JSON key: " + key)
        result[key] = value
    return result


def bad_number(value):
    raise ValueError("noninteger JSON number forbidden: " + value)


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique, parse_float=bad_number, parse_constant=bad_number)


def authenticate():
    for name, expected in (("SOURCE-PINS.json", PIN_SHA), ("CASES.json", CASE_SHA), ("SCHEMA.json", SCHEMA_SHA)):
        need(sha((ROOT / name).read_bytes()) == expected, "source/case/schema digest changed")
    source = parse((ROOT / "SOURCE-PINS.json").read_bytes())
    need(len(source["files"]) == 4, "four inert source objects required")
    for row in source["files"]:
        raw = (ROOT / row["local_path"]).read_bytes()
        need(len(raw) == row["bytes"] and sha(raw) == row["sha256"], "source bytes changed")
        blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
        need(hashlib.sha1(blob).hexdigest() == row["git_blob"], "source Git blob changed")
    parse((ROOT / "SCHEMA.json").read_bytes())
    return parse((ROOT / "CASES.json").read_bytes())


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    return len(basis)


def graph_increments(code):
    need(type(code) is int and 0 <= code < (1 << 36) and code.bit_count() == 5, "graph code must encode five edges")
    edges = [pair for index, pair in enumerate(PAIRS) if code >> index & 1]
    increments = [0] * 9
    for coordinate, (left, right) in enumerate(edges):
        increments[left] ^= 1 << coordinate
        increments[right] ^= 1 << coordinate
    need(all(increments) and rank(increments) == 5, "incidence graph has isolated position or deficient rank")
    return increments


def all_graph_codes():
    result, candidates = [], 0
    for indices in itertools.combinations(range(36), 5):
        candidates += 1
        need(candidates <= 400000, "combination scan capacity exceeded")
        covered = 0
        for index in indices:
            left, right = PAIRS[index]
            covered |= (1 << left) | (1 << right)
        if covered != 511:
            continue
        code = sum(1 << index for index in indices)
        graph_increments(code)
        result.append(code)
    need(candidates == 376992 and len(result) == len(set(result)), "complete graph-scan domain changed")
    return sorted(result), candidates


def closed_from_code(code):
    closed = [0]
    for increment in graph_increments(code):
        closed.append(closed[-1] ^ increment)
    need(closed[-1] == 0 and len(closed) == 10, "incidence path closure failed")
    return closed


def distances(slots):
    need(type(slots) in (list, tuple) and slots and all(type(v) is int and 0 <= v < 32 for v in slots), "slot labels invalid")
    distance, parents = [-1] * 64, [None] * 64
    distance[0] = 0
    pending = deque([0])
    while pending:
        state = pending.popleft()
        for index, point in enumerate(slots):
            following = state ^ ((point << 1) | 1)
            if distance[following] == -1:
                distance[following] = distance[state] + 1
                parents[following] = state, index
                pending.append(following)
    return distance, parents


def even_minima(slots):
    distance, unused = distances(slots)
    result = [distance[2 * mask] for mask in range(1, 32)]
    need(all(value > 0 and value % 2 == 0 for value in result), "readout coverage/parity failed")
    return result


def record_for_code(code):
    slots = closed_from_code(code)[:-1]
    return [code, slots, even_minima(slots)]


def minimum_readouts(slots):
    distance, parents = distances(slots)
    result = {}
    for mask in range(1, 32):
        state, indices = 2 * mask, []
        need(distance[state] > 0, "readout coverage failed")
        while state:
            state, index = parents[state]
            indices.append(index)
        need(len(indices) == len(set(indices)) and len(indices) % 2 == 0, "shortest parity path repeats a generator")
        result[mask] = sorted(indices)
    return result


def witness_word(closed):
    need(type(closed) is list and len(closed) == 10 and closed[0] == closed[-1] == 0, "nine-query path shape invalid")
    reads, result = minimum_readouts(closed[:-1]), []
    for position in range(9):
        for mask, subset in reads.items():
            if position in subset:
                result.append(["R", mask])
        delta = closed[position] ^ closed[position + 1]
        need(delta != 0, "zero query edge forbidden")
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        result.extend(["X", source, target] for source in donors)
        result.append(["Q", target])
        result.extend(["X", source, target] for source in reversed(donors))
    return result


def typed_word(word):
    need(type(word) is list and len(word) <= 4096, "word size/type invalid")
    for row in word:
        need(type(row) is list and row and type(row[0]) is str, "word instruction shape invalid")
        op = row[0]
        need(op in ("Q", "R", "X") and len(row) == (3 if op == "X" else 2), "word instruction domain invalid")
        need(all(type(value) is int for value in row[1:]), "word arguments must be integers, not bool")
        if op == "R":
            need(1 <= row[1] < 32, "readout mask invalid")
        else:
            need(all(0 <= value < 5 for value in row[1:]), "source port invalid")
            need(op != "X" or row[1] != row[2], "source shear may not alias")


def bind_word(word, closed):
    typed_word(word)
    sources, point, queries = [1 << j for j in range(5)], 0, 0
    reads = {mask: [] for mask in range(1, 32)}
    for row in word:
        if row[0] == "X":
            sources[row[2]] ^= sources[row[1]]
        elif row[0] == "Q":
            need(queries < 9 and point == closed[queries], "query prefix differs from credited path")
            point ^= sources[row[1]]
            queries += 1
            need(point == closed[queries], "query increment differs from credited path")
        else:
            need(queries < 9, "final closing zero is not an extra readout slot")
            reads[row[1]].append(queries)
    need(queries == 9 and point == 0 and sources == [1 << j for j in range(5)], "query/source restoration failed")
    minima = even_minima(closed[:-1])
    for mask, positions in reads.items():
        need(len(positions) == len(set(positions)) and len(positions) == minima[mask - 1] and len(positions) % 2 == 0,
             "readout must use one minimum even subset of the nine slots")
        value = 0
        for position in positions:
            value ^= closed[position]
        need(value == mask, "readout subset XOR differs from demanded mask")


def path_shape(word, closed):
    cursor = 0
    for position in range(9):
        while cursor < len(word) and word[cursor][0] == "R":
            cursor += 1
        delta = closed[position] ^ closed[position + 1]
        need(delta != 0, "zero query edge forbidden")
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        segment = [["X", donor, target] for donor in donors] + [["Q", target]]
        segment += [["X", donor, target] for donor in reversed(donors)]
        need(word[cursor:cursor + len(segment)] == segment, "literal path-local source lowering differs")
        cursor += len(segment)
    need(cursor == len(word), "extra operations after final closing query")


def initial_state():
    roles = ["x" + str(j) for j in range(5)] + ["y" + str(m) for m in range(1, 32)] + ["z", "w0", "w1", "w2"]
    return {role: {(role,)} for role in roles}


def formal_execute(word, initial=None):
    typed_word(word)
    state = initial_state() if initial is None else {role: set(terms) for role, terms in initial.items()}
    for row in word:
        if row[0] == "X":
            source, target, prefix = "x" + str(row[1]), "x" + str(row[2]), ()
        elif row[0] == "Q":
            source, target, prefix = "x" + str(row[1]), "z", ("B",)
        else:
            source, target, prefix = "z", "y" + str(row[1]), ("A" + str(row[1]),)
        state[target].symmetric_difference_update({prefix + term for term in state[source]})
    return state


def formal_check(word):
    expected = initial_state()
    for mask in range(1, 32):
        expected["y" + str(mask)].symmetric_difference_update(
            {("A" + str(mask), "B", "x" + str(j)) for j in range(5) if mask >> j & 1})
    actual = formal_execute(word)
    need(actual == expected, "free noncommuting dirty endpoint differs")
    need(formal_execute(list(reversed(word)), actual) == initial_state(), "literal dirty inverse failed")
    return digest({role: [list(term) for term in sorted(terms)] for role, terms in actual.items()})


def invoice(word):
    typed_word(word)
    counts = Counter(row[0] for row in word)
    leaves, nodes = 28 * counts["Q"] + counts["R"], 9 * counts["Q"]
    total = leaves + nodes + counts["X"] + len(word)
    return {"map_leaves": leaves, "echo_nodes": nodes, "source_XORs": counts["X"],
            "root_dispatches": len(word), "borrowed_dirty_rows": 4, "total": total}


def admit_prices(prices):
    need(type(prices) is dict and set(prices) == {"b", "a", "x"}, "fixed price keys invalid")
    need(all(type(value) is int for value in prices.values()) and prices == {"b": 38, "a": 2, "x": 2}, "only fixed prices38,2,2 are admitted")


def verify_witness(word, closed):
    bind_word(word, closed)
    path_shape(word, closed)
    endpoint = formal_check(word)
    bill = invoice(word)
    counts = Counter(row[0] for row in word)
    need((counts["Q"], counts["R"], counts["X"], bill["total"]) == (9, 70, 2, 486), "credited witness Q/R/X invoice differs")
    return {"closed": closed, "Q": counts["Q"], "R": counts["R"], "X": counts["X"],
            "tariff": bill["total"], "invoice": bill}, endpoint


def validate_record(value):
    need(type(value) is list and len(value) == 3, "forest record shape invalid")
    code, slots, minima = value
    need(type(code) is int, "graph code must be integer, not bool")
    need(type(slots) is list and len(slots) == 9 and slots[0] == 0, "exactly nine slots before closing zero required")
    need(all(type(v) is int and 0 <= v < 32 for v in slots), "slot labels must be five-bit integers")
    need(type(minima) is list and len(minima) == 31 and all(type(v) is int and 2 <= v <= 8 and v % 2 == 0 for v in minima),
         "minimum table requires31 positive even integer entries")
    need(slots == closed_from_code(code)[:-1], "record slots do not bind the incidence graph")


def record_equal(actual, expected):
    validate_record(actual)
    need(actual[0] == expected[0] and actual[1] == expected[1], "actual graph/slot order differs")
    need(actual[2] == expected[2], "actual minimum table differs from independent parity BFS")


def validate_common(value):
    need(type(value) is dict and set(value) == COMMON, "receipt top keys invalid")
    need(type(value["schema_version"]) is int and value["schema_version"] == 1, "receipt version must be integer1")
    need(value["source_manifest_sha256"] == PIN_SHA and value["case_manifest_sha256"] == CASE_SHA, "receipt source/case binding differs")
    floor = value["floor"]
    need(type(floor) is dict and set(floor) == FLOOR_KEYS, "floor profile keys invalid")
    for key in ("classes", "labeled_walks", "coordinate_labelings", "minimum_R"):
        need(type(floor[key]) is int and floor[key] > 0, "floor counts must be positive integers")
    need(type(floor["histogram"]) is list, "floor histogram must be list")
    for row in floor["histogram"]:
        need(type(row) is list and len(row) == 2 and all(type(v) is int and v > 0 for v in row), "histogram must contain positive integer pairs")
    need(floor["histogram"] == sorted(floor["histogram"]) and len({r[0] for r in floor["histogram"]}) == len(floor["histogram"]), "histogram not unique/sorted")
    need(sum(r[1] for r in floor["histogram"]) == floor["classes"], "histogram count differs")
    need(type(floor["records_sha256"]) is str and len(floor["records_sha256"]) == 64
         and all(c in "0123456789abcdef" for c in floor["records_sha256"]), "record digest invalid")
    witness = value["witness"]
    need(type(witness) is dict and set(witness) == WITNESS_KEYS, "witness profile keys invalid")
    need(type(witness["closed"]) is list and len(witness["closed"]) == 10 and all(type(v) is int and 0 <= v < 32 for v in witness["closed"]), "witness path types invalid")
    need(all(type(witness[k]) is int and witness[k] > 0 for k in ("Q", "R", "X", "tariff")), "witness counts invalid")
    bill = witness["invoice"]
    need(type(bill) is dict and set(bill) == INVOICE_KEYS and all(type(v) is int and v > 0 for v in bill.values()), "invoice keys/counts invalid")


def rejected(function, value, phrase):
    try:
        function(value)
    except ValueError as error:
        need(phrase in str(error), "negative control failed at unintended guard: " + str(error))
        return True
    return False


def controls(receipt, record, word, closed):
    version = parse(canonical(receipt)); version["schema_version"] = True
    extra_slot = parse(canonical(record)); extra_slot[1].append(0)
    no_parity = parse(canonical(record)); no_parity[2][0] = 1
    wrong_min = parse(canonical(record)); wrong_min[2][0] = 8 if wrong_min[2][0] != 8 else 6
    omitted_q = list(word); del omitted_q[next(i for i, row in enumerate(word) if row[0] == "Q")]
    omitted_x = list(word); del omitted_x[next(i for i, row in enumerate(word) if row[0] == "X")]
    wrong_r = parse(canonical(word)); r = next(row for row in wrong_r if row[0] == "R"); r[1] = 1 if r[1] != 1 else 2
    final_read = list(word) + [["R", 1]]
    distances_basis, unused = distances([0, 1, 2, 4, 8, 16])
    need(distances_basis[2] == 2 and distances_basis[3] == 1, "missing parity distinction failed")
    result = {"boolean_schema_rejected": rejected(validate_common, version, "version"),
              "duplicate_json_rejected": rejected(parse, '{"x":1,"x":2}', "duplicate"),
              "nonfinite_json_rejected": rejected(parse, '{"x":NaN}', "noninteger"),
              "float_json_rejected": rejected(parse, '{"x":1.0}', "noninteger"),
              "extra_closing_slot_rejected": rejected(validate_record, extra_slot, "nine slots"),
              "missing_parity_rejected": rejected(validate_record, no_parity, "positive even"),
              "wrong_minimum_rejected": rejected(lambda r: record_equal(r, record), wrong_min, "minimum table differs"),
              "wrong_price_rejected": rejected(admit_prices, {"b": 37, "a": 2, "x": 2}, "fixed prices"),
              "alias_source_rejected": rejected(typed_word, [["X", 1, 1]], "alias"),
              "boolean_source_rejected": rejected(typed_word, [["Q", True]], "not bool"),
              "omitted_query_rejected": rejected(lambda w: bind_word(w, closed), omitted_q, "query"),
              "omitted_source_XOR_rejected": rejected(lambda w: bind_word(w, closed), omitted_x, "query"),
              "final_zero_read_rejected": rejected(lambda w: bind_word(w, closed), final_read, "final closing"),
              "dirty_endpoint_rejected": rejected(formal_check, wrong_r, "free noncommuting"),
              "uncovered_slots_rejected": rejected(even_minima, [0] * 9, "coverage")}
    actual = formal_execute(word)
    need(formal_execute(list(reversed(word))[:-1], actual) != initial_state(), "omitted literal inverse control failed")
    result["omitted_literal_inverse_detected"] = True
    need(all(result.values()), "oracle control failed")
    return result


def actual_artifact(path, expected_records, expected_witness, closed):
    with gzip.open(path, "rb") as stream:
        raw = stream.read(8388609)
    need(len(raw) <= 8388608, "actual FLOOR artifact exceeds8MiB")
    value = parse(raw)
    need(type(value) is dict and set(value) == {"schema_version", "records", "witness_word"}, "FLOOR artifact keys invalid")
    need(type(value["schema_version"]) is int and value["schema_version"] == 1, "FLOOR artifact version invalid")
    need(type(value["records"]) is list and len(value["records"]) == len(expected_records), "actual forest record count invalid")
    for actual, expected in zip(value["records"], expected_records):
        record_equal(actual, expected)
    witness, endpoint = verify_witness(value["witness_word"], closed)
    need(witness == expected_witness, "actual credited witness invoice differs")
    return {"actual_records_compared": len(value["records"]), "actual_minimum_entries_compared": 31 * len(value["records"]),
            "actual_artifact_canonical_sha256": digest(value), "actual_word_sha256": digest(value["witness_word"]),
            "free_dirty_endpoint_sha256": endpoint}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", type=Path)
    parser.add_argument("--first-evidence", type=Path)
    parser.add_argument("--check-primary", type=Path)
    args = parser.parse_args()
    need(not (args.emit and args.check_primary), "blind emission cannot read primary data")
    cases = authenticate()
    admit_prices(cases["prices"])
    codes, candidates = all_graph_codes()
    records = [record_for_code(code) for code in codes]
    word = witness_word(cases["closed"])
    if args.first_evidence:
        with args.first_evidence.open("xb") as stream:
            stream.write(gzip.compress((canonical({"schema_version": 1, "records": records, "witness_word": word}) + "\n").encode(), mtime=0))
    histogram = Counter(sum(record[2]) for record in records)
    need(len(records) == 3780 and min(histogram) == 70, "credited X2 floor/control domain differs")
    witness, endpoint = verify_witness(word, cases["closed"])
    floor = {"classes": len(records), "labeled_walks": len(records) * 120, "coordinate_labelings": 120,
             "minimum_R": min(histogram), "histogram": [list(row) for row in sorted(histogram.items())], "records_sha256": digest(records)}
    need(38 * 9 + 2 * 70 + 2 * 2 == 486 and 38 * 9 + 2 * 68 + 2 * 6 == 490, "fixed-price corollary branches fail")
    value = {"schema_version": 1, "source_manifest_sha256": PIN_SHA, "case_manifest_sha256": CASE_SHA, "floor": floor, "witness": witness}
    validate_common(value)
    diagnostic = {"candidate_graphs_scanned": candidates, "controls": controls(value, records[0], word, cases["closed"]),
                  "free_dirty_endpoint_sha256": endpoint, "code_sha256": sha(Path(__file__).read_bytes()),
                  "scope": "Fixed-price corollary only; geometry, X2 floor and witness remain prior"}
    if args.emit:
        with args.emit.open("x") as stream:
            stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")
    else:
        retained = parse((ROOT / "ORACLE.json").read_bytes())
        validate_common(retained)
        need(canonical(retained) == canonical(value), "retained oracle receipt differs")
    if args.check_primary:
        peer = parse(args.check_primary.read_bytes())
        validate_common(peer)
        need(canonical(peer) == canonical(value), "actual complete primary receipt differs")
        diagnostic["actual_primary"] = actual_artifact(args.check_primary.parent / "FLOOR.json.gz", records, witness, cases["closed"])
    print("PASS_NINE_QUERY_FIXED_TARIFF_ORACLE " + canonical(diagnostic))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print("FAIL_NINE_QUERY_FIXED_TARIFF_ORACLE: " + str(error), file=sys.stderr)
        sys.exit(1)
