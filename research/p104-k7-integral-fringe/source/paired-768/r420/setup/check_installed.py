"""Use the frozen nine-recipe census with the additional period selector."""
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import runpy

ROOT = Path(__file__).resolve().parents[2]
BASE = "e16fac0f9a91930575d4f11d50e4e26b357d2dcb0992470a679f6501904629e4"
IMAGE = "c5d83f8c6acdab6828185bc6bb67537cf320ba79ab177f9da535edae7b5af72e"


def extend(root=ROOT):
    source = root / "r416/setup/check_installed.py"
    if sha256(source.read_bytes()).hexdigest() != BASE:
        raise ValueError("The frozen installed census differs")
    census = runpy.run_path(str(source))
    selectors = census["SELECTORS"]
    assert set(selectors) == {"peer", "candidate"}
    selectors["period"] = IMAGE, Fraction(".003900857312000")
    return census


if __name__ == "__main__":
    extend()["main"]()
