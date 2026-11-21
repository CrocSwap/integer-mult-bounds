"""Run the physical, arithmetic and price checks against the packaged sources."""

from argparse import ArgumentParser
from pathlib import Path
import runpy
import sys

base = Path(__file__).resolve().parent
sys.path.insert(0, str(base))
from retained import install


def execute(name, *args):
    sys.argv = [str(base / name), *map(str, args)]
    runpy.run_path(sys.argv[0], run_name="__main__")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "case",
        choices=("prices", "quotient", "body", "raw", "whole", "product", "movement", "numerics"),
    )
    case = parser.parse_args().case
    _, source, prior, _ = install()
    if case == "prices":
        execute("staged_carriers.py")
        execute("first_peak.py")
        execute("check_active_forest.py", prior, source, base)
        execute("check_uniform_space.py")
        execute("scale_audit.py", source)
    elif case == "quotient":
        execute("check_quotient_route.py", prior, "--large")
        execute("check_limb_scale.py", prior)
    elif case == "body":
        execute("check_direct_body.py", source, prior)
    elif case == "raw":
        execute("check_raw_body.py", source, prior)
    elif case == "whole":
        execute("check_receiver.py")
        execute("check_active_slots.py")
    elif case == "numerics":
        execute("check_precision.py")
    elif case == "movement":
        from check_integration import movement

        movement()
    else:
        from check_integration import native_product, public_files

        public_files()
        native_product()
    print("PASS_TRIANGULAR", case, flush=True)


if __name__ == "__main__":
    main()
