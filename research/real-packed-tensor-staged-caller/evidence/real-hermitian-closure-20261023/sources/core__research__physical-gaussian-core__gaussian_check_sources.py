"""Exact dependencies, one physical cohort and actual acyclic child owners."""
from hashlib import sha256
import importlib
from pathlib import Path
from unittest.mock import patch
import gaussian_sources
from gaussian_sources import HERE, require

REFERENCES = {
    "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md":
        "3cdf492bcb719db4295658604dc202d6a2c5a008b87de43ec54f0107c64db730",
    "references/semantic-bulk/rad20/reports/downstream-microbox-resampling.md":
        "9598c236eed7e44ac5eb41cc20f7c23249829e195247d15e2857a34e14222c49",
    "references/semantic-bulk/rad20/reports/bulk-resampling-tape-transfer.md":
        "cda26d5aca04b9c824eb6c4f50bee564fb7fa908b09a72e76852df5e0b9d2622",
    "references/semantic-bulk/rad20/reports/review-phase-cell-inverse.md":
        "113927dd4fb77a55a457bd5f6da8cbfc7262d0fbc4e9d708b591a1d632e6caf6",
    "references/semantic-bulk/rad20/reports/review-reusable-banded-inverse.md":
        "801359569c92f9d5ddd128b694993a5ac22a468e87bfea478cecc0ee413d058b",
    "references/semantic-bulk/rad20/LICENSE":
        "a2010f343487d3f7618affe54f789f5487602331c0a8d03f49e9a7c547cf0499",
    "references/semantic-bulk/rad20/NOTICE":
        "82fc72aff49769ae82a8ce886846d9bd0601827a09c955042d26a61177d14369",
    "references/semantic-bulk/rad20/SOURCE.json":
        "63477ee5103e4c1d0d1665bf2d1cfb91af5bcdef59cac6e46f4d6a1579b8eb2e",
}


def check_references():
    for path, digest in REFERENCES.items():
        require(sha256((HERE.parents[1] / path).read_bytes()).hexdigest() == digest,
                "pinned Gaussian analytic source: " + path)


def run():
    from cardinal_counts import Count
    from records import Tape
    from word_product import WordProduct
    from gaussian_core import Core
    from gaussian_prepare import Preparation
    gaussian_sources.authenticate()
    check_references()
    modules = ("gaussian_rationals", "gaussian_matrix", "gaussian_rows", "gaussian_convolution",
               "gaussian_exponentials", "gaussian_interior", "gaussian_axis", "gaussian_boundary",
               "gaussian_window", "gaussian_page", "gaussian_core", "gaussian_prepare")
    for name in modules:
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == HERE / (name + ".py"), "package-local Gaussian runtime")
        for key, expected in (("Count", Count), ("Tape", Tape)):
            if hasattr(module, key):
                require(getattr(module, key) is expected, "one shared Gaussian physical type cohort")
    core, preparation = Core(), Preparation()
    require(core.word is core.interior.word is core.interior.convolution.word is core.boundary.word,
            "one actual Gaussian word owner across the complete consumer")
    require(type(core.word.base) is WordProduct and type(core.word.product.word) is WordProduct
            and core.word.base_bits == 4096, "fixed-crossover acyclic Gaussian word dependency")
    core.idle()
    require(core.closed and preparation.closed and not core.pool.live and not preparation.pool.live,
            "closed physical source owners")
    with patch.object(gaussian_sources, "DIGEST", "0"*64):
        try:
            gaussian_sources.authenticate()
        except ValueError as error:
            require("pinned Gaussian word source" in str(error), "changed word archive rejection")
        else:
            raise ValueError("missing changed word archive rejection")
    with patch.dict(REFERENCES, {next(iter(REFERENCES)): "0"*64}):
        try:
            check_references()
        except ValueError as error:
            require("pinned Gaussian analytic source" in str(error), "changed analytic binding rejection")
        else:
            raise ValueError("missing changed analytic binding rejection")
    try:
        with gaussian_sources.opened():
            raise ValueError("second Gaussian cohort opened")
    except ValueError as error:
        require("cold Gaussian namespace" in str(error), "second Gaussian cohort rejection")
    return {"word_head": gaussian_sources.HEAD, "branchfree_head": gaussian_sources.REFERENCE_HEAD,
            "word_export_files": 21, "branchfree_package_files": 9, "runtime_modules": list(modules),
            "analytic_inputs": REFERENCES, "controls": ["word_archive_binding", "analytic_binding", "second_cohort"]}
