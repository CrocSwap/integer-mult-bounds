"""Authenticate the unchanged fallback files and run the multiplication interfaces."""

from hashlib import sha256
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from multiply import fallback_source, multiply_integer


def main():
    source = json.loads((HERE / "vendor/PINS.json").read_text())
    for item in source["files"]:
        data = (HERE / "vendor/direct-fourier" / Path(item["source"]).name).read_bytes()
        if sha256(data).hexdigest() != item["sha256"]:
            raise ValueError("A retained fallback file differs")
    program = fallback_source()
    small = program.Multiplier((3, 5), source_root=HERE.parents[1])
    result, coeffs = small.multiply(741503, 466013)
    if result != 345550037539 or coeffs[:5] != [11811, 10996, 4152, 868, 77] or any(coeffs[5:]):
        raise ValueError("The bound Fourier fallback lost a coefficient")
    x = (1 << 433) // 7 + (1 << 311) // 73
    y = (1 << 411) // 11 + (1 << 327) // 97
    receipt = {}
    if multiply_integer(-x, y, evidence=receipt) != -x*y or receipt["route"] != "ordinary":
        raise ValueError("The nonmember missed the signed recursive fallback")
    print("unchanged_fallback_files", len(source["files"]), "fourier_geometry", (3, 5),
          "product", result, "coefficients", coeffs[:5], "rejected_route", receipt["route"])


if __name__ == "__main__":
    main()
