#!/usr/bin/env python3
"""Replace 1/6400 on the one #4174 layout with L > p.

The comparison is r (2/B + beta) <= C p 2^{-G} at r = r_max. The layout
is p=2, ell=2, and 65536 widths of 1. No other layout is scanned, and
no new kappa is claimed.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "research" / "crt-reservoir-length-constant"
ALLOCATOR = ROOT / "research/crt-reservoir-placement/allocator.py"

# The minus signs in the exponent are U+2212, as printed in PROOF.md.
ABSORPTION = "r (2/B + β) < r (2 + 2^{1−62G}) 2^{−G} ≤ p 2^{−G} / 6400."


def need(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("FAIL: " + message)


def pins_and_phrases() -> None:
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in sources["files"]:
        if row["usage"] == "input":
            digest = hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest()
            need(digest == row["sha256"], row["path"])
    proof = (ROOT / "research/compact-switch-sharp-density/PROOF.md").read_text(encoding="utf-8")
    need(ABSORPTION in proof, "printed 1/6400 absorption")
    # certificates/selected-result.json is a provenance pin, checked at base_commit by scripts/research_package.py.


def load_allocator():
    spec = importlib.util.spec_from_file_location("crt_reservoir_allocator", ALLOCATOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sharp_unit(guard: int) -> int:
    """(2/B + beta) * 2^{G + 63G}, with B = 2^G and beta = 2(B-2)/2^{64G}."""
    return (1 << (1 + 63 * guard)) + (1 << (1 + guard)) - 4


def published_unit(guard: int) -> int:
    """(2/B + 8B/2^K) * 2^{G + 63G}."""
    return (1 << (1 + 63 * guard)) + (1 << (3 + guard))


def fits(numerator: int, constant_num: int, constant_den: int, modulus: int, scale: int) -> bool:
    """numerator / scale <= (constant_num / constant_den) * modulus."""
    return numerator * constant_den <= constant_num * modulus * scale


def one_layout(allocator) -> None:
    layout = allocator.Layout(2, 2, (1,) * 65536)
    need(layout.p == 2 and layout.ell == 2 and layout.L == 65536, "longer layout")
    need(layout.G == 256 and layout.r_max == 2, "longer guard and batch")
    need(layout.L > layout.p, "address longer than p")
    guard = layout.G
    batch = layout.r_max
    modulus = layout.p
    scale = 1 << (63 * guard)
    sharp = batch * sharp_unit(guard)
    published = batch * published_unit(guard)
    # Exact sharp ratio C_* = sharp / (p * 2^{63G}) = 2 + 2^{-15871} - 2^{-16126}.
    need(sharp == (1 << 16130) + (1 << 258) - 8, "exact sharp numerator")
    need(2 * modulus * scale < sharp < 3 * modulus * scale, "sharp ratio is strictly between 2 and 3")
    need(not fits(sharp, 1, 6400, modulus, scale), "1/6400 fails on the sharp term")
    need(not fits(sharp, 2, 1, modulus, scale), "integer 2 fails on the sharp term")
    need(fits(sharp, 3, 1, modulus, scale), "integer 3 holds on the sharp term")
    # Published window ratio C = published / (p * 2^{63G}) = 2 + 2^{-15869}.
    need(published == (1 << 16130) + (1 << 260), "exact published numerator")
    need(2 * modulus * scale < published < 3 * modulus * scale, "published ratio is strictly between 2 and 3")
    need(not fits(published, 1, 6400, modulus, scale), "1/6400 fails on the published term")
    need(not fits(published, 2, 1, modulus, scale), "integer 2 fails on the published term")
    need(fits(published, 3, 1, modulus, scale), "integer 3 holds on the published term")


def production_majorant() -> None:
    """The recorded production plan still fits the old constant under factor < 3."""
    need(5 * 3 * 6400 <= 9240576, "production majorant still fits 1/6400")


def main() -> None:
    pins_and_phrases()
    one_layout(load_allocator())
    production_majorant()
    print(
        "PASS_CRT_RESERVOIR_LENGTH_CONSTANT "
        "layout_p=2 layout_L=65536 r=2 G=256 sharp_between=2,3 integer_C=3"
    )


if __name__ == "__main__":
    main()
