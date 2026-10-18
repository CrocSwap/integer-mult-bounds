"""Native binding of PR2521's cross-group P104 word. No compiler/producer imports.

Adapted from ywz65 / PR2572 (fe4446d0); geometry and native-check pattern
adapt Nick Petalas / PR2550. New binding and controls: commdata2338 with
substantial OpenAI Codex assistance. Apache-2.0.
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
SOURCE_HEAD = "78e7e4c1032a3f2bce8dae4f3f2bf30ac924b050"
ADDED_PROFILE = {1: 146, 2: 36, 3: 7, 4: 1, 5: 8, 6: 40, 7: 41}
REQUIRED_INPUTS = {
    "research/p104-native-channel/inputs/LOWRANK-WITNESS.json",
    "research/p104-native-channel/inputs/P104-FIXTURE.json",
    "research/p104-native-channel/NATIVE-RECIPES.json.gz",
    "research/p104-native-channel/vendor/native_verify.py",
    "research/p104-native-channel/vendor/clifford_exact.py",
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path, compressed=False):
    limit = 3_000_000
    need(path.stat().st_size <= limit, "input capacity")
    if compressed:
        with gzip.open(path, "rb") as stream:
            raw = stream.read(limit + 1)
    else:
        raw = path.read_bytes()
    need(len(raw) <= limit, "payload capacity")
    return json.loads(raw)


def authenticate():
    manifest = load(HERE / "SOURCES.json")
    declared = [r["path"] for r in manifest["files"] if r["usage"] == "input"]
    need(len(declared) == len(set(declared)) and set(declared) == REQUIRED_INPUTS, "required external source set")
    need([r["path"] for r in manifest["vendored_inputs"]] == ["inputs/PR2521-CIRCUIT.json"], "required retained source set")
    for record in manifest["files"]:
        if record["usage"] == "input":
            raw = (ROOT / record["path"]).read_bytes()
            need(digest(raw) == record["sha256"], "external source drift: " + record["path"])
    for record in manifest["vendored_inputs"]:
        raw = (HERE / record["path"]).read_bytes()
        need(digest(raw) == record["sha256"], "retained source drift: " + record["path"])
        need(hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
             == record["git_blob"], "retained source Git blob")
    return load(NATIVE / "inputs/LOWRANK-WITNESS.json"), load(HERE / "inputs/PR2521-CIRCUIT.json")


def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    need(spec is not None and spec.loader is not None, "module loader")
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


@lru_cache(maxsize=4096)
def span(vectors):
    need(len(vectors) <= 9 and all(type(v) is int and 0 < v < 512 for v in vectors), "frame bounds")
    result = {0}
    for vector in vectors:
        result |= {x ^ vector for x in tuple(result)}
    need(len(result) == 1 << len(vectors), "independent frame basis")
    return frozenset(result)


def basis(vectors):
    covered, rows = {0}, []
    for vector in sorted(vectors):
        if vector not in covered:
            rows.append(vector)
            covered |= {x ^ vector for x in tuple(covered)}
    return tuple(rows)


def geometry(oracle):
    # Compressed coordinates are not ordinary binary physical coordinates.
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[i], row[j] = 2, 2 * sign
            roots.add(tuple(row))
    for signs in product((-1, 1), repeat=7):
        if signs.count(-1) % 2 == 0:
            roots.add((1, *signs))
    roots = sorted(roots)
    need(len(roots) == 120, "E8 root lines")
    gram = [[sum(a*b for a, b in zip(x, y)) // 4 for y in roots] for x in roots]
    iso = load(NATIVE / "NATIVE-RECIPES.json.gz", True)["label_isometry"]
    pivots = iso["pivot_root_indices"]
    need(len(pivots) == len(set(pivots)) == 9, "nine coordinate pivots")
    compressed = [sum(((row[j] + 1) % 2) << k for k, j in enumerate(pivots)) for row in gram]
    need([compressed[i] for i in pivots] == iso["compressed_gram"], "compressed Gram")
    dual = oracle.inverse(tuple(iso["compressed_gram"]))
    need(list(dual) == iso["compressed_dual_gram"], "inverse Gram")
    orth = iso["orthonormal_basis_compressed"]
    def convert(value):
        return sum(((value & oracle.mul(dual, b)).bit_count() % 2) << j for j, b in enumerate(orth))
    labels = [convert(v) for v in compressed]
    need(labels == iso["physical_root_labels"] and len(set(labels)) == 120, "physical label map")
    for i, a in enumerate(labels):
        for j, b in enumerate(labels):
            need((a & b).bit_count() % 2 == (gram[i][j] + 1) % 2, "physical pairings")
    fixture = load(NATIVE / "inputs/P104-FIXTURE.json")["section4_explicit_P104"]
    removed = {tuple(v) for v in fixture["F0"] + fixture["C"]}
    indices = [i for i, row in enumerate(roots) if row not in removed]
    need(len(indices) == 104, "104 ports")
    return convert, [roots[i] for i in indices], [labels[i] for i in indices]


def assemble(original, correction, convert):
    need(type(correction["schema_version"]) is int and correction["schema_version"] == 1, "source schema")
    need(correction["targets"] == [0, 1, 2], "three corrected targets")
    need(len(original["program"]) == 4058 and len(correction["initial_frames"]) == 90, "source sizes")
    cuts = [p["completed_cut"] for p in correction["insertions"]]
    need(cuts == sorted(set(cuts)) and all(type(c) is int and 0 <= c <= 4058 for c in cuts), "ordered cuts")
    inserts = {p["completed_cut"]: p["events"] for p in correction["insertions"]}
    def frame(f):
        return list(basis(span(tuple(convert(v) for v in f))))
    result = {"initial_frames": {}, "final_frames": {}, "program": [], "added_indices": []}
    for boundary in ("initial_frames", "final_frames"):
        need(not set(original[boundary]) & set(correction[boundary]), "disjoint helper identities")
        result[boundary] = {r: frame(f) for source in (original, correction) for r, f in source[boundary].items()}
    for cut in range(4059):
        events = [(e, True) for e in inserts.get(cut, [])]
        if cut < 4058:
            events.append((original["program"][cut], False))
        for event, added in events:
            row = copy.deepcopy(event)
            if row[0] == "transport":
                row[2], row[3] = frame(row[2]), frame(row[3])
            else:
                need(row[0] in ("add", "copy", "zero", "erase"), "source alphabet")
                row[-1] = frame(row[-1])
            if added:
                result["added_indices"].append(len(result["program"]))
            result["program"].append(row)
    need(len(result["program"]) == 4854 and len(result["initial_frames"]) == 370, "complete source sizes")
    return result


def replay(word, ports):
    initial, final = word["initial_frames"], word["final_frames"]
    need(len(initial) == len(final) == 370 and set(initial) == set(final), "370 persistent inputs")
    frames = {r: span(tuple(f)) for r, f in initial.items()}
    rows = {r: {r: Fraction(1)} for r in initial}
    counts, profile, added = Counter(), Counter(), Counter()
    added_indices = set(word["added_indices"])
    copied, erased = [], []
    for index, event in enumerate(word["program"]):
        op, reg = event[:2]
        counts[op] += 1
        if op == "transport":
            old, new, rank = tuple(event[2]), tuple(event[3]), event[4]
            a, b = span(old), span(new)
            need(reg in frames and frames[reg] == a, "transport entry")
            need(a < b or b < a, "nested transport")
            need(type(rank) is int and abs(len(old)-len(new)) == rank > 0, "paid rank")
            need(reg == "C" or a < b, "persistent descent")
            frames[reg] = b
            profile[rank] += 1
            if index in added_indices:
                added[rank] += 1
        elif op == "zero":
            need(reg == "C" and reg not in rows, "owned initialization")
            rows[reg], frames[reg] = {}, span(tuple(event[2]))
        elif op == "erase":
            need(reg == "C" and reg in rows and frames[reg] == span(tuple(event[2])), "owned disposal")
            # Original private copies can be nonzero; no stronger disposal claim.
            erased.append({k: str(v) for k, v in rows[reg].items()})
            del rows[reg], frames[reg]
        elif op in ("add", "copy"):
            src = event[2]
            need(reg != src and frames[reg] == frames[src] == span(tuple(event[-1])), "scalar common frame")
            if op == "copy":
                need(reg == "C" and not rows[reg], "owned zero COPY")
                rows[reg] = dict(rows[src])
                copied.append(src)
            else:
                coefficient = Fraction(event[3])
                for k, value in rows[src].items():
                    total = rows[reg].get(k, Fraction(0)) + coefficient*value
                    if total:
                        rows[reg][k] = total
                    else:
                        rows[reg].pop(k, None)
        else:
            raise ValueError("event alphabet")
    need(set(rows) == set(initial) and frames == {r: span(tuple(f)) for r, f in final.items()}, "closed endpoints")
    for reg in initial:
        expected = {reg: Fraction(1)}
        if reg.startswith("Y"):
            t = int(reg[1:])
            for s in range(104):
                value = Fraction(int(t == s)) if t < 3 else Fraction(sum(a*b for a, b in zip(ports[t], ports[s])), 8)
                if value:
                    expected["X" + str(s)] = value
        need(rows[reg] == expected, "arbitrary-input endpoint " + reg)
    need(dict(added) == ADDED_PROFILE, "added transport invoice")
    need(counts["erase"] == counts["zero"] == counts["copy"] == 8, "inherited private lifecycle")
    return {"events": dict(sorted(counts.items())), "paid_profile": dict(sorted(profile.items())),
            "rank_mass": sum(k*v for k, v in profile.items()), "added_profile": dict(sorted(added.items())),
            "added_rank_mass": sum(k*v for k, v in added.items()), "endpoint_coefficients": 370**2,
            "copied_from": copied, "erased_rows_sha256": digest(canonical(erased)),
            "nonzero_owned_disposals": sum(bool(r) for r in erased),
            "logical_rows_sha256": digest(canonical({r: {k: str(v) for k, v in row.items()} for r, row in rows.items()}))}


def native_edges(word):
    edges = {}
    for index, event in enumerate(word["program"]):
        if event[0] == "transport":
            edges.setdefault((tuple(event[2]), tuple(event[3])), []).append(index)
    return edges


def native_check(word, packet, oracle, labels):
    edges, seen = native_edges(word), set()
    need(len(packet["transports"]) == len(edges), "native edge count")
    for record in packet["transports"]:
        a, b = tuple(record["old"]), tuple(record["new"])
        need((a, b) in edges and (a, b) not in seen, "unique native edge")
        seen.add((a, b))
        need(record["events"] == edges[a, b], "native event coverage")
        need(type(record["recipe"]["rank"]) is int and record["recipe"]["rank"] == abs(len(a)-len(b)), "native rank")
        oracle.equal(oracle.recipe(record["recipe"]), oracle.adjoint(oracle.frame(a, 9)) + oracle.frame(b, 9), "native global phase/operator")
    need(seen == set(edges), "complete native edges")
    seen = set()
    for record in packet["endpoint_adapters"]:
        position, reg = record["position"], record["register"]
        need((position, reg) not in seen, "unique endpoint")
        seen.add((position, reg))
        normal = labels[int(reg[1:])]
        if position == "entry":
            need(reg.startswith("X"), "entry role")
            frame = tuple(word["initial_frames"][reg])
            need(frame == (normal,), "root line")
            expected = oracle.adjoint((("C", normal, 1),)) + oracle.frame(frame, 9)
        else:
            need(position == "exit" and reg.startswith("Y"), "exit role")
            frame = tuple(word["final_frames"][reg])
            need(len(frame) == 8 and all((b & normal).bit_count() % 2 == 0 for b in frame), "root hyperplane")
            expected = oracle.adjoint(oracle.frame(frame, 9)) + (("C", normal, -1),) + oracle.fourier(9)
        need(record["frame"] == list(frame) and record["normal"] == normal, "endpoint binding")
        need(type(record["recipe"]["rank"]) is int and record["recipe"]["rank"] == 0, "rank-zero endpoint")
        oracle.equal(oracle.recipe(record["recipe"]), expected, "intrinsic global phase")
    need(seen == {("entry", "X"+str(i)) for i in range(104)} | {("exit", "Y"+str(i)) for i in range(104)}, "complete endpoints")
    return {"distinct_transports": len(edges), "transport_occurrences": sum(map(len, edges.values())), "intrinsic_endpoints": len(seen)}


def rejects(call, message):
    try:
        call()
    except ValueError as error:
        need(message in str(error), "unexpected failure: " + str(error))
    else:
        raise ValueError("accepted fault: " + message)


def controls(word, packet, oracle, ports, labels):
    # Delete each new cross-group shear, not merely an inherited fanout.
    for reg, src in (("C012_0", "N39"), ("C012_1", "N35")):
        bad = copy.deepcopy(word)
        index = next(i for i in word["added_indices"]
                     if bad["program"][i][:3] == ["add", reg, src]
                     and bad["program"][i][3] == "-1")
        bad["program"][index][3] = "0"
        rejects(lambda: replay(bad, ports), "arbitrary-input endpoint")
    # The triple-to-pair branch is the new cross-group native obligation.
    branch_index = next(i for i in word["added_indices"]
                        if word["program"][i][:2] == ["transport", "C012_0"]
                        and len(word["program"][i][2]) == 6
                        and len(word["program"][i][3]) == 7)
    native_index = next(i for i, r in enumerate(packet["transports"])
                        if branch_index in r["events"])
    bad = copy.deepcopy(packet)
    rec = bad["transports"][native_index]["recipe"]["left"]
    rec["phase"] = (rec["phase"] + 1) % 4
    rejects(lambda: native_check(word, bad, oracle, labels), "native global phase/operator")
    bad = copy.deepcopy(packet)
    bad["transports"][native_index]["events"].remove(branch_index)
    rejects(lambda: native_check(word, bad, oracle, labels), "native event coverage")
    bad = copy.deepcopy(packet)
    bad["transports"][native_index]["recipe"]["rank"] += 1
    rejects(lambda: native_check(word, bad, oracle, labels), "native rank")
    bad = copy.deepcopy(packet)
    bad["endpoint_adapters"][0]["normal"] ^= 1
    rejects(lambda: native_check(word, bad, oracle, labels), "endpoint binding")
    bad = copy.deepcopy(word)
    bad["program"][branch_index][3] = bad["program"][branch_index][2]
    rejects(lambda: replay(bad, ports), "nested transport")
    # Remove late X0 capture but keep all transport counts unchanged.
    bad = copy.deepcopy(word)
    index = next(i for i in word["added_indices"]
                 if bad["program"][i][:3] == ["add", "LATE0", "X0"])
    bad["program"][index][3] = "0"
    rejects(lambda: replay(bad, ports), "arbitrary-input endpoint")
    return ["first_cross_shear", "second_cross_shear", "native_phase",
            "missing_occurrence", "native_rank", "endpoint_normal",
            "missing_branch_raise", "late_capture"]


def run():
    original, correction = authenticate()
    oracle = module(NATIVE / "vendor/native_verify.py", "cross_group_native_oracle")
    convert, ports, labels = geometry(oracle)
    word = assemble(original, correction, convert)
    packet = load(HERE / "NATIVE.json.gz", True)
    need(packet["word_sha256"] == digest(canonical(word)), "native word binding")
    result = replay(word, ports)
    result.update(native_check(word, packet, oracle, labels))
    result["controls"] = controls(word, packet, oracle, ports, labels)
    result.update(status="PASS_P104_CROSS_GROUP_NATIVE", source_head=SOURCE_HEAD,
                  word_sha256=digest(canonical(word)), native_payload_sha256=digest(canonical(packet)),
                  scope="Finite native chart transitions and three corrected logical targets; inherited nonzero private disposal, physical source delivery, routing, hosting, precision and all-size admission remain open.")
    return json.loads(canonical(result))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.out:
        need(not args.out.exists(), "output already exists")
    result = run()
    if args.out:
        with args.out.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(result, sort_keys=True, indent=2) + "\n")
    else:
        need(canonical(result) == canonical(load(HERE / "RESULT.json")), "complete receipt mismatch")
    print(result["status"], "edges=" + str(result["distinct_transports"]),
          "occurrences=" + str(result["transport_occurrences"]),
          "endpoint_coefficients=" + str(result["endpoint_coefficients"]),
          "added_rank_mass=" + str(result["added_rank_mass"]),
          "controls=" + str(len(result["controls"])))


if __name__ == "__main__":
    main()
