"""Source-bound checks for the written selected complex-layer construction."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


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
            need(sha256((ROOT/item["path"]).read_bytes()).hexdigest()==item["sha256"],"source pin: "+item["path"])
            live.append(item["path"])
    for item in sources["vendor"]:
        need(sha256((HERE/item["path"]).read_bytes()).hexdigest()==item["sha256"],"unchanged vendor pin")
    need(set(live)==set(read(HERE/"VERIFY.json")["inputs"]),"registered transitive inputs")
    old=read(ROOT/"research/selected1094-chart-phase/SOURCES.json")
    need({x["path"] for x in old["files"] if x["usage"]=="input"}<=set(live),"retained audit input closure")
    return {"live_inputs":len(live),"vendor_files":len(sources["vendor"])}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--emit",action="store_true")
    args=parser.parse_args();sources=authenticate()
    sys.path[:0]=[str(HERE),str(HERE/"vendor")]
    import selected,caller,bounds,check_arithmetic
    data=selected.load(ROOT);profiles,local=selected.local_replay(ROOT,data)
    plan=caller.schedule(data,profiles);profile={int(k):v for k,v in plan["profile"].items()}
    assembly=read(ROOT/"research/community-frontier1094-audit/ASSEMBLY.json")
    need(profile=={int(k):v for k,v in assembly["complex_profile"].items()} and
         not assembly["surcharge_model"]["complex"],"actual selected complex profile")
    result={"status":"PASS_SELECTED_COMPLEX_LAYER_INTERFACES","sources":sources,
            "member_pins":data["member_pins"],"local_replay":local,
            "native_binding":selected.native_binding(data),"private_episodes":selected.private_episodes(data),
            "caller":plan,"retained_chart_audit":selected.chart_replay(ROOT),
            "arithmetic":check_arithmetic.run(),"bounds":bounds.run(ROOT,data,profile),
            "scope":"Exact interface checks accompanying a written all-size layer proof under the completed interchange contract; not full-cover payload execution, new formal verification or a multiplication theorem."}
    if not args.emit:need(selected.normal(result)==read(HERE/"RESULT.json"),"saved receipt equality")
    print(json.dumps(result,indent=2))


if __name__=="__main__":main()
