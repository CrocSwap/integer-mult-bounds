"""Registered source, partition, price and shortest-example replay."""
import hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from algorithms import frequency_blocks, scalar_small_field
from certificates import (constructions, controls, need, partitions_report,
                          permutation_reports, ternary_cases)
from example_check import collect as examples
from families import collect as family_certificates, endpoint
from literal import identity_pass, reduce_matrix
from monomial import flat_rows
from orbit_oracle import normalize, orbit_weight
from reduction import collect as reduction
from settlement import Field, add_row, partition, ternary_extra


def frozen(name, obj):
    need(json.loads(json.dumps(obj))==json.loads((HERE/name).read_text(encoding="utf8")),
         "frozen certificate: "+name)


def sources():
    meta=json.loads((HERE/"SOURCES.json").read_text(encoding="utf8"))
    kept=[r for r in meta["files"] if "vendored_as" in r]
    for r in kept:
        data=(HERE/r["vendored_as"]).read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        need(r["git_blob"]==blob and r["sha256"]==hashlib.sha256(data).hexdigest(),
             "retained source bytes")
        if "upstream_origin" in r:
            origin=r["upstream_origin"]
            need(origin["commit"]=="465a0060fbd236a5e202619de4a45a694d44970a"
                 and origin["git_blob"]==blob and r["pin"]=="head:59457846216d7c5173fbeb4179ca120d0b32c2d3:"+r["path"],
                 "pending source identity")
    need(len(kept)==5,"retained source count")
    return len(kept)


def smoke():
    controls()
    f=Field(5)
    u,rows=add_row(f,(2,3),[(1,1)],0,1,1)
    need(u==(0,3) and rows==((1,0),),"dual inverse sign")
    need(len(partition(f,[(1,),(4,),(2,),(3,)]))==2,"two disjoint blocks")
    need(frequency_blocks(f,[(1,),(4,),(2,),(3,)])==2,"frequency boundary")
    need(scalar_small_field(f,(1,2,2,2,2,2,2,2))==2,"five-element normal form")
    f3=Field(3)
    need(normalize(f3,(0,2,1))==(0,1,2) and normalize(f3,(2,2,1))==(1,1,2),"projective types")
    need(orbit_weight((0,2),2)==4,"free orbit weight")
    need(reduce_matrix(f3,[(0,1),(1,0)])[0]==2,"literal determinant sign")
    need(endpoint(1,0,True)["cost"]==2 and endpoint(1,0,False)["cost"]==1,"sharp endpoint anchors")
    need(endpoint(1,1,False)["cost"]==1,"shared improvement")
    need(ternary_extra((2,2))==0,"negative ternary ordering")
    need(flat_rows(f3,(1,0),[(0,1)])==[(1,0),(1,1),(1,2)],"parameter coverage")
    examples_on_disk=json.loads((HERE/"EXAMPLES.json").read_text(encoding="utf8"))
    need([v["minimum"] for v in examples_on_disk]==[2,3,2,1,2],"small word fixture anchors")


def main():
    count=sources()
    if sys.argv[1:]==["--controls"]:
        smoke()
        print(json.dumps(dict(status="PASS_SETTLEMENT_CONTROLS",sources=count)))
        return
    if sys.argv[1:]:
        raise ValueError("unrecognized verification mode")
    smoke()
    reports=partitions_report()
    orders=permutation_reports()
    ternary=ternary_cases()
    endpoints=family_certificates()
    decisions=reduction()
    shortest=examples()
    for name,value in [("PARTITIONS.json",reports),("ORDERS.json",orders),("TERNARY.json",ternary),
                       ("WITNESSES.json",constructions()),("PRICE-ENVELOPE.json",endpoints),
                       ("REDUCTION.json",decisions),("EXAMPLES.json",shortest)]:
        frozen(name,value)
    print(json.dumps(dict(status="PASS_MONOMIAL_GUARD_SETTLEMENT",sources=count,
                          zero_sums=sum(r["scalar_cases"] for r in reports),
                          order_subsets=sum(r["named_subsets"] for r in orders),
                          shortest_examples=[r["minimum"] for r in shortest],envelope_cases=len(endpoints),
                          reduction_cases=sum(r["no"]+r["yes"] for r in decisions))))


if __name__=="__main__":
    main()
