"""Run one self-contained research check with the stated source versions."""

from argparse import ArgumentParser
from fractions import Fraction
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from upstream import install

_, native, bounded, source = install()
data = HERE / "inputs"
grade = source / "research/grade14-native-realization"


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=(
            "price",
            "band",
            "binary",
            "grid",
            "atlas",
            "physical",
            "product",
            "dense",
            "resources",
            "wide-product",
        ),
    )
    mode = parser.parse_args().mode
    if mode == "price":
        from calibration import PROFILES
        from strict_moment import both
        from strong_binary import native_word
        from strong_complex import word, load_changed
        from resources import all_profiles
        from prior_setup import compare
        from check_linear_geometry import run
        from inputs.triangular.multiplier import precision

        positive = word(*load_changed(data))
        for name, profile in PROFILES.items():
            result = both(native_word(profile.power), positive, profile)
            print(name, *(r["surplus_lower_units_1e12"] for r in result))
        receipt = json.loads(json.dumps(all_profiles()))
        assert receipt == json.loads((HERE / "REQUIREMENTS.json").read_bytes())
        print(json.dumps(receipt, sort_keys=True))
        print(run(precision))
        print(compare(receipt))
    elif mode == "band":
        runpy.run_path(str(HERE / "check_band.py"), run_name="__main__")
        from check_epoch_reentry import trial

        print(trial())
    elif mode == "dense":
        from check_dense_band import dense

        print(dense())
    elif mode == "binary":
        from check_strong_binary import main as binary
        from check_weighted_binary import weighted

        binary()
        weighted()
    elif mode == "grid":
        from check_strong_complex import literal_grid
        from strong_complex import load_changed

        result = literal_grid(*load_changed(data))
        print(json.dumps(result, sort_keys=True))
    elif mode == "atlas":
        from check_strong_complex import atlas, caller
        from strong_complex import load_changed

        g, l = load_changed(data)
        mass = Fraction(
            205356183613728386434052488657699504746980105023, 1621896683681232672237748224000
        )
        print(json.dumps(atlas(grade, g, l, data), sort_keys=True))
        print(json.dumps(caller(grade, g, l, data, mass), sort_keys=True))
    elif mode == "physical":
        from check_strong_physical import run
        from check_strong_raw_word import run as raw

        print(run(grade, data), raw(grade, data))
    elif mode == "product":
        from check_product import physical_product

        print(json.dumps(physical_product()), flush=True)
    elif mode == "wide-product":
        from check_product import matched

        for row in matched(wide=True):
            print(json.dumps(row), flush=True)
    else:
        from resources import all_profiles

        print(json.dumps(all_profiles(), indent=2, sort_keys=True))
        return
    print("PASS_NATIVE_SCALE", mode, flush=True)


if __name__ == "__main__":
    main()
