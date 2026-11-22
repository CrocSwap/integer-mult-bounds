"""Restore the exact predecessor, install this construction and check its public path."""

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
        from installations import RESOLUTION
        from check_product import physical_product
        import band_product
        observed = []

        def first_dispatch(frame, event, arg):
            if event == "call" and frame.f_code is band_product.h_pack.__code__:
                call = frame.f_locals
                assert call["machine"].profile is RESOLUTION
                assert call["make_supplier"].func is band_product.production_supplier
                observed.append((call["rank_log"], call["make_supplier"].args, call["machine"].total))
                sys.setprofile(None)

        sys.setprofile(first_dispatch)
        try:
            info = physical_product(RESOLUTION)
        finally:
            sys.setprofile(None)
        assert observed == [(19000, (19000, 10**21), 32)]
        assert info["product"] == "-345550037539" and info["shuttles"] == 138
        assert info["coefficients_prefix"] == [11811, 10996, 4152, 868, 77]
        print(info)
    else:
        files = {"schedule": ["check_streamed", "check_chronology", "check_reentry"],
                 "physical": ["check_binary_word", "check_positive_word", "check_nonzero_eight", "check_precision"],
                 "install": ["check_installation", "check_resolution_stop"],
                 "witness": ["check_nonzero_eight"],
                 "deep-receiver": ["true_high", "direct_recursive"],
                 "receiver": ["normal_five", "direct_exact", "check_five", "low_inventory_scan"],
                 "slabs": ["check_scans"]}
        for name in files[mode]:
            runpy.run_path(str(HERE / (name + ".py")), run_name="__main__")
    print("PASS_RETIMED_MULTIPLIER", mode)


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument("mode", choices=("cost", "schedule", "install", "physical", "product", "slabs", "receiver", "witness", "deep-receiver"))
    command = cli.parse_args().mode
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use Python 3.12 with assertions enabled")
    with TemporaryDirectory(prefix="retimed-multiplier-") as folder:
        tree = Path(folder) / "machine"
        tree.mkdir()
        check(command, tree)
