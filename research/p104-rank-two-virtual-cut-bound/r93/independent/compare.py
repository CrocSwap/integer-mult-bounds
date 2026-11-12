"""Verify all exact exterior witnesses reduce to the primary R93 field values."""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

PINS={
    "lead":"01ad2a656e69699b80b56d63cdf82448e424cd1c6e67636d53c079a6f03f55a5",
    "independent":"2800af56efe23f7420a12f0713a659cd4fa4a3fb7c58449749ef697097ccccbf",
}


def unique(pairs):
    result=dict(pairs)
    if len(result)!=len(pairs):
        raise ValueError("duplicate JSON key")
    return result


def first_residue(entries,prime):
    first=None
    for i,encoded in entries:
        q=Fraction(encoded)
        assert q.denominator%prime
        value=q.numerator*pow(q.denominator,-1,prime)%prime
        if value and first is None:
            first=[i,value]
    return first


def main():
    documents={}
    for key,arg in zip(PINS,sys.argv[1:],strict=True):
        raw=Path(arg).read_bytes()
        if sha256(raw).hexdigest()!=PINS[key]:
            raise ValueError("changed dependency: "+key)
        documents[key]=json.loads(raw,object_pairs_hook=unique)
    lead,independent=(documents[key] for key in PINS)
    assert lead["head"]==independent["head"] and lead["prime"]==65537
    assert not lead["unvisited"] and not lead["unresolved"] and not lead["exact_selected"]
    assert not independent["unvisited"] and not independent["survivors"]
    assert len(lead["results"])==len(independent["results"])==95
    for modular,exact in zip(lead["results"],independent["results"],strict=True):
        assert modular["key"]==exact["key"] and modular["status"]=="exterior_on_both"
        assert exact["status"]=="no_nonzero_pure_prefix" and exact["prefix_nonzero"] and exact["suffix_nonzero"]
        for side in ("prefix_exterior","suffix_exterior"):
            first=first_residue(exact[side],lead["prime"])
            assert first and first==modular[side]
    print(json.dumps(dict(head=lead["head"],pins=PINS,prime=lead["prime"],
        compared_keys=95,matched_nonzero_prefix_witnesses=95,matched_nonzero_suffix_witnesses=95,
        unresolved=0,paired_support_tests=0),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
