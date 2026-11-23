#!/usr/bin/env python3
"""Reconstruct #8072 and exercise the actual fixed constructors at larger heights.

The standalone serial arithmetic bound is a separate exact calculation. The
directory census is supporting finite evidence, not a claimed portable trace.
"""

from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent))
from witness import source_runtime


def safe_height(h):
    return isinstance(h, int) and 1024 <= h < 2**25


def bounded_scalars(profile):
    """Bound supplied profile encodings; no rate admissibility is implied."""
    values = (profile.kappa.numerator, profile.kappa.denominator,
              profile.eta.numerator, profile.eta.denominator,
              profile.positive_stop_denominator)
    return (all(isinstance(x, int) and abs(x).bit_length() <= 128 for x in values)
            and profile.positive_stop_denominator > 0)


def action_envelope():
    # Original 2**68 indexed actions plus a deliberately overgenerous 2**40
    # actions for new parameter installation, carrier bit writes and cleanup.
    # This is added, not assumed to fit an unspecified old action margin.
    w = 2**38
    n = 2**68 + 2**40
    h = 2*w + 2
    store = 4*w*n
    lookup = 8*store*512*128
    local = 2**16*(h+4)*(7*h+9) + 8*2**16*(h+4)**2
    total = (n+1)*(lookup+local+2**120)*2**32
    assert total < 2**228
    return {"max_datum_bits": w, "old_actions": 2**68,
            "added_action_ceiling": 2**40, "max_actions": n,
            "store_cells_upper": store, "lookup_upper": lookup,
            "local_arithmetic_upper": local, "transition_upper": total,
            "transition_power_of_two_upper": 228}


def run():
    if not __debug__:
        raise ValueError("Run this witness with assertions enabled")
    assert safe_height(2**25-1) and not safe_height(2**25)
    assert 92*(2**25-1) < 2**32 and 1024*(2**25-1)+3 < 2**35
    # Two serial 25-bit-countdown carrier constructions, generously allowing
    # 2048 summed fixed-multitape moves/writes per bit for the countdown, up to
    # sixteen output streams, head restoration and cleanup.
    carrier_steps = 2*2048*(2**25+1)
    scalar_steps = 7 * 2**24
    assert carrier_steps + scalar_steps < 2**40
    with TemporaryDirectory(prefix="eta-setup-8072-") as dirname:
        tree = Path(dirname)
        peer, runtime = source_runtime(tree)
        portable = peer / "portable"
        sys.path[:0] = [str(runtime), str(portable)]
        from upstream import install
        install()
        import installations
        from band_product import prepare_native, production_supplier
        from compiler_state import construct
        from grades import WeightedRecipe
        from record_census import inspect
        from tape_directory import dump
        from transport import Recipe

        entry, original = installations.ENTRY, installations.TERMINAL
        variants = {
            "original": original,
            "ordinary_eta": replace(original, rank_logs=(8192, 106000, 1681001), eta=Q(1,256)),
            "combined_21bit": replace(original, rank_logs=(8192,37107,589716),
                                      complex_log=1860554, kappa=Q(".0038984")),
            "combined_25bit": replace(original, rank_logs=(8192,38102,604362),
                                      complex_log=18845936, kappa=Q(".00389846")),
        }
        original_profiles = installations.PROFILES
        saved = Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width

        def forbidden(*args, **kwargs):
            raise AssertionError("Fixed constructor tried to materialize a native width/calendar")

        # If either lazy runtime path is touched, this fresh construction fails.
        Recipe.open = forbidden
        Recipe.width = property(forbidden)
        WeightedRecipe.open = forbidden
        WeightedRecipe.width = property(forbidden)
        rows = {}
        reference = None
        try:
            for name, profile in variants.items():
                assert bounded_scalars(entry) and bounded_scalars(profile)
                heights = (*entry.rank_logs, entry.complex_log,
                           *profile.rank_logs, profile.complex_log)
                assert len(heights) == 7 and all(map(safe_height, heights))
                installations.PROFILES = {"entry": entry, "terminal": profile}
                state = construct()
                layers = state[0]
                assert [[r.rank_log for r in layer] for layer in layers] == [
                    [*entry.rank_logs, entry.complex_log],
                    [*profile.rank_logs, profile.complex_log],
                ]
                assert all(r.width_log == 92*r.rank_log for layer in layers for r in layer)
                assert tuple(prepare_native(profile)) == layers[1]
                assert all(r.targets is state[1].targets and r.paid is state[1].paid
                           and r.cells is state[1].cells
                           for layer in layers for r in layer[:-1])
                assert layers[0][-1].cells is layers[1][-1].cells
                assert layers[0][-1].targets is layers[1][-1].targets
                supplier = production_supplier(profile.complex_log, profile.positive_stop_denominator)
                assert supplier.recipe is layers[1][-1]
                assert supplier.carrier.bit_length() == profile.complex_log+1
                assert supplier.carrier.bit_count() == 1
                if reference is None:
                    reference = state[1:5]
                else:
                    assert all(a is b for a,b in zip(reference, state[1:5], strict=True))
                path = tree / (name + ".dag")
                with path.open("wb") as out:
                    count = dump(out, state)
                census = inspect(path)
                assert census["records"] == count and census["largest_integer_bits"] < 2**38
                assert census["records"] < 2**32 and census["bytes"] < 2**38
                rows[name] = {
                    "rank_logs": list(profile.rank_logs), "gaussian_height": profile.complex_log,
                    "parameter_bits": max(heights).bit_length(),
                    "max_width_log": max(r.width_log for layer in layers for r in layer),
                    "materialized_gaussian_carrier_bits": supplier.carrier.bit_length(),
                    "record_count": count, "directory_bytes": census["bytes"],
                    "largest_directory_integer_bits": census["largest_integer_bits"],
                    "directory_sha256": sha256(path.read_bytes()).hexdigest(),
                    "lazy_width_and_open_forbidden": True,
                }
        finally:
            installations.PROFILES = original_profiles
            Recipe.open, Recipe.width, WeightedRecipe.open, WeightedRecipe.width = saved

        print(json.dumps({
            "source_head": "75f7e1c44f48c43983016bcf8878c4d9e5e87c62",
            "setup_height_interval": "1024 <= H < 2^25",
            "scalar_encoding_max_bits": 128,
            "variants": rows,
            "carrier_and_scalar_added_steps_bound": carrier_steps + scalar_steps,
            "serial_envelope": action_envelope(),
            "portable_caveat": "Construct/dump/census only; no new WASI fuel or trace claim. The copied #8057 portable producer contains stale fixed-profile assertions.",
            "scope": "Fixed constructor and input-independent installer bound; physical native openings, precision and caller costs retain their separate gates.",
        }, indent=2, sort_keys=True))


if __name__ == "__main__":
    run()
