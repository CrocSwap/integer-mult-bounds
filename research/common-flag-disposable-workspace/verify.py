"""Read-only source-bound replay with typed, complete receipt equality."""
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def fail(message):
    raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def verify():
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for item in sources["files"]:
        if item["usage"] == "input":
            if hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest() != item["sha256"]:
                fail("source drift: " + item["path"])
    expected = json.loads((HERE / "EXPECTED.json").read_text(encoding="utf-8"))
    proof_hash = hashlib.sha256((HERE / "PROOF.md").read_bytes()).hexdigest()
    if expected["proof_sha256"] != proof_hash:
        fail("proof drift")
    spec = importlib.util.spec_from_file_location("disposable_cut_checks", HERE / "check.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observed = {"proof_sha256": proof_hash, "evidence": module.compute()}
    if canonical(observed) != canonical(expected):
        fail("complete typed receipt mismatch")
    cases = observed["evidence"]["cases"]
    print("PASS_COMMON_FLAG_DISPOSABLE_WORKSPACE cases=" + str(len(cases))
          + " inputs=" + str(sum(x["input_assignments"] for x in cases))
          + " partitions=" + str(sum(x["binary_partitions"] for x in cases))
          + " outside_reconstructions=" + str(sum(x["outside_reconstructions"] for x in cases))
          + " controls=" + str(len(observed["evidence"]["rejection_controls"])))


if __name__ == "__main__":
    verify()
