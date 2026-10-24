"""Replay the exact equal-Bell spectrum; no floating point acceptance."""
import argparse
import json
from pathlib import Path
import runpy

P = Path(__file__).resolve().parent
m = runpy.run_path(str(P / "spectrum.py"))
a = argparse.ArgumentParser()
a.add_argument("--write", action="store_true")
args = a.parse_args()
r = m["report"]()
if args.write:
    with (P / "RESULT.json").open("x", encoding="utf-8") as f:
        json.dump(r, f, indent=2); f.write("\n")
else:
    expected = json.loads((P / "RESULT.json").read_text())
    m["require"](json.dumps(r, sort_keys=True) == json.dumps(expected, sort_keys=True), "typed result receipt")
print(json.dumps({k:v for k,v in r.items() if k not in ("representatives", "equal_label_polynomial")}, sort_keys=True))
