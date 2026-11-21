# SPDX-License-Identifier: Apache-2.0
"""Rebuild the fixed 451-factor supplier and certify its fractional logarithmic majorant."""
from fractions import Fraction as Q
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
CAP = "0.00387992804367877"
CLAIM = "0.00387992804359"
PRIOR = Q("0.00387992804356")
HASHES = {
    "APPLICATION.json": "2d46b81b9f009ec80a21ae1545f975cdf68abcfe4ea2f3f3a6becaf43e107ebf",
    "AUDIT.json": "df50d7caf1239edaad65ed5394e483e9f5b1e804495435d4386c8068cb0d8d97",
}


def ordinary_bound(base, check):
    uniform = base["uniform"]
    h = uniform["H"]
    check(h == 1202400000000000 and uniform["N"] == f"2^{h}", "frozen carrier")
    paid, productive, ambient = 11**451, 16**451, 134**451
    check(paid**200 < productive**173 and (1 << 27)*paid**200 <= ambient**173, "exit and shift")
    eta_lower = Q(uniform["eta"][0])
    ambient_upper = Q(uniform["ambient_power"][1])
    check(Q(173, 200)**237 < eta_lower**4 and ambient_upper**4 < 2**237, "fractional majorant")
    loss = Q(2969, h)
    check((1+h)**237 < 2**(4*2969) and (h+1)*loss > Q(237, 2), "carrier and tail")
    covered = Q(base["separation"]["trial"]) - loss - Q(1, h*2**44)
    stock = base["cover_and_stock"]
    rho, previous = Q(stock["rho"]), Q(stock["seed"])
    for _ in range(7):
        upper = (1-rho)*covered + rho*previous
        current = Q((upper*10**24).__floor__()-1, 10**24)
        check(previous < current < upper and current < min(rho, 1-rho), "ordinary stage")
        previous = current
    check(Q(CAP) < previous < covered, "seven-stage service")
    ceiling = Q(base["raw_crossing"][1]) - Q(uniform["uniform_loss"]) - Q(7, 10**14)
    check(Q(CLAIM) - ceiling == Q(5, 10**15), "separation from predecessor proof ceiling")
    return {"installed": CAP, "old_fixed_loss_ceiling": str(ceiling)}


def main():
    old = runpy.run_path(str(HERE / "verify.py"))
    check, digest = old["check"], old["digest"]
    check(sys.version_info[:2] == (3, 12) and __debug__, "use CPython 3.12 with assertions")
    for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
        os.environ[key] = "1"
    check(digest(HERE/"RESULT.json") == "b6dd0af1fa0d0a5b619eb199ca12116219debcd6127f5425ce4da8bf9f72fb71",
          "prior #8026 complete result")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        source = old["extract"](work)
        subprocess.run([sys.executable, "-IB", source/"replay_451.py"], cwd=source, check=True)
        rebuilt = source/"replay/BIT-451.json"
        check(digest(rebuilt) == old["BASE_RECEIPT"] == digest(source/"BIT-451.json"), "supplier reconstruction")
        base = json.loads(rebuilt.read_bytes())
        old["supplier"](base)
        component = ordinary_bound(base, check)
        out = work/"consumer"
        full = old["consumer"](source, out, component, cap=CAP, expected_claim=CLAIM, expected_hashes=HASHES)
        subprocess.run([sys.executable, "-IB", HERE/"majorant_audit.py", source, work/"audit.json",
                        "--outer", out], check=True)
        check(json.loads((work/"audit.json").read_bytes()) == json.loads((HERE/"MAJORANT.json").read_bytes()),
              "independent bound on actual outer replay")
        change = Q(full["claim"]) - PRIOR
        check(change == Q(3, 10**14), "gain over previous campaign proof")
        print("PASS_COMPLETE_FRACTIONAL_MAJORANT", f"claim={full['claim']}", f"delta_vs_8026={change}",
              f"delta_vs_7863={full['delta']}", flush=True)


if __name__ == "__main__":
    main()
