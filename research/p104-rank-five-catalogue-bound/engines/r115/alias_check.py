"""Independently certify all eight adjacent R115 row-operation aliases."""
from argparse import ArgumentParser
from collections import defaultdict
from fractions import Fraction
from gzip import decompress
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent
PINS = {
    "inputs/SELECTION.json":"a9d4cb3acf6ad489c631ae984665391fbacfc069a2ba8d4521970ed5dd46bb88",
    "inputs/GEOMETRY.json":"c2a4406cf7130a819189e8ceefb4bb6e09edd392eb56820f9fcadb0e9415ef4e",
    "inputs/ALIASES.json":"6a79a44ec164d1c1e1b3c276912ff4a37334ef17268e555330b8fe17a126d4e3",
    "RESULT.json":"6bb721c8824fd107acefd570cce44d51ecc2baef351075806c6fe91fba329c87",
    "inputs/7334-WORD.json.gz":"4b9fd1187b34ed97c3ac0c760d73531735a5d0ebc5b4d4ab4377160b20d9bb2a",
}
GROUP=(3,241)


def unique(items):
    result=dict(items)
    if len(result)!=len(items):
        raise ValueError("duplicate JSON key")
    return result


def read(root,name):
    data=(root/name).read_bytes()
    if sha256(data).hexdigest()!=PINS[name]:
        raise ValueError("changed dependency: "+name)
    if name.endswith(".gz"):
        data=decompress(data)
        assert sha256(data).hexdigest()=="9aa8d6b054ba7eb2289d052c1079b16be518d2f0fbfb244569fa18e3733acdac"
    return loads(data,object_pairs_hook=unique)


def determinant(event,bank,chart):
    op,d,*args=event
    assert d in bank and event[-1]==chart
    if op=="ADD":
        source,coefficient,_=args
        assert source in bank and source!=d and Fraction(coefficient)
        return Fraction(1)
    assert op=="SCALE" and Fraction(args[0])
    return Fraction(args[0])


def main():
    assert __debug__
    parser=ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    args=parser.parse_args()

    def stop(*_):
        raise TimeoutError("hard 20-second alias cap")

    signal(SIGALRM,stop)
    alarm(20)
    try:
        selection,geometry,primary,modular=[read(args.root,name) for name in PINS if not name.endswith(".gz")]
        assert selection["selected_group"]==list(GROUP)
        assert not primary["timeout"] and not primary["unvisited"] and primary["cap_cases"]==19
        assert modular["agreement"] and modular["counts"]=={"excluded":11}
        geometry_rows={tuple(r["key"]):r for r in geometry["candidate_rows"] if tuple(r["key"][2:])==GROUP}
        anchors={tuple(r["key"])+GROUP for r in modular["rows"]}
        pending={tuple(k) for k in selection["unselected"] if tuple(k[2:])==GROUP}
        assert len(geometry_rows)==19 and len(anchors)==11 and len(pending)==8
        assert not anchors&pending and anchors|pending==geometry_rows.keys()
        parent={key:key for key in geometry_rows}

        def root(key):
            while parent[key]!=key:
                key=parent[key]
            return key

        word=read(args.root,"inputs/7334-WORD.json.gz")
        tape=word["program"]
        links=[]
        for link in primary["links"]:
            if not link["alias"]:
                continue
            left,right=map(tuple,(link["left"],link["right"]))
            t,chart,*_=left
            assert right==(t+1,chart,*GROUP) and not link["blockers"]
            a,b=geometry_rows[left],geometry_rows[right]
            assert all(a[f]==b[f] for f in ("public","owned","pivots"))
            assert all(r<word["public"] for r in a["public"])
            value=determinant(tape[t],set(a["public"]),chart)
            assert value
            parent[root(right)]=root(left)
            links.append(dict(left=left,right=right,event=tape[t],determinant=str(value)))
        assert len(links)==8
        blocks=defaultdict(list)
        for key in sorted(geometry_rows):
            blocks[root(key)].append(key)
        groups=sorted(blocks.values())
        original=sorted(sorted(map(tuple,row["keys"])) for row in primary["classes"])
        assert groups==original and len(groups)==11
        assert all(len(anchors.intersection(group))==1 for group in groups)
    finally:
        alarm(0)
    print(dumps(dict(pins=PINS,group=GROUP,raw_banks=19,independent_prefix_anchors=11,
        checked_aliases=8,groups=groups,links=links,whole_group_excluded=True),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
