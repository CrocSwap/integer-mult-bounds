#!/usr/bin/env python3
"""One-command verification, including unchanged inherited local auditors.

Writes only a temporary directory, which is removed on exit. Apache-2.0.
Substantial OpenAI Codex assistance for Luis Leon (@mythrilium).
"""
import copy
import gzip
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gauge_verify", HERE / "verify.py")
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


def main():
    V.main()
    # Inherited auditors use assertions. Never inherit an optimized invocation.
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    subprocess.run([sys.executable, "-I", "-B", str(HERE / "test_verify.py")], check=True, env=env)
    word, programs, source_spec = V.load_inputs()
    cert = json.loads((HERE / "CERTIFICATE.json").read_text())
    candidate = copy.deepcopy(word)
    candidate["cleanup"] = V.transform(word["cleanup"], cert["exponents"])
    with tempfile.TemporaryDirectory(prefix="jp8-diagonal-gauge-") as work:
        out = Path(work)
        payload = json.dumps(candidate, sort_keys=True, separators=(",", ":")).encode()
        (out / "CANONICAL-WORD.json.gz").write_bytes(gzip.compress(payload, mtime=0))
        code = V.ROOT / "research/complex-k492-owner-repair/code"
        for filename in ("hpe_emit_local.py", "hpe_audit_local.py"):
            subprocess.run([sys.executable, "-I", "-B", str(code / filename), str(out)], check=True, env=env)
        emitted = json.loads(gzip.decompress((out / "LOCAL-PROGRAMS.json.gz").read_bytes()))
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        audit = json.loads((out / "INDEPENDENT-LOCAL-REPLAY.json").read_text())
        for name, stream in emitted.items():
            independent = V.splice(programs[name], word["cleanup"], candidate["cleanup"], name == "backward")
            V.require(stream == independent, "inherited emitter and independent splice differ")
            V.require(V.digest(stream) == expected["programs"][name]["candidate_sha256"], "emitter digest")
            V.require(audit["paid_profiles"][name] == source_spec["expected_profile"], "paid profile change")
            V.require(audit["local"][name]["prefix_l1_upper"] == expected["programs"][name]["after"]["prefix_l1"], "prefix audit disagreement")
        V.require(len(audit["negative_controls_rejected"]) == 25, "inherited controls missing")
    print("PASS_JP8_GAUGE_COMPLETE saved=6154/6154 optimal_cost=10326 tests=10 inherited_controls=25 kappa=unchanged")


if __name__ == "__main__":
    main()
