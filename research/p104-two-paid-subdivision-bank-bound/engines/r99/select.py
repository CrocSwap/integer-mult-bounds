"""Freeze at most 16 distinct two-mover normalized support forms."""
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PIN = "c89976cd5f808c29ab13770e262b2d216f56b4e1703ef836c3438d60f40eb11b"


def main():
    raw = (ROOT/"lead/GEOMETRY.json").read_bytes()
    assert sha256(raw).hexdigest() == PIN
    geometry = json.loads(raw)
    assert geometry["stage"] == "complete" and not geometry["timeout"]
    groups = defaultdict(list)
    for row in geometry["representatives"]:
        t,i = row["key"]
        window = geometry["pair_intervals"][i]
        a,d,*_ = window["left"]
        b,e,*_ = window["right"]
        group = tuple(sorted(((a,d),(b,e))))
        assert not row["owned"] and row["public"] == row["pivots"] == sorted((d,e))
        assert window["first"] <= t <= window["last"]
        groups[group].append((row,window))
    entries = []
    for key,rows in groups.items():
        # Original rank/phase normalized rows and columns stay fixed on both
        # movers. Their only incident events inside any window are their own
        # MOVEs, which are identity in normalized coordinates.
        windows = {(w["first"],w["last"]) for _,w in rows}
        assert len(windows) == 1
        rows.sort(key=lambda rw:(rw[1]["chart"] is None,rw[0]["key"]))
        chosen,w = rows[0]
        entries.append({"bank":chosen,"anchors":key,"chart":w["chart"],
                        "aliases":sorted(row["key"] for row,_ in rows[1:])})
    entries.sort(key=lambda r:(r["chart"] is None,r["bank"]["key"]))
    count = geometry["limits"]["modular_cases"]
    assert len(entries) == 17 and len({r["bank"]["key"][0] for r in entries}) == len(entries)
    print(json.dumps({"head":geometry["head"],"geometry_sha256":PIN,
                     "case_cap":count,"selected":entries[:count],"unselected":entries[count:]},
                     indent=2,sort_keys=True))


if __name__ == "__main__":
    main()
