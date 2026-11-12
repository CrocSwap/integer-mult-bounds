"""Reconcile the two exact R89 selected-bank proofs."""
from argparse import ArgumentParser
from hashlib import sha256
from json import dumps, loads
from pathlib import Path

PINS={
    "selection":"27a14af96296f0f2d162c77aa38e4051f3aaf8a8156dd654b414dd1196a6d597",
    "lead":"d2369e9657a8bb99cd07813f354a44e9fb02a74245a2ff188723d295d93ce609",
    "independent":"6821bf1f2df591d076528757fd02ce32e35743557ac33ee8b6a6810f4c81b4a3",
    "suffix":"560a22da8219d5ca3d5ec9cb8fa25bdd32f068ca28242cdd4383351dbed82f67",
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
    selection,lead,ind,suffix=docs
    assert lead["head"]==ind["head"]==suffix["head"]
    expected=[tuple(r["key"]) for r in selection["selected"]]
    old={tuple(r["key"]):r for r in lead["results"]}
    new={tuple(r["key"]):r for r in ind["results"]}
    assert len(expected)==6 and set(expected)==old.keys()==new.keys()
    assert not lead["selected_unresolved"] and not ind["unresolved"]
    assert lead["counts"]=={"no unit pairing":6} and ind["counts"]=={"no_exact_unit_pair":6}
    nullities=[]
    for key in expected:
        a,b=old[key],new[key]
        assert all(a[k]==b[k] for k in ("key","public","owned","pivots"))
        assert a["pure_prefix_dimension"]==b["prefix_nullity"]
        assert a["pure_suffix_dimension"]==b["suffix_nullity"]
        assert bool(a["nonzero_prefix_images"])==bool(b["nonzero_prefix_basis_images"])
        assert bool(a["nonzero_suffix_images"])==bool(b["nonzero_suffix_basis_images"])
        nullities.append([list(key),[b["prefix_nullity"],b["suffix_nullity"]]])
    remaining=[r for r in suffix["tested"] if r["status"]=="modular_suffix_rank_drop" and tuple(r["key"]) not in new]
    assert len(remaining)==1459
    print(dumps(dict(head=lead["head"],pins=PINS,exact_agreements=6,exact_unit_pairs=0,
        remaining_modular_drops=1459,remaining_literal_pivots=sorted({p for r in remaining for p in r["pivots"]}),
        exact_nullities=nullities),indent=2,sort_keys=True))


if __name__=="__main__":
    assert __debug__
    main()
