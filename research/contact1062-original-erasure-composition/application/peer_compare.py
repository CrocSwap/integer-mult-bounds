# SPDX-License-Identifier: Apache-2.0
"""Compare the candidate's complete bill with Clear1nsight's pinned #7645 signed bill."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import accumulate
import json
from pathlib import Path
import runpy
from tempfile import TemporaryDirectory

HERE=Path(__file__).resolve().parent
PEER_HEAD="32abeefff4d5fcc378ab3de1c1a8bf1c37737bdd"
PINS={"FINAL.json":"5f27765f5e0f4171cd3568a32c48b2611f6a3b4a4c0a5e93f54ff1bfc2b56b99",
      "SIGNED-RESULT.json":"da2adf53f209c6c0cdc91757f814812fb309600596cdc999ea306e8e876652e1"}


def compare(source,work):
    assert __debug__
    signed_file=HERE/"peer7645/SIGNED-RESULT.json"
    for name,pin in PINS.items():
        assert sha256((HERE/"peer7645"/name).read_bytes()).hexdigest()==pin
    signed=json.loads(signed_file.read_bytes())
    final=json.loads((HERE/"peer7645/FINAL.json").read_bytes())
    assert final["claim"]=="0.0036521182092"
    assert Q(final["framework_claim"])==Q("0.003652118209307")==Q(signed["claim"])
    assert final["candidate_canonical_sha256"]==signed["price"]["new_native"]=="6c52b2fba7c20343a50cb92ed4b997aa9921c78f212ac6428d13fff2bcd014cf"
    assert signed["caller_sha256"]=="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
    p=signed["price"]["after"]
    assert p["S"]==1424 and p["empty_root_credits"]==0
    prepared=json.loads((work/"PREPARED.json").read_bytes())
    candidate_path=work/"frozen-composition/CANDIDATE-INVOICE.json"
    assert sha256(candidate_path.read_bytes()).hexdigest()==prepared["source_pins"]["frozen-composition/CANDIDATE-INVOICE.json"]
    candidate=json.loads(candidate_path.read_bytes())
    assert candidate["targets"]==p["T"]
    assert sum(p["P"].values())==sum(candidate["paid"].values())==110298
    own=Counter({int(k):v for k,v in candidate["paid"].items()})
    peer=Counter({int(k):v for k,v in p["P"].items()})
    diff=own.copy()
    diff.subtract(peer)
    assert all(n%17==0 for n in diff.values())
    positive=sorted((r for r,n in diff.items() for _ in range(max(0,n//17))),reverse=True)
    negative=sorted((r for r,n in diff.items() for _ in range(max(0,-n//17))),reverse=True)
    assert positive==[5,2,2,2] and negative==[6,3,1,1]
    assert all(i>=j for i,j in zip(accumulate(negative),accumulate(positive))) and sum(positive)==sum(negative)
    lib=source/"retained/pr7605/retained/pricing/evaluate_recursive_power.py"
    manifest=json.loads((source/"data/7605-closure.json").read_bytes())
    assert sha256((source/"data/7605-closure.json").read_bytes()).hexdigest()=="d4c2500703fd651d5eee8ae9dfd64439703716d1c43656f3455d66157a1912fd"
    for filename in (lib,lib.with_name("compare_recursive_invoices.py")):
        assert sha256(filename.read_bytes()).hexdigest()==manifest[filename.relative_to(source/"retained/pr7605").as_posix()]
    engine=runpy.run_path(str(lib))
    with TemporaryDirectory() as tmp:
        peer_path=Path(tmp)/"peer.json"
        peer_path.write_text(json.dumps(dict(candidate,paid=p["P"],targets=p["T"])))
        one,_=engine["load_invoice"](candidate_path)
        two,_=engine["load_invoice"](peer_path)
        zero=dict(one,paid={},targets={})
        kappa=Q(final["claim"])
        results={}
        for key,bill,sign in (("candidate_at_peer",one,"new_cost_higher"),("peer_at_peer",two,"new_cost_lower")):
            bound=engine["evaluate"](zero,bill,1-kappa,bits=256)
            assert bound["classification"]==sign
            results[key]=bound
        direct=engine["evaluate"](two,one,1-kappa,bits=256)
        assert direct["classification"]=="new_cost_higher"
        results["candidate_minus_peer_at_peer"]=direct
    difference=Q(prepared["claim"])-kappa
    return dict(status="PASS_SIGNED_INVOICE_COMPARISON",scope="Complete literal invoice and directed recurrence comparison. Peer application uses the exact published signed receipt.",peer_head=PEER_HEAD,peer_files=PINS,peer_candidate=final["candidate_canonical_sha256"],peer_public=final["claim"],peer_framework=final["framework_claim"],candidate=prepared["candidate"],candidate_public=prepared["claim"],absolute_delta=str(difference),percent_delta=str(100*difference/kappa),paid_delta={r:n for r,n in diff.items() if n},candidate_unmatched_per_invocation=positive,peer_unmatched_per_invocation=negative,majorization="With identical targets and equal rank masses, the peer sorted prefix sums dominate strictly. Strict concavity of x^t implies lower peer cost for every 0<t<1.",directed=results)


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    result=compare(args.source.resolve(),args.work.resolve())
    with args.out.open("x") as stream:
        json.dump(result,stream,sort_keys=True,indent=2)
        stream.write("\n")
    print(result["status"],result["absolute_delta"],result["percent_delta"])
