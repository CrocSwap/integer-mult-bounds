# SPDX-License-Identifier: Apache-2.0
"""Check each source-bound result from the shipped inputs without changing them."""
from pathlib import Path
import json
import subprocess
import sys
from tempfile import TemporaryDirectory


HERE = Path(__file__).resolve().parent


def run(script, *args):
    completed = subprocess.run(
        [sys.executable, "-I", "-B", str(HERE / script), *map(str, args)],
        cwd=HERE, check=True, stdout=subprocess.PIPE, text=True, timeout=110
    )
    return completed.stdout


def same_receipt(output, name):
    if json.loads(output) != json.loads((HERE / name).read_bytes()):
        raise ValueError(f"Recomputed evidence differs from {name}")


def main():
    graph = HERE / "strong-bit.json.gz"
    caller = HERE / "EFREE-CALLER.json.gz"
    same_receipt(run("history_proof.py", graph), "HISTORY.json")
    same_receipt(run("verify_rewrite.py"), "REWRITE.json")
    same_receipt(run("constant_caller.py", graph, caller), "CALLER.json")
    with TemporaryDirectory() as directory:
        temporary = Path(directory) / "price.json"
        run("price_audit.py", temporary)
        same_receipt(temporary.read_text(), "PRICE.json")
    print(run("joint_verify.py"), end="")
    assert 6**9 > 5**10 and 2**9 * 4**10 > 7**10 and 3**9 * 2**10 > 5**10
    print("PASS_CHART510_HISTORICAL_CUT_EXACT_KERNEL_CALLER_PRICE_AND_TRANSPORT")


if __name__ == "__main__":
    main()
