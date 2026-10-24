"""Check the small ordered identities used by two scoped twiddle proofs."""

from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "temporal-reuse"
PINS = {
    "TWIDDLE-PASS-COST.md": "796b04dfb5882c0b49f98b5d6fd73580bf73929ccb663c784e1d24ad60ca4b99",
    "ACCUMULATED-TWIDDLE-CODE.md": "406e3cae0f69be8dd5c737b56e4af25b9aeb59de65d04dcb5355c67b2b5b371c",
}


def need(value, label):
    if not value:
        raise ValueError(label)


def add(x, y):
    return tuple(a + b for a, b in zip(x, y))


def scale(c, x):
    return tuple(c * a for a in x)


def mul(x, y):
    out = [F(0)] * 4
    for j, a in enumerate(x):
        for k, b in enumerate(y):
            sign = -1 if ((j & k & 1) + bool(j & k & 2)) % 2 else 1
            out[j ^ k] += sign * a * b
    return tuple(out)


ZERO = (F(0),) * 4
ONE = (F(1), F(0), F(0), F(0))
I = (F(0), F(1), F(0), F(0))
T = (F(0), F(0), F(1), F(0))


def matmul(a, b):
    return [[add(mul(a[i][0], b[0][j]), mul(a[i][1], b[1][j])) for j in range(2)] for i in range(2)]


def main():
    for name, pin in PINS.items():
        need(sha256((SOURCE / name).read_bytes()).hexdigest() == pin, "Proof pin")
    alpha, beta = scale(F(1, 2), add(ONE, I)), scale(F(1, 2), add(ONE, scale(-1, I)))
    c, ci = [[alpha, beta], [beta, alpha]], [[beta, alpha], [alpha, beta]]
    ident, z = [[ONE, ZERO], [ZERO, ONE]], [[ONE, ZERO], [ZERO, scale(-1, ONE)]]
    need(matmul(c, ci) == ident == matmul(ci, c), "Exact inverse over the four-dimensional ring")
    need(mul(T, T) == scale(-1, ONE), "The polynomial root stays separate from i")
    need(mul(add(ONE, T), add(ONE, scale(-1, T))) == scale(2, ONE), "Both twiddle sums are units")
    conjugate = matmul(matmul(c, [[ONE, ZERO], [ZERO, T]]), ci)
    diagonal = scale(F(1, 2), add(ONE, T))
    off = scale(F(1, 2), mul(I, add(ONE, scale(-1, T))))
    need(conjugate == [[diagonal, off], [scale(-1, off), diagonal]], "Exact ordered twiddle conjugation")
    need(all(value != ZERO for row in conjugate for value in row), "All four coefficients are nonzero")
    xz = [[ZERO, scale(-1, ONE)], [ONE, ZERO]]
    need(matmul(matmul(c, z), ci) == [[scale(-1, mul(I, value)) for value in row] for row in xz],
         "Positive C line Pauli phase")
    need(matmul(matmul(ci, z), c) == [[mul(I, value) for value in row] for row in xz],
         "Negative C line Pauli phase")
    signs = {}
    for weight in (1, 3, 5, 7):
        phase = ONE
        for _ in range(weight):
            phase = mul(phase, scale(-1, I))
        plus, minus = mul(scale(-1, I), phase), mul(I, phase)
        need(plus in (ONE, scale(-1, ONE)) and minus == scale(-1, plus), "Opposite parity signs")
        signs[str(weight)] = [int(plus[0]), int(minus[0])]
    need(signs["3"] == signs["7"] == [1, -1], "Actual port-weight signs")
    receipt = {
        "status": "PASS_SCOPED_TWIDDLE_PROOF_REVIEW",
        "proof_pins": PINS,
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "independent_exact_checks": ["Two-point conjugation with independent Gaussian and polynomial roots",
                                     "Unit products", "Both Pauli phases", "All odd native weights through7"],
        "parity_signs": signs,
        "proof_review": ["Separate full-stream pass depth", "Ordered J E H0 placement",
                         "Invertible joint parity blocks", "Complete-word support bound",
                         "One-native-tensor support consequence under scalar monomial wrappers"],
        "not_repeated": ["Upstream source and layout audit", "The256-column finite example",
                         "The producer checker", "Native or recursive decoder construction"],
        "scope": "Fixed complete-stream pass grammar and the stated stable-port endpoint. No general native decoder lower bound.",
    }
    (HERE / "TWIDDLE-PASS-PROOF-REVIEW.json").write_text(json.dumps(receipt, sort_keys=True, indent=2) + "\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
