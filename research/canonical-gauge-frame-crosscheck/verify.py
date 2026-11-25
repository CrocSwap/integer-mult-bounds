#!/usr/bin/env python3
"""Independently check whether the omitted gauge annihilator is caught elsewhere."""

import gzip
import hashlib
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/paired-cube-bit-fast/paired_cube_bit_word.py"
EXPECTED_SOURCE_SHA256 = "e1019ecd3a4ff328aa494ed0ba7470ba85061e90b89ad9b170023f1f1685845f"
MARKER = "PASS_CANONICAL_GAUGE_FRAME_CROSSCHECK omitted_word_field=true companion_frame_detects=true"


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL_CANONICAL_GAUGE_FRAME_CROSSCHECK " + message)


def load_pinned_producer():
    raw = SOURCE.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_SOURCE_SHA256, "producer source hash changed")
    source = raw.decode("utf-8")

    # Bind the test to the exact path exercised: the public word drops private
    # keys, the companion exporter consumes _gauge_ann, and --check visits all
    # emitted files (including frames_p*.json).
    for needle, label in (
        ("word={k: v for k, v in word.items() if not k.startswith('_')}", "canonical word filter"),
        ("for z, A in zip(word['gauges'], word['_gauge_ann']):", "companion gauge export"),
        ("for k, obj in exp.items():", "all companion outputs are named"),
        ("names['%s_p%d.json' % (k, a.p)] = dumps(obj).encode()", "companion output filenames"),
        ("for name, data in names.items():", "all named outputs are checked"),
        ("require(old == data, 'byte-identical regeneration of ' + name)", "exact output comparison"),
    ):
        require(needle in source, label + " moved")

    spec = importlib.util.spec_from_file_location("pinned_paired_cube_bit_word", SOURCE)
    require(spec is not None and spec.loader is not None, "cannot load pinned producer")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def canonical_gzip(module, word):
    public = {key: value for key, value in word.items() if not key.startswith("_")}
    output = {"graph": {}, "compile": {}, "word": public}
    return gzip.compress(module.dumps(output).encode("utf-8"), mtime=0)


def export_fixture(module, geo, word):
    # A minimal exact geometry. The producer's actual export() and
    # frame_record() functions serialize the two distinct annihilator spaces.
    graph = {"h": 2, "v": 0, "labels": [], "args": [], "roots": [], "partner_mix": []}
    witness = {
        "geo": geo,
        "n": 0,
        "roots": [],
        "ann": [],
        "order": [],
        "rann": [],
        "arcs": {},
        "usecode": [],
        "plain": [],
    }
    return module.export(1, graph, {}, witness, word, {})


def generator_compares_equal(name, old, new):
    # Mirrors the pinned --check payload rule for gzip and exact byte rule for
    # the plain-JSON companion files.
    if name.endswith(".gz"):
        old, new = gzip.decompress(old), gzip.decompress(new)
    return old == new


def evaluate():
    module = load_pinned_producer()
    geo = module.Geometry(2, [])
    ann_x = geo.T.intern([[1, 0]])
    ann_y = geo.T.intern([[0, 1]])
    require(ann_x != ann_y, "fixture annihilator spaces collapsed")
    require(module.frame_record(geo, ann_x) != module.frame_record(geo, ann_y), "exact frames collapsed")

    public = {
        "ops": [],
        "sources": {},
        "rootroles": [],
        "phase1": [],
        "gauges": [{"role": 1, "first": 0, "targets": [0], "dim": 1}],
    }
    word_x = dict(public, _gauge_ann=[ann_x])
    word_y = dict(public, _gauge_ann=[ann_y])

    # The selected canonical gzip comparison does accept the field mutation.
    gzip_x = canonical_gzip(module, word_x)
    gzip_y = canonical_gzip(module, word_y)
    require(gzip.decompress(gzip_x) == gzip.decompress(gzip_y), "private field reached word payload")

    # The producer's actual companion export retains the exact frame value.
    export_x = export_fixture(module, geo, word_x)
    export_y = export_fixture(module, geo, word_y)
    require(export_x["word"]["gauges"] != export_y["word"]["gauges"], "exported gauge frame id was omitted")
    require(export_x["frames"] != export_y["frames"], "exact companion frame file accepted the mutation")
    frames_x = module.dumps(export_x["frames"]).encode("utf-8")
    frames_y = module.dumps(export_y["frames"]).encode("utf-8")
    require(frames_x != frames_y, "serialized frame receipt did not change")

    # The normal --check path compares every emitted JSON file byte-for-byte;
    # this companion file therefore rejects the same mutation the word payload
    # alone accepts.
    files_x = {"word_p1.json.gz": gzip_x}
    files_y = {"word_p1.json.gz": gzip_y}
    for name in export_x:
        path = name + "_p1.json"
        files_x[path] = module.dumps(export_x[name]).encode("utf-8")
        files_y[path] = module.dumps(export_y[name]).encode("utf-8")
    require(generator_compares_equal("word_p1.json.gz", files_x["word_p1.json.gz"],
                                     files_y["word_p1.json.gz"]), "gzip payload control")
    require(not generator_compares_equal("frames_p1.json", files_x["frames_p1.json"],
                                         files_y["frames_p1.json"]),
            "complete output comparison accepted the companion frame mutation")
    require(any(not generator_compares_equal(name, files_x[name], files_y[name]) for name in files_x),
            "complete output bundle missed the mutation")

    changed_public = dict(public)
    changed_public["gauges"] = [{"role": 1, "first": 0, "targets": [0], "dim": 2}]
    require(gzip.decompress(gzip_x) != gzip.decompress(canonical_gzip(module, changed_public)),
            "positive control: public field was ignored")

    return {
        "annihilator_ids": [ann_x, ann_y],
        "word_payload_equal": True,
        "exported_gauge_frames_differ": True,
        "exact_frame_receipts_differ": True,
        "complete_check_rejects_mutation": True,
        "public_field_control_detected": True,
        "p12_rebuilt": False,
    }


def main():
    result = evaluate()
    require(result["word_payload_equal"] and result["exact_frame_receipts_differ"], "result state")
    print(MARKER)
    print("RESULT " + repr(result))


if __name__ == "__main__":
    main()
