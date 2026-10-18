#!/usr/bin/env python3
"""Source-bound native covariance replay; emit or compare exact evidence."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))


def canonical(value):
    return json.dumps(json.loads(json.dumps(value)),sort_keys=True,separators=(",",":"))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--emit",action="store_true")
    args=parser.parse_args()
    # Authenticate the complete live-input inventory before source imports.
    for item in json.loads((HERE/"SOURCES.json").read_text())["files"]:
        if item["usage"]=="input" and sha256((ROOT/item["path"]).read_bytes()).hexdigest()!=item["sha256"]:
            raise ValueError("pinned source changed: "+item["path"])
    import source
    import checks
    import native_check
    data=source.load()
    result={"algebra":checks.run(data),"native":native_check.run(data)}
    observed={"canonical_sha256":sha256(canonical(result).encode()).hexdigest(),"result":result}
    if not args.emit:
        expected=json.loads((HERE/"RESULT.json").read_text())
        if canonical(observed)!=canonical(expected):
            print(json.dumps(observed,sort_keys=True,indent=2))
            raise ValueError("exact evidence receipt differs")
        print("PASS_COVARIANT_NATIVE_READER_LIFT")
    print(json.dumps(observed,sort_keys=True,indent=2))


if __name__=="__main__":main()
