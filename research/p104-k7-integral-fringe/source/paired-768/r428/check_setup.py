"""Bind the Round 420 installed census to the integral-fringe selector."""

from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import runpy
import sys


BASE = "bd3bf241376d7e4e044ee8f92705c0a71bc059e52dabd8e56d971e418b69216a"
IMAGE = "6dc565fad3b91bcb43ff71397897afcc54fd5f9d595a8f88b91234994d8e70be"


def extend(root):
    source = root / "r420/setup/check_installed.py"
    if sha256(source.read_bytes()).hexdigest() != BASE:
        raise ValueError("The installed Round 420 census wrapper differs")
    census = runpy.run_path(str(source))["extend"](root)
    selectors = census["SELECTORS"]
    if set(selectors) != {"peer", "candidate", "period"}:
        raise ValueError("The inherited installed census selectors differ")
    selectors["fringe"] = IMAGE, Fraction(".003900857312674")
    return census


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--handoff-root", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    parser.add_argument("--portable", type=Path, required=True)
    parser.add_argument("--scratch", type=Path, required=True)
    args = parser.parse_args()
    main = extend(args.handoff_root.resolve())["main"]
    sys.argv[1:] = ("--profile", "fringe", "--runtime", str(args.runtime),
                    "--portable", str(args.portable), "--scratch", str(args.scratch))
    main()
