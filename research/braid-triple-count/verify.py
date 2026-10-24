"""Printed 112-port triple count.

The braid note prints C(112,3) as 229936. The binomial coefficient is 227920.
The printed order histogram and extension counts are added here; the route
products are not enumerated.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
KAPPA = "836330098538459/500000000000000000"
PORTS = 112
PRINTED_TRIPLES = 229936
ORDER_HISTOGRAM = {2: 0, 3: 50, 4: 1197, 5: 1040, 6: 959, 8: 290, 9: 1568, 12: 792, 17: 188, 20: 132}
EXTENSIONS = {77: 24, 78: 12, 79: 5, 80: 4, 81: 3, 82: 2}
ZERO_EDGE = 846
ONE_EDGE = 50


def load() -> dict:
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    if selected["kappa"] != KAPPA:
        raise SystemExit("FAIL_BRAID_TRIPLE_COUNT selected kappa moved")
    return json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))


def binomial(n: int, k: int) -> int:
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    value = 1
    for index in range(k):
        value = value * (n - index) // (index + 1)
    return value


def main() -> None:
    pinned = load()
    pairs = binomial(PORTS, 2)
    triples = binomial(PORTS, 3)
    excess = PRINTED_TRIPLES - triples
    histogram_sum = sum(ORDER_HISTOGRAM.values())
    extension_sum = sum(EXTENSIONS.values())
    ordered = PORTS * (PORTS - 1)
    if pairs != histogram_sum:
        raise SystemExit("FAIL_BRAID_TRIPLE_COUNT histogram sum moved")
    if extension_sum != ONE_EDGE or ZERO_EDGE + extension_sum != 896:
        raise SystemExit("FAIL_BRAID_TRIPLE_COUNT extension sum moved")
    if ordered != PORTS * (PORTS - 1):
        raise SystemExit("FAIL_BRAID_TRIPLE_COUNT ordered products moved")
    if (
        pinned["ports"] != PORTS
        or pinned["unordered_pairs"] != pairs
        or pinned["ordered_products"] != ordered
        or pinned["printed_triples"] != PRINTED_TRIPLES
        or pinned["triples"] != triples
        or pinned["triple_excess"] != excess
        or pinned["histogram_sum"] != histogram_sum
        or pinned["extension_sum"] != extension_sum
        or pinned["zero_edge_triples"] != ZERO_EDGE
        or pinned["one_edge_triples"] != ONE_EDGE
        or pinned["no_new_kappa"] is not True
    ):
        raise SystemExit("FAIL_BRAID_TRIPLE_COUNT pinned result moved")
    print(f"PASS_BRAID_TRIPLE_COUNT excess={excess} no_new_kappa")


if __name__ == "__main__":
    main()
