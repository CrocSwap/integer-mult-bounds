"""Replay the general density checks from the frozen independent review."""

import importlib.util
import json
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
PHYS = PACKAGE / "evidence/lanes/residual-syndrome/physical-algebra"
REVIEW = PHYS / "correlated-sector-review/review_sector.py"
QUOTIENT = PACKAGE / "evidence/lanes/coherent-port/shared-cover-quotient-20261015/QUOTIENT.json"


def main():
    spec = importlib.util.spec_from_file_location("affine_density_review", REVIEW)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    source = {"receipt": json.loads(QUOTIENT.read_text())}
    result = {
        "status": "PASS_AFFINE_DENSITY_MATH",
        "small_quotients": module.small_quotients(),
        "small_binary_gauss_counts": module.small_gauss_sums(),
        "literal_original_character_walks": module.small_walks(),
        "exact_distributions": module.distributions(source),
        "scope": "General quotient, Gauss sum, walk, and density checks only.",
        "not_replayed": ["Actual route reconstruction", "Actual 17-axis maximal frame sector"],
    }
    expected = json.loads((PHYS / "correlated-sector-review/REVIEW.json").read_text())
    for key in ("small_quotients", "small_binary_gauss_counts",
                "literal_original_character_walks", "exact_distributions"):
        if result[key] != expected[key]:
            raise ValueError("Density review result differs: " + key)
    Path("RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])


if __name__ == "__main__":
    main()
