#!/usr/bin/env python3
"""Check the full literal export, including a sparse-matrix precision oracle.

Apache-2.0. Sagar Thakrar, with substantial OpenAI Codex assistance.
Uses Dylan Crow's unchanged exporter; imports no primary census code.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def matrix_bound(records, n, reverse):
    rows = [{i: 1} for i in range(n + 1)]
    largest, opened = 1, False
    for op, a, b, c, _, _ in (reversed(records) if reverse else records):
        if op == 0:
            continue
        if op == 1:
            need(b != n or opened, "temporary lifetime")
            for j, coefficient in rows[b].items():
                rows[a][j] = rows[a].get(j, 0) + abs(c) * coefficient
            largest = max(largest, sum(rows[a].values()))
        elif (op == 2) != reverse:
            need(not opened and b == n, "fresh COPY")
            rows[b], opened = dict(rows[a]), True
        else:
            need(opened and b == n, "bound ERASE")
            rows[b], opened = {}, False
    need(not opened, "unclosed COPY")
    return largest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("words", type=Path, nargs="?", help="existing literal words, otherwise run complete verification")
    args = parser.parse_args()
    pins = json.loads((HERE / "SOURCES.json").read_text())["files"]
    for pin in pins:
        if pin["usage"] == "input":
            need(hashlib.sha256((ROOT / pin["path"]).read_bytes()).hexdigest() == pin["sha256"],
                 "source pin: " + pin["path"])
    receipt = json.loads((HERE / "CERTIFICATE.json").read_text())
    exporter = ROOT / "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
    result = {}
    with tempfile.TemporaryDirectory(prefix="r420-triple-records-") as temporary:
        word_directory = args.words
        if word_directory is None:
            word_directory = Path(temporary) / "words"
            subprocess.run([sys.executable, "-B", str(HERE / "verify.py"), "--output", str(word_directory)], check=True)
        for name, expected in receipt["words"].items():
            word_path = (word_directory / (name + ".json")).resolve()
            word = json.loads(word_path.read_text())
            canonical = json.dumps(word, sort_keys=True, separators=(",", ":")).encode()
            need(hashlib.sha256(canonical).hexdigest() == expected["canonical_sha256"], name + " word hash")
            folder = Path(temporary) / name
            subprocess.run([sys.executable, "-I", "-B", str(exporter), str(word_path), str(folder)],
                           check=True, stdout=subprocess.DEVNULL)
            records = list(struct.iter_unpack("<6i", (folder / "249-records.bin").read_bytes()))
            n = 2 * word["v"] + word["R"]
            forward = matrix_bound(records, n, False)
            reverse = matrix_bound(records, n, True)
            bill = 64 * forward ** 3 * reverse ** 2
            need(forward == expected["bounds"]["forward"] and reverse == expected["bounds"]["reverse"],
                 name + " independent matrix bounds")
            need(str(bill) == expected["bounds"]["payload"], name + " payload")
            histogram = Counter()
            operations = Counter(r[0] for r in records)
            for op, _, _, _, rank, copy_rank in records:
                if op == 0 and rank:
                    histogram[rank] += 1
                elif op == 2:
                    histogram[copy_rank] += 1
            need(operations[1] == expected["complete_ADDs"], name + " literal ADD invoice")
            need(operations[2] == operations[3] == 9, name + " COPY/ERASE invoice")
            need(dict(histogram) == {1: 1320, 2: 1440, 4: 60, 5: 120, 8: 9}, name + " paid profile")
            result[name] = {"ADDs": operations[1], "forward": forward, "reverse": reverse,
                            "bits": bill.bit_length(), "paid_rank_mass": sum(r*c for r, c in histogram.items())}
        # A missing COPY must not silently price an uninitialized temporary.
        bad = list(records)
        bad.pop(next(i for i, r in enumerate(bad) if r[0] == 2))
        try:
            matrix_bound(bad, n, False)
        except ValueError:
            pass
        else:
            raise ValueError("missing COPY was accepted")
    print("RECORD_REPORT:" + json.dumps(result, sort_keys=True))
    print("PASS_R420_TRIPLE_LITERAL_RECORDS words=7 sparse_matrix_bounds=14 profiles=7 missing_COPY_rejected")


if __name__ == "__main__":
    main()
