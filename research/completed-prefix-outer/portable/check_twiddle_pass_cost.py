"""Check exact twiddle transport identities and the actual port hypotheses."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import argparse
import json

PACKAGE = Path(__file__).resolve().parents[1]
HERE = PACKAGE / "frozen/lanes" / "temporal-reuse"
REVISION = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
WORD = PACKAGE / "frozen/CANONICAL-WORD.json.gz"
WORD_HASH = "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219"


def need(condition, message):
    if not condition:
        raise ValueError(message)


# The coefficient order is 1, i, t, i*t, with i^2=t^2=-1.
def add(a, b):
    return tuple(x+y for x, y in zip(a, b))


def multiply(a, b):
    result = [F(0)]*4
    for j, x in enumerate(a):
        for k, y in enumerate(b):
            result[j ^ k] += (-1 if (j & k).bit_count() & 1 else 1)*x*y
    return tuple(result)


def scale(a, c):
    return tuple(c*x for x in a)


def matmul(a, b):
    return [[sum_ring([multiply(a[i][k], b[k][j]) for k in range(len(b))])
             for j in range(len(b[0]))] for i in range(len(a))]


def sum_ring(values):
    result = ZERO
    for value in values:
        result = add(result, value)
    return result


ZERO = (F(0),)*4
ONE = (F(1), F(0), F(0), F(0))
I = (F(0), F(1), F(0), F(0))
T = (F(0), F(0), F(1), F(0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sources", type=Path, default=PACKAGE / "sources/upstream")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    raw = WORD.read_bytes()
    need(sha256(raw).hexdigest() == WORD_HASH, "The actual port source changed")
    ports = json.loads(gzip.decompress(raw))["ports"]
    need(len(ports) == 112 and len(set(ports)) == 112, "The actual port count differs")
    need(all(0 < p < 512 and p.bit_count() in (3, 7) for p in ports), "A port fails the orbit hypothesis")
    a, b = scale(add(ONE, I), F(1, 2)), scale(add(ONE, scale(I, -1)), F(1, 2))
    c, inverse = [[a, b], [b, a]], [[b, a], [a, b]]
    identity = [[ONE, ZERO], [ZERO, ONE]]
    need(matmul(c, inverse) == identity and matmul(inverse, c) == identity, "The line inverse differs")
    actual = matmul(matmul(c, [[ONE, ZERO], [ZERO, T]]), inverse)
    diagonal = scale(add(ONE, T), F(1, 2))
    off = scale(multiply(I, add(ONE, scale(T, -1))), F(1, 2))
    expected = [[diagonal, off], [scale(off, -1), diagonal]]
    need(actual == expected, "The conjugated twiddle identity differs")
    need(multiply(add(ONE, T), add(ONE, scale(T, -1))) == scale(ONE, 2), "The unit product differs")
    for row in actual:
        for value in row:
            need(value != ZERO, "A two-point entry vanished")
    tensor_checks = []
    for width in range(1, 9):
        entries = [ONE]
        for _ in range(width):
            entries = [multiply(value, factor) for value in entries for factor in actual[0]]
        need(len(entries) == 2**width and all(value != ZERO for value in entries), "A tensor row lost support")
        tensor_checks.append({"width": width, "nonzero_entries": len(entries)})
    tail_cases = 0
    for r_exponent in range(1, 18):
        r = 2**r_exponent
        for u_exponent in range(2, r_exponent+2):
            u, k = 2**u_exponent, 2**(u_exponent-2)
            need(0 <= k < u//2 and (2*r//u)*k == r//2, "The current-round tail is invalid")
            tail_cases += 1
    source_path = "upstream/build/sections/06-transforms.tex"
    source = (args.sources / source_path).read_bytes()
    need(b"\\frac{2r}{u_i}\\,b_i k_i" in source and b"0\\leq k_i<u_i/2" in source,
         "The actual combined twiddle statement changed")
    receipt = {"status": "PASS_EXACT_CURRENT_TWIDDLE_PASS_CONTROLS",
               "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
               "proof_sha256": sha256((HERE/"TWIDDLE-PASS-COST.md").read_bytes()).hexdigest(),
               "source_revision": REVISION, "source_path": source_path,
               "source_sha256": sha256(source).hexdigest(), "canonical_word_sha256": WORD_HASH,
               "actual_ports": len(ports), "tail_cases": tail_cases, "tensor_support": tensor_checks,
               "scope": "Exact ring controls for the separate full-stream monomial/binary-ADD pass argument. No lower bound on recursive, unequal-volume, or fused multi-round implementations."}
    args.out.write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
