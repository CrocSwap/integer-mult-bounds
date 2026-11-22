"""Run the linked signed operator and check every finite convolution coefficient."""

import json
import sys
from pathlib import Path


def main():
    sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
    from band_product import Product, multiply, prepare_native, production_supplier
    from check_product import one
    from fixed_directory import data
    from installations import PROFILES

    links = data()
    for left, right in zip(prepare_native(), links[0], strict=True):
        assert all(a is b for a, b in zip(left, right, strict=True))
    for profile, tier in zip(PROFILES.values(), links[0], strict=True):
        instance = production_supplier(
            profile.complex_log, profile.positive_stop_denominator
        )
        assert instance.recipe is tier[-1] and instance.physical is links[5][0]
    answer = multiply(-741503, 466013)
    assert answer == -345550037539
    row = one(Product((3, 5), 8, 136), -741503, 466013)
    assert row["product"] == str(answer)
    assert row["coefficients_prefix"] == [11811, 10996, 4152, 868, 77]
    print(json.dumps({"public_signed_product": answer, "finite_tensor": row}))


if __name__ == "__main__":
    main()
