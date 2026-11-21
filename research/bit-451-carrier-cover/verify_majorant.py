# SPDX-License-Identifier: Apache-2.0
"""Rebuild the fixed 451-factor supplier and certify its logarithmic majorants."""
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


NORMALIZED_CAP = "0.003879928044147"
NORMALIZED_CLAIM = "0.00387992804406"
NORMALIZED_HASHES = {
    "APPLICATION.json": "cac0e76c9eb370729f35974088b70a57c48238153f99fca69cb113593bc6163b",
    "AUDIT.json": "e68fc5f619a25881fb1d6f064f45a4cf8f161545d63c0dd7f550c1f7d48d3aaa",
}


ENDPOINT_CAP = "0.00387992804430335"
ENDPOINT_CLAIM = "0.00387992804422"
ENDPOINT_HASHES = {
    "APPLICATION.json": "d8afd25d84dd2721549686ee5a03ce5bddcf2a7957037d700e43e23b04f56f7e",
    "AUDIT.json": "af789e7e42411cfbadf411488de43626e6e23a44ccfb7d2027d488066db3691d",
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
    cap = seven_stage_bound(base, loss, CAP, check)
    ceiling = Q(base["raw_crossing"][1]) - Q(uniform["uniform_loss"]) - Q(7, 10**14)
    check(Q(CLAIM) - ceiling == Q(5, 10**15), "separation from predecessor proof ceiling")
    return {"installed": cap, "old_fixed_loss_ceiling": str(ceiling)}


def normalized_bound(base, check, *, scale, numerator, old_numerator, cap, claim):
    uniform = base["uniform"]
    carrier_log = uniform["H"]
    power = 60
    paid, productive, ambient = 11**451, 16**451, 134**451
    check(paid**15 < productive**13, "normalized exit")
    check(2**(2*scale)*paid**15 <= ambient**13, "normalized shift")
    log_ambient_lower = ambient.bit_length() - 1
    check(Q(uniform["ambient_power"][1]) < Q(scale + log_ambient_lower, scale)**power,
          "normalized base endpoint for all ranks")
    check(Q(13, 15)**power < Q(uniform["eta"][0]), "normalized capacity")
    loss = Q(numerator, carrier_log)
    check((scale+carrier_log)**power < scale**power * 2**numerator and
          (scale+carrier_log)*loss > 2*power, "normalized terminal and tail")
    seven_stage_bound(base, loss, cap, check)
    ceiling = Q(base["raw_crossing"][1]) - Q(old_numerator, carrier_log) - Q(7, 10**14)
    check(Q(claim) > ceiling, "separation from predecessor majorant ceiling")
    return {"installed": cap, "old_fixed_loss_ceiling": str(ceiling)}


def seven_stage_bound(base, loss, cap, check):
    h = base["uniform"]["H"]
    covered = Q(base["separation"]["trial"]) - loss - Q(1, h*2**44)
    stock = base["cover_and_stock"]
    rho, previous = Q(stock["rho"]), Q(stock["seed"])
    for _ in range(7):
        upper = (1-rho)*covered + rho*previous
        current = Q((upper*10**24).__floor__()-1, 10**24)
        check(previous < current < upper and current < min(rho, 1-rho), "ordinary stage")
        previous = current
    check(Q(cap) < previous < covered, "seven-stage service")
    return cap


def verify_application(source, work, legacy, component, claim, hashes, script, receipt):
    check = legacy["check"]
    out = work/"consumer"
    work.mkdir()
    full = legacy["consumer"](source, out, component, cap=component["installed"],
                              expected_claim=claim, expected_hashes=hashes)
    subprocess.run([sys.executable, "-IB", script, source, work/"audit.json",
                    "--outer", out], check=True)
    check(json.loads((work/"audit.json").read_bytes()) == json.loads(receipt.read_bytes()),
          "independent bound on actual outer replay")
    return full


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
        full = verify_application(source, work/"fractional", old, ordinary_bound(base, check), CLAIM,
                                  HASHES, HERE/"majorant_audit.py", HERE/"MAJORANT.json")
        change = Q(full["claim"]) - PRIOR
        check(change == Q(3, 10**14), "gain over previous campaign proof")
        print("PASS_COMPLETE_FRACTIONAL_MAJORANT", f"claim={full['claim']}", f"delta_vs_8026={change}",
              f"delta_vs_7863={full['delta']}", flush=True)
        check(digest(HERE/"MAJORANT.json") == "79a7363692faf04428b6cf08967426f9364bc87196e236e59b857a784a34f92f",
              "fractional predecessor receipt")
        check(digest(HERE/"normalized/SHIFTED-LOG.md") ==
              "04eba2e0a2a6cdd4ee512254142cbe45e647a73b66ad67b2c1c0a62e0883238a", "normalized theorem")
        normalized_component = normalized_bound(base, check, scale=1024, numerator=2406, old_numerator=2969,
                                                cap=NORMALIZED_CAP, claim=NORMALIZED_CLAIM)
        normalized = verify_application(source, work/"normalized", old, normalized_component,
                                        NORMALIZED_CLAIM, NORMALIZED_HASHES, HERE/"normalized/audit.py",
                                        HERE/"normalized/RESULT.json")
        increment = Q(normalized["claim"]) - Q(full["claim"])
        check(increment == Q(47, 10**14), "gain over complete fractional-majorant replay")
        print("PASS_COMPLETE_NORMALIZED_MAJORANT", f"claim={normalized['claim']}",
              f"delta_vs_fractional={increment}", f"delta_vs_7863={normalized['delta']}", flush=True)
        check(digest(HERE/"normalized/RESULT.json") ==
              "bb3f7384b8c17a396256c32d78cf8efa6a0270bb82988fa694a950f17b7f0bed", "normalized predecessor")
        # The exact shift inequality bounds the entire positive integer scale family.
        maximum_scale = (((134**451)**13 // (11**451)**15).bit_length()-1)//2
        carrier_log = base["uniform"]["H"]
        minimal_numerator = ((maximum_scale+carrier_log)**60 // maximum_scale**60).bit_length()
        check((maximum_scale, minimal_numerator) == (9012, 2218), "integer family endpoints")
        endpoint_component = normalized_bound(base, check, scale=maximum_scale, numerator=minimal_numerator,
                                              old_numerator=2406, cap=ENDPOINT_CAP, claim=ENDPOINT_CLAIM)
        endpoint = verify_application(source, work/"endpoint", old, endpoint_component, ENDPOINT_CLAIM,
                                      ENDPOINT_HASHES, HERE/"normalized/endpoint.py", HERE/"normalized/ENDPOINT.json")
        change = Q(endpoint["claim"]) - Q(normalized["claim"])
        check(change == Q(16, 10**14), "endpoint gain over the preceding complete application")
        print("PASS_COMPLETE_INTEGER_SCALE_ENDPOINT", f"claim={endpoint['claim']}",
              f"delta_vs_normalized={change}", f"delta_vs_7863={endpoint['delta']}", flush=True)


if __name__ == "__main__":
    main()
