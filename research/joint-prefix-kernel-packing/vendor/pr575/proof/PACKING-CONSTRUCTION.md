# Extending the joint prefix to all 72 calls

This is a direct helper relabeling of the literal PR571 owner assignment at
`b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3`. The exact source files are retained
under `data/packing-source/`. No new optimizer or aggregate packing inference
is needed. The source schedule has 63 width-seven calls and nine plain calls.

The newly reconstructed width-seven provider has exactly the same canonical
JSON and forward/backward program hashes as PR571's `combined-prefix-local`.
The new plain provider applies the same joint A-prefix to the ordinary
eight-cold word. Relative to PR571's old four-cold plain provider its paid
profile changes by `-12 e2 + 8 e3`. Its helper widths agree after swapping
`299 <-> 271`, `301 <-> 283`, `375 <-> 295`, and `377 <-> 307`.
The ports and centers agree exactly. These are equal-width old-to-new slot
matches, not an assumption that the same helper label has unchanged width.

`code/replay_packing.py` reads the exact pinned source PLAN and OWNERS, applies
these four swaps only in the nine plain calls, and compares the entire rebuilt
canonical owner payload with `data/OWNERS.json.gz`. Thus exactly 72 of 36,288
helper labels change, while every time, stage, replica, width, offset, owner
replica, child, port, complete family and copy is unchanged. It checks the
provider width lists, complete helper and family uniqueness per call,
nonoverlapping chronological prefix slots, every recorded window, and the
full local-plus-idle paid histogram. Seven negative controls reject altered
source owners, geometry, permutation, width placement, dispatch, program
binding and mass-preserving histogram corruption.

The unchanged idle histogram is `1200 e3 + 48 e7 + 1808 e48`. Summing 63 new
width-seven and nine new plain providers yields

```
169056 e1 + 40320 e2 + 26544 e3 + 13824 e4
+ 4032 e5 + 4032 e6 + 48 e7 + 576 e8 + 1808 e48.
```

Its rank mass is 520,704, giving `73*7168 - 520704 = 2560`. Compared with
PR571 the change is `-108 e2 + 72 e3`. At any positive exponent `a`, its
contribution to the normalized moment difference is exactly

```
216 * ((73/3)^a - (73/2)^a) / (73*7168) < 0.
```

The finite reconstruction is separate from the fresh native local-word,
Clifford phase, source-derived owner-chart, complete invoice and exact outer
assembly admissions. In particular, matching aggregate widths would not
alone justify a relabeling. Those admissions must use the actual new words
and their pinned artifact identities. All inherited all-size compiler,
common-label and mutable-source, precision/tape, analytic, native recurrence
and unchanged bit-supplier hypotheses remain conditional. No global packing
optimality is claimed.

From the package directory, replay the standard-library construction with:

```
python code/replay_packing.py --recipe data/PACKING-CONSTRUCTION.json --source-plan data/packing-source/PLAN.json --source-owners data/packing-source/OWNERS.json.gz --plan data/PLAN.json --owners data/OWNERS.json.gz --receipt PACKING-REPLAY.json
```

The helper-bijection method is adapted from PR571's
`research/structural-gain/frontier-composition/relabel_owners.py`. The joint
prefix and source geometry are credited to PR571 and its PR569/PR568 lineage;
their original notices are retained by the package. The nine-call extension,
strict replay, negative controls and exact incremental accounting were
prepared with OpenAI Codex assistance under Apache-2.0. The scratch nominator
is a discovery convenience, not a replay dependency; its hash is recorded in
`proof/PACKING-SOURCE.json`.
