"""Independent bounded exact-arithmetic checks of the written contraction proof.

This does not import the author verifier or execute the actual compiler.
The all-size claim is the rank/path argument in DERIVATION.md.
"""
from pathlib import Path
import json


def need(ok, message):
    if not ok:
        raise RuntimeError(message)


exit_cases = 0
for m in range(2, 33):
    for minimum in range(2, m + 1):
        for paid in range(1, minimum):
            for generation in range(9):
                n = m * minimum**generation
                exit_rank = paid ** (generation + 1)
                need(m * exit_rank <= (m - 1) * n, "exit contraction")
                exit_cases += 1

rank_cases = 0
for m in range(2, 33):
    need(2 * (m - 1)**m < m**m, "m-step strict halving")
    # The greatest possible contracted child bounds any admissible child.
    contexts = [0] * 513
    nodes = [0] * 513
    for n in range(1, 513):
        if n >= m:
            child = (m - 1) * n // m
            need(child < n, "proper recursive child")
            contexts[n] = n.bit_length() + contexts[child]
            nodes[n] = 1 + nodes[child]
        need(nodes[n] <= m * n.bit_length(), "node bound counts root")
        need(contexts[n] <= m * n.bit_length()**2, "context bound")
        rank_cases += 1

v = 1024
H = 65807000000000
maximum = 145**v
K = v * maximum * (H + 1)**2
need(K.bit_length() == 7455, "selected constant bit length")
need(H + 1 < 2**46 and H > 8299 and 145 < 2**8,
     "symbolic N exceeds thirty-two K")
simple_cases = 0
for small_K in (1, 2, 7):
    for N in (32 * small_K + 1, 32 * small_K + 2):
        for d in range(1, 4097):
            ell, power = 0, 1
            while power * N <= d:
                ell += 1
                power *= N
            t = small_K * ell
            need(32 * t < d, "depth absorption")
            need((d + 1)//2 + 4*t <= d, "simple fractional grid")
            need((d + 2)//2 + 14*t + 1 <= d + 2,
                 "magnitude at enlarged grid")
            simple_cases += 1
out = {
    "status": "PASS_INDEPENDENT_CONTRACTION_ARITHMETIC",
    "exit_cases": exit_cases,
    "rank_cases": rank_cases,
    "m_range": [2, 32],
    "n_range": [1, 512],
    "generation_range": [0, 8],
    "selected_K_bit_length": K.bit_length(),
    "simple_format_cases": simple_cases,
    "simple_F": "p+d",
    "simple_J": "h+d+2",
    "simple_W": "p+h+2*d+3",
    "constructed_N": False,
    "scope": "Bounded exact arithmetic supporting the separate all-size path proof; no source replay.",
}
print(json.dumps(out, indent=2, sort_keys=True))
