#!/usr/bin/env python3
"""Authenticate inputs, replay bounded evidence and compare exact receipts."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path[:0]=[str(HERE),str(HERE/"vendor")]


def canonical(value):
    # Normalize integer dictionary keys before ordering the serialized receipt.
    return json.dumps(json.loads(json.dumps(value)),sort_keys=True,separators=(",",":"))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--suite",choices=("source","node","controls"),required=True)
    parser.add_argument("--emit",action="store_true")
    args=parser.parse_args()
    sources=json.loads((HERE/"SOURCES.json").read_text())
    for item in sources["files"]:
        if item["usage"]=="input" and sha256((ROOT/item["path"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("pinned main input changed: "+item["path"])
    for item in sources["vendor_files"]:
        if sha256((HERE/"vendor"/item["name"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("unchanged predecessor source changed: "+item["name"])
    if args.suite=="source":
        from catalogue import Catalogue
        from check_sources import catalogue_checks, consumer_probes, global_scalar
        from check_layout import extents, selected_peel, complete_gapped
        from check_headers import sampled_packet
        catalogue=Catalogue(3)
        result={"selected_sources":catalogue_checks(catalogue),
                "selected_consumers":consumer_probes(catalogue),
                "global_scalar":global_scalar(catalogue),"gapped_extents":extents(),
                "generated_peel":selected_peel(catalogue),"gapped_endpoint":complete_gapped(),
                "sampled_high_packet":sampled_packet()}
    elif args.suite=="node":
        from check_runtime import complete_node
        result=complete_node()
    else:
        from control_checks import stale_controls, bridge_and_exchange, rejections_and_counts
        result={"stale_state":stale_controls(),"bridge_exchange":bridge_and_exchange(),
                "rejections_counts":rejections_and_counts()}
    observed={"full_result_sha256":sha256(canonical(result).encode()).hexdigest(),"result":result}
    if not args.emit:
        expected=json.loads((HERE/"RESULT.json").read_text())[args.suite]
        if canonical(observed)!=canonical(expected):
            print(json.dumps(observed,sort_keys=True,indent=2))
            raise ValueError("retained exact receipt differs: "+args.suite)
        print("PASS_SELECTED_BIT_NODE "+args.suite)
    print(json.dumps(observed,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
