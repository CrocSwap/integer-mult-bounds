"""Authenticated predecessor libraries and bounded common-cut contracts."""

import hashlib
import json
import runpy
from pathlib import Path
from types import SimpleNamespace

PACKAGE = Path(__file__).resolve().parent
GEOMETRY = "research/p112-simplex-coordinate-bound/vendor/geometry.py"
SOURCE_COMMIT = "f27442f87cf1fd86a50b8ba15615d8d655d06a85"
CALLER_COMMIT = "e8570c50f9591c9ca653a527ed9626aaa703c3bc"
RETAINED = {
    "vendor/pr3253-domain.py": "library",
    "vendor/pr3253-reference.py": "library",
    "vendor/pr3253-proof.md": "proof",
    "vendor/pr3253-witness.json": "witness",
    "vendor/pr3289-proof.md": "proof",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(name):
    path = PACKAGE / name
    require(path.stat().st_size <= 2_000_000, "JSON capacity")
    return json.loads(path.read_text())


def authenticate():
    manifest = read_json("RETAINED.json")
    require(type(manifest.get("schema_version")) is int, "retained schema type")
    require(manifest["schema_version"] == 1, "retained schema")
    rows = manifest.get("files")
    require(type(rows) is list and len(rows) == len(RETAINED), "retained inventory")
    require(all(type(row) is dict for row in rows), "retained row type")
    require({row.get("path") for row in rows} == set(RETAINED), "retained paths")
    for row in rows:
        require(row.get("usage") == RETAINED[row["path"]], "retained usage")
        require(
            set(row)
            == {"path", "usage", "source_commit", "source_path", "git_blob", "sha256"},
            "retained row schema",
        )
        caller = row["path"] == "vendor/pr3289-proof.md"
        require(
            row["source_commit"] == (CALLER_COMMIT if caller else SOURCE_COMMIT),
            "retained source commit",
        )
        names = {
            "domain.py": "domain.py",
            "reference.py": "reference.py",
            "proof.md": "PROOF.md",
            "witness.json": "WITNESS.json",
        }
        suffix = row["path"].split("-", 1)[1]
        original = (
            "research/p112-b6-t4-original-covers/PROOF.md"
            if caller
            else "research/p112-common-five-deletion/" + names[suffix]
        )
        require(row["source_path"] == original, "retained original path")
        data = (PACKAGE / row["path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == row["sha256"], "retained SHA256")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == row["git_blob"], "retained Git blob")
    sources = read_json("SOURCES.json")
    require(type(sources.get("schema_version")) is int, "source schema type")
    require(sources["schema_version"] == 1, "source schema")
    pins = [row for row in sources["files"] if row.get("usage") == "input"]
    require(len(pins) == 1 and pins[0]["path"] == GEOMETRY, "live input inventory")
    source = PACKAGE.parents[1] / GEOMETRY
    require(
        hashlib.sha256(source.read_bytes()).hexdigest() == pins[0]["sha256"],
        "geometry SHA256",
    )
    return source


def libraries():
    geometry = authenticate()
    domain = SimpleNamespace(**runpy.run_path(str(PACKAGE / "vendor/pr3253-domain.py")))
    g = SimpleNamespace(**runpy.run_path(str(geometry)))
    return domain, g


def reference_library():
    authenticate()
    return SimpleNamespace(
        **runpy.run_path(str(PACKAGE / "vendor/pr3253-reference.py"))
    )


def expected_result():
    result = read_json("RESULT.json")
    require(type(result.get("schema_version")) is int, "result schema type")
    require(result["schema_version"] == 1, "result schema")
    require(type(result.get("common_cut_budget")) is int, "cut budget type")
    require(result["common_cut_budget"] == 6, "cut budget")
    require(
        len(result["classes"]) == len(result["representative_masks"]) == 121,
        "class inventory",
    )
    require(result["complete_cut_records"] == 230, "completion count")
    return result


def common_unions(entries, budget=6):
    require(type(budget) is int and 0 <= budget <= 6, "union budget")
    require(len(entries) <= 2048, "completion capacity")
    cuts = set()
    for h, k, raw in entries:
        require(type(h) is int and 0 <= h < 1200, "direction index")
        require(type(k) is int and 0 <= k < 43435, "flat index")
        require(type(raw) is str and raw.isdecimal(), "cut encoding")
        cut = int(raw)
        require(0 <= cut < 1 << 112 and cut.bit_count() <= 6, "cut bounds")
        cuts.add(cut)
    states = {0}
    for cut in sorted(cuts):
        states.update(
            old | cut for old in tuple(states) if (old | cut).bit_count() <= budget
        )
        require(len(states) <= 65536, "common-union capacity")
    return states


def direction_bound(classes, bound=3):
    require(type(bound) is int and 0 <= bound <= 3, "direction bound")
    maximum, largest_states = 0, 0
    histogram = {}
    for _, entries in classes:
        states = common_unions(entries)
        largest_states = max(largest_states, len(states))
        local = 0
        for state in states:
            qualifying = {h for h, _, cut in entries if int(cut) & ~state == 0}
            require(len(qualifying) <= bound, "common-six direction bound failed")
            local = max(local, len(qualifying))
        maximum = max(maximum, local)
        histogram[str(local)] = histogram.get(str(local), 0) + 1
    require(maximum == bound, "direction bound not attained")
    return {
        "maximum_projective_directions": maximum,
        "max_union_states": largest_states,
        "class_maximum_histogram": dict(sorted(histogram.items())),
    }
