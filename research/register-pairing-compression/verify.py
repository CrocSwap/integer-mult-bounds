#!/usr/bin/env python3
"""Finite corroboration and boundary controls, not proof of the uniform lemma.
Gareth Davidson / @bitplane, substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("pairing_core", HERE / "compression.py")
c = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = c
spec.loader.exec_module(c)
require = c.require


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def source_check(package=HERE):
    source = json.loads((package / "SOURCES.json").read_text())
    checked = []
    for item in source["files"]:
        if item["usage"] != "input":
            continue
        data = (package.parents[1] / item["path"]).read_bytes()
        require(sha(data) == item["sha256"], "changed live proof input: " + item["path"])
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == item["git_blob"], "changed Git source blob")
        checked.append(item["path"])
    for item in source["archived_proofs"]:
        data = (package / item["path"]).read_bytes()
        require(sha(data) == item["sha256"], "changed archived proof: " + item["path"])
        require(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                == item["git_blob"], "changed archived source blob")
        checked.append(item["path"])
    return sorted(checked)


def bindings(package=HERE):
    return {name: sha((package / name).read_bytes())
            for name in ("compression.py", "verify.py", "PROOF.md", "SOURCES.json")}


def preflight(package=HERE):
    source_check(package)
    task = json.loads((package / "TASK.json").read_text())
    expected = json.loads((package / "RESULT.json").read_text())
    require(sha(canonical(expected)) == task["receipt_sha256"], "changed mathematical receipt")
    require(expected["bindings"] == bindings(package), "changed proof or verifier binding")
    return expected


def all_subspaces(width):
    found = {frozenset({0})}
    frontier = list(found)
    while frontier:
        current = frontier.pop()
        for v in range(1, 1 << width):
            if v not in current:
                enlarged = frozenset(current | {u ^ v for u in current})
                if enlarged not in found:
                    found.add(enlarged)
                    frontier.append(enlarged)
    return sorted(found, key=lambda s: (len(s), sorted(s)))


def set_basis(subspace):
    result, built = [], frozenset({0})
    for v in sorted(subspace):
        if v not in built:
            result.append(v)
            built = frozenset(built | {u ^ v for u in built})
    require(built == subspace, "subspace basis did not generate its input")
    return result


def oracle_pairing_rank(uspace, vspace):
    # Image enumeration is separate from the core's Gaussian elimination.
    image = {tuple((u & v).bit_count() % 2 for v in sorted(vspace)) for u in uspace}
    require(len(image) & (len(image) - 1) == 0, "pairing image is not a binary space")
    return len(image).bit_length() - 1


def compare_word(word, active, roles, coefficients=c.COEFFICIENTS):
    reduced, maps = c.compress(word, active, roles)
    require(c.word_matrix(reduced, active + maps["rank"], coefficients)
            == c.sandwich(c.word_matrix(word, roles, coefficients), maps),
            "full noncommutative product identity failed")
    before, after = Counter(f.label for f in word), Counter(f.label for f in reduced)
    require(all(after[g] <= n for g, n in before.items()), "letter cost increased")
    return reduced, maps


def subspace_census():
    rows, digest = [], hashlib.sha256()
    coefficients = {"a": (1 << 1) ^ (1 << 8) ^ (1 << 13),
                    "b": 1 ^ (1 << 32) ^ (1 << 6), "c": (1 << 3) ^ (1 << 37)}
    for width, expected in enumerate((1, 2, 5, 16, 67)):
        spaces = all_subspaces(width)
        require(len(spaces) == expected, "incomplete binary subspace enumeration")
        histogram = Counter()
        for uspace in spaces:
            for vspace in spaces:
                ub, vb = set_basis(uspace), set_basis(vspace)
                word = [c.Factor("abc"[i % 3], 1 | (u << 1), 1 | (v << 1))
                        for i, (u, v) in enumerate(itertools.zip_longest(ub, vb, fillvalue=0))]
                reduced, maps = compare_word(word, 1, width + 1, coefficients)
                rank = oracle_pairing_rank(uspace, vspace)
                require(maps["rank"] == rank, "pairing image oracle disagrees")
                histogram[rank] += 1
                digest.update(canonical([width, sorted(uspace), sorted(vspace), maps,
                                         [[f.label, f.x, f.y] for f in reduced]]))
        rows.append({"workspace": width, "subspaces": expected, "pairs": expected ** 2,
                     "pairing_rank_histogram": dict(sorted(histogram.items()))})
    return {"domains": rows, "total_pairs": sum(r["pairs"] for r in rows),
            "transcript_sha256": digest.hexdigest()}


POSITIONS = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))


def literal_matrix(g):
    matrix = [[int(i == j) for j in range(4)] for i in range(4)]
    for bit, (i, j) in enumerate(POSITIONS):
        matrix[i][j] = g >> bit & 1
    return matrix


def literal_product(g, h):
    a, b = literal_matrix(g), literal_matrix(h)
    out = [[sum(a[i][k] * b[k][j] for k in range(4)) % 2 for j in range(4)] for i in range(4)]
    return sum(out[i][j] << bit for bit, (i, j) in enumerate(POSITIONS))


LITERAL_GROUP = [[literal_product(g, h) for h in range(64)] for g in range(64)]


def faithful_columns(word, roles, matrix, coefficients=c.COEFFICIENTS):
    # Separate left regular representation on EVERY basis vector. Product
    # factors act in reverse order. No matrix-product helper is called.
    for input_role in range(roles):
        for address in range(64):
            vector = [0] * roles
            vector[input_role] = 1 << address
            for f in reversed(word):
                total = 0
                for j in range(roles):
                    if f.y >> j & 1:
                        total ^= vector[j]
                delta = 0
                for g in range(64):
                    if coefficients[f.label] >> g & 1:
                        for h in range(64):
                            if total >> h & 1:
                                delta ^= 1 << LITERAL_GROUP[g][h]
                for j in range(roles):
                    if f.x >> j & 1:
                        vector[j] ^= delta
            expected = []
            for output_role in range(roles):
                value = 0
                for g in range(64):
                    if matrix[output_role][input_role] >> g & 1:
                        value ^= 1 << LITERAL_GROUP[g][address]
                expected.append(value)
            require(vector == expected, "literal faithful column differs")
    return roles * 64


def pair_census():
    histogram, naive_failures, digest = Counter(), 0, hashlib.sha256()
    for x, y, z, w in itertools.product(range(1, 8), repeat=4):
        word = [c.Factor("a", x, y), c.Factor("b", z, w)]
        reduced, maps = compare_word(word, 1, 3)
        histogram[maps["rank"]] += 1
        naive = [c.Factor(f.label, f.x & 1, f.y & 1) for f in word if f.x & 1 and f.y & 1]
        naive_failures += c.word_matrix(naive, 1)[0][0] != c.word_matrix(word, 3)[0][0]
        digest.update(canonical([x, y, z, w, maps["rank"], [[f.label, f.x, f.y] for f in reduced]]))
    require(naive_failures > 0, "naive projection control did not exercise feedback")
    return {"ordered_pairs": 7 ** 4, "pairing_rank_histogram": dict(sorted(histogram.items())),
            "naive_projection_failures": naive_failures, "transcript_sha256": digest.hexdigest()}


def dirty_change_basis(word, active, width):
    result = list(word)
    for i in range(width):
        if width < 2:
            break
        j = (i + 1) % width
        ii, jj = active + i, active + j
        result = [c.Factor(f.label, f.x ^ (((f.x >> jj) & 1) << ii),
                           f.y ^ (((f.y >> ii) & 1) << jj)) for f in result]
    return result


def endpoint_fixtures():
    fixtures, columns, deleted, idem, nilpotent = [], 0, 0, 0, 0
    for width in range(7):
        for rank in range(width + 1):
            word = c.direct_word()
            noise = [c.Factor("abc"[j % 3], 1 | (1 << (j + 2)),
                              2 | ((1 << (j + 2)) if j < rank else 0)) for j in range(width)]
            # Every letter factor is an involution; this is an exact relator.
            word[5:5] = noise + list(reversed(noise))
            word = dirty_change_basis(word, 2, width)
            reduced, maps = compare_word(word, 2, width + 2)
            require(maps["rank"] == rank, "fixture pairing rank")
            require(c.word_matrix(word, width + 2) == c.target(width + 2), "dirty endpoint not restored")
            require(c.word_matrix(reduced, 2 + rank) == c.target(2 + rank), "compressed dirty endpoint")
            columns += faithful_columns(word, width + 2, c.target(width + 2))
            columns += faithful_columns(reduced, 2 + rank, c.target(2 + rank))
            for f in word:
                if c.dot(f.x, f.y):
                    idem += 1
                else:
                    nilpotent += 1
            deleted += len(word) - len(reduced)
            fixtures.append({"roles": width + 2, "rank": rank, "length": len(word),
                             "compressed_length": len(reduced)})
    # Both spans leave H, but their dirty pairing vanishes: neither common
    # block orientation from PR1680 holds, yet all four noise factors vanish.
    orthogonal = [c.Factor("a", 1, 8), c.Factor("b", 4, 1)]
    word = orthogonal + list(reversed(orthogonal)) + c.direct_word()
    reduced, maps = compare_word(word, 2, 4)
    require(maps["rank"] == 0 and maps["column_span_rank"] == maps["row_span_rank"] == 1,
            "orthogonal bidirectional workspace fixture")
    require(len(reduced) == 14 and c.word_matrix(word, 4) == c.target(4), "zero factors not removed")
    columns += faithful_columns(word, 4, c.target(4))
    deleted += 4
    require(idem > 0 and nilpotent > 0 and deleted > 0, "missing coupling boundary cases")
    return {"fixtures": fixtures, "orthogonal_bidirectional_fixture": True,
            "faithful_columns": columns, "deleted_nilpotent_factors": deleted,
            "idempotent_occurrences": idem, "nilpotent_occurrences": nilpotent}


def expect_failure(function, fragment):
    try:
        function()
    except (ValueError, OSError) as exc:
        require(fragment in str(exc), "wrong failure: " + str(exc))
    else:
        raise ValueError("control unexpectedly accepted: " + fragment)


def semantic_controls():
    controls = []
    word = [c.Factor("a", 1, 2), c.Factor("b", 2, 1)]
    reduced, maps = compare_word(word, 1, 2)
    require(maps["rank"] == 1 and c.word_matrix(word, 2)[0][0] != 1, "feedback is absent")
    controls.append("naive active-corner projection loses feedback")
    for field in ("F_rows", "G_columns"):
        bad = deepcopy(maps)
        bad[field] = [0]
        expect_failure(lambda: c.check_compression(word, reduced, bad), "FG is not identity")
        controls.append("wrong " + field)
    bad = deepcopy(maps)
    bad.update(rank=0, F_rows=[], G_columns=[])
    expect_failure(lambda: c.check_compression(word, [], bad), "incorrect pairing rank")
    controls.append("incorrect zero pairing rank")
    # FG=I alone is insufficient: choose an unrelated ambient direction.
    reduced, maps = c.compress(word, 1, 3)
    bad = deepcopy(maps)
    bad.update(F_rows=[2], G_columns=[2])
    expect_failure(lambda: c.check_compression(word, reduced, bad), "ordered contraction changed")
    controls.append("FG identity without contraction preservation")
    transposed = [c.Factor(f.label, f.y, f.x) for f in reduced]
    expect_failure(lambda: c.check_compression(word, transposed, maps), "compressed word mismatch")
    controls.append("transposed coupling")
    bad = deepcopy(maps)
    bad["retained_indices"] = [0]
    expect_failure(lambda: c.check_compression(word, reduced, bad), "deleted-factor indices")
    controls.append("unpriced deletion")
    for f, name in ((c.Factor("a", 4, 4), "unrestored dirty role"),
                    (c.Factor("a", 1, 4), "dirty input contaminates target")):
        actual = c.word_matrix(c.direct_word() + [f], 3)
        require([row[:2] for row in actual[:2]] == c.target(2), "active corner fixture")
        expect_failure(lambda: require(actual == c.target(3), "full endpoint differs"), "full endpoint differs")
        controls.append(name)
    require(c.ring_multiply(c.COEFFICIENTS["a"], c.COEFFICIENTS["b"])
            != c.ring_multiply(c.COEFFICIENTS["b"], c.COEFFICIENTS["a"]), "coefficients commute")
    controls.append("ordered noncommutative coefficients")
    direct = c.direct_word()
    expect_failure(lambda: require(c.word_matrix(direct[:-1], 2) == c.target(2), "omitted call"), "omitted call")
    direct[0] = c.Factor("c", 1, 1)
    expect_failure(lambda: require(c.word_matrix(direct, 2) == c.target(2), "wrong letter"), "wrong letter")
    controls.extend(["omitted restoration call", "wrong paid letter"])
    expect_failure(lambda: c.compress([c.Factor("a", 0, 1)], 1, 2), "nonzero")
    expect_failure(lambda: c.compress([c.Factor("a", 4, 1)], 1, 2), "within the role")
    controls.extend(["zero original factor", "out-of-domain role"])
    return controls


def excess_profiles(budget, parts):
    if parts == 0:
        yield ()
    else:
        for first in range(budget + 1):
            for rest in excess_profiles(budget - first, parts - 1):
                yield (first,) + rest


def ut4_budget():
    # Integer consequences of inherited inequalities, NOT a replay of the
    # PR2175/2314 exhaustive exclusion certificates.
    rows = []
    for length in range(13, 25):
        excess, cases, maximum = length - 13, 0, 0
        for e in excess_profiles(excess, 6):
            u, v = sum(e[::2]), sum(e[1::2])
            require(min(u, v) <= excess // 2, "excess does not bound pairing rank")
            maximum = max(maximum, min(u, v))
            cases += 1
        require(maximum == excess // 2, "relaxation endpoint was not attained")
        rows.append({"length": length, "span_profiles": cases, "role_bound": 2 + maximum})
    cheaper = []
    for a, b, cc in itertools.product(range(27), repeat=3):
        if a >= 4 and cc >= 4 and b >= 5 and (b != 5 or a + cc >= 10) and a + 3 * b + cc < 26:
            cheaper.append([a, b, cc])
    require(sorted(cheaper) == [[4, 5, 6], [5, 5, 5], [6, 5, 4]], "weighted candidate splits")
    require(all(sum(s) == 15 and s[0] + 3 * s[1] + s[2] == 25 for s in cheaper), "fifteen-call budget")
    return {"span_relaxations": rows, "price": [1, 3, 1], "direct_price": 26,
            "only_cheaper_count_splits": sorted(cheaper), "cheaper_price": 25,
            "maximum_roles_for_cheaper_word": 3, "fifteen_call_existence_decided": False}


def run():
    sources = source_check()
    require(LITERAL_GROUP == c.GROUP, "literal UT4 multiplication disagrees")
    for g in (1, 8, 32):
        require(c.GROUP[g][g] == 0, "letter is not an involution")
    print("checked source pins and all 4096 literal group products", flush=True)
    subspaces, pairs = subspace_census(), pair_census()
    print("checked 4775 subspace pairs and 2401 ordered rank-one pairs", flush=True)
    fixtures, controls, budget = endpoint_fixtures(), semantic_controls(), ut4_budget()
    return {"schema_version": 1, "bindings": bindings(), "source_inputs": sources,
            "literal_group_products": 4096, "subspace_census": subspaces,
            "rank_one_pair_census": pairs, "full_endpoint_fixtures": fixtures,
            "semantic_controls": controls, "ut4_consequence": budget,
            "scope": "Finite corroboration of PROOF.md; no fifteen-call census, native supplier, or kappa claim."}


def disk_controls():
    preflight()
    with tempfile.TemporaryDirectory(prefix="pairing-compression-controls-") as tmp:
        root = Path(tmp)
        package = root / "research" / HERE.name
        shutil.copytree(HERE, package)
        # The source may be a read-only export. Only this private temporary
        # copy becomes writable for deliberate corruption controls.
        package.chmod(0o755)
        for path in package.rglob("*"):
            path.chmod(0o755 if path.is_dir() else 0o644)
        source = json.loads((HERE / "SOURCES.json").read_text())
        for item in source["files"]:
            if item["usage"] == "input":
                dst = root / item["path"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(HERE.parents[1] / item["path"], dst)
        command = [sys.executable, "-I", "-O", "-B", str(package / "verify.py"), "--preflight"]
        good = subprocess.run(command, cwd=root, capture_output=True, text=True)
        require(good.returncode == 0, "Git-free relocated preflight failed: " + good.stderr)
        targets = [(root / next(i["path"] for i in source["files"] if i["usage"] == "input"), "changed live proof"),
                   (package / source["archived_proofs"][0]["path"], "changed archived proof"),
                   (package / "PROOF.md", "changed proof or verifier binding"),
                   (package / "RESULT.json", "changed mathematical receipt")]
        for path, marker in targets:
            original = path.read_bytes()
            if path.name == "RESULT.json":
                value = json.loads(original)
                value["ut4_consequence"]["maximum_roles_for_cheaper_word"] = 2
                path.write_text(json.dumps(value))
            else:
                path.write_bytes(original + b"\ncorrupted proof input\n")
            result = subprocess.run(command, cwd=root, capture_output=True, text=True)
            require(result.returncode != 0 and marker in result.stderr, "disk fault was not rejected: " + marker)
            path.write_bytes(original)
    print("PASS_PAIRING_COMPRESSION_DISK_CONTROLS mutations=4 relocated_preflight=1")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write-result", type=Path, help="write to a new, unoccupied path")
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--controls", action="store_true")
    args = parser.parse_args()
    if args.preflight:
        preflight()
        print("PASS_PAIRING_COMPRESSION_PREFLIGHT")
        return
    if args.controls:
        disk_controls()
        return
    expected = None if args.write_result else preflight()
    if args.write_result:
        require(not args.write_result.exists(), "output path is occupied")
    result = run()
    if args.write_result:
        with args.write_result.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    else:
        require(canonical(result) == canonical(expected), "mathematical receipt differs")
    print("PASS_REGISTER_PAIRING_COMPRESSION receipt_sha256=" + sha(canonical(result)))


if __name__ == "__main__":
    main()
