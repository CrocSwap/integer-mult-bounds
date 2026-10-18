#!/usr/bin/env python3
"""Deterministically reconstruct the certificate; not trusted for acceptance.

Standard library only. Writes exclusively to the required --out path.
The checker independently verifies the resulting primal/dual inequalities.
"""
import argparse
from collections import defaultdict
from functools import lru_cache
import importlib.util
from itertools import combinations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cover_verifier", HERE / "verify.py")
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


def build(support, covers):
    nontrivial = [c for c in covers if c.bit_count() > 1]
    incidence = defaultdict(set)
    for i, c in enumerate(nontrivial):
        for e in v.bits(c):
            incidence[e].add(i)
    unseen = set(incidence)
    packing, chosen = [], []
    component_stats = []
    while unseen:
        first = min(unseen)
        unseen.remove(first)
        stack, edges, ids = [first], {first}, set()
        while stack:
            e = stack.pop()
            for i in incidence[e] - ids:
                ids.add(i)
                for f in v.bits(nontrivial[i]):
                    if f not in edges:
                        edges.add(f)
                        unseen.discard(f)
                        stack.append(f)
        es, ii = sorted(edges), sorted(ids)
        options = [nontrivial[i] for i in ii]
        whole = sum(1 << e for e in es)
        found = None
        # At most 14 alternatives in the pinned instance: complete subsets.
        v.require(len(options) <= 14, "generator's bounded domain exceeded")
        for k in range(1, len(options)+1):
            for subset in combinations(range(len(options)), k):
                union = 0
                for j in subset:
                    union |= options[j]
                if union == whole:
                    found = subset
                    break
            if found is not None:
                break
        v.require(found is not None, "uncovered component")
        # A separate maximum independent-set search supplies a 0/1 dual.
        local = {e: j for j, e in enumerate(es)}
        conflict = [0] * len(es)
        for option in options:
            mask = sum(1 << local[e] for e in v.bits(option))
            for e in v.bits(option):
                conflict[local[e]] |= mask

        @lru_cache(None)
        def independent(mask):
            if not mask:
                return ()
            j = max(v.bits(mask), key=lambda x: (mask & conflict[x]).bit_count())
            yes = (j,) + independent(mask & ~conflict[j])
            no = independent(mask & ~(1 << j))
            return min((yes, no), key=lambda a: (-len(a), tuple(sorted(a))))

        packed = sorted(es[j] for j in independent((1 << len(es))-1))
        v.require(len(packed) == len(found), "nonintegral cover component")
        packing.extend([[e // v.N, e % v.N] for e in packed])
        for j in found:
            entries = list(v.bits(options[j]))
            chosen.append({"sources": sorted({e % v.N for e in entries}),
                           "targets": sorted({e // v.N for e in entries})})
        component_stats.append([len(es), len(options), len(found)])
    result = {"schema_version": 1,
              "optimum": sum(c.bit_count() == 1 for c in covers) + len(packing),
              "extra_packing": sorted(packing),
              "extra_cover": sorted(chosen, key=lambda x: (x["targets"], x["sources"]))}
    v.verify_certificate(result, support, covers)
    return result, component_stats


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    word, fixture = v.authenticate()
    support = v.correction(fixture)
    paths, _ = v.trace(word)
    covers, _ = v.cover_family(paths, support)
    certificate, components = build(support, covers)
    with args.out.open("x") as f:
        f.write(json.dumps(certificate, indent=2) + "\n")
    print(f"GENERATED_P104_COVER optimum={certificate['optimum']} components={len(components)} max_edges={max(x[0] for x in components)} max_options={max(x[1] for x in components)}")


if __name__ == "__main__":
    main()
