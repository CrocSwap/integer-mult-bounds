#!/usr/bin/env python3
"""Restore the exact predecessor, install this construction and check its paths."""

from argparse import ArgumentParser
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bootstrap import install


def check(mode, tree):
    install(tree)
    sys.path.insert(0, str(tree))
    from upstream import install as dependencies

    dependencies()
    if mode == "cost":
        from check_complete import verify

        verify()
    elif mode == "product":
        from installations import EXTENDED
        from check_product import physical_product
        import band_product

        observed = []

        def first_dispatch(frame, event, arg):
            if event == "call" and frame.f_code is band_product.h_pack.__code__:
                call = frame.f_locals
                assert call["machine"].profile is EXTENDED
                assert call["make_supplier"].func is band_product.production_supplier
                observed.append((call["rank_log"], call["make_supplier"].args, call["machine"].total))
                sys.setprofile(None)

        sys.setprofile(first_dispatch)
        try:
            info = physical_product(EXTENDED)
        finally:
            sys.setprofile(None)
        assert observed == [(EXTENDED.complex_log, (EXTENDED.complex_log, EXTENDED.positive_stop_denominator), 32)]
        assert info["product"] == "-345550037539" and info["shuttles"] == 138
        assert info["coefficients_prefix"] == [11811, 10996, 4152, 868, 77]
        print(info)
    else:
        files = {
            "binary": ["check_binary_k7", "check_binary_word"],
            "schedule": ["check_chronology", "check_precision", "check_streamed", "check_reentry"],
            "install": ["check_installation", "check_scans"],
            "physical": ["check_binary_word", "check_positive_word", "check_extended_stop"],
            "receiver": ["check_five", "check_nonzero_eight", "direct_exact"],
            "slabs": ["check_stage_fences", "check_stage_inventory"],
        }
        for name in files[mode]:
            runpy.run_path(str(HERE / (name + ".py")), run_name="__main__")
    print("PASS_K7_RETIMED_BINARY", mode)


def main():
    parser = ArgumentParser(description="Restore the exact predecessor, install the k7 retimed construction and verify it.")
    parser.add_argument(
        "mode",
        choices=("binary", "cost", "schedule", "install", "physical", "receiver", "slabs", "product"),
    )
    args = parser.parse_args()
    with TemporaryDirectory() as root:
        check(args.mode, Path(root) / "tree")


if __name__ == "__main__":
    main()
