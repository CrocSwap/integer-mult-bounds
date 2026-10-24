"""Check the exact normalization for the conditional past interface."""

from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REVISION = "3ae9a6f3ac74ded022ab3b4872a7357a621af6fb"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
ASSEMBLY_PIN = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
ZERO, ONE, I = (Q(0), Q(0)), (Q(1), Q(0)), (Q(0), Q(1))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def product(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def multiply(a, b):
    return [[add(product(a[i][0], b[0][j]), product(a[i][1], b[1][j]))
             for j in range(2)] for i in range(2)]


def scalar(z, a):
    return [[product(z, x) for x in row] for row in a]


def main():
    identity = [[ONE, ZERO], [ZERO, ONE]]
    alpha, beta = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))
    c = [[alpha, beta], [beta, alpha]]
    s = [[ONE, ZERO], [ZERO, I]]
    h0 = [[(Q(1, 2), Q(0)), (Q(1, 2), Q(0))],
          [(Q(1, 2), Q(0)), (Q(-1, 2), Q(0))]]
    h = scalar((Q(1), Q(1)), h0)
    need(multiply(s, multiply(c, s)) == h, "S C S normalization")
    need(scalar(beta, h) == h0, "Active H0 normalization")
    powers = [identity]
    for _ in range(8):
        powers.append(multiply(h, powers[-1]))
    need(powers[2] == scalar(I, identity), "h squared")
    need(powers[4] == scalar((Q(-1), Q(0)), identity), "h fourth power")
    need(powers[8] == identity, "h eighth power")
    for j, matrix in enumerate(powers):
        for row in matrix:
            norms = [x*x+y*y for x, y in row]
            need(norms == [Q(1, 2), Q(1, 2)] if j % 2 else sorted(norms) == [0, 1],
                 "The exact odd/even row support differs")
    raw = subprocess.check_output(["git", "-C", str(ROOT / "worktrees/k5-centre-sharing"),
                                   "show", REVISION+":"+ASSEMBLY])
    need(sha256(raw).hexdigest() == ASSEMBLY_PIN, "Selected assembly source")
    assembly = json.loads(raw)
    epsilon, kappa = Q(assembly["outer"]["epsilon_positive"]), Q(assembly["kappa"])
    need(1-epsilon-kappa > 0 and epsilon-kappa > 0, "Outer cost margins")
    receipt = {
        "status": "PASS_FIXED_PAST_OUTER_NORMALIZATION",
        "revision": REVISION, "assembly_sha256": ASSEMBLY_PIN,
        "h_powers": [[[[str(z) for z in v] for v in row] for row in a] for a in powers],
        "scalar_identity": "S C S = (1+i) H0",
        "tensor_period": 8,
        "odd_power_row_norm": "2^(number_of_past_bits/2)",
        "decoded_round_error": "n 2^(number_of_past_bits/2) eta",
        "terminal_decoder_cost": "O(V d)",
        "native_supplier_hypothesis_verified": False,
        "scope": "Exact scalar normalization and selected outer inequalities; the closure proof is conditional.",
    }
    (HERE / "FIXED-PAST-OUTER-CLOSURE.json").write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(receipt["status"])


if __name__ == "__main__":
    main()
