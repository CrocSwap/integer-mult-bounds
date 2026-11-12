"""Construct and replay one pinned 20-to-19 signed-sector factorization."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import perf_counter

HERE = Path(__file__).resolve().parent
FACTORIZER_SHA256 = "f946d4d02f0dc60fca48beaec5105f195257711fc9063f5b0aa0fd4a98cbe239"
CHOSEN = [0, 1, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36]


def stop(*_):
    raise TimeoutError("single R209 factorization 60-second cap reached")


def support(vector):
    return [i for i, value in enumerate(vector) if value]


def planes(indices):
    return sorted({index // 18 for index in indices})


def shape(image, covector):
    image_support = support(image)
    covector_support = support(covector)
    image_planes = planes(image_support)
    covector_planes = planes(covector_support)
    entries = [image[i] * covector[j] for i in image_support for j in covector_support]
    return {
        "image_support": image_support,
        "covector_support": covector_support,
        "image_planes": image_planes,
        "covector_planes": covector_planes,
        "mixed_image": len(image_planes) == 2,
        "mixed_covector": len(covector_planes) == 2,
        "pure_off_diagonal": len(image_planes) == len(covector_planes) == 1 and image_planes != covector_planes,
        "cross_plane_entries": sum(i // 18 != j // 18 for i in image_support for j in covector_support),
        "nondyadic_entries": sum(entry.denominator & (entry.denominator - 1) != 0 for entry in entries),
        "max_denominator_bits": max(entry.denominator.bit_length() for entry in entries),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("sha256")
    args = parser.parse_args()
    assert __debug__
    signal(SIGALRM, stop)
    alarm(60)
    started = perf_counter()
    try:
        raw = args.receipt.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == args.sha256
        src = HERE / "factorize.py"
        assert hashlib.sha256(src.read_bytes()).hexdigest() == FACTORIZER_SHA256
        functions = run_path(str(src))
        receipt = json.loads(raw)
        assert receipt["chosen"] == CHOSEN
        columns = tuple(tuple(map(Fraction, column)) for column in receipt["target_columns"])
        assert len(columns) == 36
        result = functions["factorize"](columns)
        factors = result["factors"]
        assert result["length"] == 19
        mutant = list(factors)
        image, covector = mutant[0]
        mutant[0] = (tuple(-x for x in image), covector)
        assert functions["factor_product"](mutant, 36) != columns
        shapes = [shape(image, covector) for image, covector in factors]
        report = {
            "chosen": CHOSEN, "source_sha256": args.sha256,
            "target_sha256": hashlib.sha256(json.dumps(receipt["target_columns"], separators=(",", ":")).encode()).hexdigest(),
            "factorizer_sha256": FACTORIZER_SHA256, "rank": result["rank"],
            "involution": result["involution"], "minimum_transvections": result["length"],
            "mixed_image_factors": sum(s["mixed_image"] for s in shapes),
            "mixed_covector_factors": sum(s["mixed_covector"] for s in shapes),
            "pure_off_diagonal_factors": sum(s["pure_off_diagonal"] for s in shapes),
            "cross_plane_factors": sum(s["cross_plane_entries"] > 0 for s in shapes),
            "nondyadic_factors": sum(s["nondyadic_entries"] > 0 for s in shapes),
            "sign_flip_negative_control": "rejected", "seconds": perf_counter() - started,
            "shapes": shapes,
            "factors": [[list(map(str, u)), list(map(str, v))] for u, v in factors],
        }
        print(json.dumps(report, sort_keys=True))
    finally:
        alarm(0)


if __name__ == "__main__":
    main()
