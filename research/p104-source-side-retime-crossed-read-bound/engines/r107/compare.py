"""Authenticate the two exact R107 receipts and compare their dispositions."""
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/CORRECTION.json":"de53deb4f41a5ac8aba27ee47a1450d89eae8f092db327d5cc6ab6ed877f72d8",
    "RESULT.json":"b718f015ae558ba26aae8f751a67e6db55ec839a17b104c38e2da1c9beaab963",
}


def read(name,pin):
    raw = (ROOT/name).read_bytes()
    assert sha256(raw).hexdigest()==pin, name
    return loads(raw)


def main():
    assert __debug__
    primary,exact = [read(name,pin) for name,pin in PINS.items()]
    assert primary["head"] == exact["head"]
    assert exact["timeout"] is None and exact["progress"]["bank_checked"]
    p, q = primary["old_read_bank"], exact["bank"]
    assert all(p[k]==q[k] for k in ("cut","chart","owned_excluded","public"))
    assert p["target_nnz"]==len(q["original_source_row"][0])
    assert p["target_role"]==532 and p["rank"]==q["proof"]["donor_rank"]==9
    assert q["proof"]["augmented_rank"]==10 and p["matching_coefficients"] is None
    assert p["coordinate_separator"]==[q["proof"]["coordinate"],q["proof"]["probe_original_source"]]
    assert primary["exact_crossed_response"]==q["proof"]["separated_target"]=="1/4"
    assert not primary["late_eligible"] and exact["late_counts"]=={"different chart":43}
    assert len(primary["late_cuts"])==len(exact["typed_late_cuts"])==43
    for a,b in zip(primary["late_cuts"],exact["typed_late_cuts"],strict=True):
        assert a["cut"]==b["cut"] and a["recipient_chart"]==b["reader_chart"]==207
        assert a["status"]=="wrong recipient chart" and b["status"]=="different chart"
        assert b["required_chart"]==127 and b["first_crossed_read"] is None
    assert primary["next_recipient_barrier"]==exact["reader_incidents"][0]
    print(dumps(dict(pins=PINS,agreement=True,exact_bank_exclusions=1,typed_late_exclusions=43,
        separating_coordinate=27,missing_signed_response="1/4",wrong_late_chart=207,required_late_chart=127),
        indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
