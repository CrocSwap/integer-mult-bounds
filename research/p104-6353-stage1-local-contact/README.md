# Stage-1 LOCAL contact on the PR6353 ports

**Audit; no new κ.** Selected kappa stays `781451/250000000`.

## Scope and evidence

Original card: `joint-query-controller`. The scope is **changed**. The card
asks whether a new query demand removes work. This package does not change
the caller. It checks the physical contact that the latest handoff on
[discussion 1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19344846)
left open after the formal Laurent endpoint in PR6361.

The fixed caller is PR6348, event 21, `LOCAL(1, 0, 1)`. The supplier ports
are the PR6353 word at `db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3`, vendored
at `sources/pr6353-WORD.json.gz` (git blob `03ea7690285d4cda72815f962d5710ab96e08490`,
SHA256 `0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928`).
Those 104 ports equal the PR6349 source word. The declared physical checker
`research/balanced-query-tree/physical.py` is pinned and not imported.

Independent replay of all 104 ports and 416 contacts gives diagonal `D_1`
on fresh axes `9..16` and cross term `D_1 Q^{-1}`. Central axes `0..8` are
the spectator block carried in `raw_X`. Translations for port `q=11` are in
the verifier output. The contact digest is
`ac69d4f31e86ae776ee15457d2362bf06b0daf777a7fe80b300c31632ece3498`.

The nine PR6353 output-frame edits, including `MOVE 703: 712 -> 1094`, are
disjoint from this LOCAL event. Labels 770–778 are opened, cleared, and
sometimes moved as owned fields; they are not caller roles 0 or 1. Details
are in [PROOF.md](PROOF.md).

Failure controls, all rejected: drop fresh axis 9 from `D_1`, drop `Q^{-1}`
from the cross term, and tilt the first vector of the port-11 fresh basis.

Not checked: LOCAL stages 2–19, endpoint phases, whole idles, central-square
columns, funding, compiler, and outer predicates. The five framework
assumptions remain. This does not admit PR6353 or raise the frontier.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/p104-6353-stage1-local-contact --check-only
python3 -B scripts/research_package.py --package research/p104-6353-stage1-local-contact
```

Direct replay also accepts `-O`; the checks raise `ValueError` and do not use
assertions. A direct run is:

```sh
python3 -B research/p104-6353-stage1-local-contact/verify.py
```

## Open next questions

The structured questions are in [TASK.json](TASK.json).

1. Bind LOCAL stages 2 through 19 the same way, then the endpoint phases and
   whole idles. One stage does not transfer.
2. Finish source-specific funding, compiler, and outer predicates for the
   frozen PR6353 head before any kappa admission.
3. Keep the frame-1094 width-one matrices in PR6360 separate from this
   caller contact. A later width needs its own check.

## Credit

Caller and declared contact formulas: Ali Romman, PR6348 and PR6353, with
the retained Cinna Davis / P104 native-channel lineage and DreamingOfClouds
for the PR6349 ports. Formal endpoint audit: ToikY, PR6361. Width-one
frame-1094 matrices: ToikY, PR6360. New stage-1 contact replay and controls:
unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
