"""Replay one pinned signed-factor residual under a 60-second cap."""
import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from signal import SIGALRM, alarm, signal
from time import perf_counter

from factorize import displacement, factor_product, factorize, column_matrix_vector


def stop(*_):
    raise TimeoutError("single residual 60-second cap reached")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("sha256")
    args = parser.parse_args()
    signal(SIGALRM, stop)
    alarm(60)
    started = perf_counter()
    try:
        raw = args.receipt.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == args.sha256
        receipt = json.loads(raw)
        assert receipt["chosen"] == [0, 2, 4, 6, 8, 10, 12, 14, 18, 19, 20, 22, 24, 26, 28, 30, 32, 34, 36]
        target = tuple(tuple(map(Fraction, column)) for column in receipt["target_columns"])
        assert len(target) == 36
        result = factorize(target)
        assert result["rank"] == 18
        factors = result["factors"]
        negative = list(factors)
        image, covector = negative[0]
        negative[0] = (tuple(-x for x in image), covector)
        assert factor_product(negative, 36) != target
        delta = displacement(target)
        rank_obstruction = all(column_matrix_vector(delta, d) == tuple(-2*x for x in d)
                               for d in delta)
        assert rank_obstruction == result["involution"]
        expected = tuple(tuple(Fraction((-1 if j < 18 else 1) if i == j else 0)
                               for i in range(36)) for j in range(36))
        output = {
            "chosen": receipt["chosen"], "source_sha256": args.sha256,
            "target_sha256": hashlib.sha256(json.dumps(receipt["target_columns"],separators=(",", ":")).encode()).hexdigest(),
            "rank": result["rank"], "minimum_transvections": result["length"],
            "involution": result["involution"], "exact_diag_minus18_plus18": target == expected,
            "sign_flip_negative_control": "rejected", "seconds": perf_counter()-started,
            "factors": [[list(map(str, u)), list(map(str, v))] for u,v in factors],
        }
        print(json.dumps(output, sort_keys=True))
    finally:
        alarm(0)


if __name__ == "__main__":
    main()
