"""Opt-in strict comparator for the frozen PR921 benchmark. Apache-2.0.

Arham Tahir, with substantial OpenAI Codex assistance. Keep the predecessor's
commands, module inventory, scheduling, hashes, diagnostics and rejection rule.
"""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

from comparison import POLICY, comparison_key

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREDECESSOR = "research/agent-07-verifeng-seed88/benchmark.py"
INPUTS = frozenset((PREDECESSOR, "research/agent-07-verifeng-seed88/README.md",
                    "scripts/run_isolated_tests.py"))


def check_sources(root=ROOT):
    manifest = json.loads((HERE / "SOURCES.json").read_bytes())
    rows = [r for r in manifest["files"] if r["usage"] == "input"]
    if {r["path"] for r in rows} != INPUTS or len(rows) != len(INPUTS):
        raise ValueError("mandatory predecessor input inventory differs")
    for row in rows:
        if sha256((root / row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("source drift: " + row["path"])
    return {r["path"]: r["sha256"] for r in rows}


def load_benchmark(root=ROOT, strict=True):
    """Load exactly the admitted source; each call gets its own module globals."""
    check_sources(root)
    spec = importlib.util.spec_from_file_location("receipt_predecessor", root / PREDECESSOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    if strict:
        module.normalize = comparison_key
        original_record = module.record

        def record(results):
            records = original_record(results)
            for row in records.values():
                row["stderr_comparison_policy"] = POLICY
            return records

        module.record = record
    return module


if __name__ == "__main__":
    load_benchmark().main()
