# SPDX-License-Identifier: Apache-2.0
"""Compare the original-74 construction with the published #7612 and #7617 lineages."""
import argparse
from fractions import Fraction as Q
from functools import cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CANDIDATE = "5ab1da9cae4ffb118ce79270108f879e50365c8adcb89d02d78158ffb0908d8c"
BASE7605 = "e20f3f9240ac3f5fa4bbd7ab9b5550d660886901bb209f335409c329ac45d9cd"
HEAD12 = "e814828ee5b869c9468282d57ba28c364b07d130"
HEAD17 = "12f6626e194808fa38f473a3e84b2f81e169e3d3"
BLOBS = {
    "7612-word.json.gz": "8f530e70f8ce01c13f1c6f0eeba0caa5b6c8ad23",
    "7612-invoice.json": "9a2c003c454a8ef8e6129464ee7c9825c91cc42a",
    "7617-word.json.gz": "e7bed7968c781c581a662224e58477e8a714f674",
    "7617-invoice.json": "35414003924c7fef82b07e2e8222e3fdb61502d1",
    "NOTICE-7612": "2986720dc161a10752a1fffe13674fb26cfa44ac",
    "NOTICE-7617": "684e997ec5ba3f47193f7e0ef05364d89bb63014",
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def canonical(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":")).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def read_word(path, expected=None):
    raw = gzip.decompress(path.read_bytes())
    word = json.loads(raw)
    if expected is not None:
        require(digest(canonical(word)) == expected, f"word digest {path}")
    return word


@cache
def ratio(value):
    return Q(value)


def clear_rows(w):
    # Reverse each erased scalar functional to the public inputs. MOVE has
    # identity action in the normalized frame and never changes coefficients.
    program = w["program"]
    rows = []
    for clock,clear in enumerate(program):
        if clear[0] != "CLEAR":
            continue
        coeff = {clear[1]:Q(1)}
        for i in range(clock-1,-1,-1):
            e = program[i]
            op,dest = e[:2]
            weight = coeff.get(dest)
            if weight is None or op == "MOVE":
                continue
            if op in ("COPY","INIT","CLEAR"):
                del coeff[dest]
            if op in ("COPY","ADD"):
                source = e[2]
                new = coeff.get(source,0) + ratio(e[3])*weight
                if new:
                    coeff[source] = new
                else:
                    coeff.pop(source,None)
            elif op == "SCALE":
                coeff[dest] *= ratio(e[2])
            else:
                require(op in ("INIT","CLEAR"),f"unknown event {op}")
        require(all(r < w["public"] for r in coeff),"unbound initial private field")
        rows.append((clear[1],clear[2],{str(k):str(v) for k,v in sorted(coeff.items())}))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate",type=Path,required=True)
    parser.add_argument("--source7605",type=Path,required=True)
    parser.add_argument("--gate",type=Path,required=True)
    parser.add_argument("--signed",type=Path)
    parser.add_argument("--out",type=Path,required=True)
    args = parser.parse_args()
    for name,expected in BLOBS.items():
        raw = (HERE/name).read_bytes()
        require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==expected,f"Git blob {name}")
    candidate = read_word(args.candidate,CANDIDATE)
    old = read_word(args.source7605,BASE7605)
    historic = read_word(HERE/"7612-word.json.gz","ff380ae02b238bdf41db5247a2278f7e7be391fe49879f91950fdb775a0f983a")
    dual = read_word(HERE/"7617-word.json.gz")
    read = lambda path:json.loads(path.read_bytes())
    gate = read(args.gate)
    require(gate["candidate"]==CANDIDATE,"wrong gate")
    paid,targets = gate["paid"],gate["targets"]
    invoice12 = read(HERE/"7612-invoice.json")
    invoice17 = read(HERE/"7617-invoice.json")
    require(paid==invoice12["paid"] and targets==invoice12["targets"],"historical tariff differs")
    require(sum(paid.values())==110264 and sum(targets.values())==22461,"candidate bill totals")
    if args.signed:
        signed=read(args.signed)
        require(signed["price"]["new_native"]==CANDIDATE and signed["price"]["after"]["P"]==paid
                and signed["price"]["after"]["T"]==targets,"signed caller receipt")
    actual,original,other = (clear_rows(w) for w in (candidate,old,historic))
    require(len(actual)==len(original)==len(other)==74 and actual==original,"original 74 erased rows")
    changes=[i for i,(a,b) in enumerate(zip(actual,other)) if a!=b]
    require(changes==[44],"historic differing erasures")
    original44 = ("1557","595",{"451":"-1","902":"-3/2","985":"-3/2","1495":"1"})
    historic44 = ("1557","595",{"451":"-1","1495":"1"})
    for row,expected in ((actual[44],original44),(other[44],historic44)):
        require((str(row[0]),str(row[1]),row[2])==expected,"CLEAR44 witness")
    two = ["MOVE",226,719,127,False]
    second = ["MOVE",532,3,746,False]
    half = ["ADD",134,329,"-1/2",373]
    require(all(dual["program"].count(e)==1 for e in (two,second,half)),"historic #7617 routes")
    require(all(candidate["program"].count(e)==1 for e in (two,half)) and second not in candidate["program"],"original-74 routes")
    require(sum(e[0]=="CLEAR" for e in dual["program"])==113 and invoice17["targets"]==targets
            and sum(invoice17["paid"].values())==110179,"historic #7617 scope")
    result = dict(status="PASS_FIXED_TARIFF_AND_ERASURE_COMPARISON",candidate=CANDIDATE,
                  peer7612_head=HEAD12,peer7617_head=HEAD17,git_blobs=BLOBS,
                  checked_all_paid_ranks=len(paid),checked_all_productive_ranks=len(targets),
                  paid_positions=110264,productive_positions=22461,peer7612_fixed_tariff_identical=True,
                  checked_original_erased_rows=len(actual),candidate_equals_original=True,
                  peer7612_differing_erasure_ordinals_zero_based=changes,original_44=actual[44],peer7612_44=other[44],
                  unit_input_902={"original7605_and_candidate":"-3/2","historic7612":"0"},
                  equal_ordered_erasure_digest=digest(canonical(actual)),peer7612_ordered_erasure_digest=digest(canonical(other)),
                  peer7617=dict(word=digest(canonical(dual)),erased_rows=113,paid_positions=110179,productive_positions=22461,
                                courier226_and_contact=True,additional_532_courier=True),
                  signed_receipt_sha256=digest(args.signed.read_bytes()) if args.signed else None)
    args.out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(result["status"],"rank histograms identical; original and #7612 disagree at CLEAR44",flush=True)


if __name__=="__main__":
    main()
