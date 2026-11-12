"""Check all eight independent bank and witness dispositions against the lead."""
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "lead/RESULT.json": "c38fb8b852643ab18de9d592340f1b601a26fe176a1210246ebefde5e7c63dae",
    "independent/RESULT.json": "ffad248be13a6451842a2cc3fd2564d65749cc456e87386cc0b4f389fe13cdc6",
}


def checked(name):
    data = (ROOT / name).read_bytes()
    if sha256(data).hexdigest() != PINS[name]:
        raise ValueError("changed receipt " + name)
    return loads(data)


def main():
    assert __debug__
    lead, independent = map(checked, PINS)
    assert not lead["unvisited_banks"] and not independent["unvisited"]
    assert len(lead["results"]) == len(independent["results"]) == 8
    for a, b in zip(lead["results"], independent["results"], strict=True):
        assert a["key"] + [a["clock"]] == b["key"]
        assert set(a["bank_roles"]) == {b["diagonal"], *b["public_donors"]}
        assert (a["destination"], a["source"], a["destination_chart"], a["excluded_owned_roles"]) == (
            b["destination"], b["source"], b["chart"], b["omitted_owned"])
        assert b["status"] == "outside relaxed span"
        proof = b["proof"]
        if a["status"] == "coordinate exclusion":
            j, signed = a["witness"]
            assert j == proof["coordinate"]
            assert Fraction(signed) == Fraction(a["literal_coefficient"]) * Fraction(proof["target_coefficient"])
        else:
            assert a["status"] == "rational exclusion" and proof["status"] == "exact_rank_exclusion"
            assert a["exact"]["rank"] == proof["donor_rank"]
            assert {int(j): int(v) for j, v in a["exact"]["residual"].items()} == {
                int(j): v for j, v in proof["residual_integer_row"].items()}
    print(dumps(dict(bank_and_disposition_agreement=8, pins=PINS,
        signed_coordinate_agreement=7, exact_residual_agreement=1, unresolved=0),
        indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
