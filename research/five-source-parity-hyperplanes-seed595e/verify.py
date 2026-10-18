"""Rebuild and compare the exact parity-hyperplane certificate."""
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_analyzer():
    spec = importlib.util.spec_from_file_location("parity_hyperplane_analyzer", HERE / "analyze.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    observed = load_analyzer().build_certificate()
    recorded = json.loads((HERE / "CERTIFICATE.json").read_text())
    assert observed == recorded, "regenerated certificate differs"
    print(
        "PASS_FIVE_SOURCE_PARITY_HYPERPLANES "
        "families=62 symmetry_classes=10 minima=38,40,42,44 "
        "ten_words=945 scalar_dirty_checks=246016"
    )


if __name__ == "__main__":
    main()
