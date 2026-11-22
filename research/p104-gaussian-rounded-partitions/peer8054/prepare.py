"""Materialize the #8053 fixed-carrier peer and unsplit exactly two paid returns."""

import argparse
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys
import tempfile

PEER_HEAD = "e25494616bf149217644ce08d949181ea3600e13"
PINS = {
    "PEER-SOURCE.json": "91e965d76ef4d72aa68422c382c8be25fce47b16d610783a5e3872f82953cffc",
    "RESULT.json": "3d85ccaf415b33702951ceb14b78fa1f7f0964ba3f201bf07b9e8a6e96882220",
    "verify.py": "513229ad495efab7a738644d291eb19f84bc751d6a606e84183229d4549549ab",
}
EDITS = {
    "installations.py": (
        ("Q(1071523491, 2**38)", "Q(133940467, 2**35)"),
        ('Q(".0038981721342")', 'Q(".0038981730255")'),
    ),
    "retimed_supplier.py": (
        ("SMALL_SPLITS = 1008", "SMALL_SPLITS = 1006"),
    ),
    "unpowered_price.py": (
        ("paid[1] -= 1008", "paid[1] -= 1006"),
        ("paid[F(1, 2)] = 2016", "paid[F(1, 2)] = 2012"),
    ),
    "check_complete.py": (
        ('"gaussian_c_decimal": "0.003898179751558928"', '"gaussian_c_decimal": "0.003898180642863736"'),
        ('"extended_kappa": "0.0038981721342"', '"extended_kappa": "0.0038981730255"'),
    ),
    "check_installation.py": (
        ("105216, 564144, 54", "105216, 564142, 54"),
    ),
    "check_extended_stop.py": (
        ("105216,564144,54", "105216,564142,54"),
        ("F(1071523491,2**38)", "F(133940467,2**35)"),
    ),
    "check_nonzero_eight.py": (
        ("SMALL_SPLITS == 1008", "SMALL_SPLITS == 1006"),
    ),
}


def materialize(source: Path, work: Path) -> None:
    for name, digest in PINS.items():
        if sha256((source / name).read_bytes()).hexdigest() != digest:
            raise ValueError(f"#8053 differs at {name}")
    predecessor = runpy.run_path(str(source / "verify.py"))
    work.mkdir()
    predecessor["restore"](work)
    predecessor["edit_installation"](work)
    for name, edits in EDITS.items():
        path = work / name
        code = path.read_text()
        for search, replacement in edits:
            if code.count(search) != 1:
                raise ValueError(f"Expected one change point in {name}")
            code = code.replace(search, replacement)
        path.write_text(code)


def verify_price(work: Path) -> None:
    sys.path.insert(0, str(work))
    from bootstrap import install

    with tempfile.TemporaryDirectory() as temp:
        receiver = Path(temp) / "tree"
        install(receiver)
        sys.path.insert(0, str(receiver))
        from upstream import install as sources

        sources()
        from check_complete import all_results

        result = all_results()
    assert result["positive"]["paid"] == 564142
    trial = Fraction(result["profiles"]["extended"]["kappa"])
    assert trial == Fraction(".0038981730255")
    (work / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("PASS_TWO_UNSPLIT_RETURNS", trial, result["profiles"]["extended"]["signed_gate"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    source, out = args.source.resolve(), args.out.resolve()
    materialize(source, out)
    verify_price(out)
