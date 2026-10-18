"""Source-authenticated sequential compact and monomial checks."""
import argparse
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
CLIFFORD="research/complex-sw4-frame8/vendor/main/research/complex-k492-owner-repair/vendor/multicold/vendor/pr558/vendor/pr552/complex-global/vendor531/vendor/clifford/clifford_exact.py"


def need(condition,message):
    if not condition:raise ValueError(message)


def unique(pairs):
    out={}
    for key,value in pairs:
        need(key not in out,"duplicate JSON key: "+key);out[key]=value
    return out


def read(path):return json.loads(path.read_bytes(),object_pairs_hook=unique)


def authenticate():
    sources=read(HERE/"SOURCES.json");live=[]
    for item in sources["files"]:
        if item["usage"]=="input":
            need(sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],
                 "source pin: "+item["path"])
            live.append(item["path"])
    need(set(live)==set(read(HERE/"VERIFY.json")["inputs"]),"registered transitive inputs")
    return {"live_inputs":len(live),"base_commit":sources["base_commit"]}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true")
    parser.add_argument("--large",action="store_true")
    args=parser.parse_args();sources=authenticate()
    sys.path[:0]=[str(HERE),str(ROOT/"scripts"),str(ROOT/"research/joint-query")]
    from check_streams import run as streams_run,sparse_repair_controls
    if args.large:
        result=sparse_repair_controls(True);receipt="LARGE-RESULT.json"
    else:
        import audit_compact_controls as old
        from bindings import load
        from check_monomials import run as monomial_run
        spec=importlib.util.spec_from_file_location("retained_selected_clifford",ROOT/CLIFFORD)
        clifford=importlib.util.module_from_spec(spec);sys.modules[spec.name]=clifford;spec.loader.exec_module(clifford)
        local,binding=load(ROOT)
        result={"status":"PASS_SELECTED_COMPLEX_COMPACT_ADAPTERS","sources":sources,
                "binding":binding,"streams":streams_run(old),"monomials":monomial_run(local,clifford),
                "scope":"Sequential adapter execution and source-bound tensor compiler; no complete complex supplier, fast ordinary-code implementation or multiplication theorem."}
        receipt="RESULT.json"
    if not args.emit:need(json.loads(json.dumps(result))==read(HERE/receipt),"saved receipt equality")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
