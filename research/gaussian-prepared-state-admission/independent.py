"""Original-code reproducer in a clean subprocess, without importing admission.py."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def need(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    manifest = json.loads((ROOT / "SOURCES.json").read_text(encoding="utf-8"))
    payloads = {}
    for entry in manifest["snapshots"]:
        if entry["path"].startswith("vendor/"):
            data = (ROOT / entry["path"]).read_bytes()
            need(entry["commit"] == "190637e62401516c72b267859c0dd51cac607f6d", "source pin")
            need(hashlib.sha256(data).hexdigest() == entry["sha256"], "source sha256")
            need(hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                 == entry["git_blob"], "source git blob")
            payloads[Path(entry["path"]).name] = data
    need(set(payloads) == {"intervals.py", "gaussian.py", "pipeline.py", "PROOF.md"}, "source set")
    program = r'''
import json, sys
sys.path.insert(0, sys.argv[1])
from gaussian import GaussianLine
from pipeline import uniform_certificate, multiply
out = []
for factor in (1, 2, 3):
    line = GaussianLine(5, 8, 5)
    before = uniform_certificate([line], 4)
    line.compression = [[factor * entry for entry in row] for row in line.compression]
    after = uniform_certificate([line], 4)
    value, receipt = multiply(1, 1, [line], 4, input_bits=4)
    line.operator_error = None
    try:
        uniform_certificate([line], 4)
        fresh = 'accepted'
    except ValueError as exc:
        fresh = str(exc)
    out.append(dict(factor=factor, before=before, after=after, value=value,
                    receipt=receipt, fresh=fresh))
print(json.dumps(out))
'''
    with tempfile.TemporaryDirectory(prefix="gaussian-source-replay-") as directory:
        for name, data in payloads.items():
            (Path(directory) / name).write_bytes(data)
        process = subprocess.run([sys.executable, "-I", "-O", "-B", "-c", program, directory],
                                 capture_output=True, text=True, check=True, timeout=90)
        results = json.loads(process.stdout)
    for row in results:
        factor = row["factor"]
        need(row["before"] == row["after"], "cached certificate changes unexpectedly")
        need(row["value"] == factor**3 and row["receipt"]["coefficients"] == [factor**3, 0, 0, 0, 0],
             "three-transform amplification witness")
        need(Fraction(*row["receipt"]["error_radius"]) < Fraction(1, 2), "accepted tiny radius")
        need(row["fresh"] == ("accepted" if factor == 1 else "Gaussian/Fourier operator certificate"),
             "fresh certification control")
    frozen = json.loads((ROOT / "result.json").read_text(encoding="utf-8"))
    witness = results[1]
    need(frozen["original_certificate"] == witness["before"], "frozen original certificate")
    need(frozen["stale_cache_witness"]["accepted_error_radius"] == witness["receipt"]["error_radius"]
         and frozen["stale_cache_witness"]["after_mutation"] == witness["value"], "frozen exact witness")
    print("PASS_INDEPENDENT_GAUSSIAN_STATE_WITNESS factors=1,2,3 fresh_rejections=2")


if __name__ == "__main__":
    main()
