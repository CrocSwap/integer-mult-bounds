"""Apply a canonical coefficient-and-paid-route journal to the pure birth carrier."""
import argparse
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return sha256(encode(value)).hexdigest()


def load(path):
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if raw[:2] == b"\x1f\x8b" else raw)


def require(value, text):
    if not value:
        raise ValueError(text)


def apply(graph, journal):
    require(digest(graph) == journal["source"], "overlay source graph")
    routes = {k: (a, b) for k, a, b in graph["moves"]}
    forms = {k: dict(terms) for k, terms in graph["forms"]}
    for key, old, new in journal["routes"]:
        require(routes.get(key) == (tuple(old) if old else None), "old paid route")
        if new is None:
            del routes[key]
        else:
            routes[key] = tuple(new)
    for key, present_before, present_after, changes in journal["forms"]:
        require((key in forms) == present_before, "old scalar row")
        row = dict(forms.get(key, {}))
        for donor, before, after in changes:
            require(row.get(donor) == before, "old scalar coefficient")
            if after is None:
                del row[donor]
            else:
                require(str(Fraction(after)) == after and Fraction(after) != 0, "canonical nonzero coefficient")
                row[donor] = after
        if present_after:
            forms[key] = row
        else:
            require(not row, "retiring a nonempty row")
            del forms[key]
    public = len(graph["initial"])
    first = graph["first_output"]
    require(set(forms) == set(routes) | set(range(first, first + public)), "all paid and terminal rows")
    order = journal["schedule"]
    require(len(order) == len(forms) and set(order) == set(forms), "complete scheduled rows")
    available = {~i: chart for i, chart in enumerate(graph["initial"])}
    for key in order:
        chart = routes[key][0] if key in routes else graph["final"][key-first]
        require(all(available.get(src) == chart for src in forms[key]), "all coefficient reads local and causal")
        if key in routes:
            available[key] = routes[key][1]
    child = dict(graph, moves=[[k,*v] for k,v in sorted(routes.items())],
                 forms=[[k,sorted(row.items())] for k,row in sorted(forms.items())],schedule=order)
    require(digest(child) == journal["result"], "overlay output")
    return child


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source",type=Path)
    p.add_argument("journal",type=Path)
    p.add_argument("output",type=Path)
    args = p.parse_args()
    word = apply(load(args.source),load(args.journal))
    args.output.write_bytes(gzip.compress(encode(word),mtime=0))
    print("PASS_COMPLETE_LITERAL_OVERLAY", digest(word))
