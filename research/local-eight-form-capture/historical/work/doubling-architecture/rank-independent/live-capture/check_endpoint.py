"""Check the selected chart phase and the failure of the two-tap tensor lift."""

from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASE = ROOT / "work/next-track/complex/pipeline/retimed-4"


def gaussian_add(x, y):
    return x[0] + y[0], x[1] + y[1]


def gaussian_multiply(x, y):
    return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]


def binary_apply(columns, v):
    output = 0
    for j, c in enumerate(columns):
        if v >> j & 1:
            output ^= c
    return output


def main():
    tp = BASE / "complex/GLOBAL-TEMPLATE.json.gz"
    wp = BASE / "split-centres/CANONICAL-WORD.json.gz"
    t = json.loads(gzip.decompress(tp.read_bytes()))
    w = json.loads(gzip.decompress(wp.read_bytes()))
    charts = []
    for helper in range(758, 750, -1):
        family, route = t["calls"][0]["owners"][helper]
        q = w["ports"][family % 120]
        zero = min(j for j in range(9) if not (q >> j & 1))
        u = q ^ (1 << zero)
        swap = list(range(89))
        swap[0], swap[zero] = swap[zero], swap[0]
        b = [(1 << j) ^ (u if u >> j & 1 else 0) for j in swap]
        indices = route[5] + [j for j in range(89) if j not in route[5]]
        sigma = [b[j] for j in indices]
        assert all((x & y).bit_count() % 2 == int(i == j) for i, x in enumerate(sigma) for j, y in enumerate(sigma))
        delta = sum((((c.bit_count() - 1) // 2) % 2) << j for j, c in enumerate(sigma))
        shift = binary_apply(sigma, delta)
        assert shift == u != 0
        # Linear coefficients and pair coefficients determine the mod-four phase.
        for j, c in enumerate(sigma):
            assert (c.bit_count() - 1) % 4 == 2 * ((shift & c).bit_count() % 2)
            for i in range(j):
                v = sigma[i] ^ c
                assert (v.bit_count() - 2) % 4 == 2 * ((shift & v).bit_count() % 2)
        charts.append({"family": family, "helper": helper, "q": q,
                       "translation": shift, "strict_commutation": False})
    a, b = (Q(1, 2), Q(-1, 2)), (Q(1, 2), Q(1, 2))
    assert gaussian_add(a, b) == (1, 0)
    assert gaussian_add(a, (-b[0], -b[1])) == (0, -1)
    exact_tensor_eigenvalue = gaussian_multiply((0, -1), (0, -1))
    false_two_tap_eigenvalue = gaussian_add(a, b)
    assert exact_tensor_eigenvalue == (-1, 0)
    assert false_two_tap_eigenvalue == (1, 0)
    assert exact_tensor_eigenvalue != false_two_tap_eigenvalue
    assert t["execution_schedule"][0] == {"kind": "local", "pair": 0, "reverse": False, "stage": 0}
    source = ROOT / "work/next-track/complex/pipeline/full-source/research/split-centres-global/proofs/INHERITED-COMPLEX-GEOMETRY.txt"
    text = source.read_text()
    assert "initially\nX_(-1)=C_q, Y_(-1)=I" in text
    assert "C_all C_q^(-2)=C_all X_q" in text
    result = {
        "status": "PASS_ENDPOINT_COVARIANCE_AND_TENSOR_COUNTEREXAMPLE",
        "chart_identity": "D_I P_sigma = T_translation P_sigma D_I",
        "charts": charts,
        "source_X_factor_required": "D_p^-1",
        "reason": "The initial C_q is a frame interpretation, not an extra paid initial transform.",
        "false_tensor_shortcut_witness": {
            "Fourier_character": [1, 1],
            "exact_D_inverse_tensor_2": "-1",
            "proposed_aI_plus_b_translation_tensor_2": "1",
        },
        "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in (tp, wp, source)},
        "scope": "Seed phase identities and a counterexample to a proposed constant-size all-size shortcut. No endpoint cost or modified global controller is certified.",
    }
    (HERE / "ENDPOINT-RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
