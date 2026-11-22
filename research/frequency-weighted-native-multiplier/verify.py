"""Restore the signed production program and verify one independent claim."""

from io import BytesIO
import json
from pathlib import Path
from subprocess import run
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bootstrap import install


def product(runtime):
    from band_product import multiply, multiply_tapes, production_supplier
    from check_product import physical_product
    from installations import ENTRY, TERMINAL

    assert all(
        multiply(a, b) == a * b
        for a, b in (
            (0, 0),
            (-1, 0),
            (-1, -1),
            (-741503, 466013),
            (2**129 - 17, -(2**73) + 3),
            (-(2**4096 + 9), 2**41 - 1),
        )
    )
    for tier in (ENTRY, TERMINAL):
        left = BytesIO(b"abc" + (741503).to_bytes(6, "little") + b"finish")
        right = BytesIO(b"xyz" + (466013).to_bytes(5, "little") + b"end")
        left.seek(3)
        right.seek(3)
        destination = BytesIO()
        sign, size = multiply_tapes(
            left, 6, right, 5, destination, left_negative=True, profile=tier
        )
        assert (sign, size, int.from_bytes(destination.getvalue(), "little")) == (
            True,
            5,
            345550037539,
        )
        assert left.tell() == right.tell() == 3
        recipe = production_supplier(
            tier.complex_log, tier.positive_stop_denominator
        ).recipe
        assert (
            recipe.rank_log == tier.complex_log
            and recipe.ambient == 306
            and len(recipe.cells) == 51
        )
    witness = physical_product(ENTRY)
    assert witness["product"] == "-345550037539" and witness["coefficients_prefix"] == [
        11811,
        10996,
        4152,
        868,
        77,
    ]
    print(json.dumps(witness, sort_keys=True))
    print("PASS_WEIGHTED_SIGNED_PRODUCT")


def main(scope):
    if not __debug__:
        raise RuntimeError("Enable assertions for the registered checks")
    with TemporaryDirectory(prefix="weighted-native-") as temp:
        runtime = Path(temp)
        install(runtime)
        sys.path.insert(0, str(runtime))
        if scope == "product":
            product(runtime)
            return
        files = {
            "price": ("receipt.py", "check_placement.py"),
            "calendar": ("check_calendar.py", "check_ownership.py"),
            "raw": ("check_raw.py",),
            "exterior": ("check_exterior.py",),
            "nested": ("check_nested.py",),
        }
        for name in files[scope]:
            out = run(
                [sys.executable, "-IB", str(HERE / name), str(runtime)],
                check=True,
                capture_output=True,
                text=True,
            )
            if name == "receipt.py":
                assert json.loads(out.stdout) == json.loads(
                    (HERE / "RESULT.json").read_bytes()
                )
                print(
                    "PASS_WEIGHTED_COMPLETE_PRICE",
                    json.loads(out.stdout)["complete_log2_C"],
                )
            else:
                print(out.stdout, end="")


if __name__ == "__main__":
    main(sys.argv[1])
