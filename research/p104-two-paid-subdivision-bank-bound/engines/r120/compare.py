"""Check the exact primary minor on all three independent modular prefixes."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/RESULT.json": "3fd4f688b25bcd213ff3bccdedbfeb4d254d125be90456f8bef686ef06fae664",
    "independent/RESULT.json": "94c051452dd777b23913f5dda60f170ae82ae8b3d989bef9ba9687acfccad1fb",
    "plan/PRICE.json": "b29ff21d96485317003db5d06d3332f71e7158de4fafbbc6b300a45fc5d5e3c6",
}
PRIME = 65537


def checked(name):
    raw = (ROOT / name).read_bytes()
    if sha256(raw).hexdigest() != PINS[name]:
        raise ValueError("changed dependency " + name)
    return loads(raw)


def residue(value):
    q = Fraction(value)
    return q.numerator * pow(q.denominator, -1, PRIME) % PRIME


def main():
    assert __debug__
    lead, independent, price = map(checked, PINS)
    assert lead["head"] == independent["head"] == price["head"]
    assert independent["prime"] == PRIME
    assert lead["raw_keys"] == independent["raw_excluded"] == price["raw_keys"]
    assert not lead["unresolved"] and not independent["unresolved"]
    assert independent["alias"]["shared_normalized_prefix"]
    for role, (previous, at, following) in independent["alias"]["nearest_contacts"].items():
        assert lead["moves"][role][0] == at
        assert lead["moves"][role][2:] == [previous + 1, following]
    for interval in price["intervals"]:
        span = {0}
        for v in interval["basis"]:
            assert v not in span
            span |= {v ^ u for u in span}
        assert sorted(span) == lead["fresh_spans"][str(interval["pair"])]
    axes = lead["proof"]["axes"]
    expected_matrix = [[residue(v) for v in row] for row in lead["proof"]["matrix"]]
    expected_determinant = residue(lead["proof"]["determinant"])
    cuts = []
    for row in independent["rows"]:
        assert row["rank"] == 2 and len(axes) == len(set(axes)) == 2
        actual = [[vector.get(str(j), 0) for j in axes] for vector in row["exterior"]]
        determinant = (actual[0][0] * actual[1][1] - actual[0][1] * actual[1][0]) % PRIME
        assert actual == expected_matrix and determinant == expected_determinant != 0
        cuts.append(row["cut"])
    assert len(cuts) == 3
    print(dumps(dict(pins=PINS, cut_agreement=cuts, raw_keys_agreement=len(price["raw_keys"]),
        primary_exact_axis=axes, primary_axes_matrix_mod_65537=expected_matrix,
        primary_axes_det_mod_65537=expected_determinant, unresolved=0),
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
