"""Check the signed BIT bill and replay both one-chart separation engines."""
from argparse import ArgumentParser
from collections import Counter
import gzip
from hashlib import sha1, sha256
import json
from pathlib import Path
import runpy
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
BIT = "research/paired-query-only-bit/"
FILES = {
    BIT + "retained/inputs/BIT-NATIVE-WORD.json.gz": "WORD.json.gz",
    BIT + "EFREE-RESULT.json": "INVOICE.json",
}


def keyed(items):
    result = dict(items)
    assert len(result) == len(items), "duplicate JSON key"
    return result


def read_json(raw):
    return json.loads(raw, object_pairs_hook=keyed)


def source_index(rows):
    pins = {row["path"]: row for row in rows}
    assert len(pins) == len(rows), "duplicate source path"
    return pins


def reject(fn, value):
    try:
        fn(value)
    except AssertionError:
        return
    raise AssertionError("duplicate control accepted")


def run(root):
    reject(read_json, b'{"a":1,"a":2}')
    reject(source_index, [{"path": "same"}, {"path": "same"}])
    pins = source_index(read_json((HERE / "SOURCES.json").read_bytes())["files"])
    assert set(FILES) == {key for key, pin in pins.items() if pin["usage"] == "input"}
    for key, digest in read_json((HERE / "LOCAL-PINS.json").read_bytes()).items():
        assert sha256((HERE / key).read_bytes()).hexdigest() == digest, key
    with TemporaryDirectory(prefix="bit-donor-replay-") as scratch:
        temp = Path(scratch)
        deps = temp / "deps"
        inputs = deps / "inputs"
        inputs.mkdir(parents=True)
        inputs_data = {}
        for key, filename in FILES.items():
            raw = (root / key).read_bytes()
            pin = pins[key]
            assert sha256(raw).hexdigest() == pin["sha256"], ("changed input", key)
            assert sha1(f"blob {len(raw)}\0".encode() + raw).hexdigest() == pin["git_blob"], key
            inputs_data[filename] = read_json(gzip.decompress(raw) if filename.endswith(".gz") else raw)
            (inputs / filename).write_bytes(raw)
        shutil.copyfile(HERE / "price.py", deps / "price.py")
        word = inputs_data["WORD.json.gz"]
        invoice = inputs_data["INVOICE.json"]
        price = runpy.run_path(str(HERE / "price.py"))
        moves, _, _ = price["walk"](word)
        ranks = {int(key): frame["dim"] for key, frame in word["frames"].items()}
        native = Counter(abs(ranks[src] - ranks[dst]) for src, dst, _ in moves.values())
        _, copies = price["profile"](invoice, native, word, ranks)
        assert copies == 36

        screen = runpy.run_path(str(HERE / "screen.py"))
        out = temp / "result"
        out.mkdir()
        screen["run"](deps, out, screen["time"].monotonic())
        expected_price = read_json((HERE / "PRICE.json").read_bytes())
        actual_price = read_json((out / "PRICE.json").read_bytes())
        assert actual_price == expected_price
        stock = read_json((out / "STOCK.json").read_bytes())
        stock.pop("elapsed_seconds")
        assert stock == read_json((HERE / "STOCK.json").read_bytes())
        dual = subprocess.run(
            [sys.executable, "-E", "-B", str(HERE / "check_stock.py"),
             "--deps", str(deps), "--receipt", str(out / "STOCK.json")],
            check=True, capture_output=True, text=True,
        )
        report = read_json(dual.stdout.splitlines()[0])
        assert report["dual_systems_consistent"] == stock["all_chart_pairs"] == 22190
        return {
            **report, "scope_exhausted": stock["scope_exhausted"],
            "unresolved_sites": stock["unresolved_sites"],
            "savings_upper_whole": stock["optimistic_saving_upper_whole"],
            "shortfall_remaining_lower": stock["shortfall_remaining_lower"],
            "kappa_gain": "0",
        }


if __name__ == "__main__":
    assert __debug__, "run with assertions enabled"
    p = ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path.cwd())
    print(json.dumps(run(p.parse_args().root), sort_keys=True))
