"""Replay an ordered journal of productive rational splits on its declared parent."""
from fractions import Fraction
from pathlib import Path
import argparse
import gzip
import json
import sys


def replay(args):
    cache = args.cache.resolve()
    sys.path.insert(0, str(cache / "parent/complex"))
    from birth_replay import digest, endpoint_map, require, subspace, write_word
    sys.path.insert(0, str(cache / "source/research/p104-dual-supplier-lift/complex"))
    import supplier
    from birth_event import apply_split

    source = json.loads(gzip.decompress(args.word.read_bytes()))
    layout = json.loads(gzip.decompress(args.layout.read_bytes()))
    journal = json.loads(args.journal.read_bytes())
    require(digest(source) == journal["source_sha256"] and digest(layout) == args.parent_layout,
            "unmatched parent word or layout")
    frames = source["frames"]
    spans = [subspace(tuple(rows)) for rows in frames]
    net = supplier.Network(source["first_output"], source["initial"], source["final"],
                           {k: (a, b) for k, a, b in source["moves"]},
                           {k: {i: Fraction(q) for i, q in row} for k, row in source["forms"]})
    _, mains = endpoint_map(layout, len(net.initial))
    for event in journal["events"]:
        n = len(net.initial)
        role = event["role"]
        reverse = event["reverse"]
        before = net.transpose() if reverse else net
        start, read = event["source_chart"], event["split_chart"]
        enter, end = event["fresh_source_chart"], event["return_chart"]
        require(0 <= role < n and role not in mains and (before.initial[role], before.final[role]) == (start, end),
                "helper identity and endpoint charts")
        oriented = (lambda x, y: spans[y] < spans[x]) if reverse else (lambda x, y: spans[x] < spans[y])
        require(oriented(start, read) and oriented(enter, end), "two positive strictly nested productive transfers")
        split = apply_split(before, event)
        split.initial[n] = enter
        require(split.moves == before.moves, "paid bank and move tables changed")
        net = split.transpose() if reverse else split
        require(len(net.initial) == n + 1 and len(net.final) == n + 1, "one independent field per split")
        labels = layout["source_labels"]
        layout = dict(layout, public=n + 1, source_labels=labels + [1 + max(labels)])
    candidate = supplier.dump_graph(net, frames)
    require(digest(candidate) == journal["candidate_sha256"] and digest(layout) == args.child_layout,
            "literal construction differs from declared child")
    args.out.mkdir(parents=True, exist_ok=True)
    write_word(args.out / "WORD.json.gz", candidate)
    write_word(args.out / "LAYOUT.json.gz", layout)
    print("PASS", digest(candidate), digest(layout))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    for key in ("cache", "word", "layout", "journal", "out"):
        p.add_argument("--" + key, type=Path, required=True)
    for key in ("parent-layout", "child-layout"):
        p.add_argument("--" + key, required=True)
    replay(p.parse_args())
