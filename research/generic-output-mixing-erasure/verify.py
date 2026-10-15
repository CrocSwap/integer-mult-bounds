#!/usr/bin/env python3
"""Exact normalized coefficient checker; verification never generates evidence.

An A_i event contributes v tensor A_i (z0 + sum_j q_j B_j x_j),
where v=P^-1 e_port. All dirty columns and labelled coefficients are checked.
The all-parameter proof is in README.md. No predecessor code is imported.
"""
from __future__ import annotations

import argparse
from collections import Counter, deque
import copy
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


class Invalid(ValueError):
    pass


def require(ok, reason):
    if not ok:
        raise Invalid(reason)


def integer(value, lower, upper, label):
    require(type(value) is int and lower <= value < upper, label)
    return value


def validate(f):
    require(isinstance(f, dict), "fixture object")
    s = integer(f.get("source_count"), 0, 65, "source count")
    n = integer(f.get("logical_outputs"), 0, 257, "output count")
    r = integer(f.get("bank_size"), n, 513, "bank size")
    masks = f.get("masks")
    require(isinstance(masks, list) and len(masks) == n, "mask count")
    for m in masks:
        integer(m, 0, 1 << s, "mask domain")
    require(isinstance(f.get("word"), list), "word array")
    for e in f["word"]:
        require(isinstance(e, list) and bool(e), "event array")
        if e[0] == "B":
            require(len(e) == 2, "B arity")
            integer(e[1], 0, s, "B source")
        elif e[0] == "A":
            require(len(e) == 3, "A arity")
            integer(e[1], 0, n, "A reader")
            integer(e[2], 0, r, "A port")
        elif e[0] == "X":
            require(len(e) == 3, "X arity")
            integer(e[1], 0, r, "X source")
            integer(e[2], 0, r, "X target")
            require(e[1] != e[2], "noninvertible aliased X")
        else:
            raise Invalid("unknown operation")
    return s, n, r


def analyze(f):
    _, n, r = validate(f)
    inv = [1 << i for i in range(r)]
    # Bit 0 is A_i z0; bit j+1 is A_i B_j x_j.
    coefficients = [[0] * n for _ in range(r)]
    q = 0
    erased = []
    for e in f["word"]:
        if e[0] == "B":
            q ^= 1 << e[1]
            erased.append(e.copy())
        elif e[0] == "X":
            _, source, target = e
            # P_new=E P; inverse right multiplication adds column target to source.
            inv = [row ^ (((row >> target) & 1) << source) for row in inv]
        else:
            _, reader, port = e
            signal = 1 | (q << 1)
            for row in range(r):
                if (inv[row] >> port) & 1:
                    coefficients[row][reader] ^= signal
            if (inv[reader] >> port) & 1:
                erased.append(["A", reader, reader])
    return inv, q, coefficients, erased


def check(f):
    inv, q, coefficients, erased = analyze(f)
    n, r = f["logical_outputs"], f["bank_size"]
    require(inv == [1 << i for i in range(r)], "output dirt frame")
    require(q == 0, "connector restoration")
    for row in range(r):
        for reader in range(n):
            expected = f["masks"][reader] << 1 if row == reader else 0
            require(coefficients[row][reader] == expected,
                    f"reader coefficient row={row} reader={reader}")
    return erased


def counts(word):
    return Counter((e[0], e[1]) for e in word if e[0] != "X")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def census():
    """Restricted-growth words, independent of the oracle's endpoint pairings."""
    hist = Counter()

    def visit(word, seen):
        if len(word) == 10:
            prefix, q = [0], 0
            for j in word:
                q ^= 1 << j
                prefix.append(q)
            hist[len({a ^ b for a in prefix for b in prefix})] += 1
            return
        for j, count in enumerate(seen):
            if count == 1:
                nxt = seen.copy()
                nxt[j] = 2
                visit(word + [j], nxt)
        if len(seen) < 5:
            visit(word + [len(seen)], seen + [1])

    visit([], [])
    require(sum(hist.values()) == 945 and max(hist) == 31, "pairing boundary")
    return {str(k): v for k, v in sorted(hist.items())}


def frame_census():
    """Every GL(3,2) output frame, around a generic two-source/three-row batch."""
    ident = (1, 2, 4)
    paths = {ident: []}
    queue = deque([ident])
    while queue:
        frame = queue.popleft()
        for a in range(3):
            for b in range(3):
                if a == b:
                    continue
                nxt = list(frame)
                nxt[b] ^= nxt[a]
                nxt = tuple(nxt)
                if nxt not in paths:
                    paths[nxt] = paths[frame] + [["X", a, b]]
                    queue.append(nxt)
    require(len(paths) == 168, "GL3 coverage")
    baseline = [["A", 0, 0], ["B", 0], ["A", 0, 0], ["B", 0],
                ["A", 1, 1], ["B", 1], ["A", 1, 1], ["B", 1],
                ["A", 2, 2], ["B", 0], ["B", 1], ["A", 2, 2],
                ["B", 1], ["B", 0]]
    total_reads = 0
    for frame, path in paths.items():
        word = copy.deepcopy(path)
        for e in baseline:
            if e[0] == "B":
                word.append(e.copy())
            else:
                for p in range(3):
                    if (frame[p] >> e[1]) & 1:
                        word.append(["A", e[1], p])
        word += list(reversed(path))
        f = dict(source_count=2, logical_outputs=3, bank_size=3,
                 masks=[1, 2, 3], word=word)
        erased = check(f)
        check({**f, "word": erased})
        require(not (counts(erased) - counts(word)), "componentwise dominance")
        total_reads += sum(e[0] == "A" for e in word)
    return {"frames": len(paths), "input_readouts": total_reads}


def rejected(f, reason):
    try:
        check(f)
    except Invalid as exc:
        require(reason in str(exc), f"wrong rejection: {exc}")
        return
    raise Invalid(f"control unexpectedly accepted: {reason}")


def controls(fixtures, common):
    baseline, decorated, odd = fixtures
    f = copy.deepcopy(baseline)
    f["word"].pop(next(i for i, e in enumerate(f["word"]) if e[0] == "B"))
    rejected(f, "connector restoration")
    f = copy.deepcopy(baseline)
    f["word"].pop(next(i for i, e in enumerate(f["word"]) if e[0] == "A"))
    rejected(f, "reader coefficient")
    f = copy.deepcopy(decorated)
    f["word"].pop(3)  # removes helper cancellation; all logical outputs stay right
    inv, q, coeff, _ = analyze(f)
    require(inv == [1 << i for i in range(33)] and q == 0, "helper control setup")
    require(all(coeff[row][i] == (f['masks'][i] << 1 if row == i else 0)
                for row in range(31) for i in range(31)), "helper control outputs")
    rejected(f, "reader coefficient row=31")
    f = copy.deepcopy(odd)
    f["word"].pop()
    rejected(f, "output dirt frame")
    f = copy.deepcopy(odd)
    f["word"][2] = ["X", 0, 0]
    rejected(f, "noninvertible aliased X")
    f = copy.deepcopy(baseline)
    f["word"][0][2] = True
    rejected(f, "A port")
    rejected(common, "reader coefficient")
    return 7


def check_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for pin in manifest["files"]:
        if pin["usage"] == "input":
            data = (ROOT / pin["path"]).read_bytes()
            require(hashlib.sha256(data).hexdigest() == pin["sha256"],
                    f"source drift: {pin['path']}")


def run(cert):
    require(type(cert.get("schema_version")) is int and cert["schema_version"] == 1,
            "certificate schema")
    fixtures = cert.get("fixtures")
    require(isinstance(fixtures, list) and len(fixtures) == 3, "fixture coverage")
    require([f.get("name") for f in fixtures] ==
            ["five_source_baseline", "five_source_dirty_output_helpers", "odd_reader_identity"],
            "fixture identities")
    inherited = json.loads((ROOT / "research/universal-connector-boundary/CERTIFICATE.json").read_text())
    source = inherited["schedules"]["five_extra_output"]
    source_word = [[op, i] if op == "B" else [op, i, i] for op, i in source["word"]]
    require(fixtures[0]["word"] == source_word and fixtures[0]["masks"] == source["rows"],
            "baseline source binding")
    result = []
    for f in fixtures:
        erased = check(f)
        require(erased == f.get("expected_erased"), "erasure receipt")
        check({**f, "word": erased})
        check({**f, "word": list(reversed(f["word"]))})
        require(not (counts(erased) - counts(f["word"])), "componentwise dominance")
        result.append({"name": f["name"], "map_calls": sum(counts(f["word"]).values()),
                       "erased_map_calls": len(erased),
                       "mixing_xors": sum(e[0] == "X" for e in f["word"]),
                       "dirty_bank_rows": f["bank_size"]})
    h = census()
    prices = [1, 4, 10, 16, 28]
    bill = sum(prices[e[1]] if e[0] == "B" else 1 for e in source_word)
    require(bill == 182, "weighted fixture bill")
    return {"schema_version": 1, "fixtures": result, "pairings": 945,
            "certificate_sha256": hashlib.sha256(canonical(cert).encode()).hexdigest(),
            "coverage_histogram": h, "max_coverage": 31,
            "five_source_map_optimum": 74, "weighted_fixture_optimum": bill,
            "frame_census": frame_census(),
            "negative_controls": controls(fixtures, cert["common_reader_control"]),
            "no_new_kappa": True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=HERE / "CERTIFICATE.json")
    parser.add_argument("--expected", type=Path, default=HERE / "EXPECTED.json")
    parser.add_argument("--write-expected", type=Path)
    args = parser.parse_args()
    check_pins()
    receipt = run(json.loads(args.certificate.read_text()))
    if args.write_expected:
        with args.write_expected.open("x") as handle:
            json.dump(receipt, handle, indent=2, sort_keys=True)
            handle.write("\n")
        print("WROTE_EXPECTED", args.write_expected)
    else:
        expected = json.loads(args.expected.read_text())
        require(canonical(receipt) == canonical(expected), "expected receipt mismatch")
        print("PASS_GENERIC_OUTPUT_MIXING_ERASURE fixtures=3 pairings=945 frames=168 "
              "map_optimum=74 weighted_optimum=182 controls=7 no_new_kappa")


if __name__ == "__main__":
    main()
