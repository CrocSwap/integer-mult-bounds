"""Behavioral controls for transport, strict sources and occupancy."""

import copy
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

from audit import barriers, corrections, cover_row, require, row_placement
from sources import PACKAGE, SOURCE_HASH, load, manifest, pinned_bytes


def rejects(function, text):
    try:
        function()
    except ValueError as error:
        require(text in str(error), "expected diagnostic: " + str(error))
    else:
        raise ValueError("control was accepted: " + text)


def row_controls():
    # Hosting at the same global time precedes that owner's local stage.
    order = [(0, 0), (1, 0), (2, 0)]
    times = [[0, 1, 2]]
    tags = {(0, 0): "A", (1, 0): "A", (2, 0): "A"}
    providers = {"A": {"widths": [1]}}
    starts, intervals = {0: 2, 1: 5, 2: 8}, {0: (1, 4, 0)}
    plan = {"pairs": {"0": 0}, "sides": {"0": 0}}
    prepared = order, times, tags, providers, starts, intervals, [[3]], plan
    require(
        row_placement([0, 0, 0, 0, 0, 0], prepared) == (0, 0, 0, 0, 1),
        "read-before-local same-time positive control",
    )
    rejects(lambda: row_placement([1, 0, 0, 0, 0, 0], prepared), "barrier")
    changed = copy.deepcopy(prepared)
    changed[5][0] = (2, 4, 0)
    rejects(lambda: row_placement([0, 0, 0, 0, 0, 0], changed), "barrier")
    changed = copy.deepcopy(prepared)
    changed[7]["sides"]["0"] = 1
    rejects(lambda: row_placement([0, 0, 0, 0, 0, 0], changed), "physical stream")
    rejects(lambda: row_placement([True, 0, 0, 0, 0, 0], prepared), "integer row")


def occupancy_controls():
    masks, counts, histogram = [0] * 20, [0], Counter()
    cover_row((0, 0, 0, 1, 2), masks, counts, histogram)
    rejects(lambda: cover_row((0, 0, 0, 2, 1), masks, counts, histogram), "overlapping")
    require(masks[0] == 6 and counts == [1], "failure does not mutate occupancy")


def source_controls(data):
    with tempfile.TemporaryDirectory(prefix="t740-transport-controls-") as directory:
        private = Path(directory)
        raw = (PACKAGE / "SOURCES.json").read_bytes()
        mutant = json.loads(raw)
        mutant["schema_version"] = True
        path = private / "manifest.json"
        path.write_text(json.dumps(mutant))
        rejects(lambda: manifest(path, SOURCE_HASH), "fixed manifest")
        for mutation in ("usage", "inventory"):
            mutant = json.loads(raw)
            if mutation == "usage":
                mutant["files"][0]["usage"] = "input"
            else:
                mutant["files"].append(mutant["files"][0])
            path.write_text(json.dumps(mutant))
            rejects(lambda: manifest(path, SOURCE_HASH), "fixed manifest")
        pin = json.loads(raw)["files"][0]
        path.write_bytes(b"private corrupt source")
        rejects(lambda: pinned_bytes(path, pin), "source SHA256")
    changed = copy.deepcopy(data["journal"])
    changed["edits"][0][1][0] += 1
    rejects(lambda: corrections(data["base"]["rows"], changed), "preimage")


def barrier_control(template):
    starts, old = barriers(template)
    target = next(
        child
        for child, (previous, stop, _) in old.items()
        if any(previous < start <= stop for start in starts.values())
    )
    mutated = copy.deepcopy(template)
    stop, stream = old[target][1:]
    # A new bridge immediately before insertion must block the preceding cut.
    mutated["execution_schedule"].insert(
        stop, {"kind": "bridge", "src": stream // 2, "dst": (stream // 2 + 1) % 4}
    )
    _, new = barriers(mutated)
    require(
        new[target][0] == stop, "bridge source and destination both count as touched"
    )


def process_control():
    with tempfile.TemporaryDirectory(prefix="t740-private-verifier-") as directory:
        private = Path(directory)
        for name in ("verify.py", "audit.py", "sources.py"):
            (private / name).write_bytes((PACKAGE / name).read_bytes())
        (private / "SOURCES.json").write_bytes(b'{"schema_version":true}\n')
        result = subprocess.run(
            [sys.executable, "-W", "error", "-O", "-B", str(private / "verify.py")],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        require(
            result.returncode != 0 and "fixed manifest bytes" in result.stderr,
            "actual verifier rejects private corrupt source contract",
        )


def main():
    data = load()
    row_controls()
    occupancy_controls()
    source_controls(data)
    barrier_control(data["template"])
    process_control()
    print("PASS_T740_TRANSPORT_CONTROLS groups=5 optimized_safe=true")


if __name__ == "__main__":
    main()
