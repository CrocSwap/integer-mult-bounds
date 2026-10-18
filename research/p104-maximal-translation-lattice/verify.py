"""Read-only finite checks supporting PROOF.md; not a formal proof. Apache-2.0."""

import hashlib
import json
import subprocess
import sys
from itertools import product
from pathlib import Path

from model import census, ideal_numerator, lift, member, need, pair

PACKAGE = Path(__file__).resolve().parent


def source_index(package):
    """Authenticate, then run the retained checker as a source entry point."""
    pin = json.loads((package / "PREDECESSOR.json").read_text())
    need(pin["head"] == "0cc430349a3f3dc200666bc22e997076e0a557ed", "source head")
    need(len(pin["files"]) == 1, "one retained index implementation")
    entry = pin["files"][0]
    need(entry["local"] == "vendor/prefix_index.py", "source location")
    path = package / entry["local"]
    raw = path.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == entry["sha256"], "source SHA256")
    blob = b"blob " + str(len(raw)).encode() + b"\0" + raw
    need(hashlib.sha1(blob).hexdigest() == entry["git_blob"], "source Git blob")
    execution = subprocess.run(
        [sys.executable, "-I", "-B", "-W", "error", str(path)],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    need(
        execution.returncode == 0, "retained index checker failed: " + execution.stderr
    )
    result = json.loads(execution.stdout)
    need(result["status"] == "PASS", "retained index status")
    return result["ranks"]


def pair_facts():
    """Check exact correction, output difference and inverse on signed pairs."""
    cases = 0
    for ar, ai, br, bi in product(range(-2, 3), repeat=4):
        a, b = (ar, ai), (br, bi)
        first, second = pair(a, b)
        need(
            (first[0] - second[0], first[1] - second[1]) == (bi - ai, ar - br),
            "rounding-free output difference",
        )
        need(pair(first, second, inverse=True) == (a, b), "literal pair inverse")
        ideal = ideal_numerator([ar, ai, br, bi], 1)
        parity = (ai - bi) % 2 - (ar - br) % 2
        actual = tuple(2 * x - u for x, u in zip(first + second, ideal, strict=True))
        need(actual == (parity, -parity, parity, -parity), "exact pair correction")
        cases += 1
    return cases


def rigidity_facts():
    """All parity inputs separate nonconstant increments for 81 signed shifts."""
    constant_shifts = 0
    for cr, ci, dr, di in product(range(-1, 2), repeat=4):
        increments = set()
        for ar, ai, br, bi in product(range(2), repeat=4):
            first, second = pair((ar, ai), (br, bi))
            shifted = pair((ar + cr, ai + ci), (br + dr, bi + di))
            increments.add(
                tuple(
                    x - y
                    for x, y in zip(
                        shifted[0] + shifted[1], first + second, strict=True
                    )
                )
            )
        expected = (cr - dr) % 2 == 0 and (ci - di) % 2 == 0
        need((len(increments) == 1) == expected, "pair rigidity parity classes")
        if expected:
            numerator = ideal_numerator([cr, ci, dr, di], 1)
            need(all(x % 2 == 0 for x in numerator), "constant shift integrality")
            need(increments == {tuple(x // 2 for x in numerator)}, "ideal increment")
            constant_shifts += 1
    return dict(shifts=81, parity_inputs_each=16, constant_shifts=constant_shifts)


def translation_facts():
    """Signed forward/inverse checks and the wrong-inverse-lattice control."""
    for rank in range(8):
        dimension = 2 << rank
        modulus = 1 << (rank // 2 + 1)
        x = [((-1) ** j) * (j**3 + 7) for j in range(dimension)]
        z = [modulus * (j % 5 - 2) + (j % 2) for j in range(dimension)]
        need(member(z, rank), "scalar-plus-constant sufficient shift")
        numerator = ideal_numerator(z, rank)
        need(all(u % (1 << rank) == 0 for u in numerator), "ideal shift integrality")
        v = [u // (1 << rank) for u in numerator]
        y = lift(x, rank)
        target = [a + b for a, b in zip(x, z, strict=True)]
        need(
            lift(target, rank) == [a + b for a, b in zip(y, v, strict=True)],
            "forward translation",
        )
        need(lift(y, rank, inverse=True) == x, "whole-word inverse")
        need(
            lift([a + b for a, b in zip(y, v, strict=True)], rank, inverse=True)
            == target,
            "inverse image-lattice translation",
        )
    z = [0, 0, 0, 0, 1, 1, 1, 3]
    v = [u // 4 for u in ideal_numerator(z, 2)]
    need(member(z, 2) and not member(v, 2), "distinct forward and inverse groups")
    wrong = [0, 0, 0, 0, 0, 0, 0, 1]
    y = lift(wrong, 2)
    actual = lift([a + b for a, b in zip(y, z, strict=True)], 2, inverse=True)
    zero = lift(z, 2, inverse=True)
    need(
        actual != [a + b for a, b in zip(wrong, zero, strict=True)],
        "wrong inverse-lattice reuse must fail",
    )
    return dict(signed_ranks=list(range(8)), wrong_inverse_lattice_rejected=True)


def run(package=PACKAGE):
    indices = source_index(package)
    need(
        [r["index_log2"] for r in indices] == [2, 6, 15, 34, 75, 161, 343],
        "index exponents",
    )
    return dict(
        status="PASS_P104_MAXIMAL_TRANSLATION_LATTICE",
        proof_status="written all-rank induction; finite checks are not a formal proof",
        pair_cases=pair_facts(),
        pair_rigidity=rigidity_facts(),
        exhaustive_shift_censuses=[census(1), census(2)],
        translations=translation_facts(),
        retained_index_replay=indices,
        rank7_optimal_coset_bits=343,
        four_block_optimal_coset_bits=1372,
    )


def main():
    actual = run()
    stored = json.loads((PACKAGE / "RESULT.json").read_text())
    # Canonical JSON preserves distinctions such as true, 1 and 1.0.
    need(
        json.dumps(json.loads(json.dumps(actual)), sort_keys=True)
        == json.dumps(stored, sort_keys=True),
        "typed result receipt differs",
    )
    print(json.dumps(actual, indent=2))


if __name__ == "__main__":
    main()
