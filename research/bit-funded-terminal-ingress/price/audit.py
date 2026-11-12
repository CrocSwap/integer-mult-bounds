"""Check the return-stock crossing from the already sealed directed intervals."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys


PIN = "1acd03fec0213cda8c44f4914c4c0b0c2e2124d7a0dc0586689e80bbc0fb8646"


def main(path, result):
    data = path.read_bytes()
    assert sha256(data).hexdigest() == PIN
    frozen = json.loads(data)
    result = json.loads(result.read_bytes())
    receipt = frozen["scopes"][1]["paid_refinement_price"]
    for kappa, cases in result.items():
        stock = {row["stock_upper"]: row["directed"][kappa] for row in receipt}
        fee = tuple(map(Q, stock[22]["minimum_split_charge"]))

        def bound(n, h):
            if n in stock:
                lo, hi = map(Q, stock[n]["raw_net"])
            else:
                # The #7209 retained price is affine in the return count.
                even = [tuple(map(Q, stock[q]["raw_net"])) for q in (n - 1, n + 1)]
                lo, hi = ((x + y) / 2 for x, y in zip(*even, strict=True))
            return lo - h * fee[1], hi - h * fee[0]

        for row in cases:
            h = row["h"]
            if row.get("unaffordable"):
                assert bound(22, h)[1] < 0
            else:
                n = row["needed_marked_returns"]
                assert bound(n - 1, h)[1] < 0 < bound(n, h)[0]
    assert [r.get("needed_singleton_expansions") for r in result[frozen["target"]]] == [7, 5, 4]
    assert [r.get("needed_singleton_expansions") for r in result[frozen["trial"]]] == [8, 6, None]
    print("PASS_INDEPENDENT_AFFINE_TARIFF_SIGN_CHECK")


if __name__ == "__main__":
    assert __debug__
    main(*(Path(x) for x in sys.argv[1:]))
