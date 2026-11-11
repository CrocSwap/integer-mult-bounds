#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Emit the frozen candidate from its exact parent and literal witness."""

from collections import Counter
from pathlib import Path
import argparse
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from replay_checks import check_stationary, extend_exit
from replay_sources import canonical, need, parent_archive, predecessor, read


def profile(old, new, hit):
    live = set()
    peak = lives = 0
    for e in new["program"]:
        if e[0] == "INIT":
            need(e[1] not in live, "Fresh owned life")
            live.add(e[1])
            lives += 1
            peak = max(peak, len(live))
        elif e[0] == "CLEAR":
            live.remove(e[1])
    need(not live, "All owned lives retired")
    paid = Counter(abs(len(new["frames"][e[3]])-len(new["frames"][e[2]]))
                   for e in new["program"] if e[0] == "MOVE")
    paid.subtract(abs(len(old["frames"][e[3]])-len(old["frames"][e[2]]))
                  for e in old["program"] if e[0] == "MOVE")
    delta = Counter(hit["ranks"])
    delta[8] -= 1
    need({r: n for r, n in paid.items() if n} == {1: 1}, "Exactly one paid exit rank added")
    need(new["public"] == old["public"]+1 and new["owned_fields"] == old["owned_fields"]+2,
         "One extra arbitrary public field and two owned labels")
    return dict(lifetimes=lives, peak=peak, owned=new["owned_fields"], events=len(new["program"]),
                added_events=len(new["program"])-len(old["program"]), public=new["public"],
                target_delta=dict(sorted(delta.items())), paid_delta={1: 1})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write new frozen word and profile files")
    args = parser.parse_args()
    hit = read(HERE / "WITNESS.json")
    with parent_archive() as parent:
        sys.path.insert(0, str(parent))
        from construct import construct
        old = predecessor(parent)
        check_stationary(old, hit)
        word = construct(extend_exit(old, hit), hit, read(HERE / "PATHS.json"))
    census = profile(old, word, hit)
    if args.write:
        with (HERE / "WORD.json.gz").open("xb") as out:
            out.write(gzip.compress(canonical(word), mtime=0))
        with (HERE / "PROFILE.json").open("x") as out:
            json.dump(census, out, indent=2, sort_keys=True)
            out.write("\n")
    else:
        need(canonical(word) == canonical(read(HERE / "WORD.json.gz")), "Full regenerated word")
        need(json.loads(json.dumps(census)) == read(HERE / "PROFILE.json"), "Exact emitted census")
    print("PASS_LITERAL_FUNDED_EXIT_WORD", census)


if __name__ == "__main__":
    main()
