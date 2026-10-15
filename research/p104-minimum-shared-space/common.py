"""Strict I/O only; no mathematical routines shared by the two checkers.

Gareth Davidson with OpenAI Codex assistance. Apache-2.0.
"""
from pathlib import Path
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def unique(items):
    result = {}
    for key, value in items:
        need(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read(path):
    def bad(value):
        raise ValueError("nonfinite JSON number: " + value)
    return json.loads(Path(path).read_bytes(), object_pairs_hook=unique,
                      parse_constant=bad)


def digest(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def sources(root=REPO):
    result = {}
    for pin in read(HERE / "SOURCES.json")["files"]:
        if pin["usage"] == "input":
            path = root / pin["path"]
            need(hashlib.sha256(path.read_bytes()).hexdigest() == pin["sha256"],
                 "source bytes changed: " + pin["path"])
            result[path.name] = read(path)
    return result


def certificate(value):
    need(isinstance(value, dict) and set(value) == {"schema", "terms"}, "certificate fields")
    need(value["schema"] == "p104-shared-complement/1", "certificate schema")
    need(isinstance(value["terms"], list) and bool(value["terms"]), "terms list")
    seen = set()
    for term in value["terms"]:
        need(isinstance(term, list) and len(term) == 4, "term shape")
        target, cut, reg, weight = term
        need(type(target) is int and 0 <= target < 104, "target index")
        need(type(cut) is int and 0 <= cut <= 4058, "cut index")
        need(isinstance(reg, str) and bool(reg), "register name")
        need(isinstance(weight, str) and bool(weight), "rational string")
        key = target, cut, reg
        need(key not in seen, "duplicate contact")
        seen.add(key)
    return value


def cli(run, status):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    need(args.out is None or not args.out.exists(), "output already exists")
    result = run()
    need(result == read(HERE / "RESULT.json"), "receipt differs from exact replay")
    if args.out:
        with args.out.open("x") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    print(status, "minimum=96 targets=104 cuts=4059 terms=" +
          str(result["certificate_terms"]), "receipt=" + digest(result))
