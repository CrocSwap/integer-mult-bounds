#!/usr/bin/env python3
"""Verify the R420 block-4 circuit, bounded search receipt, and exact endpoint."""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE = "bce54fb3f895cbe5cd4c0eb477c3afeed100190f"
SOURCE_WORD = ROOT / "research/e8-bit-r420/data/bitE8mut-r420.json.gz"
WORD = HERE / "candidate-word.json.gz"
CERT = HERE / "search-certificate.json"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def read_word(path: Path) -> dict:
    with gzip.open(path, "rt") as source:
        return json.load(source)


def frame_paths(word: dict) -> list[list[int]]:
    paths = [[frame] for frame in word["start"]]
    for phase in ("D", "A", "B", "C"):
        for frame, destination, sources in word[phase]:
            for register in [destination] + sources:
                if paths[register][-1] != frame:
                    paths[register].append(frame)
    for register, frame in enumerate(word["final"]):
        if paths[register][-1] != frame:
            paths[register].append(frame)
    return paths


def additions(word: dict) -> int:
    return sum(
        len(sources)
        for phase in ("D", "A", "B", "C")
        for _, _, sources in word[phase]
    ) + sum(len(row) for row in word["scatter"])


def pin_sources() -> None:
    pins = json.loads((HERE / "SOURCES.json").read_text())
    require(pins["base_commit"] == BASE, "wrong pinned base")
    for relative, pin in pins["files"].items():
        data = (ROOT / relative).read_bytes()
        require(hashlib.sha256(data).hexdigest() == pin["sha256"], f"SHA256 mismatch: {relative}")
        blob = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", f"{BASE}:{relative}"], text=True
        ).strip()
        require(blob == pin["git_blob"], f"Git blob mismatch at base: {relative}")


def load_search_module():
    spec = importlib.util.spec_from_file_location("r420_block4_search", HERE / "search.py")
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load search.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run() -> dict:
    pin_sources()
    certificate = json.loads(CERT.read_text())
    candidate = read_word(WORD)
    source = read_word(SOURCE_WORD)

    search = load_search_module()
    generated, generated_certificate = search.generate()
    require(canonical(generated) == canonical(candidate), "checked-in word differs from deterministic search")
    require(generated_certificate == certificate, "search certificate differs from deterministic search")
    require(hashlib.sha256(canonical(source)).hexdigest() == certificate["baseline"]["canonical_word_sha256"],
            "source R420 word differs from the pinned baseline")
    require(hashlib.sha256(canonical(candidate)).hexdigest() == certificate["candidate"]["canonical_word_sha256"],
            "candidate word hash mismatch")

    start, stop = certificate["object"]["baseline_B_interval"]
    replacement_len = certificate["object"]["candidate_operations"]
    frame = certificate["object"]["frame"]
    wires = certificate["object"]["input_wires"]
    require(len(source["B"][start:stop]) == 58 and replacement_len == 51, "wrong local circuit lengths")
    require(all(gate[0] == frame for gate in source["B"][start:stop]), "baseline block frame changed")
    require(all(gate[0] == frame for gate in candidate["B"][start:start + replacement_len]),
            "candidate block frame changed")
    expected_operations = [
        [frame, wires[destination], [wires[source_register]]]
        for destination, source_register in certificate["candidate"]["operations_local"]
    ]
    require(candidate["B"][start:start + replacement_len] == expected_operations,
            "physical block differs from the exact local operation certificate")
    require(all(source[key] == candidate[key] for key in source if key not in ("B", "C")),
            "a field outside the regenerated B/C schedule changed")

    full = next(i for i, basis in enumerate(candidate["frames"]) if len(basis) == candidate["v"])
    expected_cleanup = [
        [full, destination, sources[:]]
        for _, destination, sources in (candidate["A"] + candidate["B"])[::-1]
        if not candidate["v"] <= destination < 2 * candidate["v"]
    ]
    require(candidate["C"] == expected_cleanup, "cleanup is not the literal reverse of all source/helper writes")

    original_paths, candidate_paths = frame_paths(source), frame_paths(candidate)
    changed_paths = [
        {"register": i, "before": before, "after": after}
        for i, (before, after) in enumerate(zip(original_paths, candidate_paths))
        if before != after
    ]
    require(len(changed_paths) == 7, f"unexpected changed register-route count: {len(changed_paths)}")
    old_additions, new_additions = additions(source), additions(candidate)
    require((old_additions, new_additions) == (26916, 26902), "wrong complete local scalar-ADD invoice")
    require((len(source["B"]), len(candidate["B"])) == (837, 830), "wrong complete phase-B gate count")
    require((len(source["C"]), len(candidate["C"])) == (2661, 2654), "wrong complete cleanup gate count")

    with tempfile.TemporaryDirectory(prefix="r420-block4-check-") as scratch:
        scratch_path = Path(scratch)
        candidate_path = scratch_path / "candidate-word.json.gz"
        candidate_path.write_bytes(WORD.read_bytes())
        xcheck = ROOT / "research/e8-bit-r420/code/xcheck.py"
        mutants = ROOT / "research/e8-bit-r420/code/mutants.py"
        xreport = scratch_path / "xcheck.json"
        mreport = scratch_path / "mutants.json"
        subprocess.run(
            [sys.executable, "-I", "-B", str(xcheck), str(candidate_path), "--json", str(xreport)],
            cwd=ROOT, check=True,
        )
        subprocess.run(
            [sys.executable, "-I", "-B", str(mutants), str(xcheck), str(candidate_path), "--json", str(mreport)],
            cwd=ROOT, check=True,
        )
        xresult = json.loads(xreport.read_text())
        mresult = json.loads(mreport.read_text())
        require(all(xresult["hypotheses"].values()) and all(xresult["conclusion"].values()),
                "an H1-H5 hypothesis or interface conclusion failed")
        require(mresult.get("status", "").startswith("PASS"), "mutation controls did not pass")

    return {
        "status": "PASS_R420_BLOCK4_RESYNTHESIS",
        "base_commit": BASE,
        "assignment_seed": 4,
        "candidate_word_sha256": certificate["candidate"]["canonical_word_sha256"],
        "block4": {"frame": frame, "operations": [58, 51]},
        "local_additions": [old_additions, new_additions],
        "literal_cleanup_gates": [len(source["C"]), len(candidate["C"])],
        "changed_register_routes": changed_paths,
        "h1_h5_and_interface": "PASS on all 660 source, target, and helper-dirt columns",
        "mutation_controls": "PASS; see mutants.py replay output",
        "kappa_claim": None,
    }


if __name__ == "__main__":
    if sys.flags.optimize:
        raise SystemExit("Run without -O; the inherited xcheck uses assertions")
    result = run()
    print("PASS_R420_BLOCK4_RESYNTHESIS baseline=58 candidate=51 local_ADDs=26916->26902 routes_changed=7")
    print("CANDIDATE_SHA256", result["candidate_word_sha256"])
