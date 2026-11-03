"""Read-only integrity check for the bounded literal-discovery source export.
No candidate import, compilation, test, subprocess, decoder or target invocation.
The publication tree/external freeze authenticates MANIFEST.json itself.
"""
from pathlib import Path, PurePosixPath
import hashlib
import json
import os
import stat
import sys

BASE = "7c49fe32c55de02c2c873655c804b16e4c3fef0a"
TREE = "e6898c8ba7a27b71587c32ba3f639259ceeeed91"
HELPER = "56b44235f55685d61e5c8b8099d825b4ec5a53987910f506dffad309c12ffb53"

class InvalidArchive(ValueError):
    pass

def need(ok, why):
    if not ok:
        raise InvalidArchive(why)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()

def safe_path(value):
    need(type(value) is str and value != "", "empty/non-string path")
    p = PurePosixPath(value)
    need(not p.is_absolute() and p.as_posix() == value and
         all(x not in (".", "..") for x in p.parts) and chr(92) not in value,
         "noncanonical path: " + repr(value))
    return value

def inventory(root):
    found = {}
    for parent, dirs, files in os.walk(root, followlinks=False):
        for name in dirs:
            mode = (Path(parent) / name).lstat().st_mode
            need(stat.S_ISDIR(mode) and not stat.S_ISLNK(mode), "linked/non-directory component")
        for name in files:
            path = Path(parent) / name
            mode = path.lstat().st_mode
            need(stat.S_ISREG(mode) and not stat.S_ISLNK(mode), "nonregular/link file")
            need(stat.S_IMODE(mode) in (0o644, 0o444), "file permission mode differs: " + name)
            rel = safe_path(path.relative_to(root).as_posix())
            need(path.lstat().st_size <= 8 * 1024 * 1024, "pre-read file cap")
            raw = path.read_bytes()
            need(len(raw) <= 8 * 1024 * 1024, "file cap")
            found[rel] = raw
    need(len(found) <= 256, "inventory cap")
    return found

def rows_by_path(rows, key):
    need(type(rows) is list and len(rows) <= 256, "row list/cap")
    out = {}
    for row in rows:
        need(type(row) is dict, "non-object row")
        path = safe_path(row.get(key))
        need(path not in out, "duplicate row: " + path)
        out[path] = row
    return out

def verify(root):
    raw = inventory(root)
    need("MANIFEST.json" in raw, "manifest absent")
    manifest = json.loads(raw["MANIFEST.json"])
    need(manifest.get("base_commit") == BASE and manifest.get("base_tree") == TREE, "base pin")
    rows = rows_by_path(manifest.get("files"), "path")
    need(set(rows) == set(raw) - {"MANIFEST.json"}, "exact manifest inventory")
    for path, row in rows.items():
        data = raw[path]
        need(row.get("bytes") == len(data) and row.get("sha256") == digest(data) and
             row.get("git_blob") == git_blob(data) and row.get("mode") == "100644",
             "manifest byte/mode mismatch: " + path)
    mapping = json.loads(raw["SOURCE-MAP.json"])
    mapped = rows_by_path(mapping.get("files"), "package_path")
    need(set(mapped) == set(raw) - {"MANIFEST.json", "SOURCE-MAP.json"}, "source map inventory")
    for path, row in mapped.items():
        need(type(row.get("source_path")) is str and bool(row["source_path"]), "source origin absent")
        for key in ("bytes", "sha256", "git_blob", "mode"):
            need(row.get(key) == rows[path][key], "source map mismatch: " + path + ":" + key)
    pins = {
      "repair-v2/passive_image_candidates_v2.py": (11809, HELPER),
      "controls-v1/literal_fixtures_v1.py": (3022, "979f719820707490920bf39f3c398129ed6e49b2df898e76a1f7292cc8d8d47d"),
      "controls-v1/test_literal_candidates_v1.py": (8023, "cbbe3139f6d67d2da653f5aaf4a62f0ab108f5a1cde37e0f444f3ef826ae9ed6"),
      "archive/rejected-v1/passive_image_candidates_v1.py.txt": (11272, "c9044f4926cbcc880eb17b579b2cd6e323f1657bf6b6463138fc0b4310fe4b04"),
      "context/ROUND-CLOSE-v1.json": (None, "e8fc63616c75ad6dd5b5b69620764e29f7e6040ad292c5a5924cd6027a5e2c93"),
    }
    for path, (size, expected) in pins.items():
        need(digest(raw[path]) == expected and (size is None or len(raw[path]) == size), "frozen component pin: " + path)
    scope = json.loads(raw["SCOPE.json"])
    for key in ("P1_complete", "P2_complete", "P3_complete", "P4_complete", "actual_image_pass",
                "actual_guard_60_seconds_granted", "instruction_boundaries_validated",
                "relocation_effects_audited", "source_role_qualified", "D_applicability_qualified",
                "certificate_feasible", "full_C05", "full_V03", "new_research_round_authorized"):
        need(scope.get(key) is False, "qualification promotion: " + key)
    need(scope.get("round_complete") == 0 and scope.get("round_denominator") == 4 and
         scope.get("original_activity_credit_added") == 0 and scope.get("physical_costs") == "OPEN_NOT_ZERO",
         "round/credit/cost boundary")
    need(scope.get("semantic_falsifiers_unimplemented") == ["S11role", "S12relocations", "S13privatecalls"], "semantic scope")
    verify_config = json.loads(raw["VERIFY.json"])
    expected_commands = []
    for optimized in (False, True):
        expected_commands.append(["{python}", "-I", "-B"] + (["-O"] if optimized else []) +
          ["{package}/run_export_controls.py"])
    need(verify_config.get("status") == "ready" and verify_config.get("inputs") == [] and
         verify_config.get("requirements") == [] and
         [r.get("argv") for r in verify_config.get("commands", [])] == expected_commands,
         "registered command boundary")
    for mode, optimize in (("normal", 0), ("optimized", 1)):
        result = json.loads(raw["evidence/controls-execution-v1/" + mode + ".stdout.raw"])
        need(result.get("status") == "PASS_DISCOVERY_CONTROLS_ONLY" and
             result.get("case_count") == 23 and result.get("passed_count") == 23 and
             result.get("failed_count") == 0 and result.get("python_optimize") == optimize and
             len(set(result.get("passed", []))) == 23 and result.get("helper_sha256") == HELPER and
             result.get("main_or_actual_driver_called") is False, "retained finite outcome")
    need(not any(p.endswith(".py") and ("guard" in p or "supervisor" in p) for p in raw), "guard executable in export")
    return {"status": "PASS_LITERAL_DISCOVERY_ARCHIVE_INTEGRITY_ONLY", "files": len(raw),
            "candidate_source_executed": False, "historical_cases_per_mode": 23,
            "actual_image_pass": False, "full_C05": False, "full_V03": False,
            "original_credit_added": 0, "physical_costs": "OPEN_NOT_ZERO"}

if __name__ == "__main__":
    try:
        print(json.dumps(verify(Path(__file__).resolve().parent), sort_keys=True))
    except (InvalidArchive, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"status": "FAIL_ARCHIVE_INTEGRITY", "error": str(exc)}, sort_keys=True), file=sys.stderr)
        raise SystemExit(1)
