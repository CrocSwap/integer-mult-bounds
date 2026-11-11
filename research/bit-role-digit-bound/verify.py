#!/usr/bin/env python3
"""Check the selected BIT role-digit comparison. No new kappa."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
H1 = 25986965159937
X_EXPECTED = 471715391583208384


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("FAIL: " + message)


def ulog2(value: int) -> int:
    need(isinstance(value, int) and value > 0, "ulog2 domain")
    return value.bit_length()


def role_upper(width: int, mass: int, floor: int, power: int, rank: int) -> int:
    wide = width ** power
    paid = mass ** power + wide * (floor ** power)
    return ulog2(wide) + (rank + 1) * ulog2(wide + paid + 1)


def fits(upper: int, rank: int) -> bool:
    den = 5 * rank + 26
    return upper < (1 << 13) * den and rank + 13 <= 2 * rank


def phrase(path: str, text: str) -> None:
    body = (ROOT / path).read_text(encoding="utf-8")
    need(text in body, "missing phrase in " + path)


def bit_invoice():
    record = json.loads((ROOT / "research/query-thinned-controllers/RESULT.json").read_text())
    invoice = record["bit_invoice"]
    targets = {int(k): c for k, c in invoice["targets"].items()}
    paid = {int(k): c for k, c in invoice["paid"].items()}
    width = sum(targets.values())
    mass = sum(k * c for k, c in paid.items())
    need(width == invoice["productive_fields"], "productive fields")
    return width, mass, record["bit_strictification"], record["ordinary_BIT"]


def main() -> None:
    phrase("certificates/frontier6030/CLAIM.json", '"admitted_BIT_saving": "17/5000"')
    phrase("certificates/frontier6030/CLAIM.json", '"kappa": "781451/250000000"')
    phrase("certificates/frontier6030/CLAIM.json", '"rank_encoding": "2^25986965159937"')
    phrase("research/lockstep-live-role-audit/constant_c.py",
           "B_N <= C_N^N, C_N = Wv*(Wv+Pv+1)^(h+1), h <= H1.")
    phrase("research/selected-bit-stage-stock-band/PROOF.md", "c_B <= N^2")
    phrase("research/selected-bit-stage-stock-band/PROOF.md", "52182660963735")
    phrase("research/selected-old-leaf-reserve/README.md", "`S_old = 1`")
    phrase("research/selected-bit-stage-stock-band/PROOF.md",
           "ceil(log_q(B*|GL_N(F_q)|))")
    phrase("research/kappa-rebuild/bit/DELAYED-COVER-BRIDGE.md",
           r"\left\lceil\log_q(B|\operatorname{GL}_N(\mathbb F_q)|)\right\rceil")
    width, mass, strict, ordinary = bit_invoice()
    need(strict["uniform_H1"] == H1, "H1")
    need(strict["uniform_N"] == "2^25986965159937", "uniform N")
    need(strict["tensor_power"] == 1024, "tensor power")
    need(strict["target_floor_base"] == 18, "target floor")
    need(ordinary["admitted"] == "17/5000", "admitted saving")
    need(ordinary["atom"] == "1/250", "atom")
    need(ordinary["prime_rule"].startswith("odd q > 2^26*N^5"), "prime rule")
    upper = role_upper(width, mass, 18, 1024, H1)
    need(upper == X_EXPECTED, "role upper bound")
    need(upper.bit_length() == 59 and upper.bit_length() < H1, "X < 2^H1")
    need(fits(upper, H1), "c_B <= 2^(H1+13) <= N^2")
    need(not fits(upper, 12), "small-rank control must fail")
    need(not fits(upper + (1 << 13) * (5 * H1 + 26), H1), "shifted upper must fail")
    print("PASS_BIT_ROLE_DIGIT c_B<=2^(H1+13)<=N^2 "
          "X=471715391583208384 no_new_kappa")


if __name__ == "__main__":
    main()
