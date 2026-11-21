"""Run a named certificate on the packaged source files with Python 3.12."""

from argparse import ArgumentParser
from pathlib import Path
import runpy
import sys

here = Path(__file__).resolve().parent
sys.path.insert(0, str(here))
from source_inputs import activate


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "check",
        nargs="+",
        choices=(
            "prices",
            "geometry",
            "placement",
            "envelope",
            "crt",
            "product",
            "atoms",
            "cuts",
            "cohort",
            "raw-binary",
            "sparse",
            "raw-complex",
            "physical",
            "stock",
        ),
    )
    args = parser.parse_args()
    prior, root = activate()
    grade = root / "research/grade14-native-realization"
    cases = {
        "prices": ("bound.py",),
        "geometry": ("test_outer.py", root, prior / "retained/fourier"),
        "envelope": ("check_envelope.py",),
        "placement": ("check_placement.py",),
        "crt": ("check_crt_tree.py",),
        "product": ("check_binary_io.py", "--fourier"),
        "atoms": ("check_module_atoms.py", prior),
        "cuts": ("check_compiler_cut.py", prior),
        "cohort": ("check_growing_binary.py", prior),
        "raw-binary": ("check_raw_binary.py", prior),
        "sparse": ("check_raw_delta.py", prior),
        "raw-complex": ("test_raw48.py", prior, grade),
    }
    for check in args.check:
        if check in cases:
            suite = [cases[check]]
        elif check == "stock":
            suite = [
                ("measure_stock.py", prior, mode) for mode in ("scalar", "split", "split-matched")
            ]
            suite.append(("measure_stripes.py", prior, here, "81"))
        else:
            physical(prior, root)
            print("PASS_NATIVE_STOCK", check, flush=True)
            continue
        for name, *parameters in suite:
            execute(name, parameters)
        print("PASS_NATIVE_STOCK", check, flush=True)


def execute(name, parameters):
    sys.argv = [str(here / name), *map(str, parameters)]
    runpy.run_path(sys.argv[0], run_name="__main__")


def physical(prior, root):
    import os
    import subprocess
    from tempfile import TemporaryDirectory

    with TemporaryDirectory() as scratch:

        def build(name):
            path = Path(scratch) / (name + ".so")
            subprocess.run(
                [
                    os.environ.get("CC", "cc"),
                    "-std=c11",
                    "-O3",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fPIC",
                    "-shared",
                    str(here / (name + ".c")),
                    "-o",
                    str(path),
                ],
                check=True,
            )
            return path

        from io import BytesIO
        from short_product import native_product
        from product_path import Product, multiply, multiply_tapes

        library = build("packet_tapes")
        kernel = native_product(build("short_product"))
        calls = []

        def observed(a, b):
            calls.append((len(a), len(b)))
            return kernel(a, b)

        a, b = (1 << 4333) - 65, (1 << 4211) + 7
        assert multiply(-a, b, observed) == -a * b
        x, y = (v.to_bytes((v.bit_length() + 7) // 8, "little") for v in (a, b))
        output = BytesIO()
        assert multiply_tapes(
            BytesIO(x), len(x), BytesIO(y), len(y), output, left_negative=True, engine=observed
        ) == (True, (abs(a * b).bit_length() + 7) // 8)
        assert int.from_bytes(output.getvalue(), "little") == a * b
        assert Product((3,), 5, 100, engine=observed).grid.scalar_product(-a, b) == -a * b
        assert calls == [(542, 527)] * 3
        print("PASS_RETAINED_PACKED_SCALAR", calls)
        execute("check_split_product.py", (prior, root, library))
        execute("check_stripe.py", (prior, root, here, library))
        execute("check_striped_tensor.py", (prior, root, here, library))


if __name__ == "__main__":
    main()
