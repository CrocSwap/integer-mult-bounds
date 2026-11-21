# SPDX-License-Identifier: Apache-2.0
"""Rebuild the signed 451-factor application with its weighted-exit leaf bound."""
from fractions import Fraction as Q
from math import comb
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
PRIOR = PARENT / "normalized/ENDPOINT.json"
LAW = HERE / "WEIGHTED-EXITS.md"
CAP = "0.00387992804467760"
CLAIM = "0.00387992804459"
HASHES = {
    "APPLICATION.json": "72f03c3fc0131547ce7287180bf6d4ead12611a5c85d57adfd22bf997f1792e8",
    "AUDIT.json": "6baac0f0fca38d1b64a42950d0862f01916a5d81db94795bb395b6cec338bf55",
    "adapter/binary/FINITE.json": "32c38a55b268278754fb257ae9f8c46ed08129df7d3f9275c90e62ab4b3fc1ef",
}


def falling_ratios(p, q, a, b, beta):
    # Stirling numbers convert the ordinary powers to falling factorials.
    stirling = [[1]]
    for n in range(1, p + 1):
        previous = stirling[-1] + [0]
        stirling.append([0] + [j*previous[j] + previous[j-1] for j in range(1, n+1)])
    ratios = []
    for j in range(p+1):
        numerator = denominator = Q(0)
        for i in range(j, p+1):
            weight = comb(p,i) * stirling[i][j]
            numerator += weight * (q*(a+1)**(p-i) + (1-q)*a**(p-i))
            denominator += weight * b**(p-i) * beta**i
        if denominator <= 0 or numerator < 0:
            raise ValueError("invalid falling-factorial coefficient sign")
        ratios.append(q**j * numerator / denominator)
    return ratios


def component(base, prior, proof, seven_stages, check):
    p, h = 45, 1804
    q, a, b, beta = Q(3,4), Q(7,6), Q(319,100), Q(23,20)
    check((proof["p"], proof["h"], Q(proof["q"]), Q(proof["A_bar"]),
           Q(proof["B_under"]), Q(proof["beta"])) == (p,h,q,a,b,beta), "fixed coefficient input")
    check(0 < Q(proof["mean_plus_tail_ceiling_15dp"]) < q, "audited paid-log mean and tail")
    H = base["uniform"]["H"]
    paid, productive, ambient = 11**451, 16**451, 134**451
    check((2**h)**a.denominator <= paid**a.numerator and
          ((2**h)*ambient)**b.denominator >= paid**b.numerator and
          productive**beta.denominator >= paid**beta.numerator, "logarithm enclosures")
    ratios = falling_ratios(p,q,a,b,beta)
    eta = Q(base["uniform"]["eta"][0])
    check(len(ratios) == proof["coefficients"] == 46 and
          ratios == [Q(x) for x in proof["all_ratios"]], "all Stirling and Newton ratios agree")
    largest = max(ratios)
    check(Q(proof["eta_lower"]) == eta and largest < eta and
          ratios.index(largest) == proof["maximum_index"] == 7 and largest == Q(proof["maximum_ratio"]),
          "worst coefficient")
    check(Q(h + ambient.bit_length() - 1,h)**p > Q(base["uniform"]["ambient_power"][1]), "all base ranks")
    top, bottom = (H+h)**p, h**p
    J = (top//bottom).bit_length()
    loss = Q(J,H)
    check(J == proof["uniform_J"] == 1768 and bottom << (J-1) <= top < bottom << J and
          loss == Q(proof["uniform_loss"]) and loss*(H+h)>2*p, "least integer charge and entire tail")
    check(Q(prior["uniform_loss"]) == Q(2218,H) and Q(prior["charged_cover_loss"]) == Q(1,H*2**44),
          "inherited endpoint charge and physical cover")
    seven_stages(base,loss,CAP,check)
    ceiling = Q(base["raw_crossing"][1]) - Q(prior["uniform_loss"]) - Q(7,10**14)
    claim, previous = Q(CLAIM), Q(prior["candidate_grid_claim"])
    check(claim > ceiling > previous and Q(proof["cap"]) == Q(CAP) and
          Q(proof["candidate_grid_claim"]) == claim and Q(proof["old_cover_forgiven_upper"]) == ceiling and
          Q(proof["separation"]) == claim - ceiling, "directed separation from previous method")
    check(claim-previous == Q(proof["absolute_gain"]) == Q(37,10**14) and
          100*(claim-previous)/previous == Q(proof["exact_relative_percent"]), "prior and exact increase")
    return {"installed": CAP, "old_fixed_loss_ceiling": str(ceiling)}


def main():
    if sys.version_info[:2] != (3,12) or not __debug__:
        raise RuntimeError("use CPython 3.12 with assertions")
    for name in ("OPENBLAS_NUM_THREADS","OMP_NUM_THREADS","MKL_NUM_THREADS","VECLIB_MAXIMUM_THREADS"):
        os.environ[name] = "1"
    old = runpy.run_path(str(PARENT/"verify.py"))
    check, digest = old["check"], old["digest"]
    check(digest(PRIOR) == "ff9cf4ca87fa4480daac4c93aa1fa5744f5eec97385c7bae203ca2d3d874d0d9",
          "previous complete endpoint at #8026 2f82ecc8")
    check(digest(LAW) == "28e0308f315a583282291fa01998d53a874b4b7e3073cacc3ddbb38c5a7f66c7",
          "weighted-exit induction")
    seven_stages = runpy.run_path(str(PARENT/"verify_majorant.py"))["seven_stage_bound"]
    prior = json.loads(PRIOR.read_bytes())
    expected = json.loads((HERE/"RESULT.json").read_bytes())
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        source = old["extract"](work)
        subprocess.run([sys.executable,"-IB",source/"replay_451.py"],cwd=source,check=True)
        rebuilt = source/"replay/BIT-451.json"
        check(digest(rebuilt) == old["BASE_RECEIPT"] == digest(source/"BIT-451.json"), "original signed supplier")
        base = json.loads(rebuilt.read_bytes())
        check(digest(source/old["BRIDGE"]) == "9731b93026717f5fa15851e3633cbb4bdc76eba2bffb9d6b4a3b69f7dd502443",
              "delayed-cover source")
        old["supplier"](base)
        bound = component(base,prior,expected,seven_stages,check)
        outer = work/"consumer"
        full = old["consumer"](source,outer,bound,cap=CAP,expected_claim=CLAIM,expected_hashes=HASHES)
        audited = work/"weighted.json"
        subprocess.run([sys.executable,"-IB",HERE/"audit.py",source,PRIOR,LAW,audited,"--outer",outer],check=True)
        check(json.loads(audited.read_bytes()) == expected, "recomputed independent arithmetic and signed outer receipt")
        check(Q(full["tested"]) == Q(expected["candidate_tested"]) and
              Q(full["delta"]) == Q(113,10**14), "signed consumer comparison with #7863")
        print("PASS_COMPLETE_WEIGHTED_EXITS", f"claim={full['claim']}",
              f"delta_vs_endpoint={expected['absolute_gain']}", f"delta_vs_7863={full['delta']}", flush=True)


if __name__ == "__main__":
    main()
