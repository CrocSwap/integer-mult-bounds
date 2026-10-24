"""Replay the packaged exact checks in a new output directory."""

from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time


PACKAGE = Path(__file__).resolve().parent


def require(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    require(output != PACKAGE and PACKAGE not in output.parents,
            "The output directory must be outside the package")
    require(not output.exists(), "Use a new output directory")
    require(shutil.disk_usage(output.parent).free >= 3 * 1024**3,
            "At least 3 GiB of free disk space is required")
    import sympy
    manifest = load(PACKAGE / "SOURCE-MANIFEST.json")
    for entry in manifest["files"]:
        require(sha(PACKAGE / entry["path"]) == entry["sha256"],
                "A source hash differs: " + entry["path"])
    output.mkdir()
    work = output / "work"
    shutil.copytree(PACKAGE / "payload", work)
    lanes = work / "lanes"
    frozen = PACKAGE / "payload/lanes"
    report = {
        "status": "RUNNING",
        "python": sys.version,
        "sympy": sympy.__version__,
        "source_manifest_sha256": sha(PACKAGE / "SOURCE-MANIFEST.json"),
        "replay_sha256": sha(Path(__file__)),
        "source_files_checked": len(manifest["files"]),
        "checks": [],
        "omitted": [
            "The optional sixth-moment extension of the cover theorem",
            "Search and LP routines used to find cut certificates",
            "A new native-phase sweep or complete supplier replay",
            "An application to the 22 October 2026 selected frontier",
        ],
    }
    env = dict(os.environ)
    env.update(OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1",
               VECLIB_MAXIMUM_THREADS="1", NUMEXPR_NUM_THREADS="1", PYTHONDONTWRITEBYTECODE="1")
    provenance_changes = []

    def expected(relative, updates=None):
        result = load(frozen / relative)
        for key, value in (updates or {}).items():
            provenance_changes.append({"receipt": relative, "field": key,
                                       "historical": result[key], "portable": value})
            result[key] = value
        return result

    cases = []
    binding = load(frozen / "temporal-reuse/SPECTRAL-BOUND-REVIEW.json")["source_reconstruction"]
    binding["status"] = "PASS_REVERSE_SOURCE_MATRIX_BINDING"
    cases.append(("source-matrix", "temporal-reuse/check_source_matrix.py", [],
                  "temporal-reuse/SOURCE-MATRIX-BINDING.json", binding))
    cases.append(("fourth-moment", "temporal-reuse/check_query_fourth_moment.py", [],
                  "temporal-reuse/QUERY-FOURTH-MOMENT.json", expected("temporal-reuse/QUERY-FOURTH-MOMENT.json")))
    cases.append(("fifth-moment", "temporal-reuse/check_query_fifth_moment.py", [],
                  "temporal-reuse/QUERY-FIFTH-MOMENT.json", expected("temporal-reuse/QUERY-FIFTH-MOMENT.json")))
    moment_pins = {name: sha(frozen / "temporal-reuse" / name) for name in
                   ("QUERY-MOMENTS.md", "check_query_fourth_moment.py", "QUERY-FOURTH-MOMENT.json",
                    "check_query_fifth_moment.py", "QUERY-FIFTH-MOMENT.json")}
    cases.append(("moment-review", "cover-algebra/review_query_moments.py", [],
                  "cover-algebra/QUERY-MOMENTS-REVIEW.json",
                  expected("cover-algebra/QUERY-MOMENTS-REVIEW.json", {
                      "source_pins": moment_pins,
                      "checker_sha256": sha(frozen / "cover-algebra/review_query_moments.py")})))
    cases.append(("complete-snapshot-rows", "circuit-interface/snapshot-audit/review_snapshot_rows.py", [],
                  "circuit-interface/snapshot-audit/SNAPSHOT-ROWS-REVIEW.json",
                  expected("circuit-interface/snapshot-audit/SNAPSHOT-ROWS-REVIEW.json", {
                      "reviewer_sha256": sha(frozen / "circuit-interface/snapshot-audit/review_snapshot_rows.py")})))
    for name, script, receipt in [
        ("snapshot-cones", "history-encoding/check_snapshot_cone_obstruction.py", "history-encoding/SNAPSHOT-CONE-OBSTRUCTION.json"),
        ("snapshot-support-review", "cover-algebra/review_snapshot_support.py", "cover-algebra/SNAPSHOT-SUPPORT-REVIEW.json"),
        ("support-distance", "history-encoding/check_query_support_distance.py", "history-encoding/QUERY-SUPPORT-DISTANCE.json"),
        ("support-distance-review", "cover-algebra/review_query_support_distance.py", "cover-algebra/QUERY-SUPPORT-DISTANCE-REVIEW.json"),
        ("global-cut-42", "cover-algebra/check_snapshot_flag_cut.py", "cover-algebra/SNAPSHOT-FLAG-CUT.json"),
        ("global-cut-42-review", "history-encoding/review_snapshot_flag_cut.py", "history-encoding/SNAPSHOT-FLAG-CUT-REVIEW.json"),
        ("rank5-cuts-review", "cover-algebra/review_rank5_union_cuts.py", "cover-algebra/RANK5-UNION-CUTS-REVIEW.json"),
        ("rank8-cuts-review", "cover-algebra/review_movable_rank8_cuts.py", "cover-algebra/MOVABLE-RANK8-CUTS-REVIEW.json"),
    ]:
        cases.append((name, script, [], receipt, expected(receipt)))
    algebra = expected("cover-algebra/ALGEBRA.json")
    for key in ("normalized_trace_P0_P1_cubed", "sixth_moment_calculation",
                "common_range_dimension_upper_bound_from_third_moment",
                "equal_J_subspace_codimension_lower_bound_from_third_moment",
                "isoclinic_braid_third_moment_required"):
        del algebra[key]
    cases.append(("cover-algebra", "cover-algebra/verify_algebra.py",
                  ["--interface", "{lanes}/circuit-interface/INTERFACE.json", "--out", "{lanes}/cover-algebra/ALGEBRA.json"],
                  "cover-algebra/ALGEBRA.json", algebra))
    cases.append(("cover-review", "source-domain/review_cover.py",
                  ["--source-dir", "{work}/upstream", "--campaign", "{work}", "--out", "{lanes}/source-domain/COVER-REVIEW.json"],
                  "source-domain/COVER-REVIEW.json", expected("source-domain/COVER-REVIEW.json")))
    cases.append(("residual", "residual-syndrome/verify_residual.py",
                  ["--source-dir", "{work}/upstream", "--interface", "{lanes}/circuit-interface/INTERFACE.json", "--out", "{lanes}/residual-syndrome/RESIDUAL.json"],
                  "residual-syndrome/RESIDUAL.json", expected("residual-syndrome/RESIDUAL.json")))
    cases.append(("residual-review", "residual-syndrome/review/independent_residual.py", [],
                  "residual-syndrome/review/INDEPENDENT-RECEIPT.json", expected("residual-syndrome/review/INDEPENDENT-RECEIPT.json")))
    report["portable_receipt_provenance_changes"] = provenance_changes
    started = time.monotonic()
    try:
        for name, script, arguments, receipt, target in cases:
            require(shutil.disk_usage(output).free >= 3 * 1024**3,
                    "Free disk space fell below 3 GiB")
            command = [sys.executable, "-I", "-O", "-B", str(lanes / script)]
            command += [arg.format(work=work, lanes=lanes) for arg in arguments]
            begin = time.monotonic()
            run = subprocess.run(command, cwd=work, env=env, text=True, capture_output=True)
            (output / (name + ".log")).write_text(run.stdout + run.stderr)
            require(run.returncode == 0, name + " failed; inspect its log")
            actual = load(lanes / receipt)
            require(canonical(actual) == canonical(target), name + " receipt differs")
            report["checks"].append({"name": name, "status": actual["status"],
                                     "seconds": round(time.monotonic() - begin, 3),
                                     "receipt": "work/lanes/" + receipt,
                                     "receipt_sha256": sha(lanes / receipt),
                                     "exact_typed_json_match": True})
            print(name + ": " + actual["status"], flush=True)
            (output / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        report["status"] = "PASS_ACTUAL_QUERY_INFORMATION_BOUNDS_PACKAGE"
    except Exception as error:
        report["status"] = "FAIL"
        report["error"] = str(error)
        raise
    finally:
        report["seconds"] = round(time.monotonic() - started, 3)
        (output / "REPLAY.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(report["status"])


if __name__ == "__main__":
    main()
