"""Measure fixed setup for either signed multiplier in a new host process."""

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


def measure(preceding):
    package = HERE.parent / "tiered-native-multiplier" if preceding else HERE
    start, used = perf_counter(), cpu()
    with TemporaryDirectory(prefix="fixed-weighted-") as tmp:
        path = Path(tmp) / "program"
        runpy.run_path(str(package / "bootstrap.py"))["install"](path)
        sys.path.insert(0, str(path))
        from band_product import prepare_native

        recipes = prepare_native()
        ranks = [[item.rank_log for item in row] for row in recipes]
        assert len(ranks) == 2 and all(len(row) == 3 for row in ranks)
        assert recipes[0][-1].cells is recipes[1][-1].cells
        cells = len(recipes[0][-1].cells)
        assert cells == (62 if preceding else 51)
        graph = sha256((path / "strong-bit.json.gz").read_bytes()).hexdigest()
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    print(
        json.dumps(
            dict(
                model="dilation79" if preceding else "frequency90",
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
    options.add_argument("--preceding", action="store_true")
    measure(options.parse_args().preceding)
