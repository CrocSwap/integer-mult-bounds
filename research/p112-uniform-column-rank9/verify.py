#!/usr/bin/env python3
"""Quantified proof premises and exact fixtures for the uniform-column family."""
import argparse
from collections import Counter
from hashlib import sha1, sha256
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = "ef5f39403610d231a0c27e8a6b4f08c10209bcd6"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


M = module("uniform_column_model", HERE / "model.py")
need = M.need


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, "duplicate JSON key: " + key)
            result[key] = value
        return result
    def bad(value):
        raise ValueError("noninteger/nonfinite JSON number: " + value)
    return json.loads(path.read_text(), object_pairs_hook=pairs, parse_float=bad, parse_constant=bad)


def sources():
    data = read_json(HERE / "SOURCES.json")
    inputs = {"research/p112-single-lift/geometry.py", "research/p112-single-lift/NOTICE.md",
              "research/complex-frame-pair-decoders/PROOF.md"}
    provenance = {"certificates/selected-result.json", "docs/research/agent-task-catalog.json"}
    need(data["base_commit"] == BASE, "source base")
    need(len(data["files"]) == 5 and {r["path"] for r in data["files"]} == inputs | provenance,
         "source inventory")
    for row in data["files"]:
        need(row["usage"] == ("input" if row["path"] in inputs else "provenance"), "source role")
        if row["path"] not in inputs:
            continue
        prefix = "PR845-" if "p112-single-lift" in row["path"] else "PR968-"
        local = HERE / "references" / (prefix + row["path"].rsplit("/", 1)[-1])
        content = local.read_bytes()
        need(sha256(content).hexdigest() == row["sha256"], "retained source SHA256")
        need(sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest() == row["git_blob"],
             "retained source Git blob")
        live = HERE.parents[1] / row["path"]
        if live.exists():
            need(live.read_bytes() == content, "live mathematical source drift")
    remote = read_json(HERE / "REMOTE-SOURCES.json")
    expected = {"PR1591-README.md", "PR1591-PROOF.md", "PR1613-README.md"}
    need(len(remote["files"]) == 3 and {r["file"] for r in remote["files"]} == expected,
         "remote attribution inventory")
    for row in remote["files"]:
        need(row["head"] == ("264b8dcfc56584797ebf36d69ee35de18313fd27" if row["file"].startswith("PR1591")
                             else "a34723742801f877c9636ed72f176a7ffa7bf005"), "remote head")
        content = (HERE / "references" / row["file"]).read_bytes()
        need(sha256(content).hexdigest() == row["sha256"], "remote attribution SHA256")
        need(sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest() == row["git_blob"],
             "remote attribution blob")


def bind_geometry(roots, x, b):
    source = module("pinned_pr845_geometry", HERE / "references/PR845-geometry.py")
    old = source.build()
    source.check_geometry(old)
    positions = {r: i for i, r in enumerate(roots)}
    mapped = []
    for r, row in zip(old["roots"], old["X"]):
        key = max(tuple(r), tuple(-v for v in r))
        sign = 1 if key == tuple(r) else -1
        index = positions[key]
        need([sign * a for a in row] == x[index], "pinned source coordinate binding")
        mapped.append(index)
    need(len(set(mapped)) == 112, "pinned root bijection")
    for i in range(112):
        for j in range(112):
            need(((old["duals"][i] & old["labels"][j]).bit_count() & 1) ==
                 ((b[mapped[i]] >> mapped[j]) & 1), "pinned binary pairing binding")


def finite(roots, frame, x, b):
    chars = M.characters(b)
    frame_chars = [sum(int(row[k] == 0) << i for i, row in enumerate(x)) for k in range(8)]
    need(len(set(frame_chars)) == 8 and set(frame_chars) <= set(chars), "frame-character inclusion")
    rows_by_char = [[i for i in range(112) if (c >> i) & 1] for c in chars[1:]]
    counts = Counter()
    digest = sha256()
    kernels, tables = [], []
    for v in range(112):
        expected = {c: [int(j == k) for j in range(8)] for k, c in enumerate(frame_chars)}
        expected[b[v]] = x[v]
        need(len(expected) == 9, "distinct reduced normal directions")
        exceptions = []
        for index, (char, support) in enumerate(zip(chars[1:], rows_by_char), 1):
            rows = [x[i] for i in support if i != v]
            rank = len(M.rational_basis(rows))
            need(rank == (7 if char in expected else 8), "exact complex-kernel classification")
            if char in expected:
                normal = expected[char]
                need(any(normal) and all(M.dot(row, normal) == 0 for row in rows), "exact kernel normal")
                exceptions.append(index)
            counts[rank] += 1
            digest.update(f"{v},{index},{rank}\n".encode())
        kernels.append(exceptions)
        supports = [[i for i in range(112) if i != v and x[i][k]] for k in range(8)]
        supports += [[i for i in range(112) if not ((b[v] >> i) & 1)], [v], list(range(112))]
        need(len(supports[8]) == 52, "uniform-column free support")
        need([len(M.binary_basis(b[i] for i in group)) for group in supports] == [8] * 9 + [1, 9],
             "actual support-span classification")
        for k in range(8):
            need(len(M.binary_basis(b[i] for i in range(112) if x[i][k])) == 8,
                 "unshifted coordinate support")
        table = [[M.pairing_rank(b, a, c) for c in supports] for a in supports]
        for i in range(11):
            for j in range(11):
                if i == 10 or j == 10:
                    expect = 9 if i == j else (1 if 9 in (i, j) else 8)
                elif 9 in (i, j):
                    expect = 0 if 8 in (i, j) else 1
                elif i == j == 8:
                    expect = 8
                elif 8 in (i, j):
                    expect = 7 if x[v][min(i, j)] else 8
                else:
                    expect = 8
                need(table[i][j] == expect, "complete support-class pairing table")
        tables.append(table)
    unpunctured = Counter()
    for char, support in zip(chars[1:], rows_by_char):
        rank = len(M.rational_basis([x[i] for i in support]))
        need(rank == (7 if char in frame_chars else 8), "unpunctured normal classification")
        unpunctured[rank] += 1
    return {"geometry_sha256": sha256(canonical([roots, frame, x, b]).encode()).hexdigest(),
            "characters_sha256": sha256(canonical(chars).encode()).hexdigest(),
            "puncture_character_cases": 112 * 511,
            "complex_rank_counts": {str(k): v for k, v in sorted(counts.items())},
            "rank_table_sha256": digest.hexdigest(), "exceptional_character_indices": kernels,
            "pairing_table_entries": 112 * 121,
            "pairing_tables_sha256": sha256(canonical(tables).encode()).hexdigest(),
            "unpunctured_rank_counts": {str(k): v for k, v in sorted(unpunctured.items())}}


def fixture(x, b, v, parameter, kind):
    re, im, divisor = parameter
    need(divisor > 0 and (re != 0 or im != 0), "nonzero complex completion parameter")
    lam = M.g(M.F(re, divisor), M.F(im, divisor))
    left = M.fixture_left(x, v, lam, kind)
    d, t, denominator, right, h = M.factor_model(x, v, lam, left)
    s = x[v]
    w = [M.dot(row, s) - 4 * int(i == v) for i, row in enumerate(x)]
    need([i for i, value in enumerate(w) if value] == [i for i in range(112) if not ((b[v] >> i) & 1)],
         "changed entries not exactly free")
    c = [row + [int(i == v)] for i, row in enumerate(x)]
    need(len(M.rational_basis(c, 9)) == 9, "forced factor-space rank")
    hinv = M.inverse(h)
    k = [[M.g(a)] for a in s + [-4]]
    value = M.matrix_product(M.transpose(k), M.matrix_product(hinv, k))[0][0]
    need(value == M.mul(M.g(-4), M.inv(lam)), "nonzero V/V cross-duality coefficient")
    need(M.matrix_product(M.transpose(right), M.matrix_product(hinv, left)) == M.eye(9),
         "full factor duality")
    for i in range(112):
        for j in range(112):
            actual = M.ig_product_entry(d[i], t[j])
            baseline = M.dot(x[i], x[j])
            correction = w[i] * int(j == v)
            need((divisor * actual[0], divisor * actual[1]) ==
                 (denominator * (divisor * baseline + re * correction), denominator * im * correction),
                 "exact completion identity")
    ranks = []
    for j in range(9):
        readers = [i for i in range(112) if d[i][j] != (0, 0)]
        writers = [i for i in range(112) if t[i][j] != (0, 0)]
        ranks.append(M.pairing_rank(b, readers, writers))
    mixed = sum(any(left[i][j] != M.ZERO for i in range(8)) and
                any(right[i][j] != M.ZERO for i in range(8)) for j in range(9))
    need(mixed in (8, 9), "rank-eight projected coefficient block")
    need(sum(ranks) >= (71 if mixed == 9 else 64), "COPY envelope")
    if kind in ("right_zero", "left_zero"):
        need(sorted(ranks) == [0] + [8] * 8, "zero-cost residual branch")
    if kind == "pure_compensation" and parameter == [-1, 0, 1]:
        need(sorted(ranks) == [1, 7] + [8] * 7, "paid compensation boundary")
    if kind == "nine_mixed_71":
        need(mixed == 9 and sorted(ranks) == [7] + [8] * 8, "sharp nine-mixed branch")
    return {"v": v, "lambda": parameter, "kind": kind, "ranks": ranks,
            "copy_sum": sum(ranks), "mixed_terms": mixed, "matrix_entries": 112 * 112}, (d, t, denominator, left, right, h)


def fixtures(x, b):
    specifications = [(0, [-1, 0, 1], "right_zero"), (17, [1, 0, 2], "right_zero"),
                      (42, [0, 1, 1], "right_zero"), (111, [-1, 1, 1], "right_zero"),
                      (0, [-1, 0, 1], "pure_compensation"), (42, [-1, 0, 1], "pure_compensation"),
                      (17, [1, 0, 1], "left_zero"), (76, [0, 1, 1], "left_zero"),
                      (0, [-1, 0, 1], "nine_mixed_71"), (42, [1, 0, 2], "nine_mixed_71"),
                      (111, [0, 1, 1], "nine_mixed_71"), (17, [1, 0, 1], "dense_complex"),
                      (42, [-1, 1, 1], "dense_complex"), (76, [-2, 0, 1], "dense_complex")]
    reports = []
    controls = []
    for v, parameter, kind in specifications:
        report, data = fixture(x, b, v, parameter, kind)
        reports.append(report)
        d, t, denominator, left, right, h = data
        if kind == "pure_compensation":
            full = M.ig_product_entry(d[v], t[v])
            omitted = M.ig_product_entry(d[v][:-1], t[v][:-1])
            need(full[0] - omitted[0] == 4 * denominator and (b[v] >> v) & 1,
                 "omitted rank-one compensation control")
            need(sum(report["ranks"][:-1]) == 63, "false-saving control needs COPY63")
            controls.append("omit-paid-compensation-v" + str(v))
        if kind == "dense_complex":
            # The wrong Hermitian convention must fail on constrained entries.
            failed = any(M.ig_product_entry(d[i], [(a, -c) for a, c in t[j]]) !=
                         M.ig_product_entry(d[i], t[j])
                         for i in range(112) for j in range(112) if (b[i] >> j) & 1)
            need(failed, "Hermitian corruption not detected")
            controls.append("Hermitian-v" + str(v))
    def rejects(name, action):
        try:
            action()
        except (ValueError, ZeroDivisionError):
            controls.append(name)
        else:
            raise ValueError("control escaped: " + name)
    rejects("rank-eight-zero-parameter-outside-scope", lambda: fixture(x, b, 0, [0, 0, 1], "right_zero"))
    rejects("impossible-left-zero-at-minus-one", lambda: fixture(x, b, 0, [-1, 0, 1], "left_zero"))
    bad_matrix = M.eye(9)
    bad_matrix[8] = bad_matrix[7][:]
    rejects("singular-factor-basis", lambda: M.inverse(bad_matrix))
    # Complex isotropy does not create an unlisted reduced support.
    isotropic = [M.g(row[0], row[1]) for row in x]
    need(len(M.binary_basis(b[i] for i, value in enumerate(isotropic) if value != M.ZERO)) == 9,
         "complex isotropic-normal boundary")
    controls.append("isotropic-normal-has-full-binary-span")
    return reports, controls


def run():
    sources()
    roots, frame, x, b = M.geometry()
    bind_geometry(roots, x, b)
    certificate = finite(roots, frame, x, b)
    cases, controls = fixtures(x, b)
    independent = module("uniform_column_independent_boundaries", HERE / "independent.py")
    integer_cases = independent.integer_boundaries()
    return {"schema": "p112-uniform-column-rank9-v1", "base": BASE,
            "status": "PASS_P112_UNIFORM_COLUMN_RANK9", "finite": certificate,
            "fixtures": cases, "independent_integer_boundaries": integer_cases,
            "failure_controls": controls, "sharp_copy_floor": 64,
            "sharp_nine_mixed_floor": 71,
            "rank_envelopes": [[0] + [8] * 8, [1, 7] + [8] * 7, [7] + [8] * 8],
            "power_scope": "sum rho^q >= 8*8^q for all 0<q<=1; separate COPY billing",
            "limits": "uniform one-column correction, nonzero complex parameter, exactly nine factors; no supplier or new kappa"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-expected", action="store_true")
    args = parser.parse_args()
    report = run()
    path = HERE / "EXPECTED.json"
    if args.write_expected:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        need(canonical(report) == canonical(read_json(path)), "receipt mismatch")
    print(report["status"], "floor=64", "nine_mixed=71", "hyperplanes=57232",
          "receipt_sha256=" + sha256(canonical(report).encode()).hexdigest())


if __name__ == "__main__":
    main()
