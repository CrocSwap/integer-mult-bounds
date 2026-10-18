# Cold-host restoration: cancellation works; direct undo hits target frames

**No new κ claim.** This follows the open J-dim1 cold-host lead on
[`research/t74-r10-hosting-leads`](https://github.com/mdumitrean/integer-mult-bounds/tree/dfbc5ba121d5d23381393f178be8d4ba25ebfa4d),
based on [PR2802](https://github.com/CrocSwap/integer-mult-bounds/pull/2802) at
`17b2ee6ef3cf1468e78a6267f0ecbc9a0e6f60dd`. Its conditional comparison value is
`0.001717794984118634663827 - 10^-46 - 10^-70`. The selected record remains
`0.001672660197076918`.

The submission overlap check also found [PR2818](https://github.com/CrocSwap/integer-mult-bounds/pull/2818)
at `175822aee7a1858ec653f7f92d7a750aec2c2795`. Both literal words, fill, order
and dispatch match PR2802; it claims only a finer endpoint. This package keeps
its exact PR2802 comparison point. Its fixed-word obstruction is unaffected,
and increasing the comparison endpoint can only tighten the necessary cost
budgets. PR2818's high-precision endpoint was not independently certified here.

J replaces an entering width-eight helper with a retired width-four cold host.
The realized merged host ends at width nine, which loses the prospective gain.
Keeping it cold at width seven or eight requires undoing the borrowed writes,
cancelling its warp, and paying the resulting frame and owner costs.

## What this adds

1. **A constructive operator cancellation.** On `473→277`, an inverse warp at
   the zero entrance, one zero-frame prelude read, and an exact terminal undo
   restore the original dirty input. Both orientations pass the unchanged
   pinned algebra/frame auditor and semantic failure controls. The fixture
   ends at FULL9: the pinned native transport rejects FULL-ended private
   buffers, so this establishes an algebra/frame component only.
2. **A fixed-word recovery obstruction.** The 92 retained pairs in both
   orientations give 184 words and 131,788 post-use insertion slots. No direct
   recovery has a necessary rank below eight. The rank-eight slots compress to
   720 commuting classes; all 8,208 orders of their three/four contiguous
   recovery additions are frame-infeasible. Every order has a target-port
   end-frame collision, so widening another cold helper does not remove it.
3. **A changed-entry check.** All 31 rank-four hyperplanes for each of 32
   eligible first-write rank-five caps, with host 277 in the base orientation,
   give 992 variants and 368,218 direct-recovery slots. Every variant needs
   rank nine. An independent exact lattice replay reproduces the complete
   histograms without the frame optimizer.
4. **Exact cost limits.** Rational continuous-pattern duals check every one of
   the 1,163 patterns. They reject the width-nine/`−H3` ledger, even
   allowing fractional allocation. Rank-mass-consistent ideal cold ledgers
   have the small remaining net-cost budgets below.

| Hypothetical cold host | Local delta per call | Numerical gain for stored pattern invoice | Exact upper bound on extra net cost per call |
|---|---|---:|---:|
| width 7, replacing `(4,8)` | `−H3−H2` | `+8.70325321e−7` | `<0.017959 H1` |
| width 8, replacing `(4,8)` | `−H3−H2+H1` | `+2.79896668e−7` | `<0.005786 H1` |

These numerical gains concern feasible **pattern** invoices, not chronological
owner allocations or constructed words. The duals certify necessary cost
bounds and explicit rational upper caps. Every ledger preserves rank mass
4,816,512; restored variants retain 72 private buffers. Scalar gate count is
not the number of paid rank-one children.

## Reproduction and evidence

Python 3.12+, standard library only. Run from the repository root:

```sh
python3 -B scripts/research_package.py --package research/t74-cold-host-restoration
```

The registered replay authenticates package bytes before executing the
independent direct/entry-frame checks, the literal cancellation construction
and unchanged auditor, and the rational pattern certificates. It uses temporary
outputs, isolates imported bytecode caches, and leaves committed evidence
unchanged. Commands and time limits are
in [VERIFY.json](VERIFY.json). Detailed scope and evidence are in
[direct/NOTES.md](direct/NOTES.md), [operator/NOTES.md](operator/NOTES.md),
[hyperplanes/NOTES.md](hyperplanes/NOTES.md), and [pricing/NOTES.md](pricing/NOTES.md).

The research round allowed 80 cores across the primary agent and three parallel
agents, with disjoint affinities and single-threaded BLAS. The original searches
used the pinned NumPy/SciPy frame toolkit; certificate replay does not depend on
those solvers. Exact source and environment information accompanies the evidence.
The research started at canonical main `544a7e82810e30cab61c297cb2e2ea86127fe944`,
priority revision 5; the publication branch is based on
`cfddb8581e7e96d4f4cd9bfd279037014c8b296d`, with unchanged relevant guidance
and selected record. [TASK.json](TASK.json) records the complete cost ledger,
freshness checks and bounded stopping decision.

## Open next questions

The exclusion concerns **contiguous direct recovery additions** in the stated
words and interfaces. It is not a universal cold-host obstruction. Staged undo,
precomputed recovery combinations, different scalar circuits and changed
consumers remain open. The full-width cancellation fixture does not establish
a native supplier, and no new literal owner fill, complete cold replay or outer
admission is claimed.

The next useful experiment is a small staged or changed-basis recovery for
`473→277` that avoids the target-port collision and stays within the exact
width-eight cost allowance. It must provide the actual paid profile before
further packing work. A successful sub-full cold word would then need native
replay, physical stock/precision checks, literal owners and the complete outer
ledger. These obligations and first steps are also listed in [TASK.json](TASK.json).

## Credit

J's hosting mechanism, source branch, and #2802 construction: Marius-Paul
Dumitrean with substantial Anthropic Claude assistance. This round adds
substantial OpenAI Codex assistance, including three parallel AI agents and a
separate integration replay; no independent human or proof-assistant review is
claimed.

Retained lineage: tekuuu (#2751), DavidAriasC (#2766), mason-hale (#2696),
Cinna Davis / 1337isnot1337 (#2226), philippeVV (#2679), Jeremy Kothe /
jeremykothe2 (#2673/#2745), Vlado-V (#2322), Rohan Arun and the credited
T74/native/owner/outer sources. The #1186 frame toolkit is Marius-Paul
Dumitrean's earlier contribution. Frozen source notices and byte-exact source
pins are retained with the consumed inputs. Apache-2.0.
