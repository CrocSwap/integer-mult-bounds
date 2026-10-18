"""Read-only complementary-frame lift of the exact PR2497 logical dual.

The source word and native interpreter authenticate before executable import.
No producer or Clifford compiler is imported by this checker.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
NATIVE = ROOT / "research/p104-native-channel"
SOURCE_SHA = "b699cf37a30d4569e758a45b8dfe1f7998680bcdc92258f6a2f5eb9d48553fe2"
PROFILE = {1: 1216, 2: 74, 3: 86, 4: 104, 5: 48, 6: 42, 7: 76, 8: 8}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_json(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path, compressed=False):
    limit = 2 * 1024 * 1024
    need(path.stat().st_size <= limit, "JSON input capacity")
    if compressed:
        with gzip.open(path, "rb") as stream:
            raw = stream.read(limit + 1)
    else:
        raw = path.read_bytes()
    need(len(raw) <= limit, "JSON payload capacity")
    return json.loads(raw)


def authenticate():
    manifest = read_json(HERE / "SOURCES.json")
    for record in manifest["files"]:
        if record["usage"] == "input":
            path = ROOT / record["path"]
            need(path.stat().st_size <= 2 * 1024 * 1024, "external source capacity")
            need(digest(path.read_bytes()) == record["sha256"],
                 "external source drift: " + record["path"])
    path = HERE / "inputs/CLEAN-DUAL.json"
    need(path.stat().st_size == 233964, "PR2497 source size")
    raw = path.read_bytes()
    need(digest(raw) == SOURCE_SHA, "PR2497 source word drift")
    need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
         == "1311d5bbfd111b7c2de1f9b4d1807673c47a3f58", "PR2497 Git blob")
    return json.loads(raw)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "Python module loader")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=4096)
def span(basis):
    need(len(basis) <= 9 and all(type(v) is int and 0 < v < 512 for v in basis),
         "binary frame bounds")
    values = {0}
    for vector in basis:
        values |= {v ^ vector for v in tuple(values)}
    return frozenset(values)


@lru_cache(maxsize=4096)
def basis(values):
    rows = []
    covered = {0}
    for vector in sorted(values):
        if vector not in covered:
            rows.append(vector)
            covered |= {v ^ vector for v in tuple(covered)}
    need(len(rows) <= 9 and frozenset(covered) == frozenset(values), "subspace basis")
    return tuple(rows)


@lru_cache(maxsize=4096)
def orthogonal(frame):
    vectors = tuple(v for v in range(512)
                    if all((v & b).bit_count() % 2 == 0 for b in frame))
    result = basis(vectors)
    need(len(result) + len(frame) == 9, "orthogonal dimension")
    return result


def roots():
    result = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            result.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            result.add((1, *signs))
    need(len(result) == 120, "E8 root lines")
    return sorted(result)


def geometry(interpreter):
    packet = read_json(NATIVE / "NATIVE-RECIPES.json.gz", compressed=True)
    iso = packet["label_isometry"]
    rr = roots()
    gram = [[sum(a*b for a, b in zip(x, y)) // 4 for y in rr] for x in rr]
    pivots = iso["pivot_root_indices"]
    compressed = [sum(((row[j] + 1) % 2) << k for k, j in enumerate(pivots))
                  for row in gram]
    need([compressed[i] for i in pivots] == iso["compressed_gram"], "compressed Gram")
    dual = interpreter.inverse(tuple(iso["compressed_gram"]))
    need(list(dual) == iso["compressed_dual_gram"], "compressed inverse Gram")
    orth = iso["orthonormal_basis_compressed"]
    def convert(value):
        images = [interpreter.mul(dual, b) for b in orth]
        return sum(((value & b).bit_count() % 2) << j for j, b in enumerate(images))
    labels = [convert(v) for v in compressed]
    need(labels == iso["physical_root_labels"], "physical root labels")
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            need((a & b).bit_count() % 2 == (gram[i][j] + 1) % 2, "physical pairings")
    fixture = read_json(NATIVE / "inputs/P104-FIXTURE.json")
    removed = {tuple(v) for v in fixture["section4_explicit_P104"]["F0"]
               + fixture["section4_explicit_P104"]["C"]}
    indices = [i for i, row in enumerate(rr) if row not in removed]
    need(len(indices) == 104, "P104 ports")
    return convert, [rr[i] for i in indices], [labels[i] for i in indices]


def lift(source, convert):
    need(source["schema_version"] == 1 and len(source["program"]) == 4982,
         "frozen source schema and event count")
    def frame(vectors):
        physical = basis(span(tuple(convert(v) for v in vectors)))
        need(len(physical) == len(vectors), "independent source frame")
        result = orthogonal(physical)
        need(span(orthogonal(result)) == span(physical), "complement involution")
        return list(result)
    result = {"schema_version": 1,
              "initial_frames": {r: frame(f) for r, f in source["initial_frames"].items()},
              "final_frames": {r: frame(f) for r, f in source["final_frames"].items()},
              "program": []}
    for event in source["program"]:
        row = copy.deepcopy(event)
        if row[0] == "transport":
            row[2], row[3] = frame(event[2]), frame(event[3])
        else:
            need(row[0] in ("add", "sign", "zero", "erase"), "source event alphabet")
            row[-1] = frame(event[-1])
        result["program"].append(row)
    return result


def add_row(destination, source, coefficient):
    for key, value in source.items():
        total = destination.get(key, Fraction(0)) + coefficient * value
        if total:
            destination[key] = total
        else:
            destination.pop(key, None)


def scalar_step(event, frames, rows):
    op, reg = event[:2]
    if op == "zero":
        need(reg == "C" and reg not in rows, "owned zero initialization")
        frames[reg], rows[reg] = span(tuple(event[2])), {}
    elif op == "erase":
        need(reg == "C" and reg in rows and not rows[reg], "nonzero private erase")
        need(frames[reg] == span(tuple(event[2])), "private erase frame")
        del rows[reg], frames[reg]
    elif op == "sign":
        need(reg.startswith("X") and event[2] == "-1", "source sign")
        need(frames[reg] == span(tuple(event[3])), "sign frame")
        rows[reg] = {k: -v for k, v in rows[reg].items()}
    else:
        need(op == "add", "scalar event alphabet")
        src, coeff = event[2], Fraction(event[3])
        need(reg != src and frames[reg] == frames[src] == span(tuple(event[4])),
             "scalar common frame")
        add_row(rows[reg], rows[src], coeff)


def replay(word, ports):
    initial, final = word["initial_frames"], word["final_frames"]
    need(len(initial) == len(final) == 358 and set(initial) == set(final), "358 persistent inputs")
    frames = {r: span(tuple(f)) for r, f in initial.items()}
    rows = {r: {r: Fraction(1)} for r in initial}
    counts, profile = Counter(), Counter()
    for event in word["program"]:
        op, reg = event[:2]
        counts[op] += 1
        if op == "transport":
            old, new, rank = tuple(event[2]), tuple(event[3]), event[4]
            a, b = span(old), span(new)
            need(frames[reg] == a and len(a) == 1 << len(old), "transport entry")
            need(len(b) == 1 << len(new) and (a <= b or b <= a), "nested transport")
            need(abs(len(old) - len(new)) == rank > 0, "transport paid rank")
            need(reg == "C" or a < b, "persistent nonmonotone transport")
            frames[reg] = b
            profile[rank] += 1
        else:
            scalar_step(event, frames, rows)
    need(set(rows) == set(initial) and frames == {r: span(tuple(f)) for r, f in final.items()},
         "persistent endpoint frames and closed private storage")
    for reg in initial:
        expected = {reg: Fraction(1)}
        if reg.startswith("X"):
            source = int(reg[1:])
            for target in range(104):
                value = Fraction(int(target == source)) if target < 2 else Fraction(
                    sum(a*b for a, b in zip(ports[target], ports[source])), 8)
                if value:
                    expected["Y" + str(target)] = -value
        need(rows[reg] == expected, "logical inverse-transpose endpoint " + reg)
    need(dict(profile) == PROFILE and counts["erase"] == counts["zero"] == 8, "complete invoice")
    return {"events": dict(sorted(counts.items())), "paid_profile": {str(k): v for k, v in sorted(profile.items())},
            "rank_mass": sum(k*v for k, v in profile.items()), "endpoint_coefficients": 358**2,
            "logical_rows_sha256": digest(canonical_json(
                {r: {k: str(v) for k, v in row.items()} for r, row in rows.items()}))}


def native_edges(word):
    edges = {}
    for index, event in enumerate(word["program"]):
        if event[0] == "transport":
            key = (tuple(event[2]), tuple(event[3]))
            edges.setdefault(key, []).append(index)
    return edges


def native_check(word, packet, interpreter, labels):
    edges = native_edges(word)
    records = packet["transports"]
    need(len(records) == len(edges), "native edge count")
    covered = set()
    for record in records:
        a, b = tuple(record["old"]), tuple(record["new"])
        need((a, b) in edges and (a, b) not in covered, "unique native edge")
        covered.add((a, b))
        need(record["events"] == edges[a, b], "all native occurrences")
        need(record["recipe"]["rank"] == abs(len(a)-len(b)), "native positive rank")
        interpreter.equal(interpreter.recipe(record["recipe"]),
                          interpreter.adjoint(interpreter.frame(a, 9)) + interpreter.frame(b, 9),
                          "complemented native operator and global phase")
    need(covered == set(edges), "complete native transport coverage")
    adapters = packet["endpoint_adapters"]
    need(len(adapters) == 208, "208 intrinsic endpoints")
    seen = set()
    for record in adapters:
        position, reg = record["position"], record["register"]
        need((position, reg) not in seen, "unique endpoint")
        seen.add((position, reg))
        normal = labels[int(reg[1:])]
        if position == "entry":
            need(reg.startswith("Y"), "dual input role")
            frame = tuple(word["initial_frames"][reg])
            need(frame == (normal,), "dual input root line")
            expected = interpreter.adjoint((("C", normal, 1),)) + interpreter.frame(frame, 9)
        else:
            need(position == "exit" and reg.startswith("X"), "dual output role")
            frame = tuple(word["final_frames"][reg])
            need(span(frame) == span(orthogonal((normal,))), "dual output root hyperplane")
            expected = interpreter.adjoint(interpreter.frame(frame, 9)) + (
                ("C", normal, -1),) + interpreter.fourier(9)
        need(record["frame"] == list(frame) and record["normal"] == normal, "endpoint binding")
        need(record["recipe"]["rank"] == 0, "rank-zero intrinsic endpoint")
        interpreter.equal(interpreter.recipe(record["recipe"]), expected, "intrinsic phase")
    need(seen == {("entry", "Y"+str(i)) for i in range(104)}
         | {("exit", "X"+str(i)) for i in range(104)}, "all endpoint roles")
    return {"distinct_transports": len(edges), "transport_occurrences": sum(map(len, edges.values())),
            "rank_zero_endpoints": len(adapters)}


def rejects(call, message):
    try:
        call()
    except ValueError as error:
        need(message in str(error), "wrong rejection: " + str(error))
    else:
        raise ValueError("accepted fault: " + message)


def controls(word, packet, interpreter, ports, labels):
    bad = copy.deepcopy(word)
    index = next(i for i, e in enumerate(bad["program"])
                 if e[0] == "transport" and e[1] != "C" and e[2])
    event = bad["program"][index]
    event[3], event[4] = [], len(event[2])
    rejects(lambda: replay(bad, ports), "persistent nonmonotone")
    bad = copy.deepcopy(word)
    index = max(i for i, e in enumerate(bad["program"]) if e[0] == "add" and e[1] == "C")
    bad["program"][index][3] = "0"
    rejects(lambda: replay(bad, ports), "nonzero private erase")
    bad = copy.deepcopy(word)
    bad["program"].pop(0)
    rejects(lambda: replay(bad, ports), "logical inverse-transpose endpoint")
    bad = copy.deepcopy(packet)
    rec = bad["transports"][0]["recipe"]["left"]
    rec["phase"] = (rec["phase"] + 1) % 4
    rejects(lambda: native_check(word, bad, interpreter, labels), "global phase")
    bad = copy.deepcopy(packet)
    bad["transports"][0]["recipe"]["rank"] += 1
    rejects(lambda: native_check(word, bad, interpreter, labels), "positive rank")
    bad = copy.deepcopy(packet)
    bad["endpoint_adapters"][0]["normal"] ^= 1
    rejects(lambda: native_check(word, bad, interpreter, labels), "endpoint binding")
    return ["persistent_descent", "nonzero_private_erase", "missing_sign", "native_global_phase",
            "native_rank", "endpoint_normal"]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    source = authenticate()
    interpreter = load_module(NATIVE / "vendor/native_verify.py", "complement_native_oracle")
    convert, ports, labels = geometry(interpreter)
    word = lift(source, convert)
    packet = read_json(HERE / "NATIVE.json.gz", compressed=True)
    need(packet["word_sha256"] == digest(canonical_json(word)), "complete lifted word digest")
    result = replay(word, ports)
    result.update(native_check(word, packet, interpreter, labels))
    result["controls"] = controls(word, packet, interpreter, ports, labels)
    result.update(status="PASS_P104_COMPLEMENTARY_DUAL", source_sha256=SOURCE_SHA,
                  complemented_word_sha256=digest(canonical_json(word)),
                  native_payload_sha256=digest(canonical_json(packet)),
                  persistent_monotone_paths=358, restored_private_collectors=8,
                  scope="Finite complementary-chart logical inverse-transpose; no physical F^-T, "
                        "physical private storage admission, hosted supplier or new kappa.")
    if args.out:
        payload = json.dumps(result, sort_keys=True, indent=2) + "\n"
        with args.out.open("x") as stream:
            need(stream.write(payload) == len(payload), "complete receipt write")
    else:
        need(result == read_json(HERE / "RESULT.json"), "complete receipt mismatch")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
