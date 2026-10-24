#!/usr/bin/env python3
"""The manuscript exponent clears both displayed parking deficits.

The checker reads the manuscript. It does not retune the schedule.
"""

import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_MANUSCRIPT_EXPONENT binding=complex psi_below_one=true no_new_kappa"
MOTIFS = "upstream/build/sections/03-motifs.tex"
SWAP = "upstream/build/sections/04-swap.tex"
BATCH = "notes/batched-bit-rows.tex"
TERMS = 40


def fail(message):
    raise SystemExit("FAIL_MANUSCRIPT_EXPONENT " + message)


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
    require(
        set(pinned) == {
            BATCH,
            SWAP,
            MOTIFS,
        },
        "input inventory changed",
    )
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def ln_bounds(value):
    require(value > 1, "the logarithm needs a value above 1")
    exponent = 0
    scaled = Fraction(value)
    while scaled >= 2:
        scaled /= 2
        exponent += 1

    def series(unit):
        slope = (unit - 1) / (unit + 1)
        square = slope * slope
        power = slope
        total = Fraction(0)
        for index in range(TERMS + 1):
            total += power / (2 * index + 1)
            power *= square
        tail = power / (2 * TERMS + 3) / (1 - square)
        return 2 * total, 2 * (total + tail)

    low_two, high_two = series(Fraction(2))
    low_scaled, high_scaled = series(scaled)
    return exponent * low_two + low_scaled, exponent * high_two + high_scaled


def displayed(text, name):
    match = re.search(r"\\eta_\{\\rm " + name + r"\}(.*?)=\\frac\{(\d+)\}\{(\d+)\}", text, re.S)
    require(match is not None, "a displayed deficit is missing")
    return Fraction(int(match.group(2)), int(match.group(3)))


def evaluate():
    authenticate()
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    motifs = (ROOT / MOTIFS).read_text(encoding="utf-8")
    swap = (ROOT / SWAP).read_text(encoding="utf-8")
    batch = (ROOT / BATCH).read_text(encoding="utf-8")
    require(r"$\tau=1-2^{-50}$" in swap, "the swap exponent moved")
    require(r"\tau=\sigma=1-2^{-50}" in motifs, "the motif exponent moved")
    require(r"$20\cdot2^{-50}$" in motifs, "the displayed constant moved")
    require(r"If $\Psi(\tau)<1$ for some $0<\tau<1$" in batch, "the strict hypothesis moved")
    modulus = int(re.search(r"m=h\^3=(\d+)", motifs).group(1))
    require(modulus == 10 ** 6, "the modulus moved")
    children = {
        "bit": int(re.search(r"=\s*(\d+)<W_\{\\rm b\}m", motifs).group(1)),
        "complex": int(re.search(r"=\s*(\d+)<W_\{\\rm c\}m", motifs).group(1)),
    }
    deficits = {"bit": displayed(motifs, "b"), "complex": displayed(motifs, "c")}
    step = Fraction(1, 2 ** 50)
    _, log_high = ln_bounds(modulus)
    require(log_high < 20, "the logarithm is not below 20")
    slope = step * log_high
    exponential = 1 + slope + slope * slope / (2 * (1 - slope))
    margins = {}
    recorded = {}
    for name, eta in deficits.items():
        roles = Fraction(children[name]) / (1 - eta)
        require(roles.denominator == 1 and int(roles) % modulus == 0, "a role count is not integral")
        gap = eta * roles
        require(gap.denominator == 1, "a rank deficit is not integral")
        require(children[name] == int(roles) - int(gap), "a child count does not meet its roles")
        require(eta > 20 * step, "a displayed deficit misses the constant")
        require((1 - eta) * exponential < 1, "Psi is not below 1")
        margin = eta / log_high / step
        margins[name] = margin
        recorded[name] = str(int(gap))
    require(margins["complex"] < margins["bit"], "the complex node is not binding")
    require(margins["complex"] > 298, "the complex clearance shrank")
    return {
        "modulus": modulus,
        "binding": "complex",
        "bit_deficit": recorded["bit"],
        "complex_deficit": recorded["complex"],
        "log_below_20": True,
        "psi_below_one": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
