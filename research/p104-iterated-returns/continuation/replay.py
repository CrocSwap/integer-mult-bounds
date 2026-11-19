"""Verify the continued rational returns from their public e40b predecessor."""
import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
sys.path.insert(0, str(PACKAGE))
from prepare_sources import sources


def need(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if data.startswith(b"\x1f\x8b") else data)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(script, *arguments):
    subprocess.run([sys.executable, "-IB", str(script), *map(str, arguments)], check=True)


def pair(path):
    return (path / "WORD.json.gz", path / "LAYOUT.json.gz")


def checked_receipt(out, filename, claim):
    expected = HERE / "evidence" / filename
    need(digest(expected.read_bytes()) == claim["receipts"][filename], f"published digest for {filename}")
    need(read(out) == read(expected), f"replayed evidence for {filename}")


def make_parent(cache, out):
    run(cache / "parent/verify.py", "--cache", cache, "--out", out, "--part", "construction")
    return pair(out / "free")


def finite(cache, source, pins, out):
    run(HERE / "qualify.py", "--package", PACKAGE, "--cache", cache, "--word", source[0],
        "--layout", source[1], "--word-sha", pins["word_sha256"], "--layout-sha", pins["layout_sha256"],
        "--out", out)


def main(args):
    cache, out = args.cache.resolve(), args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    sources(cache)
    claim = read(HERE / "CLAIM.json")
    stage_file = HERE / "BIRTHS.json"
    need(digest(stage_file.read_bytes()) == claim["journal_sha256"], "source-bound birth journal")
    native, layout = pair(HERE)
    base = pair(PACKAGE / "complex")
    original_claim = read(cache / "parent/CLAIM.json")
    final, source = claim["candidate"], claim["source"]
    for path, expected in zip((native, layout, *base),
                              (final["word_sha256"], final["layout_sha256"],
                               source["word_sha256"], source["layout_sha256"]), strict=True):
        need(digest(json.dumps(read(path), sort_keys=True, separators=(",", ":")).encode()) == expected,
             f"canonical pin {path.name}")

    if args.part == "construction":
        sys.path.insert(0, str(PACKAGE / "complex"))
        from construction import rotated_splits, write_pair
        graph, owners, receipt = rotated_splits(cache, read(base[0]), read(base[1]), read(stage_file))
        need((graph, owners) == (read(native), read(layout)), "all constructed chart and scalar literals")
        write_pair(out, graph, owners)
        need(all(stage["controls"] for stage in receipt["continuation"]), "a negative control per independent target")
        result = out / "construction.json"
        result.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
        checked_receipt(result, result.name, claim)
    elif args.part == "operator":
        parent = make_parent(cache, out / "original")
        result = out / "operator.json"
        faults = [arg for entry in claim["controls"] for arg in ("--fault", entry)]
        run(PACKAGE / "complex/independent.py", "--cache", cache, "--base-graph", parent[0],
            "--base-layout", parent[1], "--control-word", base[0], "--control-layout", base[1],
            "--control-sha", source["word_sha256"], "--control-layout-sha", source["layout_sha256"],
            "--candidate", native, "--layout", layout, "--sha", final["word_sha256"],
            "--layout-sha", final["layout_sha256"], "--target", claim["target"],
            "--charts", "--scoped-faults", *faults, "--out", result)
        # Gzip metadata on the regenerated #7781 input is platform-dependent.
        # The checker has already verified the canonical graph and layout pins.
        expected = HERE / "evidence/operator.json"
        need(digest(expected.read_bytes()) == claim["receipts"][expected.name], "published operator receipt")
        a, b = read(result), read(expected)
        for item in (a, b):
            for key in ("word_file_sha256", "layout_file_sha256"):
                item["base"].pop(key, None)
        need(a == b, "independent operator, physical, dirty and negative controls")
    elif args.part == "comparators":
        original = make_parent(cache, out / "original")
        pins = dict(word_sha256=original_claim["complex_word"], layout_sha256=original_claim["layout"])
        for name, data, ref in (("7781", original, pins), ("e40b", base, source)):
            result = out / (name + ".json")
            finite(cache, data, ref, result)
            checked_receipt(result, result.name, claim)
    elif args.part == "audit":
        result = out / "audit.json"
        run(HERE / "audit_expanded.py", "--cache", cache, "--word", native, "--layout", layout,
            "--word-sha", final["word_sha256"], "--layout-sha", final["layout_sha256"],
            "--receipt", HERE / "evidence/application.json", "--binary-receipt", PACKAGE / "binary/INDEPENDENT.json",
            "--reference-application", PACKAGE / "evidence/application.json", "--out", result)
        checked_receipt(result, result.name, claim)
        grid = out / "common-grid.json"
        run(HERE / "common_grid.py", "--cache", cache, "--package", PACKAGE, "--receipts", HERE / "evidence", "--out", grid)
        checked_receipt(grid, grid.name, claim)
    elif args.part == "application":
        result = out / "application.json"
        finite(cache, (native, layout), final, result)
        checked_receipt(result, result.name, claim)
        app = read(result)["application"]
        need(app["claim"] == claim["finite_lower"] and app["bracket"] == claim["raw_bracket"],
             "finite admission and directed bracket")
        need(Fraction(app["claim"]) > Fraction(claim["source"]["raw_upper"]), "strict incremental gain")
        bound = Fraction(app["claim"])
        need(bound <= Fraction(claim["ordinary_binary_lower"]), "binary lower supports this common exponent")
        need((bound >= Fraction(claim["target"])) == claim["target_met"], "reported goal status")
    elif args.part.startswith("charts-"):
        result = out / "charts.json"
        run(PACKAGE / "application.py", "--cache", cache, "--word", native, "--layout", layout,
            "--binary-finite", PACKAGE / "binary/FINITE.json", "--word-sha", final["word_sha256"],
            "--layout-sha", final["layout_sha256"], "--binary-sha", claim["binary_word_sha256"],
            "--shard", args.part[-1], "--out", result)
        checked_receipt(result, args.part + ".json", claim)
    print("PASS", args.part, final["word_sha256"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", choices=("construction", "operator", "application", "comparators", "audit",
                                           "charts-0", "charts-1", "charts-2"), required=True)
    parser.add_argument("--cache", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
