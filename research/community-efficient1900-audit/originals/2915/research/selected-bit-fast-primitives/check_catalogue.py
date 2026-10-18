"""Bind the retained factor registry to every selected owner chart type."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
stage_sources.activate()
from catalogue import Catalogue
from compile_routes import selected_registry
from routes import Route, compile_route
from words import need


def run():
    catalogue = Catalogue(3)
    registry, receipt = selected_registry(catalogue)
    retained = receipt["retained"]
    ordinary = Fraction(2*(retained["data_occurrence_total"]["ordinary"] +
                           retained["hosted_occurrence_total"]["ordinary"]), 28416)
    need(ordinary == Fraction(1598048,111), "retained full entrance/return ordinary invoice")
    identity = tuple(tuple(int(i == j) for j in range(64)) for i in range(64))
    digest, cases, producer_probe = sha256(), 0, False
    for matrix in sorted(registry.words, key=repr):
        # With identity input low, the target is the reduced chart itself.
        # Every registered factor is a q-unit elementary map. Re-running full
        # GL64 inversion for each chart would duplicate that checked invariant.
        target = tuple(tuple(value.numerator*pow(value.denominator, -1, 3) % 3
                             for value in row) for row in matrix)
        route = Route(3, 64, identity, target, matrix)
        if not producer_probe and matrix != identity:
            need(route == compile_route(identity, matrix, catalogue.codes), "actual producer Route fields")
            producer_probe = True
        operations = registry.compile(route)
        need(all(operation[0] in ("swap", "add", "double", "half", "negate", "translate")
                 for operation in operations), "closed selected high vocabulary")
        digest.update(json.dumps(operations, separators=(",", ":")).encode())
        cases += 1
    return dict(source_types=receipt["source_types"], oriented_matrices=cases,
                low_carry_program_sha256=digest.hexdigest(),
                actual_producer_probe=producer_probe,
                ordinary_numerator=ordinary.numerator, ordinary_denominator=ordinary.denominator,
                scope="All selected owner chart matrices and inverses; one identity low class each, no high payload")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_SELECTED_FACTOR_BINDINGS")
