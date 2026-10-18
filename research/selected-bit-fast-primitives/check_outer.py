"""The completed ordinary wrapper with C1, preserving the sealed C0 backend."""
from pathlib import Path
from time import monotonic
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
stage_sources.activate()
from check_engine import fixture_engine, check_case, binary_fitted
from compile_routes import Registry
from stage import promote_ordinary


def run():
    started = monotonic()
    outer = promote_ordinary(fixture_engine(), fixture_engine(), Registry(2))
    result = [check_case(outer, 5, 1, 1, 1, True),
              check_case(outer, 2, 2, 3, 2, False),
              binary_fitted(outer)]
    print("complete ordinary successor seconds", round(monotonic()-started,2), flush=True)
    return dict(cases=result, successor_calls=outer.runtime.pool.adapter.calls,
                scope="Reduced q2 wrapper and binary completion around C1; preceding ordinary calls use the elementary branch")


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_COMPLETED_ORDINARY_SUCCESSOR")
