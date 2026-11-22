"""Run an isolated check on the pinned and integrated signed multiplier."""

from argparse import ArgumentParser
from pathlib import Path
import runpy
import sys
from tempfile import TemporaryDirectory

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bootstrap import install


def main():
    options = ArgumentParser(description=__doc__)
    options.add_argument("mode", choices=("census", "price", "raw", "product"))
    mode = options.parse_args().mode
    if sys.version_info[:2] != (3,12) or not __debug__:
        raise RuntimeError("Use Python 3.12 with assertions enabled")
    with TemporaryDirectory(prefix="counted-native-bands-") as work:
        tree = Path(work) / "machine"
        tree.mkdir()
        install(tree)
        sys.path.insert(0, str(tree))
        from upstream import install as dependencies
        dependencies()
        if mode == "census":
            runpy.run_path(str(HERE / "check_census.py"), run_name="__main__")
        elif mode == "price":
            import json
            from check_resources import inventory
            assert json.loads(json.dumps(inventory())) == json.loads((HERE / "RESULT.json").read_bytes())
        elif mode == "raw":
            runpy.run_path(str(HERE / "check_raw.py"), run_name="__main__")
        else:
            from calibration import SMALL_GAP
            from check_product import physical_product
            info = physical_product(SMALL_GAP)
            assert info["product"] == "-345550037539" and info["shuttles"] == 138
            assert info["coefficients_prefix"] == [11811,10996,4152,868,77]
            print(info)
    print("PASS_COUNTED_NATIVE_BANDS", mode)


if __name__ == "__main__":
    main()
