"""Bind all 43 coframed aliases to one paid edit and one crossed read."""
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PINS={
    "inputs/R106-PRICE.json":"4ac52a9f1b56a86cb96d9eb6f3be9f635a58b7341ce10905c4a40e296c0f7f8a",
    "inputs/R106-RETIMING.json":"75569c300403795c4859263f823dee3c165979afaf32b8943201e31b1a050120",
}


def main():
    docs={}
    for path,pin in PINS.items():
        raw=(ROOT/path).read_bytes()
        if sha256(raw).hexdigest()!=pin:
            raise ValueError(f"changed dependency {path}")
        docs[path]=json.loads(raw)
    price,retime=docs.values()
    assert price["head"]==retime["head"] and retime["timeout"] is None
    assert retime["counts"]=={"recipient contact barrier":43,"wrong chart":33517}
    key=[44611,46018,532]
    row=next(r for r in retime["rows"] if r["key"]==key)
    q=next(r for r in price["candidate_rows"] if r["key"]==key)
    block=[s for side in row["sides"] for s in side["intervals"] if s[2]=="recipient contact barrier"]
    assert block==[[45976,46018,"recipient contact barrier",127]]
    old,add=q["add"]
    crossed=next((t,e) for t,e in row["nearest_barriers"] if t>old)
    assert crossed==(44613,["ADD",198,205,"-1/2",207]) and add==["ADD",205,532,"-1/2",207]
    correction=Q(add[3])*Q(crossed[1][3])
    assert correction==Q(1,4)
    quote=q["quote"]
    assert Q(quote["full_probe"][0])>0>Q(quote["extra_rank_one_upper"])
    print(json.dumps(dict(head=price["head"],caller=price["caller"],pins=PINS,word_sha256=price["word_sha256"],
        payload_sha256=price["payload_sha256"],key=key,charts=q["charts"],old_add=q["add"],crossed=crossed,
        correction=str(correction),cuts=block[0][:2],price=quote,distinct_paid_edits=1,
        whole_upper=quote["net"][1],old_paid=price["old_paid"],new_paid=price["new_paid"],productive=price["productive"],
        limits={"donor_banks":1,"typed_late_cuts":43,"seconds":20,"prototype_cases":1,"prototype_seconds":120}),
        indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
