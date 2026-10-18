#!/usr/bin/env python3
"""Source-authenticated bounded replay of produced source packets."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(HERE/"vendor")]


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"))


def receipt(result):
    return {"full_result_sha256":sha256(canonical(result).encode()).hexdigest(),"result":result}


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--suite",choices=("source","packet","controls"),required=True)
    parser.add_argument("--emit",action="store_true",help="emit result without receipt comparison")
    args=parser.parse_args()
    sources=json.loads((HERE/"SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"]=="input" and sha256((ROOT/item["path"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("pinned main input changed: "+item["path"])
    for item in sources["vendor_files"]:
        if sha256((HERE/"vendor"/item["name"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("unchanged predecessor source changed: "+item["name"])
    if args.suite=="source":
        import check_sources as source
        import check_caller as caller
        result={"low_codes":source.low_codes(),
                "directories":[source.directory_case(),source.directory_case(fields=0),source.directory_case(64,1,2)],
                "routes":[source.route_case(1,3),source.route_case(),source.route_case(3,1)],
                "selected_binding":source.selected_binding(),"physical_episode":caller.complete_episode(),
                "selected_columns":caller.selected_columns(),"selected_consumer":caller.selected_consumer()}
    elif args.suite=="packet":
        from check_packet import complete_packet
        result=complete_packet()
    else:
        from control_checks import run
        result=run()
    observed=receipt(result)
    if not args.emit:
        expected=json.loads((HERE/"RESULT.json").read_text())[args.suite]
        if canonical(observed)!=canonical(expected):
            raise ValueError("retained exact receipt differs: "+args.suite)
        print("PASS_SELECTED_SOURCE_PACKETS "+args.suite)
    print(json.dumps(observed,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
