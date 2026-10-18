#!/usr/bin/env python3
"""Bind PR2753's lcm row stock to the outer wrapper and the selected fit guards.

The arithmetic is exact. Predecessor checkers are not imported or executed.
"""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
SIGMA = 6748
ELL = 16
M_CLAIM = 269241600
LIVE = 28416
PHYSICAL = 28425


def fail(message):
    raise SystemExit("FAIL_SELECTED_LCM_STOCK_WRAPPER_FIT " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {
        "research/community-frontier1094-audit/ASSEMBLY.json",
        "research/selected-outer-borrowing-wrapper/README.md",
        "research/selected-outer-borrowing-wrapper/vendor/pr2786/predecessor.tar.gz",
    }, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)
    archive = ROOT / "research/selected-outer-borrowing-wrapper/vendor/pr2786/predecessor.tar.gz"
    with tarfile.open(archive, "r:gz") as tar:
        proof = tar.extractfile("PROOF.md").read().decode("utf-8")
    wrapper = (ROOT / "research/selected-outer-borrowing-wrapper/README.md").read_text(encoding="utf-8")
    for needle in (
        "K = 269241600 N H = lcm(28416, 28425) N H.",
        "log_q K <4096w+1.",
        "k <= 2(4096w+1)log2e+1 <=8195w log2e.",
        "no historical 6748 coefficient is assumed.",
        "it does not implement that outer padding/borrowing wrapper.",
    ):
        require(needle in proof, "PR2753 proof no longer states " + needle)
    for needle in (
        "The caller supplies S with 1<=S<=R. This routine does not compute S, choose k, or assert k<e/2.",
        "R'=ceil(R/S)*S,  R<=R'<2R",
    ):
        require(needle in wrapper, "wrapper contract no longer states " + needle)
    return json.loads((ROOT / "research/community-frontier1094-audit/ASSEMBLY.json").read_text(encoding="utf-8"))


def gcd(a, b):
    while b:
        a, b = b, a % b
    return a


def lcm(a, b):
    return a // gcd(a, b) * b


def depth(atom_count):
    steps = 0
    value = atom_count
    while value >= 64:
        value = 42 * (value // 64)
        steps += 1
        require(steps <= 64, "depth recurrence did not descend")
    return steps


def depth_bound_holds(atom_count):
    """D(n) <= (28/17) log2(max(1,n)), checked as n**28 >= 2**(17 D)."""
    steps = depth(atom_count)
    if steps == 0:
        return True
    return atom_count**28 >= 2**(17 * steps)


def coefficient_room(width):
    """(28/17)*(4096 w + 1) <= 6748 w for integer atom width w >= 1."""
    return Fraction(28, 17) * (4096 * width + 1) <= SIGMA * width


def packet_comparison_proved(prime):
    """K < q**(4096 w + 1) follows from M < q and |GL_64(F_q)| < q**4096."""
    return prime > M_CLAIM and prime > 1


def padding_fits(radix, stock):
    """Wrapper precondition 1 <= S <= q^k and ceil(q^k/S)*S < 2 q^k."""
    if radix < 2 or stock < 1:
        return False
    power = 1
    while power < stock:
        power *= radix
    if stock > power:
        return False
    padded = -(-power // stock) * stock
    return power <= padded < 2 * power


def stages(assembly, lower_key, record_key):
    beta = Fraction(1, 10**24)
    bit = Fraction(assembly["bit_lower"])
    lower = Fraction(assembly[lower_key])
    saving = min(bit, (1 - beta) * lower) - Fraction(1, 10**27)
    exponent = Fraction(384599, 10**10)
    found = []
    for record in assembly[record_key]:
        previous = exponent
        exponent = (1 - saving) * saving + saving * previous
        gap = min(saving - exponent, 1 - exponent - saving,
                  1 - exponent - saving * (1 - previous), 1 - saving)
        def ceil(value):
            return -(-value.numerator // value.denominator)
        cutoff = max(ceil(36 / gap**2), ceil(2 * (4 + 1024) / gap))
        require(str(exponent) == record["exponent"], "exponent drift")
        require(str(gap) == record["gap"], "gap drift")
        require(str(cutoff) == record["cutoff_log2"], "cutoff drift")
        require(cutoff >= 3 and cutoff * gap**2 >= 36, "quadratic fit premise")
        require(cutoff * gap >= 2 * (4 + ELL), "ell=16 fit premise")
        require(0 < gap <= 1 - saving and previous < exponent < saving < 1, "stage order")
        found.append(cutoff)
    require(len(found) == 7, "stage count")
    return saving


def controls():
    rejected = 0
    require(not coefficient_room(1) or SIGMA == 6748, "internal")
    require(Fraction(28, 17) * 4097 == SIGMA, "6748 identity")
    require(not (Fraction(28, 17) * (4096 + 1) <= 6747), "6747 must miss w=1")
    rejected += 1
    require(not (2 * (4096 + 1) <= SIGMA), "weak depth factor 2 is not sigma 6748")
    rejected += 1
    require(8 * 8195 > 2**16 and 8 * SIGMA <= 2**16, "ell=16 excludes the rounded 8195")
    rejected += 1
    require(not padding_fits(3, 0), "nonpositive stock is outside the wrapper")
    rejected += 1
    require(not packet_comparison_proved(M_CLAIM), "q equal to the lcm multiplier is not enough")
    rejected += 1
    require(2**17 * 43**28 >= 64**28, "rank 43 loses the depth certificate")
    rejected += 1
    require(lcm(LIVE, PHYSICAL) != PHYSICAL, "physical role count is not the lcm")
    rejected += 1
    # A cutoff of 1 cannot satisfy the ell=16 linear premise for a positive gap.
    require(not (1 * Fraction(1, 10) >= 2 * (4 + ELL)), "unit cutoff is not an ell=16 guard")
    rejected += 1
    return rejected


def main():
    assembly = authenticate()
    require(lcm(LIVE, PHYSICAL) == M_CLAIM, "lcm")
    require(M_CLAIM // LIVE == 9475, "live quotient")
    require(M_CLAIM < 2**80, "selected prime floor dominates the multiplier")
    require(2**17 * 42**28 < 64**28, "depth certificate")
    require(64**2 == 4096, "matrix dimension")
    for width in range(1, 4097):
        require(coefficient_room(width), "coefficient room")
    for atom_count in range(0, 65537):
        require(depth_bound_holds(atom_count), "finite depth bound")
    threshold = 64
    for level in range(1, 28):
        require(depth(threshold) >= level, "threshold depth")
        if threshold > 64:
            require(depth(threshold - 1) < level, "threshold is first")
        threshold = 64 * -(-threshold // 42)
    native = stages(assembly, "complex_lower", "bootstrap")
    conservative = stages(assembly, "conservative_complex_lower", "conservative_bootstrap")
    require(native > 0 and conservative > 0, "positive selected savings")
    # The recorded stage-1 cutoff is not the separate c=17/10000 uniform cutoff.
    require(int(assembly["bootstrap"][0]["cutoff_log2"]) != 311311, "do not identify PR2324's cutoff")
    rejected = controls()
    for radix, stock in ((2, 1), (2, 2), (3, 5), (5, 25), (5, 24), (7, 48)):
        require(padding_fits(radix, stock), "small padding fixture")
    receipt = {
        "sigma": SIGMA,
        "ell": ELL,
        "lcm": M_CLAIM,
        "live_quotient": 9475,
        "stages": 14,
        "controls_rejected": rejected,
        "rounded_predecessor_coefficient": 8195,
        "uniform_cutoff_not_identified": 311311,
        "no_new_kappa": True,
    }
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(expected == receipt, "RESULT.json mismatch")
    print(
        "PASS_SELECTED_LCM_STOCK_WRAPPER_FIT"
        f" sigma={SIGMA} ell={ELL} stages=14 lcm={M_CLAIM}"
        f" controls={rejected} no_new_kappa"
    )


if __name__ == "__main__":
    main()
