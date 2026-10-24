"""Whole predecessor binding, shared types and acyclic multiplier ownership."""
from hashlib import sha256
import importlib
from pathlib import Path
from unittest.mock import patch
import fft_word_sources
from fft_word_sources import HERE, active, require


def run():
    from cardinal_counts import Count
    from records import Tape
    from fft_word_engine import FftWord
    from word_product import WordProduct
    fft_word_sources.authenticate()
    state = active()
    modules = ("fft_word_plan", "fft_word_codec", "fft_word_engine")
    for name in modules:
        module = importlib.import_module(name)
        require(Path(module.__file__).resolve() == HERE / (name + ".py"), "local FFT-word module")
        for key, canonical in (("Count", Count), ("Tape", Tape)):
            if hasattr(module, key):
                require(getattr(module, key) is canonical, "one FFT-word physical class")
    owner = FftWord()
    require(type(owner.product) is state.ring.RingProduct and type(owner.base) is WordProduct
            and type(owner.product.word) is WordProduct and owner.product.arithmetic.word is owner.product.word,
            "acyclic actual normalized-product and Karatsuba children")
    owner.idle()
    inputs = {
        "references/semantic-bulk/rad20/reports/downstream-phase-cell-inverse.md":
            "3cdf492bcb719db4295658604dc202d6a2c5a008b87de43ec54f0107c64db730",
        "references/semantic-bulk/rad20/reports/downstream-microbox-resampling.md":
            "9598c236eed7e44ac5eb41cc20f7c23249829e195247d15e2857a34e14222c49",
    }
    for path, digest in inputs.items():
        require(sha256((HERE.parents[1] / path).read_bytes()).hexdigest() == digest,
                "pinned Gaussian arithmetic source")
    with patch.object(fft_word_sources, "DIGEST", "0"*64):
        try:
            fft_word_sources.authenticate()
        except ValueError as error:
            require("pinned FFT-word source bytes" in str(error), "changed source binding rejection")
        else:
            raise ValueError("missing source binding rejection")
    try:
        with fft_word_sources.opened():
            raise ValueError("second FFT-word runtime opened")
    except ValueError as error:
        require("cold FFT-word namespace" in str(error), "second runtime rejection")
    return {"predecessor_head": fft_word_sources.HEAD, "export_sha256": fft_word_sources.DIGEST,
            "predecessor_files": 26, "runtime_modules": list(modules), "inputs": inputs,
            "controls": ["changed_archive_binding", "second_runtime"], "acyclic_children": True}
