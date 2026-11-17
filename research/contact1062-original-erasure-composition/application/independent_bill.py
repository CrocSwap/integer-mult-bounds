# SPDX-License-Identifier: Apache-2.0
"""Recalculate three complete 17-invocation bills from literal words and the signed caller."""
import argparse
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import runpy

HERE=Path(__file__).resolve().parent
CHECKER="b657117ba89a85b0cf2459236e0f117cff1c4c46b208449b2484c415e3136a3d"
CALLER="255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
WORDS={
    "7643":"dcd797e45b6d4b74411a8a73a9b6e8247bb2ea8744924332b0dd43db3e219f02",
    "7644":"86bc8a1d1276c5b8d80a19704f90279e85b24b9490a02b9afa67c1a5b119c114",
    "combined":"58a045048c853c7f89c53b8b5542e127ba2d12d122a6551d107119bd63e4b067",
}


def load(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix==".gz" else raw)


def check(source,work):
    checker=source/"independent.py"
    assert sha256(checker.read_bytes()).hexdigest()==CHECKER
    module=runpy.run_path(str(checker))
    caller_path=source/"data/caller.json"
    assert sha256(caller_path.read_bytes()).hexdigest()==CALLER
    caller=load(caller_path)
    closure=source/"data/7605-closure.json"
    assert sha256(closure.read_bytes()).hexdigest()=="d4c2500703fd651d5eee8ae9dfd64439703716d1c43656f3455d66157a1912fd"
    base=source/"retained/pr7605"
    for name,pin in load(closure).items():
        assert sha256((base/name).read_bytes()).hexdigest()==pin,name
    signed=load(work/"producer54/validation_signed/RESULT.json")
    assert signed["status"]=="PASS_COMBINED_COMPLETE_SIGNED_APPLICATION"
    assert signed["caller_sha256"]==CALLER
    heads={ "7643":(HERE/"source/7643-WORD.json.gz",HERE/"source/7643-invoice-new.json",HERE/"source/7643-FINAL.json"),
            "7644":(source/"data/word.json.gz",source/"data/invoice.json",source/"receipts/FINAL.json"),
            "combined":(work/"frozen-composition/CANDIDATE-WORD.json.gz",work/"frozen-composition/CANDIDATE-INVOICE.json",work/"FINAL.json") }
    pins=load(HERE/"SOURCE-SHA256.json")
    assert sha256((HERE/"SOURCE-SHA256.json").read_bytes()).hexdigest()=="20b8d1a726ca3fadb9f08dff07436236e3b8b7eef94451373890fb2fc00e844b"
    assert all(sha256(p.read_bytes()).hexdigest()==pins[p.name] for p in heads["7643"])
    odd=[[i,event] for i,event in enumerate(caller["events"]) if event[1]=="IDLE_ODD"]
    assert odd==[[1339,["B","IDLE_ODD",68,[8],-1]],[1340,["B","IDLE_ODD",69,[8],-1]],
                 [2970,["B","IDLE_ODD",70,[9],-1]],[2971,["B","IDLE_ODD",71,[9],-1]]]
    width=len(caller["types"]["B"]["ports"])
    assert width==8
    # This deliberate mutant implements the erroneous omission of the odd-axis debit.
    wrong=Counter()
    for _,event in odd:
        wrong[8*len(event[3])]+=width
        wrong[8*len(event[3])+1]-=width
    assert wrong=={8:32,9:-32}
    result={}
    with module["caller_source"](base) as archive:
        raw=archive.extractfile("research/signed-caller-8x9/expected/ODD-TYPE-AB-CALLER.json").read()
        assert sha256(raw).hexdigest()==CALLER and json.loads(raw)==caller
        grid=module["original_caller_grid"](archive,caller,caller_path)
        for label,(w,i,f) in heads.items():
            word,invoice,final=load(w),load(i),load(f)
            assert module["digest"](word)==WORDS[label]==final["candidate_canonical_sha256"]
            stats=module["replay"](word,set())
            assert not stats["bad_helpers"] and len(stats["erased"])==len(stats["lifetime"])==74
            bill=module["bill"](word,caller,stats,int(grid["caller_odd_scale"]))
            assert dict(bill["paid"])=={int(k):v for k,v in invoice["paid"].items()}
            assert dict(bill["targets"])=={int(k):v for k,v in invoice["targets"].items()}
            assert sum(bill["paid"].values())==final["paid_calls"]
            assert sum(bill["targets"].values())==final["productive_calls"]
            assert bill["ordinary"]==final["ordinary_bound"] and bill["tape"]==final["tape"] and bill["surplus"]==final["surplus"]
            assert bill["caller_paid"][8]==656 and bill["caller_paid"][9]==32
            precision=module["exact_precision"](archive,caller,word,stats,grid)
            assert precision["context_c"]==final["precision_c"]
            h=module["h_check"](precision,{"H":final["public_H"]})
            assert h["conservative_context_bound_bits"]==final["public_context_bound_bits"]
            if label=="combined":
                admission=signed["checks"]["ODD-ADMISSION-PARTIAL.json"]
                assert dict(bill["paid"])=={int(k):v for k,v in admission["invoice"]["P"].items()}
                assert dict(bill["targets"])=={int(k):v for k,v in admission["invoice"]["T"].items()}
                assert bill["ordinary"]==admission["ordinary"]["conservative_total"]
                tape=signed["checks"]["ODD-FIXED-TAPE-COUNTS.json"]
                assert all(tape[k]==v for k,v in bill["tape"].items())
                assert precision["context_c"]==tape["context_c"]
                assert Fraction(final["framework_claim"])==Fraction(signed["claim"])
            result[label]={"canonical":WORDS[label],"bill":bill,"precision":{"context_c":precision["context_c"],"context_height":precision["context_height"],"context_mass_bits":precision["context_mass_bits"],"source_sha256":precision["source_sha256"],"executed_code_sha256":precision["executed_code_sha256"]},"public_H_check":h,"checked_original_erasures":len(stats["erased"])}
            print("PASS independent concrete accounting",label,bill["ordinary"],flush=True)
    return {"status":"PASS_INDEPENDENT_CONCRETE_BILLS_PRECISION_TAPE","independent_source_sha256":CHECKER,
            "caller_sha256":CALLER,"method":"Exact predecessor-independent verifier replays three full words. Caller productive debits are computed from the signed output diagonals, with paid debits from raw signed caller operations. Every ordinary item and tape term is priced from the actual events and 17 applications.",
            "literal_odd_events":odd,"type_B_ports":width,"missing_odd_axis_mutation_minus_correct":dict(wrong),
            "caller_grid":grid,"words":result}


if __name__=="__main__":
    assert __debug__
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--work",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    report=check(args.source.resolve(),args.work.resolve())
    with args.out.open("x") as stream:
        json.dump(report,stream,indent=2,sort_keys=True)
        stream.write("\n")
    print(report["status"],flush=True)
