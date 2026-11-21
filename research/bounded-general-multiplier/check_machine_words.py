"""Exercise the compiled finite scalar engine inside all three direct Fourier transforms."""

from collections import Counter
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from multiply import receiver, signed_leaf
from short_product import native_product


def check(library):
    engine = native_product(library)
    counts = Counter()
    def observed(a,b):
        counts["packed"] += 1
        return engine(a,b)
    def scalar(a,b):
        counts["scalar"] += 1
        return signed_leaf(a,b,observed)
    machine = receiver()((3,), 8, 4100, source_root=Path(__file__).resolve().parents[2],
                         scalar_product=scalar)
    value, coeff = machine.multiply(279,517)
    if (value,coeff) != (144243,[115,51,2]) or not counts["packed"]:
        raise ArithmeticError((value,coeff,counts))
    print("wide_fourier",value,coeff,"full_H",machine.transform.h_calls,dict(counts))
    print("PASS_PACKED_FOURIER_WORDS")


if __name__ == "__main__":
    check(sys.argv[1])
