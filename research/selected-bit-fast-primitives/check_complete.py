"""Full retained four-family caller with the new primitive bindings."""
from fractions import Fraction as F
from pathlib import Path
from time import monotonic
import json
import sys
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stage_sources
stage_sources.activate()
from check_routes import native_fixture
from compile_routes import Registry
import macro_local_checks as retained
import model
from stage import successor_machine
from words import BLANK, need


def run():
    started = monotonic()
    registry = Registry(2)
    registry.register(model.S, (("swap",0,1,F(1)),))
    native = native_fixture(3)
    observed = []
    def machine(binding, topology, programs, arena, indices, observe=None):
        runtime = successor_machine(binding, topology, programs, arena, indices, native, registry, observe)
        observed.append(runtime)
        return runtime
    with patch.object(retained, "Machine", machine):
        result = retained.run()
    need(len(observed) == 1, "one complete generated successor")
    runtime = observed[0]
    need(runtime.pool.adapter.calls["swaps"] > 0 and runtime.pool.adapter.calls["cubes"] > 0,
         "both successor sites reached throughout the whole caller")
    work = [*native.pool.tapes, *native.runtime.roles.values(), *native.runtime.handoff.values(),
            *native.runtime.pool.tapes, native.runtime.output, native.output]
    for bank in (*native.banks, native.runtime.arena, native.runtime.indices, runtime.pool.adapter.high_bank):
        need(not bank.live and not bank.initialized, "whole caller closes preceding numerical work")
        work.extend(word.tape for word in (*bank.words, bank.template))
    need(all(all(bit == BLANK for bit in tape.cells) for tape in work), "whole preceding stage erasure")
    result["successor_calls"] = runtime.pool.adapter.calls
    result["scope"] = "Complete retained q3/w1 four-family model; B1 uses its elementary branch"
    print("complete four-family successor seconds", round(monotonic()-started,2), flush=True)
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
    print("PASS_FOUR_FAMILY_SUCCESSOR")
