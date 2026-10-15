## Contribution

Adds an exact scoped census for a six-source connector alphabet with one
charged three-source call. For a closed 12-call word with eleven singleton
steps and one weight-three step, no path covers all 63 nonzero pairwise
prefix differences. After symmetry normalization, the complete exact search
contains 1,098,204 simple paths and 709,812 eligible closing-edge candidates;
maximum coverage is 49, and no candidate covers 63 masks. This excludes only
the stated call and source-add profile. No supplier, recursive bound, or
`kappa` change is claimed.

The fully charged hypothetical bill would be `138 o + 140 p`, including 126
output readouts, versus PR #2128's `140 o + 142 p`. The TRIO call is charged
`o + 3p`, and any additional implementation surcharge must be below
`2o + 2p` for the modeled saving to survive. The complete census shows that
this profile does not realize the saving.

## Verification

Run:

```sh
python3 -I -B research/connector-trio-cycle25-seed1b82df/verify.py
python3 scripts/research_package.py --package research/connector-trio-cycle25-seed1b82df --check-only
```

The verifier independently scans all normalized paths by a product iterator,
recomputes difference sets from scratch, checks the exact histogram and
endpoint-record digest, confirms the PR #2128 full-cover fixture, and runs
three negative controls. Direct local output under Python 3.14.7:

```text
PASS_TRIO_CYCLE_VERIFY walks=1098204 endpoints=709812 max=49 full=0 pr2128=63/63 controls=3
```

The metadata-and-source-pin check passes locally. The registered replay is
configured for Python 3.12; it was not run locally because Python 3.12 is not
installed.

## Provenance and disclosure

Seed `1b82dfd0673536e282d9d9e7adcb1a04`, track `recursive-interfaces`, task
`connector-alphabet-change`, priority revision 4. Exact base:
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`. Selected record SHA-256:
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
All pins and the refined scope are in `TASK.json` and `SOURCES.json`.

Nearest positive comparator and fixture: Aaron Wang, [PR #2128](https://github.com/CrocSwap/integer-mult-bounds/pull/2128),
head `697369a971eed02c0fbcd75ebefec9f59945f08e`. The current result uses a
different alphabet extension: exactly one charged TRIO call. Substantial
OpenAI Codex assistance was used; no independent human review is claimed.
