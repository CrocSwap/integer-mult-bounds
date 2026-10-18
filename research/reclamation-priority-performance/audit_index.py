"""Untimed sorted-set comparison of every complete eligible candidate sequence."""

import argparse
import json
from pathlib import Path

import adapter
from priority import RankedSlots
from run import run


class AuditedSlots(RankedSlots):
    instances = []

    def __init__(self, *args):
        super().__init__(*args)
        self.queries = 0
        self.unfiltered_candidates = 0
        self.eligible_candidates = 0
        self.instances.append(self)

    def ordered(self, frame):
        core, union = frame
        expected = []
        for slot in self.members:
            rank, (old_core, old_union) = self.state_of(slot)
            if not (core & ~old_core) and not (old_union & ~union):
                expected.append((-rank, slot))
        expected = [slot for _, slot in sorted(expected)]
        actual = list(super().ordered(frame))
        adapter.require(actual == expected, "Eligible candidate sequence differs")
        self.queries += 1
        self.unfiltered_candidates += len(self.members)
        self.eligible_candidates += len(actual)
        return iter(actual)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--h", type=int, choices=(23, 25), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    adapter.RankedSlots = AuditedSlots
    run("indexed", args.h, args.out)
    adapter.require(len(AuditedSlots.instances) == 1, "Expected one index")
    index = AuditedSlots.instances[0]
    result = dict(status="PASS", h=args.h, queries=index.queries,
                  unfiltered_candidates=index.unfiltered_candidates,
                  eligible_candidates=index.eligible_candidates,
                  scope="Every eligible candidate, including candidates beyond the chosen slot; original state/frame oracle")
    (args.out / "AUDIT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("PASS_RECLAMATION_INDEX_AUDIT " + json.dumps(result), flush=True)
