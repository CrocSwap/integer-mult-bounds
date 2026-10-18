# SPDX-License-Identifier: Apache-2.0
"""Replay the pinned selected exporter, including its reused correlated temp661."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EXPORTER = "research/e8-bit-carrier-skeleton/code/bit/export_records.py"
WORD = "research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
PINS = {EXPORTER: "8a5999601f917dbb492bb9ae9a344611f18cc7cedc53dc3c76496a369e530eb3",
        WORD: "e3e301e62bc2b41dbf1ceac0acf3d35824ebeab1848c5a2142d4577b109da52f"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def replay(records, word):
    n, v = 2 * word["v"] + word["R"], word["v"]
    values = {r: 1 << r for r in range(n)}
    frames = dict(enumerate(word["start"]))
    live, lifetimes = {}, []
    b_adds = 0
    cut = None
    for index, record in enumerate(records):
        op, x, y, z, f, phase = record
        if op == 0:
            require(frames.get(x) == y, "MOVE source frame")
            frames[x] = z
        elif op == 1:
            require(x in values and y in values, "ADD missing role or erased copy")
            require(frames[x] == f and frames[y] == f, "literal common frame")
            values[x] ^= values[y]
            if phase == 4:
                b_adds += 1
                if b_adds == 10:
                    require(not live and len(values) == n, "correlated temp live at cut10")
                    cut = dict(values)
                    cut_record = index
        elif op == 2:
            require(y not in values and y not in live, "COPY overwrites live correlated role")
            require(frames[x] == z and f == 0, "COPY source/temporary frames")
            values[y], frames[y] = values[x], f
            life = {"source": x, "temporary": y, "source_frame": z, "temporary_frame": f,
                    "paid_rank": phase, "copy_record": index, "original_u465_coefficient": (values[x] >> 465) & 1}
            live[y] = (life, values[y])
        elif op == 3:
            require(y in live and values[y] == values[x], "ERASE correlated value mismatch")
            life, snapshot = live.pop(y)
            life["erase_record"] = index
            lifetimes.append((life, snapshot))
            del values[y]
            del frames[y]
        else:
            raise ValueError("unknown record opcode")
    require(cut is not None and not live and len(lifetimes) == 9, "literal coverage")
    for life, snapshot in lifetimes:
        # B[0:10] only writes targets: each retained source is exactly its
        # independent ordinary cut coordinate, not a new independent copy.
        require(snapshot == cut[life["source"]], "retained source changed before cut")
        life["cut_coordinate_support"] = [life["source"]]
        life["cut_coordinate465_coefficient"] = int(life["source"] == 465)
        require(life["erase_record"] < cut_record, "late ERASE")
    for r in range(n):
        expected = (1 << r) ^ ((1 << (r - v)) if v <= r < 2 * v else 0)
        require(values[r] == expected and frames[r] == word["final"][r], "literal baseline endpoint")
    return {"schema_version": 1, "record_count": len(records), "ordinary_columns": n,
            "cut_after_B_adds": 10, "cut_record": cut_record, "live_temporaries_at_cut": [],
            "copy_lifetimes": [life for life, _ in lifetimes],
            "note": "No native checker run: exact exported scalar records and explicit frame IDs only."}


def compute(root=ROOT):
    for path, pin in PINS.items():
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == pin, "literal source hash")
    word = json.loads(gzip.decompress((root / WORD).read_bytes()))
    with tempfile.TemporaryDirectory(prefix="r439-copy-cut-") as work:
        completed = subprocess.run([sys.executable, "-I", "-B", str(root / EXPORTER), str(root / WORD), work],
                                   check=True, capture_output=True, text=True, timeout=120)
        data = (Path(work) / "249-records.bin").read_bytes()
    require(len(data) % 24 == 0, "record width")
    records = list(struct.iter_unpack("<6i", data))
    result = replay(records, word)
    result["exporter_stdout"] = completed.stdout.strip()
    result["records_sha256"] = hashlib.sha256(data).hexdigest()
    controls = []
    first_erase = next(i for i, record in enumerate(records) if record[0] == 3)
    for label, bad in (("omitted_ERASE", records[:first_erase] + records[first_erase + 1:]),
                       ("COPY_before_ERASE", records[:first_erase] + [records[next(i for i, r in enumerate(records) if i > first_erase and r[0] == 2)]] + records[first_erase:])):
        try:
            replay(bad, word)
        except ValueError:
            controls.append(label)
        else:
            raise ValueError("lifecycle control accepted: " + label)
    result["negative_controls"] = controls
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true")
    args = parser.parse_args()
    result = compute()
    if args.emit:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        require(result == json.loads((HERE / "COPY-LIFECYCLE.json").read_text()), "lifecycle receipt mismatch")
        print("PASS_R439_LITERAL_COPY_CUT copies=9 reused_temp=661 live_at_B10=0 controls=2 records=27234")


if __name__ == "__main__":
    main()
