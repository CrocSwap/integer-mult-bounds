"""Reconcile both R89 suffix fields on the exact frozen keys."""
from argparse import ArgumentParser
from fractions import Fraction
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS = {
    "keys":"a131ec5bf96baac89f0f6623cf7d9dff06601b36ea720474311ee7ecb394f6e2",
    "lead":"340d1beb37477198e4690a56153d1a225c8ad70e00cf470c07a5bc080c0255ad",
    "independent":"560a22da8219d5ca3d5ec9cb8fa25bdd32f068ca28242cdd4383351dbed82f67",
}


def main():
    p=ArgumentParser(description=__doc__)
    for name in PINS:
        p.add_argument(name,type=Path)
    a=p.parse_args()
    docs=[]
    for name,pin in PINS.items():
        raw=getattr(a,name).read_bytes()
        assert sha256(raw).hexdigest()==pin, f"Changed input {name}"
        docs.append(loads(raw))
    frozen,lead,ind=docs
    assert frozen["head"]==lead["head"]==ind["head"] and lead["prime"]==65521 and ind["prime"]==65537
    assert not lead["unvisited"] and not ind["unvisited"] and not ind["control_discrepancies"]
    assert len(ind["prior_exact_controls"])==6 and not ind["control_unvisited"]
    for left,right,key in zip(lead["results"],ind["tested"],frozen["keys"],strict=True):
        assert all(left[k]==right[k]==key[k] for k in ("key","public","owned","pivots"))
        assert left["suffix_rank_mod_65521"]==right["suffix_exterior_rank"]
        assert (left["disposition"]=="excluded")==(right["status"]=="no_nonzero_pure_suffix")
    assert lead["rank_drops"]==ind["suffix_rank_drops"] and len(ind["tested"])==2128
    remaining=[r for r in ind["tested"] if r["status"]=="modular_suffix_rank_drop"]
    pivots=sorted({p for r in remaining for p in r["pivots"]})
    assert len(remaining)==1465 and len(pivots)==109
    print(dumps(dict(head=lead["head"],pins=PINS,agreed_keys=2128,full_suffix_exclusions=663,
        suffix_rank_drops=1465,unresolved_before_exact_followup=1465,
        remaining_pivots=pivots,remaining_charts=len({r["key"][1] for r in remaining}),
        old_crossing_optimistic_gross_upper=str(len(pivots)*Fraction(frozen["at_incumbent"]["one_edit_credit"][1])),
        moonshot_optimistic_complete_upper=str(Fraction(frozen["at_moonshot"]["old_margin"][1])+
                                               len(pivots)*Fraction(frozen["at_moonshot"]["one_edit_credit"][1]))),
        sort_keys=True,indent=2))


if __name__=="__main__":
    assert __debug__
    main()
