"""Build a clean signed machine and check the requested construction evidence."""

from argparse import ArgumentParser
import json
from pathlib import Path
import resource
import runpy
import sys
from tempfile import TemporaryDirectory
from time import perf_counter, process_time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from bootstrap import install


def check(mode, tree):
    baseline = mode == "original-setup"
    install(tree, baseline)
    sys.path.insert(0, str(tree))
    start, cpu = perf_counter(), process_time()
    import band_product
    from installations import RESOLUTION

    if mode in ("setup", "original-setup"):
        recipes = band_product.prepare_native(RESOLUTION)
        supplier = band_product.production_supplier(
            RESOLUTION.complex_log, RESOLUTION.positive_stop_denominator
        )
        assert supplier.recipe is recipes[-1]
        assert tuple(x.rank_log for x in recipes) == (
            *RESOLUTION.rank_logs,
            RESOLUTION.complex_log,
        )
        assert (
            len(recipes[-1].targets),
            len(recipes[-1].paid),
            len(recipes[-1].cells),
        ) == (105216, 564144, 54)
        peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        print(
            json.dumps(
                dict(
                    mode=mode,
                    wall_s=perf_counter() - start,
                    cpu_s=process_time() - cpu,
                    peak_process_bytes=peak
                    if sys.platform == "darwin"
                    else 1024 * peak,
                )
            )
        )
    elif mode == "phase":
        runpy.run_path(str(HERE / "check_gauss.py"), run_name="__main__")
        import charts
        from phase_atlas import catalogue
        from strong_complex import load_changed, digest

        graph, layout = load_changed(tree / "inputs")
        built = catalogue(graph, layout)
        assert (
            digest(built)
            == "8a9ff9558bf5fa3854699937fe063f98c86467d5d32a4488bfc878d2be081e70"
        )
        assert charts.native_catalogue(graph, layout, stored=built) == built
        a, b, record = built["pairs"][0]
        tampered = dict(
            record, left=dict(record["left"], phase=(record["left"]["phase"] + 1) % 4)
        )
        frames = graph["frames"]
        reviewer = charts.check_clifford
        try:
            reviewer.equal(
                reviewer.recipe(tampered),
                reviewer.adjoint(reviewer.frame(tuple(frames[a]), 9))
                + reviewer.frame(tuple(frames[b]), 9),
                "mutated phase",
            )
        except ValueError as exc:
            assert "exact global phase" in str(exc)
        else:
            raise AssertionError(
                "The independent verifier accepted a changed unit phase"
            )
        print(
            "Independent all-column/tableau and absolute phase records:",
            len(built["pairs"]),
            2 * len(built["ports"]),
        )
    elif mode == "cost":
        runpy.run_path(str(HERE / "census.py"), run_name="__main__")
        runpy.run_path(str(HERE / "check_labels.py"), run_name="__main__")
    elif mode == "physical":
        runpy.run_path(str(tree / "check_nonzero_eight.py"), run_name="__main__")
    elif mode == "product":
        from check_product import one

        assert (
            band_product.multiply(-741503, 466013, profile=RESOLUTION) == -345550037539
        )
        assert band_product.multiply(0, -466013, profile=RESOLUTION) == 0
        machine = band_product.Product((3, 5), 8, 136, profile=RESOLUTION)
        product = one(machine, -741503, 466013)
        assert product["H_calls"] == 157248 and product["coefficients_prefix"] == [
            11811,
            10996,
            4152,
            868,
            77,
        ]
        print(json.dumps(product))
    print("PASS_QUADRATIC_INSTALLATION", mode, flush=True)


if __name__ == "__main__":
    cli = ArgumentParser(description=__doc__)
    cli.add_argument(
        "mode",
        choices=("phase", "setup", "original-setup", "cost", "physical", "product"),
    )
    opts = cli.parse_args()
    if sys.version_info[:2] != (3, 12) or not __debug__:
        raise RuntimeError("Use Python 3.12 with assertions enabled")
    with TemporaryDirectory(prefix="phase-install-") as folder:
        check(opts.mode, Path(folder) / "machine")
