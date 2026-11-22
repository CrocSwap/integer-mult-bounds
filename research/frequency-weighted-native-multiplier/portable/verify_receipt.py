"""Recompute both finite fixed-tape invoices with standard-library integers."""

import json
import sys
from pathlib import Path


def time_bound(receipt, code, depth):
    f = receipt["fuel"]
    calls = receipt["host_calls"]
    assert calls == sum(receipt["operations"].values())
    extent = 2**64
    assert f < 2**40 and calls < 2**16 and receipt["linear_bytes"] < 2**30
    assert (
        receipt["maxima"]["iov"] == 1
        and receipt["maxima"]["joined_path"] < 4096
        and receipt["maxima"]["entries"] < 2**16
    )
    assert receipt["source_seed_bytes"] + code["bytes"] < 2**27
    labels = 512 * (5 + depth + code["max_locals"] + code["max_params"])
    assert 4 * ((f + 2) * (labels + 512) + 2**50 + 2**37) < extent
    steps = (2 * f + 4) * (code["max_body_bytes"] + 1)
    assert steps < 2**58
    arithmetic = 128 * 64 * 2**16 * (2**14 + 4) ** 2
    assert arithmetic < 2**58
    return (
        2**111
        + steps * (2**20 * extent + 2**58)
        + calls * 2**92
        + 2**110
        + 4 * extent * 2**12
    )


def local_time_bound(receipt, code, depth, free):
    """Price the same operations using the head positions and the parsed code."""
    coarse = time_bound(receipt, code, depth)
    assert free == 274 and depth == 284
    fuel = receipt["fuel"]
    steps = (2 * fuel + 4) * (free + 1)
    active = 2**40
    frame = 512 * (5 + depth + code["max_locals"] + code["max_params"])
    frame_operands = 512 * (19 * code["max_body_bytes"] + 18)
    assert frame_operands < 2**30
    assert 4 * (2**37 + 2 * frame + frame_operands) < active
    # At a return or branch only the discarded value records require extra travel.
    erased = (fuel + 2) * 512 * 2**14
    local = (
        2**111
        + steps * (2**20 * active + 2**58)
        + erased
        + receipt["host_calls"] * 2**92
        + 2**110
        + 4 * 2**64 * 2**12
    )
    max_fuel, max_calls = 2**40, 2**16
    max_steps = (2 * max_fuel + 4) * (free + 1)
    max_pair = 2 * (
        2**111
        + max_steps * (2**20 * active + 2**58)
        + (max_fuel + 2) * 512 * 2**14
        + max_calls * 2**92
        + 2**110
        + 4 * 2**64 * 2**12
    )
    assert 2 * local <= max_pair < 2**113
    assert local < coarse
    return local


def verify():
    if sys.flags.optimize:
        raise ValueError("run with assertions enabled")
    observed = json.loads(Path(__file__).with_name("EVIDENCE.json").read_bytes())
    clock = observed["clock"]
    assert (
        clock["module"]["sha256"]
        == "e5dc5a398b07b54ea8fdb503bf68fb583d533f10ec3f930963e02b9505f7a763"
    )
    assert (clock["compiled_files"], clock["compiled_sha256"]) == (
        106,
        "594661d65b3022ba679c29b193800813ed0c41d8f3a8c691e46a7a20ea38229f",
    )
    assert (clock["linked_files"], clock["linked_sha256"]) == (
        110,
        "3b4c1c8ae6b15cf97c49f801f3b0059da0eaefb2db2aae79d52957e651eaee30",
    )
    assert (
        clock["directory_sha256"]
        == "045c482b6d32fc58bae8e047e22d519f9269e0124fe3cb1695e930e4f472f2a8"
    )
    assert clock["opcodes"] == 2665134 and clock["max_depth"] == 284
    assert (
        clock["directory"]["largest_key_bytes"] == 28
        and clock["directory"]["largest_integer_bits"] == 261
    )
    assert (clock["directory"]["records"], clock["directory"]["edges"]) == (
        2407819,
        5174419,
    )
    assert (
        observed["independent"]["native_directory_sha256"] == clock["directory_sha256"]
    )
    assert observed["signed"]["public_signed_product"] == -345550037539
    assert observed["signed"]["finite_tensor"]["coefficients_prefix"] == [
        11811,
        10996,
        4152,
        868,
        77,
    ]
    coarse = [
        time_bound(clock[k], clock["module"], clock["max_depth"])
        for k in ("installer", "receiver")
    ]
    stages = [
        local_time_bound(
            clock[k], clock["module"], clock["max_depth"], clock["max_free_segment"]
        )
        for k in ("installer", "receiver")
    ]
    assert all(0 < n < 2**145 for n in coarse)
    assert sum(coarse).bit_length() == clock["full_store_trace_exponent"] == 142
    assert str(sum(coarse)) == clock["full_store_bound"]
    total = sum(stages)
    assert str(total) == clock["transition_bound"]
    assert total.bit_length() == clock["trace_exponent"] == 113
    assert total < 2**113 < 2 ** clock["exponent"] == 2**146
    return {
        "producer": str(stages[0]),
        "receiver": str(stages[1]),
        "transitions": str(total),
        "trace_exponent": total.bit_length(),
        "full_store_trace_exponent": 142,
        "conservative_exponent": 146,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
