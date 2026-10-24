#!/usr/bin/env python3
"""Check the reviewed package and retain the independent check results."""

import ast
from fractions import Fraction
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
from urllib.parse import unquote


REVIEW = Path(__file__).resolve().parent
WRAP = REVIEW.parents[1]
PACKAGE = WRAP / "packages/original-clean-source-interface"
REPO = WRAP.parents[2]
COLD = REVIEW / "cold/package"
LANES = "frozen/work/centre-encoding-campaign-20261014/lanes/"


def need(value, reason):
    if not value:
        raise ValueError(reason)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    free_before = shutil.disk_usage(REVIEW).free
    need(free_before >= 3 * 1024 ** 3, "Free space below 3 GiB")
    manifest_path = PACKAGE / "PACKAGE-SHA256.json"
    manifest_raw = manifest_path.read_bytes()
    manifest = json.loads(manifest_raw)["files"]
    manifest_hash = digest(manifest_raw)
    need(manifest_hash == "54b73508241ee124872dbbeb01305c7b70bf3d7c214fc153233725220196e07b", "Final manifest changed")
    actual = {str(p.relative_to(PACKAGE)): digest(p.read_bytes())
              for p in PACKAGE.rglob("*") if p.is_file()}
    need(set(actual) == set(manifest) | {"PACKAGE-SHA256.json"}, "File inventory differs")
    need(all(actual[name] == value for name, value in manifest.items()), "Package hash differs")
    cold_snapshot = json.loads((REVIEW / "COLD-SOURCE-SNAPSHOT.json").read_text())
    need(all(actual[name] == value for name, value in cold_snapshot.items()), "Replayed input changed")
    need(all(digest((COLD / name).read_bytes()) == value for name, value in cold_snapshot.items()), "Cold input changed")

    sources = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    archives = {}
    archive_members = 0
    decompressed = 0
    for source in sources:
        raw = (PACKAGE / source["package_path"]).read_bytes()
        need(digest(raw) == source["sha256"], "Pinned source differs")
        need(len(raw) == source["bytes"], "Pinned byte count differs")
        if "decompressed_sha256" in source:
            need(digest(gzip.decompress(raw)) == source["decompressed_sha256"], "Payload hash differs")
            decompressed += 1
        original = REPO / source["source_path"]
        if "member" in source:
            if original not in archives:
                archive_raw = original.read_bytes()
                need(digest(archive_raw) == source["archive_sha256"], "Original archive differs")
                archives[original] = source["archive_sha256"]
            with tarfile.open(original, "r:gz") as archive:
                handle = archive.extractfile(source["member"])
                need(handle is not None, "Archive member absent")
                original_raw = handle.read()
            archive_members += 1
        else:
            original_raw = original.read_bytes()
        need(raw == original_raw, "Original source bytes differ")

    scripts = [
        ("replay.py", "require"),
        ("portable/check_physical_binding.py", "require"),
        ("portable/check_binding.py", "need"),
        (LANES + "residual-syndrome/physical-algebra/review-gauss/original-clean-source/check_review.py", "need"),
    ]
    source_checks = []
    guards = []
    guard_dir = REVIEW / "guard-controls"
    guard_dir.mkdir(exist_ok=True)
    environment = dict(os.environ)
    environment.update({name: "1" for name in ["OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"]})
    for index, (relative, guard) in enumerate(scripts):
        tree = ast.parse((PACKAGE / relative).read_text())
        nodes = list(ast.walk(tree))
        need(not any(isinstance(node, ast.Assert) for node in nodes), "An assertion can be removed by -O")
        imports = set()
        for node in nodes:
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                need(node.level == 0, "Relative module import")
                imports.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                need(node.func.id not in {"eval", "exec", "__import__"}, "Dynamic source evaluation")
        need(imports <= sys.stdlib_module_names, "Non-standard module import")
        source_checks.append({"file": relative, "assert_nodes": 0, "imports": sorted(imports), "all_imports_standard_library": True})
        code = "import runpy,sys; ns=runpy.run_path(sys.argv[1]); ns[sys.argv[2]](False,'independent-review-negative-control')"
        for optimized in (False, True):
            mode = "optimized" if optimized else "normal"
            command = [sys.executable, "-I", "-B"] + (["-O"] if optimized else [])
            command += ["-c", code, str(COLD / relative), guard]
            result = subprocess.run(command, cwd=REVIEW, env=environment, capture_output=True, text=True)
            log = result.stdout + result.stderr
            need(result.returncode != 0 and "ValueError: independent-review-negative-control" in log, "Guard failed to reject false input")
            (guard_dir / f"{index}-{mode}.txt").write_text(log)
            guards.append({"file": relative, "mode": mode, "exit_code": result.returncode, "false_requirement_rejected": True})

    links = []
    for relative in ("README.md", "PROOF.md", "NOTICE.md"):
        path = PACKAGE / relative
        for match in re.finditer(r"\[[^\]]*\]\(([^)]+)\)", path.read_text()):
            target = match.group(1).strip("<>").split("#", 1)[0]
            if not target or re.match(r"[a-zA-Z]+:", target):
                continue
            need((path.parent / unquote(target)).is_file(), "Local link target absent: " + target)
            links.append({"file": relative, "target": target})

    interface = json.loads((PACKAGE / (LANES + "circuit-interface/INTERFACE.json")).read_text())
    matrix = [{int(k): Fraction(v) for k, v in row.items()} for row in interface["R"]]
    need(len(matrix) == 8, "R row count")
    gram = [[sum(row.get(k, 0) * col.get(k, 0) for k in range(112)) for col in matrix] for row in matrix]
    need(gram == [[56 if i == j else 0 for j in range(8)] for i in range(8)], "R Gram")
    diagonal = [sum(row.get(k, 0) ** 2 for row in matrix) / 4 for k in range(112)]
    need(diagonal == [1] * 112, "KR diagonal")
    need(sum(len(row) for row in matrix) == 448, "R support")
    word = json.loads(gzip.decompress((PACKAGE / "archive-members/candidate/strict/global/base/providers/gauge44/CANONICAL-WORD.json.gz").read_bytes()))
    need(word["ports"][0] == 11 and (11 & 1).bit_count() == 1, "Native odd character witness")
    forward_added = 896 * 8 + 448 * 12 + 448 * 10 + 16
    backward_added = 448 * 12 + 896 * 14 + 448 * 10 + 16
    need((forward_added, backward_added) == (17040, 22416), "Added cost")
    totals = (204418 + forward_added, 204418 + backward_added)
    subtotal = 80 * totals[0] + 64 * totals[1]
    need(subtotal == 32234016, "Original invocation subtotal")
    local_profile = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82}
    global_profile = {1: 349604, 2: 60192, 3: 62585, 4: 20448, 5: 11808, 7: 7, 48: 4866}
    need(sum(k * v for k, v in local_profile.items()) == 5522, "Local paid mass")
    need(sum(k * v for k, v in global_profile.items()) == 1032192, "Retained global mass")

    replay = json.loads((REVIEW / "cold/replay/REPLAY.json").read_text())
    need(replay["status"] == "PASS_ORIGINAL_CLEAN_SOURCE_INTERFACE", "Replay status")
    need(len(replay["jobs"]) == 6 and replay["normal_optimized_equal"], "Replay coverage")
    need(all(job["frozen_receipt_byte_equal"] for job in replay["jobs"]), "Replay receipt differs")
    free_after = shutil.disk_usage(REVIEW).free
    need(free_after >= 3 * 1024 ** 3, "Free space below 3 GiB")
    report = {
        "status": "PASS_INDEPENDENT_PACKAGE_CHECKS",
        "package_manifest_sha256": manifest_hash,
        "package_files_including_manifest": len(actual),
        "package_bytes_including_manifest": sum((PACKAGE / name).stat().st_size for name in actual),
        "cold_snapshot_files": len(cold_snapshot),
        "all_cold_inputs_unchanged": True,
        "post_snapshot_additions": sorted(set(actual) - set(cold_snapshot)),
        "pinned_source_files_equal_original": len(sources),
        "archive_members_equal_original": archive_members,
        "full_original_archives_verified": {str(p.relative_to(REPO)): value for p, value in archives.items()},
        "decompressed_payload_hashes_checked": decompressed,
        "script_static_checks": source_checks,
        "guard_controls": guards,
        "local_wrapper_links_checked": links,
        "independent_arithmetic": {"R_shape": [8, 112], "R_nonzero": 448, "RR_transpose": "56 I_8", "KR_diagonal": "all 112 entries equal one", "native_witness_port": 0, "native_witness_q": 11, "native_witness_character": 1, "added_costs": [forward_added, backward_added], "per_call_costs": list(totals), "original_scalar_subtotal": subtotal, "local_native_mass": 5522, "retained_global_native_mass": 1032192},
        "cold_replay_runs": len(replay["jobs"]),
        "cold_replay_seconds_sum": round(sum(job["seconds"] for job in replay["jobs"]), 3),
        "free_space_before_bytes": free_before,
        "free_space_after_bytes": free_after,
        "scope": "Source equality, manifest coverage, cold input stability, static imports, explicit failure guards, local links, exact arithmetic, and six actual replay runs. No dense native kernel or full old axis history rerun."
    }
    (REVIEW / "PACKAGE-CHECKS.json").write_text(json.dumps(report, indent=2) + "\n")
    (REVIEW / "REVIEWED-PACKAGE-SHA256.json").write_bytes(manifest_raw)
    (REVIEW / "REVIEWED-README.md").write_bytes((PACKAGE / "README.md").read_bytes())
    print(json.dumps({key: report[key] for key in ["status", "package_manifest_sha256", "package_files_including_manifest", "pinned_source_files_equal_original", "archive_members_equal_original", "cold_replay_runs", "cold_replay_seconds_sum", "free_space_after_bytes"]}, indent=2))


if __name__ == "__main__":
    main()
