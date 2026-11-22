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
        "e27aaa69b1f7edd294140762a0daed56d3d4d95427d97e2bd874c8967243ddcf",
    )
    assert (clock["linked_files"], clock["linked_sha256"]) == (
        110,
        "027a5ea7375324c9d31b34894baf6bdc16bdf8448bbb7359db9a9ab647203273",
    )
    assert (
        clock["directory_sha256"]
        == "32b5d7d611a0987569b895a6649d514a6f8ad55cf8f5fbec3d1dcec5925897a8"
    )
    assert clock["opcodes"] == 2665134 and clock["max_depth"] == 284
    assert (
        clock["directory"]["largest_key_bytes"] == 28
        and clock["directory"]["largest_integer_bits"] == 261
    )
    assert (clock["directory"]["records"], clock["directory"]["edges"]) == (
        2407815,
        5174401,
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
    stages = [
        time_bound(clock[k], clock["module"], clock["max_depth"])
        for k in ("installer", "receiver")
    ]
    assert all(0 < n < 2**145 for n in stages)
    total = sum(stages)
    assert str(total) == clock["transition_bound"]
    assert total.bit_length() == clock["trace_exponent"] == 142
    assert total < 2**142 < 2 ** clock["exponent"] == 2**146
    return {
        "producer": str(stages[0]),
        "receiver": str(stages[1]),
        "transitions": str(total),
        "trace_exponent": total.bit_length(),
        "conservative_exponent": 146,
    }


if __name__ == "__main__":
    print(json.dumps(verify(), sort_keys=True))
