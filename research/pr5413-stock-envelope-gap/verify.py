#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""The promoted PR5413 caller does not publish a selected stock coefficient."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent

SELECTED = "certificates/selected-result.json"
CLAIMS = "research/coupled-helper-neutral-completion/CLAIMS.json"
INVOICE = (
    "research/coupled-helper-neutral-completion/capsule/workspace/"
    "swarm-coupled-caller-sol-high-20261024/agents/invoice/"
    "neutral-v16c-run/INVOICE-NEUTRAL-LITERAL.json"
)
MARGIN = "research/stock-margin-chain/README.md"
PINS = {
    SELECTED: "66974efdced4083c00025f97d95d83909a226cdf801edb9301c195c6641f6903",
    CLAIMS: "bf4cc5cb47cf85ddd229b35a99e953b1973980e20aef9d16e8edb46ec4a44861",
    INVOICE: "e7df9fe1a7a00f67bbf35e9b155537fd26a0c05b61788653b878bd84d9006450",
    MARGIN: "5f82112f15b9db4e74478900afb46e02bfad6a3ab23cb8062665fecfcce95156",
}
KAPPA = Fraction(605457647, 200000000000)
GAIN = Fraction(1, 200000000000)
PREVIOUS = Fraction(15108879, 5000000000)
ASSUMPTIONS = (
    "native_all_columns",
    "owned_erasure",
    "compiler",
    "precision_tape",
    "analytic_recovery",
)
LEMMA = (
    "The selected PR5413 caller publishes kappa 605457647/200000000000 and "
    "does not publish a parent-reserve or depth coefficient; its stated gain "
    "1/200000000000 is compiler headroom over 605457646/200000000000."
)
STOCK_WORDS = ("stock", "reserve", "depth", "envelope")


class AuditFailure(Exception):
    """Explicit failure. python -O does not disable it."""


def need(ok, *why):
    if not ok:
        raise AuditFailure(" ".join(map(str, why)))


def load(name):
    raw = (ROOT / name).read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PINS[name], "sha256", name)
    if name.endswith(".json"):
        return json.loads(raw)
    return raw.decode("utf-8")


def decimal(text):
    need(isinstance(text, str) and text.startswith((".", "0.")), "decimal", text)
    return Fraction(text)


def main():
    need(LEMMA in (PACKAGE / "README.md").read_text(encoding="utf-8"), "README dropped the lemma")
    selected = load(SELECTED)
    claims = load(CLAIMS)
    invoice = load(INVOICE)
    margin = load(MARGIN)

    need(selected["kappa"] == "605457647/200000000000", "selected kappa")
    need(Fraction(selected["kappa"]) == KAPPA == decimal(selected["decimal"]), "kappa agreement")
    need(selected["source_prs"][0] == 5413, "selected pr")
    need(Fraction(selected["previous_kappa"]) == PREVIOUS, "previous kappa")
    need(decimal(claims["selected_baseline"]) == PREVIOUS, "claims baseline")
    need(decimal(claims["candidate_kappa"]) == KAPPA, "candidate")
    need(decimal(claims["comparison_kappa"]) == KAPPA - GAIN, "comparison")
    need(Fraction(claims["gain"]) == GAIN, "gain")
    need(claims["gain_type"] == "compiler headroom only; no recursive economic saving", "gain type")
    need(claims["raw_signed_profile_changed"] is False, "profile changed")
    ids = tuple(row["id"] for row in selected["assumptions"])
    need(ids == ASSUMPTIONS, "selected assumptions", ids)
    need(tuple(row["id"] for row in claims["assumptions"]) == ASSUMPTIONS, "claims assumptions")

    for word in STOCK_WORDS:
        need(word not in claims, "claims key", word)
    blob = json.dumps(claims).lower()
    need("stock" not in blob and "reserve" not in blob and "actual_stock_coefficient" not in blob,
         "claims text names a stock coefficient")
    need(invoice["full_ordinary_budget"] is None, "invoice budget is numeric")
    need(invoice["forward_packet_bound"] is True, "packet bound")
    need("actual_stock_coefficient" not in invoice, "invoice coefficient")

    def stock_coefficient(obj):
        raw = obj.get("actual_stock_coefficient")
        if not isinstance(raw, str):
            return None
        value = Fraction(raw)
        if value == GAIN and obj.get("gain_type", claims["gain_type"]).startswith("compiler headroom"):
            return None
        return value

    need(stock_coefficient(claims) is None, "published claims carry a stock coefficient")
    gain_forged = dict(claims, actual_stock_coefficient=str(GAIN))
    need(stock_coefficient(gain_forged) is None, "compiler gain was accepted as stock")
    reserve_forged = dict(claims, actual_stock_coefficient="128/1", gain_type="stock")
    need(stock_coefficient(reserve_forged) == Fraction(128, 1), "a real coefficient was missed")

    need("coefficient=unresolved" in margin, "older note resolved a coefficient")
    need("selected-bootstrap-stock-audit/RESULT.json" in margin, "older receipt")
    need("605457647" not in margin and "5413" not in margin, "older note names the new caller")
    print(
        "PASS_PR5413_STOCK_ENVELOPE_GAP "
        "kappa=605457647/200000000000 gain=1/200000000000 "
        "coefficient=absent older_receipt=bootstrap"
    )


if __name__ == "__main__":
    main()
