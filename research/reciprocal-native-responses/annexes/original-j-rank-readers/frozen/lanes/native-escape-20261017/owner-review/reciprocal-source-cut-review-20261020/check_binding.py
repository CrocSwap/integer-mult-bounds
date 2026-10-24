"""Bind the final reader packet to the independent source-cut check."""

import argparse
from fractions import Fraction as F
import gzip
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PRODUCER = HERE.parents[1] / "reciprocal-reader-cuts-20261020"
PINS = {
    "SOURCE-CUTS.md": "0da0fb811c2c2841ac63b77ea678fa973000b79408cc2d4d825167d721bf5c02",
    "check_cuts.py": "b3c15399f56018680b93cc3254218ced032ea9f2dbcbd080814fa1a63f556d45",
    "bound-normal/CHECKS.json": "bf1722a6ee21a5c14f50db6b848972a4bbc9fc56ec69c301357103cdc02e6c9b",
    "bound-normal/READERS.json.gz": "f0a3eb19e09f425fc87e3563af72a7879f9cf64799fee0dcbd059bd297bc8045",
}


def need(test, name):
    if not test:
        raise ValueError(name)


def digest(data):
    return sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    manifest, objects = {}, {}
    for rel, expected in PINS.items():
        path = PRODUCER / rel
        stored = path.read_bytes()
        raw = gzip.decompress(stored) if path.suffix == ".gz" else stored
        need(digest(raw) == expected, "Final producer source " + rel)
        manifest[str(path)] = {"file_sha256": digest(stored), "content_sha256": expected}
        if ".json" in rel.lower():
            objects[path.name] = json.loads(raw)
    for name in ("CHECKS.json", "READERS.json.gz"):
        normal, optimized = [(PRODUCER / folder / name).read_bytes()
                             for folder in ("bound-normal", "bound-optimized")]
        need(normal == optimized, "Producer normal and optimized bytes " + name)
        manifest[str(PRODUCER / "bound-optimized" / name)] = manifest[str(PRODUCER / "bound-normal" / name)]
    for path in sorted((HERE / "final-normal").glob("*.json")):
        raw = path.read_bytes()
        other = HERE / "final-optimized" / path.name
        need(raw == other.read_bytes(), "Independent normal and optimized bytes " + path.name)
        manifest[str(path)] = manifest[str(other)] = {"file_sha256": digest(raw), "content_sha256": digest(raw)}
    independent = json.loads((HERE / "final-normal/CHECKS.json").read_text())
    need(independent["checker_sha256"] == digest((HERE / "check_review.py").read_bytes()),
         "Final independent checker bytes")
    body = json.loads((HERE / "final-normal/CONDITIONAL-READER.json").read_text())["events"]
    payload, receipt = objects["READERS.json.gz"], objects["CHECKS.json"]
    need(receipt["checker_sha256"] == PINS["check_cuts.py"], "Final producer checker binding")
    need(receipt["payload_decompressed_sha256"] == PINS["bound-normal/READERS.json.gz"], "Producer payload binding")
    for name, offset in (("FULL_X", 0), ("current_I_Y", 112)):
        expected = [[op, 640 + target - 112, source + offset, c] for op, target, source, c in body]
        program = payload["programs"][name]
        need(program["events"] == expected, "Every actual signed reader instruction " + name)
        inverse = [[op, target, source, str(-F(c))] for op, target, source, c in reversed(expected)]
        need(program["inverse_events"] == inverse, "Immediate inverse instruction order " + name)
        need(program["complex_ADDs"] == 136 and program["real_scalar_units"] == 1088,
             "Producer scalar invoice " + name)
    need([row["global_accumulator_frame"] for row in payload["cut_types"]] == ["F9", "F9 q_anchor", "F25"],
         "All three serialized accumulator types")
    need([row["reader"] for row in payload["cut_types"]] ==
         ["c0=ell0 x", "c1=ell1 P0 t", "c2=ell2 (P1 P0) w"], "All three serialized ordered queries")
    need(receipt["reader_nonzeros"] == 136 and receipt["reader_source_port_support"] == 96 and
         receipt["reader_coefficients"] == {"-1": 90, "1": 46}, "Exact serialized reader counts")
    need(not receipt["native_word_replayed_here"] and not receipt["record_retention_or_restoration_claimed"]
         and not receipt["complete_supplier_claimed"], "Explicit scope boundaries")
    need(receipt["phase_counts"] == {"FULL_exit": 224, "FULL_source_entry": 224, "hole_target_entry": 224},
         "Producer phase coverage")
    report = {"status": "PASS_FINAL_RECIPROCAL_READER_BINDING", "material_findings": [],
              "producer_normal_optimized_byte_identical": True,
              "independent_normal_optimized_byte_identical": True,
              "exact_reader_instructions_checked": 272, "exact_immediate_inverse_instructions_checked": 272,
              "ordered_queries_checked": 3, "accumulator_types_checked": 3,
              "producer_checker_imported_or_executed": False,
              "native_word_or_record_retention_replayed": False}
    for name, value in (("SOURCE-MANIFEST.json", manifest), ("CHECKS.json", report)):
        (args.out / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
