"""Authenticate retained inputs before imports and replay the scoped checks."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def need(condition,message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    out={}
    for key,value in pairs:
        need(key not in out,"duplicate JSON key: "+key)
        out[key]=value
    return out


def read(path):
    return json.loads(path.read_bytes(),object_pairs_hook=unique_object)


def authenticate():
    sources=read(HERE/"SOURCES.json")
    live=[]
    for item in sources["files"]:
        if item["usage"]=="input":
            need(sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],
                 "source pin: "+item["path"])
            live.append(item["path"])
    for item in sources["vendor"]:
        need(sha256((HERE/item["path"]).read_bytes()).hexdigest()==item["sha256"],
             "unchanged predecessor pin: "+item["path"])
    need(set(live)==set(read(HERE/"VERIFY.json")["inputs"]),"complete registered input list")
    old=read(ROOT/"research/pr589-five-helper-hosting/SOURCES.json")
    need({i["path"] for i in old["files"] if i["usage"]=="input"}<=set(live),
         "retained verifier transitive input coverage")
    return {"live_inputs":len(live),"unchanged_vendored_files":len(sources["vendor"])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true")
    args=parser.parse_args()
    sources=authenticate()
    sys.path[:0]=[str(HERE),str(HERE/"vendor")]
    from provider import Catalogue
    import check_provider,check_leaf,check_headers,check_recursion
    import physical_stream
    def no_child_oracle(*_args,**_kwargs):
        raise ValueError("completed leaf invoked an opaque weighted child")
    physical_stream.child_oracle=no_child_oracle
    catalogue=Catalogue(ROOT)
    inherited=catalogue.old.run()
    need(json.loads(json.dumps(inherited))==read(ROOT/"research/pr589-five-helper-hosting/RESULT.json"),
         "retained PR1627 literal and chronological receipt")
    result={"status":"PASS_SELECTED_BIT_RECURSIVE_INTERFACES",
            "scope":"Finite source-bound checks accompanying the written recursive interchange proof; not a full payload execution, proof-assistant verification or multiplication theorem.",
            "sources":sources,"retained_PR1627_replay":inherited["status"],
            "provider":check_provider.run(catalogue),
            "leaves":check_leaf.run(catalogue),
            "headers":check_headers.run(catalogue,ROOT),
            "recursion":check_recursion.run(catalogue,ROOT)}
    if not args.emit:
        need(json.loads(json.dumps(result))==read(HERE/"RESULT.json"),"saved receipt equality")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
