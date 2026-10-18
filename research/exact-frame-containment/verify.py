"""One complete scoped replay: exact oracle, full audits, and failure controls.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
sys.path.insert(0, str(PACKAGE))
from worker import check_sources


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical_json(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def compare_payload(actual, expected):
    require(set(actual) == set(expected) | {"audit_seconds", "peak_rss_kib"},
            "unexpected receipt fields")
    digest = hashlib.sha256(canonical_json(actual["result"]).encode()).hexdigest()
    require(digest == actual["result_sha256"], "result digest mismatch")
    payload = {k: v for k, v in actual.items() if k not in ("audit_seconds", "peak_rss_kib")}
    require(canonical_json(payload) == canonical_json(expected), "complete payload mismatch")


def run_engine(engine, output, cpu=None):
    command = [sys.executable, "-I", "-B", str(PACKAGE / "worker.py"), engine, str(output)]
    if cpu is not None:
        command.extend(["--cpu", str(cpu)])
    process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
    require(process.returncode == 0, process.stdout + process.stderr)
    return json.loads(output.read_text())


def rejection_controls():
    """Reach actual forward-frame and endpoint checks in the unchanged compiler."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import rational_span_frames as frames
    from experiments.mixed_point_circuit import build, factored_transpose
    from kernel import ExactContainment
    circuit, _ = factored_transpose(build(10, 3, 3, 1))
    require(circuit.verify(), "baseline circuit")
    captured = {}
    original_compile = frames.compiled_frames
    original_contained = frames.contained

    def capture(circuit, labels):
        captured.update(labels)
        return original_compile(circuit, labels)

    frames.compiled_frames = capture
    try:
        require(frames.audit(circuit)["cut_certified"], "baseline cut")
    finally:
        frames.compiled_frames = original_compile
    gates = [node for node in circuit.active if circuit.args[node]]
    nonempty = next(node for node in gates if captured[node])
    multirow = next(node for node in gates if len(captured[node]) > 1)
    controls = {
        "missing_frame": {**captured, nonempty: ()},
        "scaled_frame": {**captured, nonempty:
                         (tuple(2 * x for x in captured[nonempty][0]),) + captured[nonempty][1:]},
        "reordered_frame": {**captured, multirow: tuple(reversed(captured[multirow]))},
        "invalid_injection": {node: tuple(tuple(int(i == j) for i in range(10)) for j in range(10))
                              for node in captured},
    }
    results = {}
    try:
        positive = original_compile(circuit, captured)
        for engine in (original_contained, ExactContainment()):
            frames.contained = engine
            require(original_compile(circuit, captured) == positive, "positive compiler result")
            for name, labels in controls.items():
                try:
                    original_compile(circuit, labels)
                except ValueError as error:
                    message = str(error)
                    if name in results:
                        require(results[name] == message, "changed rejection: " + name)
                    results[name] = message
                else:
                    raise ValueError("accepted invalid frame: " + name)
    finally:
        frames.contained = original_contained
    return results


def source_controls(work):
    files = json.loads((PACKAGE / "SOURCES.json").read_text())["files"]
    files = [item for item in files if item["usage"] == "input"]
    for item in files:
        path = work / item["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / item["path"]).read_bytes())
    check_sources(work)
    for item in files:
        path = work / item["path"]
        data = path.read_bytes()
        path.write_bytes(data + b"\n# source corruption control\n")
        try:
            check_sources(work)
        except ValueError as error:
            require(str(error) == "source pin mismatch: " + item["path"], "wrong pin failure")
        else:
            raise ValueError("source drift accepted")
        path.write_bytes(data)
    import worker
    metadata = work / "metadata"
    metadata.mkdir()
    for altered in (files[:-1], files[:-1] + [files[0]]):
        (metadata / "SOURCES.json").write_text(json.dumps({"files": altered}))
        with patch.object(worker, "PACKAGE", metadata):
            try:
                check_sources(work)
            except ValueError as error:
                require(str(error) == "source inventory mismatch", "wrong inventory failure")
            else:
                raise ValueError("incomplete/duplicate source inventory accepted")
    return {"changed_input_bytes": len(files), "invalid_inventories": 2}


def receipt_controls(actual, expected):
    def rehash(receipt):
        receipt["result_sha256"] = hashlib.sha256(canonical_json(receipt["result"]).encode()).hexdigest()
    corruptions = []
    changed = copy.deepcopy(actual)
    changed["result"][0]["cut_certified"] = 1  # Equal to True under naive Python ==.
    rehash(changed)
    corruptions.append(changed)
    changed = copy.deepcopy(actual)
    changed["result"][1]["frame_sha256"] = "0" * 64
    rehash(changed)
    corruptions.append(changed)
    changed = copy.deepcopy(actual)
    del changed["result"][0]["compiled"]["reverse_nested"]
    rehash(changed)
    corruptions.append(changed)
    changed = copy.deepcopy(actual)
    changed["unknown_proof_field"] = True
    corruptions.append(changed)
    for changed in corruptions:
        try:
            compare_payload(changed, expected)
        except ValueError:
            pass
        else:
            raise ValueError("receipt corruption accepted")
    return len(corruptions)


def main():
    if sys.flags.optimize:
        raise SystemExit("Run without -O: inherited circuit assertions must remain enabled")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="Optional new receipt; never overwritten")
    args = parser.parse_args()
    check_sources()
    for flags in ([], ["-O"]):
        subprocess.run([sys.executable, "-I", "-B", *flags, str(PACKAGE / "test_kernel.py")],
                       cwd=ROOT, check=True, timeout=60)
    expected = json.loads((PACKAGE / "EXPECTED.json").read_text())
    with tempfile.TemporaryDirectory(prefix="exact frame containment ") as temporary:
        work = Path(temporary)
        for engine in ("reference", "equations", "crosscheck"):
            actual = run_engine(engine, work / (engine + ".json"))
            compare_payload(actual, expected)
        decisions = json.loads((work / "crosscheck.decisions.json").read_text())
        require(decisions == {"calls": 42860, "true": 42860, "false": 0},
                "changed complete audit containment coverage")
        pins = source_controls(work / "pin controls")
        bad_receipts = receipt_controls(actual, expected)
        refused = subprocess.run([sys.executable, "-I", "-O", "-B", str(PACKAGE / "worker.py"),
                                  "equations", str(work / "must-not-exist.json")],
                                 capture_output=True, text=True, timeout=10)
        require(refused.returncode != 0 and "assertions must remain enabled" in refused.stderr,
                "optimized historical replay was not refused")
        require(not (work / "must-not-exist.json").exists(), "failed replay wrote success receipt")
    from test_kernel import MUTATIONS, cases
    controls = rejection_controls()
    result = {"status": "PASS_EXACT_FRAME_CONTAINMENT", "assignment_seed": 90,
              "kernel_cases": sum(1 for _ in cases()), "kernel_test_groups": 5,
              "kernel_modes": ["normal", "optimized"], "kernel_mutations": sorted(MUTATIONS),
              "complete_audits": 6, "dimensions": [10, 12], "decisions": decisions,
              "full_payload_sha256": expected["result_sha256"],
              "compiler_controls": controls, "source_controls": pins,
              "receipt_controls": bad_receipts, "optimized_worker_refused": True,
              "scope": "Historical mixed-point frame audits only; no new kappa or full theorem."}
    if args.out:
        with args.out.open("x") as stream:
            stream.write(json.dumps(result, indent=2) + "\n")
    print(result["status"], "audits=6 decisions=42860 compiler_controls=4 kernel_mutations=5")


if __name__ == "__main__":
    main()
