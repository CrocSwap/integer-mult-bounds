"""Authenticate sources and compare one complete cold scalar receipt."""
import argparse
from hashlib import sha256
import importlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0,str(HERE))


def authenticate():
    sources = json.loads((HERE/"SOURCES.json").read_text())
    manifest = json.loads((HERE/"VERIFY.json").read_text())
    inputs = {row["path"]:row for row in sources["files"] if row["usage"] == "input"}
    if set(inputs) != set(manifest["inputs"]):
        raise ValueError("complete scalar input inventory")
    for name,row in inputs.items():
        if sha256((ROOT/name).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("changed live tape-source input: "+name)
    for row in sources["archives"]:
        if sha256((HERE/row["path"]).read_bytes()).hexdigest() != row["sha256"]:
            raise ValueError("changed immutable scalar source archive")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--suite",required=True,choices=("bindings","shifts","packets","prefixes","returns","failures"))
    parser.add_argument("--emit",action="store_true")
    args = parser.parse_args()
    authenticate()
    checks = importlib.import_module("check_"+args.suite)
    result = checks.run()
    digest = sha256(json.dumps(result,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()
    if not args.emit:
        expected = json.loads((HERE/"RESULT.json").read_text())[args.suite]
        if digest != expected:
            raise ValueError("complete typed scalar receipt differs: "+args.suite+": "+digest)
    print(json.dumps(dict(suite=args.suite,sha256=digest,result=result),sort_keys=True,indent=2))
    print("PASS_PHYSICAL_SCALAR_"+args.suite.upper())


if __name__ == "__main__":
    main()
