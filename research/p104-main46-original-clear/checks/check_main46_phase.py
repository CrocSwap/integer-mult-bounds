"""Check the three literal main-46 chart maps in exact signed arithmetic."""
import argparse
from copy import deepcopy
import gzip
from hashlib import sha256
import json
from pathlib import Path
from runpy import run_path

WORD_SHA = "37358c493d18ebc6be386aebb4c17529b38883674731f7009ef4e96a5313467d"
ENGINE_PINS = {
    "clifford_exact.py": "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    "native_verify.py": "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
}
FRAMES = {
    914: [1, 10, 20, 32, 64, 134, 256],
    245: [1, 6, 10, 18, 32, 64, 128, 256],
    127: [1, 2, 4, 8, 16, 32, 64, 128, 256],
}


def sha(data):
    return sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--word", type=Path, required=True)
    parser.add_argument("--engine-root", type=Path, required=True)
    parser.add_argument("--all-columns", action="store_true")
    args = parser.parse_args()
    assert __debug__
    raw = args.word.read_bytes()
    assert sha(raw) == WORD_SHA
    word = json.loads(gzip.decompress(raw))
    assert all(word["frames"][i] == f for i, f in FRAMES.items())
    assert word["program"][46844] == ["MOVE", 497, 914, 127, False]
    for name, expected in ENGINE_PINS.items():
        assert sha((args.engine_root / name).read_bytes()) == expected
    compiler = run_path(str(args.engine_root / "clifford_exact.py"))
    interp = run_path(str(args.engine_root / "native_verify.py"))
    frames = {i: compiler["canonical_frame"](9, tuple(f)) for i, f in FRAMES.items()}
    native = {}
    for a, b, rank in ((914, 245, 1), (245, 127, 1), (914, 127, 2)):
        record, _ = compiler["lower_child"](frames[a].adjoint().then(frames[b]))
        assert record["rank"] == rank
        expected = interp["adjoint"](interp["frame"](FRAMES[a], 9)) + interp["frame"](FRAMES[b], 9)
        native[a, b] = interp["recipe"](record)
        interp["equal"](native[a, b], expected, f"canonical {a}→{b}")
        damaged = deepcopy(record)
        damaged["left"]["phase"] = (damaged["left"]["phase"] + 1) % 4
        try:
            interp["equal"](interp["recipe"](damaged), expected, "reject wrong phase")
        except ValueError as e:
            assert "exact global phase" in str(e)
        else:
            raise AssertionError("phase control accepted")
    via = native[914, 245] + native[245, 127]
    direct = native[914, 127]
    for label, left, right in (("forward", via, direct),
                              ("adjoint", interp["adjoint"](via), interp["adjoint"](direct))):
        interp["equal"](left, right, label)
        if args.all_columns:
            for j in range(512):
                assert interp["state"](left, j) == interp["state"](right, j), (label, j)
    print(json.dumps({"status": "PASS_MAIN46_PHASE", "word_sha256": WORD_SHA,
                      "engine_pins": ENGINE_PINS, "ranks": [1, 1, 2],
                      "signed_generator_count": 18, "existing_direct_move_clock": 46844,
                      "absolute_phase_controls": 3,
                      "columns_per_direction": 512 if args.all_columns else 1}, sort_keys=True))


if __name__ == "__main__":
    main()
