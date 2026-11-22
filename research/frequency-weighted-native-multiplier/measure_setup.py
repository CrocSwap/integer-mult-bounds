"""Measure fixed setup through all native recipes of the selected signed multiplier."""

from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path
import platform
import resource
import runpy
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

HERE = Path(__file__).resolve().parent


def cpu():
    times = [
        resource.getrusage(who)
        for who in (resource.RUSAGE_SELF, resource.RUSAGE_CHILDREN)
    ]
    return sum(t.ru_utime + t.ru_stime for t in times)


def measure(preceding, peer=None):
    package = HERE.parent / "tiered-native-multiplier" if preceding else HERE
    start, used = perf_counter(), cpu()
    with TemporaryDirectory(prefix="fixed-weighted-") as tmp:
        path = Path(tmp) / "program"
        if peer is not None:
            loader = peer / "prepare.py"
            if sha256(loader.read_bytes()).hexdigest() != (
                "1a4d885677ba9bd435927d5c400f598dc35c6a793686389a1fb84a1f49d6096e"
            ):
                raise ValueError(
                    "Use the rounded-packet source at c5cbef6e558542d6e809aabb6ead89b9e51f7b1c"
                )
            package = Path(tmp) / "peer"
            runpy.run_path(str(loader))["materialize"](
                peer / "peer8054", peer / "round370", package
            )
        runpy.run_path(str(package / "bootstrap.py"))["install"](path)
        sys.path.insert(0, str(path))
        from band_product import prepare_native
        from installations import PROFILES

        if peer is None:
            recipes = prepare_native()
            terminal = (
                [35327, 559005, 680000] if preceding else [8192, 129414, 524288, 483871]
            )
            expected = [[3000, 3080, 1024], terminal]
            assert recipes[0][-1].cells is recipes[1][-1].cells
            model = "dilation79" if preceding else "frequency90"
            expected_cells = 62 if preceding else 51
        else:
            recipes = (prepare_native(PROFILES["extended"]),)
            expected = [[60000, 960000, 20000000]]
            gaussian = recipes[0][-1]
            assert (len(gaussian.targets), len(gaussian.paid)) == (105216, 564142)
            model, expected_cells = "rounded_quarters", 55
        ranks = [[item.rank_log for item in row] for row in recipes]
        assert ranks == expected
        cells = len(recipes[0][-1].cells)
        assert cells == expected_cells
        graph = sha256((path / "strong-bit.json.gz").read_bytes()).hexdigest()
        assert (
            graph == "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362"
        )
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(
        json.dumps(
            dict(
                model=model,
                wall=perf_counter() - start,
                cpu=cpu() - used,
                rss_bytes=rss if sys.platform == "darwin" else 1024 * rss,
                python=platform.python_version(),
                system=platform.platform(),
                ranks=ranks,
                gaussian_grade_cells=cells,
                binary_sha256=graph,
            )
        )
    )


if __name__ == "__main__":
    options = ArgumentParser(description=__doc__)
    group = options.add_mutually_exclusive_group()
    group.add_argument("--preceding", action="store_true")
    group.add_argument(
        "--quarter-peer",
        type=Path,
        help="Path to the source-bound PR 8056 research package",
    )
    args = options.parse_args()
    measure(args.preceding, args.quarter_peer.resolve() if args.quarter_peer else None)
