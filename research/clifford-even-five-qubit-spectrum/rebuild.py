"""Compare a fresh GAP export to the retained invariants, ignoring line wrapping."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
NAMES = ["Sp10", "O10+", "O10-", "P5"]
FAMILIES = ["Sp", "O+", "O-"]


def parse(path):
    text = path.read_text().replace("\\\n", "")
    groups, lower = json.loads("\n".join(
        line for line in text.splitlines() if not line.startswith("#I")
    ))
    corners = {
        name: {"polys": polynomials, "counts": counts, "columns": columns}
        for name, (polynomials, counts, columns) in zip(NAMES, groups, strict=True)
    }
    small = [dict(zip(FAMILIES, family, strict=True)) for family in lower]
    return {"corners": corners, "lower": small}


if __name__ == "__main__":
    if parse(Path(sys.argv[1])) != json.loads((ROOT / "CORNERS.json").read_text()):
        raise ValueError("GAP regeneration differs from the retained data")
    print("GAP export agrees on every spectral polynomial, multiplicity and packet column.")
