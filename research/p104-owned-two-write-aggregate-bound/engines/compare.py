"""Compare the two exact R122 aggregate and endpoint bank receipts."""
from hashlib import sha256
from json import dumps,loads
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "lead/RESULT.json":"6d040aae3e99a8261152c17965b692b964d18ed7139c7a003da50934ec8d2098",
    "independent/RESULT.json":"12d42fc77b2de5d955744259741e63d0e4fbe0735ca290103c6a024557ec6996",
}


def checked(name):
    raw=(ROOT/name).read_bytes()
    if sha256(raw).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency "+name)
    return loads(raw)


def main():
    assert __debug__
    primary,reverse=map(checked,PINS)
    assert (primary["head"],primary["caller"])==(reverse["head"],reverse["caller"])
    for key in ("plan/PRICE.json","inputs/7334-WORD.json.gz"):
        assert primary["pins"][key]==reverse["pins"][key]
    assert primary["old_adds"]==reverse["old_adds"]
    assert primary["aggregate"]==reverse["aggregate"] and len(reverse["aggregate"])==219
    assert not primary["unvisited"] and not reverse["unvisited"]
    assert primary["timeout"] is reverse["timeout"] is None
    assert reverse["progress"]=={"events":76466,"last_unvisited":None}
    banks=[]
    for a,b in zip(primary["results"],reverse["results"],strict=True):
        assert a["key"]==b["key"] and a["old_owner_diagonal_clock"]==b["old_owner_diagonal_clock"]==41996
        assert a["read_only_donors"]==sorted(b["read_only_public"]+b["read_only_owned"])
        assert a["status"]=="coordinate exclusion" and b["proof"]["status"]=="absent_exterior_coordinate"
        assert a["witness"]==[b["proof"]["coordinate"],b["proof"]["target_coefficient"]]==[244,"-1/2"]
        banks.append(dict(key=a["key"],read_only_donors=a["read_only_donors"],
            donor_rank=b["proof"]["donor_rank"],augmented_rank=b["proof"]["augmented_rank"]))
    assert len(banks)==2
    print(dumps(dict(pins=PINS,bank_agreement=banks,old_adds=reverse["old_adds"],
        aggregate_nonzero_coordinates=219,common_separator={"244":"1"},separator_value="-1/2",unresolved=0),
        indent=2,sort_keys=True))


if __name__=="__main__":
    main()
